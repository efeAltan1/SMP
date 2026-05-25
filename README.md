# SMP - Student Management Platform

SMP is a personal academic dashboard that pulls the crucial data from my university's student portal and puts it all in one place. The real portal works, but it's slow, scattered across multiple pages and tabs, and gives you no tools to actually work and visualize your data.

## 1 - What is it?

A full-stack web app that syncs with OBIS (obis.gelisim.edu.tr) and gives you a clean view of your academic life. You hit Sync, it logs in, grabs everything, and stores it locally. From there the app is fast and works entirely off the local database.

It currently tracks:

- Courses and credits
- Grades
- Attendance
- Exams
- Announcements

## 2 - What does it cover that OBIS doesn't?

- **Unified dashboard** — everything in one view. OBIS has a separate page for every single information, which makes it hard to navigate through.
- **Attendance rate per course** — OBIS shows absences as a count. SMP converts it to a percentage and flags courses where you're close to the limit
- **Upcoming exams and deadlines** — filtered and sorted views so you actually see what's next, not just a full calendar dump
- **Analytics** — grade distribution, attendance trends, per-subject breakdowns. None of this exists in the portal.

## 3 - Stack

**Backend:** Python 3.11 + Flask + pymongo + flask-cors + python-dotenv + pandas + numpy + playwright + beautifulsoup4

**Database:** MongoDB Atlas (Free Tier M0)

**Frontend:** React 18 (Vite) + axios + react-router-dom

**Deploy:** Render (backend) + Vercel (frontend)

## 4 - Architecture

```
React (Vercel)
    ↓ HTTP/JSON
Flask API (Render)
    ↓ pymongo
MongoDB Atlas
    ↑
scrapers/obis.py
    ↑
OBIS (obis.gelisim.edu.tr)
```

For more detailed information, please check out the [ARCH.md](ARCH.md) file.

## 5 - Structure

```
smp/
├── backend/
│   ├── app.py              # Flask entry point, registers all blueprints
│   ├── config.py           # MongoDB connection and db singleton
│   ├── models/             # BaseModel + one model per collection
│   ├── routes/             # One blueprint per resource + sync.py
│   ├── scrapers/           # obis.py → Playwright + BeautifulSoup
│   └── utils/              # Validators, analytics helpers, CSV exporter
└── frontend/
    └── src/
        ├── api/            # Axios wrappers for every endpoint
        ├── components/     # Reusable UI components
        └── pages/          # One page per section of the dashboard
```
