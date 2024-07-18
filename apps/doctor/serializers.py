from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.doctor.models import DoctorAddress
from apps.doctor.models import DoctorCity
from apps.doctor.models import DoctorImage
from apps.doctor.models import DoctorSpecialist
from apps.doctor.models import DoctorUser
from apps.doctor.models import ShiftTime
from apps.doctor.models import Telephone
from apps.doctor.models import WeekDays
from apps.patient.models import Appointment

User = get_user_model()


class DoctorCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorCity
        fields = "__all__"


class DoctorAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAddress
        fields = "__all__"


class DoctorTelephoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telephone
        fields = "__all__"


class DoctorShiftTimeSerializer(serializers.ModelSerializer):
    # free_capacity = serializers.CharField()

    class Meta:
        model = ShiftTime
        fields = "__all__"


class DoctorWeekDaysSerializer(serializers.ModelSerializer):
    shift_times = DoctorShiftTimeSerializer(many=True)

    class Meta:
        model = WeekDays
        fields = "__all__"


class DoctorSpecialistSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSpecialist
        fields = "__all__"


class DoctorImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField("get_image_url")

    def get_image_url(self, obj):
        request = self.context.get("request")
        image_obj = obj.image
        if image_obj:
            return request.build_absolute_uri(image_obj.url)
        return ""

    class Meta:
        model = DoctorImage
        fields = ("image_url",)


class DoctorDetailSerializer(serializers.ModelSerializer):
    image = DoctorImageSerializer()
    full_name = serializers.CharField(source="user.full_name")
    city = DoctorCitySerializer()
    address = DoctorAddressSerializer()
    telephones = DoctorTelephoneSerializer(many=True)
    week_days = DoctorWeekDaysSerializer(many=True)
    specialist = DoctorSpecialistSerializer()

    class Meta:
        model = DoctorUser
        fields = "__all__"


class DoctorListSerializer(serializers.ModelSerializer):
    city = DoctorCitySerializer()
    specialist = DoctorSpecialistSerializer()
    image = DoctorImageSerializer()
    full_name = serializers.CharField(source="user.full_name")

    class Meta:
        model = DoctorUser
        fields = (
            "id",
            "full_name",
            "city",
            "specialist",
            "image",
        )


class AppointmentReportSerializer(serializers.ModelSerializer):
    patient_national_code = serializers.CharField(source="patient.user.national_code", read_only=True)
    patient_full_name = serializers.CharField(source="patient.user.full_name", read_only=True)
    patient_phone_number = serializers.CharField(source="patient.user.phone_number", read_only=True)
    appointment_date = serializers.DateField(source="date", read_only=True)
    appointment_start_time = serializers.TimeField(source="shift_time.start_time", read_only=True)
    appointment_end_time = serializers.TimeField(source="shift_time.end_time", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient_national_code",
            "patient_full_name",
            "patient_phone_number",
            "appointment_date",
            "appointment_start_time",
            "appointment_end_time",
            "status",
            "paid",
        ]


class DoctorUserUpdateSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)
    email = serializers.EmailField(write_only=True, required=False)
    medical_system_code = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "national_code",
            "old_password",
            "new_password",
            "address",
            "medical_system_code",
        ]

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
        address_data = validated_data.pop("address", None)
        if address_data:
            address_instance, _ = DoctorAddress.objects.get_or_create(doctor__user=instance)
            address_instance.address = address_data
            address_instance.save()

        if "old_password" in validated_data and "new_password" in validated_data:
            instance.set_password(validated_data["new_password"])

        if "medical_system_code" in validated_data:
            dr_obj = DoctorUser.objects.get(user=instance)
            dr_obj.medical_system_code = validated_data["medical_system_code"]
            dr_obj.save()

        for attr, value in validated_data.items():
            if attr not in ["old_password", "new_password", "address", "city_id", "medical_system_code"]:
                setattr(instance, attr, value)

        instance.save()
        return instance


class UpdateShiftTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftTime
        fields = (
            "id",
            "start_time",
            "end_time",
        )


class UpdateWeekDaysSerializer(serializers.ModelSerializer):
    shift_times = UpdateShiftTimeSerializer(many=True, required=False)

    class Meta:
        model = WeekDays
        fields = ("id", "day", "shift_times")

    def update(self, instance, validated_data):
        shift_times_data = validated_data.pop("shift_times", [])

        # Update WeekDays fields
        instance.day = validated_data.get("day", instance.day)
        instance.save()

        # Update or create ShiftTime instances
        for shift_time_data in shift_times_data:
            shift_time_id = shift_time_data.get("id", None)
            if shift_time_id:
                shift_time_instance = ShiftTime.objects.get(id=shift_time_id, week_day=instance)
                shift_time_instance.start_time = shift_time_data.get("start_time", shift_time_instance.start_time)
                shift_time_instance.end_time = shift_time_data.get("end_time", shift_time_instance.end_time)
                # shift_time_instance.capacity = shift_time_data.get('capacity', shift_time_instance.capacity)
                shift_time_instance.save()
            else:
                ShiftTime.objects.create(
                    week_day=instance,
                    start_time=shift_time_data["start_time"],
                    end_time=shift_time_data["end_time"],
                    # capacity=shift_time_data['capacity'],
                )

        return instance
