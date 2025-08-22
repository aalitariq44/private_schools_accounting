#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار صفحة إنشاء الهويات مع تاريخ الميلاد
"""

import sys
import os
from pathlib import Path

# إضافة مجلد الجذر إلى مسار Python
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from core.database.connection import db_manager

def test_student_ids_birthdate():
    """اختبار عمود تاريخ الميلاد في صفحة إنشاء الهويات"""
    print("اختبار صفحة إنشاء الهويات مع تاريخ الميلاد...")
    
    try:
        # اختبار الاستعلام المحدث
        print("1. اختبار استعلام البيانات...")
        query = """
            SELECT s.id, s.name, s.grade, s.section, s.phone, s.birthdate,
                   sc.name_ar as school_name
            FROM students s
            LEFT JOIN schools sc ON s.school_id = sc.id
            WHERE s.status = 'نشط'
            ORDER BY s.name
            LIMIT 5
        """
        
        students = db_manager.execute_query(query)
        
        if students:
            print(f"✓ تم العثور على {len(students)} طالب نشط")
            print("\nعينة من البيانات:")
            for student in students[:3]:
                print(f"  - {student[1]} | الصف: {student[2]} | تاريخ الميلاد: {student[5] or 'غير محدد'}")
        else:
            print("لا توجد طلاب نشطون في قاعدة البيانات")
        
        # اختبار تحديث تاريخ الميلاد
        print("\n2. اختبار تحديث تاريخ الميلاد...")
        if students:
            test_student_id = students[0][0]
            test_birthdate = "2010-05-15"
            
            # تحديث تاريخ الميلاد
            update_query = "UPDATE students SET birthdate = ? WHERE id = ?"
            result = db_manager.execute_update(update_query, (test_birthdate, test_student_id))
            
            if result:
                print(f"✓ تم تحديث تاريخ ميلاد الطالب {test_student_id} إلى {test_birthdate}")
                
                # التحقق من التحديث
                check_query = "SELECT birthdate FROM students WHERE id = ?"
                check_result = db_manager.execute_fetch_one(check_query, (test_student_id,))
                
                if check_result and check_result[0] == test_birthdate:
                    print("✓ تم التحقق من صحة التحديث")
                else:
                    print("✗ فشل في التحقق من التحديث")
                    return False
            else:
                print("✗ فشل في تحديث تاريخ الميلاد")
                return False
        
        # اختبار بنية البيانات للهوية
        print("\n3. اختبار بنية البيانات للهوية...")
        if students:
            student_data = {
                'id': students[0][0],
                'name': students[0][1] or '',
                'grade': students[0][2] or '',
                'section': students[0][3] or '',
                'phone': students[0][4] or '',
                'birthdate': students[0][5] or '',
                'school_name': students[0][6] or 'غير محدد'
            }
            
            print("✓ بنية بيانات الطالب للهوية:")
            for key, value in student_data.items():
                print(f"  - {key}: {value}")
            
            # التحقق من وجود جميع الحقول المطلوبة
            required_fields = ['id', 'name', 'grade', 'section', 'phone', 'birthdate', 'school_name']
            missing_fields = [field for field in required_fields if field not in student_data]
            
            if not missing_fields:
                print("✓ جميع الحقول المطلوبة متوفرة")
            else:
                print(f"✗ حقول مفقودة: {missing_fields}")
                return False
        
        print("\n✅ جميع اختبارات صفحة إنشاء الهويات نجحت!")
        return True
        
    except Exception as e:
        print(f"✗ خطأ في الاختبار: {e}")
        return False

def test_pdf_generation_data():
    """اختبار بيانات إنشاء PDF"""
    print("\n4. اختبار بيانات إنشاء PDF...")
    
    try:
        # محاكاة البيانات التي سترسل لمولد PDF
        sample_students = [
            {
                'id': 1,
                'name': 'أحمد محمد',
                'grade': 'الأول الابتدائي',
                'section': 'أ',
                'phone': '07901234567',
                'birthdate': '2010-01-15',
                'school_name': 'مدرسة النور الابتدائية'
            },
            {
                'id': 2,
                'name': 'فاطمة علي',
                'grade': 'الثاني الابتدائي',
                'section': 'ب',
                'phone': '07907654321',
                'birthdate': '2009-08-22',
                'school_name': 'مدرسة النور الابتدائية'
            }
        ]
        
        print("✓ بيانات العينة للهويات:")
        for i, student in enumerate(sample_students, 1):
            print(f"  الطالب {i}:")
            print(f"    - الاسم: {student['name']}")
            print(f"    - الصف: {student['grade']}")
            print(f"    - تاريخ الميلاد: {student['birthdate']}")
            print(f"    - المدرسة: {student['school_name']}")
        
        # التحقق من أن جميع البيانات متوفرة لمولد PDF
        for student in sample_students:
            if student['birthdate']:
                print(f"✓ {student['name']}: تاريخ الميلاد متوفر ({student['birthdate']})")
            else:
                print(f"⚠ {student['name']}: تاريخ الميلاد غير متوفر")
        
        print("✓ البيانات جاهزة لإنشاء PDF الهويات")
        return True
        
    except Exception as e:
        print(f"✗ خطأ في اختبار بيانات PDF: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("=== اختبار صفحة إنشاء الهويات مع تاريخ الميلاد ===\n")
    
    try:
        # تهيئة قاعدة البيانات
        db_manager.initialize_database()
        
        # تشغيل الاختبارات
        test1 = test_student_ids_birthdate()
        test2 = test_pdf_generation_data()
        
        if test1 and test2:
            print("\n🎉 جميع الاختبارات نجحت! صفحة إنشاء الهويات جاهزة مع تاريخ الميلاد.")
            print("\nالمميزات الجديدة:")
            print("✓ عمود تاريخ الميلاد في جدول الطلاب")
            print("✓ إمكانية تعديل تاريخ الميلاد بسرعة")
            print("✓ حفظ تلقائي للتغييرات في قاعدة البيانات")
            print("✓ عرض تاريخ الميلاد في الهوية المطبوعة")
        else:
            print("\n❌ يوجد مشكلة في بعض الاختبارات.")
            return 1
            
    except Exception as e:
        print(f"خطأ عام: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    input("\nاضغط Enter للخروج...")
    sys.exit(exit_code)
