from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from config import db
import re


BASE_URL = "https://obis.gelisim.edu.tr"

TABLE_IDS = {
    "schedule": "tbl",
    "grades": "dtList_Sinif_grdTanim_0",
    "attendance": "dtList_Sinif",
    "exams": "grdTanim",
    "announcements": "grdBildirimList"
}

PAGES = {
    "schedule": "/Ders_Program.aspx",
    "grades": "/Ders_Notlari.aspx",
    "attendance": "/Devamsizlik.aspx",
    "exams": "/Sinav_Tarihlerim.aspx",
    "announcements": "/Bildirimler.aspx"
}


class OBISScraper:

    # Attaches to an existing Chrome session via CDP. User must login to OBIS manually.
    # Opens a NEW tab for scraping so the user's existing tabs are not disturbed.
    def scrape_all(self):
        errors = {}
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.new_page()
            try:
              for name, fn in [
                ('schedule',      self._get_schedule),
                ('grades',        self._get_grades),
                ('attendance',    self._get_attendance),
                ('exams',         self._get_exams),
                ('announcements', self._get_announcements),
            ]:
                try:
                    fn(page)
                except Exception as e:
                    errors[name] = str(e)
            finally:
                page.close()
        return errors  # empty dict means full success

    def _navigate(self, page, route):
        page.goto(BASE_URL + route, timeout=60000)
        page.wait_for_load_state('networkidle', timeout=60000)
        return BeautifulSoup(page.content(), 'html.parser')

    def _parse_table(self, soup, table_id):
        table = soup.find('table', {'id': table_id})
        if not table:
            return []
        rows = table.find_all('tr')
        headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
        result = []
        for row in rows[1:]:
            cells = row.find_all('td')
            if cells:
                result.append(dict(zip(headers, [c.get_text(strip=True) for c in cells])))
        return result

# A spaghetti solution for tables with nested headers. Scans rows to find the one header that contains 'DERS KODU'. Assumes that's the real header row, uses that header to parse the rest.
    def _find_header_row(self, rows):
        for i, row in enumerate(rows):
            cells = row.find_all(['th', 'td'])
            if any('DERS KODU' in c.get_text(strip=True) for c in cells):
                return i
        return 0
    
# Used for tables where row 0 is the semester header. 
    def _parse_table_nested(self, soup, table_id):
        table = soup.find('table', {'id': table_id})
        if not table:
            return []
        rows = table.find_all('tr')
        header_index = self._find_header_row(rows)
        headers = [th.get_text(strip=True) for th in rows[header_index].find_all(['th', 'td'])]
        result = []
        for row in rows[header_index + 1:]:
            cells = row.find_all('td')
            if cells:
                result.append(dict(zip(headers, [c.get_text(strip=True) for c in cells])))
        return result

