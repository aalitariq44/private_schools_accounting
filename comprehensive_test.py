#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager
import logging

def comprehensive_test():
    """اختبار شامل للنظام"""
    
    print("🔄 بدء الاختبار الشامل للنظام...")
    errors = []
    
    try:
        # 1. اختبار الاتصال بقاعدة البيانات
        print("\n1️⃣ اختبار الاتصال بقاعدة البيانات...")
        conn = db_manager.get_connection()
        if conn:
            print("✅ تم الاتصال بقاعدة البيانات بنجاح")
        else:
            errors.append("❌ فشل في الاتصال بقاعدة البيانات")
        
        # 2. اختبار هيكل الجداول
        print("\n2️⃣ اختبار هيكل الجداول...")
        
        # فحص جدول الطلاب
        print("   - فحص جدول الطلاب...")
        students_cols = db_manager.execute_query("PRAGMA table_info(students)")
        expected_student_cols = ['id', 'full_name', 'school_id', 'grade', 
                               'section', 'gender', 'phone', 'total_fee', 
                               'start_date', 'status', 'created_at', 'updated_at']
        
        actual_student_cols = [col[1] for col in students_cols]
        missing_cols = [col for col in expected_student_cols if col not in actual_student_cols]
        if missing_cols:
            errors.append(f"❌ أعمدة مفقودة في جدول الطلاب: {missing_cols}")
        else:
            print("   ✅ جدول الطلاب مكتمل")
        
        # فحص جدول الأقساط
        print("   - فحص جدول الأقساط...")
        installments_cols = db_manager.execute_query("PRAGMA table_info(installments)")
        expected_installment_cols = ['id', 'student_id', 'type', 'amount', 'due_date', 
                                   'payment_date', 'payment_time', 'paid_amount', 'status', 
                                   'notes', 'created_at']
        
        actual_installment_cols = [col[1] for col in installments_cols]
        missing_cols = [col for col in expected_installment_cols if col not in actual_installment_cols]
        if missing_cols:
            errors.append(f"❌ أعمدة مفقودة في جدول الأقساط: {missing_cols}")
        else:
            print("   ✅ جدول الأقساط مكتمل")
        
        # فحص جدول الرسوم الإضافية
        print("   - فحص جدول الرسوم الإضافية...")
        fees_cols = db_manager.execute_query("PRAGMA table_info(additional_fees)")
        expected_fee_cols = ['id', 'student_id', 'fee_type', 'amount', 'due_date', 'paid', 
                           'payment_date', 'collection_date', 'collected_amount', 'status', 
                           'notes', 'created_at', 'updated_at']
        
        actual_fee_cols = [col[1] for col in fees_cols]
        missing_cols = [col for col in expected_fee_cols if col not in actual_fee_cols]
        if missing_cols:
            errors.append(f"❌ أعمدة مفقودة في جدول الرسوم الإضافية: {missing_cols}")
        else:
            print("   ✅ جدول الرسوم الإضافية مكتمل")
        
        # 3. اختبار الاستعلامات
        print("\n3️⃣ اختبار الاستعلامات...")
        
        # استعلام الطلاب
        try:
            students_query = """
                SELECT s.id, s.name as full_name, s.national_id_number, sc.name_ar as school_name,
                       s.grade, s.academic_year, s.guardian_name, s.guardian_phone,
                       s.status, s.created_at
                FROM students s
                LEFT JOIN schools sc ON s.school_id = sc.id
                LIMIT 5
            """
            result = db_manager.execute_query(students_query)
            print("   ✅ استعلام الطلاب يعمل بنجاح")
        except Exception as e:
            errors.append(f"❌ خطأ في استعلام الطلاب: {e}")
        
        # استعلام الأقساط
        try:
            installments_query = """
                SELECT i.id, s.name as student_name, sc.name_ar as school_name,
                       i.type, i.amount, i.due_date, i.payment_date,
                       i.paid_amount, (i.amount - COALESCE(i.paid_amount, 0)) as remaining,
                       i.status, i.notes
                FROM installments i
                LEFT JOIN students s ON i.student_id = s.id
                LEFT JOIN schools sc ON s.school_id = sc.id
                LIMIT 5
            """
            result = db_manager.execute_query(installments_query)
            print("   ✅ استعلام الأقساط يعمل بنجاح")
        except Exception as e:
            errors.append(f"❌ خطأ في استعلام الأقساط: {e}")
        
        # استعلام الرسوم الإضافية
        try:
            fees_query = """
                SELECT af.id, s.name as student_name, sc.name_ar as school_name,
                       af.fee_type, af.notes, af.amount, af.created_at,
                       af.collection_date, af.collected_amount, af.status, af.notes
                FROM additional_fees af
                LEFT JOIN students s ON af.student_id = s.id
                LEFT JOIN schools sc ON s.school_id = sc.id
                LIMIT 5
            """
            result = db_manager.execute_query(fees_query)
            print("   ✅ استعلام الرسوم الإضافية يعمل بنجاح")
        except Exception as e:
            errors.append(f"❌ خطأ في استعلام الرسوم الإضافية: {e}")
        
        # 4. تلخيص النتائج
        print("\n" + "="*50)
        if not errors:
            print("🎉 تم اجتياز جميع الاختبارات بنجاح!")
            print("✅ النظام جاهز للاستخدام")
        else:
            print(f"⚠️  تم العثور على {len(errors)} مشكلة:")
            for i, error in enumerate(errors, 1):
                print(f"   {i}. {error}")
        
        return len(errors) == 0
        
    except Exception as e:
        print(f"❌ خطأ عام في الاختبار: {e}")
        return False

if __name__ == "__main__":
    comprehensive_test()
