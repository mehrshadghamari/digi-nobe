from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.doctor.models import DoctorUser
from apps.patient.models import PatientUser

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["phone_number", "password","first_name","last_name" ,"email", "national_code"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class PatientUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = PatientUser
        fields = ["user"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        patient = PatientUser.objects.create(user=user)
        return patient


class DoctorUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    medical_system_code = serializers.IntegerField()

    class Meta:
        model = DoctorUser
        fields = ["user", "medical_system_code"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        doctor = DoctorUser.objects.create(user=user, **validated_data)
        return doctor
