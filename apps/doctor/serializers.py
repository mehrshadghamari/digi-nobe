from rest_framework import serializers

from apps.doctor.models import DoctorAddress
from apps.doctor.models import DoctorCity
from apps.doctor.models import DoctorImage
from apps.doctor.models import DoctorSpecialist
from apps.doctor.models import DoctorUser
from apps.doctor.models import ShiftTime
from apps.doctor.models import Telephone
from apps.doctor.models import WeekDays


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
    free_capacity = serializers.CharField()

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
    image = serializers.SerializerMethodField("get_image_url")

    def get_image_url(self, obj):
        request = self.context.get("request")
        image_url = obj.image.url
        return request.build_absolute_uri(image_url)

    class Meta:
        model = DoctorImage
        fields = "__all__"


class DoctorDetailSerializer(serializers.ModelSerializer):
    image = DoctorImageSerializer()
    city = DoctorCitySerializer()
    address = DoctorAddressSerializer()
    telephones = DoctorTelephoneSerializer(many=True)
    week_days = DoctorWeekDaysSerializer(many=True)
    sepecialist = DoctorSpecialistSerializer()

    class Meta:
        model = DoctorUser
        fields = "__all__"


class DoctorListSerializer(serializers.ModelSerializer):
    city = DoctorCitySerializer()
    sepecialist = DoctorSpecialistSerializer()
    image = DoctorImageSerializer()

    class Meta:
        model = DoctorUser
        fields = (
            "id",
            "city",
            "sepecialist",
            "image",
        )
