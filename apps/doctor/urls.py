from django.urls import path

from apps.doctor import views

urlpatterns = [
    path("doctor-detail/<int:doctor_id>/", views.DoctorDetail.as_view(), name="doctor_detail"),
    path("doctor-list/", views.DocotorList.as_view(), name="doctor_list"),
]
