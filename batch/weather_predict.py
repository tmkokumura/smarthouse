# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.utils import formatdate
import time
import json
import requests
import logging
import os
import smtplib
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

log_fmt = '%(asctime)s %(levelname)s %(name)s :%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_fmt)

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = '587'
SMTP_USER = 'buntshift@gmail.com'
SMTP_PASSWORD = 'obviously0621YES'
TO_ADDRESS = ['buntshift@gmail.com', 'y_momo_12@yahoo.co.jp']
SUBJECT = '傘を持っていこう'
BODY = 'pythonでメール送信'

TEMPLATE = '''今日は雨がふるよ！傘を持っていこう！

【今日の天気】
{dt1} {weather1}
{dt2} {weather2}
{dt3} {weather3}
{dt4} {weather4}
{dt5} {weather5}
{dt6} {weather6}
'''


def create_message(from_addr, to_addrs, subject, message_body):
    msg = MIMEText(message_body)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ','.join(to_addrs)
    msg['Date'] = formatdate()
    return msg


def send(from_addr, to_addrs, msg):
    smtpobj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtpobj.set_debuglevel(True)
    smtpobj.ehlo()
    smtpobj.starttls()
    smtpobj.ehlo()
    smtpobj.login(SMTP_USER, SMTP_PASSWORD)
    smtpobj.sendmail(from_addr, ','.join(to_addrs), msg.as_string())
    smtpobj.close()


def parse(json_dict, max_time):
    data_list = json_dict['list']

    weather_list = []
    for data in data_list:
        dt = data['dt']
        weather = data['weather'][0]
        main = weather['main']
        description = weather['description']
        if dt <= max_time:
            weather_list.append((dt, main, description))

    return weather_list


def request():
    url = 'http://api.openweathermap.org/data/2.5/forecast'
    url_params = {'q': 'Tokyo', 'units': 'metric', 'APPID': 'e7fbfe9a2c96e5ff6f3924c7056a441e'}
    res = requests.get(url, params=url_params)

    return res.status_code, json.loads(res.text)


def get_weather_text(api_text):
    if api_text == 'Clear':
        return '晴'
    elif api_text == 'Cloud':
        return 'くもり'
    elif api_text == 'Rain':
        return '雨'
    else:
        return api_text


def has_rain(weather_list):
    for weather in weather_list:
        if weather[1] == 'Rain':
            return True
    return False


if __name__ == '__main__':
    logging.info('Start [weather_predict.py]')

    while True:
        logging.info('loop start')

        now = datetime.now()
        logging.info('now: {}'.format(now))

        if now.hour == 5:

            status_code, res_dict = request()

            if status_code == 200:
                max_time = now + timedelta(hours=18)
                max_unix_time = int(max_time.timestamp())
                weather_list = parse(res_dict, max_unix_time)
                logging.info('weather_list: {}'.format(weather_list))

                if has_rain(weather_list):
                    params = {"dt1": datetime.fromtimestamp(weather_list[0][0]),
                              "weather1": get_weather_text(weather_list[0][1]),
                              "dt2": datetime.fromtimestamp(weather_list[1][0]),
                              "weather2": get_weather_text(weather_list[1][1]),
                              "dt3": datetime.fromtimestamp(weather_list[2][0]),
                              "weather3": get_weather_text(weather_list[2][1]),
                              "dt4": datetime.fromtimestamp(weather_list[3][0]),
                              "weather4": get_weather_text(weather_list[3][1]),
                              "dt5": datetime.fromtimestamp(weather_list[4][0]),
                              "weather5": get_weather_text(weather_list[4][1]),
                              "dt6": datetime.fromtimestamp(weather_list[5][0]),
                              "weather6": get_weather_text(weather_list[5][1])
                              }

                    logging.info('send mail to {}'.format(TO_ADDRESS))
                    message_body = TEMPLATE.format(**params)
                    msg = create_message(SMTP_USER, TO_ADDRESS, SUBJECT, message_body)
                    send(SMTP_USER, TO_ADDRESS, msg)

        else:
            logging.info('skip')

        sleep_time = 60 * 60    # 1 hour
        time.sleep(sleep_time)

    logging.info('End [weather_predict]')
