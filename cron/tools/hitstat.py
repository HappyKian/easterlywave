import django
import os
import sys

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(root)
sys.path.append(root)
os.environ['DJANGO_SETTINGS_MODULE'] = 'windygram.settings'

django.setup()

import datetime
from django.db.models import Sum
from django.conf import settings

from viewer.models import HitRecord

EXPORT_TXT_FILE = os.path.join(settings.MEDIA_ROOT, 'dailyreport.txt')
RANKING_STATION_NUM = 15

def export_report(date):
    queryset = HitRecord.objects.filter(date=date)
    stations_num = len(queryset)
    hot_choices = queryset[:RANKING_STATION_NUM]
    total_hits = queryset.aggregate(Sum('hit'))['hit__sum']
    try:
        HitRecord.objects.get(name='0', date=date)
    except HitRecord.DoesNotExist:
        pass
    else:
        stations_num -= 1
    with open(EXPORT_TXT_FILE, 'w', encoding='utf8') as f:
        f.write('windygram每日报告  {}\n'.format(date.strftime('%Y/%m/%d')))
        f.write('\n============================\n\n')
        f.write('总共查询  {}  次，涵盖  {}  个站点。\n'.format(total_hits, stations_num))
        f.write('\n============================\n\n')
        f.write('热门查询站点（前15名）：\n\n')
        for choice in hot_choices:
            if choice.name == '0':
                name = '<非站点>'
            else:
                name = choice.name
            f.write('{}  {}\n'.format(name, choice.hit))
        f.write('\n')

def daily_export():
    export_time = datetime.date.today() - datetime.timedelta(days=1)
    export_report(export_time)


if __name__ == "__main__":
     daily_export()

