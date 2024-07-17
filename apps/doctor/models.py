from django.db import models

from apps.account.models import TimeStampedModel
from apps.account.models import User


class DoctorCity(TimeStampedModel):
    """
    Represents a city where a doctor practices.
    """

    province = models.CharField(max_length=60)
    city = models.CharField(max_length=60, null=True, blank=True)

    def __str__(self):
        return f"Province: {self.province} - City: {self.city}"

    class Meta:
        verbose_name = "Doctor City"
        verbose_name_plural = "Doctor Cities"


class DoctorSpecialist(TimeStampedModel):
    """
    Represents a specialist category of a doctor.
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Doctor Specialist"
        verbose_name_plural = "Doctor Specialists"


class Insurance(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class DoctorUser(TimeStampedModel):
    """
    Represents a doctor user.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    medical_system_code = models.IntegerField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    cost_of_visit = models.PositiveBigIntegerField(default=10000, null=True, blank=True)
    city = models.ForeignKey(DoctorCity, on_delete=models.CASCADE, null=True, blank=True)
    sepecialist = models.ForeignKey(DoctorSpecialist, on_delete=models.CASCADE, null=True, blank=True)
    insurances = models.ManyToManyField(Insurance, blank=True)

    def __str__(self):
        return f"Doctor profile for {self.user.username}"

    class Meta:
        verbose_name = "Doctor User"
        verbose_name_plural = "Doctor Users"


class DoctorAddress(TimeStampedModel):
    """
    Represents the address details of a doctor.
    """

    doctor = models.OneToOneField(DoctorUser, on_delete=models.CASCADE, related_name="address")
    address = models.TextField(null=True, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"Address for {self.doctor.user.username}"

    class Meta:
        verbose_name = "Doctor Address"
        verbose_name_plural = "Doctor Addresses"


class Telephone(TimeStampedModel):
    """
    Represents a telephone number associated with a doctor.
    """

    doctor = models.ForeignKey(DoctorUser, on_delete=models.CASCADE, related_name="telephones")
    call_number = models.PositiveBigIntegerField(unique=True)

    def __str__(self):
        return f"Telephone {self.call_number} for {self.doctor.user.username}"

    class Meta:
        verbose_name = "Telephone"
        verbose_name_plural = "Telephones"


class WeekDays(TimeStampedModel):
    """
    Represents the availability of doctors on different days of the week.
    """

    choice_days = (
        ("شنبه", "شنبه"),
        ("یکشنبه", "یکشنبه"),
        ("دوشنبه", "دوشنبه"),
        ("سه شنبه", "سه شنبه"),
        ("چهارشنبه", "چهارشنبه"),
        ("پنجشنبه", "پنجشنبه"),
        ("جمعه", "جمعه"),
    )
    day = models.CharField(choices=choice_days, max_length=10)
    doctor = models.ForeignKey(DoctorUser, on_delete=models.CASCADE, related_name="week_days")

    def __str__(self):
        return f"{self.day} - {self.doctor.user.username}"

    class Meta:
        verbose_name = "Week Day"
        verbose_name_plural = "Week Days"


class ShiftTime(TimeStampedModel):
    """
    Represents the shift times of doctors.
    """

    week_day = models.ForeignKey(WeekDays, on_delete=models.CASCADE, related_name="shift_times")
    start_time = models.TimeField()
    end_time = models.TimeField()
    # capacity = models.PositiveIntegerField(default=1)
    # reserved_capacity = models.PositiveIntegerField(default=0)

    # @property
    # def free_capacity(self):
    #     return self.capacity - self.reserved_capacity

    def __str__(self):
        return f"{self.week_day.day}: {self.start_time} - {self.end_time}"

    class Meta:
        verbose_name = "Shift Time"
        verbose_name_plural = "Shift Times"


class DoctorImage(TimeStampedModel):
    image = models.ImageField()
    doctor = models.OneToOneField(DoctorUser, on_delete=models.CASCADE, related_name="image")
