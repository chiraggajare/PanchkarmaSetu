# PanchkarmaSetu — Complete Technical Documentation

> **Project Type:** Django Web Application
> **Django Version:** 6.0.2 / 6.0.3
> **Database:** SQLite3 (development)
> **Language:** Python 3
> **Last Documented:** April 2026

---

## Table of Contents

1. Project Overview
2. Directory Structure
3. Configuration and Settings
4. Data Models
5. URL Routing
6. Views and Business Logic
7. Forms
8. Admin Interface
9. PDF Generation Utility
10. Templates and Frontend
11. Static Files and Design System
12. Authentication and Role-Based Access Control
13. Database Migrations
14. User Workflow Diagrams
15. Notification System
16. API Endpoints (JSON)
17. Known Limitations and Future Work

---

## 1. Project Overview

**PanchkarmaSetu** ("Panchkarma Bridge") is a role-based wellness management web platform designed to digitize and streamline the traditional Ayurvedic Panchkarma treatment workflow. It connects three types of stakeholders:

| Stakeholder    | Role in System                                                   | Portal             |
|----------------|------------------------------------------------------------------|--------------------|
| Patient        | Books appointments, undergoes diagnosis, follows treatment cycles | Patient Dashboard  |
| Therapist      | Conducts diagnosis sessions, tracks daily attendance and vitals  | Therapist Dashboard|
| Centre Head    | Manages users, assigns therapists, views centre-wide analytics   | Head Dashboard     |

### Core Business Flow

```
Patient Books Appointment
        |
Centre Head Assigns Therapist
        |
Therapist Conducts Session -> Submits Diagnosis Report
        |
Patient Reviews Diagnosis -> Accepts/Declines Treatment
        |
Dummy Payment Gateway (conceptual)
        |
Treatment Cycle Begins (N days of attendance)
        |
Therapist Marks Daily Attendance + Vitals
        |
Therapist Ends Cycle -> Patient Submits Feedback
        |
PDF Treatment Completion Report Generated
```

---

## 2. Directory Structure

```
PanchkarmaSetu/
├── manage.py                        Django CLI entry point
├── db.sqlite3                       SQLite database (auto-generated)
│
├── panchkarma_setu/                 Project configuration package
│   ├── __init__.py
│   ├── settings.py                  All Django settings
│   ├── urls.py                      Root URL dispatcher
│   ├── asgi.py                      ASGI gateway config
│   └── wsgi.py                      WSGI gateway config
│
├── core/                            Main application package
│   ├── __init__.py
│   ├── apps.py                      AppConfig (name='core')
│   ├── models.py                    All database models (6 models)
│   ├── views.py                     All view functions (24 views)
│   ├── urls.py                      App-level URL patterns (21 routes)
│   ├── forms.py                     Django ModelForms (5 forms)
│   ├── admin.py                     Admin site registration
│   ├── pdf_utils.py                 ReportLab PDF generation (377 lines)
│   ├── tests.py                     (Boilerplate, no tests written)
│   └── migrations/
│       ├── 0001_initial.py          Creates all base tables
│       ├── 0002_attendance_*.py     Adds vitals fields to Attendance
│       └── 0003_treatmentcycle_*.py Adds is_cancelled_midway flag
│
├── templates/
│   ├── base.html                    Global layout template w/ navbar and notifications
│   └── core/
│       ├── home.html                Public landing page
│       ├── login.html               Login form
│       ├── signup.html              Registration form
│       ├── profile.html             User profile (password/email change)
│       ├── book_appointment.html    Patient appointment booking
│       ├── treatment_decision.html  Accept/decline diagnosis
│       ├── dummy_payment.html       Simulated payment step
│       ├── submit_feedback.html     Post-cycle patient feedback
│       ├── submit_diagnosis.html    Therapist diagnosis form
│       ├── patient_dashboard.html   Full patient portal
│       ├── therapist_dashboard.html Full therapist portal
│       └── head_dashboard.html      Full centre head portal
│
├── static/
│   └── css/
│       ├── styles.css               Global design system (dark theme, glassmorphism)
│       └── home.css                 Landing page specific styles
│
└── venv/                            Python virtual environment (excluded from git)
```

---

## 3. Configuration and Settings

**File:** `panchkarma_setu/settings.py`

### Key Settings Table

| Setting               | Value                      | Notes                                                 |
|-----------------------|----------------------------|-------------------------------------------------------|
| DEBUG                 | True                       | Must be False in production                           |
| SECRET_KEY            | Hardcoded string           | MUST be moved to env variable for production          |
| ALLOWED_HOSTS         | []                         | Add production domain before deploying                |
| AUTH_USER_MODEL       | 'core.User'                | Overrides Django's default User with custom model     |
| LOGIN_REDIRECT_URL    | '/dashboard/'              | Where to go after successful login                    |
| LOGOUT_REDIRECT_URL   | '/'                        | Redirects to home after logout                        |
| LOGIN_URL             | '/login/'                  | URL for @login_required redirects                     |
| LANGUAGE_CODE         | 'en-us'                    | Locale                                                |
| TIME_ZONE             | 'UTC'                      | All datetimes stored in UTC                           |
| USE_TZ                | True                       | Timezone-aware datetimes                              |

