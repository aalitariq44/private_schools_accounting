#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعادة إنشاء قاعدة البيانات بشكل مباشر
"""

import os
import sys
import sqlite3
from pathlib import Path
import logging

# إضافة المسار الجذر للمشروع
sys.path.insert(0, str(Path(__file__).parent))

import config

def recreate_database():
    """إعادة إنشاء قاعدة البيانات"""
    try:
        # إنشاء مجلد قاعدة البيانات
        config.DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        
        # اتصال مباشر بقاعدة البيانات (سيتم إنشاؤها إذا لم تكن موجودة)
        conn = sqlite3.connect(str(config.DATABASE_PATH))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        
        cursor = conn.cursor()
        
        print("📋 إنشاء الجداول...")
        
        # حذف الجداول الموجودة
        tables_to_drop = [
            'external_income', 'expenses', 'salaries', 'additional_fees', 
            'installments', 'students', 'teachers', 'employees', 
            'schools', 'users', 'app_settings'
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"  - تم حذف جدول {table}")
            except:
                pass
        
        # إنشاء الجداول
        
        # جدول المستخدمين
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL DEFAULT 'admin',
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✅ تم إنشاء جدول المستخدمين")
        
        # جدول المدارس
        cursor.execute("""
            CREATE TABLE schools (
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
        print("  ✅ تم إنشاء جدول المدارس")
        
        # جدول الطلاب
        cursor.execute("""
            CREATE TABLE students (
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
        print("  ✅ تم إنشاء جدول الطلاب")
        
        # جدول الأقساط
        cursor.execute("""
            CREATE TABLE installments (
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
        print("  ✅ تم إنشاء جدول الأقساط")
        
        # جدول الرسوم الإضافية
        cursor.execute("""
            CREATE TABLE additional_fees (
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
        print("  ✅ تم إنشاء جدول الرسوم الإضافية")
        
        # جدول المعلمين
        cursor.execute("""
            CREATE TABLE teachers (
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
        print("  ✅ تم إنشاء جدول المعلمين")
        
        # جدول الموظفين
        cursor.execute("""
            CREATE TABLE employees (
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
        print("  ✅ تم إنشاء جدول الموظفين")
        
        # جدول الإيرادات الخارجية - مع قيم افتراضية لحل مشكلة NOT NULL
        cursor.execute("""
            CREATE TABLE external_income (
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
        print("  ✅ تم إنشاء جدول الإيرادات الخارجية مع إصلاح قيود NOT NULL")
        
        # جدول المصروفات - مع قيم افتراضية لحل مشكلة NOT NULL
        cursor.execute("""
            CREATE TABLE expenses (
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
        print("  ✅ تم إنشاء جدول المصروفات مع إصلاح قيود NOT NULL")
        
        # جدول الرواتب
        cursor.execute("""
            CREATE TABLE salaries (
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
        print("  ✅ تم إنشاء جدول الرواتب")
        
        # جدول إعدادات التطبيق
        cursor.execute("""
            CREATE TABLE app_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✅ تم إنشاء جدول إعدادات التطبيق")
        
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
        print(f"  ✅ تم إنشاء مدرسة افتراضية برقم: {school_id}")
        
        # إنشاء مستخدم افتراضي
        import hashlib
        password = "admin123"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """, ("admin", password_hash))
        print("  ✅ تم إنشاء مستخدم افتراضي: admin / admin123")
        
        # حفظ التغييرات
        conn.commit()
        
        # إغلاق الاتصال
        cursor.close()
        conn.close()
        
        print("\n✅ تم إعادة إنشاء قاعدة البيانات بنجاح!")
        print("🔧 الإصلاحات المطبقة:")
        print("   - إصلاح قيود NOT NULL للحقل school_id في جدول external_income")
        print("   - إصلاح قيود NOT NULL للحقل school_id في جدول expenses")
        print("   - إضافة قيم افتراضية لجميع الحقول المطلوبة")
        print("   - إنشاء مدرسة افتراضية لضمان وجود school_id صالح")
        print("   - إنشاء مستخدم افتراضي للدخول للنظام")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إعادة إنشاء قاعدة البيانات: {e}")
        return False

def main():
    print("🔧 إعادة إنشاء قاعدة البيانات مع إصلاح مشاكل قيود البيانات")
    print("=" * 60)
    
    if recreate_database():
        print("\n🎉 العملية مكتملة بنجاح!")
        print("يمكنك الآن تشغيل التطبيق بدون مشاكل.")
        return True
    else:
        print("\n❌ فشلت العملية!")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
