import logging
import os
from datetime import date, timedelta

from precipstat.models import AnnualStat, DailyStat
from precipstat.pstat import get_percip_ogimet


__file_dir = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)

def update_list(date):
    f = open(os.path.join(__file_dir, 'stations.txt'))
    for line in f:
        code, name = tuple(line.split())
        percip = get_percip_ogimet(code, date.year, date.month, date.day)
        if percip is None:
            logger.warn("Get {} percip failed.".format(name))
            continue
        update_station(code, name, date, percip)
    f.close()
        
def update_today():
    update_list(date.today())

def update_single_station(code, name, date):
    percip = get_percip_ogimet(code, date.year, date.month, date.day)
    if percip is None:
        logger.warn("Get {} percip failed.".format(name))
        return
    update_station(code, name, date, percip)

def update_station(code, name, report_date, percip):
    date = report_date - timedelta(days=1)
    logger.info("GET {} {} {:.1f}mm".format(name, date.strftime('%Y%m%d'), percip))
    try:
        daily_value = DailyStat.objects.get(name=name, date=date)
    except DailyStat.DoesNotExist:
        pass
    else:
        return _update_station_existed(code, name, date, percip, daily_value)
    DailyStat.objects.create(code=code, name=name, percip=percip, date=date)
    try:
        annual_value = AnnualStat.objects.get(name=name, year=date.year)
    except AnnualStat.DoesNotExist:
        annual_value = AnnualStat.objects.create(code=code, name=name, year=date.year)
    annual_value.percip = float(annual_value.percip) + percip
    logger.info("UPDATE {} annual {:.1f}mm".format(name, annual_value.percip))
    annual_value.save()

def _update_station_existed(code, name, date, percip, prev_val):
    prev_percip = float(prev_val.percip)
    prev_val.percip = percip
    prev_val.save()
    annual_val = AnnualStat.objects.get(name=name, year=date.year)
    annual_val.percip = float(annual_val.percip) - prev_percip + percip
    logger.info("UPDATE {} annual {:.1f}mm".format(name, annual_val.percip))
    annual_val.save()

def update(year, month, day):
    update_list(date(year, month, day))

def search_missing(code, name, fill=False):
    today = date.today() - timedelta(days=1)
    annual_count = DailyStat.objects.filter(date__year=today.year, name=name).count()
    yday = today.timetuple().tm_yday
    if annual_count == yday:
        logger.info('No missing value found for {}'.format(name))
        return
    missing_days = yday - annual_count
    logger.info("{} missing days for {}.".format(missing_days, name))
    found_days = 0
    for i in range(yday):
        search_date = today - timedelta(days=i)
        try:
            DailyStat.objects.get(name=name, date=search_date)
        except DailyStat.DoesNotExist:
            logger.info("Found missing values for {} on {}.".format(name, search_date.strftime('%Y%m%d')))
            if fill:
                logger.info("Try to fill...")
                update_single_station(code, name, search_date)
            found_days += 1
            logger.debug("Found days: {}".format(found_days))
            if found_days == missing_days:
                break

def search_missing_list(fill=True):
    f = open(os.path.join(__file_dir, 'stations.txt'))
    for line in f:
        code, name = tuple(line.split())
        search_missing(code, name, fill=fill)
    f.close()