### Database

SQLite is used for the development/demo environment. For production, this should be replaced with PostgreSQL or MySQL.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Static Files

```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

### Email Configuration (Placeholders)

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'    # MUST BE CHANGED
EMAIL_HOST_PASSWORD = 'your-app-password'   # MUST BE CHANGED
DEFAULT_FROM_EMAIL = 'Panchkarma Setu <noreply@panchkarmasetu.com>'
```

WARNING: Email credentials are placeholders. The system uses Django's in-app Notification model instead of outgoing emails. Configure SMTP for real-world email delivery.

### Password Validators

All four built-in Django validators are active:
- UserAttributeSimilarityValidator - won't allow password similar to username/email
- MinimumLengthValidator - default minimum 8 characters
- CommonPasswordValidator - blocks common passwords
- NumericPasswordValidator - blocks all-numeric passwords

---

## 4. Data Models

**File:** `core/models.py`

All models are defined in the single `core` application.

### Entity Relationship Overview

```
User (custom AbstractUser)
 ├── Appointment [patient FK, therapist FK]
 │    └── DiagnosisReport [OneToOne -> Appointment]
 │         └── TreatmentPlan [FK]
 ├── TreatmentCycle [patient FK, therapist FK, treatment_plan FK]
 │    └── Attendance [cycle FK] (1 per day of duration)
 └── Notification [user FK]

TreatmentPlan (standalone, managed by admin)
```

---

### 4.1 User (extends AbstractUser)

Inherits all standard Django user fields (username, password, email, first_name, last_name, is_staff, is_superuser, is_active, date_joined, last_login, groups, user_permissions).

Custom Field:

| Field | Type          | Choices                              | Default   | Description                                        |
|-------|---------------|--------------------------------------|-----------|----------------------------------------------------|
| role  | CharField(20) | patient, therapist, centre_head      | patient   | Determines dashboard and permissions the user gets |

AUTH_USER_MODEL = 'core.User' globally overrides Django's User model.

---

### 4.2 TreatmentPlan

Represents a structured Ayurvedic treatment program. Created and managed by admins.

| Field         | Type              | Details                                           |
|---------------|-------------------|---------------------------------------------------|
| id            | BigAutoField (PK) | Auto-incremented                                  |
| name          | CharField(100)    | e.g., "Panchakarma Detox"                        |
| description   | TextField         | Short overview                                    |
| duration_days | IntegerField      | Typically 7-15 days                               |
| target_dosha  | CharField(20)     | One of 7 dosha choices (see below)               |
| detailed_info | TextField (blank) | Point-wise explanation shown to patients          |

Dosha Choices: vata, pitta, kapha, vata_pitta, pitta_kapha, vata_kapha, tridoshic

__str__ returns: "<name> (<duration_days> days) - <dosha display>"

---

### 4.3 Appointment

Represents a patient's initial diagnosis scheduling request.

| Field               | Type               | Details                                                           |
|---------------------|--------------------|-------------------------------------------------------------------|
| id                  | BigAutoField (PK)  | Auto-incremented                                                  |
| patient             | FK -> User         | on_delete=CASCADE; related_name='appointments'                    |
| therapist           | FK -> User (null)  | limit_choices_to={'role':'therapist'}; SET_NULL on delete         |
| height              | FloatField         | Height in cm                                                      |
| weight              | FloatField         | Weight in kg                                                      |
| age                 | IntegerField       | Patient's age at time of booking                                  |
| prior_health_issues | TextField (blank)  | Free text health history                                          |
| date                | DateField          | Scheduled date                                                    |
| time_slot           | TimeField          | One of 6 hourly slots (10:00-15:00)                              |
| status              | CharField(20)      | scheduled / in_progress / completed / cancelled                   |
| created_at          | DateTimeField      | Auto-set on creation                                              |

Concurrency Check: At appointment creation, the view re-verifies slot availability after form validation to handle race conditions.

---

### 4.4 DiagnosisReport

One-to-one clinical assessment associated with a completed appointment.

| Field                 | Type                       | Details                                              |
|-----------------------|----------------------------|------------------------------------------------------|
| id                    | BigAutoField (PK)          | Auto-incremented                                     |
| appointment           | OneToOneField -> Appointment | on_delete=CASCADE; related_name='diagnosis_report' |
| dosha                 | CharField(20)              | Assessed dosha                                       |
| diagnosis_result      | TextField                  | Therapist's free-text clinical findings              |
| recommended_treatment | FK -> TreatmentPlan (null) | SET_NULL if plan deleted                             |

Access Pattern: appointment.diagnosis_report — use hasattr() to check existence.

---

### 4.5 TreatmentCycle

Represents an active or completed N-day treatment program for a patient.

