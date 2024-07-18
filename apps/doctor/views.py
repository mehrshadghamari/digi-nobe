import math

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.doctor.models import DoctorUser
from apps.doctor.models import ShiftTime
from apps.doctor.models import WeekDays
from apps.doctor.serializers import AppointmentReportSerializer
from apps.doctor.serializers import DoctorDetailSerializer
from apps.doctor.serializers import DoctorListSerializer
from apps.doctor.serializers import DoctorUserUpdateSerializer
from apps.doctor.serializers import UpdateWeekDaysSerializer
from apps.patient.models import Appointment


@extend_schema(
    description="Retrieve details of a specific doctor", responses={200: DoctorDetailSerializer, 404: "Not Found"}
)
class DoctorDetail(APIView):
    def get(self, request, doctor_id):
        doctor_obj = get_object_or_404(
            DoctorUser.objects.select_related("city", "address").prefetch_related(
                "telephones", "week_days__shift_times"
            ),
            id=doctor_id,
        )

        serializer = DoctorDetailSerializer(doctor_obj, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    description="Retrieve a paginated list of doctors with optional filtering by city and specialist.",
    parameters=[
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Page number for pagination (default: 1).",
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of items per page (default: 20).",
        ),
        OpenApiParameter(
            name="city",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter doctors by city ID.",
        ),
        OpenApiParameter(
            name="specialist",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter doctors by specialist ID.",
        ),
    ],
    responses={200: {"doctors": DoctorListSerializer}},
)
class DoctorList(APIView):
    def get(self, request):
        page_number = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 20)
        city_id = request.query_params.get("city")
        specialist_id = request.query_params.get("specialist")

        query = DoctorUser.objects.all().select_related("city", "specialist", "image")

        if city_id:
            query = query.filter(city_id=city_id)
        if specialist_id:
            query = query.filter(specialist_id=specialist_id)

        paginator = Paginator(query, page_size)
        serializer = DoctorListSerializer(paginator.page(page_number), many=True, context={"request": request})
        page_count = math.ceil(query.count() / int(page_size))

        return Response(
            {
                "current_page": int(page_number),
                "page_count": page_count,
                "doctors": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    description="Retrieve a list of 15 random doctors for the home page.", responses={200: DoctorListSerializer}
)
class HomePageDocotorList(APIView):
    def get(self, request):

        query = DoctorUser.objects.all().select_related("city", "specialist", "image").order_by("?")[:15]
        serializer = DoctorListSerializer(query, many=True, context={"request": request})
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    description="Search for doctors based on a query parameter.",
    parameters=[
        OpenApiParameter(
            name="q",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search query string. Searches in doctor's first name, last name, or specialist name.",
        )
    ],
    responses={200: DoctorListSerializer},
)
class DoctorSearch(APIView):
    def get(self, request):
        search_query = request.query_params.get("q", "")
        if not search_query:
            return Response({"message": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        doctors = DoctorUser.objects.select_related("city", "specialist", "image").filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(specialist__name__icontains=search_query)
        )

        serializer = DoctorListSerializer(doctors,many=True,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    description="Retrieve appointment reports for a specific doctor within a date range.",
    parameters=[
        OpenApiParameter(
            name="start_date",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Start date of the appointment range. Format: YYYY-MM-DD. Defaults to current date.",
        ),
        OpenApiParameter(
            name="end_date",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="End date of the appointment range. Format: YYYY-MM-DD. Defaults to start_date.",
        ),
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter appointments by status. Options: pending, confirmed, completed, cancelled.",
        ),
    ],
    responses={200: AppointmentReportSerializer},
)
class AppointmentReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Check if the user is a doctor
        try:
            doctor = DoctorUser.objects.get(user=user)
        except DoctorUser.DoesNotExist:
            return Response(
                {"message": "You are not authorized to access this resource"}, status=status.HTTP_403_FORBIDDEN
            )

        # Get query parameters
        start_date = request.query_params.get("start_date", timezone.now().date())
        end_date = request.query_params.get("end_date", start_date)
        status_filter = request.query_params.get("status", None)

        # Filter appointments for the specific doctor within the date range
        appointments = Appointment.objects.filter(doctor=doctor, date__range=[start_date, end_date]).select_related(
            "patient__user", "shift_time"
        )

        if status_filter:
            appointments = appointments.filter(status=status_filter)

        serializer = AppointmentReportSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    description="Update doctor details",
    request=DoctorUserUpdateSerializer,
    responses={200: None},  # Specify response schema if needed
)
class DoctorUserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        # Check if the user is a doctor
        try:
            DoctorUser.objects.get(user=user)
        except DoctorUser.DoesNotExist:
            return Response(
                {"message": "You are not authorized to access this resource"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = DoctorUserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Doctor details updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description="Update doctor availability (weekdays and shift times)",
    request=UpdateWeekDaysSerializer,
    responses={200: None},  # Specify response schema if needed
)
class DoctorAvailabilityUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Assuming the logged-in user is the doctor whose availability is being updated
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            doctor = DoctorUser.objects.get(user=user)
        except DoctorUser.DoesNotExist:
            return Response(
                {"message": "You are not authorized to access this resource"}, status=status.HTTP_403_FORBIDDEN
            )

        week_days_instances = WeekDays.objects.filter(doctor=doctor)
        serializer = UpdateWeekDaysSerializer(week_days_instances, data=request.data, many=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Doctor availability updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
