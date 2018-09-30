from flask import Flask, render_template, redirect, request, url_for

from datetime import datetime
from contextlib import closing
import os
import sqlite3

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'upload')
DATABASE_NAME = "smarthouse"


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    message = "こんにちは、あなたの名前を入力してください"
    return render_template('index.html', message=message)


@app.route('/upload', methods=['POST'])
def upload():
    ts = datetime.now().strftime('%Y%m%d%H%M%S')

    f = request.files['example']

    upload_file_name = ts + '_' + f.filename
    upload_file_path = os.path.join(UPLOAD_DIR, upload_file_name)

    app.logger.info('saving:{}'.format(upload_file_path))
    f.save(upload_file_path)

    return redirect(url_for('/upload/complete'), code=302)


@app.route('/upload/complete', methods=['GET'])
def upload_complete():
    return render_template('upload_complete.html')


@app.route('/graph', methods=['GET'])
def graph():
    return render_template('graph.html')


@app.route('/sensor/value', methods=['GET'])
def sensor_value():

    sensor_id = request.args.get('sensor_id')
    datetime = request.args.get('datetime')
    value = request.args.get('value')

    with closing(sqlite3.connect(DATABASE_NAME)) as conn:
        c = conn.cursor()
        sql = 'INSERT INTO sensor_value(sensor_id, datetime, value) VALUES (?, ?, ?)'
        params = (sensor_id, datetime, value)
        c.execute(sql, params)
        conn.commit()

if __name__ == '__main__':
    app.run(debug=True)
