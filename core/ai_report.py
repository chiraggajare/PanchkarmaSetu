import os
import logging
from django.conf import settings
from django.utils import timezone
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv

# Load env file if it exists
load_dotenv()

logger = logging.getLogger(__name__)

def generate_patient_narrative(cycle):
    """
    Generates a personalized, comprehensive Ayurvedic wellness report narrative
    for a completed TreatmentCycle. Automatically routes to Groq (Llama-3.3-70b)
    or Google Gemini (gemini-2.0-flash) based on API key format.
    """
    # 1. Retrieve the API Key
    # Checks GROQ_API_KEY first, then GOOGLE_API_KEY env or Django settings
    api_key = (
        os.environ.get('GROQ_API_KEY') or
        getattr(settings, 'GROQ_API_KEY', '') or
        os.environ.get('GOOGLE_API_KEY') or 
        getattr(settings, 'GOOGLE_API_KEY', '')
    )
    
    if not api_key:
        logger.error("No API key configured for Groq or Gemini.")
        return get_fallback_report(cycle, "API Key is missing. Please set GROQ_API_KEY or GOOGLE_API_KEY environment variable.")

    # 2. Compile Context Data
    patient = cycle.patient
    plan = cycle.treatment_plan
    
    # Calculate attendance
    attendances = list(cycle.attendances.all().order_by('date'))
    total_days = plan.duration_days if plan else 7
    attended_count = sum(1 for a in attendances if a.is_attended)
    attendance_pct = int((attended_count / total_days) * 100) if total_days else 0
    
    # Try to find the latest completed appointment with diagnosis
    appt = patient.appointments.filter(status='completed').select_related('diagnosis_report').order_by('-date').first()
    diag_report = appt.diagnosis_report if appt and hasattr(appt, 'diagnosis_report') else None
    
    age = appt.age if appt else "N/A"
    height = f"{appt.height} cm" if appt else "N/A"
    weight = f"{appt.weight} kg" if appt else "N/A"
    prior_issues = appt.prior_health_issues if appt and appt.prior_health_issues else "None reported"
    diagnosis_result = diag_report.diagnosis_result if diag_report else "General constitution imbalance"
    dosha = plan.get_target_dosha_display() if plan else "Unknown"

    # Aggregated session notes from daily attendance
    session_notes_list = []
    for att in attendances:
        if att.is_attended and att.session_notes:
            session_notes_list.append(f"Day {att.date.strftime('%d')}: {att.session_notes} (Weight: {att.weight_kg or 'N/A'}kg, BP: {att.avg_bp or 'N/A'}, Pulse: {att.pulse_bpm or 'N/A'}bpm)")
    session_notes_str = "\n".join(session_notes_list) if session_notes_list else "No detailed session logs captured."

    # Patient feedback
    feedback = cycle.feedback_text if cycle.feedback_text else "No final feedback submitted yet."
    therapist_rating = cycle.therapist_rating if cycle.therapist_rating else "N/A"
    overall_rating = cycle.overall_rating if cycle.overall_rating else "N/A"

    # 3. Construct the prompt
    prompt = f"""
You are a highly experienced clinical Ayurvedic doctor and wellness consultant writing a formal Treatment Completion Summary Report on behalf of the PanchkarmaSetu wellness platform.
Based on the patient's data below, generate a personalized, compassionate, and professional Ayurvedic narrative report.

PATIENT METRICS & DEMOGRAPHICS:
- Patient Name/Username: {patient.username}
- Email: {patient.email}
- Age: {age}
- Height / Weight: {height} / {weight}
- Prior Health Issues: {prior_issues}

CLINICAL INITIAL DIAGNOSIS:
- Diagnosed Prakriti/Vikruti Dosha: {dosha}
- Initial Clinical Findings: {diagnosis_result}

TREATMENT CYCLE DETAILS:
- Prescribed Treatment Plan: {plan.name if plan else 'Panchakarma Treatment'}
- Plan Description: {plan.description if plan else ''}
- Planned Duration: {total_days} days
- Cycle Start Date: {cycle.start_date.strftime('%B %d, %Y')}
- Attendance: {attended_count} out of {total_days} days attended ({attendance_pct}%)
- Cancelled Midway: {"Yes" if cycle.is_cancelled_midway else "No"}

DAILY VITAL SIGNS & CLINICAL SESSION NOTES (from therapist):
{session_notes_str}

PATIENT'S POST-TREATMENT FEEDBACK:
- Feedback Narrative: "{feedback}"
- Therapist Rating: {therapist_rating}/5
- Overall Treatment Rating: {overall_rating}/5

INSTRUCTIONS FOR REPORT GENERATION:
1. Write a professional, cohesive medical/wellness summary report.
2. Structure the report exactly with these sections (using Markdown bold labels like "**Executive Summary**" but DO NOT use main heading headers like `#`, `##` or `###`):
   - **Executive Summary**: A brief, warm, and supportive summary of the patient's overall treatment outcome.
   - **Clinical Wellness Assessment**: Analyze the initial dosha imbalance in comparison to the session progress, vitals notes, and current state.
   - **Commitment & Progress Analysis**: Address their attendance rate ({attendance_pct}%), commenting on consistency and its effect on efficacy.
   - **AI-Recommended Lifestyle & Dietary Plan**: Tailor specific dietary (Ahar), lifestyle (Vihar), and mental wellness habits for their {dosha} dosha.
   - **Long-Term Prognosis & Follow-Up**: Outline the path forward, recommended herbal suggestions (based on the dosha), and when they should return.
3. Keep the tone warm, highly professional, empathetic, and authentically Ayurvedic.
4. Total length should be around 350 to 500 words. Do not use generic placeholders; speak directly about this specific patient's case and metrics.
"""

    # 4. Route based on key prefix (gsk_ = Groq, otherwise Gemini)
    if api_key.startswith('gsk_'):
        import requests
        logger.info("Routing request to Groq API using Llama-3.3-70b-versatile")
        url = 'https://api.groq.com/openai/v1/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'llama-3.3-70b-versatile',
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.7
        }
        try:
            r = requests.post(url, headers=headers, json=data, timeout=30)
            if r.status_code == 200:
                res = r.json()
                return res['choices'][0]['message']['content'].strip()
            else:
                err_msg = r.json().get('error', {}).get('message', 'Unknown Groq Error')
                logger.error(f"Groq API returned status {r.status_code}: {err_msg}")
                return get_fallback_report(cycle, f"Groq API Error: {err_msg[:200]}")
        except Exception as e:
            logger.error(f"Failed to call Groq API: {e}")
            return get_fallback_report(cycle, f"Failed to call Groq API: {str(e)[:200]}")
            
    else:
        logger.info("Routing request to Google Gemini API")
        # Call the Gemini API — try gemini-2.0-flash first, fall back to gemini-1.5-flash
        models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash']
        client = genai.Client(api_key=api_key)
        last_error = None
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                logger.info(f"AI report generated successfully using model: {model_name}")
                return response.text
            except APIError as e:
                err_str = str(e)
                logger.warning(f"Model {model_name} failed: {err_str[:200]}")
                # 429 quota exhaustion — try next model
                if '429' in err_str or 'RESOURCE_EXHAUSTED' in err_str:
                    last_error = f"Quota exhausted on {model_name}."
                    continue
                # Any other API error — bail out immediately
                return get_fallback_report(cycle, f"Gemini API Error: {err_str[:300]}")
            except Exception as e:
                logger.error(f"Unexpected error with model {model_name}: {e}")
                return get_fallback_report(cycle, f"Unexpected error: {str(e)[:300]}")

        hint = ("All Gemini models are quota-exhausted for this API key. "
                "Go to https://aistudio.google.com/ and create a fresh API key, "
                "or enable billing to increase your quota.")
        return get_fallback_report(cycle, hint)

