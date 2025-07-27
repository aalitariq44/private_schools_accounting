#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط لقاعدة البيانات والوظائف الأساسية
"""

import sys
import os
import logging
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

import config
from core.utils.logger import setup_logging
from core.database.connection import DatabaseManager
from core.auth.login_manager import AuthManager


def test_database():
    """اختبار قاعدة البيانات"""
    print("🔍 اختبار قاعدة البيانات...")
    
    try:
        db_manager = DatabaseManager()
        
        # تهيئة قاعدة البيانات
        if db_manager.initialize_database():
            print("✅ تم إعداد قاعدة البيانات بنجاح")
        else:
            print("❌ فشل في إعداد قاعدة البيانات")
            return False
        
        # اختبار الاتصال
        result = db_manager.execute_query("SELECT 1 as test")
        if result and result[0]['test'] == 1:
            print("✅ اتصال قاعدة البيانات يعمل بشكل صحيح")
        else:
            print("❌ مشكلة في اتصال قاعدة البيانات")
            return False
        
        # اختبار الجداول
        tables = ['users', 'schools', 'students', 'installments', 'additional_fees']
        for table in tables:
            try:
                result = db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                count = result[0]['count'] if result else 0
                print(f"  📊 جدول {table}: {count} سجل")
            except Exception as e:
                print(f"  ❌ خطأ في جدول {table}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار قاعدة البيانات: {e}")
        return False


def test_authentication():
    """اختبار نظام المصادقة"""
    print("\n🔐 اختبار نظام المصادقة...")
    
    try:
        auth_manager = AuthManager()
        
        # التحقق من وجود مستخدمين
        has_users = auth_manager.has_users()
        print(f"  👥 يوجد مستخدمين في النظام: {'نعم' if has_users else 'لا'}")
        
        if not has_users:
            # إنشاء مستخدم تجريبي
            test_password = "123456"
            if auth_manager.create_first_user(test_password):
                print("✅ تم إنشاء المستخدم التجريبي بنجاح")
                
                # اختبار المصادقة
                if auth_manager.authenticate("admin", test_password):
                    print("✅ تم تسجيل الدخول بنجاح")
                    
                    # اختبار معلومات الجلسة
                    session_info = auth_manager.get_session_info()
                    if session_info:
                        print(f"  📝 معلومات الجلسة: {session_info['user']['username']}")
                    
                    # تسجيل خروج
                    auth_manager.logout()
                    print("✅ تم تسجيل الخروج بنجاح")
                    
                    return True
                else:
                    print("❌ فشل في تسجيل الدخول")
                    return False
            else:
                print("❌ فشل في إنشاء المستخدم التجريبي")
                return False
        else:
            print("  ℹ️ يوجد مستخدمين في النظام مسبقاً")
            return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار المصادقة: {e}")
        return False


def test_schools_operations():
    """اختبار عمليات المدارس"""
    print("\n🏫 اختبار عمليات المدارس...")
    
    try:
        db_manager = DatabaseManager()
        
        # إضافة مدرسة تجريبية
        school_data = {
            'name_ar': 'مدرسة الاختبار الأهلية',
            'name_en': 'Test Private School',
            'address': 'بغداد - الكرادة',
            'phone': '07901234567',
            'principal_name': 'أحمد محمد علي',
            'school_types': '["ابتدائية", "متوسطة"]'
        }
        
        insert_query = """
            INSERT INTO schools (name_ar, name_en, address, phone, principal_name, school_types)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        school_id = db_manager.execute_insert(
            insert_query,
            (school_data['name_ar'], school_data['name_en'], school_data['address'],
             school_data['phone'], school_data['principal_name'], school_data['school_types'])
        )
        
        if school_id:
            print(f"✅ تم إضافة مدرسة تجريبية بالمعرف: {school_id}")
            
            # استعلام المدرسة
            select_query = "SELECT * FROM schools WHERE id = ?"
            result = db_manager.execute_query(select_query, (school_id,))
            
            if result:
                school = result[0]
                print(f"  📝 الاسم: {school['name_ar']}")
                print(f"  📞 الهاتف: {school['phone']}")
                print(f"  👨‍💼 المدير: {school['principal_name']}")
                
                # تحديث المدرسة
                update_query = "UPDATE schools SET phone = ? WHERE id = ?"
                updated_rows = db_manager.execute_update(update_query, ("07909876543", school_id))
                
                if updated_rows > 0:
                    print("✅ تم تحديث المدرسة بنجاح")
                
                return True
            else:
                print("❌ لم يتم العثور على المدرسة المضافة")
                return False
        else:
            print("❌ فشل في إضافة المدرسة")
            return False
        
    except Exception as e:
        print(f"❌ خطأ في اختبار عمليات المدارس: {e}")
        return False


