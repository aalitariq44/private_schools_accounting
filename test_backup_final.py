#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لمدير النسخ الاحتياطي في التطبيق
"""

import sys
from pathlib import Path

# إضافة مسار المشروع
sys.path.append(str(Path(__file__).parent))

def test_backup_in_app():
    """اختبار مدير النسخ الاحتياطي داخل التطبيق"""
    
    print("=" * 50)
    print("اختبار مدير النسخ الاحتياطي في التطبيق")
    print("=" * 50)
    
    try:
        # استيراد مدير النسخ من التطبيق
        from core.backup.backup_manager import BackupManager
        
        print("✅ تم استيراد مدير النسخ بنجاح")
        
        # إنشاء مدير النسخ
        backup_manager = BackupManager()
        print("✅ تم إنشاء مدير النسخ بنجاح")
        
        # اختبار قائمة النسخ الاحتياطية
        print("\n📋 جلب قائمة النسخ الاحتياطية...")
        backups = backup_manager.list_backups()
        
        print(f"✅ تم جلب {len(backups)} نسخة احتياطية")
        
        if backups:
            print("\n📦 النسخ الاحتياطية المتاحة:")
            for i, backup in enumerate(backups[:5]):  # أول 5 نسخ
                print(f"  {i+1}. {backup['filename']}")
                print(f"     التاريخ: {backup['formatted_date']}")
                print(f"     الحجم: {backup['formatted_size']}")
                print(f"     المسار: {backup['path']}")
                print()
        else:
            print("⚠️ لم يتم العثور على نسخ احتياطية")
        
        # اختبار إنشاء نسخة احتياطية جديدة (اختياري)
        print("🆕 هل تريد إنشاء نسخة احتياطية جديدة للاختبار؟ (y/n): ", end="")
        response = input().strip().lower()
        
        if response in ['y', 'yes', 'نعم', 'ن']:
            print("📤 إنشاء نسخة احتياطية جديدة...")
            success, message = backup_manager.create_backup("اختبار من السكريبت")
            
            if success:
                print(f"✅ {message}")
                
                # جلب القائمة مرة أخرى للتأكد
                print("🔄 تحديث قائمة النسخ...")
                updated_backups = backup_manager.list_backups()
                print(f"📋 العدد الجديد: {len(updated_backups)} نسخة")
                
            else:
                print(f"❌ فشل في إنشاء النسخة: {message}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_backup_in_app()
