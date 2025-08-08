#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعادة إنشاء قاعدة البيانات مع جميع الجداول المطلوبة
"""

import sys
import os
import logging
from pathlib import Path

# إضافة المسار الجذر للمشروع
sys.path.insert(0, str(Path(__file__).parent))

import config
from core.database.connection import db_manager

def recreate_database():
    """إعادة إنشاء قاعدة البيانات"""
    try:
        print("بدء إعادة إنشاء قاعدة البيانات...")
        
        # إغلاق أي اتصالات موجودة
        db_manager.close_connection()
        
        # حذف قاعدة البيانات إذا كانت موجودة
        if config.DATABASE_PATH.exists():
            config.DATABASE_PATH.unlink()
            print("تم حذف قاعدة البيانات القديمة")
        
        # إعادة إنشاء قاعدة البيانات
        print("إنشاء قاعدة البيانات الجديدة...")
        success = db_manager.initialize_database()
        
        if success:
            print("✅ تم إعادة إنشاء قاعدة البيانات بنجاح!")
            
            # التحقق من الجداول المنشأة
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print("\nالجداول المنشأة:")
                for table in tables:
                    print(f"  - {table[0]}")
            
            return True
        else:
            print("❌ فشل في إعادة إنشاء قاعدة البيانات")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في إعادة إنشاء قاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    # إعداد نظام التسجيل
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/database_recreate.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    success = recreate_database()
    if success:
        print("\n🎉 تم إعادة إنشاء قاعدة البيانات بنجاح!")
        print("يمكنك الآن تشغيل التطبيق دون مشاكل.")
    else:
        print("\n💥 فشل في إعادة إنشاء قاعدة البيانات!")
        sys.exit(1)
