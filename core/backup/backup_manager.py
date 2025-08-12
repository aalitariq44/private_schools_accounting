#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير النسخ الاحتياطية - Supabase Storage
يدير عمليات رفع وعرض النسخ الاحتياطية من قاعدة البيانات على Supabase
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
    from supabase import create_client  # type: ignore
except ImportError:
    create_client = None
    logging.warning("supabase library not installed; backup functionality disabled.")
"""StorageException for handling storage errors; using generic Exception as fallback."""
StorageException = Exception

import config


class BackupManager:
    """مدير النسخ الاحتياطية"""
    
    def __init__(self):
        """تهيئة مدير النسخ الاحتياطية"""
        self.logger = logging.getLogger(__name__)
        # تحقق من توفر عميل Supabase
        if create_client is None:
            self.logger.error("Supabase client not available; backup functionality is disabled.")
            raise Exception("مكتبة Supabase غير مثبتة. يرجى تثبيتها باستخدام: pip install supabase")
        
        # تهيئة عميل Supabase
        try:
            self.supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            self.bucket_name = config.SUPABASE_BUCKET
            self.setup_storage()
        except Exception as e:
            self.logger.error(f"فشل في تهيئة Supabase: {e}")
            raise Exception(f"فشل في الاتصال بـ Supabase: {e}")
    
    def setup_storage(self):
        """إعداد التخزين على Supabase"""
        try:
            # التحقق من وجود البكت بدون محاولة إنشاؤه
            self.logger.info(f"محاولة الاتصال بـ Supabase Storage...")
            
            # نجرب فقط الوصول للبكت الموجود
            # إذا كان موجود سيعمل، إذا لم يكن موجود فسنتعامل مع الخطأ في create_backup
            self.logger.info(f"سنستخدم بكت التخزين: {self.bucket_name}")
                
        except Exception as e:
            self.logger.warning(f"تحذير في إعداد التخزين: {type(e).__name__}: {e}")
            # لا نرمي خطأ هنا، فقط تحذير
    
    def _get_safe_organization_folder_name(self, organization_name: str) -> str:
        """إنشاء اسم مجلد آمن من اسم المؤسسة"""
        if not organization_name:
            return "organization"
        
        import hashlib
        import re
        
        # تحويل الأحرف العربية إلى أحرف لاتينية آمنة
        # إزالة الأحرف الخاصة أولاً
        cleaned_name = re.sub(r'[<>:"/\\|?*\s]', '_', organization_name)
        
        # إنشاء hash قصير للاسم العربي لضمان الفرادة
        name_hash = hashlib.md5(organization_name.encode('utf-8')).hexdigest()[:8]
        
        # دمج الاسم المنظف مع الـ hash
        safe_org_name = f"org_{name_hash}"
        
        # التأكد من أن الاسم لا يحتوي على أحرف غير مدعومة
        safe_org_name = re.sub(r'[^\w\-_]', '_', safe_org_name)
        
        return safe_org_name
    
    def create_backup(self, description: str = "") -> Tuple[bool, str]:
        """
        إنشاء نسخة احتياطية جديدة ورفعها على Supabase
        
        Args:
            description: وصف النسخة الاحتياطية
            
        Returns:
            tuple: (نجح العملية, رسالة النتيجة)
        """
        try:
            # التحقق من وجود قاعدة البيانات
            if not config.DATABASE_PATH.exists():
                return False, "قاعدة البيانات غير موجودة"
            
            # إنشاء اسم الملف بالتاريخ والوقت
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.zip"
            
            # إنشاء ملف مؤقت للنسخة الاحتياطية
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                temp_path = temp_file.name
            
            try:
                # إنشاء أرشيف ZIP يحتوي على قاعدة البيانات
                with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # إضافة قاعدة البيانات
                    zip_file.write(config.DATABASE_PATH, "schools.db")
                    
                    # إضافة ملف معلومات النسخة الاحتياطية
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
                
                # رفع على Supabase - طريقة مبسطة مثل المثال الناجح
                self.logger.info("محاولة رفع النسخة الاحتياطية على Supabase...")
                
                # الحصول على اسم المؤسسة من الإعدادات
                from core.utils.settings_manager import settings_manager
                organization_name = settings_manager.get_organization_name()
                
                # الحصول على اسم مجلد آمن
                safe_org_name = self._get_safe_organization_folder_name(organization_name)
                
                # مسار المجلد الجديد: اسم المؤسسة مباشرة
                folder_path = f"backups/{safe_org_name}"
                file_path = f"{folder_path}/{backup_filename}"
                
                # قراءة الملف كما في المثال الناجح
                with open(temp_path, 'rb') as f:
                    data = f.read()
                
                # رفع الملف بنفس الطريقة البسيطة
                upload_result = self.supabase.storage.from_(self.bucket_name).upload(file_path, data)
                
                # التحقق من النتيجة مثل المثال الناجح
                if hasattr(upload_result, 'error') and upload_result.error:
                    error_msg = f"فشل في رفع النسخة الاحتياطية: {upload_result.error}"
                    self.logger.error(error_msg)
                    return False, error_msg
                
                self.logger.info(f"تم إنشاء النسخة الاحتياطية على Supabase: {file_path}, النتيجة: {upload_result}")
                
                # حفظ اسم آخر نسخة تم رفعها لاستخدامها في list_backups
                self._last_uploaded_backup = backup_filename
                
                return True, f"تم إنشاء النسخة الاحتياطية بنجاح على Supabase\nالملف: {backup_filename}"
                    
            finally:
                # حذف الملف المؤقت
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except StorageException as e:
            error_msg = f"خطأ في التخزين: {e}"
            self.logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"خطأ في إنشاء النسخة الاحتياطية: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def list_backups(self) -> List[Dict]:
        """
        قائمة بجميع النسخ الاحتياطية المتاحة على Supabase
        
        Returns:
            قائمة بالنسخ الاحتياطية مع معلوماتها
        """
        try:
            backups = []
            
            # الحصول على اسم المؤسسة من الإعدادات
            from core.utils.settings_manager import settings_manager
            organization_name = settings_manager.get_organization_name()
            
            if not organization_name:
                self.logger.warning("لم يتم العثور على اسم المؤسسة في الإعدادات")
                return []
            
            # الحصول على اسم مجلد آمن
            safe_org_name = self._get_safe_organization_folder_name(organization_name)
            
            # جلب قائمة الملفات من مجلد المؤسسة
            organization_folder = f"backups/{safe_org_name}"
            
            try:
                self.logger.info(f"البحث عن النسخ في المجلد: {organization_folder}")
                
                # البحث في جميع الملفات مباشرة بدلاً من محاولة المجلد أولاً
                try:
                    # البحث في جميع ملفات التخزين
                    all_files = self.supabase.storage.from_(self.bucket_name).list("")
                    
                    prefix = f"backups/{safe_org_name}/"
                    self.logger.info(f"البحث عن الملفات التي تبدأ بـ: {prefix}")
                    self.logger.info(f"عدد الملفات الكلي: {len(all_files)}")
                    
                    for file_item in all_files:
                        file_path = file_item.get('name', '')
                        self.logger.info(f"فحص الملف: {file_path}")
                        if file_path.startswith(prefix) and file_path.endswith('.zip'):
                            self.logger.info(f"ملف مطابق: {file_path}")
                            backup_info = self._parse_backup_info(
                                file_path,
                                file_item
                            )
                            if backup_info:
                                backups.append(backup_info)
                                    
                except Exception as search_error:
                    self.logger.error(f"فشل في البحث العام: {search_error}")
                            
            except Exception as e:
                self.logger.warning(f"لم يتم العثور على مجلد النسخ الاحتياطية للمؤسسة: {e}")
                # محاولة البحث في المجلدات القديمة للتوافق مع النظام السابق
                try:
                    result = self.supabase.storage.from_(self.bucket_name).list("backups", {
                        "limit": 100,
                        "sortBy": {"column": "created_at", "order": "desc"}
                    })
                    
                    for item in result:
                        if self._is_backup_folder(item):
                            # جلب الملفات من هذا المجلد
                            folder_files = self.supabase.storage.from_(self.bucket_name).list(
                                f"backups/{item['name']}", {"limit": 100}
                            )
                            
                            for folder_item in folder_files:
                                if self._is_backup_folder(folder_item):
                                    # مجلد شهر، جلب الملفات منه
                                    month_files = self.supabase.storage.from_(self.bucket_name).list(
                                        f"backups/{item['name']}/{folder_item['name']}", {"limit": 100}
                                    )
                                    
                                    for file_item in month_files:
                                        if file_item['name'].endswith('.zip'):
                                            backup_info = self._parse_backup_info(
                                                f"backups/{item['name']}/{folder_item['name']}/{file_item['name']}",
                                                file_item
                                            )
                                            if backup_info:
                                                backups.append(backup_info)
                                elif folder_item['name'].endswith('.zip'):
                                    # ملف مباشر في المجلد
                                    backup_info = self._parse_backup_info(
                                        f"backups/{item['name']}/{folder_item['name']}",
                                        folder_item
                                    )
                                    if backup_info:
                                        backups.append(backup_info)
                except Exception as fallback_e:
                    self.logger.error(f"خطأ في البحث عن النسخ الاحتياطية القديمة: {fallback_e}")
            
            # ترتيب النسخ حسب التاريخ (الأحدث أولاً)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            return backups
            
        except Exception as e:
            self.logger.error(f"خطأ في جلب قائمة النسخ الاحتياطية: {e}")
            return []
    
    def _is_backup_folder(self, item: Dict) -> bool:
        """التحقق من أن العنصر مجلد وليس ملف"""
        return item.get('id') is None and 'name' in item
    
    def _parse_backup_info(self, file_path: str, file_item: Dict) -> Optional[Dict]:
        """استخراج معلومات النسخة الاحتياطية"""
        try:
            filename = file_item['name']
            
            # استخراج التاريخ من اسم الملف
            if filename.startswith('backup_') and filename.endswith('.zip'):
                timestamp_str = filename[7:-4]  # إزالة 'backup_' و '.zip'
                
                try:
                    # تحويل timestamp إلى datetime
                    backup_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                except ValueError:
                    backup_date = datetime.now()
                
                return {
                    'filename': filename,
                    'path': file_path,
                    'created_at': backup_date,
                    'size': file_item.get('metadata', {}).get('size', 0),
                    'formatted_date': backup_date.strftime("%Y-%m-%d %H:%M:%S"),
                    'formatted_size': self._format_file_size(
                        file_item.get('metadata', {}).get('size', 0)
                    )
                }
                
        except Exception as e:
            self.logger.error(f"خطأ في استخراج معلومات النسخة الاحتياطية: {e}")
            
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
        """
        الحصول على رابط تحميل النسخة الاحتياطية
        
        Args:
            file_path: مسار الملف
            expires_in: مدة صلاحية الرابط بالثواني
            
        Returns:
            رابط التحميل أو None في حالة الخطأ
        """
        if self.supabase is None:
            return None
        try:
            result = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                file_path, expires_in
            )
            return result.get('signedURL')
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء رابط التحميل: {e}")
            return None
    
    def delete_backup(self, file_path: str) -> Tuple[bool, str]:
        """
        حذف نسخة احتياطية من Supabase
        
        Args:
            file_path: مسار الملف
            
        Returns:
            tuple: (نجح العملية, رسالة النتيجة)
        """
        try:
            result = self.supabase.storage.from_(self.bucket_name).remove([file_path])
            
            if result:
                self.logger.info(f"تم حذف النسخة الاحتياطية: {file_path}")
                return True, "تم حذف النسخة الاحتياطية بنجاح"
            else:
                return False, "فشل في حذف النسخة الاحتياطية"
                
        except Exception as e:
            error_msg = f"خطأ في حذف النسخة الاحتياطية: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def cleanup_old_backups(self, keep_days: int = 30) -> Tuple[bool, str]:
        """
        تنظيف النسخ الاحتياطية القديمة على Supabase
        
        Args:
            keep_days: عدد الأيام للاحتفاظ بالنسخ
            
        Returns:
            tuple: (نجح العملية, رسالة النتيجة)
        """
        try:
            backups = self.list_backups()
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - keep_days)
            
            deleted_count = 0
            for backup in backups:
                if backup['created_at'] < cutoff_date:
                    success, _ = self.delete_backup(backup['path'])
                    if success:
                        deleted_count += 1
            
            message = f"تم حذف {deleted_count} نسخة احتياطية قديمة"
            self.logger.info(message)
            return True, message
            
        except Exception as e:
            error_msg = f"خطأ في تنظيف النسخ الاحتياطية: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_backup_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        الحصول على رابط تحميل النسخة الاحتياطية من Supabase
        
        Args:
            file_path: مسار الملف
            expires_in: مدة صلاحية الرابط بالثواني
            
        Returns:
            رابط التحميل أو None في حالة الخطأ
        """
        try:
            result = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                file_path, expires_in
            )
            return result.get('signedURL')
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء رابط التحميل: {e}")
            return None


# إنشاء مثيل مشترك من مدير النسخ الاحتياطية - تجنب None
backup_manager = None

def get_backup_manager():
    """الحصول على مثيل من مدير النسخ الاحتياطية مع إعادة المحاولة"""
    global backup_manager
    if backup_manager is None:
        try:
            backup_manager = BackupManager()
        except Exception as e:
            import logging
            logging.error(f"فشل في تهيئة مدير النسخ الاحتياطية: {e}")
            # إرجاع كائن وهمي بدلاً من None لتجنب NoneType errors
            class DummyBackupManager:
                def create_backup(self, description=""):
                    return False, f"فشل في تهيئة النظام: {e}"
                def list_backups(self):
                    return []
            backup_manager = DummyBackupManager()
    return backup_manager

# تهيئة فورية
backup_manager = get_backup_manager()
