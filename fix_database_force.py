#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح مشاكل قيود قاعدة البيانات مع إجبار إغلاق الاتصالات
"""

import sys
import os
import time
import gc
from pathlib import Path
import logging
import sqlite3

# إضافة المسار الجذر للمشروع
sys.path.insert(0, str(Path(__file__).parent))

import config

# إعداد نظام التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def force_close_database_connections():
    """إجبار إغلاق جميع اتصالات قاعدة البيانات"""
    try:
        # تنظيف الذاكرة
        gc.collect()
        
        # محاولة إغلاق أي اتصالات موجودة
        try:
            from core.database.connection import db_manager
            if hasattr(db_manager, 'connection') and db_manager.connection:
                db_manager.connection.close()
                db_manager.connection = None
                logging.info("تم إغلاق اتصال db_manager")
        except:
            pass
        
        # انتظار قصير لضمان إغلاق الاتصالات
        time.sleep(2)
        
        return True
        
    except Exception as e:
        logging.error(f"خطأ في إغلاق الاتصالات: {e}")
        return False

def delete_existing_database():
    """حذف قاعدة البيانات الحالية مع محاولات متعددة"""
    max_attempts = 5
    
    for attempt in range(max_attempts):
        try:
            # إجبار إغلاق الاتصالات
            force_close_database_connections()
            
            if config.DATABASE_PATH.exists():
                # محاولة حذف الملف
                os.remove(str(config.DATABASE_PATH))
                logging.info(f"تم حذف قاعدة البيانات الحالية: {config.DATABASE_PATH}")
                return True
            else:
                logging.info("لا توجد قاعدة بيانات موجودة للحذف")
                return True
                
        except PermissionError as e:
            logging.warning(f"المحاولة {attempt + 1}: لا يمكن حذف قاعدة البيانات (مستخدمة بواسطة عملية أخرى)")
            if attempt < max_attempts - 1:
                logging.info(f"انتظار 3 ثوانٍ قبل المحاولة التالية...")
                time.sleep(3)
            else:
                logging.error("فشل في حذف قاعدة البيانات بعد عدة محاولات")
                
                # محاولة إنشاء نسخة احتياطية وحذف الأصلية
                try:
                    backup_path = config.DATABASE_PATH.with_suffix('.backup')
                    import shutil
                    shutil.move(str(config.DATABASE_PATH), str(backup_path))
                    logging.info(f"تم نقل قاعدة البيانات إلى: {backup_path}")
                    return True
                except Exception as backup_error:
                    logging.error(f"فشل في النقل أيضاً: {backup_error}")
                    return False
                    
        except Exception as e:
            logging.error(f"خطأ غير متوقع في حذف قاعدة البيانات: {e}")
            return False
    
    return False

def create_new_database_manager():
    """إنشاء مدير قاعدة بيانات جديد"""
    class NewDatabaseManager:
        """مدير قاعدة البيانات الجديد"""
        
        def __init__(self):
            """تهيئة مدير قاعدة البيانات"""
            self.db_path = config.DATABASE_PATH
            self.connection = None
            
        def get_connection(self) -> sqlite3.Connection:
            """الحصول على اتصال قاعدة البيانات"""
            try:
                if self.connection is None:
                    self.connection = sqlite3.connect(
                        str(self.db_path),
                        check_same_thread=False
                    )
                    self.connection.row_factory = sqlite3.Row
                    # تفعيل المفاتيح الأجنبية
                    self.connection.execute("PRAGMA foreign_keys = ON")
                    
                return self.connection
                
            except Exception as e:
                logging.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
                raise
        
        def get_cursor(self):
            """الحصول على cursor"""
            from contextlib import contextmanager
            
            @contextmanager
            def cursor_context():
                conn = self.get_connection()
                cursor = conn.cursor()
                try:
                    yield cursor
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    logging.error(f"خطأ في قاعدة البيانات: {e}")
                    raise
                finally:
                    cursor.close()
            
            return cursor_context()
        
        def create_tables(self):
            """إنشاء جداول قاعدة البيانات"""
            try:
                with self.get_cursor() as cursor:
                    # جدول المستخدمين
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL DEFAULT 'admin',
                            password TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # جدول المدارس
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS schools (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name_ar TEXT NOT NULL,
                            name_en TEXT,
                            logo_path TEXT,
                            address TEXT,
                            phone TEXT,
                            principal_name TEXT,
                            school_types TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # جدول الطلاب
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS students (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            national_id_number TEXT,
                            school_id INTEGER NOT NULL,
                            grade TEXT NOT NULL,
                            section TEXT NOT NULL,
                            academic_year TEXT,
                            gender TEXT NOT NULL,
                            birthdate DATE,
                            phone TEXT,
                            guardian_name TEXT,
                            guardian_phone TEXT,
                            total_fee DECIMAL(10,2) NOT NULL,
                            start_date DATE NOT NULL,
                            status TEXT DEFAULT 'نشط',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
                        )
                    """)
                    
                    # جدول الأقساط
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS installments (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            student_id INTEGER NOT NULL,
                            amount DECIMAL(10,2) NOT NULL,
                            payment_date DATE NOT NULL,
                            payment_time TIME NOT NULL,
                            notes TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                        )
                    """)
                    
                    # جدول الرسوم الإضافية
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS additional_fees (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            student_id INTEGER NOT NULL,
                            fee_type TEXT NOT NULL,
                            amount DECIMAL(10,2) NOT NULL,
                            paid BOOLEAN DEFAULT FALSE,
                            payment_date DATE,
                            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            notes TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                        )
                    """)
                    
                    # جدول المعلمين
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS teachers (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            school_id INTEGER NOT NULL,
                            class_hours INTEGER NOT NULL DEFAULT 0,
                            monthly_salary DECIMAL(10,2) NOT NULL,
                            phone TEXT,
                            notes TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
                        )
                    """)
                    
                    # جدول الموظفين
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS employees (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            school_id INTEGER NOT NULL,
                            job_type TEXT NOT NULL,
                            monthly_salary DECIMAL(10,2) NOT NULL,
                            phone TEXT,
                            notes TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
                        )
                    """)
                    
                    # جدول الإيرادات الخارجية - مع قيم افتراضية
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS external_income (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            school_id INTEGER NOT NULL,
                            title TEXT NOT NULL DEFAULT 'إيراد خارجي',
                            amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                            category TEXT NOT NULL DEFAULT 'متنوع',
                            income_type TEXT NOT NULL DEFAULT 'نقدي',
                            description TEXT DEFAULT '',
                            income_date DATE NOT NULL DEFAULT (date('now')),
                            notes TEXT DEFAULT '',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
                        )
                    """)
                    
                    # جدول المصروفات - مع قيم افتراضية
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS expenses (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            school_id INTEGER NOT NULL,
                            expense_type TEXT NOT NULL DEFAULT 'مصروف عام',
                            amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                            expense_date DATE NOT NULL DEFAULT (date('now')),
                            description TEXT DEFAULT '',
                            notes TEXT DEFAULT '',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
                        )
                    """)
                    
                    # جدول الرواتب
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS salaries (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            staff_type TEXT NOT NULL CHECK (staff_type IN ('teacher', 'employee')),
                            staff_id INTEGER NOT NULL,
                            base_salary DECIMAL(10,2) NOT NULL,
                            paid_amount DECIMAL(10,2) NOT NULL,
                            from_date DATE NOT NULL,
                            to_date DATE NOT NULL,
                            days_count INTEGER NOT NULL,
                            payment_date DATE NOT NULL,
                            payment_time TIME NOT NULL,
                            notes TEXT,
                            school_id INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE SET NULL
                        )
                    """)
                    
                    # جدول إعدادات التطبيق
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS app_settings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            setting_key TEXT UNIQUE NOT NULL,
                            setting_value TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    logging.info("تم إنشاء جداول قاعدة البيانات بنجاح")
                    
            except Exception as e:
                logging.error(f"خطأ في إنشاء جداول قاعدة البيانات: {e}")
                raise
        
        def close_connection(self):
            """إغلاق اتصال قاعدة البيانات"""
            if self.connection:
                self.connection.close()
                self.connection = None
    
    return NewDatabaseManager()

def create_fixed_database():
    """إنشاء قاعدة بيانات جديدة مع إصلاح المشاكل"""
    try:
        # إنشاء مدير قاعدة بيانات جديد
        db_manager = create_new_database_manager()
        
        # التأكد من وجود مجلد قاعدة البيانات
        config.DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        
        # إنشاء الجداول
        db_manager.create_tables()
        
        logging.info("تم إنشاء قاعدة البيانات الجديدة بنجاح")
        
        # التحقق من الجداول المنشأة
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            logging.info("الجداول المنشأة:")
            for table in tables:
                logging.info(f"  - {table[0]}")
        
        return db_manager
        
    except Exception as e:
        logging.error(f"خطأ في إنشاء قاعدة البيانات الجديدة: {e}")
        return None

def create_default_school(db_manager):
    """إنشاء مدرسة افتراضية"""
    try:
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM schools")
            school_count = cursor.fetchone()[0]
            
            if school_count == 0:
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
                cursor.execute("SELECT id FROM schools LIMIT 1")
                school_id = cursor.fetchone()[0]
                logging.info(f"توجد مدرسة برقم: {school_id}")
                return school_id
                
    except Exception as e:
        logging.error(f"خطأ في إنشاء المدرسة الافتراضية: {e}")
        return None

def create_default_user(db_manager):
    """إنشاء مستخدم افتراضي"""
    try:
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
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
    print("🔧 إصلاح مشاكل قيود قاعدة البيانات (محسن)")
    print("=" * 50)
    
    # الخطوة 1: حذف قاعدة البيانات الحالية
    print("🗑️  حذف قاعدة البيانات الحالية...")
    if not delete_existing_database():
        print("❌ فشل في حذف قاعدة البيانات الحالية")
        return False
    
    # الخطوة 2: إنشاء قاعدة بيانات جديدة
    print("🏗️  إنشاء قاعدة بيانات جديدة...")
    db_manager = create_fixed_database()
    if not db_manager:
        print("❌ فشل في إنشاء قاعدة البيانات الجديدة")
        return False
    
    # الخطوة 3: إنشاء مدرسة افتراضية
    print("🏫 إنشاء مدرسة افتراضية...")
    school_id = create_default_school(db_manager)
    if school_id is None:
        print("❌ فشل في إنشاء المدرسة الافتراضية")
        return False
    
    # الخطوة 4: إنشاء مستخدم افتراضي
    print("👤 إنشاء مستخدم افتراضي...")
    if not create_default_user(db_manager):
        print("❌ فشل في إنشاء المستخدم الافتراضي")
        return False
    
    # إغلاق الاتصال
    db_manager.close_connection()
    
    print("\n✅ تم إصلاح جميع مشاكل قاعدة البيانات بنجاح!")
    print("📋 ملخص الإصلاحات:")
    print(f"   - تم إنشاء قاعدة بيانات جديدة في: {config.DATABASE_PATH}")
    print(f"   - تم إنشاء مدرسة افتراضية برقم: {school_id}")
    print("   - تم إنشاء مستخدم افتراضي: admin / admin123")
    print("   - تم إصلاح قيود NOT NULL للحقول school_id")
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
