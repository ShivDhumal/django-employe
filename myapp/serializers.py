from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):  # ✅ Correct naming
    class Meta:
        model = Student
        fields = '__all__'
