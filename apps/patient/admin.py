from django.contrib import admin

from apps.patient.models import PatientUser,Appointment

admin.site.register(PatientUser)
admin.site.register(Appointment)
