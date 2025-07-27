#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار النسخ الاحتياطية
"""

try:
    print("1. محاولة استيراد المكتبات...")
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    print("2. استيراد config...")
    import config
    print(f"   DATABASE_PATH: {config.DATABASE_PATH}")
    print(f"   DATABASE exists: {config.DATABASE_PATH.exists()}")
    
    print("3. استيراد supabase...")
    from supabase import create_client
    print("   ✅ supabase imported successfully")
    
    print("4. إنشاء client...")
    supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    print("   ✅ supabase client created")
    
    print("5. اختبار الاتصال...")
    buckets = supabase.storage.list_buckets()
    print(f"   ✅ Connection successful, buckets: {len(buckets)}")
    
    print("6. اختبار backup_manager...")
    from core.backup.backup_manager import backup_manager
    print(f"   backup_manager type: {type(backup_manager)}")
    
    print("7. اختبار create_backup...")
    success, message = backup_manager.create_backup("اختبار بسيط")
    print(f"   Result: {success}, Message: {message}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
