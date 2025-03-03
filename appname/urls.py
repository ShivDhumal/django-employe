from appname.views import*
from django.urls import path

urlpatterns = [
    path('list/<int:pk>/',employe_list.as_view(),name='view_list'),
    path('list/',employe_list.as_view(),name='view_list'),
    path('create/',Create.as_view(),name='create_list'),
    path('update/<int:pk>/', Update.as_view(), name='employee-update'),
    path('delete/<int:pk>/', Delete.as_view(), name='employee-delete'),

]
