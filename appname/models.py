from django.db import models

# Your existing Employee model
class employee(models.Model):
    employe_name = models.CharField(max_length=100)
    employe_add = models.CharField(max_length=100)
    employe_number = models.BigIntegerField()

    def __str__(self):
        return self.employe_name

