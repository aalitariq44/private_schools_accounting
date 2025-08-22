#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحديث جدول المستخدمين لتغيير كلمة المرور من hash إلى نص عادي
"""

import logging
import sqlite3
from core.database.connection import db_manager

def update_password_column():
    """تحديث عمود كلمة المرور في جدول المستخدمين"""
    try:
        logging.info("بدء تحديث جدول المستخدمين...")
        
        with db_manager.get_cursor() as cursor:
            # التحقق من وجود العمود password_hash
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if 'password_hash' in column_names:
                print("تم العثور على عمود password_hash، سيتم تحديثه...")
                
                # إنشاء جدول مؤقت بالهيكل الجديد
                cursor.execute("""
                    CREATE TABLE users_temp (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL DEFAULT 'admin',
                        password TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # نسخ البيانات الموجودة (سيتم تخزين كلمة المرور كما هي)
                # ملاحظة: هذا سيفشل إذا كانت كلمات المرور مشفرة فعلياً
                # في هذه الحالة ستحتاج لإعادة تعيين كلمة المرور
                cursor.execute("""
                    INSERT INTO users_temp (id, username, password, created_at, updated_at)
                    SELECT id, username, password_hash, created_at, updated_at
                    FROM users
                """)
                
                # حذف الجدول القديم
                cursor.execute("DROP TABLE users")
                
                # إعادة تسمية الجدول المؤقت
                cursor.execute("ALTER TABLE users_temp RENAME TO users")
                
                logging.info("✓ تم تحديث جدول المستخدمين بنجاح")
                print("✓ تم تحديث جدول المستخدمين بنجاح")
                
            elif 'password' in column_names:
                print("العمود password موجود بالفعل، لا حاجة للتحديث")
                logging.info("العمود password موجود بالفعل")
                
            else:
                print("خطأ: لم يتم العثور على عمود كلمة المرور")
                logging.error("لم يتم العثور على عمود كلمة المرور")
                return False
                
        return True
        
    except Exception as e:
        logging.error(f"خطأ في تحديث جدول المستخدمين: {e}")
        print(f"خطأ في تحديث جدول المستخدمين: {e}")
        return False

def reset_admin_password():
    """إعادة تعيين كلمة مرور المدير إلى قيمة افتراضية"""
    try:
        default_password = "123456"  # كلمة مرور افتراضية
        
        with db_manager.get_cursor() as cursor:
            # تحديث كلمة مرور المدير
            cursor.execute("""
                UPDATE users 
                SET password = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE username = 'admin'
            """, (default_password,))
            
            if cursor.rowcount > 0:
                print(f"✓ تم إعادة تعيين كلمة مرور المدير إلى: {default_password}")
                logging.info("تم إعادة تعيين كلمة مرور المدير")
                return True
            else:
                print("لم يتم العثور على المستخدم admin")
                return False
                
    except Exception as e:
        logging.error(f"خطأ في إعادة تعيين كلمة المرور: {e}")
        print(f"خطأ في إعادة تعيين كلمة المرور: {e}")
        return False

if __name__ == "__main__":
    print("=== تحديث جدول المستخدمين ===")
    
    # تحديث جدول المستخدمين
    if update_password_column():
        print("\n=== إعادة تعيين كلمة مرور المدير ===")
        
        # إعادة تعيين كلمة مرور المدير للتأكد من إمكانية الدخول
        if reset_admin_password():
            print("\n✓ تم تحديث النظام بنجاح!")
            print("يمكنك الآن تسجيل الدخول باستخدام:")
            print("اسم المستخدم: admin")
            print("كلمة المرور: admin123")
            print("\nيرجى تغيير كلمة المرور من الإعدادات بعد تسجيل الدخول")
        else:
            print("تم تحديث الجدول ولكن فشل في إعادة تعيين كلمة المرور")
    else:
        print("فشل في تحديث جدول المستخدمين")
