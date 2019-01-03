import datetime
import os
import shutil

MEDIA_ADDR = '/root/web/media/'
DAYS_BUFFER = 7
DAYS_CHECKED = 3

def main():
    today = datetime.date.today()
    for i in range(DAYS_CHECKED):
        check_and_delete(today - datetime.timedelta(days=DAYS_BUFFER+i+1))

def check_and_delete(date):
    for hour in (0, 12):
        dt = datetime.datetime(date.year, date.month, date.day, hour)
        directory = MEDIA_ADDR + dt.strftime('%Y%m%d%H')
        if os.path.exists(directory):
            shutil.rmtree(directory)


if __name__ == '__main__':
    main()
