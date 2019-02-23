import logging
import os
import random
import sys
from datetime import date, datetime, timedelta

import django

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
sys.path.append(root)
os.environ['DJANGO_SETTINGS_MODULE'] = 'windygram.settings'

django.setup()

from django.db.models import Max, Sum

from precipstat.bot import RichTable, RichText, TybbsBot
from precipstat.dailyplot import DailyPlot
from precipstat.models import AnnualStat, DailyStat
from precipstat.psche import search_missing_list, update_today
from precipstat.pstat import get_month_percent


logger = logging.getLogger('precipstat.dailyupdate')
DEBUG = False

class DailyUpdate:

    def __init__(self, dry=False):
        self.bot = TybbsBot()
        self.plot = DailyPlot()
        if DEBUG:
            self.target_thread = 77749
            self.target_forum = 65
        else:
            self.target_thread = 77421
            self.target_forum = 70
        self.today = date.today() - timedelta(days=1)
        self.dry = dry
        if dry:
            logger.warn('Dry TURNED ON')

    def auto(self):
        self.update_data()
        self.prepare_data()
        self.prepare_text()
        self.write_header()
        self.write_today()
        self.write_record()
        self.write_month()
        self.write_annual()
        self.write_footer()
        self.send()

    def set_date(self, _date):
        logger.info('Using date {}'.format(_date.strftime('%Y/%m/%d')))
        self.today = _date

    def get_record(self):
        current_year_records = DailyStat.objects.filter(date__year=self.today.year,
            date__lt=self.today)
        qs_record = current_year_records.values('name').annotate(max=Max('percip'))
        self.record_data = {}
        for query in qs_record:
            name = query['name']
            record = query['max']
            date = current_year_records.filter(name=name, percip=record).latest().date
            self.record_data[name] = {'date': date, 'record': record}

    def update_data(self):
        self.get_record()
        logger.info("Begin daily update! Now time: {}".format(datetime.now()))
        update_today()
        search_missing_list()
        logger.info("End daily update! Now: {}".format(datetime.now()))

    def prepare_data(self):
        self.today_data = DailyStat.objects.filter(date=self.today).order_by('-percip')
        self.month_data = DailyStat.objects.filter(date__month=self.today.month,
            date__year=self.today.year).values('name').annotate(sum=Sum('percip')).order_by('-sum')
        self.annual_data = AnnualStat.objects.filter(year=self.today.year).order_by('-percip')

    def prepare_text(self):
        self.text = RichText()
        self.real_text = RichText()
        self.city_list = []
        filepath = os.path.join(root, 'precipstat', 'stations.txt')
        with open(filepath) as f:
            for line in f:
                code, name = tuple(line.split())
                self.city_list.append(name)
        self.table = RichTable(len(self.city_list)+1, 4)
        self.table.set_richtext(self.text)
        self.table.set_header('', '本月累积', '', '本年累积')

    def write_header(self):
        with self.text.bold():
            self.text.add(self.today.strftime('%Y/%m/%d'))

    def write_today(self):
        self.has_percip = [] # If no major city has any percip, go for vacation today!
        for city_data in self.today_data:
            percip = city_data.percip
            name = city_data.name
            if percip == 0:
                continue
            self.has_percip.append(name)
            self.plot.add_today_info(name, percip)
            text = '{} {:.1f}mm'.format(name, percip)
            if percip >= 50:
                with self.text.red():
                    self.text.add(text)
            else:
                self.text.add(text)
        if len(self.has_percip) == 0:
            logger.info("Uh-oh, no city has any percip today! Exit happily!")
            exit(0)
        self.text.add()

    def write_record(self):
        has_record = False
        for city_data in self.today_data:
            percip = city_data.percip
            name = city_data.name
            prev_record = self.record_data[name]['record']
            if percip > prev_record and percip >= 20:
                has_record = True
                prev_date = self.record_data[name]['date']
                self.plot.add_record_text('{}刷新了今年的日雨量纪录 （原纪录：{:.1f}mm {}）'
                              ''.format(name, prev_record, prev_date.strftime('%Y/%m/%d')))
        if has_record:
            self.text.add()
    
    def write_month(self):
        # self.text.add('{}月排名'.format(self.today.month))
        # for city_data in self.month_data:
        #     self.text.add('{} {:.1f}mm'.format(city_data['name'], city_data['sum']))
        # self.text.add()
        for i, city_data in enumerate(self.month_data, 2):
            month_percent = get_month_percent(city_data['name'], self.today.month, city_data['sum'])
            self.plot.add_month_info(city_data['name'], city_data['sum'], month_percent)
            text = '{:.1f}mm'.format(city_data['sum'])
            if city_data['name'] in self.has_percip:
                text = text + '*'
            self.table.set_cell(i, 1, ' ' + city_data['name'])
            self.table.set_cell(i, 2, text)

    def write_annual(self):
        # self.text.add('本年累积雨量')
        # for city_data in self.annual_data:
        #     self.text.add('{} {:.1f}mm'.format(city_data.name, city_data.percip), newline=False)
        #     if city_data.name in self.has_percip:
        #         self.text.add('*')
        #     else:
        #         self.text.add()
        # self.text.add()
        for i, city_data in enumerate(self.annual_data, 2):
            self.plot.add_annual_info(city_data.name, city_data.percip)
            text = '{:.1f}mm'.format(city_data.percip)
            if city_data.name in self.has_percip:
                text = text + '*'
            self.table.set_cell(i, 3, ' ' + city_data.name)
            self.table.set_cell(i, 4, text)
        self.table.export()

    def write_footer(self):
        with self.text.very_small():
            self.text.add('我是个机器人账号，发给我的任何消息都不会被注意:) 如果有任何疑问，请询问nasdaq')
            self.text.add('数据收集于国际交换站报文，统计时间为08-08，每日更新时间为上午10点。', newline=False)
            with self.text.blue():
                self.text.add('*号表示本日有降水量更新')
            with self.text.italic():
                self.text.add('bleep bloop~')

    def send(self):
        logger.info("===TODAY'S POST===")
        logger.info(self.text.content)
        self.plot.set_date(self.today)
        self.plot.set_title('南方省会降水量统计')
        logger.info('Plotting...')
        self.plot.plot()
        path = 'precipstat/plots/{}.png'.format(self.today.strftime('%Y%m%d'))
        self.plot.save(path)
        logger.info('Export to {}'.format(path))
        if self.dry:
            return
        self.bot.login()
        self.real_text.insert_image(self.bot.upload_image(self.target_thread, self.target_forum, path))
        self.bot.post_rich(self.target_thread, self.target_forum, content=self.real_text)
        logger.info("===POST FINISHED===")

if __name__ == '__main__':
    if len(sys.argv) == 2:
        cmd = sys.argv[1]
        if cmd == 'dry':
            DailyUpdate(dry=True).auto()
    else:
        DailyUpdate().auto()
