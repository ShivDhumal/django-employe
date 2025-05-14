from django.contrib import admin
from django.urls import path, include
from appname.views import user_profiles_view
from myapp.views import demo_profiles_view
from django.urls import path
from appname.views import overall_api_chart_data
from myapp.views import overall_api_chart_data2
from appname.views import export_all_requests_csv
from django.conf import settings


# Include Debug Toolbar URLs when in DEBUG mode
if settings.DEBUG:
    import debug_toolbar

urlpatterns = [
    # Django Debug Toolbar URL
    path('__debug__/', include(debug_toolbar.urls)),

    # Your other URLs
    path('', include('appname.urls')),
    path('silk/', include('silk.urls', namespace='silk')),  # Silk dashboard
    path('silk/user_prof/', user_profiles_view, name='user_profiling'),
    path('silk/demo_prof/', demo_profiles_view, name='demo_profiles'), 

    path("api/overall-chart/", overall_api_chart_data, name="overall_api_chart_data"),
    path("api/overall-chart2/", overall_api_chart_data2, name="overall_api_chart_data2"),

    # For myapp
    path('admin/', admin.site.urls),
    path('myapp/', include('myapp.urls')),  # Include myapp routes

    path('export/all/', export_all_requests_csv, name='export_all_requests_csv'),
]
