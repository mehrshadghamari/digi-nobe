from django.urls import path

from . import views

urlpatterns = [
    path("login/patient/", views.PatientLogin.as_view()),
    path("signup/patient/", views.PatientSignup.as_view(), name="patient_signup"),
    path("login/doctor/", views.DoctorLogin.as_view()),
    path("signup/doctor/", views.DoctorSignup.as_view(), name="doctor_signup"),
    path("specialists/", views.DoctorSpecialistList.as_view(), name="specialist-list"),
    path("insurances/", views.InsuranceList.as_view(), name="insurance-list"),
    path("doctor-city-list/", views.DoctorCityList.as_view(), name="doctor-city-list"),
]
