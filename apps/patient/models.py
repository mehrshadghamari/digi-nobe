from django.db import models
from django.utils import timezone

from apps.account.models import TimeStampedModel
from apps.account.models import User
from apps.doctor.models import DoctorUser
from apps.doctor.models import ShiftTime


class PatientUser(TimeStampedModel):
    """
    Represents a Patient user.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Patient profile for {self.user.username}"

    class Meta:
        verbose_name = "Patient User"
        verbose_name_plural = "Patient Users"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    patient = models.ForeignKey(PatientUser, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(DoctorUser, on_delete=models.CASCADE, related_name="appointments")
    shift_time = models.ForeignKey(ShiftTime, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"

    def __str__(self):
        return f"Appointment on {self.date} with {self.doctor.user.full_name} for {self.patient.user.full_name}"
