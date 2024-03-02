from django.urls import path

from . import views

urlpatterns = [
    path("login/doctor/", views.DoctorLogin.as_view()),
    path("login/patient/", views.PatientLogin.as_view()),
    path("signup/patient/", views.PatientSignup.as_view(), name="patient_signup"),
    path("signup/doctor/", views.DoctorSignup.as_view(), name="doctor_signup"),
]
