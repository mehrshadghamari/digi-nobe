from django.urls import path
from . import views


urlpatterns = [
    path('login/doctor/', views.UserLogin.as_view(role='doctor')),
    path('login/patient/', views.UserLogin.as_view(role='patient')),
    path('api/signup/patient/', views.PatientSignup.as_view(), name='patient_signup'),
    path('api/signup/doctor/', views.DoctorSignup.as_view(), name='doctor_signup'),
]
