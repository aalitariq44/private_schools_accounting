#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

db_path = 'data/database/schools.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('الجداول الموجودة في قاعدة البيانات:')
    for table in tables:
        print(f'- {table[0]}')
    conn.close()
else:
    print('قاعدة البيانات غير موجودة')
