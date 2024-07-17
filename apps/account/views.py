from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import OpenApiTypes
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.account.models import User

# Rename duplicate serializers
from apps.account.serializers import DoctorAddressSerializer as AccountDoctorAddressSerializer
from apps.doctor.models import DoctorCity
from apps.doctor.models import DoctorSpecialist
from apps.doctor.models import DoctorUser
from apps.doctor.models import Insurance
from apps.doctor.serializers import DoctorAddressSerializer as DoctorDoctorAddressSerializer
from apps.patient.models import PatientUser

from .serializers import DoctorSpecialistSerializer
from .serializers import DoctorUserSerializer
from .serializers import InsuranceSerializer
from .serializers import PatientUserSerializer
from .serializers import getDoctorCitySerializer


# Define response serializers
class TokenResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class ErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()


class ForbiddenSerializer(serializers.Serializer):
    detail = serializers.CharField()


class SignupResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class DoctorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorUser
        fields = "__all__"

    @extend_schema_field(OpenApiTypes.STR)
    def get_image_url(self, obj):
        # Implementation of get_image_url
        return "image_url"


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Customizing JWT token claims
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["phone_number"] = user.phone_number
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


def get_tokens_for_user(user):
    refresh = MyTokenObtainPairSerializer.get_token(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@extend_schema(
    request=MyTokenObtainPairSerializer,
    responses={
        200: TokenResponseSerializer,
        400: ErrorSerializer,
        403: ForbiddenSerializer,
    },
)
class DoctorLogin(APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")

        if not phone_number or not password:
            return Response({"message": "شماره تلفن و رمز عبور الزامی است"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"message": "شماره تلفن وارد شده معتبر نمیباشد"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({"message": "رمز عبور وارد شده صحیح نمیباشد"}, status=status.HTTP_400_BAD_REQUEST)

        # Check user role
        if not DoctorUser.objects.filter(user=user).exists():
            return Response({"message": "کاربر مورد نظر دکتر نمیباشد"}, status=status.HTTP_403_FORBIDDEN)

        token = get_tokens_for_user(user)
        return Response(token, status=status.HTTP_200_OK)


@extend_schema(
    request=MyTokenObtainPairSerializer,
    responses={
        200: TokenResponseSerializer,
        400: ErrorSerializer,
        403: ForbiddenSerializer,
    },
)
class PatientLogin(APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")

        if not phone_number or not password:
            return Response({"message": "شماره تلفن و رمز عبور الزامی است"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"message": "شماره تلفن وارد شده معتبر نمیباشد"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({"message": "رمز عبور وارد شده صحیح نمیباشد"}, status=status.HTTP_400_BAD_REQUEST)

        # Check user role
        if not PatientUser.objects.filter(user=user).exists():
            return Response({"message": "کاربر مورد نظر بیمار نمیباشد"}, status=status.HTTP_403_FORBIDDEN)

        token = get_tokens_for_user(user)
        return Response(token, status=status.HTTP_200_OK)


@extend_schema(
    request=PatientUserSerializer,
    responses={
        201: SignupResponseSerializer,
        400: ErrorSerializer,
    },
)
class PatientSignup(APIView):
    def post(self, request):
        serializer = PatientUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "ثبت نام با موفقیت انجام شد"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=DoctorUserSerializer,
    responses={
        201: SignupResponseSerializer,
        400: ErrorSerializer,
    },
)
class DoctorSignup(APIView):
    """
    View to handle doctor signup.
    """

    def post(self, request):
        serializer = DoctorUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "ثبت نام دکتر با موفقیت انجام شد"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={200: DoctorSpecialistSerializer(many=True)},
)
class DoctorSpecialistList(APIView):
    def get(self, request):
        specialists = DoctorSpecialist.objects.all()
        serializer = DoctorSpecialistSerializer(specialists, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: InsuranceSerializer(many=True)},
)
class InsuranceList(APIView):
    def get(self, request):
        insurances = Insurance.objects.all()
        serializer = InsuranceSerializer(insurances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: getDoctorCitySerializer(many=True)},
)
class DoctorCityList(APIView):
    def get(self, request):
        doctor_cities = DoctorCity.objects.all()
        serializer = getDoctorCitySerializer(doctor_cities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
