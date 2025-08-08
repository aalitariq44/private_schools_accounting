#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع للتأكد من عمل قاعدة البيانات
"""

import sys
import os
from pathlib import Path

# إضافة المسار الجذر للمشروع
sys.path.insert(0, str(Path(__file__).parent))

from core.database.connection import db_manager

def test_database():
    """اختبار قاعدة البيانات"""
    try:
        print("اختبار الاتصال بقاعدة البيانات...")
        
        # اختبار جدول المدارس
        print("اختبار جدول المدارس...")
        schools = db_manager.execute_query("SELECT * FROM schools")
        print(f"عدد المدارس: {len(schools)}")
        
        # اختبار جدول الطلاب
        print("اختبار جدول الطلاب...")
        students = db_manager.execute_query("SELECT * FROM students")
        print(f"عدد الطلاب: {len(students)}")
        
        # اختبار جدول الإيرادات الخارجية
        print("اختبار جدول الإيرادات الخارجية...")
        external_income = db_manager.execute_query("SELECT * FROM external_income")
        print(f"عدد الإيرادات الخارجية: {len(external_income)}")
        
        # اختبار جدول المصروفات
        print("اختبار جدول المصروفات...")
        expenses = db_manager.execute_query("SELECT * FROM expenses")
        print(f"عدد المصروفات: {len(expenses)}")
        
        # اختبار جدول الرواتب
        print("اختبار جدول الرواتب...")
        salaries = db_manager.execute_query("SELECT * FROM salaries")
        print(f"عدد الرواتب: {len(salaries)}")
        
        print("✅ جميع الجداول تعمل بشكل صحيح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار قاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    success = test_database()
    if success:
        print("\n🎉 قاعدة البيانات تعمل بشكل صحيح!")
    else:
        print("\n💥 هناك مشكلة في قاعدة البيانات!")
        sys.exit(1)
