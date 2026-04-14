from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/', views.book_appointment, name='book'),
    path('slots/', views.get_slots_for_date, name='slots_for_date'),
    path('my/', views.my_appointments, name='my_appointments'),
    path('<int:pk>/', views.appointment_detail, name='detail'),
    path('<int:pk>/start/', views.start_session, name='start_session'),
    path('<int:pk>/cancel/', views.cancel_appointment, name='cancel'),
]
