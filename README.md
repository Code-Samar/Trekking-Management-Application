# Trekking Management Application (TMA) — V2

Full-stack app: **Flask** (API) + **Vue 3 / Vite** (UI) + **SQLite** + **Redis** + **Celery**.

This has been built and tested end-to-end (login for all 3 roles, trek CRUD,
booking/cancellation with slot management, staff trek management, Redis
caching, and all three Celery jobs) on a local machine equivalent setup.

## Folder structure

```
Trekking Management Application _23f3001032/
├── backend/
│   ├── app.py              # Flask app factory, blueprint registration, admin bootstrap
│   ├── config.py            # All config (DB, JWT, Redis, Celery, mail)
│   ├── extensions.py         # db, jwt, cache, celery singletons
│   ├── models.py             # User (unified), Trek, Booking
│   ├── tasks.py               # 3 Celery tasks (reminders, monthly report, CSV export)
│   ├── celery_worker.py        # Celery entrypoint + beat schedule
│   ├── seed_demo_data.py        # Optional: populate demo staff/users/treks
│   ├── requirements.txt
│   ├── routes/
│   │   ├── auth.py            # login (all roles) + register (trekker only)
│   │   ├── admin.py           # treks, staff, users, dashboard, bookings, reports
│   │   ├── staff.py           # assigned treks, slots/status, participants
│   │   └── user.py            # browse/book/cancel, history, profile, CSV export
│   └── utils/decorators.py     # @role_required RBAC decorator
└── frontend/
    ├── src/
    │   ├── main.js, App.vue
    │   ├── router/index.js      # role-based route guards
    │   ├── store/auth.js         # Pinia auth store (JWT)
    │   ├── api/index.js           # axios instance w/ JWT interceptor
    │   ├── components/AppLayout.vue
    │   └── views/
    │       ├── Login.vue, Register.vue
    │       ├── admin/  (Dashboard, Treks, Staff, Users, Bookings, Reports)
    │       ├── staff/  (Dashboard, TrekManage)
    │       └── user/   (Dashboard, BrowseTreks, History, Profile)
    ├── package.json, vite.config.js, index.html
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- Redis server installed locally

## 1. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        
pip install -r requirements.txt
```

Start Redis (separate terminal):
```bash
redis-server
```

Run the Flask app (this also creates the SQLite DB + the single Admin
account programmatically on first run):
```bash
python3 app.py
```
Backend runs on **http://127.0.0.1:5001/api/health**. Watch the console — it prints
the admin login on first run:
```
[SETUP] Admin created -> email: admin@tma.com  password: Admin@123
```

Optional — seed some demo staff/users/treks for a quick demo:
```bash
python3 seed_demo_data.py
```

## 2. Celery (background jobs) — 2 more terminals

Worker (Mac needs `--pool=solo`; Linux can drop that flag):
```bash
cd backend
source venv/bin/activate
celery -A celery_worker.celery worker --loglevel=info --pool=solo
```

Beat scheduler (drives the daily reminder + monthly report jobs):
```bash
cd backend
source venv/bin/activate
celery -A celery_worker.celery beat --loglevel=info
```

> Without SMTP credentials set (`TMA_MAIL_USERNAME` / `TMA_MAIL_PASSWORD`
> env vars), emails are just logged to the console instead of actually
> sent — so the app is fully runnable and demoable with zero external
> service setup. Set `MAIL_ENABLED = True` in `config.py` plus those env
> vars to send real email.

## 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```
Frontend runs on **http://localhost:5173** and proxies `/api/*` calls to
the Flask backend automatically (see `vite.config.js`).

## Login

| Role    | How to get an account                          |
|---------|-------------------------------------------------|
| Admin   | Pre-created automatically — see console output on first run |
| Staff   | Created by Admin from **Admin → Trekking Staff → Create New Trekking Staff** |
| Trekker | Self-register from the **Register as User** link on the login page |

## Notes on design decisions

- **Unified user model**: one `User` table with a `role` column
  (`admin` / `staff` / `trekker`) plus a `status` column
  (`active` / `blacklisted`), per the spec's "unified user model" requirement.
- **Slot management**: booking a trek atomically decrements
  `available_slots`; cancelling restores it. Overbooking and duplicate
  active bookings are blocked in `routes/user.py`.
- **Caching**: trek listings (`/api/admin/treks`, `/api/user/treks`) are
  cached in Redis for 60s and invalidated on any trek/booking write.
- **Celery jobs**:
  - `send_daily_reminders` — runs daily at 08:00, emails/logs reminders to
    users with a trek starting the next day.
  - `send_monthly_report` — runs on the 1st of each month, builds an HTML
    report (treks conducted, participants, popular treks) and emails it to
    Admin; also saved under `backend/reports/`.
  - `export_booking_history_csv` — user-triggered from the History page,
    runs async, writes a CSV under `backend/exports/`, downloadable via
    `/api/downloads/exports/<filename>`.
