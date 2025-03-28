from django.contrib import admin
from .models import Student
from django.contrib.auth.admin import UserAdmin
from silk.models import Request, Response, Profile,SQLQuery

# Register Silk models
# admin.site.register(Request)
# admin.site.register(Response)
# admin.site.register(Profile)
# admin.site.register(SQLQuery)


@admin.register(Student)
class employe_admin(admin.ModelAdmin):
    list_display=('name','age','email')

# Register your models here.
