from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('patient/', views.patient_dashboard, name='patient'),
    path('therapist/', views.therapist_dashboard, name='therapist'),
    path('therapist/patients/', views.therapist_patients, name='therapist_patients'),
    path('centre/', views.centre_head_dashboard, name='centre_head'),
    path('centre/assign/<int:appointment_pk>/', views.assign_therapist, name='assign_therapist'),
]
