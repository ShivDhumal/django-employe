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
from django.shortcuts import render

from django.http import JsonResponse
from silk.models import Request
from django.db.models import Avg
from datetime import datetime, timedelta
   
from django.shortcuts import render
from django.db.models import Avg, Min, Max, Count
from silk.models import Request  # Ensure correct import






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





def silk_chart_data(request):
    try:
        total_requests = Request.objects.count()
        total_profiles = Profile.objects.count()
        total_response_time = sum(p.time_taken or 0 for p in Profile.objects.all())
        total_query_time = sum(sum(q.time_taken for q in p.queries.all()) for p in Profile.objects.all())
        total_query_count = sum(p.queries.count() for p in Profile.objects.all())

        avg_response_time = total_response_time / total_profiles if total_profiles else 0
        avg_query_time = total_query_time / total_profiles if total_profiles else 0
        avg_num_queries = total_query_count / total_profiles if total_profiles else 0

        data = {
            'requests': total_requests,
            'profiles': total_profiles,
            'avg_response_time': round(avg_response_time * 1000, 2),
            'avg_query_time': round(avg_query_time * 1000, 2),
            'avg_num_queries': round(avg_num_queries, 2)
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
        
def silk_chart_view(request):
    return render(request, 'silk/chart.html')

#for most_db_queries.html

def most_db_queries_view(request):
    return render(request, 'silk/most_db_queries.html')
def most_queries_chart_api(request):
    data = [{'view_name': r.view_name, 'num_queries': r.num_sql_queries} for r in Request.objects.order_by('-num_sql_queries')]
    return JsonResponse(data, safe=False)  # ✅ Corrected syntax



#for chart_most_time_overall.html
def chart_most_time_overall_view(request):
    return render(request, 'silk/chart_most_time_overall.html')

def most_time_overall_data(request):
    data = [{'path': r.path, 'time_taken': round(r.time_taken, 2)} for r in Request.objects.order_by('-time_taken')[:10]]
    return JsonResponse(data,safe=False)


    

def user_profiles_view(request):
    # Get the date from request parameters (if provided)
    date_str = request.GET.get('date')  # Format: 'YYYY-MM-DD'
    
    if date_str:
        from datetime import datetime
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_date = datetime.combine(selected_date, datetime.min.time())  # 00:00:00
        end_date = datetime.combine(selected_date, datetime.max.time())  # 23:59:59
        
        # Filter requests by selected date
        user_profiles = Request.objects.filter(start_time__range=[start_date, end_date])
    else:
        # If no date is provided, fetch all records
        user_profiles = Request.objects.all()

    # Aggregate data by HTTP method
    aggregated_profiles = user_profiles.values('method').annotate(
        avg_time_taken=Avg('time_taken'),
        min_time_taken=Min('time_taken'),
        max_time_taken=Max('time_taken'),
        request_count=Count('id'),  # Count of API calls per method
        first_start_time=Min('start_time'),  # Earliest request time
        last_start_time=Max('start_time')   # Latest request time
    )

    # Convert the QuerySet to a list of dictionaries
    aggregated_profiles_list = list(aggregated_profiles)

    context = {
        'aggregated_profiles': aggregated_profiles_list,
        'selected_date': date_str,  # Pass selected date to template
    }

    return render(request, 'silk/appname_profiling.html', context)



