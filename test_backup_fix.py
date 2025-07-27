#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار النظام المُحدث للنسخ الاحتياطية
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.backup.backup_manager import backup_manager
    print("✅ تم تحميل backup_manager بنجاح")
    print(f"نوع backup_manager: {type(backup_manager)}")
    
    # اختبار دالة create_backup
    if hasattr(backup_manager, 'create_backup'):
        print("✅ دالة create_backup موجودة")
        
        # تنفيذ اختبار النسخ الاحتياطي
        print("\n🔄 بدء اختبار النسخ الاحتياطي...")
        success, message = backup_manager.create_backup("اختبار النظام المُحدث - طريقة مبسطة")
        
        if success:
            print(f"✅ نجح إنشاء النسخة الاحتياطية: {message}")
        else:
            print(f"❌ فشل إنشاء النسخة الاحتياطية: {message}")
    else:
        print("❌ دالة create_backup غير موجودة")
        
except Exception as e:
    print(f"❌ خطأ في الاختبار: {e}")
    import traceback
    traceback.print_exc()
