from django.urls import path
from .views import silk_data, silk_chart_view, employe_list, Create, Update, Delete


urlpatterns = [
    path('list/<int:pk>/', employe_list.as_view(), name='view_list'),
    path('list/', employe_list.as_view(), name='view_list'),
    path('create/', Create.as_view(), name='create_list'),
    path('update/<int:pk>/', Update.as_view(), name='employee-update'),
    path('delete/<int:pk>/', Delete.as_view(), name='employee-delete'),
    
    # Silk analytics endpoints
    path('silk-data/', silk_data, name='silk_data'),
    path('silk-chart/', silk_chart_view, name='silk_chart'),
]
