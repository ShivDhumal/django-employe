import logging
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from silk.profiling.profiler import silk_profile
from .models import Student
from .serializers import StudentSerializer
from silk.models import Request
from django.shortcuts import render
from django.db.models import Avg
from django.shortcuts import render
from django.db.models import Avg, Min, Max, Count
from datetime import datetime
from silk.models import Request  # Ensure this is the correct import for your Silk Request model

logger = logging.getLogger(__name__)

class StudentList(APIView):
    # throttle_classes = [AnonRateThrottle, UserRateThrottle]

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
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

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
#for deletion
class StudentDelete(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

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
    # Get the date from request parameters (if provided)
    date_str = request.GET.get('date')  # Format: 'YYYY-MM-DD'
    
    # Convert date string to a date object
    if date_str:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_date = datetime.combine(selected_date, datetime.min.time())  # 00:00:00
        end_date = datetime.combine(selected_date, datetime.max.time())  # 23:59:59
        
        # Filter requests by selected date and path for 'myapp'
        user_profiles = Request.objects.filter(
            path__startswith="/myapp/",
            start_time__range=[start_date, end_date]
        )
    else:
        # If no date is provided, fetch all records for 'myapp'
        user_profiles = Request.objects.filter(path__startswith="/myapp/")

    # Aggregate by method and calculate various statistics
    aggregated_profiles = user_profiles.values('method').annotate(
        avg_time_taken=Avg('time_taken'),
        request_count=Count('id'),
        first_start_time=Min('start_time'),
        last_start_time=Max('start_time')
    )

    # Convert QuerySet to a list of dictionaries (serializable)
    aggregated_profiles_list = list(aggregated_profiles)

    context = {
        'aggregated_profiles': aggregated_profiles_list,
        'selected_date': date_str,  # Pass the selected date to the template
    }

    return render(request, 'silk/myapp_profiling.html', context)


from django.shortcuts import render


