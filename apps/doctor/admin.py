from django.contrib import admin

from apps.doctor.models import DoctorAddress
from apps.doctor.models import DoctorCity
from apps.doctor.models import DoctorImage
from apps.doctor.models import DoctorUser
from apps.doctor.models import ShiftTime
from apps.doctor.models import Telephone
from apps.doctor.models import WeekDays

admin.site.register(DoctorAddress)
admin.site.register(DoctorCity)
admin.site.register(DoctorUser)
admin.site.register(ShiftTime)
admin.site.register(Telephone)
admin.site.register(WeekDays)
admin.site.register(DoctorImage)
