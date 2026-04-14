from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
     
    # User Flows
    path('profile/', views.user_profile, name='user_profile'),
    path('notification/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('patient/book/', views.book_appointment, name='book_appointment'),
    path('patient/payment/<int:cycle_id>/', views.dummy_payment, name='dummy_payment'),
    path('patient/slots/', views.get_available_slots, name='get_available_slots'),
    path('patient/decision/<int:report_id>/', views.treatment_decision, name='treatment_decision'),
    path('patient/feedback/<int:cycle_id>/', views.submit_feedback, name='submit_feedback'),
    path('patient/cycle/<int:cycle_id>/cancel/', views.cancel_active_cycle, name='cancel_active_cycle'),
    
    # Therapist Flows
    path('therapist/appointment/<int:appointment_id>/status/', views.update_appointment_status, name='update_appointment_status'),
    path('therapist/appointment/<int:appointment_id>/diagnose/', views.submit_diagnosis, name='submit_diagnosis'),
    path('therapist/cycle/<int:cycle_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    path('therapist/cycle/<int:cycle_id>/end/', views.end_treatment, name='end_treatment'),
    path('cycle/<int:cycle_id>/pdf/', views.download_treatment_pdf, name='download_treatment_pdf'),
    
    # Center Head Flows
    path('head/assign/', views.assign_therapist, name='assign_therapist'),
    path('head/add-user/', views.add_user, name='add_user'),
    path('head/remove-user/<int:user_id>/', views.remove_user, name='remove_user'),
]