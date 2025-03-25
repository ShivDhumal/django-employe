import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.http import Http404, JsonResponse
from django.shortcuts import render
from .models import employee
from .serializers import employe_serializer
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from silk.profiling.profiler import silk_profile
from django.db.models import Avg, Sum
from silk.models import Request, Profile

logger = logging.getLogger(__name__)

class employe_list(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    @silk_profile(name="Employee List API")
    def get(self, request, pk=None):
        try:
            if pk:
                item = employee.objects.get(pk=pk)
                serializer = employe_serializer(item)
            else:
                item = employee.objects.all().order_by('id')
                serializer = employe_serializer(item, many=True)

            logger.info("Employee list accessed")
            return Response(serializer.data)
        except employee.DoesNotExist:
            logger.error("Employee not found")
            raise Http404("Employee Not Found")

class Create(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    @silk_profile(name="Employee post API")
    def post(self, request):
        serializer = employe_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("New employee created")
            return Response({'data': request.data})
        logger.warning(f"Failed employee creation: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Update(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    @silk_profile(name="Employee put API")
    def put(self, request, pk):
        try:
            item = employee.objects.get(pk=pk)
        except employee.DoesNotExist:
            logger.error("Employee not found")
            raise Http404("Employee Not Found")

        serializer = employe_serializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Employee updated successfully")
            return Response({'message': 'Employee updated successfully', 'data': serializer.data})
        logger.error("Update failed for Employee")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Delete(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def delete(self, request, pk):
        try:
            item = employee.objects.get(pk=pk)
            item.delete()
            logger.info(f"Employee {pk} deleted successfully")
            return Response({'message': 'Employee deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except employee.DoesNotExist:
            logger.error(f"Delete failed: Employee {pk} not found")
            raise Http404("Employee Not Found")

def silk_data(request):
    requests_count = Request.objects.count()
    profiles_count = Profile.objects.count()
    avg_response_time = Request.objects.aggregate(avg_time=Avg('time_taken'))['avg_time'] or 0  
    total_sql_queries = Request.objects.aggregate(total_queries=Sum('num_sql_queries'))['total_queries'] or 0
    total_db_time = Request.objects.aggregate(total_db_time=Sum('meta_time_spent_queries'))['total_db_time'] or 0
    avg_query_time = Request.objects.aggregate(avg_db_time=Avg('meta_time_spent_queries'))['avg_db_time'] or 0

    return JsonResponse({
        "requests": requests_count,
        "profiles": profiles_count,
        "avg_response_time": round(avg_response_time, 2),
        "avg_num_queries": round(total_sql_queries / requests_count, 2) if requests_count else 0,
        "avg_query_time": round(avg_query_time, 2)
    })  

def silk_chart_view(request):
    return render(request, 'silk/chart.html')
