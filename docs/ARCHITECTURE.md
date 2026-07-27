# PanchkarmaSetu Architecture & Workflow Analysis

## 1. System Integrity Verification
Following the removal of the unused `accounts`, `appointments`, and `dashboard` directories, a full system integrity check was performed (`python manage.py check`). The result was **0 issues identified**. The codebase is completely intact. The reason for this stability is that all logic, URLs, and templates had already been thoroughly refactored and consolidated into the monolithic `core` application prior to the deletion of the legacy folders.

---

## 2. Complete Project Workflow (From Registration to Feedback)

### Phase 1: Registration & Onboarding
1. **Public Registration:** A new patient visits `/signup/`. The server renders the `PatientSignUpForm` via `signup.html`. The user inputs their `username` and `email`.
2. **Account Creation:** Upon submission, the `signup` view saves the user. Because the custom `User` model sets `default='patient'`, the database strictly enforces their role without them explicitly choosing it.
3. **Login & Routing:** The view automatically calls `login()` and redirects to `/dashboard/`. The master `dashboard` view acts as a traffic cop, checks `request.user.role`, and routes them to `render_patient_dashboard`.

### Phase 2: Booking & Assignment
4. **Appointment Booking:** The patient navigates to "Book Appointment" (`/appointment/book/`) and fills out clinical intake data (height, weight, prior issues, desired date/time) using `IntakeForm`. An `Appointment` is saved with status `scheduled`. A system `Notification` is created for the patient.
5. **Therapist Assignment:** The Centre Head logs in, views the `head_dashboard`, and sees the unassigned appointment. Using the `assign_therapist` view, they link a specific Therapist to the Appointment. A `Notification` alerts the patient.

### Phase 3: Diagnosis & Treatment Initiation
6. **Diagnosis Submission:** The assigned Therapist conducts the consultation. They access `/appointment/<id>/diagnose/`, fill out the `DiagnosisReportForm`, determine the patient's dosha, and prescribe a `TreatmentPlan`. The appointment is marked `completed`.
7. **Patient Decision:** The patient is notified. They review the Diagnosis Report and click "Proceed" (`treatment_decision` view). 
8. **Cycle Creation:** Proceeding generates a `TreatmentCycle` entity. This links the Patient, the Therapist, and the TreatmentPlan, setting `is_active=True` and scheduling it to begin the next day. The user is taken to a dummy payment gateway.

### Phase 4: Treatment Execution & Feedback
9. **Daily Clinical Tracking:** During the cycle, the Therapist uses the dashboard to `mark_attendance`. For each day, they record clinical vitals (`avg_bp`, `weight_kg`, `pulse_bpm`) and `session_notes`. This data is saved in `Attendance` records.
10. **Cycle Completion:** Once all days are logged, the therapist ends the cycle (`end_treatment` view), marking it `is_active=False`.
11. **Feedback Collection:** The patient logs in and is immediately prompted to submit feedback (`submit_feedback` view). They provide an `overall_rating`, a `therapist_rating`, and written `feedback_text`.
12. **Report Generation:** At any time post-completion, the patient or therapist can trigger `download_treatment_pdf`. The `pdf_utils.py` module queries the cycle and its attendance records to stream a dynamically generated PDF report.

---

## 3. Role-Based Access Control (RBAC)
- **Setup:** RBAC is built directly into the database. The `User` model extends `AbstractUser` to inherit Django's core authentication but adds a custom `role` CharField (`patient`, `therapist`, `centre_head`).
- **Enforcement:**
  - **View-Level Routing:** Views like `dashboard` explicitly check `request.user.role` to render entirely different HTML context.
  - **Security Guards:** State-changing functions (e.g., `assign_therapist`, `add_user`) begin with explicit checks like `if request.user.role != 'centre_head': return redirect('dashboard')` to block unauthorized POST requests.
- **Role Responsibilities:**
  - **Patient:** Book appointments, review diagnostic results, authorize treatment cycles, provide post-treatment ratings.
  - **Therapist:** Receive assignments, conduct diagnoses, prescribe treatments, manage daily session vitals (BP, weight, notes), and formally close cycles.
  - **Centre Head:** Administer the clinic. Create internal accounts (therapists), monitor clinic analytics (success rates, average feedback), and orchestrate the assignment of incoming patient appointments to available therapists.

---

