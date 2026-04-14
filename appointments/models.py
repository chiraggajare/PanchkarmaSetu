from django.db import models
from django.conf import settings


TIME_SLOT_CHOICES = [
    ('10:00', '10:00 AM'),
    ('11:00', '11:00 AM'),
    ('12:00', '12:00 PM'),
    ('13:00', '01:00 PM'), 
    ('14:00', '02:00 PM'),
    ('15:00', '03:00 PM'),
]

STATUS_CHOICES = [
    ('scheduled', 'Scheduled'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('no_show', 'No Show'),
]


class Appointment(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='patient_appointments'
    )
    therapist = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='therapist_appointments'
    )
    date = models.DateField()
    time_slot = models.CharField(max_length=10, choices=TIME_SLOT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    # Patient health info at time of booking
    height_cm = models.DecimalField(max_digits=5, decimal_places=2)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)
    age = models.PositiveIntegerField()
    prior_health_issues = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['date', 'time_slot', 'therapist']
        ordering = ['-date', 'time_slot']

    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.date} {self.time_slot}"

    def get_time_display(self):
        return dict(TIME_SLOT_CHOICES).get(self.time_slot, self.time_slot)

    def is_booked(self):
        return self.status in ['scheduled', 'in_progress']
