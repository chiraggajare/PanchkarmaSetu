import json
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Appointment, TIME_SLOT_CHOICES
from .forms import AppointmentBookingForm
from treatments.models import DiagnosisReport


def get_booked_slots(selected_date):
    """Returns list of booked time_slots on a given date."""
    booked = Appointment.objects.filter(
        date=selected_date, status__in=['scheduled', 'in_progress']
    ).values_list('time_slot', flat=True)
    return list(booked)


@login_required
def book_appointment(request):
    if not request.user.is_patient():
        messages.error(request, 'Only patients can book appointments.')
        return redirect('dashboard:home')

    # Build calendar data for next 30 days
    today = date.today()
    calendar_days = []
    for i in range(0, 30):
        day = today + timedelta(days=i)
        if day.weekday() < 6:  # Mon-Sat open
            booked = Appointment.objects.filter(
                date=day, status__in=['scheduled', 'in_progress']
            ).count()
            total_slots = len(TIME_SLOT_CHOICES)
            calendar_days.append({
                'date': str(day),
                'day_name': day.strftime('%a'),
                'day_num': day.day,
                'month': day.strftime('%b'),
                'full': booked >= total_slots,
                'partially_booked': 0 < booked < total_slots,
                'is_today': day == today,
            })

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            # Check if slot is taken
            exists = Appointment.objects.filter(
                date=appointment.date,
                time_slot=appointment.time_slot,
                status__in=['scheduled', 'in_progress']
            ).exists()
            if exists:
                messages.error(request, 'This slot is already booked. Please select another.')
            else:
                appointment.save()
                messages.success(request, f'Appointment booked for {appointment.date} at {appointment.get_time_display()}!')
                return redirect('appointments:my_appointments')
        else:
            messages.error(request, 'Please fill in all required fields.')
    else:
        form = AppointmentBookingForm()

    return render(request, 'appointments/book_appointment.html', {
        'form': form,
        'calendar_days': json.dumps(calendar_days),
        'time_slots': TIME_SLOT_CHOICES,
    })


@login_required
def get_slots_for_date(request):
    """AJAX: returns slot availability for a given date."""
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'No date provided'}, status=400)
    try:
        selected_date = date.fromisoformat(date_str)
    except ValueError:
        return JsonResponse({'error': 'Invalid date'}, status=400)

    booked = get_booked_slots(selected_date)
    slots_data = []
    for code, label in TIME_SLOT_CHOICES:
        slots_data.append({
            'code': code,
            'label': label,
            'booked': code in booked,
        })
    return JsonResponse({'slots': slots_data})


@login_required
def my_appointments(request):
    user = request.user
    if user.is_patient():
        appointments = Appointment.objects.filter(patient=user).select_related('therapist')
    elif user.is_therapist():
        appointments = Appointment.objects.filter(therapist=user).select_related('patient')
    else:
        appointments = Appointment.objects.all().select_related('patient', 'therapist')

    return render(request, 'appointments/my_appointments.html', {'appointments': appointments})


@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    user = request.user

    # Access check
    if user.is_patient() and appointment.patient != user:
        messages.error(request, 'Access denied.')
        return redirect('appointments:my_appointments')
    if user.is_therapist() and appointment.therapist != user:
        messages.error(request, 'Access denied.')
        return redirect('appointments:my_appointments')

    diagnosis = getattr(appointment, 'diagnosis_report', None)
    patient_treatment = getattr(appointment, 'patient_treatment', None)

    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment,
        'diagnosis': diagnosis,
        'patient_treatment': patient_treatment,
    })


@login_required
@require_POST
def start_session(request, pk):
    if not request.user.is_therapist():
        messages.error(request, 'Only therapists can start sessions.')
        return redirect('dashboard:home')
    appointment = get_object_or_404(Appointment, pk=pk, therapist=request.user)
    if appointment.status == 'scheduled':
        appointment.status = 'in_progress'
        appointment.save()
        messages.success(request, 'Session started. Status updated to In Progress.')
    return redirect('appointments:detail', pk=pk)


@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)
    if appointment.status == 'scheduled':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled.')
    else:
        messages.error(request, 'This appointment cannot be cancelled.')
    return redirect('appointments:my_appointments')
