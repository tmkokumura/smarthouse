# -*- coding: utf-8 -*-
from datetime import datetime
import time
import json
import requests
import logging
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from util import db_utils

logging.basicConfig(level=logging.DEBUG)


def get_insert_params(data_dict):

    main_dict = data_dict['main']
    wind_dict = data_dict['wind']
    weather_dict = data_dict['weather'][0]

    city = data_dict['name']
    dt = datetime.fromtimestamp(data_dict['dt'])    # JST
    temp = main_dict['temp']                        # Celsius
    pressure = main_dict['pressure']                # hPa
    humidity = main_dict['humidity']                # %
    wind_speed = wind_dict['speed']                 # m/s
    wind_deg = wind_dict['deg']                     # degree
    description = weather_dict['main']
    sub_description = weather_dict['description']

    params = (city, dt, temp, pressure, humidity, wind_speed, wind_deg, description, sub_description)

    return params


def get_select_params(data_dict):
    city = data_dict['name']
    dt = datetime.fromtimestamp(data_dict['dt'])    # JST

    params = (city, dt)

    return params


def request():
    url = 'http://api.openweathermap.org/data/2.5/weather'
    url_params = {'q': 'Tokyo', 'units': 'metric', 'APPID': 'e7fbfe9a2c96e5ff6f3924c7056a441e'}
    res = requests.get(url, params=url_params)

    return res.status_code, json.loads(res.text)


def insert_weather(res_dict_):
    sql = 'INSERT INTO weather (city, dt, temp, pressure, humidity, wind_speed, wind_deg, \
                    description, sub_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
    sql_params = get_insert_params(res_dict_)
    logging.debug(sql_params)

    db_utils.insert(sql, params=sql_params)


def select_weather(res_dict_):
    sql = 'SELECT COUNT(1) FROM weather WHERE city = ? AND dt = ?;'
    sql_params = get_select_params(res_dict_)
    logging.debug(sql_params)

    return db_utils.select(sql, params=sql_params)[0][0]


if __name__ == '__main__':
    logging.info('Start [weather.py]')

    while True:
        logging.info('execute api')
        status_code, res_dict = request()

        if status_code == 200:
            logging.info('execute select')
            count = select_weather(res_dict)

            if count == 0:
                logging.info('execute insert')
                insert_weather(res_dict)
            else:
                logging.info('skip executing insert')

        time.sleep(3600)

    logging.info('End [weather.py]')
