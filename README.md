# AICTE APAAR-Based Student Data Management & Verification Portal

A centralized platform for managing, validating, and verifying student enrolment records across educational institutions using APAAR/ABC IDs.

## Features

- **Role-Based Portals**:
  - **Institute**: Manage institution profile, upload bulk student data via CSV/XLSX, resolve validation flags, and view approved programme intake capacities.
  - **Admin**: Review flagged duplicate records, view institution directories, audit intake capacity utilization, and process verification queues.
  - **Super Admin**: National analytics, user management, policy configuration, and tamper-evident audit logging.
- **Data Integrity & Validation Engine**:
  - Syntax & format validation for APAAR IDs, academic years, seat categories, and enrolment numbers.
  - Duplicate detection across active enrolments within and between institutions.
  - Programme approved intake capacity enforcement with excess enrolment tracking.
- **Audit Logging**: Comprehensive activity tracking across all sensitive system actions with timestamps and actor tracking.

## Technology Stack

- **Frontend**: Vue 3, TypeScript, Vite, Tailwind CSS, Lucide Icons, Pinia, Vue Router
- **Backend**: Python 3, Flask, Flask-SQLAlchemy, Flask-CORS, Flask-JWT-Extended, Pandas, Marshmallow
- **Database**: SQLite (local development / prototyping)

---

## Quick Start (Single Click)

### On Windows
Simply double-click **`run.bat`** (or **`start.bat`**) in the root directory.

This automatically:
1. Starts the Flask backend at `http://127.0.0.1:5000`
2. Starts the Vue 3 frontend development server at `http://localhost:5173`
3. Launches the application in your default web browser

### Manual Execution

#### 1. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python seed.py       # Seeds demo institutions and user accounts
python run.py        # Starts backend on http://127.0.0.1:5000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev          # Starts frontend on http://localhost:5173
```

---

## Demo Credentials

| Role | Username | Password | Access Scope |
|---|---|---|---|
| **Super Admin** | `superadmin_demo` | `password123` | Full national administrative access & audit logs |
| **Admin** | `admin_demo` | `password123` | Institutional oversight, verification queues & reports |
| **Institute** | `institute_demo` | `password123` | College student records, batch upload & intake monitoring |

---

## Repository Structure

```
├── backend/
│   ├── app/
│   │   ├── models/           # SQLAlchemy database models
│   │   ├── routes/           # REST API endpoints (auth, students, institutions, etc.)
│   │   ├── services/         # Business logic & audit services
│   │   └── utils/            # Security & helper utilities
│   ├── requirements.txt      # Python dependencies
│   ├── run.py                # Backend entry point
│   └── seed.py               # Pre-seeded database populator
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI components & layouts
│   │   ├── router/           # Client-side routing with role guards
│   │   ├── services/         # Axios API clients
│   │   ├── stores/           # Pinia state stores
│   │   └── views/            # Dashboard & portal views
│   ├── package.json          # Frontend dependencies
│   └── vite.config.ts        # Vite configuration & proxy
├── run.bat                   # Single-click launcher for Windows
├── start.bat                 # Alternative launcher
└── run.py                    # Cross-platform Python launcher
```
