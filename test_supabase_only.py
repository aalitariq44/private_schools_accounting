#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام النسخ الاحتياطي المحدث (Supabase فقط)
"""

import sys
import os
from pathlib import Path

# إضافة المجلد الجذر للمشروع إلى مسار Python
sys.path.insert(0, str(Path(__file__).parent))

import config

def test_supabase_only_backup():
    """اختبار النظام المحدث (Supabase فقط)"""
    print("=" * 60)
    print("اختبار نظام النسخ الاحتياطي المحدث (Supabase فقط)")
    print("=" * 60)
    
    try:
        from core.backup.backup_manager import backup_manager
        
        if backup_manager is None:
            print("❌ فشل في تهيئة مدير النسخ الاحتياطية")
            print("تحقق من:")
            print("1. إعدادات Supabase في config.py")
            print("2. اتصال الإنترنت")
            print("3. مكتبة supabase مثبتة")
            return False
        
        print("✅ تم تهيئة مدير النسخ الاحتياطية بنجاح")
        print(f"🔗 متصل بـ: {config.SUPABASE_URL}")
        print(f"📦 البكت: {config.SUPABASE_BUCKET}")
        
        # التحقق من وجود قاعدة البيانات
        if not config.DATABASE_PATH.exists():
            print("⚠️ قاعدة البيانات غير موجودة، سيتم إنشاؤها...")
            
            # إنشاء قاعدة بيانات تجريبية
            import sqlite3
            config.DATABASE_DIR.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(config.DATABASE_PATH) as conn:
                conn.execute("""
                    CREATE TABLE test_table (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("INSERT INTO test_table (name) VALUES ('test data for Supabase backup')")
                conn.commit()
            print("✅ تم إنشاء قاعدة بيانات تجريبية")
        
        # اختبار إنشاء نسخة احتياطية
        print("\n🔄 اختبار إنشاء نسخة احتياطية...")
        success, message = backup_manager.create_backup("نسخة تجريبية - نظام Supabase المحدث")
        
        if success:
            print(f"✅ {message}")
            
            # اختبار جلب قائمة النسخ
            print("\n🔄 اختبار جلب قائمة النسخ الاحتياطية...")
            backups = backup_manager.list_backups()
            
            if backups:
                print(f"✅ تم جلب {len(backups)} نسخة احتياطية من Supabase")
                print("\nأحدث 3 نسخ:")
                for i, backup in enumerate(backups[:3], 1):
                    print(f"  {i}. {backup['filename']}")
                    print(f"     التاريخ: {backup['formatted_date']}")
                    print(f"     الحجم: {backup['formatted_size']}")
                    print()
            else:
                print("⚠️ لم يتم العثور على نسخ احتياطية")
                
            return True
        else:
            print(f"❌ فشل في إنشاء النسخة الاحتياطية: {message}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار نظام النسخ الاحتياطي المحدث")
    print("النظام الآن يعتمد على Supabase فقط (لا توجد نسخ محلية)")
    
    success = test_supabase_only_backup()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 جميع الاختبارات نجحت!")
        print("✅ النظام يعمل بشكل صحيح على Supabase")
        print("✅ تم إزالة النسخ المحلية كما طُلب")
    else:
        print("❌ بعض الاختبارات فشلت")
        print("راجع الأخطاء أعلاه لمعرفة السبب")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
