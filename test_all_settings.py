#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لصفحة الإعدادات ومدير الإعدادات
"""

import sys
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def test_settings_manager():
    """اختبار مدير الإعدادات"""
    print("=== اختبار مدير الإعدادات ===")
    
    try:
        from core.database.connection import db_manager
        from core.utils.settings_manager import settings_manager
        
        # تهيئة قاعدة البيانات
        db_manager.initialize_database()
        
        # تهيئة الإعدادات الافتراضية
        settings_manager.initialize_default_settings()
        
        # اختبار العام الدراسي
        current_year = settings_manager.get_academic_year()
        print(f"العام الدراسي الحالي: {current_year}")
        
        # تغيير العام الدراسي
        new_year = "2025 - 2026"
        if settings_manager.set_academic_year(new_year):
            print(f"تم تحديث العام الدراسي إلى: {new_year}")
        else:
            print("فشل في تحديث العام الدراسي")
        
        # التحقق من التحديث
        updated_year = settings_manager.get_academic_year()
        print(f"العام الدراسي بعد التحديث: {updated_year}")
        
        # اختبار إعدادات أخرى
        settings_manager.set_setting('test_setting', 'test_value')
        test_value = settings_manager.get_setting('test_setting')
        print(f"إعداد التجربة: {test_value}")
        
        # عرض جميع الإعدادات
        all_settings = settings_manager.get_all_settings()
        print("جميع الإعدادات:")
        for key, value in all_settings.items():
            print(f"  {key}: {value}")
        
        print("✓ نجح اختبار مدير الإعدادات")
        return True
        
    except Exception as e:
        print(f"✗ فشل اختبار مدير الإعدادات: {e}")
        return False

def test_academic_year_widget():
    """اختبار ويدجت العام الدراسي"""
    print("\n=== اختبار ويدجت العام الدراسي ===")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        from ui.widgets.academic_year_widget import AcademicYearWidget
        
        app = QApplication([])
        app.setLayoutDirection(Qt.RightToLeft)
        
        # إنشاء الويدجت
        widget = AcademicYearWidget(show_label=True, auto_refresh=False)
        year = widget.get_academic_year()
        print(f"العام الدراسي في الويدجت: {year}")
        
        print("✓ نجح اختبار ويدجت العام الدراسي")
        return True
        
    except Exception as e:
        print(f"✗ فشل اختبار ويدجت العام الدراسي: {e}")
        return False

def test_settings_page_import():
    """اختبار استيراد صفحة الإعدادات"""
    print("\n=== اختبار استيراد صفحة الإعدادات ===")
    
    try:
        from ui.pages.settings.settings_page import SettingsPage
        from ui.pages.settings.change_password_dialog import ChangePasswordDialog
        
        print("✓ نجح استيراد صفحة الإعدادات")
        print("✓ نجح استيراد حوار تغيير كلمة المرور")
        return True
        
    except Exception as e:
        print(f"✗ فشل استيراد صفحة الإعدادات: {e}")
        return False

def test_auth_manager():
    """اختبار مدير المصادقة"""
    print("\n=== اختبار مدير المصادقة ===")
    
    try:
        from core.auth.login_manager import auth_manager
        
        # التحقق من وجود مستخدمين
        has_users = auth_manager.has_users()
        print(f"وجود مستخدمين في النظام: {has_users}")
        
        if not has_users:
            # إنشاء مستخدم تجريبي
            if auth_manager.create_first_user("123456"):
                print("✓ تم إنشاء مستخدم تجريبي")
            else:
                print("✗ فشل في إنشاء مستخدم تجريبي")
        
        print("✓ نجح اختبار مدير المصادقة")
        return True
        
    except Exception as e:
        print(f"✗ فشل اختبار مدير المصادقة: {e}")
        return False

def main():
    """الدالة الرئيسية للاختبار"""
    print("بدء الاختبار الشامل لصفحة الإعدادات")
    print("=" * 50)
    
    tests = [
        test_settings_manager,
        test_academic_year_widget,
        test_settings_page_import,
        test_auth_manager
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"نتائج الاختبار: {passed}/{total} نجح")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت!")
        print("\nصفحة الإعدادات جاهزة للاستخدام!")
        print("يمكنك الآن:")
        print("- تشغيل التطبيق الرئيسي: python main.py")
        print("- الذهاب لصفحة الإعدادات من القائمة الجانبية")
        print("- تغيير العام الدراسي")
        print("- تغيير كلمة المرور")
    else:
        print("❌ هناك مشاكل تحتاج لحل")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