# Scrapes the weekly schedule from Ders_Program.aspx.
# Each cell contains course code, name, building, room and teacher across day columns.
# Same course repeats across consecutive time rows — we collect all slots and
# compute time_start/time_end so we get one clean document per course+day.
    def _get_schedule(self, page):
        page.goto(BASE_URL + PAGES['schedule'], timeout=60000)
        page.wait_for_load_state('networkidle', timeout=60000)
        soup = BeautifulSoup(page.content(), 'html.parser')
        table = soup.find('table', {'id': TABLE_IDS['schedule']})
        if not table:
            return
        rows = table.find_all('tr')
        if not rows:
            return

        # Row 0 is the header: SAAT, PAZARTESİ, SALI, ÇARŞAMBA, PERŞEMBE, CUMA, CUMARTESİ, PAZAR
        headers = [td.get_text(strip=True) for td in rows[0].find_all('td')]
        days = headers[1:]

        # Collect entries keyed by (code, day) to merge consecutive time slots
        schedule = {}

        for row in rows[1:]:
            cells = row.find_all('td')
            if not cells:
                continue

            time_slot = cells[0].get_text(strip=True)
            if '-' not in time_slot:
                continue

            time_start = time_slot.split('-')[0].strip()
            time_end = time_slot.split('-')[1].strip()

            for i, cell in enumerate(cells[1:]):
                text = cell.get_text(separator='\n', strip=True)
                if not text:
                    continue

                lines = [l.strip() for l in text.split('\n') if l.strip()]
                if len(lines) < 4 or '-' not in lines[0]:
                    continue

                code = lines[0].split('-')[0].strip()
                name = lines[0].split('-', 1)[1].strip()
                building = lines[1].strip('()')
                room_match = re.search(r'\(([^)]+)\)', lines[2])
                room = room_match.group(1) if room_match else lines[2]
                teacher = lines[3]
                day = days[i] if i < len(days) else ''

                key = (code, day)
                if key not in schedule:
                    schedule[key] = {
                        "code": code,
                        "name": name,
                        "day": day,
                        "time_start": time_start,
                        "time_end": time_end,
                        "building": building,
                        "room": room,
                        "teacher": teacher
                    }
                else:
                    # Extend time_end as we hit later slots for the same course
                    schedule[key]['time_end'] = time_end

        for entry in schedule.values():
            db['subjects'].replace_one(
                {"code": entry['code'], "day": entry['day']},
                entry,
                upsert=True
            )

    # Parses a BeautifulSoup table element directly into a list of dicts.
    # Used by _get_grades which finds tables dynamically rather than by a fixed ID.
    def _parse_table_element(self, table):
        rows = table.find_all('tr')
        if not rows:
            return []
        headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
        result = []
        for row in rows[1:]:
            cells = row.find_all('td')
            if cells:
                result.append(dict(zip(headers, [c.get_text(strip=True) for c in cells])))
        return result

    # Iterates through all semester grade tables on Ders_Notlari.aspx.
    # Table IDs follow the pattern dtList_Sinif_grdTanim_0, _1, _2 etc.
    # Semester labels follow dtList_Sinif_lblBASLIK_0, _1, _2 etc.
    # Stops when neither a table nor a label is found at index i.
    def _get_grades(self, page):
        soup = self._navigate(page, PAGES['grades'])
        i = 0
        while True:
            table_id = f'dtList_Sinif_grdTanim_{i}'
            label_id = f'dtList_Sinif_lblBASLIK_{i}'

            table = soup.find('table', {'id': table_id})
            label = soup.find(id=label_id)

            if not table and not label:
                break

            semester = label.get_text(strip=True) if label else f'semester_{i}'

            if table:
                for row in self._parse_table_element(table):
                    if row.get('DERS KODU'):
                        db['grades'].replace_one(
                            {"code": row.get('DERS KODU', ''), "semester": semester},
                            {
                                "code": row.get('DERS KODU', ''),
                                "subject": row.get('DERS ADI', ''),
                                "semester": semester,
                                "credits": row.get('KREDİ', ''),
                                "ects": row.get('AKTS', ''),
                                "teacher": row.get('DERSİ VEREN Ö.ELEMANI', ''),
                                "homework": row.get('ÖDEV', ''),
                                "quiz": row.get('KISA SINAV', ''),
                                "midterm": row.get('VİZE', ''),
                                "midterm_makeup": row.get('VİZE MAZERET', ''),
                                "final": row.get('FİNAL', ''),
                                "resit": row.get('BÜTÜNLEME', ''),
                                "letter_grade": row.get('HARF NOTU', '')
                            },
                            upsert=True
                        )
            i += 1

# Need to hardcode column positions due to misalignments. Confirmed the column positions from manual inspection of the OBIS attendance table.
    def _get_attendance(self, page):
        soup = self._navigate(page, PAGES['attendance'])
        table = soup.find('table', {'id': TABLE_IDS['attendance']})
        if not table:
            return

        rows = table.find_all('tr')
        header_index = self._find_header_row(rows)
    
        columns = ['code', 'subject', 'theoretical_absence', 'practical_absence',
                    'theoretical_max', 'practical_max', 'letter_grade']

        for row in rows[header_index + 1:]:
            cells = row.find_all('td')
            if len(cells) >= len(columns):
                data = {col: cells[i].get_text(strip=True) for i, col in enumerate(columns)}
                # Only keep rows where code looks like a real course code (e.g. ISL220, ATA202)
                # and at least one absence field is populated.
                code_is_valid = bool(re.match(r'^[A-ZÇĞİÖŞÜ]+\d+$', data['code'])) and len(data['code']) <= 7
                has_absence_data = data['theoretical_absence'] != '' or data['practical_absence'] != ''
                if code_is_valid and has_absence_data:
                    db['attendance'].replace_one(
                        {"code": data['code']},
                        data,
                        upsert=True
                    )

    def _get_exams(self, page):
        rows = self._parse_table(self._navigate(page, PAGES['exams']), TABLE_IDS['exams'])
        for row in rows:
            db['exams'].replace_one(
                {"code": row.get('DERS KODU', ''), "type": row.get('SINAV TÜRÜ', '')},
                {
                    "code": row.get('DERS KODU', ''),
                    "subject": row.get('DERS ADI', ''),
                    "type": row.get('SINAV TÜRÜ', ''),
                    "date": row.get('SINAV TARİHİ', ''),
                    "hour": row.get('SAATİ', ''),
                    "location": row.get('SINAV YERİ', '')
                },
                upsert=True
            )

# Getting the most recent 25 announcements. Older announcements are not relevant.
    def _get_announcements(self, page):
        soup = self._navigate(page, PAGES['announcements'])
        rows = self._parse_table(soup, TABLE_IDS['announcements'])[:25]

        db['announcements'].delete_many({})
        for row in rows:
            db['announcements'].insert_one({
                "title": row.get('BAŞLIK', ''),
                "content": row.get('MESAJ', ''),
                "date": row.get('GÖNDERİM TARİHİ', '')
            })
                