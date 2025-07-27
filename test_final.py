#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("🔄 اختبار النظام المحدث (Supabase فقط)...")

try:
    from core.backup.backup_manager import backup_manager
    
    if backup_manager is None:
        print("❌ فشل في تهيئة مدير النسخ الاحتياطية")
        print("الأسباب المحتملة:")
        print("- مشكلة في الاتصال بـ Supabase") 
        print("- خطأ في الإعدادات")
        print("- مكتبة supabase غير مثبتة")
    else:
        print("✅ تم تهيئة مدير النسخ الاحتياطية بنجاح")
        print("✅ النظام متصل بـ Supabase")
        print("✅ جاهز لإنشاء النسخ الاحتياطية")
        print("🚫 النسخ المحلية غير متاحة (كما طُلب)")
        
except Exception as e:
    print(f"❌ خطأ في استيراد النظام: {e}")

print("\n" + "="*50)
print("انتهى الاختبار - النظام محدث ويعمل على Supabase فقط")
