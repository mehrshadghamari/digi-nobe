import random

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from faker import Faker

from apps.account.models import User
from apps.doctor.models import DoctorAddress
from apps.doctor.models import DoctorCity
from apps.doctor.models import DoctorUser
from apps.doctor.models import ShiftTime
from apps.doctor.models import Telephone
from apps.doctor.models import WeekDays


class Command(BaseCommand):
    help = "Generates dummy data for Doctor app models"

    def handle(self, *args, **kwargs):
        # Initialize Faker with the Persian locale
        fake = Faker('fa_IR')

        for _ in range(20):  # Loop to create 20 sets of data
            # Create dummy User with more realistic data
            username = fake.user_name()
            email = fake.email()
            password = "12345678"  # Consider using set_password for hashing
            phone_number = f"98912{random.randint(1000000, 9999999)}"    # Generates a realistic phone number

            user_instance = User.objects.create(
                username=username, email=email, password=password, phone_number=phone_number
            )

            # Create dummy DoctorCity with Persian names
            city = DoctorCity.objects.create(
                province=fake.state(),  # Generates a realistic Persian province name
                city=fake.city()  # Generates a realistic Persian city name
            )

            # Create dummy DoctorUser
            doctor_user = DoctorUser.objects.create(
                user=user_instance,
                medical_system_code=random.randint(1000, 9999),
                bio=fake.text(max_nb_chars=200),  # Generates realistic text for bio
                cost_of_visit=random.randint(10000, 100000),
                city=city,
            )

            # Create dummy DoctorAddress with a realistic Persian address
            DoctorAddress.objects.create(
                doctor=doctor_user,
                address=fake.address(),  # Generates a realistic Persian address
                lat=fake.latitude(),
                lng=fake.longitude(),
            )

            # Create dummy Telephone with a realistic phone number
            Telephone.objects.create(doctor=doctor_user, call_number=random.randint(100000000, 999999999))

            # Create dummy WeekDays with choices
            for choice in WeekDays.choice_days:
                day, _ = choice
                week_day = WeekDays.objects.create(doctor=doctor_user, day=day)

                # Create dummy ShiftTime for each WeekDay with more structured times
                ShiftTime.objects.create(
                    week_day=week_day,
                    start_time=random.choice(["08:00", "10:00", "12:00"]),
                    end_time=random.choice(["14:00", "16:00", "19:00"]),
                    capacity=random.randint(1, 10),
                    reserved_capacity=random.randint(0, 5),
                )

        self.stdout.write(self.style.SUCCESS("Successfully created dummy data for Doctor app"))
