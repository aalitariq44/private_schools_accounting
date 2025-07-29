#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار وإصلاح مشكلة نافذة طباعة الرسوم الإضافية
"""

import sys
import os
import sqlite3
from pathlib import Path

# إضافة المجلد الجذر للمشروع
sys.path.insert(0, str(Path(__file__).parent))

def create_test_student_with_fees():
    """إنشاء طالب تجريبي مع رسوم إضافية للاختبار"""
    try:
        import config
        from core.database.connection import db_manager
        
        # الاتصال بقاعدة البيانات
        print("🔍 الاتصال بقاعدة البيانات...")
        
        # البحث عن طالب موجود أو إنشاء طالب جديد
        students_query = "SELECT id, name FROM students LIMIT 1"
        students = db_manager.execute_query(students_query)
        
        if students:
            student_id = students[0][0]
            student_name = students[0][1]
            print(f"✅ تم العثور على طالب موجود: {student_name} (ID: {student_id})")
        else:
            print("❌ لم يتم العثور على طلاب في قاعدة البيانات")
            print("يرجى إضافة طالب أولاً من خلال النظام")
            return None
        
        # التحقق من الرسوم الموجودة
        existing_fees_query = "SELECT COUNT(*) FROM additional_fees WHERE student_id = ?"
        existing_count = db_manager.execute_query(existing_fees_query, (student_id,))
        existing_count = existing_count[0][0] if existing_count else 0
        
        print(f"📊 عدد الرسوم الموجودة للطالب: {existing_count}")
        
        if existing_count == 0:
            print("➕ إضافة رسوم تجريبية...")
            
            # إضافة رسوم تجريبية
            test_fees = [
                ("رسوم كتب", 50000, True, "2025-01-15", "2025-01-10", "رسوم كتب الفصل الثاني"),
                ("رسوم نشاطات", 25000, False, None, "2025-01-12", "رسوم النشاطات اللاصفية"),
                ("رسوم امتحانات", 30000, True, "2025-01-20", "2025-01-18", "رسوم امتحانات نصف السنة"),
                ("رسوم مختبر", 15000, False, None, "2025-01-22", "رسوم استخدام المختبر"),
            ]
            
            insert_query = """
                INSERT INTO additional_fees (student_id, fee_type, amount, paid, payment_date, created_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            for fee in test_fees:
                try:
                    db_manager.execute_query(insert_query, (student_id,) + fee)
                    print(f"  ✅ تم إضافة: {fee[0]} - {fee[1]:,} د.ع")
                except Exception as e:
                    print(f"  ❌ فشل في إضافة {fee[0]}: {e}")
            
            print("✅ تم إضافة الرسوم التجريبية بنجاح")
        
        # التحقق من الرسوم النهائية
        final_fees_query = """
            SELECT id, fee_type, amount, paid, payment_date, created_at, notes
            FROM additional_fees 
            WHERE student_id = ?
            ORDER BY created_at DESC
        """
        final_fees = db_manager.execute_query(final_fees_query, (student_id,))
        
        print(f"\n📋 الرسوم الإضافية للطالب {student_name}:")
        for fee in final_fees:
            status = "مدفوع" if fee[3] else "غير مدفوع"
            print(f"  • {fee[1]}: {fee[2]:,} د.ع - {status}")
        
        return student_id
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات التجريبية: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_dialog_with_qt():
    """اختبار النافذة مع Qt"""
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.pages.students.additional_fees_print_dialog import AdditionalFeesPrintDialog
        
        print("\n🔍 اختبار نافذة طباعة الرسوم الإضافية...")
        
        # إنشاء تطبيق Qt
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        # الحصول على معرف طالب تجريبي
        student_id = create_test_student_with_fees()
        if not student_id:
            print("❌ لا يوجد طالب للاختبار")
            return False
        
        # إنشاء وعرض النافذة
        dialog = AdditionalFeesPrintDialog(student_id)
        print("✅ تم إنشاء النافذة بنجاح")
        
        # عرض النافذة (غير محجوبة للاختبار)
        dialog.show()
        
        print("📱 النافذة معروضة الآن. أغلقها لإنهاء الاختبار.")
        
        # تشغيل حلقة الأحداث
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار النافذة: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 اختبار وإصلاح مشكلة نافذة طباعة الرسوم الإضافية")
    print("=" * 60)
    
    # اختبار إنشاء البيانات
    student_id = create_test_student_with_fees()
    
    if student_id:
        print(f"\n✅ تم إعداد البيانات للطالب ID: {student_id}")
        
        # عرض خيارات الاختبار
        print("\nخيارات الاختبار:")
        print("1. تشغيل النافذة مع Qt (تفاعلي)")
        print("2. اختبار تحميل البيانات فقط")
        print("3. الخروج")
        
        choice = input("\nاختر رقم الخيار (1-3): ").strip()
        
        if choice == "1":
            test_dialog_with_qt()
        elif choice == "2":
            print("\n🔍 اختبار تحميل البيانات...")
            try:
                from core.database.connection import db_manager
                query = """
                    SELECT id, fee_type, amount, paid, payment_date, created_at, notes
                    FROM additional_fees
                    WHERE student_id = ?
                    ORDER BY created_at DESC
                """
                fees_data = db_manager.execute_query(query, (student_id,))
                print(f"✅ تم تحميل {len(fees_data)} رسم بنجاح")
                for i, fee in enumerate(fees_data):
                    print(f"  {i+1}. {fee}")
            except Exception as e:
                print(f"❌ خطأ في تحميل البيانات: {e}")
        else:
            print("👋 إنهاء الاختبار")
    else:
        print("\n❌ فشل في إعداد البيانات للاختبار")
    
    print("\n" + "=" * 60)
    print("🏁 انتهى الاختبار")
