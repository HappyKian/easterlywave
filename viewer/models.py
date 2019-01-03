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

    class Meta:

        ordering = ['-hit']


class HitRecord(models.Model):

    name = models.CharField(max_length=32)
    date = models.DateField(auto_now_add=True)
    hit = models.IntegerField(editable=False, default=1, blank=True)

    def __str__(self):
        return '{} {} > {}'.format(self.date.strftime('%Y/%m/%d'), self.name, self.hit)

    class Meta:

        unique_together = ('name', 'date')
        ordering = ['-hit']


NOTICE_TYPES = ((1, 'good'), (2, 'neutral'), (3, 'bad'))

class Notice(models.Model):

    typ = models.IntegerField(choices=NOTICE_TYPES)
    ttl = models.IntegerField(default=360, blank=True) # in minutes
    start_time = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=256)

    def __str__(self):
        return '<Notice at {}>'.format(self.start_time)
