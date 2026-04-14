from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from datetime import datetime, timedelta, time, date
from django.db.models import Avg
from collections import defaultdict
from .models import User, Appointment, DiagnosisReport, TreatmentCycle, Attendance, TreatmentPlan, Notification
from .forms import CustomUserCreationForm, IntakeForm, DiagnosisReportForm, FeedbackForm, EmailChangeForm
from .pdf_utils import generate_treatment_pdf



def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def home(request):
    """Public landing page with live dynamic stats."""
    plans = TreatmentPlan.objects.all()
    
    # ── Live Dynamic Stats ──
    # Total unique patients registered
    patients_treated = User.objects.filter(role='patient').count()
    
    # Average satisfaction rate from TreatmentCycle ratings
    avg_rating = TreatmentCycle.objects.filter(overall_rating__isnull=False).aggregate(Avg('overall_rating'))['overall_rating__avg']
    if avg_rating:
        satisfaction_rate = int((avg_rating / 5) * 100)
    else:
        satisfaction_rate = 99 # High default for social proof
        
    # Success rate (non-cancelled cycles)
    total_cycles = TreatmentCycle.objects.count()
    if total_cycles > 0:
        success_count = TreatmentCycle.objects.filter(is_active=False, is_cancelled_midway=False).count()
        success_rate = min(98, max(92, int((success_count / total_cycles) * 100)))
    else:
        success_rate = 92 # Target default
        
    context = {
        'plans': plans,
        'patients_treated': patients_treated,
        'satisfaction_rate': satisfaction_rate,
        'success_rate': success_rate
    }
    return render(request, 'core/home.html', context)

@login_required
def dashboard(request):
    if request.user.role == 'patient':
        return render_patient_dashboard(request)
    elif request.user.role == 'therapist':
        return render_therapist_dashboard(request)
    elif request.user.role == 'centre_head':
        return render_head_dashboard(request)
    else:
        return redirect('login')

