#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لنظام النسخ الاحتياطية
"""

import sys
import os
import logging
from pathlib import Path

# إضافة مسار المشروع إلى sys.path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

import config
from core.backup.backup_manager import backup_manager


def test_backup_system():
    """اختبار نظام النسخ الاحتياطية"""
    print("🚀 بدء اختبار نظام النسخ الاحتياطية...")
    print("=" * 50)
    
    try:
        # 1. اختبار الاتصال بـ Supabase
        print("📡 اختبار الاتصال بـ Supabase...")
        
        # محاولة جلب قائمة النسخ (اختبار بسيط للاتصال)
        backups = backup_manager.list_backups()
        print(f"✅ نجح الاتصال! تم العثور على {len(backups)} نسخة احتياطية")
        
        # 2. عرض النسخ الموجودة
        if backups:
            print("\n📋 النسخ الاحتياطية الموجودة:")
            print("-" * 30)
            for i, backup in enumerate(backups[:5], 1):  # عرض أول 5 نسخ فقط
                print(f"{i}. {backup['filename']}")
                print(f"   📅 التاريخ: {backup['formatted_date']}")
                print(f"   📦 الحجم: {backup['formatted_size']}")
                print()
        else:
            print("📋 لا توجد نسخ احتياطية مسبقة")
        
        # 3. اختبار إنشاء نسخة احتياطية (اختياري)
        test_create = input("\n❓ هل تريد اختبار إنشاء نسخة احتياطية؟ (y/n): ")
        
        if test_create.lower() == 'y':
            print("\n🔄 إنشاء نسخة احتياطية تجريبية...")
            
            success, message = backup_manager.create_backup("نسخة اختبار - تم الإنشاء من ملف الاختبار")
            
            if success:
                print("✅ تم إنشاء النسخة الاحتياطية بنجاح!")
                print(f"📝 التفاصيل: {message}")
            else:
                print("❌ فشل في إنشاء النسخة الاحتياطية")
                print(f"💬 الخطأ: {message}")
        
        print("\n" + "=" * 50)
        print("🎉 انتهى الاختبار بنجاح!")
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        print("\n🔧 نصائح لحل المشكلة:")
        print("1. تأكد من الاتصال بالإنترنت")
        print("2. تحقق من تثبيت المكتبات: pip install supabase storage3")
        print("3. تأكد من صحة إعدادات Supabase في config.py")
        return False
    
    return True


def test_requirements():
    """اختبار المتطلبات"""
    print("🔍 فحص المتطلبات...")
    
    requirements = [
        ("supabase", "مكتبة Supabase"),
        ("storage3", "مكتبة Storage3"),
        ("sqlite3", "قاعدة البيانات SQLite"),
        ("zipfile", "مكتبة الضغط"),
        ("datetime", "مكتبة التاريخ والوقت")
    ]
    
    missing = []
    
    for module, description in requirements:
        try:
            __import__(module)
            print(f"✅ {description}")
        except ImportError:
            print(f"❌ {description} - غير مثبت!")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️  المكتبات المفقودة: {', '.join(missing)}")
        print("💡 قم بتشغيل: install_backup_libs.bat")
        return False
    
    print("✅ جميع المتطلبات متوفرة!")
    return True


def main():
    """الدالة الرئيسية"""
    print("🏫 نظام حسابات المدارس الأهلية")
    print("🔒 اختبار نظام النسخ الاحتياطية")
    print("=" * 50)
    
    # فحص المتطلبات أولاً
    if not test_requirements():
        input("\nاضغط Enter للخروج...")
        return
    
    print()
    
    # اختبار النظام
    if test_backup_system():
        print("\n✨ النظام جاهز للاستخدام!")
    else:
        print("\n⚠️  يحتاج النظام إلى إعداد إضافي")
    
    input("\nاضغط Enter للخروج...")


if __name__ == "__main__":
    main()
