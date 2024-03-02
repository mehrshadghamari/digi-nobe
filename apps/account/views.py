from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.account.models import User
from apps.doctor.models import DoctorUser
from apps.patient.models import PatientUser

from .serializers import DoctorUserSerializer
from .serializers import PatientUserSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Customizing JWt token claims
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


class DoctorLogin(APIView):
    def post(self, request, role):
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


class PatientLogin(APIView):
    def post(self, request, role):
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


class PatientSignup(APIView):
    def post(self, request):
        serializer = PatientUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Patient registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorSignup(APIView):
    def post(self, request):
        serializer = DoctorUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Doctor registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
