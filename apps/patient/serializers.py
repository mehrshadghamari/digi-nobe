from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Appointment
from .models import PatientUser

User = get_user_model()
from .models import DoctorUser
from .models import PatientUser
from .models import ShiftTime


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["doctor", "shift_time", "date", "status", "paid"]
        read_only_fields = ["status", "paid"]

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        patient_user = PatientUser.objects.get(user_id=user.id)
        doctor = get_object_or_404(DoctorUser, pk=validated_data["doctor"])
        shift_time = get_object_or_404(ShiftTime, pk=validated_data["shift_time"])
        # validated_data['patient'] = user.patientuser
        obj = Appointment.objects.create(
            patient=patient_user,
            doctor=doctor,
            shift_time=shift_time,
            date=validated_data["date"],
        )
        return obj


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_id = serializers.IntegerField(source="doctor.id", read_only=True)
    doctor_name = serializers.CharField(source="doctor.user.full_name", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    appointment_date = serializers.DateField(source="date", read_only=True)
    appointment_start_time = serializers.TimeField(source="shift_time.start_time", read_only=True)
    appointment_end_time = serializers.TimeField(source="shift_time.end_time", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctor_id",
            "doctor_name",
            "created_at",
            "appointment_date",
            "appointment_start_time",
            "appointment_end_time",
            "status",
            "paid",
        ]


class PatientUserUpdateSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["phone_number", "first_name", "last_name", "national_code", "old_password", "new_password"]

    def validate(self, data):
        user = self.instance

        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if old_password and not new_password:
            raise serializers.ValidationError(
                {"new_password": "New password is required when old password is provided."}
            )

        if new_password and not old_password:
            raise serializers.ValidationError({"old_password": "Old password is required when changing the password."})

        if old_password and new_password and not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})

        return data

    def update(self, instance, validated_data):
        if "old_password" in validated_data and "new_password" in validated_data:
            instance.set_password(validated_data["new_password"])

        for attr, value in validated_data.items():
            if attr not in ["old_password", "new_password"]:
                setattr(instance, attr, value)

        instance.save()
        return instance