## 4. Notifications Handling
- **Setup:** A standalone `Notification` model is connected to the `User` model via a ForeignKey. 
- **Generation:** Notifications are instantiated programmatically within view functions at key workflow moments (e.g., `Notification.objects.create(...)` inside `book_appointment` and `submit_diagnosis`).
- **Delivery & Rendering:** In `base.html`, a bell icon utilizes template logic (`{% for n in user.notifications.all %}`) to globally render notifications for the authenticated user on any page.
- **Dismissal:** Users dismiss alerts via the `delete_notification` view, which deletes the record from the database.

---

## 5. Database Setup & Data Handling
- **Engine:** SQLite (`db.sqlite3`), configured in `settings.py`.
- **Entity Storage & Linkages:**
  - `User`: Identity and role.
  - `TreatmentPlan`: Static clinic offerings (e.g., "7-day Vata Detox").
  - `Appointment`: Pre-diagnosis scheduling. (Linked to Patient).
  - `DiagnosisReport`: The medical result of an Appointment. (OneToOne with Appointment; ForeignKey to TreatmentPlan).
  - `TreatmentCycle`: The active medical engagement. (Linked to Patient, Therapist, and TreatmentPlan).
  - `Attendance`: The daily clinical log. (Linked to TreatmentCycle).
- **Database Functions & Triggers (Views):**
  - **Reads:** Views use Django's ORM (e.g., `Appointment.objects.filter(...)`) to fetch data. Complex views like the Head Dashboard use `select_related('patient', 'therapist')` to optimize database joins. Aggregation is used (`.aggregate(Avg('overall_rating'))`) to calculate clinic analytics directly in the DB.
  - **Writes:** Forms translate HTTP POST data into DB inserts (e.g., `form.save()`). Transactions are mostly implicit, handling creations in single functional blocks.

---

## 6. App & File Responsibilities

### The `core` App (The Engine)
- **`models.py`**: Defines the exact structure, constraints, and relationships of the database schema.
- **`views.py`**: The "Controllers." They intercept HTTP requests, enforce security, query the database, process logic, and return responses or templates.
- **`forms.py`**: Handles validation. Acts as a shield between raw HTML form input and the database models. Ensures required fields are present and data types are correct (e.g., ensuring `PatientSignUpForm` cannot inject a `role`).
- **`urls.py`**: The routing map. Connects specific web addresses (like `/signup/`) to specific functions in `views.py`.
- **`pdf_utils.py`**: An isolated service file that uses the `reportlab` library to draw shapes, text, and tables for dynamic PDF generation.
- **`admin.py`**: Registers models so the Centre Head (or Django Superuser) can manually edit database rows in the `/admin/` portal.

### The `panchkarma_setu` Project Folder (The Configuration)
- **`settings.py`**: Global configuration. Holds the `SECRET_KEY`, defines `INSTALLED_APPS` (where `core` lives), configures database connections, and defines where static files and templates live.
- **`urls.py`**: The master dispatcher. It mounts the `admin/` panel and forwards everything else to `core.urls`.

---

## 7. Interview Questions on Specific Files (10 Questions)

1. **Q: In `models.py`, why did we extend `AbstractUser` instead of `AbstractBaseUser`?**
   **A:** `AbstractUser` provides all standard fields (username, email, passwords) and auth functionalities out-of-the-box. We only needed to add one extra field (`role`), so extending `AbstractUser` saved us from reinventing the wheel.
   
2. **Q: In `forms.py`, why was the `PatientSignUpForm` explicitly created?**
   **A:** To strip out the `role` field from the registration page. If we used `CustomUserCreationForm`, users could technically inspect the HTML and submit themselves as a `centre_head`. This form secures role assignment.

3. **Q: How does `urls.py` in the `core` app integrate with the main project?**
   **A:** The project-level `urls.py` uses the `include('core.urls')` function to delegate all traffic routing directly to the core application.

4. **Q: What architectural purpose does `pdf_utils.py` serve?**
   **A:** It enforces "Separation of Concerns." Rendering PDFs requires complex canvas drawing code. Moving this out of `views.py` keeps the view logic focused strictly on HTTP and database operations.

5. **Q: In `views.py`, how does the `dashboard` view function act as a traffic router?**
   **A:** It intercepts the user post-login, inspects `request.user.role`, and routes the request to highly specific sub-functions (e.g., `render_patient_dashboard`), acting as a gateway.

