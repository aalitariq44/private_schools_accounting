#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
وحدة مساعدة لإدارة إعدادات التطبيق
"""

import logging
from typing import Optional, Dict, Any
from core.database.connection import db_manager

# استيراد PyQt5 للإشارات
try:
    from PyQt5.QtCore import pyqtSignal, QObject
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    logging.warning("PyQt5 غير متوفر، لن تكون إشارات التحديث الفوري متاحة")


class SettingsManager:
    """مدير إعدادات التطبيق"""
    
    def __init__(self):
        """تهيئة مدير الإعدادات"""
        self._cache = {}
        
        # إعداد إشارة تغيير الإعدادات
        if QT_AVAILABLE:
            # إنشاء كلاس للإشارات
            class SettingsSignals(QObject):
                setting_changed = pyqtSignal(str, str)  # key, value
            
            self._signals = SettingsSignals()
            self.setting_changed = self._signals.setting_changed
        else:
            self.setting_changed = None
    
    def get_setting(self, key: str, default_value: Any = None) -> Any:
        """الحصول على إعداد من قاعدة البيانات"""
        try:
            # البحث في الكاش أولاً
            if key in self._cache:
                return self._cache[key]
            
            # البحث في قاعدة البيانات
            query = "SELECT setting_value FROM app_settings WHERE setting_key = ?"
            result = db_manager.execute_query(query, (key,))
            
            if result and len(result) > 0:
                value = result[0]['setting_value']
                self._cache[key] = value
                return value
            
            return default_value
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على الإعداد {key}: {e}")
            return default_value
    
    def set_setting(self, key: str, value: Any) -> bool:
        """تعيين إعداد في قاعدة البيانات"""
        try:
            query = """
                INSERT OR REPLACE INTO app_settings (setting_key, setting_value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """
            
            affected_rows = db_manager.execute_update(query, (key, str(value)))
            
            if affected_rows >= 0:
                # تحديث الكاش
                self._cache[key] = value
                logging.info(f"تم تحديث الإعداد {key}: {value}")
                
                # إرسال إشارة التحديث الفوري
                self._emit_setting_changed(key, value)
                
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"خطأ في تعيين الإعداد {key}: {e}")
            return False
    
    def _emit_setting_changed(self, key: str, value: Any):
        """إرسال إشارة تغيير الإعداد"""
        try:
            if self.setting_changed and QT_AVAILABLE:
                logging.info(f"إرسال إشارة تغيير الإعداد: {key} = {value}")
                self.setting_changed.emit(key, str(value))
                logging.debug(f"تم إرسال إشارة تغيير الإعداد: {key} = {value}")
        except Exception as e:
            logging.error(f"خطأ في إرسال إشارة تغيير الإعداد: {e}")
    
    def get_academic_year(self) -> str:
        """الحصول على العام الدراسي الحالي"""
        return self.get_setting('academic_year', '2024 - 2025')
    
    def set_academic_year(self, year: str) -> bool:
        """تعيين العام الدراسي الحالي"""
        return self.set_setting('academic_year', year)
    
    def get_organization_name(self) -> str:
        """الحصول على اسم المؤسسة"""
        return self.get_setting('organization_name', '')
    
    def set_organization_name(self, name: str) -> bool:
        """تعيين اسم المؤسسة (للاستخدام في الإعداد الأولي فقط)"""
        return self.set_setting('organization_name', name)
    
    def get_mobile_password(self) -> str:
        """الحصول على كلمة مرور التطبيق المحمول"""
        return self.get_setting('mobile_app_password', '')
    
    def set_mobile_password(self, password: str) -> bool:
        """تعيين كلمة مرور التطبيق المحمول"""
        return self.set_setting('mobile_app_password', password)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """الحصول على جميع الإعدادات"""
        try:
            query = "SELECT setting_key, setting_value FROM app_settings"
            result = db_manager.execute_query(query)
            
            settings = {}
            for row in result:
                settings[row['setting_key']] = row['setting_value']
            
            # تحديث الكاش
            self._cache.update(settings)
            
            return settings
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على جميع الإعدادات: {e}")
            return {}
    
    def clear_cache(self):
        """مسح كاش الإعدادات"""
        self._cache.clear()
    
    def delete_setting(self, key: str) -> bool:
        """حذف إعداد من قاعدة البيانات"""
        try:
            query = "DELETE FROM app_settings WHERE setting_key = ?"
            affected_rows = db_manager.execute_update(query, (key,))
            
            if affected_rows > 0:
                # إزالة من الكاش
                self._cache.pop(key, None)
                logging.info(f"تم حذف الإعداد {key}")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"خطأ في حذف الإعداد {key}: {e}")
            return False
    
    def initialize_default_settings(self):
        """تهيئة الإعدادات الافتراضية"""
        try:
            defaults = {
                'academic_year': '2024 - 2025',
                'app_language': 'ar',
                'auto_backup': 'true',
                'backup_interval': '7',
                'print_school_logo': 'true',
                'currency_symbol': 'ر.س',
                'date_format': 'dd/MM/yyyy',
                'organization_name': '',  # سيتم تعيينه في الإعداد الأولي
                'mobile_app_password': ''  # كلمة مرور التطبيق المحمول
            }
            
            for key, value in defaults.items():
                # تحقق من وجود الإعداد
                current_value = self.get_setting(key)
                if current_value is None:
                    self.set_setting(key, value)
                    logging.info(f"تم إنشاء الإعداد الافتراضي {key}: {value}")
            
            logging.info("تم تهيئة الإعدادات الافتراضية")
            
        except Exception as e:
            logging.error(f"خطأ في تهيئة الإعدادات الافتراضية: {e}")
    
    def get_academic_year(self) -> str:
        """الحصول على العام الدراسي الحالي"""
        return self.get_setting('academic_year', '2024 - 2025')
    
    def set_academic_year(self, year: str) -> bool:
        """تعيين العام الدراسي الحالي"""
        return self.set_setting('academic_year', year)
    
    def get_organization_name(self) -> str:
        """الحصول على اسم المؤسسة"""
        return self.get_setting('organization_name', '')
    
    def set_organization_name(self, name: str) -> bool:
        """تعيين اسم المؤسسة (للاستخدام في الإعداد الأولي فقط)"""
        return self.set_setting('organization_name', name)
    
    def get_mobile_password(self) -> str:
        """الحصول على كلمة مرور التطبيق المحمول"""
        return self.get_setting('mobile_app_password', '')
    
    def set_mobile_password(self, password: str) -> bool:
        """تعيين كلمة مرور التطبيق المحمول"""
        return self.set_setting('mobile_app_password', password)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """الحصول على جميع الإعدادات"""
        try:
            query = "SELECT setting_key, setting_value FROM app_settings"
            result = db_manager.execute_query(query)
            
            settings = {}
            for row in result:
                settings[row['setting_key']] = row['setting_value']
            
            # تحديث الكاش
            self._cache.update(settings)
            
            return settings
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على جميع الإعدادات: {e}")
            return {}
    
    def clear_cache(self):
        """مسح كاش الإعدادات"""
        self._cache.clear()
    
    def delete_setting(self, key: str) -> bool:
        """حذف إعداد من قاعدة البيانات"""
        try:
            query = "DELETE FROM app_settings WHERE setting_key = ?"
            affected_rows = db_manager.execute_update(query, (key,))
            
            if affected_rows > 0:
                # إزالة من الكاش
                self._cache.pop(key, None)
                logging.info(f"تم حذف الإعداد {key}")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"خطأ في حذف الإعداد {key}: {e}")
            return False
    
    def initialize_default_settings(self):
        """تهيئة الإعدادات الافتراضية"""
        try:
            defaults = {
                'academic_year': '2024 - 2025',
                'app_language': 'ar',
                'auto_backup': 'true',
                'backup_interval': '7',
                'print_school_logo': 'true',
                'currency_symbol': 'ر.س',
                'date_format': 'dd/MM/yyyy',
                'organization_name': '',  # سيتم تعيينه في الإعداد الأولي
                'mobile_app_password': ''  # كلمة مرور التطبيق المحمول
            }
            
            for key, value in defaults.items():
                # تحقق من وجود الإعداد
                current_value = self.get_setting(key)
                if current_value is None:
                    self.set_setting(key, value)
                    logging.info(f"تم إنشاء الإعداد الافتراضي {key}: {value}")
            
            logging.info("تم تهيئة الإعدادات الافتراضية")
            
        except Exception as e:
            logging.error(f"خطأ في تهيئة الإعدادات الافتراضية: {e}")


# إنشاء مثيل مشترك من مدير الإعدادات
settings_manager = SettingsManager()


def get_academic_year() -> str:
    """دالة مساعدة للحصول على العام الدراسي الحالي"""
    return settings_manager.get_academic_year()


def get_organization_name() -> str:
    """دالة مساعدة للحصول على اسم المؤسسة"""
    return settings_manager.get_organization_name()


def get_app_setting(key: str, default_value: Any = None) -> Any:
    """دالة مساعدة للحصول على إعداد التطبيق"""
    return settings_manager.get_setting(key, default_value)


def set_app_setting(key: str, value: Any) -> bool:
    """دالة مساعدة لتعيين إعداد التطبيق"""
    return settings_manager.set_setting(key, value)


def get_mobile_password() -> str:
    """دالة مساعدة للحصول على كلمة مرور التطبيق المحمول"""
    return settings_manager.get_mobile_password()


def set_mobile_password(password: str) -> bool:
    """دالة مساعدة لتعيين كلمة مرور التطبيق المحمول"""
    return settings_manager.set_mobile_password(password)
