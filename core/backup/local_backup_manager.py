#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير النسخ الاحتياطي المحلي
يدير عمليات النسخ الاحتياطي المحلي للملفات
"""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional
import zipfile
import tempfile

import config


class LocalBackupManager:
    """مدير النسخ الاحتياطي المحلي"""

    def __init__(self):
        """تهيئة مدير النسخ الاحتياطي المحلي"""
        self.logger = logging.getLogger(__name__)

    def create_local_backup(self, backup_path: str, description: str = "") -> Tuple[bool, str]:
        """
        إنشاء نسخة احتياطية محلية

        Args:
            backup_path: مسار المجلد المراد حفظ النسخة الاحتياطية فيه
            description: وصف النسخة الاحتياطية

        Returns:
            tuple: (نجح العملية, رسالة النتيجة)
        """
        try:
            # التحقق من وجود قاعدة البيانات
            if not config.DATABASE_PATH.exists():
                return False, "قاعدة البيانات غير موجودة"

            # التحقق من صحة المسار
            if not os.path.exists(backup_path):
                return False, "مسار النسخ الاحتياطي غير موجود"

            # إنشاء اسم الملف بالتاريخ والوقت
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"local_backup_{timestamp}.zip"
            backup_file_path = os.path.join(backup_path, backup_filename)

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
                        "version": config.APP_VERSION,
                        "type": "local_backup"
                    }

                    info_content = "\n".join([
                        f"تاريخ الإنشاء: {backup_info['created_at']}",
                        f"الوصف: {backup_info['description']}",
                        f"حجم قاعدة البيانات: {backup_info['database_size']} بايت",
                        f"إصدار التطبيق: {backup_info['version']}",
                        f"نوع النسخة: {backup_info['type']}"
                    ])

                    zip_file.writestr("backup_info.txt", info_content.encode('utf-8'))

                # نقل الملف المؤقت إلى المسار المحدد
                shutil.move(temp_path, backup_file_path)

                self.logger.info(f"تم إنشاء النسخة الاحتياطية المحلية: {backup_file_path}")

                return True, f"تم إنشاء النسخة الاحتياطية المحلية بنجاح\nالملف: {backup_filename}"

            finally:
                # حذف الملف المؤقت في حالة وجوده
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            error_msg = f"خطأ في إنشاء النسخة الاحتياطية المحلية: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def list_local_backups(self, backup_path: str) -> list:
        """
        قائمة بالنسخ الاحتياطية المحلية المتاحة

        Args:
            backup_path: مسار مجلد النسخ الاحتياطية

        Returns:
            قائمة بالنسخ الاحتياطية مع معلوماتها
        """
        try:
            backups = []

            if not os.path.exists(backup_path):
                return backups

            # البحث عن ملفات ZIP التي تحتوي على كلمة backup
            for filename in os.listdir(backup_path):
                if filename.endswith('.zip') and 'backup' in filename.lower():
                    file_path = os.path.join(backup_path, filename)

                    try:
                        # استخراج معلومات النسخة الاحتياطية
                        with zipfile.ZipFile(file_path, 'r') as zip_file:
                            if 'backup_info.txt' in zip_file.namelist():
                                with zip_file.open('backup_info.txt') as info_file:
                                    info_content = info_file.read().decode('utf-8')

                                backup_info = self._parse_backup_info(info_content, filename, file_path)
                                if backup_info:
                                    backups.append(backup_info)

                    except Exception as e:
                        self.logger.warning(f"خطأ في قراءة ملف النسخة الاحتياطية {filename}: {e}")

            # ترتيب حسب التاريخ (الأحدث أولاً)
            backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)

            return backups

        except Exception as e:
            self.logger.error(f"خطأ في قائمة النسخ الاحتياطية المحلية: {e}")
            return []

    def _parse_backup_info(self, info_content: str, filename: str, file_path: str) -> Optional[dict]:
        """تحليل معلومات النسخة الاحتياطية من الملف"""
        try:
            lines = info_content.strip().split('\n')
            info_dict = {}

            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    if key == "تاريخ الإنشاء":
                        info_dict['created_at'] = value
                    elif key == "الوصف":
                        info_dict['description'] = value
                    elif key == "حجم قاعدة البيانات":
                        info_dict['database_size'] = value
                    elif key == "إصدار التطبيق":
                        info_dict['version'] = value
                    elif key == "نوع النسخة":
                        info_dict['type'] = value

            # إضافة معلومات إضافية
            info_dict['filename'] = filename
            info_dict['file_path'] = file_path
            info_dict['file_size'] = os.path.getsize(file_path)

            # تحويل التاريخ إلى كائن datetime للترتيب
            if 'created_at' in info_dict:
                try:
                    # إزالة الجزء الزمني إذا كان موجوداً
                    date_str = info_dict['created_at'].split('T')[0] if 'T' in info_dict['created_at'] else info_dict['created_at']
                    info_dict['date'] = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
                except:
                    info_dict['date'] = "غير محدد"

            return info_dict

        except Exception as e:
            self.logger.error(f"خطأ في تحليل معلومات النسخة الاحتياطية: {e}")
            return None

    def restore_local_backup(self, backup_file_path: str) -> Tuple[bool, str]:
        """
        استعادة نسخة احتياطية محلية

        Args:
            backup_file_path: مسار ملف النسخة الاحتياطية

        Returns:
            tuple: (نجح العملية, رسالة النتيجة)
        """
        try:
            if not os.path.exists(backup_file_path):
                return False, "ملف النسخة الاحتياطية غير موجود"

            # إنشاء نسخة احتياطية من قاعدة البيانات الحالية قبل الاستعادة
            current_db_backup = config.DATABASE_PATH.with_suffix('.backup')
            shutil.copy2(config.DATABASE_PATH, current_db_backup)

            try:
                # استخراج قاعدة البيانات من الأرشيف
                with zipfile.ZipFile(backup_file_path, 'r') as zip_file:
                    if 'schools.db' not in zip_file.namelist():
                        return False, "ملف قاعدة البيانات غير موجود في الأرشيف"

                    # استخراج قاعدة البيانات
                    with zip_file.open('schools.db') as db_file:
                        with open(config.DATABASE_PATH, 'wb') as output_file:
                            shutil.copyfileobj(db_file, output_file)

                self.logger.info(f"تم استعادة النسخة الاحتياطية المحلية: {backup_file_path}")

                return True, "تم استعادة النسخة الاحتياطية بنجاح"

            except Exception as e:
                # في حالة فشل الاستعادة، إعادة قاعدة البيانات الأصلية
                if current_db_backup.exists():
                    shutil.copy2(current_db_backup, config.DATABASE_PATH)
                raise e

            finally:
                # حذف النسخة الاحتياطية المؤقتة
                if current_db_backup.exists():
                    current_db_backup.unlink()

        except Exception as e:
            error_msg = f"خطأ في استعادة النسخة الاحتياطية المحلية: {e}"
            self.logger.error(error_msg)
            return False, error_msg


# إنشاء كائن عام للاستخدام
local_backup_manager = LocalBackupManager()
