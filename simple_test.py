#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔧 اختبار نظام الرواتب...")
    
    # فحص الملفات الأساسية
    files_to_check = [
        "ui/pages/salaries/salaries_page.py",
        "ui/pages/salaries/add_salary_dialog.py",
        "update_db_for_salaries.py"
    ]
    
    print("\n📁 فحص الملفات:")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - غير موجود")
    
    # فحص قاعدة البيانات
    db_path = "data/database/schools.db"
    if os.path.exists(db_path):
        print(f"\n✅ قاعدة البيانات موجودة: {db_path}")
        
        # محاولة استيراد إدارة قاعدة البيانات
        try:
            from core.database.connection import db_manager
            print("✅ تم استيراد مدير قاعدة البيانات بنجاح")
            
            # تهيئة قاعدة البيانات
            db_manager.initialize_database()
            print("✅ تم تهيئة قاعدة البيانات بنجاح")
            
        except Exception as e:
            print(f"❌ خطأ في استيراد مدير قاعدة البيانات: {e}")
    else:
        print(f"\n❌ قاعدة البيانات غير موجودة: {db_path}")
    
    print("\n✅ انتهاء اختبار النظام")
    
except Exception as e:
    print(f"❌ خطأ عام: {e}")
    import traceback
    traceback.print_exc()