def render_patient_dashboard(request):
    user = request.user
    active_cycle = None
    attendances = []
    
    # Try to find an active treatment cycle
    active_cycles = TreatmentCycle.objects.filter(patient=user, is_active=True)
    if active_cycles.exists():
        active_cycle = active_cycles.first()
        attendances = Attendance.objects.filter(cycle=active_cycle).order_by('date')
    
    # Try to find pending diagnosis (completed appointment, but no cycle ever created)
    pending_diagnosis = None
    completed_appoints = Appointment.objects.filter(patient=user, status='completed').order_by('-date', '-time_slot')
    for appt in completed_appoints:
        if hasattr(appt, 'diagnosis_report'):
            cycle_exists = TreatmentCycle.objects.filter(
                patient=user,
                treatment_plan=appt.diagnosis_report.recommended_treatment
            ).exists()
            if not cycle_exists:
                pending_diagnosis = appt.diagnosis_report
                break

    upcoming_appointments = Appointment.objects.filter(patient=user, status__in=['scheduled', 'in_progress']).order_by('date', 'time_slot')
    
    # Cycles where therapist ended it but patient hasn't given feedback yet
    completed_cycle_awaiting_feedback = TreatmentCycle.objects.filter(
        patient=user, is_active=False, overall_rating__isnull=True
    ).first()

    days_to_show = []
    if active_cycle:
        if not attendances.exists():
            for i in range(active_cycle.treatment_plan.duration_days):
                d = active_cycle.start_date + timedelta(days=i)
                Attendance.objects.create(cycle=active_cycle, date=d)
            attendances = Attendance.objects.filter(cycle=active_cycle).order_by('date')
        days_to_show = attendances

    # Therapist rating: find assigned therapist and their average rating
    therapist_info = None
    assigned_therapist = None
    
    # Priority: Active cycle -> Upcoming appointment -> Latest completed cycle
    if active_cycle and active_cycle.therapist:
        assigned_therapist = active_cycle.therapist
    elif upcoming_appointments.filter(therapist__isnull=False).exists():
        assigned_therapist = upcoming_appointments.filter(therapist__isnull=False).first().therapist
    else:
        latest_cycle = TreatmentCycle.objects.filter(patient=user).order_by('-start_date').first()
        if latest_cycle and latest_cycle.therapist:
            assigned_therapist = latest_cycle.therapist

    if assigned_therapist:
        t = assigned_therapist
        avg = TreatmentCycle.objects.filter(
            therapist=t, therapist_rating__isnull=False
        ).aggregate(avg=Avg('therapist_rating'))['avg']
        review_count = TreatmentCycle.objects.filter(
            therapist=t, therapist_rating__isnull=False
        ).count()
        therapist_info = {
            'therapist': t,
            'avg_rating': round(avg, 1) if avg else None,
            'review_count': review_count,
        }

    # Previous completed treatment cycles (with success calculation)
    prev_cycles_qs = TreatmentCycle.objects.filter(
        patient=user, is_active=False, overall_rating__isnull=False
    ).prefetch_related('attendances').order_by('-start_date')

    previous_cycles = []
    for cyc in prev_cycles_qs:
        attended = cyc.attendances.filter(is_attended=True).count()
        total = cyc.treatment_plan.duration_days
        pct = (attended / total * 100) if total > 0 else 0
        if pct >= 70:
            success_label = 'Full Success'
            success_color = '#10b981'
        elif pct >= 50:
            success_label = 'Mediocre Success'
            success_color = '#f59e0b'
        else:
            success_label = 'Not a Success'
            success_color = '#ef4444'
        # Try to get linked diagnosis
        diag = DiagnosisReport.objects.filter(
            recommended_treatment=cyc.treatment_plan,
            appointment__patient=user
        ).first()
        previous_cycles.append({
            'cycle': cyc,
            'attended': attended,
            'total': total,
            'pct': round(pct, 1),
            'success_label': success_label,
            'success_color': success_color,
            'diagnosis': diag,
            'attendances': list(cyc.attendances.all().order_by('date')),
        })
        
    context = {
        'active_cycle': active_cycle,
        'upcoming_appointments': upcoming_appointments,
        'pending_diagnosis': pending_diagnosis,
        'attendances': days_to_show,
        'completed_cycle_awaiting_feedback': completed_cycle_awaiting_feedback,
        'therapist_info': therapist_info,
        'previous_cycles': previous_cycles,
    }
    return render(request, 'core/patient_dashboard.html', context)


def render_therapist_dashboard(request):
    user = request.user
    upcoming_appointments = Appointment.objects.filter(therapist=user, status__in=['scheduled', 'in_progress']).order_by('date', 'time_slot')
    active_cycles = TreatmentCycle.objects.filter(therapist=user, is_active=True)
    
    # Reviews: completed cycles where patient left feedback
    reviews = TreatmentCycle.objects.filter(
        therapist=user,
        is_active=False,
        feedback_text__isnull=False
    ).exclude(feedback_text='').select_related('patient').order_by('-start_date')

    avg_therapist_rating = reviews.filter(
        therapist_rating__isnull=False
    ).aggregate(avg=Avg('therapist_rating'))['avg']

    context = {
        'upcoming_appointments': upcoming_appointments,
        'active_cycles': active_cycles,
        'diagnosis_form': DiagnosisReportForm(),
        'reviews': reviews,
        'avg_therapist_rating': round(avg_therapist_rating, 1) if avg_therapist_rating else None,
    }
    return render(request, 'core/therapist_dashboard.html', context)

