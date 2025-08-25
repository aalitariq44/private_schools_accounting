#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار قاعدة البيانات بعد الإصلاح
"""

import sys
from pathlib import Path
import logging
from datetime import datetime, date

# إضافة المسار الجذر للمشروع
sys.path.insert(0, str(Path(__file__).parent))

from core.database.connection import db_manager

# إعداد نظام التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_external_income():
    """اختبار إضافة إيراد خارجي"""
    try:
        print("🧪 اختبار إضافة إيراد خارجي...")
        
        # الحصول على أول مدرسة
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT id FROM schools LIMIT 1")
            school = cursor.fetchone()
            
            if not school:
                print("❌ لا توجد مدارس في قاعدة البيانات")
                return False
                
            school_id = school[0]
            
            # إضافة إيراد خارجي جديد
            cursor.execute("""
                INSERT INTO external_income (
                    school_id, title, amount, category, income_type, 
                    description, income_date, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                school_id,
                "إيراد تجريبي",
                1000.00,
                "إيرادات متنوعة",
                "نقدي",
                "هذا إيراد تجريبي للاختبار",
                date.today(),
                "ملاحظات تجريبية"
            ))
            
            income_id = cursor.lastrowid
            print(f"✅ تم إضافة إيراد خارجي برقم: {income_id}")
            
            # التحقق من الإضافة
            cursor.execute("SELECT * FROM external_income WHERE id = ?", (income_id,))
            income = cursor.fetchone()
            if income:
                print(f"   العنوان: {income['title']}")
                print(f"   المبلغ: {income['amount']}")
                print(f"   النوع: {income['category']}")
                return True
            else:
                print("❌ لم يتم العثور على الإيراد المضاف")
                return False
                
    except Exception as e:
        print(f"❌ خطأ في اختبار الإيراد الخارجي: {e}")
        return False

def test_expenses():
    """اختبار إضافة مصروف"""
    try:
        print("🧪 اختبار إضافة مصروف...")
        
        # الحصول على أول مدرسة
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT id FROM schools LIMIT 1")
            school = cursor.fetchone()
            
            if not school:
                print("❌ لا توجد مدارس في قاعدة البيانات")
                return False
                
            school_id = school[0]
            
            # إضافة مصروف جديد
            cursor.execute("""
                INSERT INTO expenses (
                    school_id, expense_type, amount, expense_date, 
                    description, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                school_id,
                "مصروف تجريبي",
                500.00,
                date.today(),
                "هذا مصروف تجريبي للاختبار",
                "ملاحظات تجريبية"
            ))
            
            expense_id = cursor.lastrowid
            print(f"✅ تم إضافة مصروف برقم: {expense_id}")
            
            # التحقق من الإضافة
            cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
            expense = cursor.fetchone()
            if expense:
                print(f"   النوع: {expense['expense_type']}")
                print(f"   المبلغ: {expense['amount']}")
                print(f"   التاريخ: {expense['expense_date']}")
                return True
            else:
                print("❌ لم يتم العثور على المصروف المضاف")
                return False
                
    except Exception as e:
        print(f"❌ خطأ في اختبار المصروف: {e}")
        return False

def test_students():
    """اختبار إضافة طالب"""
    try:
        print("🧪 اختبار إضافة طالب...")
        
        # الحصول على أول مدرسة
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT id FROM schools LIMIT 1")
            school = cursor.fetchone()
            
            if not school:
                print("❌ لا توجد مدارس في قاعدة البيانات")
                return False
                
            school_id = school[0]
            
            # إضافة طالب جديد
            cursor.execute("""
                INSERT INTO students (
                    name, school_id, grade, section, gender, 
                    total_fee, start_date, academic_year
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "أحمد محمد علي",
                school_id,
                "الصف الأول",
                "أ",
                "ذكر",
                2000.00,
                date.today(),
                "2024-2025"
            ))
            
            student_id = cursor.lastrowid
            print(f"✅ تم إضافة طالب برقم: {student_id}")
            
            # التحقق من الإضافة
            cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
            student = cursor.fetchone()
            if student:
                print(f"   الاسم: {student['name']}")
                print(f"   الصف: {student['grade']}")
                print(f"   الشعبة: {student['section']}")
                return True
            else:
                print("❌ لم يتم العثور على الطالب المضاف")
                return False
                
    except Exception as e:
        print(f"❌ خطأ في اختبار الطالب: {e}")
        return False

