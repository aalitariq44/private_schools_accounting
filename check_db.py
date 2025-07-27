#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

# التحقق من وجود قاعدة البيانات
db_path = 'data/database/schools.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # فحص هيكل جدول الطلاب
    print('=== جدول الطلاب ===')
    cursor.execute('PRAGMA table_info(students)')
    students_cols = cursor.fetchall()
    for col in students_cols:
        print(f'{col[1]} - {col[2]}')
    
    print('\n=== جدول الأقساط ===')
    cursor.execute('PRAGMA table_info(installments)')
    installments_cols = cursor.fetchall()
    for col in installments_cols:
        print(f'{col[1]} - {col[2]}')
        
    print('\n=== جدول الرسوم الإضافية ===')
    cursor.execute('PRAGMA table_info(additional_fees)')
    fees_cols = cursor.fetchall()
    for col in fees_cols:
        print(f'{col[1]} - {col[2]}')
    
    conn.close()
else:
    print('قاعدة البيانات غير موجودة')
