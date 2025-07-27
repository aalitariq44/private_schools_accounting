#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لصفحة الرواتب
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager

def test_salaries_table():
    """اختبار جدول الرواتب"""
    try:
        print("🔍 اختبار جدول الرواتب...")
        
        with db_manager.get_cursor() as cursor:
            # التحقق من وجود الجدول
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='salaries'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("✅ جدول الرواتب موجود")
                
                # عرض هيكل الجدول
                cursor.execute("PRAGMA table_info(salaries)")
                columns = cursor.fetchall()
                
                print("📋 أعمدة الجدول:")
                for col in columns:
                    print(f"   - {col['name']}: {col['type']}")
                
                # عدد السجلات
                cursor.execute("SELECT COUNT(*) as count FROM salaries")
                count = cursor.fetchone()['count']
                print(f"📊 عدد السجلات: {count}")
                
                # عرض آخر 5 سجلات إذا وجدت
                if count > 0:
                    cursor.execute("SELECT * FROM salaries ORDER BY created_at DESC LIMIT 5")
                    salaries = cursor.fetchall()
                    
                    print("💰 آخر الرواتب المضافة:")
                    for salary in salaries:
                        print(f"   - {salary['staff_name']} ({salary['staff_type']}): {salary['paid_amount']} دينار")
                
            else:
                print("❌ جدول الرواتب غير موجود!")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار جدول الرواتب: {e}")
        return False

def test_teachers_employees_data():
    """اختبار بيانات المعلمين والموظفين"""
    try:
        print("\n🔍 اختبار بيانات المعلمين والموظفين...")
        
        with db_manager.get_cursor() as cursor:
            # عدد المعلمين
            cursor.execute("SELECT COUNT(*) as count FROM teachers")
            teachers_count = cursor.fetchone()['count']
            print(f"👨‍🏫 عدد المعلمين: {teachers_count}")
            
            # عدد الموظفين
            cursor.execute("SELECT COUNT(*) as count FROM employees")
            employees_count = cursor.fetchone()['count']
            print(f"👷 عدد الموظفين: {employees_count}")
            
            if teachers_count > 0:
                cursor.execute("SELECT name, monthly_salary FROM teachers LIMIT 3")
                teachers = cursor.fetchall()
                print("📝 عينة من المعلمين:")
                for teacher in teachers:
                    print(f"   - {teacher['name']}: {teacher['monthly_salary']} دينار")
            
            if employees_count > 0:
                cursor.execute("SELECT name, monthly_salary FROM employees LIMIT 3")
                employees = cursor.fetchall()
                print("📝 عينة من الموظفين:")
                for employee in employees:
                    print(f"   - {employee['name']}: {employee['monthly_salary']} دينار")
                    
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار بيانات المعلمين والموظفين: {e}")
        return False

def test_database_indexes():
    """اختبار فهارس قاعدة البيانات"""
    try:
        print("\n🔍 اختبار فهارس قاعدة البيانات...")
        
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='salaries'")
            indexes = cursor.fetchall()
            
            expected_indexes = [
                'idx_salaries_staff_type',
                'idx_salaries_staff_id', 
                'idx_salaries_payment_date',
                'idx_salaries_from_date',
                'idx_salaries_to_date'
            ]
            
            found_indexes = [idx['name'] for idx in indexes if idx['name'].startswith('idx_salaries')]
            
            print("📈 الفهارس الموجودة:")
            for idx in found_indexes:
                print(f"   ✅ {idx}")
                
            missing_indexes = set(expected_indexes) - set(found_indexes)
            if missing_indexes:
                print("⚠️ فهارس مفقودة:")
                for idx in missing_indexes:
                    print(f"   ❌ {idx}")
            else:
                print("✅ جميع الفهارس موجودة")
                
        return len(missing_indexes) == 0
        
    except Exception as e:
        print(f"❌ خطأ في اختبار الفهارس: {e}")
        return False

def main():
    """الوظيفة الرئيسية للاختبار"""
    print("🚀 بدء اختبار صفحة الرواتب")
    print("=" * 50)
    
    # تهيئة قاعدة البيانات
    try:
        db_manager.initialize_database()
        print("✅ تم تهيئة قاعدة البيانات")
    except Exception as e:
        print(f"❌ فشل في تهيئة قاعدة البيانات: {e}")
        return
    
    # تشغيل الاختبارات
    tests = [
        test_salaries_table(),
        test_teachers_employees_data(),
        test_database_indexes()
    ]
    
    print("\n" + "=" * 50)
    print("📊 نتائج الاختبار:")
    
    passed = sum(tests)
    total = len(tests)
    
    if passed == total:
        print(f"🎉 نجحت جميع الاختبارات ({passed}/{total})")
        print("✅ صفحة الرواتب جاهزة للاستخدام!")
    else:
        print(f"⚠️ نجح {passed} من {total} اختبارات")
        print("❌ يرجى مراجعة الأخطاء أعلاه")

if __name__ == "__main__":
    main()