| Field               | Type                  | Details                                                          |
|---------------------|-----------------------|------------------------------------------------------------------|
| id                  | BigAutoField (PK)     | Auto-incremented                                                 |
| patient             | FK -> User            | on_delete=CASCADE; related_name='treatment_cycles'               |
| therapist           | FK -> User (null)     | SET_NULL; related_name='assigned_cycles'                         |
| treatment_plan      | FK -> TreatmentPlan   | on_delete=RESTRICT — prevents plan deletion if cycles exist      |
| start_date          | DateField             | Set to today + 1 day at cycle creation                           |
| is_active           | BooleanField          | True while in-progress; False after therapist ends it            |
| feedback_text       | TextField (null)      | Patient's review after completion                                |
| therapist_rating    | IntegerField (null)   | 1-5 star rating for therapist                                    |
| overall_rating      | IntegerField (null)   | 1-5 star overall experience rating                               |
| is_cancelled_midway | BooleanField          | True if patient cancelled before completion                       |

Attendance Lazy Creation: Attendance rows are batch-created when a patient first visits their dashboard with an active cycle (if no records exist yet).

---

### 4.6 Notification

In-app notification stored per user.

| Field      | Type              | Details                                                |
|------------|-------------------|--------------------------------------------------------|
| id         | BigAutoField (PK) | Auto-incremented                                       |
| user       | FK -> User        | on_delete=CASCADE; related_name='notifications'        |
| title      | CharField(200)    | Short notification headline                            |
| message    | TextField         | Full notification body                                 |
| is_read    | BooleanField      | Default False; not currently toggled but field exists  |
| created_at | DateTimeField     | Auto-set; used for ordering                            |

Meta: ordering = ['-created_at'] — newest first always.

---

### 4.7 Attendance

One record per day per treatment cycle, tracking session presence and clinical vitals.

| Field         | Type                    | Details                                                    |
|---------------|-------------------------|------------------------------------------------------------|
| id            | BigAutoField (PK)       | Auto-incremented                                           |
| cycle         | FK -> TreatmentCycle    | on_delete=CASCADE; related_name='attendances'              |
| date          | DateField               | The specific day of the cycle                              |
| is_attended   | BooleanField            | True when therapist marks patient as present               |
| avg_bp        | CharField(20) (null)    | Blood pressure e.g. "120/80 mmHg"                        |
| weight_kg     | FloatField (null)       | Patient weight that session day (kg)                       |
| pulse_bpm     | IntegerField (null)     | Pulse rate in beats per minute                             |
| session_notes | TextField (null)        | Clinical notes from therapist                              |

Meta: unique_together = ('cycle', 'date') — prevents duplicate attendance records.

---

## 5. URL Routing

### Root URLs (panchkarma_setu/urls.py)

```
/admin/    -> Django Admin
/          -> core.urls (all application routes)
```

### Public Routes

| URL       | View          | Name   | HTTP      |
|-----------|---------------|--------|-----------|
| /         | home          | home   | GET       |
| /login/   | login_view    | login  | GET, POST |
| /logout/  | logout_view   | logout | GET       |
| /signup/  | signup        | signup | GET, POST |

### Authenticated — Common Routes

| URL                                  | View                   | Name                  | HTTP      |
|--------------------------------------|------------------------|-----------------------|-----------|
| /dashboard/                          | dashboard              | dashboard             | GET       |
| /profile/                            | user_profile           | user_profile          | GET, POST |
| /notification/<id>/delete/           | delete_notification    | delete_notification   | GET       |
| /cycle/<id>/pdf/                     | download_treatment_pdf | download_treatment_pdf| GET       |

### Authenticated — Patient Routes

| URL                                  | View                   | Name                  | HTTP      |
|--------------------------------------|------------------------|-----------------------|-----------|
| /patient/book/                       | book_appointment       | book_appointment      | GET, POST |
| /patient/slots/                      | get_available_slots    | get_available_slots   | GET (AJAX)|
| /patient/decision/<report_id>/       | treatment_decision     | treatment_decision    | GET, POST |
| /patient/payment/<cycle_id>/         | dummy_payment          | dummy_payment         | GET, POST |
| /patient/feedback/<cycle_id>/        | submit_feedback        | submit_feedback       | GET, POST |
| /patient/cycle/<cycle_id>/cancel/    | cancel_active_cycle    | cancel_active_cycle   | POST      |

### Authenticated — Therapist Routes

| URL                                        | View                        | Name                       | HTTP |
|--------------------------------------------|-----------------------------|----------------------------|------|
| /therapist/appointment/<id>/status/        | update_appointment_status   | update_appointment_status  | POST |
| /therapist/appointment/<id>/diagnose/      | submit_diagnosis             | submit_diagnosis           | GET, POST |
| /therapist/cycle/<id>/attendance/          | mark_attendance             | mark_attendance            | POST |
| /therapist/cycle/<id>/end/                 | end_treatment               | end_treatment              | POST |

### Authenticated — Centre Head Routes

| URL                          | View             | Name             | HTTP |
|------------------------------|------------------|------------------|------|
| /head/assign/                | assign_therapist | assign_therapist | POST |
| /head/add-user/              | add_user         | add_user         | POST |
| /head/remove-user/<user_id>/ | remove_user      | remove_user      | POST |

