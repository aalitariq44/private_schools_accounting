#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع للنظام المحدث
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """اختبار استيراد الوحدات الجديدة"""
    try:
        print("اختبار استيراد الوحدات الجديدة...")
        
        # اختبار استيراد نوافذ المدارس
        from ui.pages.schools.add_school_dialog import AddSchoolDialog
        from ui.pages.schools.edit_school_dialog import EditSchoolDialog
        print("نوافذ المدارس - تم بنجاح")
        
        # اختبار استيراد صفحة الطلاب
        from ui.pages.students.students_page import StudentsPage
        print("صفحة الطلاب - تم بنجاح")
        
        # اختبار استيراد صفحة الأقساط
        from ui.pages.installments.installments_page import InstallmentsPage
        print("صفحة الأقساط - تم بنجاح")
        
        # اختبار استيراد صفحة الرسوم الإضافية
        from ui.pages.additional_fees.additional_fees_page import AdditionalFeesPage
        print("صفحة الرسوم الإضافية - تم بنجاح")
        
        return True
        
    except Exception as e:
        print(f"خطأ في الاستيراد: {e}")
        return False

def test_database_structure():
    """اختبار هيكل قاعدة البيانات"""
    try:
        print("اختبار هيكل قاعدة البيانات...")
        
        from core.database.connection import db_manager
        
        # التحقق من وجود الجداول
        tables = ["users", "schools", "students", "installments", "additional_fees", "app_settings"]
        
        for table in tables:
            query = f"SELECT COUNT(*) FROM {table}"
            result = db_manager.execute_query(query)
            if result is not None:
                print(f"جدول {table} - موجود")
            else:
                print(f"جدول {table} - غير موجود")
                return False
        
        return True
        
    except Exception as e:
        print(f"خطأ في قاعدة البيانات: {e}")
        return False

def main():
    """تشغيل الاختبارات"""
    print("اختبار سريع لنظام حسابات المدارس الأهلية المحدث")
    print("=" * 60)
    
    success = True
    
    # اختبار الاستيراد
    if not test_imports():
        success = False
    
    print()
    
    # اختبار قاعدة البيانات
    if not test_database_structure():
        success = False
    
    print()
    print("=" * 60)
    
    if success:
        print("جميع الاختبارات نجحت! النظام جاهز للاستخدام")
        print("\nالميزات المضافة:")
        print("   - نوافذ إضافة وتعديل المدارس مع رفع الشعارات")
        print("   - صفحة إدارة الطلاب مع الفلاتر والبحث")
        print("   - صفحة إدارة الأقساط مع الملخص المالي")
        print("   - صفحة إدارة الرسوم الإضافية مع التصنيف")
        print("\nللتطوير اللاحق:")
        print("   - نوافذ إضافة وتعديل الطلاب")
        print("   - نوافذ إدارة الأقساط والمدفوعات")
        print("   - نظام التقارير المالية")
    else:
        print("فشل في بعض الاختبارات")
    
    print("\nلتشغيل النظام:")
    print("python main.py")

if __name__ == "__main__":
    main()
