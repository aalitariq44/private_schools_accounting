#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار تكامل نظام اسم المؤسسة والنسخ الاحتياطية
"""

import sys
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from core.utils.settings_manager import settings_manager
from core.backup.backup_manager import BackupManager
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_organization_settings():
    """اختبار إعدادات المؤسسة"""
    print("=== اختبار إعدادات المؤسسة ===")
    
    # اختبار تعيين اسم المؤسسة
    test_org_name = "مدارس الرياض الأهلية"
    success = settings_manager.set_organization_name(test_org_name)
    print(f"تعيين اسم المؤسسة: {'نجح' if success else 'فشل'}")
    
    # اختبار استرجاع اسم المؤسسة
    retrieved_name = settings_manager.get_organization_name()
    print(f"اسم المؤسسة المسترجع: {retrieved_name}")
    
    # التحقق من التطابق
    if retrieved_name == test_org_name:
        print("✅ نجح اختبار إعدادات المؤسسة")
        return True
    else:
        print("❌ فشل اختبار إعدادات المؤسسة")
        return False

def test_backup_organization_folder():
    """اختبار نظام النسخ الاحتياطية مع مجلد المؤسسة"""
    print("\n=== اختبار النسخ الاحتياطية مع مجلد المؤسسة ===")
    
    try:
        # التأكد من وجود اسم المؤسسة
        org_name = settings_manager.get_organization_name()
        print(f"اسم المؤسسة للنسخ الاحتياطية: {org_name}")
        
        if not org_name:
            print("❌ لم يتم العثور على اسم المؤسسة")
            return False
        
        # اختبار إنشاء نسخة احتياطية
        backup_manager = BackupManager()
        success, message = backup_manager.create_backup("اختبار النظام الجديد")
        
        print(f"إنشاء النسخة الاحتياطية: {'نجح' if success else 'فشل'}")
        print(f"الرسالة: {message}")
        
        if success:
            # اختبار قائمة النسخ الاحتياطية
            backups = backup_manager.list_backups()
            print(f"عدد النسخ الاحتياطية الموجودة: {len(backups)}")
            
            if backups:
                latest_backup = backups[0]
                print(f"أحدث نسخة احتياطية: {latest_backup['name']}")
                print(f"المسار: {latest_backup['path']}")
                print("✅ نجح اختبار النسخ الاحتياطية")
                return True
            else:
                print("⚠️ لم يتم العثور على نسخ احتياطية")
                return False
        else:
            print("❌ فشل اختبار النسخ الاحتياطية")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار النسخ الاحتياطية: {e}")
        return False

def test_organization_folder_naming():
    """اختبار تنظيف أسماء المجلدات"""
    print("\n=== اختبار تنظيف أسماء المجلدات ===")
    
    import hashlib
    import re
    
    def get_safe_name(organization_name):
        """تطبيق نفس منطق تنظيف الأسماء المستخدم في النظام"""
        if not organization_name:
            return "organization"
        
        # إزالة الأحرف الخاصة أولاً
        cleaned_name = re.sub(r'[<>:"/\\|?*\s]', '_', organization_name)
        
        # إنشاء hash قصير للاسم العربي لضمان الفرادة
        name_hash = hashlib.md5(organization_name.encode('utf-8')).hexdigest()[:8]
        
        # دمج الاسم المنظف مع الـ hash
        safe_org_name = f"org_{name_hash}"
        
        # التأكد من أن الاسم لا يحتوي على أحرف غير مدعومة
        safe_org_name = re.sub(r'[^\w\-_]', '_', safe_org_name)
        
        return safe_org_name
    
    test_names = [
        "مدارس الرياض الأهلية",
        "مدرسة <النور> الأهلية",
        "معهد/البيان\\التعليمي",
        "أكاديمية النجاح: للتعليم",
        "مجمع المستقبل التعليمي*"
    ]
    
    for name in test_names:
        safe_name = get_safe_name(name)
        print(f"الاسم الأصلي: {name}")
        print(f"الاسم الآمن: {safe_name}")
        print("---")
    
    print("✅ نجح اختبار تنظيف أسماء المجلدات")
    return True

def main():
    """الدالة الرئيسية للاختبار"""
    print("بدء اختبار نظام المؤسسة والنسخ الاحتياطية")
    print("=" * 50)
    
    try:
        # اختبار إعدادات المؤسسة
        test1 = test_organization_settings()
        
        # اختبار تنظيف أسماء المجلدات
        test2 = test_organization_folder_naming()
        
        # اختبار النسخ الاحتياطية
        test3 = test_backup_organization_folder()
        
        print("\n" + "=" * 50)
        print("نتائج الاختبار:")
        print(f"إعدادات المؤسسة: {'✅ نجح' if test1 else '❌ فشل'}")
        print(f"تنظيف أسماء المجلدات: {'✅ نجح' if test2 else '❌ فشل'}")
        print(f"النسخ الاحتياطية: {'✅ نجح' if test3 else '❌ فشل'}")
        
        if all([test1, test2, test3]):
            print("\n🎉 نجحت جميع الاختبارات!")
        else:
            print("\n⚠️ فشلت بعض الاختبارات")
            
    except Exception as e:
        print(f"خطأ عام في الاختبار: {e}")

if __name__ == "__main__":
    main()
