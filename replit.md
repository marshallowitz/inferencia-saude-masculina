# Engine de Inferência em Saúde Masculina

A clinical decision support tool (v3) that transforms patient clinical data (exams, scales, and history) into traceable epidemiological inferences for male health using a custom α-weighted model coverage formula.

## Architecture

The project has two layers:

**Marketing / static pages** — served directly by Flask:
- `index.html` — Landing page / commercial pitch
- `saude_engine_v3.html` — Public static engine demo (V3)
- `docs_saude_v3.html` — Technical documentation
- `grafo_saude_v2.html` — Interactive inference graph
- `about_saude.html` — About page (Sofia Marshallowitz)

**Full application** — authenticated multi-user app at `/app`:
- `app.html` — Single-page app (SPA) with all screens
- `server.py` — Flask backend with SQLite database
- `health.db` — SQLite database (created on first run)

## App Features

- **Role selection**: Doctor or Patient on first access
- **Auth**: Register / Login (session-based, password hashed with SHA-256)
- **Patient flow**: Enter clinical data → run engine → save record → view history
- **Doctor flow**: Search patients by email, view patient list, see chronological records, run engine for any patient
- **Engine**: Full N1 (15 models) / N2 (9 models) / N3 (4 meta-inferences) calculation in JS client-side
- **Storage**: All records stored in SQLite (`health.db`)

## Database Schema

```sql
users (id, name, email, password_hash, role, created_at)
records (id, patient_id, doctor_id, input_data JSON, results JSON, notes, created_at)
doctor_patients (doctor_id, patient_id)
```

## Tech Stack

- **Backend**: Python / Flask (session-based auth, REST API)
- **Database**: SQLite (via Python built-in `sqlite3`)
- **Frontend**: Vanilla JS SPA (no framework), HTML5, CSS3
- **Fonts**: Google Fonts (Syne, Source Serif 4, DM Sans)
- **Shared**: `shared.js` + `shared.css` for consistent nav across all pages

## Running the Project

```
python3 server.py
```

Workflow: "Start application" → `python3 server.py` → port 5000

## API Routes

```
POST /api/auth/register        Register new user (name, email, password, role)
POST /api/auth/login           Login (email, password)
POST /api/auth/logout          Clear session
GET  /api/me                   Current user info

GET  /api/records              Patient: get own records
POST /api/records              Create record (patient_id optional for doctor)

GET  /api/patients             Doctor: list linked patients
GET  /api/patients/search      Doctor: search patient by email
POST /api/patients/:id/link    Doctor: link patient
GET  /api/patients/:id/records Doctor: get patient's records
```

## Deployment

Flask app — requires "autoscale" deployment (not static).
