#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import config
    print(f"✅ إعدادات Supabase:")
    print(f"URL: {config.SUPABASE_URL}")
    print(f"Bucket: {config.SUPABASE_BUCKET}")
    
    from core.backup.backup_manager import backup_manager
    
    if backup_manager.supabase is None:
        print("❌ عميل Supabase غير متاح")
    else:
        print("✅ عميل Supabase متاح ومُهيأ")
        
        # اختبار الاتصال
        try:
            buckets = backup_manager.supabase.storage.list_buckets()
            print(f"✅ نجح الاتصال بـ Supabase - عدد البكتات: {len(buckets)}")
            
            # التحقق من البكت المطلوب
            bucket_names = [bucket.name for bucket in buckets]
            if config.SUPABASE_BUCKET in bucket_names:
                print(f"✅ البكت موجود: {config.SUPABASE_BUCKET}")
            else:
                print(f"⚠️ البكت غير موجود، سيتم إنشاؤه: {config.SUPABASE_BUCKET}")
                print(f"البكتات المتاحة: {bucket_names}")
                
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            
except Exception as e:
    print(f"❌ خطأ: {e}")
    import traceback
    traceback.print_exc()
