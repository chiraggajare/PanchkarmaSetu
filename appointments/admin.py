from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'therapist', 'date', 'time_slot', 'status']
    list_filter = ['status', 'date']
    search_fields = ['patient__username', 'patient__first_name', 'patient__last_name']
    date_hierarchy = 'date'

