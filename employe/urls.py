from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from appname.views import (
    user_profiles_view,
    overall_api_chart_data,
    export_all_requests_csv)
from myapp.views import demo_profiles_view, overall_api_chart_data2

urlpatterns = [
    # Your app URLs
    path('', include('appname.urls')),
    path('myapp/', include('myapp.urls')),  # myapp routes

    # Silk profiling URLs
    path('silk/', include('silk.urls', namespace='silk')),
    path('silk/user_prof/', user_profiles_view, name='user_profiling'),
    path('silk/demo_prof/', demo_profiles_view, name='demo_profiles'),

    # API URLs
    path('api/overall-chart/', overall_api_chart_data, name='overall_api_chart_data'),
    path('api/overall-chart2/', overall_api_chart_data2, name='overall_api_chart_data2'),

    # Export CSV
    path('export/all/', export_all_requests_csv, name='export_all_requests_csv'),

    # Admin
    path('admin/', admin.site.urls),
]