---

## 6. Views and Business Logic

**File:** core/views.py (609 lines)

All views are function-based views (FBVs). Protected views use @login_required. Role enforcement is done manually via request.user.role checks.

---

### 6.1 signup(request)
- Template: core/signup.html
- Renders CustomUserCreationForm.
- On valid POST: saves user, logs them in, redirects to dashboard.
- No email verification. Roles are self-selected at signup.

---

### 6.2 login_view(request)
- Template: core/login.html
- Uses Django's built-in AuthenticationForm.
- If already authenticated: redirects to dashboard.
- On valid POST: calls login(), redirects to dashboard.

---

### 6.3 logout_view(request)
- Calls Django's logout().
- Redirects to home.

---

### 6.4 home(request)
- Template: core/home.html
- Public landing page. Computes three live statistics:

| Stat              | Computation                                                                                  |
|-------------------|----------------------------------------------------------------------------------------------|
| patients_treated  | User.objects.filter(role='patient').count()                                                  |
| satisfaction_rate | Average overall_rating as percentage; defaults to 99 if no ratings                          |
| success_rate      | (non-cancelled completed cycles / total cycles) x 100, clamped to [92, 98]; default 92      |

- Passes all TreatmentPlan objects for display.

---

### 6.5 dashboard(request) — Role Router
- Decorated with @login_required.
- Dispatches to render_patient_dashboard, render_therapist_dashboard, or render_head_dashboard based on role.

---

### 6.6 render_patient_dashboard(request) — Private Helper
- Template: core/patient_dashboard.html
- Context: active_cycle, upcoming_appointments, pending_diagnosis, attendances, completed_cycle_awaiting_feedback, therapist_info, previous_cycles

Therapist Priority Logic:
  1. From active treatment cycle
  2. From upcoming appointment (if therapist assigned)
  3. From most recent past cycle

