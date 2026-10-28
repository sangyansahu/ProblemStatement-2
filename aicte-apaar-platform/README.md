# AICTE APAAR-Based Student Data Management & Verification System

An authoritative, government-style digital prototype enabling technical and higher education institutions to submit student enrolment data in bulk, detect discrepancies, prevent duplicate candidate enrolments, and allow public verification of issued credentials via privacy-preserving QR codes.

All data is **SYNTHETIC**. All APAAR checks go through a **MOCK provider** labeled **"Simulated"**.

---

## 1. Tech Stack (Fixed)

- **Frontend**: React + TypeScript + Vite, Tailwind CSS, Recharts, Axios, React Router Dom
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic (+ pydantic-settings), pandas, openpyxl, python-multipart, httpx, PyJWT, cryptography, qrcode[pil]
- **Database**: PostgreSQL 16
- **Auth**: Keycloak (OIDC) / JWT Bearer with pre-seeded realm and role-enforcement on every endpoint
- **Tests**: pytest + HTTPX (backend) & Playwright (end-to-end happy-path)
- **Deployment**: Docker Compose (`db`, `keycloak`, `backend`, `frontend`)

---

## 2. Setup & Execution

### Option A: Running with Docker Compose (Recommended)

```bash
cd aicte-apaar-platform
docker compose up --build
```

Services started:
- **Frontend**: http://localhost:5173
- **Backend API & Swagger Docs**: http://localhost:8000/docs
- **Keycloak Admin**: http://localhost:8080 (admin / admin)
- **PostgreSQL 16**: localhost:5432 (aicte / aicte_password)

### Option B: Running Standalone (Local Development)

#### 1. Backend Setup:
```bash
cd aicte-apaar-platform/backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Note: When `DATABASE_URL` is omitted, the backend defaults to `sqlite:///./aicte_platform.db` and automatically creates all tables and seeds 5 fictional institutions and test accounts upon first startup.*

#### 2. Frontend Setup:
```bash
cd aicte-apaar-platform/frontend
npm install
npm run dev
```

#### 3. Running Backend Tests:
```bash
cd aicte-apaar-platform
python -m pytest backend/tests -q
```

---

## 3. Demo User Accounts

The platform includes pre-seeded demo accounts across the 5 permitted roles:

| Username | Role | Organization | Permissions / Scope |
|---|---|---|---|
| `aicte_admin` | `aicte_admin` | AICTE Headquarters | National analytics, all validation cases, XLSX reports |
| `inst_admin` | `institution_admin` | Delhi Inst of Adv Eng & Tech | View own records, resolve/dismiss validation cases, issue credentials |
| `inst_operator` | `institution_operator` | Delhi Inst of Adv Eng & Tech | Upload CSV/XLSX batches, edit permitted student fields |
| `verifier` | `verifier` | External Verification Agency | Verify credentials; **cannot** read student profiles |
| `auditor` | `auditor` | Compliance Audit Wing | Read-only audit trail inspection and national oversight |

*Password for all demo accounts in Keycloak / SSO:* `password123`

---

## 4. End-to-End Demo Script (4 Steps)

### Step 1: Institution Operator Uploads Student Data
1. Navigate to http://localhost:5173/login.
2. Select **Institution Operator** and click **Sign in**.
3. Navigate to **Upload Students** in the top navigation.
4. Select `sample_data/synthetic_students.csv` and click **Upload**.
5. The synchronous pipeline validates the file against row-level rules, detects duplicate candidate entries, performs row-locking capacity verification, and displays the **Batch Validation Results** table with accepted, rejected, and flagged items. Click **Download report** to export the row results.

### Step 2: Review Discrepancies and Resolve Cases
1. Click **Logout** and log in as **Institution Admin** (`inst_admin`).
2. Navigate to **Validation Cases**.
3. Review flagged cases (e.g. `CROSS_INSTITUTION_ACTIVE_CONFLICT` or `INTAKE_EXCEEDED`).
4. Click **Resolve** on an open case, enter a mandatory justification note, and click **Confirm Resolution**. The case is marked resolved and an immutable audit log entry is written.

### Step 3: Monitor National AICTE Analytics
1. Click **Logout** and log in as **AICTE Administrator** (`aicte_admin`).
2. Navigate to **National Dashboard**.
3. Observe the 4 real-time KPI metrics (*Institutions Reporting*, *Students Reported*, *Records Flagged*, *Pending Reviews*), the Recharts bar chart of enrolment by academic year, and the 10 most recent validation discrepancies.
4. Navigate to **Reports** and click **Download Enrolment Report (XLSX)**. Verify that raw APAAR IDs are excluded and masked tokens are exported.

### Step 4: Public Privacy-Preserving Credential Verification
1. As **Institution Admin**, navigate to **Verify Credential**, select an enrolled student, and click **Generate QR**.
2. Copy the generated opaque reference (e.g. `CR-sample-ref...`).
3. Click **Logout** and open `http://localhost:5173/verify/<opaque-ref>` without logging in.
4. Verify that the public verification outcome displays **ONLY**:
   - Issuing Institution
   - Credential Type
   - Status (`valid` / `revoked` / `expired`)
   - Issued & Verified Timestamps
5. Confirm that **NO** personal student information (name, raw APAAR ID, DOB, or phone) is revealed.

---

## 5. Architectural Assumptions & Technical Notes

1. **Synthetic Privacy Protection**: Raw APAAR IDs are never stored in the database or written to logs. The backend computes a deterministic keyed HMAC-SHA256 hash (`apaar_id_token`) using a secret key loaded strictly from environment variables.
2. **Minimal Government Aesthetic**: Designed in accordance with official National Testing Agency (NTA) & AICTE design standards: plain white card backgrounds, 1 px borders, high-contrast typography, deep navy primary headers, saffron active indicators, and a top 4 px national tricolour strip.
3. **Database Flexibility**: SQLAlchemy models use platform-agnostic `GUID` abstractions with native PostgreSQL UUID in production and SQLite string fallback for standalone local unit tests.
4. **Idempotent Ingestion**: Upload batches record SHA-256 checksums. Re-uploading an identical file returns the existing batch and prevents duplicate admission insertions.
5. **No Microservices / Celery**: In compliance with the prompt, all batch processing and validation run synchronously within configured limits (10 MB file size and 5,000 rows).
