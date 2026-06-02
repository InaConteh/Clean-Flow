# CleanFlow SL

Water security platform for Sierra Leone — bridging web dashboards with SMS for low-bandwidth communities.

## Architecture

- **Frontend:** React + Tailwind CSS + Leaflet.js
- **Backend:** Flask REST API (Gunicorn in production)
- **Database:** PostgreSQL (managed locally with pgAdmin)
- **SMS:** Africa's Talking (inbound webhook + outbound messaging)
- **Workers:** Celery + Redis (prediction broadcasts, async SMS)

See `docs/` references in the repo root (TRD, Design System, Architecture diagram).

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

| Service  | URL                    |
|----------|------------------------|
| Web UI   | http://localhost:8080  |
| API      | http://localhost:5000  |
| Health   | http://localhost:5000/health |
| pgAdmin  | http://localhost:5050  |

pgAdmin login:

- Email: `admin@cleanflow.local`
- Password: `cleanflow`

Register the database server in pgAdmin with:

- Host: `db`
- Port: `5432`
- Database: `cleanflow`
- Username: `cleanflow`
- Password: `cleanflow`

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://cleanflow:cleanflow@localhost:5432/cleanflow
flask --app wsgi db upgrade
python seed.py
flask --app wsgi run --debug
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 (API proxied to port 5000).

## API endpoints

| Endpoint            | Method | Description                          |
|---------------------|--------|--------------------------------------|
| `/api/sources`      | GET    | Water sources as GeoJSON             |
| `/api/report`       | POST   | Submit issue report (web)            |
| `/api/sms/callback` | POST   | Africa's Talking inbound SMS         |
| `/api/tips`         | GET    | Educational content                  |
| `/api/auth/login`   | POST   | Admin JWT login (scaffold)           |
| `/api/repairs`      | GET    | Repair cases (JWT required)          |

### SMS commands

- `STATUS WELL123` — current source status
- `CAUSE WELL123 BROKEN_PUMP` — report an issue
- `TIPS` — educational message

## Environment variables

Copy `.env.example` to `.env` and set Africa's Talking credentials for live SMS.

## License

MIT — see [LICENSE](LICENSE).
