import json
import os
import re

import requests

CWD = os.path.dirname(os.path.abspath(__file__))
MEANVALUES = json.load(open(os.path.join(CWD, 'mean.json'), encoding='utf8'))

def get_percip_meteomanz(station_code, year, month, day):
    base_url = 'http://www.meteomanz.com/sy1'
    params = {
        'ind': station_code,
        'ty': 'hd',
        'l': 1,
        'd1': '{:02d}'.format(day),
        'm1': '{:02d}'.format(month),
        'y1': year,
        'd2': '{:02d}'.format(day),
        'm2': '{:02d}'.format(month),
        'y2': year,
        'h1': '00Z',
        'h2': '00Z'
    }
    res = requests.get(base_url, params=params)
    match = re.search('<p><br>(.*)<br><br>', res.content.decode('utf8'))
    if match is None or match.group(1) is None:
        return None
    synop = match.group(1)
    match = re.search('333 7([0-9]{4})', synop)
    if match is None or match.group(1) is None:
        return 0
    precip = match.group(1)
    precip = int(precip) / 10
    if percip > 950:
        return 0
    return precip

def get_percip_ogimet(station_code, year, month, day):
    base_url = 'https://www.ogimet.com/display_synops2.php'
    params = {
        'lang': 'en',
        'lugar': station_code,
        'tipo': 'ALL',
        'ord': 'REV',
        'nil': 'Sl',
        'fmt': 'html',
        'ano': year,
        'mes': '{:02d}'.format(month),
        'day': '{:02d}'.format(day),
        'hora': '00',
        'anof': year,
        'mesf': '{:02d}'.format(month),
        'dayf': '{:02d}'.format(day),
        'horaf': '00',
        'send': 'send'
    }
    res = requests.get(base_url, params=params)
    match = re.findall('<b><pre>([^<>]*)</pre></b>', res.content.decode('utf8').replace('\n', ''))
    if len(match) != 2:
        return None
    synop = match[1].replace('\n', '')
    match = re.search('333.*7([0-9]{4}).*=', synop)
    if match is None or match.group(1) is None:
        return 0.0
    percip = match.group(1)
    percip = int(percip) / 10
    if percip > 950:
        return 0.0
    return percip

def get_mean_value(city, month):
    return MEANVALUES[city]['month'][month-1]

def get_month_percent(city, month, value):
    return float(value) / MEANVALUES[city]['month'][month-1] * 100
