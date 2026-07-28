# AI-Powered Personalized Patient Reports Feature

This document provides a comprehensive overview of the AI Wellness Analysis feature integrated into the PanchkarmaSetu platform. It details the architecture, the modified files, and the end-to-end workflow of how patient data is transformed into a personalized Ayurvedic medical report using Large Language Models (LLMs).

---

## 1. Feature Overview
The AI Wellness Analysis feature automatically generates a professional, 350-500 word post-treatment completion report tailored to an individual patient. 

It synthesizes:
- **Patient Demographics:** Age, height, weight, prior issues.
- **Clinical Diagnosis:** The target Dosha (Vata/Pitta/Kapha) and initial findings.
- **Treatment Progression:** Attendance rate, duration, and therapist daily session notes (vitals like BP, Pulse, Weight).
- **Patient Feedback:** Post-cycle ratings and feedback strings.

Using **Groq (Llama-3.3-70b)** or **Google Gemini**, it creates a highly accurate, empathetic narrative that is permanently saved and injected into a downloadable PDF.

---

## 2. Files & Folders Modified

### 🔹 New Files Created
1. **`core/ai_report.py`** 
   - **Purpose:** Acts as the AI service layer. Contains the `generate_patient_narrative` function.
   - **Details:** Constructs the massive prompt using the patient's context, handles API routing (auto-detects if the key is for Groq or Gemini), manages error handling, and provides a fallback text generation method if quotas are exhausted.
2. **`.env`**
   - **Purpose:** Environment variables configuration.
   - **Details:** Stores `GROQ_API_KEY` and `GOOGLE_API_KEY` securely without hardcoding them into the repository.

### 🔹 Existing Files Modified
1. **`core/models.py`**
   - **Change:** Added `ai_report_text` (TextField) and `ai_report_generated_at` (DateTimeField) to the `TreatmentCycle` model.
   - **Purpose:** To persist the LLM's output so we only pay the latency/API cost once per cycle.
2. **`core/views.py`**
   - **Change:** Added the `generate_ai_report` view endpoint.
   - **Purpose:** Handles the AJAX POST request from the frontend, checks authorization, calls `core/ai_report.py`, caches the result in the database, sends an in-app notification to the patient, and returns the markdown payload.
3. **`core/urls.py`**
   - **Change:** Registered the route `path('patient/cycle/<int:cycle_id>/generate-report/', ...)`
4. **`core/pdf_utils.py`**
   - **Change:** Upgraded the PDF builder (`generate_treatment_pdf`) to dynamically support 2 pages.
   - **Purpose:** If an `ai_report_text` exists on the cycle, the PDF generator appends a `PageBreak()` and beautifully formats the Markdown-styled AI output directly into the official clinical PDF.
5. **`templates/core/patient_dashboard.html`**
   - **Change:** Added the "✨ AI Wellness Analysis" button, the modal popup UI, and Vanilla JS fetch logic.
   - **Purpose:** Provides a seamless user experience. Uses JavaScript to parse the Markdown response into HTML and displays a loading spinner during the 2-3 second generation window.
6. **`panchkarma_setu/settings.py`**
   - **Change:** Integrated `python-dotenv` to load `.env` variables at the very beginning of the application lifecycle and exposed `GROQ_API_KEY` globally.
7. **`requirements.txt`**
   - **Change:** Pinned new dependencies (`google-genai`, `python-dotenv`, `requests`).

---

## 3. End-to-End Workflow

Here is the step-by-step lifecycle of how the AI report is generated when a patient clicks the button:

1. **User Interaction (Frontend)**
   - The patient views a completed treatment cycle on their dashboard.
   - They click the **"✨ AI Wellness Analysis"** button.
   - JavaScript prevents the default link action, opens a modal with a loading spinner, and sends an asynchronous AJAX `POST` request to `/patient/cycle/<id>/generate-report/`.

2. **Route & View Resolution (Django)**
   - `core.urls` routes the request to the `generate_ai_report` function in `views.py`.
   - The view verifies that the current user is either the patient who owns the cycle or an authorized therapist.
   - **Cache Check:** The view checks if `cycle.ai_report_text` is already filled. If it is (and the user hasn't clicked "Regenerate"), it instantly returns the cached text. If empty, it proceeds to generation.

3. **Context Gathering & Prompting (Service Layer)**
   - `views.py` calls `generate_patient_narrative(cycle)` inside `ai_report.py`.
   - The function queries the database to aggregate:
     - The patient's latest appointment and diagnosis.
     - A loop through all `Attendance` records to aggregate session notes, vitals, and calculate the attendance percentage.
   - An extensive Prompt is constructed instructing the LLM to act as a Clinical Ayurvedic Doctor.

4. **API Routing & LLM Execution**
   - The script inspects the loaded API key. 
   - If it detects `gsk_` (Groq), it routes the HTTP POST request to Groq's high-speed inference engine using the `llama-3.3-70b-versatile` model via the `requests` library.
   - If it detects a standard key, it uses the official `google-genai` SDK to query `gemini-2.0-flash`.
   
5. **Persistence & Response**
   - The LLM returns a markdown-formatted response.
   - Django saves this text to `cycle.ai_report_text` and logs the timestamp in `cycle.ai_report_generated_at`.
   - A `Notification` is created in the database to alert the patient that their report is ready.
   - The Markdown text is returned via JSON to the browser.

6. **UI Rendering & PDF Generation**
   - The frontend JavaScript parses the Markdown into HTML (`**text**` -> `<strong>text</strong>`) and injects it into the modal.
   - The user can read the report instantly.
   - When the user clicks **"Download Full PDF"**, the system hits `/cycle/<id>/pdf/` (`pdf_utils.py`), which reads the saved AI text, translates the markdown into ReportLab Paragraph styles, and generates a cohesive 2-page PDF document.

---

## 4. Environment & Keys
The system is built to be highly robust to quota limits:
- It relies on `python-dotenv` reading from `.env`.
- It currently operates seamlessly on **Groq** for high-speed, free inference bypassing Google's strict Cloud Billing requirements.

*Document generated by Antigravity during pair programming session.*
