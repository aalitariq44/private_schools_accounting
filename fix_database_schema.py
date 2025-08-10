#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح شامل لقاعدة البيانات - إضافة الأعمدة المفقودة
"""

import sqlite3
import os
import logging

def fix_database_schema():
    """إصلاح بنية قاعدة البيانات بإضافة الأعمدة المفقودة"""
    db_path = 'data/database/schools.db'
    
    if not os.path.exists(db_path):
        print("ملف قاعدة البيانات غير موجود!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== بدء إصلاح قاعدة البيانات ===")
        
        # 1. إصلاح جدول external_income
        print("إصلاح جدول external_income...")
        
        # التحقق من وجود العمودين المفقودين
        cursor.execute("PRAGMA table_info(external_income)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]
        
        # إضافة العمودين المفقودين إذا لم يكونا موجودين
        if 'income_type' not in existing_columns:
            cursor.execute("ALTER TABLE external_income ADD COLUMN income_type TEXT")
            print("✓ تم إضافة عمود income_type")
        
        if 'description' not in existing_columns:
            cursor.execute("ALTER TABLE external_income ADD COLUMN description TEXT")
            print("✓ تم إضافة عمود description")
        
        # 2. نقل البيانات من title إلى income_type إذا كانت title موجودة
        if 'title' in existing_columns:
            cursor.execute("UPDATE external_income SET income_type = title WHERE income_type IS NULL")
            cursor.execute("UPDATE external_income SET description = title WHERE description IS NULL")
            print("✓ تم نقل البيانات من title إلى income_type و description")
        
        # 3. تحديث البيانات الفارغة بقيم افتراضية
        cursor.execute("UPDATE external_income SET income_type = 'غير محدد' WHERE income_type IS NULL OR income_type = ''")
        cursor.execute("UPDATE external_income SET description = income_type WHERE description IS NULL OR description = ''")
        
        # 4. التأكد من عدم وجود قيم NULL في الحقول المطلوبة
        cursor.execute("UPDATE external_income SET category = 'أخرى' WHERE category IS NULL OR category = ''")
        
        print("✓ تم تحديث البيانات الفارغة")
        
        # 5. إنشاء فهارس للأعمدة الجديدة
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_external_income_type ON external_income(income_type)")
            print("✓ تم إنشاء فهرس income_type")
        except:
            pass
        
        # 6. التحقق من النتيجة النهائية
        cursor.execute("PRAGMA table_info(external_income)")
        final_columns = cursor.fetchall()
        print("\n=== بنية الجدول النهائية ===")
        for col in final_columns:
            print(f"العمود: {col[1]}, النوع: {col[2]}")
        
        # 7. اختبار بعض الاستعلامات
        print("\n=== اختبار الاستعلامات ===")
        cursor.execute("SELECT COUNT(*) FROM external_income")
        count = cursor.fetchone()[0]
        print(f"إجمالي السجلات: {count}")
        
        if count > 0:
            cursor.execute("SELECT income_type, description, amount FROM external_income LIMIT 3")
            sample_data = cursor.fetchall()
            print("عينة من البيانات:")
            for row in sample_data:
                print(f"  النوع: {row[0]}, الوصف: {row[1]}, المبلغ: {row[2]}")
        
        conn.commit()
        conn.close()
        
        print("\n✅ تم إصلاح قاعدة البيانات بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إصلاح قاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    fix_database_schema()