def test_students_operations():
    """اختبار عمليات الطلاب"""
    print("\n👨‍🎓 اختبار عمليات الطلاب...")
    
    try:
        db_manager = DatabaseManager()
        
        # البحث عن مدرسة للطالب
        schools_query = "SELECT id FROM schools LIMIT 1"
        schools_result = db_manager.execute_query(schools_query)
        
        if not schools_result:
            print("❌ لا توجد مدارس لإضافة طالب")
            return False
        
        school_id = schools_result[0]['id']
        
        # إضافة طالب تجريبي
        student_data = {
            'full_name': 'علي أحمد محمد',
            'school_id': school_id,
            'grade': 'الأول الابتدائي',
            'section': 'أ',
            'gender': 'ذكر',
            'phone': '07801234567',
            'total_fee': 1500000.0,  # 1,500,000 دينار
            'start_date': '2024-09-01'
        }
        
        insert_query = """
            INSERT INTO students (full_name, school_id, grade, section, gender, phone, total_fee, start_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        student_id = db_manager.execute_insert(
            insert_query,
            (student_data['name'], student_data['school_id'], student_data['grade'],
             student_data['section'], student_data['gender'], student_data['phone'],
             student_data['total_fee'], student_data['start_date'])
        )
        
        if student_id:
            print(f"✅ تم إضافة طالب تجريبي بالمعرف: {student_id}")
            
            # إضافة قسط للطالب
            installment_data = {
                'student_id': student_id,
                'amount': 500000.0,  # 500,000 دينار
                'payment_date': '2024-09-15',
                'payment_time': '10:30:00'
            }
            
            installment_query = """
                INSERT INTO installments (student_id, amount, payment_date, payment_time)
                VALUES (?, ?, ?, ?)
            """
            
            installment_id = db_manager.execute_insert(
                installment_query,
                (installment_data['student_id'], installment_data['amount'],
                 installment_data['payment_date'], installment_data['payment_time'])
            )
            
            if installment_id:
                print(f"✅ تم إضافة قسط بالمعرف: {installment_id}")
                
                # حساب المتبقي
                remaining = student_data['total_fee'] - installment_data['amount']
                print(f"  💰 القسط الكلي: {student_data['total_fee']:,.0f} د.ع")
                print(f"  💸 المدفوع: {installment_data['amount']:,.0f} د.ع")
                print(f"  📊 المتبقي: {remaining:,.0f} د.ع")
                
                return True
            else:
                print("❌ فشل في إضافة القسط")
                return False
        else:
            print("❌ فشل في إضافة الطالب")
            return False
        
    except Exception as e:
        print(f"❌ خطأ في اختبار عمليات الطلاب: {e}")
        return False


def test_statistics():
    """اختبار الإحصائيات"""
    print("\n📊 اختبار الإحصائيات...")
    
    try:
        db_manager = DatabaseManager()
        
        # إحصائيات المدارس
        schools_query = "SELECT COUNT(*) as count FROM schools"
        schools_result = db_manager.execute_query(schools_query)
        schools_count = schools_result[0]['count'] if schools_result else 0
        
        # إحصائيات الطلاب
        students_query = "SELECT COUNT(*) as count FROM students"
        students_result = db_manager.execute_query(students_query)
        students_count = students_result[0]['count'] if students_result else 0
        
        # إحصائيات الأقساط
        total_fees_query = "SELECT SUM(total_fee) as total FROM students"
        total_fees_result = db_manager.execute_query(total_fees_query)
        total_fees = total_fees_result[0]['total'] if total_fees_result and total_fees_result[0]['total'] else 0
        
        paid_fees_query = "SELECT SUM(amount) as total FROM installments"
        paid_fees_result = db_manager.execute_query(paid_fees_query)
        paid_fees = paid_fees_result[0]['total'] if paid_fees_result and paid_fees_result[0]['total'] else 0
        
        remaining_fees = total_fees - paid_fees
        
        # عرض الإحصائيات
        print(f"  🏫 عدد المدارس: {schools_count}")
        print(f"  👨‍🎓 عدد الطلاب: {students_count}")
        print(f"  💰 إجمالي الأقساط: {total_fees:,.0f} د.ع")
        print(f"  💸 المبالغ المدفوعة: {paid_fees:,.0f} د.ع")
        print(f"  📊 المبالغ المتبقية: {remaining_fees:,.0f} د.ع")
        
        print("✅ تم حساب الإحصائيات بنجاح")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار الإحصائيات: {e}")
        return False


def main():
    """الدالة الرئيسية للاختبار"""
    print("🚀 بدء اختبار نظام حسابات المدارس الأهلية")
    print("=" * 60)
    
    try:
        # إعداد نظام التسجيل
        setup_logging()
        
        # اختبار قاعدة البيانات
        if not test_database():
            print("\n❌ فشل اختبار قاعدة البيانات")
            return 1
        
        # اختبار المصادقة
        if not test_authentication():
            print("\n❌ فشل اختبار المصادقة")
            return 1
        
        # اختبار عمليات المدارس
        if not test_schools_operations():
            print("\n❌ فشل اختبار عمليات المدارس")
            return 1
        
        # اختبار عمليات الطلاب
        if not test_students_operations():
            print("\n❌ فشل اختبار عمليات الطلاب")
            return 1
        
        # اختبار الإحصائيات
        if not test_statistics():
            print("\n❌ فشل اختبار الإحصائيات")
            return 1
        
        print("\n" + "=" * 60)
        print("🎉 تم اجتياز جميع الاختبارات بنجاح!")
        print("✅ النظام جاهز للاستخدام")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ خطأ عام في الاختبار: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    input("\nاضغط Enter للخروج...")
    sys.exit(exit_code)
