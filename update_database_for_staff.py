#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحديث قاعدة البيانات لإضافة جداول المعلمين والموظفين
"""

import logging
import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager

def update_database():
    """تحديث قاعدة البيانات"""
    try:
        print("بدء تحديث قاعدة البيانات...")
        
        # تهيئة قاعدة البيانات (سيتم إنشاء الجداول الجديدة)
        db_manager.initialize_database()
        
        print("تم تحديث قاعدة البيانات بنجاح!")
        print("تم إضافة جداول:")
        print("- جدول المعلمين (teachers)")
        print("- جدول الموظفين (employees)")
        
        # التحقق من وجود الجداول
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print("\nجداول قاعدة البيانات الحالية:")
            for table in tables:
                print(f"- {table['name']}")
        
        return True
        
    except Exception as e:
        print(f"خطأ في تحديث قاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    success = update_database()
    if success:
        print("\n✓ تم التحديث بنجاح")
        input("اضغط Enter للمتابعة...")
    else:
        print("\n✗ فشل في التحديث")
        input("اضغط Enter للمتابعة...")
