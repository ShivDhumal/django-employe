from django.contrib import admin
from .models import employee
from django.contrib.auth.admin import UserAdmin

@admin.register(employee)
class employe_admin(admin.ModelAdmin):
    list_display=('employe_name','employe_add','employe_number')

# Register your models here.
