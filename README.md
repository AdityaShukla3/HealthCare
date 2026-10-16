# Healthcare Backend System

A robust, secure backend system for a healthcare application built with **Django**, **Django REST Framework (DRF)**, **PostgreSQL**, and **JWT Authentication** (`djangorestframework-simplejwt`).

---

## 📋 Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture & Folder Structure](#architecture--folder-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Step 1: Clone & Navigate](#step-1-clone--navigate)
  - [Step 2: Start PostgreSQL with Docker](#step-2-start-postgresql-with-docker)
  - [Step 3: Setup Python Environment](#step-3-setup-python-environment)
  - [Step 4: Configure Environment Variables](#step-4-configure-environment-variables)
  - [Step 5: Run Database Migrations](#step-5-run-database-migrations)
  - [Step 6: Seed Demo Data (Optional)](#step-6-seed-demo-data-optional)
  - [Step 7: Start Development Server](#step-7-start-development-server)
- [API Documentation](#api-documentation)
  - [Interactive Swagger / OpenAPI UI](#interactive-swagger--openapi-ui)
  - [1. Authentication APIs](#1-authentication-apis)
  - [2. Patient Management APIs](#2-patient-management-apis)
  - [3. Doctor Management APIs](#3-doctor-management-apis)
  - [4. Patient-Doctor Mapping APIs](#4-patient-doctor-mapping-apis)
- [Testing](#testing)
- [Postman Collection](#postman-collection)

---

## 🚀 Features
- **JWT Authentication**: Secure user registration, login, and token refresh using `djangorestframework-simplejwt`.
- **Custom User Model**: Authenticate with email as username, storing user name and hashed passwords securely.
- **Patient Management**: Full CRUD operations with user-level isolation (users only access and manage patients they created).
- **Doctor Management**: Full CRUD operations for registered medical specialists with creator-restricted update/delete permissions (`IsDoctorCreatorOrReadOnly`).
- **Patient-Doctor Mapping**: Assign doctors to patients with strict patient ownership isolation, duplicate-assignment prevention constraints, deterministic lookup by patient ID, and unassign capabilities.
- **Production-Ready PostgreSQL**: Backed by a dedicated PostgreSQL container with persistent volume storage (with optional SQLite support for testing).
- **Automated Test Suite**: 22 unit and integration tests covering authentication, user ownership isolation, permissions, models, validations, and edge cases.
- **Interactive Documentation**: Integrated Swagger UI & ReDoc via `drf-spectacular`.

---

## 🛠️ Tech Stack
- **Framework**: Django 5.1 & Django REST Framework (DRF)
- **Database**: PostgreSQL 16 (running via Docker)
- **Authentication**: JWT (`djangorestframework-simplejwt`)
- **API Documentation**: OpenAPI 3.0 / Swagger UI (`drf-spectacular`)
- **Environment Management**: `python-dotenv`
- **CORS**: `django-cors-headers`

---

## 📂 Architecture & Folder Structure

```
HealthCare/
├── accounts/                  # User model, custom manager, registration, JWT login
│   ├── models.py              # Custom User model (email, name, password)
│   ├── serializers.py         # Registration & JWT token serializers
│   ├── views.py               # RegisterView, LoginView
│   ├── urls.py                # /api/auth/...
│   └── tests.py               # Auth test cases
├── patients/                  # Patient CRUD
│   ├── models.py              # Patient model (created_by foreign key)
│   ├── serializers.py         # PatientSerializer with validations
│   ├── views.py               # PatientViewSet (scoped to request.user)
│   ├── urls.py                # /api/patients/...
│   └── tests.py               # Patient test cases
├── doctors/                   # Doctor CRUD
│   ├── models.py              # Doctor model (specialization, experience)
│   ├── serializers.py         # DoctorSerializer with phone & exp validation
│   ├── views.py               # DoctorViewSet with search & filter
│   ├── urls.py                # /api/doctors/...
│   └── tests.py               # Doctor test cases
├── mappings/                  # Patient-Doctor relationships
│   ├── models.py              # PatientDoctorMapping with UniqueConstraint
│   ├── serializers.py         # Serializer with duplicate checks
│   ├── views.py               # MappingListCreateView, MappingDetailView
│   ├── urls.py                # /api/mappings/...
│   └── tests.py               # Mapping test cases
├── healthcare_backend/        # Project settings and root routing
│   ├── settings.py            # PostgreSQL, SimpleJWT, DRF config
│   ├── urls.py                # Root router & Swagger endpoints
│   ├── wsgi.py
│   └── asgi.py
├── docker-compose.yml         # PostgreSQL 16 Docker service configuration
├── seed_data.py               # Helper script to populate demo data
├── postman_collection.json    # Complete Postman Collection export
├── requirements.txt           # Project dependencies
├── .env                       # Local environment variables (git-ignored)
├── .env.example               # Template environment variables
└── manage.py
```

---

## ⚡ Getting Started

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (or a local PostgreSQL server)

### Step 1: Clone & Navigate
```bash
cd HealthCare
```

### Step 2: Start PostgreSQL with Docker
Start the PostgreSQL container in background:
```bash
docker compose up -d
```
Verify the container is healthy:
```bash
docker ps
```

### Step 3: Setup Python Environment
Create and activate a virtual environment:

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create your local `.env` file by copying `.env.example`. Update the values if needed.

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

The template `.env.example` provides ready-to-run development defaults:
```ini
SECRET_KEY=django-insecure-h3althc@re-s3cur3-k3y-2026-drf-jwt-pg
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432

# CORS Configuration (Optional, defaults to True for local dev)
CORS_ALLOW_ALL_ORIGINS=True
```

> [!IMPORTANT]
> - **`SECRET_KEY`**: Required. The application enforces fail-loud behavior (`ImproperlyConfigured`) if `SECRET_KEY` is missing in the environment.
> - **`DEBUG`**: Defaults safely to `False` if not explicitly defined as `True` in `.env`.
> - **`CORS_ALLOW_ALL_ORIGINS`**: Set to `True` for development and Postman testing ease. For production deployments, set this to `False` and define explicit whitelist origins via `CORS_ALLOWED_ORIGINS`.

### Step 5: Run Database Migrations
Apply migrations to PostgreSQL:
```bash
python manage.py migrate
```

### Step 6: Seed Demo Data (Optional)
Populate the database with sample doctors, patients, user accounts, and mappings:
```bash
python seed_data.py
```

**Default Seed Credentials:**
- **Staff User**: `doctor.staff@healthcare.com` / `Staff@123456`
- **Admin User**: `admin@healthcare.com` / `Admin@123456`

### Step 7: Start Development Server
```bash
python manage.py runserver
```
The server will start at `http://127.0.0.1:8000/`.

---

## 📖 API Documentation

### Interactive Swagger / OpenAPI UI
Once the server is running, visit:
- **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **ReDoc**: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- **OpenAPI Schema (JSON/YAML)**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

---

### 1. Authentication APIs

#### Register User
- **Endpoint**: `POST /api/auth/register/`
- **Permission**: `AllowAny`
- **Request Body**:
```json
{
  "name": "Jane Watson",
  "email": "jane.watson@healthcare.com",
  "password": "SecurePassword123!"
}
```
- **Response** (`201 Created`):
```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 3,
    "name": "Jane Watson",
    "email": "jane.watson@healthcare.com"
  },
  "tokens": {
    "refresh": "<refresh_jwt_token>",
    "access": "<access_jwt_token>"
  }
}
```

#### Login User
- **Endpoint**: `POST /api/auth/login/`
- **Permission**: `AllowAny`
- **Request Body**:
```json
{
  "email": "doctor.staff@healthcare.com",
  "password": "Staff@123456"
}
```
- **Response** (`200 OK`):
```json
{
  "refresh": "<refresh_jwt_token>",
  "access": "<access_jwt_token>",
  "user": {
    "id": 2,
    "name": "Medical Staff Officer",
    "email": "doctor.staff@healthcare.com"
  }
}
```

#### Token Refresh
- **Endpoint**: `POST /api/auth/token/refresh/`
- **Request Body**: `{"refresh": "<refresh_token>"}`

---

### 2. Patient Management APIs
*All patient endpoints require `Authorization: Bearer <access_token>`.*

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/patients/` | Add a new patient |
| `GET` | `/api/patients/` | Retrieve all patients created by the authenticated user |
| `GET` | `/api/patients/<id>/` | Get details of a specific patient |
| `PUT` | `/api/patients/<id>/` | Update patient details |
| `DELETE`| `/api/patients/<id>/` | Delete patient record |

#### Create Patient Example:
- **POST** `/api/patients/`
```json
{
  "name": "Tony Stark",
  "date_of_birth": "1970-05-29",
  "gender": "Male",
  "contact_number": "+12125550199",
  "email": "tony@starkindustries.com",
  "address": "10880 Malibu Point, CA",
  "medical_history": "Arc reactor shrapnel wound recovery."
}
```

---

### 3. Doctor Management APIs
*All doctor endpoints require `Authorization: Bearer <access_token>`.*

> [!NOTE]
> **Access & Ownership Policy**:
> - Per assignment specifications, `GET /api/doctors/` retrieves all doctors across the hospital so any patient can be assigned to specialists.
> - To prevent unauthorized modifications in multi-user environments, `PUT` and `DELETE` operations are protected by `IsDoctorCreatorOrReadOnly`: only the user who created the doctor record (or administrators/staff) can update or delete it.

| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/doctors/` | Add a new doctor (automatically tags `created_by=request.user`) | Authenticated |
| `GET` | `/api/doctors/` | Retrieve all doctors across the system | Authenticated |
| `GET` | `/api/doctors/<id>/` | Get details of a specific doctor | Authenticated |
| `PUT` | `/api/doctors/<id>/` | Update doctor details | Creator or Staff/Admin |
| `DELETE`| `/api/doctors/<id>/` | Delete doctor record | Creator or Staff/Admin |

#### Create Doctor Example:
- **POST** `/api/doctors/`
```json
{
  "name": "Leonard McCoy",
  "specialization": "Space Medicine & Trauma Surgery",
  "contact_number": "+1555432100",
  "email": "bones.mccoy@starfleet.org",
  "years_of_experience": 14,
  "hospital_affiliation": "Starfleet Medical Command"
}
```

---

### 4. Patient-Doctor Mapping APIs
*All mapping endpoints require `Authorization: Bearer <access_token>`.*

> [!IMPORTANT]
> **Ownership Isolation & Deterministic Route Semantics**:
> - **Patient Ownership Isolation**: Patients are private to each user. The mapping serializer dynamically filters `patient_id` to only patients created by the logged-in user (`patient.created_by == request.user`). Users cannot view, assign doctors to, or delete mappings of patients created by others.
> - **`GET /api/mappings/`**: Returns all doctor mappings strictly for patients created by the authenticated user.
> - **`GET /api/mappings/<patient_id>/`**: **Deterministic Lookup**. The URL parameter is strictly interpreted as `patient_id` (not a mapping ID). It returns all doctors assigned to that patient (must belong to the authenticated user). The route `/api/mappings/patient/<patient_id>/` is also supported as an alias. Optional query parameter `?format=doctors` returns pure doctor objects.
> - **`DELETE /api/mappings/<id>/`**: The URL parameter is strictly the mapping `id`. Verifies that the underlying patient belongs to the authenticated user before deletion.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/mappings/` | Assign a doctor to a patient (User must own the patient) |
| `GET` | `/api/mappings/` | Retrieve mappings for all patients created by the user |
| `GET` | `/api/mappings/<patient_id>/` | Get all doctors assigned to a specific patient owned by the user |
| `DELETE`| `/api/mappings/<id>/` | Remove a doctor from a patient (delete mapping by mapping ID) |

#### Assign Doctor to Patient Example:
- **POST** `/api/mappings/`
```json
{
  "patient_id": 1,
  "doctor_id": 2,
  "notes": "Assigned for diagnostic consult."
}
```

---

## 🧪 Testing

Run the full automated test suite (22 tests covering authentication, user ownership isolation, permissions, models, validations, and deterministic routing):
```bash
python manage.py test
```

*(Optional: For testing in local environments without a running PostgreSQL container, set `DB_ENGINE=sqlite3`)*:
```powershell
$env:DB_ENGINE="sqlite3"; python manage.py test
```

Sample output:
```
Creating test database for alias 'default'...
Found 22 test(s).
System check identified no issues (0 silenced).
......................
----------------------------------------------------------------------
Ran 22 tests in 18.057s

OK
Destroying test database for alias 'default'...
```

---

## 📬 Postman Collection

A complete, ready-to-test Postman collection file is included:
- File: [`postman_collection.json`](./postman_collection.json)

### How to use with Postman:
1. Open Postman and click **Import**.
2. Select or drag-and-drop `postman_collection.json`.
3. Run the **Login User (Captures Token)** request under `1. Authentication`.
   - The test script will **automatically capture** the JWT `access` token and store it in the `jwt_access_token` variable.
4. You can now execute any request under **Patients**, **Doctors**, and **Patient-Doctor Mappings** without copying tokens manually!
