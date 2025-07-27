#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إنشاء نسخة احتياطية على Supabase
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import config
from core.backup.backup_manager import backup_manager
import sqlite3

def main():
    print("🔄 اختبار إنشاء نسخة احتياطية على Supabase")
    print("=" * 60)
    
    # التحقق من حالة Supabase
    if backup_manager.supabase is None:
        print("❌ عميل Supabase غير متاح")
        print("تحقق من اللوغات للمزيد من التفاصيل")
        return False
    else:
        print("✅ عميل Supabase متاح")
    
    # التحقق من وجود قاعدة البيانات أو إنشاؤها
    if not config.DATABASE_PATH.exists():
        print("⚠️ قاعدة البيانات غير موجودة، سيتم إنشاؤها...")
        config.DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        
        # إنشاء قاعدة بيانات تجريبية
        with sqlite3.connect(config.DATABASE_PATH) as conn:
            conn.execute("""
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("INSERT INTO test_table (name) VALUES ('test data for backup')")
            conn.commit()
        print("✅ تم إنشاء قاعدة بيانات تجريبية")
    else:
        print(f"✅ قاعدة البيانات موجودة: {config.DATABASE_PATH}")
    
    # إنشاء النسخة الاحتياطية
    print("\n🔄 إنشاء النسخة الاحتياطية...")
    success, message = backup_manager.create_backup("نسخة احتياطية تجريبية - اختبار Supabase")
    
    if success:
        print(f"✅ {message}")
        
        # جلب قائمة النسخ الاحتياطية للتأكد
        print("\n🔄 جلب قائمة النسخ الاحتياطية...")
        backups = backup_manager.list_backups()
        
        if backups:
            print(f"✅ تم جلب {len(backups)} نسخة احتياطية")
            if len(backups) > 0:
                latest = backups[0]
                print(f"أحدث نسخة: {latest['filename']} - {latest['formatted_date']}")
        else:
            print("⚠️ لم يتم العثور على نسخ احتياطية")
        
        return True
    else:
        print(f"❌ فشل في إنشاء النسخة الاحتياطية: {message}")
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 60)
    if success:
        print("🎉 الاختبار نجح! نظام النسخ الاحتياطي يعمل على Supabase")
    else:
        print("❌ الاختبار فشل! تحقق من الإعدادات واللوغات")
    
    sys.exit(0 if success else 1)
