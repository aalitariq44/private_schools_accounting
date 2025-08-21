#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحديث قاعدة البيانات الحالية - التأكد من إضافة عمود الملاحظات
"""
import logging
from core.database.connection import db_manager

logging.basicConfig(level=logging.INFO)

def update_existing_database():
    """تحديث قاعدة البيانات الحالية لإضافة عمود الملاحظات"""
    try:
        print("🔄 فحص وتحديث قاعدة البيانات...")
        
        # فحص إذا كان عمود الملاحظات موجود
        columns_info = db_manager.execute_query('PRAGMA table_info(students)')
        existing_columns = [column[1] for column in columns_info]
        
        if 'notes' not in existing_columns:
            print("➕ إضافة عمود الملاحظات...")
            db_manager.execute_query("""
                ALTER TABLE students 
                ADD COLUMN notes TEXT DEFAULT ''
            """)
            print("✅ تم إضافة عمود الملاحظات بنجاح")
        else:
            print("✅ عمود الملاحظات موجود بالفعل")
        
        # عرض البنية النهائية
        print("\n📋 بنية جدول الطلاب:")
        columns_info = db_manager.execute_query('PRAGMA table_info(students)')
        for column in columns_info:
            status = "🆕" if column[1] == 'notes' else "  "
            print(f"{status} {column[1]:<20} - {column[2]}")
        
        # فحص بعض البيانات التجريبية
        print(f"\n📊 عدد الطلاب في قاعدة البيانات:")
        student_count = db_manager.execute_query("SELECT COUNT(*) FROM students")
        if student_count:
            print(f"   {student_count[0][0]} طالب")
        
        return True
        
    except Exception as e:
        logging.error(f"خطأ في تحديث قاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    print("🎯 تحديث قاعدة البيانات - إضافة ميزة ملاحظات الطالب")
    print("=" * 60)
    
    success = update_existing_database()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 تم تحديث قاعدة البيانات بنجاح!")
        print("📝 يمكنك الآن إضافة وتعديل ملاحظات الطلاب من صفحة تفاصيل الطالب")
    else:
        print("❌ فشل في تحديث قاعدة البيانات")
