from django.urls import path

from . import views

urlpatterns = [
    path("patient/appointments/request/", views.AppointmentRequest.as_view(), name="appointment-request"),
    path("patient/appointments/history/", views.AppointmentHistory.as_view(), name="appointment-history"),
    path("patient/user/update/", views.PatientUserUpdateView.as_view(), name="patient-user-update"),
]
