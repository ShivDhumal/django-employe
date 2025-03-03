
from rest_framework import serializers
from .models import employee

class employe_serializer(serializers.ModelSerializer):
    class Meta:
        model=employee  
        fields='__all__'  #getting all fields from models