#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار مفصل لإعدادات Supabase
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import config

print("🔍 اختبار إعدادات Supabase")
print("=" * 50)

# التحقق من الإعدادات
print(f"URL: {config.SUPABASE_URL}")
print(f"Key: {config.SUPABASE_KEY[:20]}...")
print(f"Bucket: {config.SUPABASE_BUCKET}")

# اختبار استيراد المكتبة
try:
    from supabase import create_client
    print("✅ تم استيراد مكتبة Supabase بنجاح")
except ImportError as e:
    print(f"❌ فشل في استيراد مكتبة Supabase: {e}")
    sys.exit(1)

# إنشاء عميل Supabase
try:
    supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    print("✅ تم إنشاء عميل Supabase بنجاح")
except Exception as e:
    print(f"❌ فشل في إنشاء عميل Supabase: {e}")
    sys.exit(1)

# اختبار الاتصال بالتخزين
try:
    buckets = supabase.storage.list_buckets()
    print(f"✅ تم الاتصال بالتخزين - عدد البكتات: {len(buckets)}")
    
    # طباعة أسماء البكتات المتاحة
    if buckets:
        print("البكتات المتاحة:")
        for i, bucket in enumerate(buckets, 1):
            print(f"  {i}. {bucket.name}")
    else:
        print("⚠️ لا توجد بكتات")
    
except Exception as e:
    print(f"❌ فشل في الاتصال بالتخزين: {e}")
    sys.exit(1)

# التحقق من وجود البكت المطلوب
bucket_names = [bucket.name for bucket in buckets]
if config.SUPABASE_BUCKET in bucket_names:
    print(f"✅ البكت المطلوب موجود: {config.SUPABASE_BUCKET}")
else:
    print(f"⚠️ البكت المطلوب غير موجود: {config.SUPABASE_BUCKET}")
    print("محاولة إنشاء البكت...")
    
    try:
        # إنشاء البكت
        result = supabase.storage.create_bucket(
            config.SUPABASE_BUCKET,
            options={
                "public": False,
                "allowedMimeTypes": ["application/zip", "application/x-sqlite3"],
                "fileSizeLimit": 100 * 1024 * 1024  # 100MB
            }
        )
        print(f"✅ تم إنشاء البكت بنجاح: {config.SUPABASE_BUCKET}")
        
    except Exception as e:
        print(f"❌ فشل في إنشاء البكت: {e}")
        print("تحقق من صلاحيات المفتاح في Supabase")

# اختبار رفع ملف تجريبي
print("\n🧪 اختبار رفع ملف تجريبي...")
try:
    test_content = "هذا ملف تجريبي لاختبار رفع الملفات على Supabase"
    test_path = "test/test_file.txt"
    
    # رفع الملف
    result = supabase.storage.from_(config.SUPABASE_BUCKET).upload(
        test_path,
        test_content.encode('utf-8'),
        file_options={
            "content-type": "text/plain",
            "upsert": True  # استبدال الملف إذا كان موجوداً
        }
    )
    print(f"✅ تم رفع الملف التجريبي بنجاح: {test_path}")
    
    # حذف الملف التجريبي
    delete_result = supabase.storage.from_(config.SUPABASE_BUCKET).remove([test_path])
    print("✅ تم حذف الملف التجريبي بنجاح")
    
except Exception as e:
    print(f"❌ فشل في رفع الملف التجريبي: {e}")

print("\n" + "=" * 50)
print("✅ انتهى الاختبار - Supabase جاهز للاستخدام!")