6. **Q: Why are we using `select_related('patient', 'therapist')` in `render_head_dashboard`?**
   **A:** To solve the N+1 query problem. Instead of querying the database for the user details inside a template `for` loop, `select_related` performs a SQL JOIN to fetch all related user data in a single, efficient query.

7. **Q: How does `book_appointment` in `views.py` prevent double-booking race conditions?**
   **A:** Before calling `.save()`, it queries the database to see if an active appointment already exists for that exact `date` and `time_slot`. If it does, it returns an error message.

8. **Q: In `models.py`, what is the purpose of `unique_together = ('cycle', 'date')` in the `Attendance` model?**
   **A:** It establishes database-level data integrity, ensuring that a therapist cannot accidentally (or maliciously) create two attendance records for the same patient on the exact same day.

9. **Q: In `base.html`, how is the notification system made dynamic across all pages?**
   **A:** By utilizing `request.user.notifications.all`. Django's global context processors automatically inject the `user` object into every template, allowing us to query related notifications globally.

10. **Q: What is the role of `AUTH_USER_MODEL = 'core.User'` in `settings.py`?**
    **A:** It instructs Django's deep internal authentication machinery to swap out its default User table for our custom `core.User` table, enabling our `role` field to integrate perfectly with `login()` and `@login_required`.

---

## 8. Fundamental Django Interview Questions (20 Questions)

*Use these to prepare for core Django architectural concepts based on your project.*

1. **Architecture:** What is the MTV architecture in Django, and how does it roughly map to the traditional MVC pattern?
   **Answer:** MTV stands for Model-Template-View. It maps to MVC (Model-View-Controller) where Django's "Model" maps to MVC's Model (data access), Django's "Template" maps to MVC's View (presentation), and Django's "View" maps to MVC's Controller (business logic and routing).

2. **ORM Basics:** What is an ORM (Object-Relational Mapper), and what specific benefits did it provide when building PanchkarmaSetu?
   **Answer:** An ORM allows developers to interact with the database using Python classes and methods instead of writing raw SQL. For PanchkarmaSetu, it made creating relationships (like linking an Appointment to a User) seamless and database-agnostic, while automatically handling SQL injection protection.

3. **Relationships:** Explain the practical difference between a `ForeignKey`, a `OneToOneField`, and a `ManyToManyField` using your models as examples.
   **Answer:** `ForeignKey` is Many-to-One (Many Appointments can belong to One User). `OneToOneField` is One-to-One (One Appointment has exactly One DiagnosisReport). `ManyToManyField` links Many-to-Many (e.g., if a TreatmentPlan required Multiple Therapists simultaneously, though not used here).

4. **Database Nulls:** In your models, what is the exact difference between `null=True` and `blank=True`?
   **Answer:** `null=True` is database-related; it tells the database column to accept SQL NULL values. `blank=True` is validation-related; it allows Django forms to accept empty submissions for that field without throwing a "This field is required" error.

5. **Security:** How do Django Forms protect against Cross-Site Request Forgery (CSRF) attacks?
   **Answer:** Django requires `{% csrf_token %}` inside POST forms. It injects a hidden field with a unique token that is verified against a token stored in the user's session cookie. If they don't match or the token is missing, the POST request is rejected (403 Forbidden).

6. **Query Optimization:** Explain the "N+1 query problem." How do `select_related` and `prefetch_related` solve it?
   **Answer:** N+1 occurs when fetching a list of items and then performing an additional database query for each item's related data in a loop. `select_related` solves this for ForeignKeys using a SQL JOIN. `prefetch_related` solves it for ManyToMany/Reverse relations by executing exactly two queries and joining the data in Python.

7. **Lifecycles:** Walk me through the Request/Response lifecycle in Django from the moment a user clicks "Book Appointment."
   **Answer:** The browser sends an HTTP request. Django's WSGI server routes it through Middlewares. `urls.py` matches the `/appointment/book/` path to the `book_appointment` view. The view checks auth, instantiates the `IntakeForm`, queries the DB, processes logic, renders the `book_appointment.html` template, passes it back through Middlewares, and returns an HTTP Response to the browser.

8. **Middlewares:** What are Middlewares in Django? Give an example of a built-in middleware used in your project.
   **Answer:** Middleware is a framework of hooks that process requests/responses globally before they reach the view or after they leave it. Example: `AuthenticationMiddleware` attaches the `request.user` object to every incoming request.

