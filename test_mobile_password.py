#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار ميزة كلمة مرور التطبيق المحمول
"""

import sys
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from core.database.connection import db_manager
from core.utils.settings_manager import settings_manager


def test_mobile_password_feature():
    """اختبار ميزة كلمة مرور التطبيق المحمول"""
    print("=== اختبار ميزة كلمة مرور التطبيق المحمول ===\n")
    
    try:
        # تهيئة قاعدة البيانات
        db_manager.initialize_database()
        print("✓ تم تهيئة قاعدة البيانات")
        
        # اختبار الحصول على كلمة المرور الحالية
        current_password = settings_manager.get_mobile_password()
        print(f"✓ كلمة المرور الحالية: '{current_password}' (فارغة إذا لم تُعين)")
        
        # اختبار تعيين كلمة مرور جديدة
        test_password = "test_mobile_123"
        success = settings_manager.set_mobile_password(test_password)
        if success:
            print(f"✓ تم تعيين كلمة مرور اختبار: '{test_password}'")
        else:
            print("✗ فشل في تعيين كلمة مرور الاختبار")
            return False
        
        # التحقق من حفظ كلمة المرور
        saved_password = settings_manager.get_mobile_password()
        if saved_password == test_password:
            print(f"✓ تم حفظ كلمة المرور بنجاح: '{saved_password}'")
        else:
            print(f"✗ كلمة المرور المحفوظة لا تطابق المُدخلة. المحفوظة: '{saved_password}'")
            return False
        
        # اختبار الحصول على اسم المؤسسة (مطلوب للتطبيق المحمول)
        org_name = settings_manager.get_organization_name()
        if org_name:
            print(f"✓ اسم المؤسسة: '{org_name}'")
        else:
            print("⚠ تحذير: لم يتم تعيين اسم المؤسسة (مطلوب للتطبيق المحمول)")
        
        # اختبار حذف كلمة المرور
        success = settings_manager.set_mobile_password("")
        if success:
            print("✓ تم حذف كلمة مرور الاختبار")
        else:
            print("✗ فشل في حذف كلمة مرور الاختبار")
            return False
        
        # التحقق من الحذف
        deleted_password = settings_manager.get_mobile_password()
        if not deleted_password:
            print("✓ تم التأكد من حذف كلمة المرور")
        else:
            print(f"✗ كلمة المرور لم تُحذف بشكل كامل: '{deleted_password}'")
            return False
        
        print("\n✅ نجح اختبار جميع وظائف كلمة مرور التطبيق المحمول!")
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ في الاختبار: {e}")
        return False


def test_database_structure():
    """اختبار بنية قاعدة البيانات للتأكد من وجود جدول الإعدادات"""
    print("\n=== اختبار بنية قاعدة البيانات ===")
    
    try:
        # التحقق من وجود جدول app_settings
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='app_settings'"
        result = db_manager.execute_query(query)
        
        if result:
            print("✓ جدول app_settings موجود")
            
            # التحقق من أعمدة الجدول
            query = "PRAGMA table_info(app_settings)"
            columns = db_manager.execute_query(query)
            
            required_columns = ['setting_key', 'setting_value']
            existing_columns = [col['name'] for col in columns]
            
            for col in required_columns:
                if col in existing_columns:
                    print(f"✓ العمود {col} موجود")
                else:
                    print(f"✗ العمود {col} مفقود")
                    return False
            
            return True
        else:
            print("✗ جدول app_settings غير موجود")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار قاعدة البيانات: {e}")
        return False


def test_import_dependencies():
    """اختبار استيراد التبعيات المطلوبة"""
    print("\n=== اختبار التبعيات ===")
    
    try:
        # اختبار استيراد نافذة الحوار
        from ui.dialogs.mobile_password_dialog import MobilePasswordDialog, show_mobile_password_dialog
        print("✓ تم استيراد نافذة حوار كلمة مرور التطبيق المحمول")
        
        # اختبار استيراد دوال مدير الإعدادات
        from core.utils.settings_manager import get_mobile_password, set_mobile_password
        print("✓ تم استيراد دوال كلمة مرور التطبيق المحمول")
        
        return True
        
    except ImportError as e:
        print(f"✗ خطأ في استيراد التبعيات: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return False


if __name__ == "__main__":
    print("بدء اختبار ميزة كلمة مرور التطبيق المحمول...\n")
    
    # تشغيل الاختبارات
    tests = [
        test_import_dependencies,
        test_database_structure,
        test_mobile_password_feature
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("-" * 50)
    
    print(f"\nنتائج الاختبار: {passed}/{total} اختبارات نجحت")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت! الميزة جاهزة للاستخدام.")
    else:
        print("⚠ بعض الاختبارات فشلت. يرجى مراجعة الأخطاء أعلاه.")
    
    input("\nاضغط Enter للخروج...")
