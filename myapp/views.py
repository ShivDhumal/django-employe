import logging
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.db.models import Avg, Min, Max, Count
from datetime import datetime
from silk.models import Request  # Ensure this is the correct import for Silk Request model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from silk.profiling.profiler import silk_profile
from .models import Student
from .serializers import StudentSerializer

logger = logging.getLogger(__name__)

class StudentList(APIView):
    @silk_profile(name="Student List API")
    def get(self, request, pk=None):
        try:
            if pk:
                student = Student.objects.get(pk=pk)
                serializer = StudentSerializer(student)
            else:
                students = Student.objects.all().order_by('id')
                serializer = StudentSerializer(students, many=True)

            logger.info("Student list accessed")
            return Response(serializer.data)
        except Student.DoesNotExist:
            logger.error("Student not found")
            raise Http404("Student Not Found")

class StudentCreate(APIView):
    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Student added successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentUpdate(APIView):
    @silk_profile(name="Student Put API")
    def put(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            logger.error("Student not found")
            raise Http404("Student Not Found")

        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Student updated successfully")
            return Response({'message': 'Student updated successfully', 'data': serializer.data})
        logger.error("Update failed for Student")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentDelete(APIView):
    def delete(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
            student.delete()
            logger.info(f"Student {pk} deleted successfully")
            return Response({'message': 'Student deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Student.DoesNotExist:
            logger.error(f"Delete failed: Student {pk} not found")
            raise Http404("Student Not Found")

def demo_profiles_view(request):
    date_str = request.GET.get('date')

    if date_str:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_date = datetime.combine(selected_date, datetime.min.time())
        end_date = datetime.combine(selected_date, datetime.max.time())

        user_profiles = Request.objects.filter(
            path__startswith="/myapp/",
            start_time__range=[start_date, end_date]
        )
    else:
        user_profiles = Request.objects.filter(path__startswith="/myapp/")

    aggregated_profiles = user_profiles.values('method').annotate(
        avg_time_taken=Avg('time_taken'),
        request_count=Count('id'),
        first_start_time=Min('start_time'),
        last_start_time=Max('start_time')
    )

    # Format date-time in AM/PM format
    aggregated_profiles_list = [
        {
            "method": profile["method"],
            "avg_time_taken": profile["avg_time_taken"],
            "request_count": profile["request_count"],
            "first_start_time": profile["first_start_time"].strftime("%Y-%m-%d %I:%M %p") if profile["first_start_time"] else "N/A",
            "last_start_time": profile["last_start_time"].strftime("%Y-%m-%d %I:%M %p") if profile["last_start_time"] else "N/A",
        }
        for profile in aggregated_profiles
    ]

    context = {
        'aggregated_profiles': aggregated_profiles_list,
        'selected_date': date_str,
    }

    return render(request, 'silk/myapp_profiling.html', context)

def overall_api_chart_data2(request):
    data = (
        Request.objects.filter(path__startswith="/myapp/")
        .values("method")
        .annotate(request_count=Count("id"))
        .order_by("method")
    )
    chart_data = {entry["method"]: entry["request_count"] for entry in data}
    return JsonResponse(chart_data)
