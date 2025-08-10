#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص بنية جداول قاعدة البيانات
"""

import sqlite3
import os

def check_table_structure():
    """فحص بنية جداول قاعدة البيانات"""
    db_path = 'data/database/schools.db'
    
    if not os.path.exists(db_path):
        print("ملف قاعدة البيانات غير موجود!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # فحص جدول external_income
        print("=== بنية جدول external_income ===")
        cursor.execute("PRAGMA table_info(external_income)")
        columns = cursor.fetchall()
        if columns:
            for col in columns:
                print(f"العمود: {col[1]}, النوع: {col[2]}, NULL: {col[3]}, افتراضي: {col[4]}")
        else:
            print("الجدول غير موجود أو فارغ")
        
        print("\n=== بنية جدول expenses ===")
        cursor.execute("PRAGMA table_info(expenses)")
        columns = cursor.fetchall()
        if columns:
            for col in columns:
                print(f"العمود: {col[1]}, النوع: {col[2]}, NULL: {col[3]}, افتراضي: {col[4]}")
        else:
            print("الجدول غير موجود أو فارغ")
            
        print("\n=== بنية جدول salaries ===")
        cursor.execute("PRAGMA table_info(salaries)")
        columns = cursor.fetchall()
        if columns:
            for col in columns:
                print(f"العمود: {col[1]}, النوع: {col[2]}, NULL: {col[3]}, افتراضي: {col[4]}")
        else:
            print("الجدول غير موجود أو فارغ")
        
        # فحص جميع الجداول الموجودة
        print("\n=== جميع الجداول الموجودة ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"جدول: {table[0]}")
            
        conn.close()
        
    except Exception as e:
        print(f"خطأ في فحص قاعدة البيانات: {e}")

if __name__ == "__main__":
    check_table_structure()
