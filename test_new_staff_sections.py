#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع للتأكد من عمل الأقسام الجديدة
"""

import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """اختبار استيراد الصفحات الجديدة"""
    try:
        print("اختبار استيراد صفحات المعلمين...")
        from ui.pages.teachers.teachers_page import TeachersPage
        from ui.pages.teachers.add_teacher_dialog import AddTeacherDialog
        from ui.pages.teachers.edit_teacher_dialog import EditTeacherDialog
        print("✓ تم استيراد صفحات المعلمين بنجاح")
        
        print("اختبار استيراد صفحات الموظفين...")
        from ui.pages.employees.employees_page import EmployeesPage
        from ui.pages.employees.add_employee_dialog import AddEmployeeDialog
        from ui.pages.employees.edit_employee_dialog import EditEmployeeDialog
        print("✓ تم استيراد صفحات الموظفين بنجاح")
        
        return True
        
    except Exception as e:
        print(f"✗ خطأ في الاستيراد: {e}")
        return False

def test_database():
    """اختبار قاعدة البيانات"""
    try:
        print("اختبار الاتصال بقاعدة البيانات...")
        from core.database.connection import db_manager
        
        with db_manager.get_cursor() as cursor:
            # التحقق من جدول المعلمين
            cursor.execute("SELECT COUNT(*) as count FROM teachers")
            teachers_count = cursor.fetchone()['count']
            print(f"✓ جدول المعلمين: {teachers_count} سجل")
            
            # التحقق من جدول الموظفين
            cursor.execute("SELECT COUNT(*) as count FROM employees")
            employees_count = cursor.fetchone()['count']
            print(f"✓ جدول الموظفين: {employees_count} سجل")
            
        return True
        
    except Exception as e:
        print(f"✗ خطأ في قاعدة البيانات: {e}")
        return False

def test_main_window():
    """اختبار النافذة الرئيسية"""
    try:
        print("اختبار النافذة الرئيسية...")
        from app.main_window import MainWindow
        print("✓ تم استيراد النافذة الرئيسية بنجاح")
        return True
        
    except Exception as e:
        print(f"✗ خطأ في النافذة الرئيسية: {e}")
        return False

if __name__ == "__main__":
    print("=== اختبار الأقسام الجديدة ===\n")
    
    all_passed = True
    
    # اختبار الاستيرادات
    if not test_imports():
        all_passed = False
    
    print()
    
    # اختبار قاعدة البيانات
    if not test_database():
        all_passed = False
    
    print()
    
    # اختبار النافذة الرئيسية
    if not test_main_window():
        all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 جميع الاختبارات نجحت! الأقسام الجديدة جاهزة للاستخدام.")
    else:
        print("⚠️ بعض الاختبارات فشلت. راجع الأخطاء أعلاه.")
    
    input("\nاضغط Enter للمتابعة...")
