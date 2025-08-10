#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص بنية جدول المصروفات
"""

import sqlite3
import os

def check_expenses_table():
    """فحص بنية جدول المصروفات"""
    db_path = 'data/database/schools.db'
    
    if not os.path.exists(db_path):
        print("ملف قاعدة البيانات غير موجود!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== بنية جدول expenses ===")
        cursor.execute("PRAGMA table_info(expenses)")
        columns = cursor.fetchall()
        if columns:
            for col in columns:
                print(f"العمود: {col[1]}, النوع: {col[2]}, NULL: {col[3]}, افتراضي: {col[4]}")
        else:
            print("الجدول غير موجود أو فارغ")
        
        conn.close()
        
    except Exception as e:
        print(f"خطأ في فحص قاعدة البيانات: {e}")

if __name__ == "__main__":
    check_expenses_table()
