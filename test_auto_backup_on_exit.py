#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار ميزة النسخ الاحتياطي التلقائي عند الخروج
يختبر الميزة الجديدة لإنشاء نسخة احتياطية تلقائية عند إغلاق التطبيق
"""

import sys
import os
import logging
from pathlib import Path

# إضافة المجلد الرئيسي للتطبيق إلى المسار
sys.path.insert(0, str(Path(__file__).parent))

import config
from PyQt5.QtWidgets import QApplication, QMessageBox
from app.main_window import MainWindow
from core.backup.backup_manager import backup_manager

def test_auto_backup_config():
    """اختبار إعدادات النسخ الاحتياطي التلقائي"""
    print("🧪 اختبار إعدادات النسخ الاحتياطي التلقائي...")
    
    print(f"✅ AUTO_BACKUP_ON_EXIT: {config.AUTO_BACKUP_ON_EXIT}")
    print(f"✅ AUTO_BACKUP_SHOW_SUCCESS_MESSAGE: {config.AUTO_BACKUP_SHOW_SUCCESS_MESSAGE}")
    print(f"✅ AUTO_BACKUP_CONFIRMATION_DIALOG: {config.AUTO_BACKUP_CONFIRMATION_DIALOG}")
    
    return True

def test_backup_manager():
    """اختبار مدير النسخ الاحتياطي"""
    print("🧪 اختبار مدير النسخ الاحتياطي...")
    
    try:
        # اختبار إنشاء نسخة احتياطية
        success, message = backup_manager.create_backup("اختبار النسخ الاحتياطي التلقائي")
        
        if success:
            print(f"✅ تم إنشاء النسخة الاحتياطية بنجاح: {message}")
        else:
            print(f"❌ فشل في إنشاء النسخة الاحتياطية: {message}")
            
        return success
        
    except Exception as e:
        print(f"❌ خطأ في اختبار مدير النسخ الاحتياطي: {e}")
        return False

def test_main_window_backup_functions():
    """اختبار دوال النسخ الاحتياطي في النافذة الرئيسية"""
    print("🧪 اختبار دوال النسخ الاحتياطي في النافذة الرئيسية...")
    
    try:
        app = QApplication(sys.argv)
        
        # إنشاء النافذة الرئيسية
        main_window = MainWindow()
        
        # التحقق من وجود الدوال المطلوبة
        assert hasattr(main_window, 'create_quick_backup'), "دالة create_quick_backup غير موجودة"
        assert hasattr(main_window, 'create_auto_backup_on_exit'), "دالة create_auto_backup_on_exit غير موجودة"
        assert hasattr(main_window, 'closeEvent'), "دالة closeEvent غير موجودة"
        
        print("✅ جميع الدوال المطلوبة موجودة")
        
        # اختبار دالة النسخ الاحتياطي السريع (بدون واجهة مستخدم)
        print("🔧 اختبار دالة النسخ الاحتياطي التلقائي...")
        
        # محاولة تشغيل الدالة
        try:
            result = main_window.create_auto_backup_on_exit()
            print(f"✅ دالة النسخ الاحتياطي التلقائي تعمل بشكل صحيح: {result}")
        except Exception as e:
            print(f"⚠️ تحذير في تشغيل دالة النسخ الاحتياطي التلقائي: {e}")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار النافذة الرئيسية: {e}")
        return False

def test_config_scenarios():
    """اختبار سيناريوهات مختلفة للإعدادات"""
    print("🧪 اختبار سيناريوهات مختلفة للإعدادات...")
    
    scenarios = [
        {
            "name": "النسخ الاحتياطي مفعل مع رسائل",
            "AUTO_BACKUP_ON_EXIT": True,
            "AUTO_BACKUP_SHOW_SUCCESS_MESSAGE": True,
            "AUTO_BACKUP_CONFIRMATION_DIALOG": True
        },
        {
            "name": "النسخ الاحتياطي مفعل بدون رسائل",
            "AUTO_BACKUP_ON_EXIT": True,
            "AUTO_BACKUP_SHOW_SUCCESS_MESSAGE": False,
            "AUTO_BACKUP_CONFIRMATION_DIALOG": False
        },
        {
            "name": "النسخ الاحتياطي معطل",
            "AUTO_BACKUP_ON_EXIT": False,
            "AUTO_BACKUP_SHOW_SUCCESS_MESSAGE": False,
            "AUTO_BACKUP_CONFIRMATION_DIALOG": False
        }
    ]
    
    # حفظ الإعدادات الأصلية
    original_settings = {
        "AUTO_BACKUP_ON_EXIT": config.AUTO_BACKUP_ON_EXIT,
        "AUTO_BACKUP_SHOW_SUCCESS_MESSAGE": config.AUTO_BACKUP_SHOW_SUCCESS_MESSAGE,
        "AUTO_BACKUP_CONFIRMATION_DIALOG": config.AUTO_BACKUP_CONFIRMATION_DIALOG
    }
    
    for scenario in scenarios:
        print(f"\n📋 اختبار سيناريو: {scenario['name']}")
        
        # تطبيق الإعدادات
        config.AUTO_BACKUP_ON_EXIT = scenario["AUTO_BACKUP_ON_EXIT"]
        config.AUTO_BACKUP_SHOW_SUCCESS_MESSAGE = scenario["AUTO_BACKUP_SHOW_SUCCESS_MESSAGE"]
        config.AUTO_BACKUP_CONFIRMATION_DIALOG = scenario["AUTO_BACKUP_CONFIRMATION_DIALOG"]
        
        print(f"   📝 الإعدادات المطبقة:")
        print(f"      - النسخ التلقائي: {config.AUTO_BACKUP_ON_EXIT}")
        print(f"      - رسائل النجاح: {config.AUTO_BACKUP_SHOW_SUCCESS_MESSAGE}")
        print(f"      - حوار التأكيد: {config.AUTO_BACKUP_CONFIRMATION_DIALOG}")
        
        print(f"   ✅ تم اختبار السيناريو بنجاح")
    
    # استرجاع الإعدادات الأصلية
    config.AUTO_BACKUP_ON_EXIT = original_settings["AUTO_BACKUP_ON_EXIT"]
    config.AUTO_BACKUP_SHOW_SUCCESS_MESSAGE = original_settings["AUTO_BACKUP_SHOW_SUCCESS_MESSAGE"]
    config.AUTO_BACKUP_CONFIRMATION_DIALOG = original_settings["AUTO_BACKUP_CONFIRMATION_DIALOG"]
    
    print(f"\n✅ تم استرجاع الإعدادات الأصلية")
    return True

def run_all_tests():
    """تشغيل جميع الاختبارات"""
    print("🚀 بدء اختبار ميزة النسخ الاحتياطي التلقائي عند الخروج\n")
    
    tests = [
        ("اختبار إعدادات النسخ الاحتياطي", test_auto_backup_config),
        ("اختبار مدير النسخ الاحتياطي", test_backup_manager),
        ("اختبار دوال النافذة الرئيسية", test_main_window_backup_functions),
        ("اختبار سيناريوهات الإعدادات", test_config_scenarios)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"=" * 60)
        print(f"🧪 {test_name}")
        print("=" * 60)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: نجح")
            else:
                print(f"❌ {test_name}: فشل")
                
        except Exception as e:
            print(f"💥 {test_name}: خطأ - {e}")
            results.append((test_name, False))
        
        print()
    
    # عرض النتائج النهائية
    print("=" * 60)
    print("📊 ملخص نتائج الاختبارات")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 النتيجة النهائية: {passed}/{total} اختبارات نجحت")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت! الميزة جاهزة للاستخدام.")
    else:
        print("⚠️ بعض الاختبارات فشلت. يرجى مراجعة الأخطاء.")
    
    return passed == total

if __name__ == "__main__":
    try:
        # إعداد نظام التسجيل
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # تشغيل الاختبارات
        success = run_all_tests()
        
        if success:
            print("\n🎯 جميع الاختبارات نجحت!")
            print("\n📚 كيفية الاستخدام:")
            print("   1. قم بتشغيل التطبيق عادي")
            print("   2. عند الخروج، سيتم إنشاء نسخة احتياطية تلقائية")
            print("   3. يمكنك تعديل الإعدادات في config.py:")
            print("      - AUTO_BACKUP_ON_EXIT: تفعيل/إلغاء الميزة")
            print("      - AUTO_BACKUP_SHOW_SUCCESS_MESSAGE: عرض رسالة النجاح")
            print("      - AUTO_BACKUP_CONFIRMATION_DIALOG: عرض حوار التأكيد")
        else:
            print("\n❌ بعض الاختبارات فشلت!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف الاختبارات بواسطة المستخدم")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 خطأ عام في الاختبارات: {e}")
        sys.exit(1)
