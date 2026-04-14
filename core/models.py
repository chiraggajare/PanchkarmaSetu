from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('therapist', 'Therapist'),
        ('centre_head', 'Centre Head'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')


class TreatmentPlan(models.Model): 
    DOSHA_CHOICES = (
        ('vata', 'Vata'),
        ('pitta', 'Pitta'),
        ('kapha', 'Kapha'),
        ('vata_pitta', 'Vata-Pitta'),
        ('pitta_kapha', 'Pitta-Kapha'),
        ('vata_kapha', 'Vata-Kapha'),
        ('tridoshic', 'Tridoshic'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_days = models.IntegerField(help_text="Usually 7 to 15 days")
    target_dosha = models.CharField(max_length=20, choices=DOSHA_CHOICES)
    detailed_info = models.TextField(blank=True, help_text="In-depth point-wise explanation of the treatment for patients")
    
    def __str__(self):
        return f"{self.name} ({self.duration_days} days) - {self.get_target_dosha_display()}"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    therapist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_appointments', limit_choices_to={'role': 'therapist'})
    
    # Intake details
    height = models.FloatField(help_text="Height in cm")
    weight = models.FloatField(help_text="Weight in kg")
    age = models.IntegerField()
    prior_health_issues = models.TextField(blank=True)
    
    # Scheduling details
    date = models.DateField()
    time_slot = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    created_at = models.DateTimeField(auto_now_add=True)

class DiagnosisReport(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='diagnosis_report')
    dosha = models.CharField(max_length=20, choices=TreatmentPlan.DOSHA_CHOICES)
    diagnosis_result = models.TextField()
    recommended_treatment = models.ForeignKey(TreatmentPlan, on_delete=models.SET_NULL, null=True, blank=True)
    
class TreatmentCycle(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='treatment_cycles')
    therapist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_cycles', limit_choices_to={'role': 'therapist'})
    treatment_plan = models.ForeignKey(TreatmentPlan, on_delete=models.RESTRICT)
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    # Feedback
    feedback_text = models.TextField(blank=True, null=True)
    therapist_rating = models.IntegerField(null=True, blank=True, help_text="1 to 5 stars")
    overall_rating = models.IntegerField(null=True, blank=True, help_text="1 to 5 stars")
    is_cancelled_midway = models.BooleanField(default=False)
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class Attendance(models.Model):
    cycle = models.ForeignKey(TreatmentCycle, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    is_attended = models.BooleanField(default=False)
    # Daily clinical vitals (filled by therapist when attended)
    avg_bp = models.CharField(max_length=20, blank=True, null=True, help_text="e.g., 120/80 mmHg")
    weight_kg = models.FloatField(blank=True, null=True, help_text="Patient weight in kg")
    pulse_bpm = models.IntegerField(blank=True, null=True, help_text="Pulse rate in bpm")
    session_notes = models.TextField(blank=True, null=True, help_text="Therapist's clinical notes for this session")

    class Meta:
        unique_together = ('cycle', 'date')
