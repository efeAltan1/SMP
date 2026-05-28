# ARCH.md - Detailed Design Decisions

This file covers the why behind how SMP is built. If you're reading the code and wondering why something is done a certain way, it's probably explained here.

## 1 - Why Flask over FastAPI?

Flask is simpler and has less magic. FastAPI's automatic validation and async model are useful in production systems but add overhead for a project this size. Flask does exactly what you tell it to, nothing more. That makes it easier to reason about when something breaks.

## 2 - Why MongoDB over SQL?

A rigid SQL schema would require constant migration work every time the scraper returns something slightly different. MongoDB handles that naturally. Schema flexibility was the deciding factor.

## 3 - Why upsert instead of insert?

Every sync re-fetches all data from OBIS. If we used plain inserts, every sync would create duplicate records. Upsert checks whether the record already exists and updates it if it does, inserts it if it doesn't. This means you can sync as many times as you want without corrupting the database.

## 4 - Why does GPA never get stored?

Storing a calculated value creates two sources of truth. If a grade changes after a sync, the stored GPA would be stale until something explicitly recalculates and updates it. By always computing GPA on the fly from the raw grade data using NumPy, it's always accurate and there's nothing to keep in sync.

## 5 - The BaseModel pattern

Routes never talk to MongoDB directly. Every collection has a corresponding model class that inherits from `BaseModel`. All database reads and writes go through these classes.

This keeps the routes clean and makes the database logic reusable. If the way data is stored changes, you update the model — the route doesn't care.

`BaseModel` provides:

- `save()` — upserts the document
- `to_dict()` — serializes to JSON-safe dict (handles ObjectId → str conversion)
- `validate()` — checks required fields before any write
- `find_by_id()` — class method, fetches one document by ID
- `find_all()` — class method, fetches all documents in the collection

The `db` object is a module-level singleton imported from `config.py`. It is not passed into model instances — every model imports it directly. This avoids threading issues and keeps instantiation simple.

## 6 - Route ordering in Flask

Static routes must be registered before dynamic routes in every blueprint. For example:

```python
@bp.route('/gpa')        # this must come first
@bp.route('/<grade_id>') # this must come second
```

If the dynamic route is registered first, Flask matches `gpa` as a value for `grade_id` and the `/gpa` endpoint silently breaks with no error. This is a Flask-specific gotcha, not obvious from the docs.

## 7 - Why Playwright instead of requests?

OBIS is ASP.NET WebForms. Every page carries hidden form fields (`__VIEWSTATE`, `__EVENTVALIDATION`) that are generated server-side and tied to an active browser session. A plain HTTP request with `requests` cannot replicate this — the tokens expire immediately and the server rejects the request.

Playwright runs a real headless browser. It maintains the session exactly as a real user would, handles the token lifecycle automatically, and navigates between pages without any manual token management. BeautifulSoup then parses the loaded HTML.

## 8 - CORS configuration

CORS is configured with a specific origin pulled from the `FRONTEND_URL` environment variable:

```python
CORS(app, origins=[os.getenv('FRONTEND_URL')])
```

Never `CORS(app)` with no arguments — that opens the API to any origin, which is a security risk even for a personal project.

## 9 - Standard response format

Every endpoint returns the same shape:

```json
{ "status": "ok", "data": {} }
{ "status": "error", "message": "..." }
```

This makes error handling on the frontend predictable. Every axios call checks `status` first, always knows where the payload is, and never has to guess the shape of a response.

## 10 - ObjectId serialization

MongoDB stores document IDs as `ObjectId` objects, which are not JSON-serializable. Every `to_dict()` method explicitly converts `_id` to a string:

```python
doc['_id'] = str(doc['_id'])
```

Without this, any route that returns a document will throw a serialization error. It's handled once in `BaseModel.to_dict()` so no route or subclass has to think about it.

## 11 - Why scraping?

Student portal has no API. It's ASP.NET WebForms — every page uses server-side tokens (`__VIEWSTATE`, `__EVENTVALIDATION`) tied to a live session. A plain HTTP request won't work. Playwright runs a real headless browser that handles all of that automatically. BeautifulSoup parses the page once it loads.

