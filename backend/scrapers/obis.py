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

    def scrape_all(self):
        # connects to an already-running Chrome session the user logged into manually
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
        # navigates to the given OBIS page and returns a BeautifulSoup object
        page.goto(BASE_URL + route)
        page.wait_for_load_state('networkidle')
        return BeautifulSoup(page.content(), 'html.parser')

    def _parse_table(self, soup, table_id):
        # finds the table by id, extracts headers and rows, returns list of dicts
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

    def _get_courses(self, page):
        soup = self._navigate(page, PAGES['courses'])
        rows = self._parse_table(soup, TABLE_IDS['courses'])
        for row in rows:
            db['subjects'].insert_one(row)

    def _get_grades(self, page):
        soup = self._navigate(page, PAGES['grades'])
        rows = self._parse_table(soup, TABLE_IDS['grades'])
        for row in rows:
            db['grades'].insert_one(row)

    def _get_attendance(self, page):
        soup = self._navigate(page, PAGES['attendance'])
        rows = self._parse_table(soup, TABLE_IDS['attendance'])
        for row in rows:
            db['attendance'].insert_one(row)

    def _get_exams(self, page):
        soup = self._navigate(page, PAGES['exams'])
        rows = self._parse_table(soup, TABLE_IDS['exams'])
        for row in rows:
            db['exams'].insert_one(row)

    def _get_announcements(self, page):
        soup = self._navigate(page, PAGES['announcements'])
        rows = self._parse_table(soup, TABLE_IDS['announcements'])
        for row in rows:
            db['announcements'].insert_one(row)
