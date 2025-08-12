#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار اتصال Supabase بسيط
"""

import sys
from pathlib import Path

# إضافة مسار المشروع
sys.path.append(str(Path(__file__).parent))

import config

def test_supabase_connection():
    """اختبار الاتصال مع Supabase"""
    
    print("=" * 50)
    print("اختبار اتصال Supabase Storage")
    print("=" * 50)
    
    # 1. التحقق من المكتبات
    try:
        from supabase import create_client
        print("✅ مكتبة Supabase مثبتة")
    except ImportError:
        print("❌ مكتبة Supabase غير مثبتة")
        print("قم بتثبيتها: pip install supabase")
        return False
    
    # 2. التحقق من الإعدادات
    try:
        url = config.SUPABASE_URL
        key = config.SUPABASE_KEY
        bucket = config.SUPABASE_BUCKET
        
        print(f"✅ URL: {url[:30]}...")
        print(f"✅ Key: {key[:30]}...")
        print(f"✅ Bucket: {bucket}")
        
    except AttributeError as e:
        print(f"❌ إعدادات Supabase ناقصة: {e}")
        return False
    
    # 3. إنشاء العميل
    try:
        supabase = create_client(url, key)
        print("✅ تم إنشاء عميل Supabase")
    except Exception as e:
        print(f"❌ فشل في إنشاء العميل: {e}")
        return False
    
    # 4. اختبار الوصول للتخزين
    try:
        # جلب قائمة الملفات العامة
        files = supabase.storage.from_(bucket).list("")
        print(f"✅ تم الوصول للبكت بنجاح")
        print(f"📁 عدد الملفات/المجلدات: {len(files) if files else 0}")
        
        # التحقق من صحة البيانات
        if files and len(files) > 0:
            print("📋 قائمة الملفات:")
            for i, file_item in enumerate(files[:5]):
                if file_item and isinstance(file_item, dict):
                    name = file_item.get('name', 'بدون اسم')
                    size = file_item.get('metadata', {}).get('size', 'غير معروف')
                    print(f"   {i+1}. {name} ({size} bytes)")
                else:
                    print(f"   {i+1}. عنصر غير صالح: {file_item}")
        else:
            print("📁 البكت فارغ أو لا توجد ملفات")
            
    except Exception as e:
        print(f"❌ فشل في الوصول للبكت: {e}")
        return False
    
    # 5. اختبار البحث عن النسخ الاحتياطية
    try:
        print("\n🔍 البحث عن النسخ الاحتياطية...")
        backup_files = []
        
        if files:
            for file_item in files:
                if file_item and isinstance(file_item, dict):
                    name = file_item.get('name', '')
                    if 'backup' in name.lower() or name.endswith('.zip'):
                        backup_files.append(file_item)
        
        print(f"📦 عدد ملفات النسخ الاحتياطية المحتملة: {len(backup_files)}")
        
        for i, backup in enumerate(backup_files[:3]):
            if backup and isinstance(backup, dict):
                name = backup.get('name', 'بدون اسم')
                created = backup.get('created_at', 'غير معروف')
                print(f"   📄 {name} - {created}")
            
    except Exception as e:
        print(f"⚠️ مشكلة في البحث عن النسخ: {e}")
    
    # 6. اختبار رفع ملف بسيط
    try:
        print("\n📤 اختبار رفع ملف بسيط...")
        
        from datetime import datetime
        test_content = f"اختبار في {datetime.now()}\nهذا ملف اختبار بسيط"
        test_filename = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        test_path = f"test_files/{test_filename}"
        
        # رفع الملف
        upload_result = supabase.storage.from_(bucket).upload(
            test_path, 
            test_content.encode('utf-8')
        )
        
        if hasattr(upload_result, 'error') and upload_result.error:
            print(f"❌ فشل في رفع الملف: {upload_result.error}")
        else:
            print(f"✅ تم رفع الملف بنجاح: {test_path}")
            
            # محاولة قراءة الملف المرفوع
            try:
                downloaded_data = supabase.storage.from_(bucket).download(test_path)
                downloaded_content = downloaded_data.decode('utf-8')
                
                if test_content == downloaded_content:
                    print("✅ تم التحقق من صحة المحتوى")
                else:
                    print("⚠️ المحتوى المحمل مختلف عن المرفوع")
                    
            except Exception as read_e:
                print(f"❌ فشل في قراءة الملف: {read_e}")
        
    except Exception as e:
        print(f"❌ فشل في اختبار الرفع: {e}")
    
    print("\n" + "=" * 50)
    print("انتهى الاختبار")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_supabase_connection()