9. **Schema Evolution:** How does Django manage changes to database schemas? What exactly are migration files?
   **Answer:** Django uses migrations to track changes to `models.py`. Migration files are auto-generated Python scripts that describe how to build, alter, or drop database tables to match the current state of the models, allowing schema evolution without data loss.

10. **Authorization:** What is the difference between checking access via `@login_required` versus writing a custom permission Mixin for class-based views?
    **Answer:** `@login_required` is a simple decorator for function-based views that just ensures the user is authenticated. A permission Mixin (like `UserPassesTestMixin`) is used in Object-Oriented Class-Based Views to enforce complex, granular, object-level logic (e.g., "Is this user the specific therapist assigned to this cycle?").

11. **Security Settings:** Why is the `SECRET_KEY` in `settings.py` critical? What happens if a hacker obtains it?
    **Answer:** It is used for cryptographic signing in Django (passwords, session cookies, CSRF tokens, password reset tokens). If a hacker steals it, they can forge session cookies, impersonate any user, and bypass CSRF protection.

12. **Templates:** How does Django template inheritance (`{% extends 'base.html' %}`) work to keep frontend code DRY?
    **Answer:** It allows you to create a master `base.html` with headers, footers, and navbars. Child templates "extend" this base and only inject unique content into defined `{% block content %}` areas, preventing the repetition of boilerplate HTML across 50 different pages.

13. **State Management:** HTTP is stateless. How do Sessions work in Django to keep users logged in, and where is session data actually stored?
    **Answer:** Django creates a unique Session ID and sends it to the browser as a cookie. On subsequent requests, the browser sends the cookie back. Django looks up that ID in the `django_session` database table (by default) to retrieve the user's state.

14. **Template Globals:** What is the purpose of Django's `context_processors`?
    **Answer:** Context processors are functions that run before the template is rendered to inject global variables into the context dictionary. For example, the `auth` context processor ensures `{{ user }}` is available in every single template without the view needing to pass it explicitly.

15. **Data Cleaning:** How does form validation work behind the scenes in `forms.py`? What is the difference between `clean_<fieldname>()` and `clean()`?
    **Answer:** Calling `form.is_valid()` triggers validation. `clean_<fieldname>()` validates a specific field in isolation (e.g., ensuring a username doesn't have spaces). `clean()` is used to validate fields that depend on each other (e.g., checking that `end_date` is strictly after `start_date`).

16. **Media Handling:** How would you handle uploading profile pictures in Django? Explain the roles of `MEDIA_ROOT` and `MEDIA_URL`.
    **Answer:** Add an `ImageField` to the model. Configure `MEDIA_ROOT` (the absolute filesystem path where uploaded files are saved) and `MEDIA_URL` (the base URL route used to serve those files to the browser).

17. **Event Triggers:** What are Django Signals (like `post_save` or `pre_save`), and what is a use-case for them?
    **Answer:** Signals allow decoupled applications to get notified when certain actions occur elsewhere. Use-case: Using a `post_save` signal on the `User` model to automatically create an empty `Profile` model immediately after a new user registers.

18. **Lazy Evaluation:** What is a QuerySet? What does it mean when developers say QuerySets are "lazy"?
    **Answer:** A QuerySet is a collection of objects from the database. They are "lazy" because creating or filtering a QuerySet (e.g., `User.objects.filter(role='patient')`) does not actually query the database. The database hit only happens when the QuerySet is evaluated (iterated over, printed, or cast to a list).

19. **Design Philosophy:** Explain the concept of "Fat Models, Thin Views" in Django design philosophy. Does your project follow this?
    **Answer:** It means business logic (like calculating a success rate or generating a PDF) should be encapsulated as methods inside the Model class, keeping the `views.py` clean ("thin") to only handle HTTP routing and form processing. Currently, the project's logic is mostly in views, meaning it leans towards "Fat Views", which is common for rapid prototyping but could be refactored.

20. **Admin Panel:** How does Django's built-in Admin panel work under the hood, and how do you customize what columns are displayed?
    **Answer:** The Admin panel dynamically inspects registered models and builds a CRUD interface. You customize it by creating a subclass of `admin.ModelAdmin` in `admin.py` and setting `list_display = ('field1', 'field2')`, then passing it to `admin.site.register(MyModel, MyModelAdmin)`.
