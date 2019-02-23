from django.db import models

# Create your models here.
class AnnualStat(models.Model):

    code = models.CharField(max_length=10)
    name = models.CharField(max_length=32)
    year = models.IntegerField()
    percip = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {:.1f}mm  [{}]'.format(self.name, self.percip, self.last_update.strftime('%m/%d %H:%M'))


class DailyStat(models.Model):

    code = models.CharField(max_length=10)
    name = models.CharField(max_length=32)
    percip = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True)
    date = models.DateField()
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}  {} {:.1f}mm'.format(self.date.strftime('%Y/%m/%d'), self.name, self.percip)

    class Meta:
        get_latest_by = 'date'
