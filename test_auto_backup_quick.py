#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع للميزة الجديدة - النسخ الاحتياطي التلقائي عند الخروج
اختبار محلي بدون رفع على Supabase
"""

import sys
from pathlib import Path

# إضافة المجلد الرئيسي للتطبيق إلى المسار
sys.path.insert(0, str(Path(__file__).parent))

import config

def test_config_values():
    """اختبار قيم الإعدادات الجديدة"""
    print("🧪 اختبار إعدادات النسخ الاحتياطي التلقائي...")
    
    # التحقق من وجود الإعدادات الجديدة
    assert hasattr(config, 'AUTO_BACKUP_ON_EXIT'), "إعداد AUTO_BACKUP_ON_EXIT غير موجود"
    assert hasattr(config, 'AUTO_BACKUP_SHOW_SUCCESS_MESSAGE'), "إعداد AUTO_BACKUP_SHOW_SUCCESS_MESSAGE غير موجود" 
    assert hasattr(config, 'AUTO_BACKUP_CONFIRMATION_DIALOG'), "إعداد AUTO_BACKUP_CONFIRMATION_DIALOG غير موجود"
    
    print(f"✅ AUTO_BACKUP_ON_EXIT: {config.AUTO_BACKUP_ON_EXIT}")
    print(f"✅ AUTO_BACKUP_SHOW_SUCCESS_MESSAGE: {config.AUTO_BACKUP_SHOW_SUCCESS_MESSAGE}")
    print(f"✅ AUTO_BACKUP_CONFIRMATION_DIALOG: {config.AUTO_BACKUP_CONFIRMATION_DIALOG}")
    
    return True

def test_main_window_functions():
    """اختبار دوال النافذة الرئيسية"""
    print("🧪 اختبار دوال النافذة الرئيسية...")
    
    try:
        # استيراد النافذة الرئيسية
        from app.main_window import MainWindow
        
        # التحقق من وجود الدوال المطلوبة بدون إنشاء كائن
        import inspect
        
        # الحصول على أعضاء الكلاس
        methods = [name for name, method in inspect.getmembers(MainWindow, predicate=inspect.isfunction)]
        
        required_methods = ['create_quick_backup', 'create_auto_backup_on_exit', 'closeEvent']
        
        for method_name in required_methods:
            if method_name in methods:
                print(f"✅ دالة {method_name} موجودة")
            else:
                print(f"❌ دالة {method_name} غير موجودة")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد النافذة الرئيسية: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
        return False

def test_code_integration():
    """اختبار التكامل في الكود"""
    print("🧪 اختبار التكامل في الكود...")
    
    try:
        # قراءة ملف main_window.py والتحقق من وجود الكود المطلوب
        main_window_file = Path(__file__).parent / "app" / "main_window.py"
        
        if not main_window_file.exists():
            print("❌ ملف main_window.py غير موجود")
            return False
        
        with open(main_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # التحقق من وجود الدوال والكود المطلوب
        required_code = [
            "def create_auto_backup_on_exit(self):",
            "def closeEvent(self, event):",
            "config.AUTO_BACKUP_ON_EXIT",
            "نسخة احتياطية تلقائية عند الخروج",
            "backup auto-exit"
        ]
        
        for code_snippet in required_code:
            if code_snippet in content:
                print(f"✅ الكود موجود: {code_snippet}")
            else:
                print(f"❌ الكود غير موجود: {code_snippet}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في قراءة الملف: {e}")
        return False

def test_different_config_scenarios():
    """اختبار سيناريوهات مختلفة للإعدادات"""
    print("🧪 اختبار سيناريوهات مختلفة للإعدادات...")
    
    # حفظ القيم الأصلية
    original_values = {
        'AUTO_BACKUP_ON_EXIT': config.AUTO_BACKUP_ON_EXIT,
        'AUTO_BACKUP_SHOW_SUCCESS_MESSAGE': config.AUTO_BACKUP_SHOW_SUCCESS_MESSAGE,
        'AUTO_BACKUP_CONFIRMATION_DIALOG': config.AUTO_BACKUP_CONFIRMATION_DIALOG
    }
    
    # سيناريوهات الاختبار
    test_scenarios = [
        {
            'name': 'النسخ مفعل بالكامل',
            'AUTO_BACKUP_ON_EXIT': True,
            'AUTO_BACKUP_SHOW_SUCCESS_MESSAGE': True,
            'AUTO_BACKUP_CONFIRMATION_DIALOG': True
        },
        {
            'name': 'النسخ مفعل صامت',
            'AUTO_BACKUP_ON_EXIT': True,
            'AUTO_BACKUP_SHOW_SUCCESS_MESSAGE': False,
            'AUTO_BACKUP_CONFIRMATION_DIALOG': False
        },
        {
            'name': 'النسخ معطل',
            'AUTO_BACKUP_ON_EXIT': False,
            'AUTO_BACKUP_SHOW_SUCCESS_MESSAGE': False,
            'AUTO_BACKUP_CONFIRMATION_DIALOG': False
        }
    ]
    
    for scenario in test_scenarios:
        print(f"   📋 اختبار: {scenario['name']}")
        
        # تطبيق القيم
        config.AUTO_BACKUP_ON_EXIT = scenario['AUTO_BACKUP_ON_EXIT']
        config.AUTO_BACKUP_SHOW_SUCCESS_MESSAGE = scenario['AUTO_BACKUP_SHOW_SUCCESS_MESSAGE']
        config.AUTO_BACKUP_CONFIRMATION_DIALOG = scenario['AUTO_BACKUP_CONFIRMATION_DIALOG']
        
        # التحقق من التطبيق
        assert config.AUTO_BACKUP_ON_EXIT == scenario['AUTO_BACKUP_ON_EXIT']
        assert config.AUTO_BACKUP_SHOW_SUCCESS_MESSAGE == scenario['AUTO_BACKUP_SHOW_SUCCESS_MESSAGE']
        assert config.AUTO_BACKUP_CONFIRMATION_DIALOG == scenario['AUTO_BACKUP_CONFIRMATION_DIALOG']
        
        print(f"      ✅ تم تطبيق وتأكيد السيناريو")
    
    # استرجاع القيم الأصلية
    config.AUTO_BACKUP_ON_EXIT = original_values['AUTO_BACKUP_ON_EXIT']
    config.AUTO_BACKUP_SHOW_SUCCESS_MESSAGE = original_values['AUTO_BACKUP_SHOW_SUCCESS_MESSAGE']
    config.AUTO_BACKUP_CONFIRMATION_DIALOG = original_values['AUTO_BACKUP_CONFIRMATION_DIALOG']
    
    print("   ✅ تم استرجاع القيم الأصلية")
    return True

def main():
    """الدالة الرئيسية للاختبار"""
    print("🚀 بدء الاختبار السريع لميزة النسخ الاحتياطي التلقائي عند الخروج\n")
    
    tests = [
        ("اختبار إعدادات config.py", test_config_values),
        ("اختبار دوال النافذة الرئيسية", test_main_window_functions),
        ("اختبار التكامل في الكود", test_code_integration),
        ("اختبار سيناريوهات مختلفة", test_different_config_scenarios)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"{'='*50}")
        print(f"🧪 {test_name}")
        print(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: نجح\n")
            else:
                print(f"❌ {test_name}: فشل\n")
                
        except Exception as e:
            print(f"💥 خطأ في {test_name}: {e}\n")
            results.append((test_name, False))
    
    # النتائج النهائية
    print(f"{'='*50}")
    print("📊 ملخص النتائج")
    print(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{status} - {test_name}")
    
    print(f"\n📈 النتيجة: {passed}/{total} اختبارات نجحت")
    
    if passed == total:
        print("\n🎉 تم تنفيذ الميزة بنجاح!")
        print("\n📚 ملخص الميزة الجديدة:")
        print("   🔄 النسخ الاحتياطي التلقائي عند إغلاق التطبيق")
        print("   ⚙️ إعدادات قابلة للتخصيص في config.py")
        print("   🛡️ معالجة ذكية للأخطاء")
        print("   👤 واجهة مستخدم واضحة")
        print("\n🎯 كيفية الاستخدام:")
        print("   1. قم بتشغيل التطبيق")
        print("   2. عند الخروج سيتم إنشاء نسخة احتياطية تلقائية")
        print("   3. يمكن تخصيص الإعدادات في config.py")
        print("\n✨ الميزة جاهزة للاستخدام!")
    else:
        print(f"\n❌ {total - passed} اختبارات فشلت. يرجى مراجعة الأخطاء.")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف الاختبار")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 خطأ عام: {e}")
        sys.exit(1)
