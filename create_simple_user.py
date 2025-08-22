#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إنشاء مستخدم جديد بكلمة مرور عادية (غير مشفرة)
"""

import logging
from core.database.connection import db_manager

def create_simple_user(username="admin", password="admin123"):
    """إنشاء مستخدم بكلمة مرور عادية"""
    try:
        with db_manager.get_cursor() as cursor:
            # التحقق من وجود المستخدم
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            
            if result['count'] > 0:
                print(f"المستخدم {username} موجود بالفعل")
                
                # تحديث كلمة المرور
                cursor.execute("""
                    UPDATE users 
                    SET password = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE username = ?
                """, (password, username))
                
                print(f"✓ تم تحديث كلمة مرور المستخدم {username}")
                
            else:
                # إنشاء مستخدم جديد
                cursor.execute("""
                    INSERT INTO users (username, password)
                    VALUES (?, ?)
                """, (username, password))
                
                print(f"✓ تم إنشاء المستخدم {username}")
            
            print(f"بيانات تسجيل الدخول:")
            print(f"اسم المستخدم: {username}")
            print(f"كلمة المرور: {password}")
            
            return True
            
    except Exception as e:
        print(f"خطأ في إنشاء المستخدم: {e}")
        logging.error(f"خطأ في إنشاء المستخدم: {e}")
        return False

if __name__ == "__main__":
    print("=== إنشاء/تحديث المستخدم ===")
    
    # يمكنك تغيير اسم المستخدم وكلمة المرور هنا
    username = input("أدخل اسم المستخدم (افتراضي: admin): ").strip() or "admin"
    password = input("أدخل كلمة المرور (افتراضي: admin123): ").strip() or "admin123"
    
    if create_simple_user(username, password):
        print("\n✓ تم إنشاء/تحديث المستخدم بنجاح!")
    else:
        print("\n✗ فشل في إنشاء/تحديث المستخدم")