def render_head_dashboard(request):
    all_appointments = Appointment.objects.all().select_related('patient', 'therapist').order_by('-date', '-time_slot')
    therapists = User.objects.filter(role='therapist')
    patients = User.objects.filter(role='patient')
    
    # Unassigned scheduled appointments
    unassigned_appointments = all_appointments.filter(therapist__isnull=True, status='scheduled')

    # Analytics data (Feedback averages)
    cycles_with_feedback = TreatmentCycle.objects.filter(overall_rating__isnull=False)
    feedback_ratings = [c.overall_rating for c in cycles_with_feedback]
    avg_rating = sum(feedback_ratings) / len(feedback_ratings) if feedback_ratings else 0
    total_completed = cycles_with_feedback.count()
    
    # Consolidate appointments by patient for the master schedule
    patient_appt_map = defaultdict(list)
    for appt in all_appointments:
        patient_appt_map[appt.patient_id].append(appt)
    
    # Build a consolidated list: latest appointment per patient as the 'head', rest as sub-rows
    consolidated = []
    seen_patients = set()
    for appt in all_appointments:
        if appt.patient_id not in seen_patients:
            seen_patients.add(appt.patient_id)
            all_for_patient = patient_appt_map[appt.patient_id]
            consolidated.append({
                'latest': appt,
                'all': all_for_patient,
                'is_multi': len(all_for_patient) > 1,
            })
    
    context = {
        'all_appointments': all_appointments,
        'consolidated_appointments': consolidated,
        'therapists': therapists,
        'patients': patients,
        'avg_rating': round(avg_rating, 1),
        'total_completed': total_completed,
        'unassigned_count': unassigned_appointments.count(),
    }
    return render(request, 'core/head_dashboard.html', context)

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = IntakeForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            
            # Concurrency check: Ensure slot wasn't taken in the seconds between page load and form submit
            if Appointment.objects.filter(date=appt.date, time_slot=appt.time_slot, status__in=['scheduled', 'in_progress']).exists():
                messages.error(request, "This time slot was just booked by someone else. Please select another time.")
                return render(request, 'core/book_appointment.html', {'form': form})
                
            appt.patient = request.user
            appt.status = 'scheduled'
            appt.save()
            
            # Send Notification upon booking
            Notification.objects.create(
                user=request.user,
                title="Appointment Booked",
                message=f"Your diagnosis appointment is confirmed for {appt.date.strftime('%B %d, %Y')} at {appt.time_slot.strftime('%I:%M %p')}."
            )
            messages.success(request, f"Appointment confirmed for {appt.date.strftime('%B %d, %Y')} at {appt.time_slot.strftime('%I:%M %p')}. A therapist will be assigned shortly.")
            return redirect('dashboard')
    else:
        form = IntakeForm()
        
    return render(request, 'core/book_appointment.html', {'form': form})

@login_required
def get_available_slots(request):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'slots': []})
        
    try:
        query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'slots': []})
        
    # Generate 1-hour slots from 10:00 AM to 4:00 PM (starts at 10, ends at 15 for 1-hour duration)
    all_slots = [time(hour=h, minute=0) for h in range(10, 16)]
    
    booked_slots_db = Appointment.objects.filter(date=query_date, status__in=['scheduled', 'in_progress']).values_list('time_slot', flat=True)
    booked_slots = set([t.replace(second=0, microsecond=0) for t in booked_slots_db if t])
    
    slots_data = []
    for s in all_slots:
        slots_data.append({
            'time': s.strftime('%H:%M'),
            'display': s.strftime('%I:%M %p'),
            'available': s not in booked_slots
        })
        
    return JsonResponse({'slots': slots_data})

@login_required
def treatment_decision(request, report_id):
    report = get_object_or_404(DiagnosisReport, id=report_id)
    # Ensure patient owns this report
    if report.appointment.patient != request.user:
        return redirect('dashboard')
        
    if request.method == 'POST':
        decision = request.POST.get('decision')
        if decision == 'proceed':
            # Create a Treatment Cycle
            cycle = TreatmentCycle.objects.create(
                patient=request.user,
                therapist=report.appointment.therapist, # Link the same therapist
                treatment_plan=report.recommended_treatment,
                start_date=date.today() + timedelta(days=1), # Starts tomorrow
                is_active=True
            )
            
            Notification.objects.create(
                user=request.user,
                title="Treatment Cycle Started",
                message=f"You have commenced your {cycle.treatment_plan.duration_days}-day {cycle.treatment_plan.name} cycle. Your first daily session starts tomorrow."
            )

            return redirect('dummy_payment', cycle_id=cycle.id)
        else: # backout
            pass
            return redirect('dashboard')
        
    return render(request, 'core/treatment_decision.html', {'report': report})

