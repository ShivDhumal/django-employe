import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.http import Http404
from .models import Student
from .serializer import StudentSerializer
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from silk.profiling.profiler import silk_profile



logger = logging.getLogger(__name__)

class StudentList(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    @silk_profile(name="Student List API")
    def get(self, request, pk=None):
        try:
            if pk:
                item = Student.objects.get(pk=pk)
                serializer = StudentSerializer(item)
            else:
                item = Student.objects.all().order_by('id')
                serializer = StudentSerializer(item, many=True)

            logger.info("Student list accessed")
            return Response(serializer.data)
        except Student.DoesNotExist:
            logger.error("Student not found")
            raise Http404("Student Not Found")

class CreateStudent(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    @silk_profile(name="Student Create API")
    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("New student created")
            return Response({'data': request.data})
        logger.warning(f"Failed student creation: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateStudent(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    @silk_profile(name="Student Update API")
    def put(self, request, pk):
        try:
            item = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            logger.error("Student not found")
            raise Http404("Student Not Found")

        serializer = StudentSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Student updated successfully")
            return Response({'message': 'Student updated successfully', 'data': serializer.data})
        logger.error("Update failed for Student")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteStudent(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def delete(self, request, pk):
        try:
            item = Student.objects.get(pk=pk)
            item.delete()
            logger.info(f"Student {pk} deleted successfully")
            return Response({'message': 'Student deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Student.DoesNotExist:
            logger.error(f"Delete failed: Student {pk} not found")
            raise Http404("Student Not Found")
