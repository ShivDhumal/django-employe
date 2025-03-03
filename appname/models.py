from django.db import models


# Create your models here.
class employee(models.Model):
    
    employe_name=models.CharField(max_length=100)
    employe_add=models.CharField(max_length=100)
    employe_number = models.BigIntegerField()

    def __str__(self):
        return self.employe_name