from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.doctor.models import DoctorAddress
from apps.doctor.models import DoctorCity
from apps.doctor.models import DoctorImage
from apps.doctor.models import DoctorSpecialist
from apps.doctor.models import DoctorUser
from apps.doctor.models import Insurance
from apps.doctor.models import ShiftTime
from apps.doctor.models import Telephone
from apps.doctor.models import WeekDays
from apps.patient.models import PatientUser

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["phone_number", "password", "first_name", "last_name", "national_code"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class PatientUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = PatientUser
        fields = [
            "user",
        ]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        patient = PatientUser.objects.create(user=user)
        return patient


class DoctorCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorCity
        fields = "__all__"


class ShiftTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftTime
        fields = [
            "start_time",
            "end_time",
        ]


class WeekDaysSerializer(serializers.ModelSerializer):
    shift_times = ShiftTimeSerializer(many=True)

    class Meta:
        model = WeekDays
        fields = ["day", "shift_times"]

    def create(self, validated_data):
        shift_times_data = validated_data.pop("shift_times")
        week_day = WeekDays.objects.create(**validated_data)
        for shift_time_data in shift_times_data:
            ShiftTime.objects.create(week_day=week_day, **shift_time_data)
        return week_day


class DoctorAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAddress
        fields = ["address", "lat", "lng"]


class TelephoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telephone
        fields = [
            "call_number",
        ]


class DoctorImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorImage
        fields = [
            "image",
        ]


class DoctorUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    address = DoctorAddressSerializer()
    telephones = TelephoneSerializer(many=True)
    insurances = serializers.PrimaryKeyRelatedField(queryset=Insurance.objects.all(), many=True)
    city = serializers.PrimaryKeyRelatedField(queryset=DoctorCity.objects.all())
    specialist = serializers.PrimaryKeyRelatedField(queryset=DoctorSpecialist.objects.all())
    workdays = WeekDaysSerializer(many=True)
    image = DoctorImageSerializer()

    class Meta:
        model = DoctorUser
        fields = [
            "user",
            "medical_system_code",
            "bio",
            "cost_of_visit",
            "city",
            "specialist",
            "address",
            "telephones",
            "insurances",
            "workdays",
            "image",
        ]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        address_data = validated_data.pop("address")
        telephones_data = validated_data.pop("telephones")
        insurances_data = validated_data.pop("insurances")
        workdays_data = validated_data.pop("workdays")
        image_data = validated_data.pop("image")

        user = UserSerializer.create(UserSerializer(), validated_data=user_data)

        doctor_user = DoctorUser.objects.create(user=user, **validated_data)

        DoctorAddress.objects.create(doctor=doctor_user, **address_data)

        for telephone_data in telephones_data:
            Telephone.objects.create(doctor=doctor_user, **telephone_data)

        doctor_user.insurances.set(insurances_data)

        for workday_data in workdays_data:
            shift_times_data = workday_data.pop("shift_times")
            workday = WeekDays.objects.create(doctor=doctor_user, **workday_data)
            for shift_time_data in shift_times_data:
                ShiftTime.objects.create(week_day=workday, **shift_time_data)

        DoctorImage.objects.create(doctor=doctor_user, **image_data)

        return doctor_user


class DoctorSpecialistSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSpecialist
        fields = ["id", "name"]


class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = ["id", "name"]


class getDoctorCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorCity
        fields = "__all__"


# class DoctorUserSerializer(serializers.ModelSerializer):
#     user = UserSerializer()
#     medical_system_code = serializers.IntegerField()

#     class Meta:
#         model = DoctorUser
#         fields = ["user", "medical_system_code"]

#     def create(self, validated_data):
#         user_data = validated_data.pop("user")
#         user = UserSerializer.create(UserSerializer(), validated_data=user_data)
#         doctor = DoctorUser.objects.create(user=user, **validated_data)
#         return doctor
