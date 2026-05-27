from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from config import db


BASE_URL = "https://obis.gelisim.edu.tr"

TABLE_IDS = {
    "courses": "dtNot_Dokum",
    "grades": "dtList_Sinif_grdTanim_0",
    "attendance": "dtList_Sinif",
    "exams": "grdTanim",
    "announcements": "grdBildirimList"
}

PAGES = {
    "courses": "/Alacagim_Dersler.aspx",
    "grades": "/Ders_Notlari.aspx",
    "attendance": "/Devamsizlik.aspx",
    "exams": "/Sinav_Tarihlerim.aspx",
    "announcements": "/Bildirimler.aspx"
}


class OBISScraper:

# Attaches to an existing Chrome session via CDP. User must launch Chrome with
# --remote-debugging-port=9222 and log in to OBIS manually before calling sync.
    def scrape_all(self):
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.pages[0]
            self._get_courses(page)
            self._get_grades(page)
            self._get_attendance(page)
            self._get_exams(page)
            self._get_announcements(page)

    def _navigate(self, page, route):
        page.goto(BASE_URL + route)
        page.wait_for_load_state('networkidle')
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

# Temporarily using insert_one to inspect raw column names in Atlas.
# Will switch to replace_one (upsert) once real field names are confirmed.
    def _get_courses(self, page):
        rows = self._parse_table(self._navigate(page, PAGES['courses']), TABLE_IDS['courses'])
        for row in rows:
            db['subjects'].insert_one(row)

    def _get_grades(self, page):
        rows = self._parse_table(self._navigate(page, PAGES['grades']), TABLE_IDS['grades'])
        for row in rows:
            db['grades'].insert_one(row)

    def _get_attendance(self, page):
        rows = self._parse_table(self._navigate(page, PAGES['attendance']), TABLE_IDS['attendance'])
        for row in rows:
            db['attendance'].insert_one(row)

    def _get_exams(self, page):
        rows = self._parse_table(self._navigate(page, PAGES['exams']), TABLE_IDS['exams'])
        for row in rows:
            db['exams'].insert_one(row)

    def _get_announcements(self, page):
        rows = self._parse_table(self._navigate(page, PAGES['announcements']), TABLE_IDS['announcements'])
        for row in rows:
            db['announcements'].insert_one(row)
