from django.urls import path
from .views import StudentList, StudentCreate, StudentUpdate, StudentDelete

urlpatterns = [
    path('students/', StudentList.as_view(), name='student_list'),
    path('students/<int:pk>/', StudentList.as_view(), name='student_detail'),
    path('students/add/', StudentCreate.as_view(), name='student_create'),
    path('students/edit/<int:pk>/', StudentUpdate.as_view(), name='student_update'),
    path('students/delete/<int:pk>/', StudentDelete.as_view(), name='student_delete'),
]
