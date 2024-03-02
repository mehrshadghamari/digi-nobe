from django.urls import path

from apps.doctor import views

urlpatterns = [
    path("doctor_detail/<int:doctor_id>/", views.DoctorDetail.as_view(), name="doctor_detail"),
]
