from django.db import models

from apps.account.models import TimeStampedModel
from apps.account.models import User


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
