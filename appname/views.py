import logging
import csv
from datetime import datetime

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Min, Max, Count
from django.utils.timezone import localtime, make_aware, get_current_timezone
from django.core.paginator import Paginator
from django.db import connection

from silk.profiling.profiler import silk_profile
from silk.models import Request, Profile

from .models import employee       
from .serializers import employe_serializer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# EMPLOYEE CRUD  (unchanged)
# ---------------------------------------------------------------------

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
            return Response({'message': 'Employee updated successfully',
                             'data': serializer.data})
        logger.error("Update failed for Employee")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Delete(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def delete(self, request, pk):
        try:
            item = employee.objects.get(pk=pk)
            item.delete()
            logger.info(f"Employee {pk} deleted successfully")
            return Response({'message': 'Employee deleted successfully'},
                            status=status.HTTP_204_NO_CONTENT)
        except employee.DoesNotExist:
            logger.error(f"Delete failed: Employee {pk} not found")
            raise Http404("Employee Not Found")

# ---------------------------------------------------------------------
# SILK-BASED DASHBOARD / CHART VIEWS  (unchanged)
# ---------------------------------------------------------------------

def silk_chart_data(request):
    try:
        total_requests = Request.objects.count()
        total_profiles = Profile.objects.count()
        total_response_time = sum(p.time_taken or 0 for p in Profile.objects.all())
        total_query_time = sum(sum(q.time_taken for q in p.queries.all())
                               for p in Profile.objects.all())
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


# -- Most DB queries
def most_db_queries_view(request):
    return render(request, 'silk/most_db_queries.html')


def most_queries_chart_api(request):
    data = [
        {'view_name': r.view_name, 'num_queries': r.num_sql_queries}
        for r in Request.objects.order_by('-num_sql_queries')
    ]
    return JsonResponse(data, safe=False)


# -- Slowest overall requests
def chart_most_time_overall_view(request):
    return render(request, 'silk/chart_most_time_overall.html')


def most_time_overall_data(request):
    data = [
        {'path': r.path, 'time_taken': round(r.time_taken, 2)}
        for r in Request.objects.order_by('-time_taken')[:10]
    ]
    return JsonResponse(data, safe=False)

# -- Aggregated profile / pagination
def user_profiles_view(request):
    date_str = request.GET.get('date')          # 'YYYY-MM-DD'
    page_number = request.GET.get('page', 1)
    tz = get_current_timezone()

    if date_str:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_date = make_aware(datetime.combine(selected_date, datetime.min.time()),
                                timezone=tz)
        end_date = make_aware(datetime.combine(selected_date, datetime.max.time()),
                              timezone=tz)
        user_profiles = Request.objects.filter(start_time__range=[start_date, end_date])
    else:
        user_profiles = Request.objects.all()

    aggregated_profiles = user_profiles.values('method').annotate(
        avg_time_taken=Avg('time_taken'),
        request_count=Count('id'),
        first_start_time=Min('start_time'),
        last_start_time=Max('start_time')
    )

    aggregated_profiles_list = [
        {
            'method': p['method'],
            'avg_time_taken': p['avg_time_taken'],
            'request_count': p['request_count'],
            'first_start_time': localtime(p['first_start_time'], tz)
                                .strftime('%Y-%m-%d %I:%M %p') if p['first_start_time'] else 'N/A',
            'last_start_time': localtime(p['last_start_time'], tz)
                               .strftime('%Y-%m-%d %I:%M %p') if p['last_start_time'] else 'N/A'
        }
        for p in aggregated_profiles
    ]

    paginator = Paginator(aggregated_profiles_list, 5)
    page_obj = paginator.get_page(page_number)

    return render(request, 'silk/appname_profiling.html', {
        'aggregated_profiles': page_obj,
        'selected_date': date_str,
    })


def overall_api_chart_data(request):
    data = (
        Request.objects.values("method")
        .annotate(request_count=Count("id"))
        .order_by("method")
    )
    return JsonResponse({entry["method"]: entry["request_count"] for entry in data})


def export_all_requests_csv(request):
    all_requests = Request.objects.all().order_by('method', 'start_time')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_api_requests.csv"'

    writer = csv.writer(response)
    writer.writerow(['Method', 'ID', 'Path', 'Time Taken (ms)', 'Start Time'])

    for r in all_requests:
        writer.writerow([
            r.method,
            r.id,
            r.path,
            round(r.time_taken or 0, 2),
            r.start_time.strftime('%Y-%m-%d %I:%M %p') if r.start_time else ''
        ])

    return response