def test_installments():
    """اختبار إضافة قسط"""
    try:
        print("🧪 اختبار إضافة قسط...")
        
        # الحصول على أول طالب
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT id FROM students LIMIT 1")
            student = cursor.fetchone()
            
            if not student:
                print("❌ لا يوجد طلاب في قاعدة البيانات")
                return False
                
            student_id = student[0]
            
            # إضافة قسط جديد
            cursor.execute("""
                INSERT INTO installments (
                    student_id, amount, payment_date, payment_time, notes
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                student_id,
                500.00,
                date.today(),
                datetime.now().strftime('%H:%M:%S'),  # تحويل الوقت إلى نص
                "قسط تجريبي"
            ))
            
            installment_id = cursor.lastrowid
            print(f"✅ تم إضافة قسط برقم: {installment_id}")
            
            # التحقق من الإضافة
            cursor.execute("SELECT * FROM installments WHERE id = ?", (installment_id,))
            installment = cursor.fetchone()
            if installment:
                print(f"   المبلغ: {installment['amount']}")
                print(f"   التاريخ: {installment['payment_date']}")
                return True
            else:
                print("❌ لم يتم العثور على القسط المضاف")
                return False
                
    except Exception as e:
        print(f"❌ خطأ في اختبار القسط: {e}")
        return False

def show_database_summary():
    """عرض ملخص قاعدة البيانات"""
    try:
        print("\n📊 ملخص قاعدة البيانات:")
        print("=" * 40)
        
        with db_manager.get_cursor() as cursor:
            # عدد المدارس
            cursor.execute("SELECT COUNT(*) FROM schools")
            schools_count = cursor.fetchone()[0]
            print(f"🏫 المدارس: {schools_count}")
            
            # عدد الطلاب
            cursor.execute("SELECT COUNT(*) FROM students")
            students_count = cursor.fetchone()[0]
            print(f"👨‍🎓 الطلاب: {students_count}")
            
            # عدد الأقساط
            cursor.execute("SELECT COUNT(*) FROM installments")
            installments_count = cursor.fetchone()[0]
            print(f"💰 الأقساط: {installments_count}")
            
            # عدد الإيرادات الخارجية
            cursor.execute("SELECT COUNT(*) FROM external_income")
            income_count = cursor.fetchone()[0]
            print(f"📈 الإيرادات الخارجية: {income_count}")
            
            # عدد المصروفات
            cursor.execute("SELECT COUNT(*) FROM expenses")
            expenses_count = cursor.fetchone()[0]
            print(f"📉 المصروفات: {expenses_count}")
            
            # عدد المستخدمين
            cursor.execute("SELECT COUNT(*) FROM users")
            users_count = cursor.fetchone()[0]
            print(f"👤 المستخدمين: {users_count}")
            
    except Exception as e:
        print(f"❌ خطأ في عرض ملخص قاعدة البيانات: {e}")

def main():
    """الدالة الرئيسية للاختبار"""
    print("🧪 اختبار قاعدة البيانات بعد الإصلاح")
    print("=" * 50)
    
    tests = [
        test_external_income,
        test_expenses,
        test_students,
        test_installments
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
            print()  # سطر فارغ بين الاختبارات
        except Exception as e:
            print(f"❌ خطأ في تنفيذ الاختبار: {e}")
            print()
    
    # عرض النتائج
    print("📋 نتائج الاختبارات:")
    print(f"   ✅ نجح: {passed_tests}")
    print(f"   ❌ فشل: {total_tests - passed_tests}")
    print(f"   📊 النسبة: {(passed_tests / total_tests) * 100:.1f}%")
    
    # عرض ملخص قاعدة البيانات
    show_database_summary()
    
    if passed_tests == total_tests:
        print("\n🎉 جميع الاختبارات نجحت! قاعدة البيانات تعمل بشكل صحيح.")
        return True
    else:
        print(f"\n⚠️  فشل {total_tests - passed_tests} اختبار من أصل {total_tests}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✨ اختبار قاعدة البيانات مكتمل بنجاح!")
        else:
            print("\n💥 هناك مشاكل في قاعدة البيانات تحتاج لإصلاح!")
    except Exception as e:
        print(f"\n💥 خطأ عام في الاختبار: {e}")
        sys.exit(1)
