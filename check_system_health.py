"""
فحص سلامة النظام قبل التصدير النهائي
"""

import os
import sys
import importlib
from pathlib import Path

def check_python_version():
    """فحص إصدار Python"""
    print("🔍 فحص إصدار Python...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - متوافق")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - غير متوافق (يتطلب 3.7+)")
        return False

def check_required_modules():
    """فحص الوحدات المطلوبة"""
    print("\n🔍 فحص الوحدات المطلوبة...")
    
    required_modules = [
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtWidgets',
        'PyQt5.QtWebEngineWidgets',
        'supabase',
        'reportlab',
        'PIL',
        'arabic_reshaper',
        'bidi',
        'bcrypt',
        'dotenv',
        'jinja2'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - مفقود")
            missing_modules.append(module)
    
    return len(missing_modules) == 0, missing_modules

def check_required_files():
    """فحص الملفات المطلوبة"""
    print("\n🔍 فحص الملفات المطلوبة...")
    
    required_files = [
        'main.py',
        'config.py',
        'printing_config.json',
        'app/main_window.py',
        'app/resources/images/icon.ico',
        'core',
        'ui',
        'data'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - مفقود")
            missing_files.append(file_path)
    
    return len(missing_files) == 0, missing_files

def check_main_py():
    """فحص ملف main.py"""
    print("\n🔍 فحص ملف main.py...")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'if __name__ == "__main__"' in content:
            print("✅ main.py - يحتوي على نقطة الدخول الصحيحة")
            return True
        else:
            print("❌ main.py - لا يحتوي على نقطة الدخول الصحيحة")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في قراءة main.py: {e}")
        return False

def check_pyinstaller():
    """فحص PyInstaller"""
    print("\n🔍 فحص PyInstaller...")
    
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} - جاهز")
        return True
    except ImportError:
        print("❌ PyInstaller - غير مثبت")
        return False

def main():
    """الفحص الرئيسي"""
    print("=" * 50)
    print("🔧 فحص سلامة النظام قبل التصدير النهائي")
    print("=" * 50)
    
    all_checks_passed = True
    
    # فحص Python
    if not check_python_version():
        all_checks_passed = False
    
    # فحص الوحدات
    modules_ok, missing_modules = check_required_modules()
    if not modules_ok:
        all_checks_passed = False
        print(f"\n❌ وحدات مفقودة: {', '.join(missing_modules)}")
        print("يرجى تثبيتها باستخدام: pip install -r requirements_final.txt")
    
    # فحص الملفات
    files_ok, missing_files = check_required_files()
    if not files_ok:
        all_checks_passed = False
        print(f"\n❌ ملفات مفقودة: {', '.join(missing_files)}")
    
    # فحص main.py
    if not check_main_py():
        all_checks_passed = False
    
    # فحص PyInstaller
    if not check_pyinstaller():
        all_checks_passed = False
    
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 جميع الفحوصات نجحت! النظام جاهز للتصدير")
        print("يمكنك الآن تشغيل: build_final_distribution.bat")
    else:
        print("⚠️  يوجد مشاكل يجب حلها قبل التصدير")
        print("يرجى إصلاح المشاكل المذكورة أعلاه")
    print("=" * 50)
    
    return all_checks_passed

if __name__ == "__main__":
    main()
    input("\nاضغط Enter للخروج...")
