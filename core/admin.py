from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, TreatmentPlan, Appointment, DiagnosisReport, TreatmentCycle, Attendance,Notification

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(TreatmentPlan)
admin.site.register(Appointment)
admin.site.register(DiagnosisReport)
admin.site.register(TreatmentCycle)
admin.site.register(Attendance)
admin.site.register(Notification)

