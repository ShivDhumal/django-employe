from django.urls import path
from appname.views import (
    silk_chart_data, 
    silk_chart_view, 
    employe_list, 
    Create, 
    Update, 
    Delete,
    most_queries_chart_page,  
    most_queries_chart_api,   
    most_time_chart_page,      # ✅ Added import for Most Time Chart Page
    most_time_overall_data  ,# ✅ Added import for Most Time Overall API
  
)

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
    path('silk/most-queries/', most_queries_chart_page, name='most_queries_chart_page'),  
    path('api/silk-most-queries/', most_queries_chart_api, name='most_queries_chart_api'),  

    # ✅ New URLs for `chart_most_time_overall.html`
    path('silk/most-time-overall/', most_time_chart_page, name='most_time_chart_page'),
    path('api/silk-most-time-overall/', most_time_overall_data, name='most_time_overall_data'),  # Returns JSON data
   
]
