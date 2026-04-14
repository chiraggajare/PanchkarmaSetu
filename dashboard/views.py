from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from datetime import date

from appointments.models import Appointment
from treatments.models import PatientTreatment, Feedback, TreatmentPlan
from accounts.models import CustomUser, TherapistProfile


@login_required
def home(request):
    user = request.user
    if user.is_patient():
        return patient_dashboard(request)
    elif user.is_therapist():
        return therapist_dashboard(request)
    elif user.is_centre_head():
        return centre_head_dashboard(request)
    # Fallback
    return redirect('accounts:login')


@login_required
def patient_dashboard(request):
    user = request.user
    appointments = Appointment.objects.filter(patient=user).select_related('therapist').order_by('-date')
    active_treatment = PatientTreatment.objects.filter(patient=user, status='active').select_related('plan', 'therapist').first()
    completed_treatments = PatientTreatment.objects.filter(patient=user, status='completed').select_related('plan')

    context = {
        'appointments': appointments[:5],
        'active_treatment': active_treatment,
        'completed_treatments': completed_treatments,
        'attendance_grid': active_treatment.get_attendance_grid() if active_treatment else [],
        'today': date.today(),
    }
    return render(request, 'dashboard/patient_dashboard.html', context)


@login_required
def therapist_dashboard(request):
    user = request.user
    my_appointments = Appointment.objects.filter(therapist=user).select_related('patient').order_by('-date')
    active_treatments = PatientTreatment.objects.filter(therapist=user, status='active').select_related('patient', 'plan')
    completed_treatments = PatientTreatment.objects.filter(therapist=user, status='completed').select_related('patient', 'plan')
    feedbacks = Feedback.objects.filter(patient_treatment__therapist=user).select_related('patient_treatment__patient')

    avg_rating = feedbacks.aggregate(
        avg_therapist=Avg('therapist_rating'),
        avg_satisfaction=Avg('satisfaction_rating')
    )

    context = {
        'my_appointments': my_appointments[:10],
        'active_treatments': active_treatments,
        'completed_treatments': completed_treatments,
        'feedbacks': feedbacks[:5],
        'avg_rating': avg_rating,
        'today': date.today(),
    }
    return render(request, 'dashboard/therapist_dashboard.html', context)


@login_required
def centre_head_dashboard(request):
    if not request.user.is_centre_head():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')

    all_appointments = Appointment.objects.all().select_related('patient', 'therapist').order_by('-date')
    therapists = CustomUser.objects.filter(role='therapist').select_related('therapist_profile')

    # Stats
    stats = {
        'total_appointments': all_appointments.count(),
        'scheduled': all_appointments.filter(status='scheduled').count(),
        'in_progress': all_appointments.filter(status='in_progress').count(),
        'completed': all_appointments.filter(status='completed').count(),
        'cancelled': all_appointments.filter(status='cancelled').count(),
    }

    # Satisfaction data for chart
    feedbacks = Feedback.objects.all()
    satisfaction_data = {
        '5': feedbacks.filter(satisfaction_rating=5).count(),
        '4': feedbacks.filter(satisfaction_rating=4).count(),
        '3': feedbacks.filter(satisfaction_rating=3).count(),
        '2': feedbacks.filter(satisfaction_rating=2).count(),
        '1': feedbacks.filter(satisfaction_rating=1).count(),
    }

    context = {
        'all_appointments': all_appointments[:20],
        'therapists': therapists,
        'stats': stats,
        'satisfaction_data': satisfaction_data,
    }
    return render(request, 'dashboard/centre_head_dashboard.html', context)


@login_required
def assign_therapist(request, appointment_pk):
    if not request.user.is_centre_head():
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    appointment = get_object_or_404(Appointment, pk=appointment_pk)
    if request.method == 'POST':
        therapist_id = request.POST.get('therapist_id')
        therapist = get_object_or_404(CustomUser, pk=therapist_id, role='therapist')
        appointment.therapist = therapist
        appointment.save()
        messages.success(request, f'Therapist {therapist.get_full_name()} assigned to appointment.')
    return redirect('dashboard:centre_head')


@login_required
def therapist_patients(request):
    if not request.user.is_therapist():
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    treatments = PatientTreatment.objects.filter(
        therapist=request.user
    ).select_related('patient', 'plan').order_by('-created_at')
    return render(request, 'dashboard/therapist_patients.html', {'treatments': treatments})
