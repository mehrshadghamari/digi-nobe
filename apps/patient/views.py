from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Appointment
from .models import DoctorUser
from .models import PatientUser
from .models import ShiftTime
from .serializers import AppointmentCreateSerializer
from .serializers import AppointmentSerializer
from .serializers import PatientUserUpdateSerializer


class AppointmentRequest(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Create a new appointment request for a patient.",
        request=AppointmentCreateSerializer,
        # responses={
        #     201: {"message": "Appointment created successfully. Returns appointment ID.", "appointment_id": int}
        # },
    )
    def post(self, request):
        serializer = AppointmentCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            doctor = get_object_or_404(DoctorUser, pk=serializer.validated_data["doctor"].id)
            shift_time = get_object_or_404(ShiftTime, pk=serializer.validated_data["shift_time"].id)

            # You might want to add more business logic here, e.g., checking if the shift time is available

            appointment = serializer.save()
            return Response(
                {"message": "Appointment created successfully", "appointment_id": appointment.id},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentHistory(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Retrieve appointment history for the authenticated patient user.",
        parameters=[
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=f"Filter by appointment status. Choices are: {dict(Appointment.STATUS_CHOICES).keys()}",
                enum=list(dict(Appointment.STATUS_CHOICES).keys()),  # Provide the list of enum values
            ),
        ],
        responses={200: AppointmentSerializer},
    )
    def get(self, request):
        user = request.user
        try:
            patient = PatientUser.objects.get(user_id=user.id)
        except PatientUser.DoesNotExist:
            return Response(
                {"message": "You are not authorized to access this resource"}, status=status.HTTP_403_FORBIDDEN
            )

        status_filter = request.query_params.get("status")

        query = Appointment.objects.all().select_related("doctor", "shift_time")

        if status_filter:
            appointments = query.filter(patient=patient, status=status_filter)
        else:
            appointments = query.objects.filter(patient=patient)

        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PatientUserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @extend_schema(
        description="Update patient user information (phone number, first name, last name, national code, password).",
        request=PatientUserUpdateSerializer,
        responses={200: {"message": "User updated successfully"}},
    )
    def put(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            patient = PatientUser.objects.get(user_id=user.id)
        except PatientUser.DoesNotExist:
            return Response(
                {"message": "You are not authorized to access this resource"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = PatientUserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
