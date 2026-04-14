from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('therapist', 'Therapist'),
        ('centre_head', 'Centre Head'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def is_patient(self):
        return self.role == 'patient'

    def is_therapist(self):
        return self.role == 'therapist'

    def is_centre_head(self):
        return self.role == 'centre_head'

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


class PatientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male','Male'),('female','Female'),('other','Other')], blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True)
    prior_health_issues = models.TextField(blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Profile: {self.user.get_full_name()}"


class TherapistProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='therapist_profile')
    specialization = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

    def average_rating(self):
        from treatments.models import Feedback
        feedbacks = Feedback.objects.filter(patient_treatment__therapist=self.user)
        if feedbacks.exists():
            total = sum(f.therapist_rating for f in feedbacks)
            return round(total / feedbacks.count(), 1)
        return 0
