from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Appointment, DiagnosisReport, TreatmentCycle

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role',)

class IntakeForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['height', 'weight', 'age', 'prior_health_issues', 'date', 'time_slot']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time_slot': forms.TimeInput(attrs={'type': 'time'}), 
            'prior_health_issues': forms.Textarea(attrs={'rows': 3}),
        }

class DiagnosisReportForm(forms.ModelForm):
    class Meta:
        model = DiagnosisReport
        fields = ['dosha', 'diagnosis_result', 'recommended_treatment']
        widgets = {
            'diagnosis_result': forms.Textarea(attrs={'rows': 4}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = TreatmentCycle
        fields = ['feedback_text', 'therapist_rating', 'overall_rating']
        widgets = {
            'feedback_text': forms.Textarea(attrs={'rows': 3}),
            'therapist_rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'overall_rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }

class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your new email'}),
        }
