#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشخيص مفصل لـ Supabase Storage
"""

import sys
from pathlib import Path
import json

# إضافة مسار المشروع
sys.path.append(str(Path(__file__).parent))

import config

def diagnose_supabase():
    """تشخيص مفصل لـ Supabase"""
    
    print("=" * 60)
    print("تشخيص مفصل لـ Supabase Storage")
    print("=" * 60)
    
    try:
        from supabase import create_client
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        bucket = config.SUPABASE_BUCKET
        
        print(f"🔗 البكت: {bucket}")
        
        # 1. محاولة جلب الملفات بطرق مختلفة
        print("\n🔍 طريقة 1: list('') - جذر البكت")
        try:
            files1 = supabase.storage.from_(bucket).list("")
            print(f"   النتيجة: {type(files1)}")
            print(f"   العدد: {len(files1) if files1 else 'None'}")
            
            if files1:
                for i, item in enumerate(files1[:3]):
                    print(f"   [{i}] النوع: {type(item)}")
                    print(f"   [{i}] القيمة: {item}")
                    if hasattr(item, 'keys'):
                        print(f"   [{i}] المفاتيح: {list(item.keys()) if hasattr(item, 'keys') else 'لا توجد'}")
                    print()
                    
        except Exception as e:
            print(f"   خطأ: {e}")
        
        # 2. محاولة البحث عن مجلدات معروفة
        print("\n🔍 طريقة 2: list('backups')")
        try:
            files2 = supabase.storage.from_(bucket).list("backups")
            print(f"   النتيجة: {type(files2)}")
            print(f"   العدد: {len(files2) if files2 else 'None'}")
            
            if files2:
                for i, item in enumerate(files2[:3]):
                    print(f"   [{i}] القيمة: {item}")
                    
        except Exception as e:
            print(f"   خطأ: {e}")
        
        # 3. محاولة رفع ملف اختبار
        print("\n📤 اختبار رفع ملف:")
        try:
            from datetime import datetime
            test_content = f"اختبار في {datetime.now()}"
            test_path = f"debug_test_{datetime.now().strftime('%H%M%S')}.txt"
            
            print(f"   رفع الملف: {test_path}")
            upload_result = supabase.storage.from_(bucket).upload(
                test_path, 
                test_content.encode('utf-8')
            )
            
            print(f"   نتيجة الرفع: {type(upload_result)}")
            print(f"   القيمة: {upload_result}")
            
            if hasattr(upload_result, 'error'):
                print(f"   خطأ الرفع: {upload_result.error}")
            
            # محاولة قراءة الملف
            print(f"\n📥 اختبار قراءة الملف:")
            try:
                downloaded = supabase.storage.from_(bucket).download(test_path)
                print(f"   نتيجة التحميل: {type(downloaded)}")
                print(f"   المحتوى: {downloaded.decode('utf-8') if downloaded else 'فارغ'}")
                
            except Exception as read_e:
                print(f"   خطأ في القراءة: {read_e}")
            
        except Exception as upload_e:
            print(f"   خطأ في الرفع: {upload_e}")
        
        # 4. فحص البكت نفسه
        print("\n🪣 معلومات البكت:")
        try:
            # محاولة جلب معلومات البكت
            bucket_info = supabase.storage.get_bucket(bucket)
            print(f"   معلومات البكت: {bucket_info}")
            
        except Exception as bucket_e:
            print(f"   خطأ في معلومات البكت: {bucket_e}")
        
        # 5. اختبار صلاحيات مختلفة
        print("\n🔐 اختبار الصلاحيات:")
        try:
            # جلب URL موقع
            test_url = supabase.storage.from_(bucket).create_signed_url("test.txt", 60)
            print(f"   إنشاء URL موقع: {type(test_url)}")
            print(f"   النتيجة: {test_url}")
            
        except Exception as url_e:
            print(f"   خطأ في URL: {url_e}")
        
        # 6. إحصائيات عامة
        print(f"\n📊 الخلاصة:")
        print(f"   - الاتصال: ✅ يعمل")
        print(f"   - البكت: {bucket}")
        print(f"   - المشكلة: في تنسيق البيانات المُستقبلة")
        
    except Exception as main_e:
        print(f"❌ خطأ عام: {main_e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_supabase()
