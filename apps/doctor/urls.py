from django.urls import path

from apps.doctor import views

urlpatterns = [
    path("doctor-detail/<int:doctor_id>/", views.DoctorDetail.as_view(), name="doctor_detail"),
    path("doctor-list/", views.DoctorList.as_view(), name="doctor_list"),
    path("random-doctor-list/", views.HomePageDocotorList.as_view(), name="doctor_list"),
    path("search/", views.DoctorSearch.as_view(), name="doctor-search"),
    path("doctor-appointments-report/", views.AppointmentReport.as_view(), name="doctor-appointments-report"),
    path("doctor/user/update/", views.DoctorUserUpdateView.as_view(), name="doctor-user-update"),
    path("doctor/shifts/update/", views.DoctorAvailabilityUpdate.as_view(), name="doctor-shifts-update"),
]
