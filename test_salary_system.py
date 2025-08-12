#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار إضافة راتب
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.database.connection import db_manager
from datetime import datetime, date
import logging

# إعداد نظام التسجيل
logging.basicConfig(level=logging.INFO)

def test_add_salary():
    """اختبار إضافة راتب"""
    try:
        # البحث عن معلم موجود
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM teachers LIMIT 1")
            teacher = cursor.fetchone()
            
            if not teacher:
                print("❌ لا يوجد معلمين في قاعدة البيانات")
                return False
            
            print(f"✅ تم العثور على المعلم: {teacher['name']}")
            print(f"   الراتب المسجل: {teacher['monthly_salary']} دينار")
            
            # إضافة راتب تجريبي
            test_salary_data = {
                'staff_type': 'teacher',
                'staff_id': teacher['id'],
                'staff_name': teacher['name'],
                'base_salary': teacher['monthly_salary'],
                'paid_amount': teacher['monthly_salary'],
                'from_date': '2024-01-01',
                'to_date': '2024-01-31',
                'days_count': 31,
                'payment_date': '2024-01-31',
                'payment_time': '14:30:00',
                'notes': 'راتب تجريبي للاختبار'
            }
            
            print("جاري إضافة راتب تجريبي...")
            cursor.execute("""
                INSERT INTO salaries 
                (staff_type, staff_id, staff_name, base_salary, paid_amount, 
                 from_date, to_date, days_count, payment_date, payment_time, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_salary_data['staff_type'],
                test_salary_data['staff_id'],
                test_salary_data['staff_name'],
                test_salary_data['base_salary'],
                test_salary_data['paid_amount'],
                test_salary_data['from_date'],
                test_salary_data['to_date'],
                test_salary_data['days_count'],
                test_salary_data['payment_date'],
                test_salary_data['payment_time'],
                test_salary_data['notes']
            ))
            
            salary_id = cursor.lastrowid
            print(f"✅ تم إضافة الراتب بنجاح! رقم الراتب: {salary_id}")
            
            # التحقق من البيانات المُضافة
            cursor.execute("SELECT * FROM salaries WHERE id = ?", (salary_id,))
            saved_salary = cursor.fetchone()
            
            print("البيانات المحفوظة:")
            print(f"  - النوع: {saved_salary['staff_type']}")
            print(f"  - الاسم: {saved_salary['staff_name']}")
            print(f"  - الراتب الأساسي: {saved_salary['base_salary']}")
            print(f"  - المبلغ المدفوع: {saved_salary['paid_amount']}")
            print(f"  - فترة الراتب: {saved_salary['from_date']} إلى {saved_salary['to_date']}")
            print(f"  - عدد الأيام: {saved_salary['days_count']}")
            print(f"  - تاريخ الدفع: {saved_salary['payment_date']}")
            print(f"  - الملاحظات: {saved_salary['notes']}")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في اختبار إضافة الراتب: {e}")
        return False

def show_all_salaries():
    """عرض جميع الرواتب المحفوظة"""
    try:
        with db_manager.get_cursor() as cursor:
            cursor.execute("""
                SELECT s.*, 
                       CASE s.staff_type 
                           WHEN 'teacher' THEN 'معلم'
                           WHEN 'employee' THEN 'موظف'
                           ELSE s.staff_type
                       END as staff_type_ar
                FROM salaries s
                ORDER BY s.payment_date DESC, s.created_at DESC
            """)
            salaries = cursor.fetchall()
            
            print(f"\n📊 إجمالي الرواتب المحفوظة: {len(salaries)}")
            
            if salaries:
                print("\nقائمة الرواتب:")
                for i, salary in enumerate(salaries, 1):
                    print(f"  {i}. {salary['staff_name']} ({salary['staff_type_ar']})")
                    print(f"     المبلغ: {salary['paid_amount']} دينار")
                    print(f"     تاريخ الدفع: {salary['payment_date']}")
                    print(f"     الفترة: {salary['from_date']} إلى {salary['to_date']}")
                    print()
            else:
                print("لا توجد رواتب محفوظة")
                
    except Exception as e:
        print(f"❌ خطأ في عرض الرواتب: {e}")

if __name__ == "__main__":
    print('🧪 اختبار نظام الرواتب...')
    print('=' * 50)
    
    success = test_add_salary()
    
    if success:
        print('\n✅ نجح اختبار إضافة الراتب!')
    else:
        print('\n❌ فشل اختبار إضافة الراتب!')
    
    print('\n' + '=' * 50)
    show_all_salaries()
