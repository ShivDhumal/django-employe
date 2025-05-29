from django.contrib import admin
from .models import employee
from django.contrib.auth.admin import UserAdmin
from silk.models import Request, Response, Profile

# Register Silk models
admin.site.register(Request)
admin.site.register(Response)
admin.site.register(Profile)

# admin.site.register(Intercept)

@admin.register(employee)
class employe_admin(admin.ModelAdmin):
    list_display = ('employe_name', 'employe_add', 'employe_number')


