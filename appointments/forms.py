from django import forms
from .models import Appointment, TIME_SLOT_CHOICES


class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time_slot', 'height_cm', 'weight_kg', 'age', 'prior_health_issues', 'notes']
        widgets = {
            'date': forms.HiddenInput(),
            'time_slot': forms.HiddenInput(),
            'prior_health_issues': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List any existing conditions, allergies, or medications...'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Any specific concerns for this visit?'}),
            'height_cm': forms.NumberInput(attrs={'placeholder': 'e.g. 170', 'step': '0.1'}),
            'weight_kg': forms.NumberInput(attrs={'placeholder': 'e.g. 70', 'step': '0.1'}),
            'age': forms.NumberInput(attrs={'placeholder': 'e.g. 35'}),
        }
        labels = {
            'height_cm': 'Height (cm)',
            'weight_kg': 'Weight (kg)',
        }

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and (age < 1 or age > 120):
            raise forms.ValidationError('Please enter a valid age.')
        return age
