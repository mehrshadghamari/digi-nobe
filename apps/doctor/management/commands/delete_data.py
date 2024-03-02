import random

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from apps.account.models import User
from apps.doctor.models import DoctorAddress
from apps.doctor.models import DoctorCity
from apps.doctor.models import DoctorUser
from apps.doctor.models import ShiftTime
from apps.doctor.models import Telephone
from apps.doctor.models import WeekDays


class Command(BaseCommand):
    help = "Deletes dummy data form project"  # noqa : A003 VNE003

    def handle(self, *args, **kwargs):
        models = [
            User,
            DoctorUser,
            DoctorCity,
            DoctorAddress,
            Telephone,
            WeekDays,
            ShiftTime,
        ]
        for m in models:  # noqa : VNE001
            if m == User:
                m.objects.filter(is_superuser=False).delete()
            else:
                m.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Deleting all dummy data from models "))
