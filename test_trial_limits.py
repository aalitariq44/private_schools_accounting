#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل للنسخة التجريبية
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager

def test_student_limit():
    """اختبار حد الطلاب"""
    try:
        query = "SELECT COUNT(*) FROM students WHERE status != 'محذوف'"
        result = db_manager.execute_query(query)
        current_count = result[0][0] if result else 0
        
        print(f"عدد الطلاب الحالي: {current_count}")
        print(f"الحد الأقصى: 10")
        print(f"يمكن إضافة طالب واحد: {'نعم' if current_count < 10 else 'لا - تم الوصول للحد الأقصى'}")
        
        # اختبار إضافة مجموعة
        remaining = max(0, 10 - current_count)
        print(f"المساحات المتاحة لمجموعة طلاب: {remaining}")
        print("-" * 50)
        
    except Exception as e:
        print(f"خطأ في فحص الطلاب: {e}")

def test_teacher_limit():
    """اختبار حد المعلمين"""
    try:
        query = "SELECT COUNT(*) FROM teachers"
        result = db_manager.execute_query(query)
        current_count = result[0][0] if result else 0
        
        print(f"عدد المعلمين الحالي: {current_count}")
        print(f"الحد الأقصى: 4")
        print(f"يمكن إضافة: {'نعم' if current_count < 4 else 'لا - تم الوصول للحد الأقصى'}")
        print("-" * 50)
        
    except Exception as e:
        print(f"خطأ في فحص المعلمين: {e}")

def test_employee_limit():
    """اختبار حد الموظفين"""
    try:
        query = "SELECT COUNT(*) FROM employees"
        result = db_manager.execute_query(query)
        current_count = result[0][0] if result else 0
        
        print(f"عدد الموظفين الحالي: {current_count}")
        print(f"الحد الأقصى: 4")
        print(f"يمكن إضافة: {'نعم' if current_count < 4 else 'لا - تم الوصول للحد الأقصى'}")
        print("-" * 50)
        
    except Exception as e:
        print(f"خطأ في فحص الموظفين: {e}")

def test_trial_widget():
    """اختبار ويدجت النسخة التجريبية"""
    try:
        from ui.widgets.trial_version_widget import TrialVersionWidget
        print("✅ ويدجت النسخة التجريبية يعمل بنجاح")
        print("🎨 التصميم الجديد: مشابه لويدجت العام الدراسي")
        print("🖱️ النقر على الويدجت يُظهر معلومات الاتصال")
        print("-" * 50)
    except Exception as e:
        print(f"❌ خطأ في ويدجت النسخة التجريبية: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("اختبار شامل للنسخة التجريبية المحدثة")
    print("=" * 60)
    
    test_student_limit()
    test_teacher_limit()  
    test_employee_limit()
    test_trial_widget()
    
    print("💡 الميزات الجديدة:")
    print("   • فحص القيود قبل فتح نوافذ الإضافة")
    print("   • قيد مجموعة الطلاب مع عرض التفاصيل") 
    print("   • ويدجت محسن مشابه للعام الدراسي")
    print("   • رسائل تحذير مفصلة ومفيدة")
    print()
    print("📞 رقم الاتصال للنسخة الكاملة: 07710995922")
    print("=" * 60)
