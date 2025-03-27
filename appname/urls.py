from django.urls import path
from appname.views import (
    silk_chart_data, 
    silk_chart_view, 
    employe_list, 
    Create, 
    Update, 
    Delete,
   most_queries_chart_api,   
   most_time_overall_data  ,# ✅ Added import for Most Time Overall API
    
  
)
from .views import chart_most_time_overall_view
from .views import most_db_queries_view  # Import the new view



urlpatterns = [
    path('list/<int:pk>/', employe_list.as_view(), name='view_list'),
    path('list/', employe_list.as_view(), name='view_list'),
    path('create/', Create.as_view(), name='create_list'),
    path('update/<int:pk>/', Update.as_view(), name='employee-update'),
    path('delete/<int:pk>/', Delete.as_view(), name='employee-delete'),

    # Silk analytics endpoints
    path('silk-chart/', silk_chart_view, name='silk_chart'),
    path('api/silk-data/', silk_chart_data, name='silk_chart_data'),

    # ✅ URLs for `most_db_queries.html`
    
    path('silk/most_db_queries/', most_db_queries_view, name='most_db_queries'),
    path('api/silk-most-queries/', most_queries_chart_api, name='most_queries_chart_api'),  

    # ✅ New URLs for `chart_most_time_overall.html`

    path('silk/chart_most_time_overall/', chart_most_time_overall_view, name='chart_most_time_overall'),
    path('api/silk-most-time-overall/', most_time_overall_data, name='most_time_overall_data'),  # Returns JSON data
   
]
