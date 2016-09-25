from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=7)

    def __unicode__(self):
        return self.name


class Store(models.Model):
    name = models.CharField(max_length=20)
    region = models.ForeignKey(Region)

    def __unicode__(self):
        return self.name


class ShirtSales(models.Model):
    gender = models.CharField(max_length=4)
    style = models.CharField(max_length=5)
    shipped = models.DateField()
    units = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    store = models.ForeignKey(Store)
