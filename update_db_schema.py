#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import logging

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_database_schema():
    """تحديث هيكل قاعدة البيانات لإضافة الأعمدة المفقودة"""
    
    db_path = 'data/database/schools.db'
    if not os.path.exists(db_path):
        logging.error("قاعدة البيانات غير موجودة")
        return False
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # إضافة الأعمدة المفقودة إلى جدول الطلاب
        logging.info("إضافة الأعمدة المفقودة إلى جدول الطلاب...")
        
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN national_id_number TEXT")
            logging.info("تم إضافة عمود national_id_number")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("عمود national_id_number موجود مسبقاً")
            else:
                raise
                
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN academic_year TEXT")
            logging.info("تم إضافة عمود academic_year")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("عمود academic_year موجود مسبقاً")
            else:
                raise
                
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN guardian_name TEXT")
            logging.info("تم إضافة عمود guardian_name")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("عمود guardian_name موجود مسبقاً")
            else:
                raise
                
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN guardian_phone TEXT")
            logging.info("تم إضافة عمود guardian_phone")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("عمود guardian_phone موجود مسبقاً")
            else:
                raise
                
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN status TEXT DEFAULT 'نشط'")
            logging.info("تم إضافة عمود status")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("عمود status موجود مسبقاً")
            else:
                raise
        
        # لم يعد هناك أعمدة إضافية لجداول الأقساط بعد التعديل
        
        # إضافة الأعمدة المفقودة إلى جدول الرسوم الإضافية
        logging.info("إضافة الأعمدة المفقودة إلى جدول الرسوم الإضافية...")
        
        try:
            cursor.execute("ALTER TABLE additional_fees ADD COLUMN collection_date DATE")
            logging.info("تم إضافة عمود collection_date")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("عمود collection_date موجود مسبقاً")
            else:
                raise
                
        try:
            cursor.execute("ALTER TABLE additional_fees ADD COLUMN collected_amount DECIMAL(10,2) DEFAULT 0")
            logging.info("تم إضافة عمود collected_amount")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("عمود collected_amount موجود مسبقاً")
            else:
                raise
                
        try:
            cursor.execute("ALTER TABLE additional_fees ADD COLUMN status TEXT DEFAULT 'غير محصل'")
            logging.info("تم إضافة عمود status")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("عمود status موجود مسبقاً")
            else:
                raise
        
        # حفظ التغييرات
        conn.commit()
        
        # طباعة الهيكل المحدث
        logging.info("=== الهيكل المحدث لجدول الطلاب ===")
        cursor.execute('PRAGMA table_info(students)')
        students_cols = cursor.fetchall()
        for col in students_cols:
            logging.info(f'{col[1]} - {col[2]}')
        
        logging.info("=== الهيكل المحدث لجدول الأقساط ===")
        cursor.execute('PRAGMA table_info(installments)')
        installments_cols = cursor.fetchall()
        for col in installments_cols:
            logging.info(f'{col[1]} - {col[2]}')
            
        logging.info("=== الهيكل المحدث لجدول الرسوم الإضافية ===")
        cursor.execute('PRAGMA table_info(additional_fees)')
        fees_cols = cursor.fetchall()
        for col in fees_cols:
            logging.info(f'{col[1]} - {col[2]}')
        
        conn.close()
        logging.info("تم تحديث هيكل قاعدة البيانات بنجاح!")
        return True
        
    except Exception as e:
        logging.error(f"خطأ في تحديث قاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    update_database_schema()
