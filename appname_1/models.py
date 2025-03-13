from django.db import models

class Student(models.Model):
    student_name = models.CharField(max_length=100)
    student_address = models.CharField(max_length=100)
    student_number = models.BigIntegerField()

    def __str__(self):
        return self.student_name

