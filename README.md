# GetYourPrint — Flask + Supabase

A campus printing web application rebuilt with **Python/Flask** for the backend and **vanilla HTML/CSS/JS** for the frontend, keeping Supabase as the database and storage provider.

---

## Stack

| Layer      | Technology |
|------------|------------|
| Backend    | Python 3.11 + Flask |
| Frontend   | Vanilla HTML / CSS / JavaScript |
| Database   | Supabase (PostgreSQL) |
| Storage    | Supabase Storage (`print-files` bucket) |
| PDF Parsing| PDF.js (CDN, client-side) |

---

## Project Structure

```
campus-print/
├── app.py                  # Flask application & API routes
├── requirements.txt
├── .env.example            # Copy to .env and fill in credentials
└── templates/
    ├── base.html           # Shared layout, CSS variables, fonts
    ├── navbar.html         # Sticky nav with logout (included in pages)
    ├── auth.html           # Login / Sign-up page
    ├── student.html        # Student dashboard
    └── staff.html          # Staff dashboard
```

---

## Quick Start

### 1. Clone / copy the project

```bash
cd campus-print
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
SECRET_KEY=some-random-secret-string
```

### 5. Supabase setup (same as the original project)

Your Supabase project needs:

**Table: `users`**
```sql
create table users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  password text not null,
  is_staff boolean default false,
  created_at timestamptz default now()
);
```

**Table: `print_job`**
```sql
create table print_job (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id),
  file_url text,
  copies int default 1,
  page_count int default 1,
  is_colour boolean default false,
  is_double_sided boolean default false,
  total_price numeric(10,2) default 0,
  status text default 'pending',
  created_at timestamptz default now()
);
```

**Storage bucket:** Create a public bucket named `print-files`.

### 6. Run the app

```bash
python app.py
```

Visit [http://localhost:5000](http://localhost:5000)

---

## API Endpoints (Flask → Supabase)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/login` | Auth page |
| GET | `/student` | Student dashboard |
| GET | `/staff` | Staff dashboard |
| POST | `/api/login` | Authenticate user |
| POST | `/api/signup` | Register new user |
| GET | `/api/jobs` | Fetch jobs (student or staff view) |
| POST | `/api/jobs` | Create a new print job |
| PATCH | `/api/jobs/<id>/status` | Update job status |
| DELETE | `/api/jobs/<id>` | Delete a job |
| POST | `/api/storage/sign` | Get signed upload URL for PDF |

---

## Features

- **Login / Sign-up** with role selection (Student / Staff)
- **Student Dashboard**
  - Drag-and-drop PDF upload
  - Auto page-count detection via PDF.js (client-side)
  - Live cost calculator (colour, double-sided, copies)
  - Job status tracking
- **Staff Dashboard**
  - View all jobs with student email, file info, pricing
  - Filter by status (All / Pending / Printing / Completed)
  - One-click status transitions: Pending → Printing → Completed
  - Delete collected jobs
  - Auto-refresh every 15 seconds
