#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعادة إنشاء قاعدة البيانات مع العمود الجديد school_id في جدول الرواتب
"""

import os
import sys
import logging
from pathlib import Path

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from core.database.connection import db_manager

def recreate_database():
    """حذف قاعدة البيانات القديمة وإنشاء واحدة جديدة"""
    try:
        print("🔄 بدء إعادة إنشاء قاعدة البيانات...")
        
        # إغلاق أي اتصال موجود
        db_manager.close_connection()
        
        # حذف ملف قاعدة البيانات إذا كان موجوداً
        if config.DATABASE_PATH.exists():
            print(f"🗑️ حذف قاعدة البيانات القديمة: {config.DATABASE_PATH}")
            config.DATABASE_PATH.unlink()
        
        # إنشاء قاعدة البيانات الجديدة
        print("🏗️ إنشاء قاعدة البيانات الجديدة...")
        db_manager.initialize_database()
        
        print("✅ تم إعادة إنشاء قاعدة البيانات بنجاح!")
        print("📝 قاعدة البيانات الجديدة تحتوي على:")
        print("   - عمود school_id في جدول الرواتب")
        print("   - جميع الفهارس المحدثة")
        print("   - المفاتيح الأجنبية الصحيحة")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إعادة إنشاء قاعدة البيانات: {e}")
        logging.error(f"خطأ في إعادة إنشاء قاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    success = recreate_database()
    if success:
        print("\n🎉 يمكنك الآن:")
        print("1. تشغيل سكريبت البيانات التجريبية: python 'test data/generate_test_data.py'")
        print("2. تشغيل التطبيق: python main.py")
    else:
        print("\n❌ فشل في إعادة إنشاء قاعدة البيانات")
        sys.exit(1)
