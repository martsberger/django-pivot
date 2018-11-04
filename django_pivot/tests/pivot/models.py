from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=7)

    def __unicode__(self):
        return self.name


class Store(models.Model):
    name = models.CharField(max_length=20)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.name


class ShirtSales(models.Model):
    GENDER_CHOICES = (('B', 'Boy'),
                      ('G', 'Girl'))

    gender = models.CharField(max_length=4, choices=GENDER_CHOICES)
    style = models.CharField(max_length=5)
    shipped = models.DateField()
    units = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