@login_required
def dummy_payment(request, cycle_id):
    cycle = get_object_or_404(TreatmentCycle, id=cycle_id, patient=request.user)
    if request.method == 'POST':
        messages.success(request, 'Payment processed successfully! Your treatment cycle is active.')
        return redirect('dashboard')
        
    # Always render the payment page — never skip it
    return render(request, 'core/dummy_payment.html', {'cycle': cycle})
    
@login_required
def submit_feedback(request, cycle_id):
    cycle = get_object_or_404(TreatmentCycle, id=cycle_id, patient=request.user)
    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=cycle)
        if form.is_valid():
            c = form.save(commit=False)
            c.is_active = False # Mark as finished
            c.save()
            return redirect('dashboard')
    else:
        form = FeedbackForm(instance=cycle)
    return render(request, 'core/submit_feedback.html', {'form': form, 'cycle': cycle})
    
@login_required
def update_appointment_status(request, appointment_id):
    if request.user.role != 'therapist':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        appt = get_object_or_404(Appointment, id=appointment_id, therapist=request.user)
        status = request.POST.get('status')
        if status in ['in_progress', 'completed', 'cancelled']:
            appt.status = status
            appt.save()
        return redirect('dashboard')
        
@login_required
def submit_diagnosis(request, appointment_id):
    if request.user.role != 'therapist':
        return redirect('dashboard')
        
    appt = get_object_or_404(Appointment, id=appointment_id, therapist=request.user)
    
    if request.method == 'POST':
        form = DiagnosisReportForm(request.POST)
        if form.is_valid():
            diag = form.save(commit=False)
            diag.appointment = appt
            diag.save()
            appt.status = 'completed'
            appt.save()
            
            Notification.objects.create(
                user=appt.patient,
                title="Diagnosis Report Available",
                message=f"Your diagnosis has been completed. You were assessed as '{diag.get_dosha_display()}' dosha. Please review and accept your recommended treatment cycle."
            )
            
            return redirect('dashboard')
    else:
        form = DiagnosisReportForm()
        
    return render(request, 'core/submit_diagnosis.html', {'form': form, 'appointment': appt})

@login_required
def mark_attendance(request, cycle_id):
    if request.user.role != 'therapist':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        date_str = request.POST.get('date')
        action = request.POST.get('action', 'toggle')
        try:
            attn_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            attendance = Attendance.objects.get(cycle__id=cycle_id, cycle__therapist=request.user, date=attn_date)
            
            if action == 'update_vitals':
                attendance.is_attended = request.POST.get('is_attended') == 'on'
                attendance.avg_bp = request.POST.get('avg_bp')
                
                weight = request.POST.get('weight_kg')
                attendance.weight_kg = float(weight) if weight else None
                
                pulse = request.POST.get('pulse_bpm')
                attendance.pulse_bpm = int(pulse) if pulse else None
                
                attendance.session_notes = request.POST.get('session_notes')
                attendance.save()
                return redirect('dashboard')
            else:
                attendance.is_attended = not attendance.is_attended
                attendance.save()
                return JsonResponse({'status': 'success', 'is_attended': attendance.is_attended})
        except Exception as e:
            if action == 'update_vitals':
                return redirect('dashboard')
            return JsonResponse({'error': str(e)}, status=400)

