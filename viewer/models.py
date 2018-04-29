from django.db import models

# Create your models here.
class Station(models.Model):

    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=32)
    location = models.CharField(max_length=32, null=True, blank=True)
    en_name = models.CharField(max_length=64, null=True, blank=True)
    lat = models.DecimalField(max_digits=7, decimal_places=5)
    lon = models.DecimalField(max_digits=8, decimal_places=5)
    altitude = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    hit = models.IntegerField(editable=False, default=0, blank=True)

    def __str__(self):
        return '{} {}'.format(self.code, self.name)

