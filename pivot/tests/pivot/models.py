from django.db import models


class ShirtSales(models.Model):
    region = models.CharField(max_length=6)
    gender = models.CharField(max_length=4)
    style = models.CharField(max_length=5)
    shipped = models.DateField()
    units = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)