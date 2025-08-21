#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار ميزة ملاحظات الطالب
"""
import logging
from core.database.connection import db_manager

logging.basicConfig(level=logging.INFO)

def test_student_notes_feature():
    """اختبار ميزة ملاحظات الطالب"""
    try:
        print("🧪 اختبار ميزة ملاحظات الطالب")
        print("=" * 50)
        
        # فحص بنية الجدول
        print("1️⃣ فحص بنية جدول الطلاب...")
        columns_info = db_manager.execute_query('PRAGMA table_info(students)')
        notes_column_exists = any(column[1] == 'notes' for column in columns_info)
        
        if notes_column_exists:
            print("✅ عمود الملاحظات موجود")
        else:
            print("❌ عمود الملاحظات غير موجود")
            return False
        
        # فحص الطلاب الموجودين
        print("\n2️⃣ فحص الطلاب الموجودين...")
        students = db_manager.execute_query("SELECT id, name, notes FROM students LIMIT 5")
        
        if students:
            print(f"📊 تم العثور على {len(students)} طالب/طلاب:")
            for student in students:
                student_id, name, notes = student
                notes_preview = (notes[:30] + "...") if notes and len(notes) > 30 else (notes or "بدون ملاحظات")
                print(f"   👤 {name} (#{student_id}) - {notes_preview}")
        else:
            print("⚠️ لا توجد بيانات طلاب للاختبار")
            return True
        
        # اختبار تحديث الملاحظات
        print("\n3️⃣ اختبار تحديث الملاحظات...")
        first_student = students[0]
        student_id = first_student[0]
        test_note = "ملاحظة اختبار - تم التحديث في " + str(db_manager.execute_query("SELECT datetime('now', 'localtime')")[0][0])
        
        # تحديث الملاحظات
        success = db_manager.execute_query(
            "UPDATE students SET notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (test_note, student_id)
        )
        
        if success is not False:
            print("✅ تم تحديث الملاحظات بنجاح")
            
            # التحقق من التحديث
            updated_student = db_manager.execute_query(
                "SELECT name, notes, updated_at FROM students WHERE id = ?",
                (student_id,)
            )
            
            if updated_student:
                name, notes, updated_at = updated_student[0]
                print(f"📝 الطالب: {name}")
                print(f"💬 الملاحظة: {notes}")
                print(f"🕒 آخر تحديث: {updated_at}")
            
        else:
            print("❌ فشل في تحديث الملاحظات")
            return False
        
        # اختبار حذف الملاحظات
        print("\n4️⃣ اختبار حذف الملاحظات...")
        success = db_manager.execute_query(
            "UPDATE students SET notes = '', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (student_id,)
        )
        
        if success is not False:
            print("✅ تم حذف الملاحظات بنجاح")
        else:
            print("❌ فشل في حذف الملاحظات")
            return False
        
        return True
        
    except Exception as e:
        logging.error(f"خطأ في اختبار ميزة الملاحظات: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🎯 اختبار ميزة ملاحظات الطالب")
    print("📱 نظام حسابات المدارس الأهلية")
    print("=" * 60)
    
    success = test_student_notes_feature()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 نجح الاختبار! ميزة ملاحظات الطالب تعمل بشكل صحيح")
        print("📋 يمكنك الآن استخدام الميزة من صفحة تفاصيل الطالب")
    else:
        print("❌ فشل الاختبار! يرجى مراجعة الأخطاء أعلاه")

if __name__ == "__main__":
    main()
