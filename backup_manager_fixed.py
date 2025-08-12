#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح مدير النسخ الاحتياطي - نسخة مبسطة
"""

import os
import shutil
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import tempfile
import zipfile

try:
    from supabase import create_client
except ImportError:
    create_client = None
    logging.warning("supabase library not installed; backup functionality disabled.")

import config


class BackupManagerFixed:
    """مدير النسخ الاحتياطي المُصلح"""
    
    def __init__(self):
        """تهيئة مدير النسخ الاحتياطية"""
        self.logger = logging.getLogger(__name__)
        
        if create_client is None:
            self.logger.error("Supabase client not available")
            raise Exception("مكتبة Supabase غير مثبتة")
        
        try:
            self.supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            self.bucket_name = config.SUPABASE_BUCKET
        except Exception as e:
            self.logger.error(f"فشل في تهيئة Supabase: {e}")
            raise Exception(f"فشل في الاتصال بـ Supabase: {e}")
    
    def _get_safe_organization_folder_name(self, organization_name: str) -> str:
        """إنشاء اسم مجلد آمن من اسم المؤسسة"""
        if not organization_name:
            return "organization"
        import re
        safe_org_name = re.sub(r'[<>:"/\\|?*]', '', organization_name)
        safe_org_name = safe_org_name.strip().replace(' ', '_')
        return safe_org_name
    
    def create_backup(self, description: str = "") -> Tuple[bool, str]:
        """إنشاء نسخة احتياطية ورفعها"""
        try:
            if not config.DATABASE_PATH.exists():
                return False, "قاعدة البيانات غير موجودة"
            
            # إنشاء اسم الملف
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.zip"
            
            # إنشاء ملف مؤقت
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                temp_path = temp_file.name
            
            try:
                # إنشاء أرشيف ZIP
                with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    zip_file.write(config.DATABASE_PATH, "schools.db")
                    
                    backup_info = {
                        "created_at": datetime.now().isoformat(),
                        "description": description,
                        "database_size": os.path.getsize(config.DATABASE_PATH),
                        "version": config.APP_VERSION
                    }
                    
                    info_content = "\n".join([
                        f"تاريخ الإنشاء: {backup_info['created_at']}",
                        f"الوصف: {backup_info['description']}",
                        f"حجم قاعدة البيانات: {backup_info['database_size']} بايت",
                        f"إصدار التطبيق: {backup_info['version']}"
                    ])
                    
                    zip_file.writestr("backup_info.txt", info_content.encode('utf-8'))
                
                # الحصول على اسم المؤسسة
                from core.utils.settings_manager import settings_manager
                organization_name = settings_manager.get_organization_name()
                safe_org_name = self._get_safe_organization_folder_name(organization_name)
                
                # مسار الرفع المُبسط
                file_path = f"backups/{safe_org_name}/{backup_filename}"
                
                # قراءة الملف ورفعه
                with open(temp_path, 'rb') as f:
                    data = f.read()
                
                upload_result = self.supabase.storage.from_(self.bucket_name).upload(file_path, data)
                
                if hasattr(upload_result, 'error') and upload_result.error:
                    error_msg = f"فشل في رفع النسخة الاحتياطية: {upload_result.error}"
                    self.logger.error(error_msg)
                    return False, error_msg
                
                self.logger.info(f"تم إنشاء النسخة الاحتياطية: {file_path}")
                return True, f"تم إنشاء النسخة الاحتياطية بنجاح\nالملف: {backup_filename}"
                    
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            error_msg = f"خطأ في إنشاء النسخة الاحتياطية: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def list_backups(self) -> List[Dict]:
        """قائمة النسخ الاحتياطية - طريقة مُبسطة"""
        try:
            # الحصول على اسم المؤسسة
            from core.utils.settings_manager import settings_manager
            organization_name = settings_manager.get_organization_name()
            
            if not organization_name:
                self.logger.warning("لم يتم العثور على اسم المؤسسة")
                return []
            
            safe_org_name = self._get_safe_organization_folder_name(organization_name)
            backups = []
            
            self.logger.info(f"البحث عن النسخ في مجلد: {safe_org_name}")
            
            try:
                # البحث في مجلد المؤسسة مباشرة
                org_folder_path = f"backups/{safe_org_name}"
                files = self.supabase.storage.from_(self.bucket_name).list(org_folder_path)
                
                self.logger.info(f"عدد الملفات في مجلد المؤسسة: {len(files) if files else 0}")
                
                if files:
                    for file_item in files:
                        if file_item and isinstance(file_item, dict):
                            filename = file_item.get('name', '')
                            self.logger.info(f"فحص الملف: {filename}")
                            
                            # التحقق من أن هذا ملف نسخة احتياطية
                            if filename.endswith('.zip') and 'backup_' in filename:
                                backup_info = self._parse_backup_info_simple(
                                    f"{org_folder_path}/{filename}",
                                    file_item
                                )
                                if backup_info:
                                    backups.append(backup_info)
                                    self.logger.info(f"تم إضافة النسخة: {filename}")
                
            except Exception as folder_e:
                self.logger.error(f"خطأ في البحث في مجلد المؤسسة: {folder_e}")
                
                # محاولة البحث في جميع المجلدات
                try:
                    all_backups_folders = self.supabase.storage.from_(self.bucket_name).list("backups")
                    
                    for folder_item in all_backups_folders:
                        if folder_item and isinstance(folder_item, dict):
                            folder_name = folder_item.get('name', '')
                            
                            # البحث في كل مجلد
                            try:
                                folder_files = self.supabase.storage.from_(self.bucket_name).list(f"backups/{folder_name}")
                                
                                for file_item in folder_files:
                                    if file_item and isinstance(file_item, dict):
                                        filename = file_item.get('name', '')
                                        
                                        if filename.endswith('.zip') and 'backup_' in filename:
                                            backup_info = self._parse_backup_info_simple(
                                                f"backups/{folder_name}/{filename}",
                                                file_item
                                            )
                                            if backup_info:
                                                backups.append(backup_info)
                                                
                            except Exception as subfolder_e:
                                self.logger.warning(f"خطأ في البحث في مجلد {folder_name}: {subfolder_e}")
                                
                except Exception as fallback_e:
                    self.logger.error(f"خطأ في البحث العام: {fallback_e}")
            
            # ترتيب النسخ حسب التاريخ
            backups.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
            
            self.logger.info(f"تم العثور على {len(backups)} نسخة احتياطية")
            return backups
            
        except Exception as e:
            self.logger.error(f"خطأ في جلب قائمة النسخ الاحتياطية: {e}")
            return []
    
    def _parse_backup_info_simple(self, file_path: str, file_item: Dict) -> Optional[Dict]:
        """استخراج معلومات النسخة الاحتياطية - طريقة مبسطة"""
        try:
            filename = file_item.get('name', '')
            
            if filename.startswith('backup_') and filename.endswith('.zip'):
                timestamp_str = filename[7:-4]  # إزالة 'backup_' و '.zip'
                
                try:
                    backup_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                except ValueError:
                    backup_date = datetime.now()
                
                # حجم الملف من metadata
                size = 0
                if file_item.get('metadata') and isinstance(file_item['metadata'], dict):
                    size = file_item['metadata'].get('size', 0)
                
                return {
                    'filename': filename,
                    'path': file_path,
                    'created_at': backup_date,
                    'size': size,
                    'formatted_date': backup_date.strftime("%Y-%m-%d %H:%M:%S"),
                    'formatted_size': self._format_file_size(size)
                }
                
        except Exception as e:
            self.logger.error(f"خطأ في استخراج معلومات النسخة: {e}")
            
        return None
    
    def _format_file_size(self, size_bytes: int) -> str:
        """تنسيق حجم الملف"""
        if size_bytes < 1024:
            return f"{size_bytes} بايت"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} كيلوبايت"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} ميجابايت"
    
    def get_backup_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """الحصول على رابط تحميل النسخة الاحتياطية"""
        try:
            result = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                file_path, expires_in
            )
            
            if isinstance(result, dict) and 'signedURL' in result:
                return result['signedURL']
            
            return None
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء رابط التحميل: {e}")
            return None
    
    def delete_backup(self, file_path: str) -> Tuple[bool, str]:
        """حذف نسخة احتياطية"""
        try:
            result = self.supabase.storage.from_(self.bucket_name).remove([file_path])
            
            if hasattr(result, 'error') and result.error:
                return False, f"فشل في حذف النسخة: {result.error}"
            
            return True, "تم حذف النسخة الاحتياطية بنجاح"
            
        except Exception as e:
            error_msg = f"خطأ في حذف النسخة الاحتياطية: {e}"
            self.logger.error(error_msg)
            return False, error_msg


# اختبار سريع
def test_backup_manager():
    """اختبار مدير النسخ المُصلح"""
    print("اختبار مدير النسخ الاحتياطي المُصلح...")
    
    try:
        manager = BackupManagerFixed()
        
        # اختبار قائمة النسخ
        print("\n📋 اختبار قائمة النسخ الاحتياطية:")
        backups = manager.list_backups()
        print(f"عدد النسخ المُكتشفة: {len(backups)}")
        
        for i, backup in enumerate(backups[:3]):
            print(f"  {i+1}. {backup['filename']} - {backup['formatted_date']} ({backup['formatted_size']})")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False


if __name__ == "__main__":
    test_backup_manager()