## 12 - How Do I handle OBIS credentials?

OBIS credentials (OBIS_USERNAME, OBIS_PASSWORD) live in backend/.env. They never touch the frontend. The user doesn't enter their credentials manually, they're set in the environment once and stay there.

When the user hits Sync, the frontend sends a plain [POST /api/sync] with no body. The backend reads the credentials from environment variables and passes them directly to the Playwright scraper. They never travel over the network, never get stored in MongoDB, and never appear in any API response.

## 13 - Learnings & Fixes

While building SMP, several unnaccounted for problems came up that needed out of box thinking to fix. This section logs what's broken, why it broke, and how it was fixed. 

- **reCaptcha**: Auto-login was the original plan to get into the OBIS system. But I did not account for the Google reCaptcha that OBIS uses. The first solution was to try and use 'playwright_stealth' to mask the browser fingerprint. But it caused two problems; with stealth, the challenge didn't render client-side, and without stealth, Google served an image challenge that the bot could not solve. The solution was the CDP attachment, where the user logs into OBIS manually in a remote debugging Chrome window, and Playwright attaches itself to that existing session without touching the flow.

- **Nested Header Tables**: I tried to standardize data collection by reading header columns and getting the table_id data underneath. But several OBIS tables have a semester label as the first row, which then push the real column header down 1 row. The solution was to creating '_find_header_row()', which scans rows until it finds one containing 'DERS KODU', then treats that as the real header.

- **Attendance Field Column Misalignment**: The attendance table had merged header cells, which meant that the header row had fewer cells than the data rows. Using 'zip(headers, cells)' shifted every value into the wrong columns. The solution was to hardcode column positions based on manual inspection of the HTML code, and filtering rows with a rigid course code regex to discard junk rows.

- **Subject Scraper Rework**: The original plan was to get the subject scraper to target 'Alacagim_Dersler.aspx', but it had the same nested header table problem. The solution was to change the scraper path to 'Ders_Program.aspx.', which returned cleaner and more granular data: course code, name, day, time slot, building, room, teacher.

- **Announcements Upsert Collision**: All announcements share the same title (Duyuru/Announcement: OBİS) and have an empty date field. Upserting on those keys means every announcement overwrites the same slot, leaving only one record. The solution was to clear the collection with delete_many before each sync and use insert_one instead.

- **Sync HTTP Timeout**: The scraper navigates five OBIS pages sequentially. This takes 15-25 seconds. The problem was that the browser dropped the HTTP connection before Flask sent a response, and the frontend received a network error even though the scrape completed successfully. The solution was to running the scraper in a background thread and returning a 202 immediately. This then made the frontend polls 'GET /api/sync/status' every ~3 seconds until the status changed to 'done', 'partial', or 'error'.

## 14 - Scaling Beyond One User

SMP, currently, is built as a single-user, highly personalized tool. My school credentials are hardcoded in '.env', there is no auth layer, and the sync runs in a single Flask thread tied to one person's browser session. This was an intentional approach, because I wanted to keep the scope and the architecture design simple. However, if I were to extend the project to support multiple users, three main layers would have to change:

- **CDP Approach**: The entire reason CDP works is that a human solves the login manually, due to the Google reCaptcha system. At scale, you cannot have every user keep a Chrome tab open. Any multi-user architecture would need solve the login problem first, either through a CAPTCHA solving service (risky, and legally dubious) or supervised one-time login flow that stores the resulting session cookies (need to manage and work around cookie expiry cycles, timeout sessions).

- **Auth Layer and Credential Storage**: As it stands currently, OBIS credentials live in '.env' file and belong to a single person. At scale, each user would have their own credentials stored encrypted in the database, never exposed to any API call and response.

- **Scrape Queue**: With multiple users trying to sync at the same time, playwright won't be able to run in a single Flask thread. Each sing request would need to be queued and assigned to a dedicated worker process with its own playwright instance, so the users can sync at the same time. The approach I would take for this would be the standard Celery with a Redis broker. 