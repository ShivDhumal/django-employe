from appname.views import *
from django.urls import path
from .views import StudentList, CreateStudent, UpdateStudent, DeleteStudent

urlpatterns = [
    path('list/<int:pk>/', StudentList.as_view(), name='student_list'),
    path('list/', StudentList.as_view(), name='student_list'),
    path('create/', CreateStudent.as_view(), name='student_create'),
    path('update/<int:pk>/', UpdateStudent.as_view(), name='student_update'),
    path('delete/<int:pk>/', DeleteStudent.as_view(), name='student_delete'),
]