Success Labels for Past Cycles:
  - >= 70% attendance -> 'Full Success' (green #10b981)
  - >= 50% attendance -> 'Mediocre Success' (amber #f59e0b)
  - < 50% attendance -> 'Not a Success' (red #ef4444)

Attendance Auto-Creation: If active_cycle has no attendance rows, creates one Attendance per day of treatment_plan.duration_days starting from active_cycle.start_date.

---

### 6.7 render_therapist_dashboard(request) — Private Helper
- Template: core/therapist_dashboard.html
- Context: upcoming_appointments, active_cycles, diagnosis_form (empty), reviews, avg_therapist_rating

---

### 6.8 render_head_dashboard(request) — Private Helper
- Template: core/head_dashboard.html
- Context: all_appointments, consolidated_appointments, therapists, patients, avg_rating, total_completed, unassigned_count
- Consolidation Logic: Uses defaultdict(list) and seen_patients set to group all appointments per patient.

---

### 6.9 book_appointment(request) — @login_required
- Template: core/book_appointment.html | Form: IntakeForm
- On valid POST:
  - Concurrency check: re-verifies slot before saving.
  - Sets patient and status='scheduled', saves.
  - Creates Notification: "Appointment Booked".
  - Redirects to dashboard.

---

### 6.10 get_available_slots(request) — @login_required — AJAX
- Accepts ?date=YYYY-MM-DD query param.
- Generates 6 hourly slots from 10:00 to 15:00.
- Returns each slot as {time, display, available: bool}.

---

### 6.11 treatment_decision(request, report_id) — @login_required
- Template: core/treatment_decision.html
- Verifies report.appointment.patient == request.user.
- On decision='proceed':
  - Creates TreatmentCycle with start_date = today + 1 day.
  - Creates Notification: "Treatment Cycle Started".
  - Redirects to dummy_payment.
- On decision='backout': redirects to dashboard.

---

### 6.12 dummy_payment(request, cycle_id) — @login_required
- Template: core/dummy_payment.html
- Simulates payment. On POST: success message, redirect to dashboard.
- Always renders the payment page on GET (never skipped).

---

### 6.13 submit_feedback(request, cycle_id) — @login_required
- Template: core/submit_feedback.html | Form: FeedbackForm
- On valid POST: saves feedback_text, ratings; sets is_active=False; redirects.

---

### 6.14 update_appointment_status(request, appointment_id) — @login_required
- Role check: 403 JSON if not therapist.
- Updates appt.status to in_progress, completed, or cancelled.

---

### 6.15 submit_diagnosis(request, appointment_id) — @login_required
- Template: core/submit_diagnosis.html | Form: DiagnosisReportForm
- Role check: non-therapists redirected.
- On valid POST: saves DiagnosisReport, marks appointment completed, sends Notification to patient.

---

### 6.16 mark_attendance(request, cycle_id) — @login_required
- Role check: 403 JSON if not therapist.
- action='update_vitals': Full vitals update (is_attended, avg_bp, weight_kg, pulse_bpm, session_notes). Redirects.
- action='toggle' (default): Flips is_attended. Returns JSON.

---

### 6.17 assign_therapist(request) — @login_required
- Role check: centre_head only.
- Assigns therapist to appointment AND updates any active TreatmentCycle for that patient.
- Creates Notification: "Therapist Assigned".

---

### 6.18 add_user(request) — @login_required
- Role check: centre_head only.
- Creates new user via CustomUserCreationForm. Flash messages on success/error.

---

### 6.19 remove_user(request, user_id) — @login_required
- Role check: centre_head only.
- Deletes user only if role is therapist or patient (cannot delete admins or other heads).

---

### 6.20 cancel_active_cycle(request, cycle_id) — @login_required
- Sets is_active=False, is_cancelled_midway=True.
- Redirects to submit_feedback for partial feedback.

---

### 6.21 user_profile(request) — @login_required
- Template: core/profile.html | Forms: PasswordChangeForm, EmailChangeForm
- action='change_password': validates, saves, calls update_session_auth_hash() to keep user logged in.
- action='change_email': validates and saves new email.

---

### 6.22 end_treatment(request, cycle_id) — @login_required
- Role check: therapist only.
- Sets cycle.is_active=False. Patient sees feedback prompt.

---

### 6.23 download_treatment_pdf(request, cycle_id) — @login_required
- Accessible by patient OR therapist of the cycle.
- Ensures Attendance rows exist. Calls generate_treatment_pdf(cycle).
- Returns HTTP response as application/pdf attachment.
- Filename: PanchkarmaSetu_Report_<PatientName>.pdf

---

### 6.24 delete_notification(request, notification_id) — @login_required
- Fetches notification owned by current user (404 if not found).
- Deletes it. Redirects to dashboard.

---

## 7. Forms

**File:** core/forms.py

All forms are ModelForm subclasses.

### 7.1 CustomUserCreationForm
Extends UserCreationForm. Fields: username, email, role, password1, password2.
Used by: signup and add_user views.

### 7.2 IntakeForm
Mapped to Appointment model.
Fields: height, weight, age, prior_health_issues (Textarea rows=3), date (DateInput type=date), time_slot (TimeInput type=time).
Used by: book_appointment view.

### 7.3 DiagnosisReportForm
Mapped to DiagnosisReport model.
Fields: dosha (Select), diagnosis_result (Textarea rows=4), recommended_treatment (ModelChoiceField).
Used by: submit_diagnosis view.

### 7.4 FeedbackForm
Mapped to TreatmentCycle model.
Fields: feedback_text (Textarea rows=3), therapist_rating (NumberInput min=1 max=5), overall_rating (NumberInput min=1 max=5).
Used by: submit_feedback view.

### 7.5 EmailChangeForm
Mapped to User model.
Fields: email (EmailInput with placeholder).
Used by: user_profile view.

---

## 8. Admin Interface

**File:** core/admin.py

All models registered at /admin/.

CustomUserAdmin:
- Extends UserAdmin.
- list_display: username, email, role, is_staff.
- Fieldsets: Default Django fields + role in its own section.

All other models (TreatmentPlan, Appointment, DiagnosisReport, TreatmentCycle, Attendance, Notification) use the default ModelAdmin.

---

## 9. PDF Generation Utility

**File:** core/pdf_utils.py (377 lines)
**Library:** ReportLab
**Output:** Single-page A4 PDF streamed as BytesIO

Entry point: generate_treatment_pdf(cycle) -> BytesIO

### PDF Section Structure

| Section | Content                                                              |
|---------|----------------------------------------------------------------------|
| 1       | Header: "PanchkarmaSetu" brand logo + report title                  |
| 2       | Status Block: dynamic color-coded attendance percentage              |
| 3       | Attendance Log: numbered grid of day cells (8 per row)              |
| 4       | Patient Information: username, age, height/weight, email, report date|
| 5       | Clinical Diagnosis: Prakriti (dominant dosha) and Vikruti (findings) |
| 6       | Prescribed Treatment: plan name, dosha, duration, start date         |
| 7       | Post-Treatment Precautions: 7 dosha-specific lifestyle rules         |
| 8       | Herbal Supplements: 3-4 Ayurvedic herbs with dosage                 |
| 9       | Footer: Therapist, Patient, PanchkarmaSetu signature slots + legal   |

### Status Block (Dynamic Colors)

| Attendance      | Background | Text     | Label                        |
|-----------------|------------|----------|------------------------------|
| >= 70%          | #F0FDF4    | #059669  | TREATMENT SUCCESS / FULL SUCCESS |
| >= 50% < 70%    | #FFFBEB    | #F59E0B  | PARTIAL SUCCESS              |
| < 50%           | #FEF2F2    | #B91C1C  | TREATMENT INCOMPLETE         |

### Color Palette

| Constant           | Hex     | Usage                   |
|--------------------|---------|-------------------------|
| COLOR_BRAND_GREEN  | #10B981 | Brand accent, HR lines  |
| COLOR_BRAND_TEXT   | #1F2937 | Header dark text         |
| COLOR_SUCCESS_BG   | #F0FDF4 | Attendance cells         |
| COLOR_PRIMARY      | #374151 | Main body text           |
| COLOR_SECONDARY    | #6B7280 | Section labels           |
| COLOR_MUTED        | #9CA3AF | Interpretations          |
| COLOR_BORDER       | #E5E7EB | Table borders            |
| COLOR_TABLE_BG     | #F9FAFB | Label cell backgrounds   |
| COLOR_ORANGE       | #F59E0B | Diagnosis section accent |

### Dosha Guidance Data (_get_dosha_guidance)

Provides for vata, pitta, kapha:
- Vikruti description (1 sentence on imbalance)
- 7 Post-treatment precautions
- 3-4 Herbal supplement recommendations with dosage

Mixed doshas (e.g. vata_pitta) fall back to the first matched base dosha.

---

## 10. Templates and Frontend

All templates extend base.html using {% block content %} and {% block scripts %}.

### base.html — Global Layout
- Loads Bootstrap 5.3.3 CSS + JS from CDN.
- Loads static/css/styles.css.
- Navbar: Brand link, notification bell with badge count, username/role display, logout.
- Notifications Dropdown: Toggled by bell; shows all user.notifications.all ordered newest first; click-outside closes.
- Flash Messages: Green (success), red (error), amber (default).

### home.html — Public Landing Page
- Marketing page: hero, features, treatment plans, live stats, CTA.
- Uses home.css for page-specific styles.

### book_appointment.html
- Renders IntakeForm.
- JavaScript time-slot picker: Fires AJAX to /patient/slots/ on date change; renders dynamic slot buttons; populates hidden time_slot input on selection.

### patient_dashboard.html
- Sections: Active Cycle (progress + therapist), Attendance Heatmap, Upcoming Appointments, Pending Diagnosis alert, Awaiting Feedback alert, Therapist Card (avg star rating), Previous Cycles history.

### therapist_dashboard.html
- Sections: Upcoming Appointments (with status update + diagnose button), Active Treatment Cycles (attendance toggle + vitals modal), Reviews (ratings + feedback text).

### head_dashboard.html
- Sections: Analytics bar (avg rating, completed count, unassigned count), Master Appointment Schedule (per-patient consolidated with therapist assignment dropdown), User Management (add/remove users).

### submit_diagnosis.html
- Renders DiagnosisReportForm. Shows patient intake details as context.

### treatment_decision.html
- Shows DiagnosisReport. Two submit buttons: decision=proceed / decision=backout.

### dummy_payment.html
- Mock payment page. Single POST button to confirm payment.

### submit_feedback.html
- Renders FeedbackForm with star rating inputs.

### profile.html
- Two sections: change email + change password. Each uses a different action hidden field.

### login.html / signup.html
- Minimal form pages using Django's built-in forms.

---

## 11. Static Files and Design System

**Files:** static/css/styles.css, static/css/home.css

### CSS Custom Properties (Design Tokens)

```css
:root {
    --bg-dark: #0f172a;                       Deep navy background
    --bg-card: rgba(30, 41, 59, 0.7);         Glassmorphism card background
    --primary: #10b981;                        Vibrant emerald green (brand)
    --primary-hover: #059669;                  Darker emerald for hover states
    --secondary: #3b82f6;                      Vivid blue accent
    --accent: #f59e0b;                         Warm amber (badges, highlights)
    --text-main: #f8fafc;                      Near-white main text
    --text-muted: #94a3b8;                     Subdued label text
    --border: rgba(255, 255, 255, 0.1);        Subtle white border
    --glass-blur: blur(12px);                  Backdrop filter value
    --booked-slot: #334155;                    Disabled slot background
    --booked-text: #64748b;                    Disabled slot text color
}
```

Font: Outfit (Google Fonts) — weights 300, 400, 500, 600, 700.

### Key UI Classes

| Class               | Description                                                        |
|---------------------|--------------------------------------------------------------------|
| .glass-card         | Glassmorphism card: dark blur bg, rounded 16px corners, hover lift |
| .btn-primary        | Gradient emerald button with glow shadow                           |
| .btn-outline        | Transparent with emerald border                                    |
| .slots-grid         | 3-column CSS grid for time-slot picker                             |
| .slot               | Time slot button (hover/selected/disabled states)                  |
| .slot.selected      | Active slot: full green bg, glow, scale(1.02)                     |
| .slot.disabled      | Taken slot: dashed border, "Taken" pseudo-element                  |
| .heatmap            | Auto-fill CSS grid of 40x40px attendance day cells                 |
| .heatmap-cell       | Day cell; [data-attended="true"] = green + glow                   |
| .badge-recommended  | Amber pill badge                                                   |
| .badge-status       | Blue pill badge                                                    |
| .badge-success      | Green pill badge                                                   |
| .data-table         | Full-width table with subtle borders and hover rows                |
| .dashboard-grid     | 2-column grid (collapses to 1 column below 768px)                 |
| .unread-bg          | Light green tint for unread notification items                     |

### Visual Effects

H1 Gradient Text:
```css
h1 {
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
```

Body Background:
```css
body {
    background-image:
        radial-gradient(circle at 15% 50%, rgba(16,185,129,0.05) 0%, transparent 25%),
        radial-gradient(circle at 85% 30%, rgba(59,130,246,0.05) 0%, transparent 25%);
}
```

---

## 12. Authentication and Role-Based Access Control

### Mechanism
- Session-based authentication (Django built-in).
- CSRF protection on all POST forms via CsrfViewMiddleware.
- @login_required redirects unauthenticated users to /login/.

### Role -> Dashboard Mapping

| Role        | Dashboard View              | Template                  |
|-------------|-----------------------------|-----------------------------|
| patient     | render_patient_dashboard    | patient_dashboard.html      |
| therapist   | render_therapist_dashboard  | therapist_dashboard.html    |
| centre_head | render_head_dashboard       | head_dashboard.html         |

### Access Control Summary

| View                        | Required Role        | Enforcement                                            |
|-----------------------------|----------------------|--------------------------------------------------------|
| book_appointment            | Any authenticated    | @login_required only                                   |
| get_available_slots         | Any authenticated    | @login_required only                                   |
| treatment_decision          | Patient (owner)      | FK owner check on report.appointment.patient           |
| submit_feedback             | Patient (owner)      | get_object_or_404(..., patient=user)                   |
| cancel_active_cycle         | Patient (owner)      | get_object_or_404(..., patient=user)                   |
| update_appointment_status   | Therapist            | role != 'therapist' -> 403 JSON                        |
| submit_diagnosis            | Therapist (assigned) | role check + therapist=user FK filter                  |
| mark_attendance             | Therapist (assigned) | role check + cycle queryset filter                     |
| end_treatment               | Therapist (assigned) | role check + get_object_or_404(..., therapist=user)    |
| assign_therapist            | Centre Head          | role != 'centre_head' -> redirect                      |
| add_user                    | Centre Head          | role != 'centre_head' -> redirect                      |
| remove_user                 | Centre Head          | role != 'centre_head' -> redirect                      |
| download_treatment_pdf      | Patient OR Therapist | user != cycle.patient and user != cycle.therapist check|
| delete_notification         | Owner only           | get_object_or_404(..., user=user)                      |

NOTE: All access control is manual role checking inside view functions. No Django Permission or Group model is used.

---

## 13. Database Migrations

### 0001_initial.py — Created: 2026-03-20

Creates all base tables:
- core_user (custom User with role field)
- core_treatmentplan
- core_appointment
- core_treatmentcycle
- core_diagnosisreport
- core_attendance (with unique_together on cycle + date)

### 0002_attendance_avg_bp_attendance_pulse_bpm_and_more.py

Adds clinical vitals fields to Attendance:
- avg_bp (CharField(20), nullable)
- pulse_bpm (IntegerField, nullable)
- weight_kg (FloatField, nullable)
- session_notes (TextField, nullable)

### 0003_treatmentcycle_is_cancelled_midway_and_more.py

Adds:
- is_cancelled_midway (BooleanField, default=False) to TreatmentCycle
- detailed_info (TextField, blank=True) to TreatmentPlan

---

## 14. User Workflow Diagrams

### 14.1 Patient End-to-End Flow

```
[Public Landing Page]
        |
        v
[Sign Up / Log In]
        |
        v
[Patient Dashboard] <-----------------------------------------------+
        |                                                           |
        +-- No appointment yet                                      |
        |       |                                                   |
        |       v                                                   |
        |   [Book Appointment]                                      |
        |   -> Select date | AJAX fetch slots                      |
        |   -> Fill vitals (height, weight, age)                   |
        |   -> Submit -> Appointment scheduled                     |
        |       |                                                   |
        |       v                                                   |
        |   [Wait for Therapist Assignment by Centre Head]         |
        |       |                                                   |
        |       v                                                   |
        |   [Therapist: Set In Progress -> Submit Diagnosis]        |
        |       |                                                   |
        |       v                                                   |
        +-- Pending Diagnosis available                             |
        |       |                                                   |
        |       v                                                   |
        |   [Treatment Decision Page]                               |
        |   -> Proceed: TreatmentCycle created -> Dummy Payment    |
        |   -> Backout: Back to Dashboard                          |
        |       |                                                   |
        +-- Active cycle exists                                     |
        |       |                                                   |
        |       v                                                   |
        |   [View attendance heatmap]                               |
        |   [Therapist marks daily attendance + vitals]             |
        |   [Patient can cancel midway -> Feedback form]            |
        |                                                           |
        +-- Cycle ended by therapist                                |
                |                                                   |
                v                                                   |
            [Submit Feedback: rating + comment]                    |
                |                                                   |
                v                                                   |
            [Cycle archived in Previous Cycles section]            |
            [Download PDF Report] -> Back to Dashboard ------------+
```

### 14.2 Therapist Flow

```
[Log In as Therapist] -> [Therapist Dashboard]
        |
        +-- Upcoming Appointments
        |   -> Update Status: Scheduled | In Progress | Completed | Cancelled
        |   -> Submit Diagnosis (Dosha + Findings + Recommended Plan)
        |      -> Appointment marked Completed
        |      -> Patient notified
        |
        +-- Active Treatment Cycles
        |   -> Toggle attendance per day (AJAX)
        |   -> Open vitals modal -> Submit (bp, weight, pulse, notes)
        |   -> End Treatment -> patient sees feedback prompt
        |
        +-- Reviews section (past ratings and feedback from patients)
```

### 14.3 Centre Head Flow

```
[Log In as Centre Head] -> [Head Dashboard]
        |
        +-- Analytics bar: avg rating | completed count | unassigned count
        |
        +-- Master Appointment Schedule
        |   -> Assign Therapist to unassigned appointments (dropdown)
        |   -> Submit: Appointment + active TreatmentCycle updated
        |   -> Patient gets "Therapist Assigned" notification
        |
        +-- User Management
            +-- Add User (role: patient or therapist)
            +-- Remove User (patients and therapists only)
```

---

## 15. Notification System

Notifications are stored in core_notification table (not emails — in-app only).

### Events that Trigger Notifications

| Event                              | Recipient | Title                     | Message                          |
|------------------------------------|-----------|---------------------------|----------------------------------|
| Appointment booked                 | Patient   | Appointment Booked        | Formatted date + time            |
| Therapist assigned by head         | Patient   | Therapist Assigned        | Dr. username for date            |
| Diagnosis submitted by therapist   | Patient   | Diagnosis Report Available| Dosha name + prompt to review    |
| Treatment cycle started (proceed)  | Patient   | Treatment Cycle Started   | Plan name + duration             |

### Display Mechanics

- Rendered in base.html navbar via {% for n in user.notifications.all %}.
- ordered by created_at descending (newest first).
- Badge count: {{ user.notifications.count }}.
- Each entry: title, message, timesince, delete link.
- delete_notification permanently removes the record.
- is_read field exists but is not toggled by any current view.

---

## 16. API Endpoints (JSON)

### GET /patient/slots/ — Slot Availability

Auth required: Yes (@login_required)
Query param: ?date=YYYY-MM-DD

Success response:
```json
{
  "slots": [
    {"time": "10:00", "display": "10:00 AM", "available": true},
    {"time": "11:00", "display": "11:00 AM", "available": false},
    {"time": "12:00", "display": "12:00 PM", "available": true},
    {"time": "13:00", "display": "01:00 PM", "available": true},
    {"time": "14:00", "display": "02:00 PM", "available": true},
    {"time": "15:00", "display": "03:00 PM", "available": true}
  ]
}
```

Bad/missing date: {"slots": []}

---

### POST /therapist/cycle/<id>/attendance/ — Toggle Action

Success: {"status": "success", "is_attended": true}
Error:   {"error": "<exception message>"}
Auth failure: {"error": "Unauthorized"} with HTTP 403

---

## 17. Known Limitations and Future Work

### Security Issues

| Issue                                     | Severity | Recommendation                                |
|-------------------------------------------|----------|-----------------------------------------------|
| SECRET_KEY hardcoded in settings.py       | CRITICAL | Move to .env using python-decouple or environ |
| DEBUG = True by default                   | CRITICAL | Set False in production via env variable      |
| ALLOWED_HOSTS = [] (empty)                | HIGH     | Add production domain name                    |
| SMTP credentials are placeholder strings  | HIGH     | Configure real credentials in env vars        |
| No HTTPS enforcement                      | MEDIUM   | Set SECURE_SSL_REDIRECT = True                |
| SESSION_COOKIE_AGE not configured         | LOW      | Set for proper session expiry                 |

### Feature / Correctness Gaps

| Issue                           | Description                                                              |
|---------------------------------|--------------------------------------------------------------------------|
| No email verification           | Users register without verifying email ownership                         |
| is_read field unused            | Notification.is_read exists but never set True by any view               |
| No pagination                   | Long lists (appointments, notifications) have no pagination              |
| Hardcoded slot times            | Slots (10:00-15:00) hardcoded in views.py; not admin-configurable        |
| Mixed dosha PDF gap             | _get_dosha_guidance only handles pure doshas; mixed fall back to first   |
| Empty tests.py                  | No automated tests written                                               |
| PDF therapist null risk         | cycle.therapist.get_full_name() would AttributeError if therapist deleted|
| Attendance side-effect          | Auto-creation on dashboard load could cause issues if called concurrently|

### Architecture Improvements

| Issue                   | Description                                                                   |
|-------------------------|-------------------------------------------------------------------------------|
| Single core app         | Consider splitting into accounts, appointments, cycles, reports apps          |
| No caching              | home view recomputes DB stats on every request; use cache.get_or_set()        |
| SQLite for production   | Not suitable for concurrent writes; migrate to PostgreSQL                     |
| No async task queue     | PDF generation is synchronous; use Celery + Redis for production              |
| No logging configured   | Add structured LOGGING dict to settings.py                                    |
| No API versioning       | AJAX endpoint has no versioning; consider DRF if expanding                    |

---

*This documentation was generated from full source code analysis of the PanchkarmaSetu project as of April 2026.*