def get_fallback_report(cycle, error_detail=""):
    """
    Returns a nicely formatted fallback report in case the API call fails or is not configured.
    """
    plan = cycle.treatment_plan
    dosha = plan.get_target_dosha_display() if plan else "Constitutional"
    
    return f"""**Executive Summary**
This report contains a standard completion analysis for {cycle.patient.username}. Although the automated AI narrative system is currently offline or unconfigured, we have compiled your basic clinical metrics.

**Clinical Wellness Assessment**
Your prescribed plan, {plan.name if plan else 'Ayurvedic Treatment'}, was targeted to balance the {dosha} dosha. Based on your initial diagnosis, your therapist noted a primary focus on restoring system equilibrium.

**Commitment & Progress Analysis**
Our records show an attendance rate of {cycle.attendances.filter(is_attended=True).count()} of {plan.duration_days if plan else 7} days. High attendance ensures optimal therapeutic absorption.

**AI-Recommended Lifestyle & Dietary Plan**
- **Dietary (Ahar):** Follow a diet tailored to pacify {dosha} dosha. Favor warm, freshly prepared meals and avoid ice-cold beverages.
- **Lifestyle (Vihar):** Keep a regular schedule for sleeping, waking, and eating. Gentle yoga and meditation are recommended.

**Long-Term Prognosis & Follow-Up**
We advise checking in with your therapist or doctor in 4-6 weeks to evaluate your progress.
*(Diagnostic note: {error_detail})*"""