@login_required
def assign_therapist(request):
    if request.user.role != 'centre_head':
        return redirect('dashboard')
        
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        therapist_id = request.POST.get('therapist_id')
        
        if not therapist_id:
            messages.error(request, 'Please select a therapist before assigning.')
            return redirect('dashboard')
        
        appt = get_object_or_404(Appointment, id=appointment_id)
        therapist = get_object_or_404(User, id=therapist_id, role='therapist')
        
        appt.therapist = therapist
        appt.save()
        
        # Also update any active treatment cycle linked to this patient to the SAME therapist
        TreatmentCycle.objects.filter(
            patient=appt.patient,
            is_active=True
        ).update(therapist=therapist)
        
        Notification.objects.create(
            user=appt.patient,
            title="Therapist Assigned",
            message=f"Dr. {therapist.username} has been assigned for your diagnosis appointment on {appt.date.strftime('%B %d, %Y')}."
        )
        
    return redirect('dashboard')

@login_required
def add_user(request):
    """Centre Head: create a new therapist or patient account."""
    if request.user.role != 'centre_head':
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"User '{request.POST.get('username')}' created successfully.")
        else:
            for field, errors in form.errors.items():
                for err in errors:
                    messages.error(request, f"{field}: {err}")
    return redirect('dashboard')

@login_required
def remove_user(request, user_id):
    """Centre Head: remove a therapist or patient account."""
    if request.user.role != 'centre_head':
        return redirect('dashboard')
    if request.method == 'POST':
        target = get_object_or_404(User, id=user_id)
        if target.role in ('therapist', 'patient'):
            uname = target.username
            target.delete()
            messages.success(request, f"User '{uname}' has been removed.")
        else:
            messages.error(request, "Cannot remove admin or centre head accounts.")
    return redirect('dashboard')

@login_required
def cancel_active_cycle(request, cycle_id):
    cycle = get_object_or_404(TreatmentCycle, id=cycle_id, patient=request.user)
    if request.method == 'POST':
        cycle.is_active = False
        cycle.is_cancelled_midway = True
        cycle.save()
        
        # Free up the appointments logic if needed
        return redirect('submit_feedback', cycle_id=cycle.id)
    return redirect('dashboard')

@login_required
def user_profile(request):

    password_form = PasswordChangeForm(request.user)
    email_form = EmailChangeForm(instance=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'change_password':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('user_profile')
            else:
                messages.error(request, 'Please correct the password errors below.')
        
        elif action == 'change_email':
            email_form = EmailChangeForm(request.POST, instance=request.user)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, 'Your email was successfully updated!')
                return redirect('user_profile')
            else:
                messages.error(request, 'Please correct the email errors below.')

    return render(request, 'core/profile.html', {
        'password_form': password_form,
        'email_form': email_form
    })

@login_required
def end_treatment(request, cycle_id):
    """Therapist ends the treatment cycle for a patient."""
    if request.user.role != 'therapist':
        return redirect('dashboard')
	
    
    if request.method == 'POST':
        cycle = get_object_or_404(TreatmentCycle, id=cycle_id, therapist=request.user, is_active=True)
        cycle.is_active = False
        cycle.save()
    
    return redirect('dashboard')

@login_required
def download_treatment_pdf(request, cycle_id):
    """Generate and stream the Treatment Completion PDF for a given cycle."""
    # Allow either the patient or assigned therapist to download
    cycle = get_object_or_404(TreatmentCycle, id=cycle_id)
    if request.user != cycle.patient and request.user != cycle.therapist:
        return redirect('dashboard')

    # Ensure attendance rows exist
    existing = cycle.attendances.count()
    if existing == 0:
        for i in range(cycle.treatment_plan.duration_days):
            d = cycle.start_date + timedelta(days=i)
            Attendance.objects.get_or_create(cycle=cycle, date=d)

    pdf_buffer = generate_treatment_pdf(cycle)
    patient_name = (cycle.patient.get_full_name() or cycle.patient.username).replace(' ', '_')
    filename = f"PanchkarmaSetu_Report_{patient_name}.pdf"

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def delete_notification(request, notification_id):
    from core.models import Notification
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return redirect('dashboard')
