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
    # Fetch the profiling data for 'demo'
    user_profiles = Request.objects.filter(path__startswith="/")

    # Aggregate by method and calculate the average time taken for each method
    aggregated_profiles = user_profiles.values('method').annotate(
        avg_time_taken=Avg('time_taken')
    )

    # Convert the QuerySet to a list of dictionaries (serializable)
    aggregated_profiles_list = list(aggregated_profiles)

    context = {
        'aggregated_profiles': aggregated_profiles_list,
    }
    return render(request,'silk/myapp_profiling.html',context)
