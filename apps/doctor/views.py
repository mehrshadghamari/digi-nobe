import math

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.doctor.models import DoctorUser
from apps.doctor.serializers import DoctorDetailSerializer
from apps.doctor.serializers import DoctorListSerializer


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


class DocotorList(APIView):
    def get(self, request):
        page_number = self.request.query_params.get("page", 1)
        # page_size = 20
        page_size = self.request.query_params.get("page_size", 20)

        query = DoctorUser.objects.all()
        paginator = Paginator(query, page_size)
        serializer = DoctorListSerializer(paginator.page(page_number), many=True, context={"request": request})
        page_count = math.ceil(query.count() / int(page_size))
        return Response(
            {
                "current_page": int(page_number),
                "page_count": page_count,
                "docotrs": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
