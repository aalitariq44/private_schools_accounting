#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير إعدادات واجهة المستخدم
يحفظ ويقرأ إعدادات كل صفحة من ملف JSON
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# استيراد config
try:
    import config
    SETTINGS_FILE = config.DATA_DIR / "ui_settings.json"
except ImportError:
    # في حالة عدم وجود config، استخدم مسار نسبي
    SETTINGS_FILE = Path(__file__).parent.parent / "data" / "ui_settings.json"

class UISettingsManager:
    """مدير إعدادات واجهة المستخدم"""

    def __init__(self):
        self.settings_file = SETTINGS_FILE
        self.settings = {}
        self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """
        تحميل الإعدادات من ملف JSON

        Returns:
            dict: الإعدادات المحملة
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                logging.info(f"تم تحميل إعدادات UI من {self.settings_file}")
            else:
                # إنشاء إعدادات افتراضية إذا لم يكن الملف موجوداً
                self.settings = self.get_default_settings()
                self.save_settings()
                logging.info(f"تم إنشاء إعدادات UI افتراضية في {self.settings_file}")
        except Exception as e:
            logging.error(f"خطأ في تحميل إعدادات UI: {e}")
            # استخدام الإعدادات الافتراضية في حالة الخطأ
            self.settings = self.get_default_settings()

        return self.settings

    def save_settings(self) -> bool:
        """
        حفظ الإعدادات في ملف JSON

        Returns:
            bool: نجح الحفظ أم لا
        """
        try:
            # التأكد من وجود مجلد البيانات
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)

            logging.info(f"تم حفظ إعدادات UI في {self.settings_file}")
            return True

        except Exception as e:
            logging.error(f"خطأ في حفظ إعدادات UI: {e}")
            return False

    def get_page_settings(self, page_name: str) -> Dict[str, Any]:
        """
        الحصول على إعدادات صفحة معينة

        Args:
            page_name (str): اسم الصفحة

        Returns:
            dict: إعدادات الصفحة
        """
        page_key = f"{page_name}_page"
        if page_key in self.settings:
            return self.settings[page_key]
        else:
            # إرجاع إعدادات افتراضية للصفحة
            default_page_settings = self.get_default_page_settings(page_name)
            self.settings[page_key] = default_page_settings
            self.save_settings()
            return default_page_settings

    def update_page_settings(self, page_name: str, settings: Dict[str, Any]) -> bool:
        """
        تحديث إعدادات صفحة معينة

        Args:
            page_name (str): اسم الصفحة
            settings (dict): الإعدادات الجديدة

        Returns:
            bool: نجح التحديث أم لا
        """
        try:
            page_key = f"{page_name}_page"
            if page_key not in self.settings:
                self.settings[page_key] = {}

            # تحديث الإعدادات
            self.settings[page_key].update(settings)

            # حفظ التغييرات
            return self.save_settings()

        except Exception as e:
            logging.error(f"خطأ في تحديث إعدادات صفحة {page_name}: {e}")
            return False

    def get_font_size(self, page_name: str) -> str:
        """
        الحصول على حجم الخط لصفحة معينة

        Args:
            page_name (str): اسم الصفحة

        Returns:
            str: حجم الخط
        """
        page_settings = self.get_page_settings(page_name)
        return page_settings.get('font_size', 'متوسط')

    def set_font_size(self, page_name: str, font_size: str) -> bool:
        """
        تعيين حجم الخط لصفحة معينة

        Args:
            page_name (str): اسم الصفحة
            font_size (str): حجم الخط الجديد

        Returns:
            bool: نجح التعيين أم لا
        """
        return self.update_page_settings(page_name, {'font_size': font_size})

    def get_statistics_visible(self, page_name: str) -> bool:
        """
        الحصول على حالة رؤية نافذة الإحصائيات

        Args:
            page_name (str): اسم الصفحة

        Returns:
            bool: مرئية أم لا
        """
        page_settings = self.get_page_settings(page_name)
        return page_settings.get('statistics_window_visible', True)

    def set_statistics_visible(self, page_name: str, visible: bool) -> bool:
        """
        تعيين حالة رؤية نافذة الإحصائيات

        Args:
            page_name (str): اسم الصفحة
            visible (bool): مرئية أم لا

        Returns:
            bool: نجح التعيين أم لا
        """
        return self.update_page_settings(page_name, {'statistics_window_visible': visible})

    def get_table_columns_visible(self, page_name: str) -> Dict[str, bool]:
        """
        الحصول على حالة رؤية أعمدة الجدول

        Args:
            page_name (str): اسم الصفحة

        Returns:
            dict: حالة رؤية كل عمود
        """
        page_settings = self.get_page_settings(page_name)
        return page_settings.get('table_columns_visible', {})

    def set_table_column_visible(self, page_name: str, column_name: str, visible: bool) -> bool:
        """
        تعيين حالة رؤية عمود معين في الجدول

        Args:
            page_name (str): اسم الصفحة
            column_name (str): اسم العمود
            visible (bool): مرئي أم لا

        Returns:
            bool: نجح التعيين أم لا
        """
        columns_visible = self.get_table_columns_visible(page_name)
        columns_visible[column_name] = visible
        return self.update_page_settings(page_name, {'table_columns_visible': columns_visible})

    def get_default_settings(self) -> Dict[str, Any]:
        """
        الحصول على الإعدادات الافتراضية

        Returns:
            dict: الإعدادات الافتراضية
        """
        return {
            "students_page": {
                "font_size": "متوسط",
                "statistics_window_visible": True,
                "table_columns_visible": {
                    "name": True,
                    "class": True,
                    "fees": True,
                    "payments": True
                },
                "search_filters_visible": True,
                "export_options_visible": True
            },
            "schools_page": {
                "font_size": "متوسط",
                "statistics_window_visible": True,
                "table_columns_visible": {
                    "name": True,
                    "location": True,
                    "students_count": True,
                    "fees": True
                },
                "search_filters_visible": True,
                "export_options_visible": True
            },
            "teachers_page": {
                "font_size": "متوسط",
                "statistics_window_visible": True,
                "table_columns_visible": {
                    "name": True,
                    "subject": True,
                    "salary": True,
                    "phone": True
                },
                "search_filters_visible": True,
                "export_options_visible": True
            },
            "employees_page": {
                "font_size": "متوسط",
                "statistics_window_visible": True,
                "table_columns_visible": {
                    "name": True,
                    "position": True,
                    "salary": True,
                    "phone": True
                },
                "search_filters_visible": True,
                "export_options_visible": True
            },
            "installments_page": {
                "font_size": "متوسط",
                "statistics_window_visible": True,
                "table_columns_visible": {
                    "student_name": True,
                    "amount": True,
                    "due_date": True,
                    "status": True
                },
                "search_filters_visible": True,
                "export_options_visible": True
            },
            "additional_fees_page": {
                "font_size": "متوسط",
                "statistics_window_visible": True,
                "table_columns_visible": {
                    "student_name": True,
                    "fee_type": True,
                    "amount": True,
                    "date": True
                },
                "search_filters_visible": True,
                "export_options_visible": True
            },
            "student_ids_page": {
                "font_size": "متوسط",
                "statistics_window_visible": False,
                "preview_visible": True,
                "print_options_visible": True
            },
            "external_income_page": {
                "font_size": "متوسط",
                "statistics_window_visible": True,
                "table_columns_visible": {
                    "source": True,
                    "amount": True,
                    "date": True,
                    "description": True
                },
                "search_filters_visible": True,
                "export_options_visible": True
            },
            "expenses_page": {
                "font_size": "متوسط",
                "statistics_window_visible": True,
                "table_columns_visible": {
                    "category": True,
                    "amount": True,
                    "date": True,
                    "description": True
                },
                "search_filters_visible": True,
                "export_options_visible": True
            },
            "salaries_page": {
                "font_size": "متوسط",
                "statistics_window_visible": True,
                "table_columns_visible": {
                    "employee_name": True,
                    "amount": True,
                    "month": True,
                    "status": True
                },
                "search_filters_visible": True,
                "export_options_visible": True
            },
            "backup_page": {
                "font_size": "متوسط",
                "auto_backup_enabled": True,
                "backup_history_visible": True
            },
            "settings_page": {
                "font_size": "متوسط",
                "advanced_settings_visible": False
            },
            "dashboard_page": {
                "font_size": "متوسط",
                "charts_visible": True,
                "quick_stats_visible": True
            }
        }

    def get_default_page_settings(self, page_name: str) -> Dict[str, Any]:
        """
        الحصول على الإعدادات الافتراضية لصفحة معينة

        Args:
            page_name (str): اسم الصفحة

        Returns:
            dict: الإعدادات الافتراضية للصفحة
        """
        defaults = self.get_default_settings()
        page_key = f"{page_name}_page"
        return defaults.get(page_key, {
            "font_size": "متوسط",
            "statistics_window_visible": True
        })

    def reset_page_settings(self, page_name: str) -> bool:
        """
        إعادة تعيين إعدادات صفحة معينة للقيم الافتراضية

        Args:
            page_name (str): اسم الصفحة

        Returns:
            bool: نجح الإعادة أم لا
        """
        try:
            page_key = f"{page_name}_page"
            default_settings = self.get_default_page_settings(page_name)
            self.settings[page_key] = default_settings
            return self.save_settings()
        except Exception as e:
            logging.error(f"خطأ في إعادة تعيين إعدادات صفحة {page_name}: {e}")
            return False

    def save_setting(self, page_name: str, setting_key: str, value: Any) -> bool:
        """
        حفظ إعداد معين لصفحة معينة

        Args:
            page_name (str): اسم الصفحة
            setting_key (str): مفتاح الإعداد
            value (Any): قيمة الإعداد

        Returns:
            bool: نجح الحفظ أم لا
        """
        try:
            page_key = f"{page_name}_page"
            if page_key not in self.settings:
                self.settings[page_key] = {}

            self.settings[page_key][setting_key] = value
            return self.save_settings()

        except Exception as e:
            logging.error(f"خطأ في حفظ إعداد {setting_key} لصفحة {page_name}: {e}")
            return False

    def get_setting(self, page_name: str, setting_key: str, default_value: Any = None) -> Any:
        """
        الحصول على إعداد معين لصفحة معينة

        Args:
            page_name (str): اسم الصفحة
            setting_key (str): مفتاح الإعداد
            default_value (Any): القيمة الافتراضية إذا لم يكن الإعداد موجوداً

        Returns:
            Any: قيمة الإعداد
        """
        try:
            page_settings = self.get_page_settings(page_name)
            return page_settings.get(setting_key, default_value)
        except Exception as e:
            logging.error(f"خطأ في الحصول على إعداد {setting_key} لصفحة {page_name}: {e}")
            return default_value

# إنشاء instance واحد من المدير
ui_settings_manager = UISettingsManager()

# دوال مساعدة للتوافق
def get_page_font_size(page_name: str) -> str:
    """
    دالة مساعدة للحصول على حجم الخط لصفحة معينة

    Args:
        page_name (str): اسم الصفحة

    Returns:
        str: حجم الخط
    """
    return ui_settings_manager.get_font_size(page_name)

def set_page_font_size(page_name: str, font_size: str) -> bool:
    """
    دالة مساعدة لتعيين حجم الخط لصفحة معينة

    Args:
        page_name (str): اسم الصفحة
        font_size (str): حجم الخط

    Returns:
        bool: نجح التعيين أم لا
    """
    return ui_settings_manager.set_font_size(page_name, font_size)

def get_page_statistics_visible(page_name: str) -> bool:
    """
    دالة مساعدة للحصول على حالة رؤية الإحصائيات

    Args:
        page_name (str): اسم الصفحة

    Returns:
        bool: مرئية أم لا
    """
    return ui_settings_manager.get_statistics_visible(page_name)

def save_page_setting(page_name: str, setting_key: str, value: Any) -> bool:
    """
    دالة مساعدة لحفظ إعداد صفحة معينة

    Args:
        page_name (str): اسم الصفحة
        setting_key (str): مفتاح الإعداد
        value (Any): قيمة الإعداد

    Returns:
        bool: نجح الحفظ أم لا
    """
    return ui_settings_manager.save_setting(page_name, setting_key, value)

def get_page_setting(page_name: str, setting_key: str, default_value: Any = None) -> Any:
    """
    دالة مساعدة للحصول على إعداد صفحة معينة

    Args:
        page_name (str): اسم الصفحة
        setting_key (str): مفتاح الإعداد
        default_value (Any): القيمة الافتراضية

    Returns:
        Any: قيمة الإعداد
    """
    return ui_settings_manager.get_setting(page_name, setting_key, default_value)
