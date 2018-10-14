# -*- coding: utf-8 -*-

import sqlite3
from contextlib import closing

DATABASE_NAME = "smarthouse.sqlite"


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
