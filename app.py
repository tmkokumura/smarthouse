from flask import Flask, render_template, redirect, request, url_for

from datetime import datetime
from contextlib import closing
import os
import sqlite3

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'upload')
DATABASE_NAME = "smarthouse.sqlite"


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


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


@app.route('/chart', methods=['GET'])
def chart():
    sql = 'SELECT detect_dt, value FROM sensor_values WHERE sensor_id = 1 ORDER BY detect_dt;'
    rows = select(sql)
    detect_dt_list = [x[0] for x in rows]
    value_list = [x[1] for x in rows]

    labels = list_to_text(detect_dt_list)
    datas = list_to_text(value_list)

    return render_template('chart.html', labels=labels, datas=datas)


@app.route('/sensor/list', methods=['GET'])
def sensor_list():

    sql = 'SELECT sensor_id, sensor_name, description FROM sensors WHERE del_flag = ? ORDER BY sensor_id;'
    params = ('0',)
    rows = select(sql, params)

    sensors = []
    for row in rows:
        sensor = {
            'sensor_id': row[0],
            'sensor_name': row[1],
            'description': row[2]
        }
        sensors.append(sensor)

    return render_template('sensor_list.html', sensors=sensors)


@app.route('/sensor/update', methods=['GET', 'POST'])
def sensor_update():

    # 初期表示
    if request.method == 'GET':
        # クエリパラメータの取得
        sensor_id = request.args.get('sensor_id')

        sensor = {}

        # クエリパラメータが設定されている場合はセンサー値を取得
        if sensor_id is not None:
            sql = 'SELECT sensor_id, sensor_name, description FROM sensors WHERE sensor_id = ? AND del_flag = ?;'
            params = (sensor_id, '0')
            row = select(sql, params)[0]
            sensor = {
                'sensor_id': row[0],
                'sensor_name': row[1],
                'description': row[2]
            }

        return render_template('sensor_update.html', sensor=sensor)

    # 登録・更新
    else:
        # Formパラメータの取得
        sensor_id = request.form['sensor_id']
        sensor_name = request.form['sensor_name']
        description = request.form['description']

        # 登録の場合
        if sensor_id == '':
            # センサーを登録する
            sql = 'INSERT INTO sensors(sensor_name, description, del_flag) VALUES (?, ?, ?);'
            params = (sensor_name, description, '0')
            insert(sql, params)

        # 更新の場合
        else:
            # センサー値を更新する
            sql = 'UPDATE sensors SET sensor_name = ?, description = ? WHERE sensor_id = ?;'
            params = (sensor_name, description, sensor_id)
            update(sql, params)

        return redirect(url_for('sensor_list'), code=302)


@app.route('/sensor/value/list', methods=['GET'])
def sensor_value_list():

    # クエリパラメータの取得
    sensor_id = request.args.get('sensor_id')

    sql = 'SELECT detect_id, detect_dt, value FROM sensor_values WHERE sensor_id = ? ORDER BY sensor_id, detect_dt, detect_id;'
    params = (sensor_id,)
    rows = select(sql, params)

    sensor_values = []
    for row in rows:
        sensor_value = {
            'detect_id': row[0],
            'detect_dt': row[1],
            'value': row[2]
        }
        sensor_values.append(sensor_value)

        print(sensor_id)

    return render_template('sensor_value_list.html', sensor_id=sensor_id, sensor_values=sensor_values)


@app.route('/sensor/value/update', methods=['GET', 'POST'])
def sensor_value_update():

    # 初期表示
    if request.method == 'GET':
        # クエリパラメータの取得
        sensor_id = request.args.get('sensor_id')
        detect_id = request.args.get('detect_id')

        sensor_value = {}

        # detect_idが設定されている場合はセンサー値を取得
        if detect_id is not None:
            sql = 'SELECT detect_id, detect_dt, value FROM sensor_values WHERE sensor_id = ? AND detect_id = ?;'
            params = (sensor_id, detect_id)
            row = select(sql, params)[0]
            sensor_value = {
                'detect_id': row[0],
                'detect_dt': row[1],
                'value': row[2]
            }

        return render_template('sensor_value_update.html', sensor_id=sensor_id, sensor_value=sensor_value)

    # 登録・更新
    else:
        # Formパラメータの取得
        sensor_id = request.form['sensor_id']
        detect_id = request.form['detect_id']
        detect_dt = request.form['detect_dt']
        value = request.form['value']

        print('sensor_id: {}'.format(sensor_id))

        # 登録の場合
        if detect_id == '':
            # detect_idを求める
            sql = 'SELECT MAX(detect_id) FROM sensor_values WHERE sensor_id = ?;'
            params = (sensor_id,)
            row = select(sql, params)[0]
            detect_id = row[0]

            if detect_id is None:
                detect_id = 1
            else:
                detect_id += 1

            # センサー値を登録する
            sql = 'INSERT INTO sensor_values(sensor_id, detect_id, detect_dt, value) VALUES (?, ?, ?, ?);'
            params = (sensor_id, detect_id, detect_dt, value)
            insert(sql, params)

        # 更新の場合
        else:
            # センサー値を更新する
            sql = 'UPDATE sensor_values SET detect_dt = ?, value = ? WHERE sensor_id = ? AND detect_id = ?;'
            params = (detect_dt, value, sensor_id, detect_id)
            update(sql, params)

        return redirect(url_for('sensor_value_list', sensor_id=sensor_id), code=302)


def select(sql, params=None):
    with closing(sqlite3.connect(DATABASE_NAME)) as conn:
        c = conn.cursor()
        if params is None:
            c.execute(sql)
        else:
            c.execute(sql, params)
        return c.fetchall()


def insert(sql, params=None):
    with closing(sqlite3.connect(DATABASE_NAME)) as conn:
        c = conn.cursor()
        if params is None:
            c.execute(sql)
        else:
            c.execute(sql, params)
        conn.commit()


def update(sql, params=None):
    with closing(sqlite3.connect(DATABASE_NAME)) as conn:
        c = conn.cursor()
        if params is None:
            c.execute(sql)
        else:
            c.execute(sql, params)
        conn.commit()


def list_to_text(liststr):
    text = ''
    for i, s in enumerate(liststr):
        text += str(s)
        text += ','
    return text.rstrip(',')




if __name__ == '__main__':
    app.run(debug=True)
