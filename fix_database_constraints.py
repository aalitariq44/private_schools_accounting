#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح مشاكل قيود قاعدة البيانات
هذا السكريبت سيحذف قاعدة البيانات الحالية ويعيد إنشاءها مع إصلاح المشاكل
"""

import sys
import os
from pathlib import Path
import logging

# إضافة المسار الجذر للمشروع
sys.path.insert(0, str(Path(__file__).parent))

import config
from core.database.connection import DatabaseManager

# إعداد نظام التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def delete_existing_database():
    """حذف قاعدة البيانات الحالية"""
    try:
        if config.DATABASE_PATH.exists():
            config.DATABASE_PATH.unlink()
            logging.info(f"تم حذف قاعدة البيانات الحالية: {config.DATABASE_PATH}")
            return True
        else:
            logging.info("لا توجد قاعدة بيانات موجودة للحذف")
            return True
    except Exception as e:
        logging.error(f"خطأ في حذف قاعدة البيانات: {e}")
        return False

def create_fixed_database():
    """إنشاء قاعدة بيانات جديدة مع إصلاح المشاكل"""
    try:
        # إنشاء مدير قاعدة بيانات جديد
        db_manager = DatabaseManager()
        
        # تهيئة قاعدة البيانات
        success = db_manager.initialize_database()
        
        if success:
            logging.info("تم إنشاء قاعدة البيانات الجديدة بنجاح")
            
            # التحقق من الجداول المنشأة
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                logging.info("الجداول المنشأة:")
                for table in tables:
                    logging.info(f"  - {table[0]}")
                    
                # التحقق من هيكل جداول external_income و expenses
                for table_name in ['external_income', 'expenses']:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    logging.info(f"\nهيكل جدول {table_name}:")
                    for col in columns:
                        logging.info(f"  - {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'PRIMARY KEY' if col[5] else ''}")
            
            return True
        else:
            logging.error("فشل في إنشاء قاعدة البيانات")
            return False
            
    except Exception as e:
        logging.error(f"خطأ في إنشاء قاعدة البيانات الجديدة: {e}")
        return False

def create_default_school():
    """إنشاء مدرسة افتراضية لضمان وجود school_id صالح"""
    try:
        db_manager = DatabaseManager()
        
        # التحقق من وجود مدارس
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM schools")
            school_count = cursor.fetchone()[0]
            
            if school_count == 0:
                # إنشاء مدرسة افتراضية
                cursor.execute("""
                    INSERT INTO schools (name_ar, name_en, school_types, address, phone)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    "المدرسة الافتراضية",
                    "Default School", 
                    "جميع المراحل",
                    "العنوان الافتراضي",
                    "0000000000"
                ))
                
                school_id = cursor.lastrowid
                logging.info(f"تم إنشاء مدرسة افتراضية برقم: {school_id}")
                return school_id
            else:
                # الحصول على أول مدرسة موجودة
                cursor.execute("SELECT id FROM schools LIMIT 1")
                school_id = cursor.fetchone()[0]
                logging.info(f"توجد مدرسة برقم: {school_id}")
                return school_id
                
    except Exception as e:
        logging.error(f"خطأ في إنشاء المدرسة الافتراضية: {e}")
        return None

def create_default_user():
    """إنشاء مستخدم افتراضي"""
    try:
        db_manager = DatabaseManager()
        
        with db_manager.get_cursor() as cursor:
            # التحقق من وجود مستخدمين
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                # إنشاء مستخدم افتراضي
                import hashlib
                password = "admin123"
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                cursor.execute("""
                    INSERT INTO users (username, password)
                    VALUES (?, ?)
                """, ("admin", password_hash))
                
                logging.info("تم إنشاء مستخدم افتراضي: admin / admin123")
                return True
            else:
                logging.info("يوجد مستخدمون في النظام")
                return True
                
    except Exception as e:
        logging.error(f"خطأ في إنشاء المستخدم الافتراضي: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 إصلاح مشاكل قيود قاعدة البيانات")
    print("=" * 50)
    
    # الخطوة 1: حذف قاعدة البيانات الحالية
    print("🗑️  حذف قاعدة البيانات الحالية...")
    if not delete_existing_database():
        print("❌ فشل في حذف قاعدة البيانات الحالية")
        return False
    
    # الخطوة 2: إنشاء قاعدة بيانات جديدة
    print("🏗️  إنشاء قاعدة بيانات جديدة...")
    if not create_fixed_database():
        print("❌ فشل في إنشاء قاعدة البيانات الجديدة")
        return False
    
    # الخطوة 3: إنشاء مدرسة افتراضية
    print("🏫 إنشاء مدرسة افتراضية...")
    school_id = create_default_school()
    if school_id is None:
        print("❌ فشل في إنشاء المدرسة الافتراضية")
        return False
    
    # الخطوة 4: إنشاء مستخدم افتراضي
    print("👤 إنشاء مستخدم افتراضي...")
    if not create_default_user():
        print("❌ فشل في إنشاء المستخدم الافتراضي")
        return False
    
    print("\n✅ تم إصلاح جميع مشاكل قاعدة البيانات بنجاح!")
    print("📋 ملخص الإصلاحات:")
    print(f"   - تم إنشاء قاعدة بيانات جديدة في: {config.DATABASE_PATH}")
    print(f"   - تم إنشاء مدرسة افتراضية برقم: {school_id}")
    print("   - تم إنشاء مستخدم افتراضي: admin / admin123")
    print("\n🎯 يمكنك الآن تشغيل التطبيق بدون مشاكل في قيود البيانات")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✨ العملية مكتملة بنجاح!")
        else:
            print("\n💥 فشلت العملية!")
            sys.exit(1)
    except Exception as e:
        logging.error(f"خطأ عام في العملية: {e}")
        print(f"\n💥 خطأ عام: {e}")
        sys.exit(1)
