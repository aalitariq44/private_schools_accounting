#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
وحدة إدارة أحجام الخطوط - قابلة لإعادة الاستخدام
"""

class FontSizeManager:
    """مدير أحجام الخطوط للتطبيق"""

    # تعريف أحجام الخطوط المتاحة
    FONT_SIZES = {
        "صغير جدا": {
            'base': 10,
            'filter_label': 10,
            'filter_combo': 9,
            'search_input': 9,
            'buttons': 9,
            'table': 9,
            'table_header': 9,
            'summary_title': 10,
            'summary_label': 8,
            'summary_value': 11,
            'stat_label': 8
        },
        "صغير": {
            'base': 13,
            'filter_label': 13,
            'filter_combo': 12,
            'search_input': 12,
            'buttons': 12,
            'table': 12,
            'table_header': 12,
            'summary_title': 13,
            'summary_label': 11,
            'summary_value': 14,
            'stat_label': 11
        },
        "متوسط": {
            'base': 15,
            'filter_label': 15,
            'filter_combo': 14,
            'search_input': 14,
            'buttons': 14,
            'table': 14,
            'table_header': 14,
            'summary_title': 15,
            'summary_label': 13,
            'summary_value': 16,
            'stat_label': 13
        },
        "كبير": {
            'base': 18,
            'filter_label': 18,
            'filter_combo': 16,
            'search_input': 16,
            'buttons': 16,
            'table': 16,
            'table_header': 16,
            'summary_title': 18,
            'summary_label': 15,
            'summary_value': 20,
            'stat_label': 15
        },
        "كبير جدا": {
            'base': 22,
            'filter_label': 22,
            'filter_combo': 20,
            'search_input': 20,
            'buttons': 20,
            'table': 20,
            'table_header': 20,
            'summary_title': 22,
            'summary_label': 18,
            'summary_value': 24,
            'stat_label': 18
        }
    }

    # قائمة أحجام الخطوط المتاحة
    AVAILABLE_SIZES = ["صغير جدا", "صغير", "متوسط", "كبير", "كبير جدا"]

    # الحجم الافتراضي
    DEFAULT_SIZE = "صغير"

    @staticmethod
    def get_font_sizes(size_name):
        """
        الحصول على أحجام الخطوط حسب الخيار المختار

        Args:
            size_name (str): اسم حجم الخط المطلوب

        Returns:
            dict: قاموس يحتوي على أحجام الخطوط لكل عنصر
        """
        if size_name in FontSizeManager.FONT_SIZES:
            return FontSizeManager.FONT_SIZES[size_name]
        else:
            # إرجاع الحجم الافتراضي إذا لم يكن الاسم صحيحاً
            return FontSizeManager.FONT_SIZES[FontSizeManager.DEFAULT_SIZE]

    @staticmethod
    def get_available_sizes():
        """
        الحصول على قائمة أحجام الخطوط المتاحة

        Returns:
            list: قائمة بأسماء أحجام الخطوط المتاحة
        """
        return FontSizeManager.AVAILABLE_SIZES.copy()

    @staticmethod
    def get_default_size():
        """
        الحصول على الحجم الافتراضي

        Returns:
            str: اسم الحجم الافتراضي
        """
        return FontSizeManager.DEFAULT_SIZE

    @staticmethod
    def generate_css_styles(size_name, cairo_font=None):
        """
        إنشاء أنماط CSS بناءً على حجم الخط المحدد

        Args:
            size_name (str): اسم حجم الخط
            cairo_font (str): اسم خط Cairo (إذا لم يتم تمرير شيء، سيتم تحميل الخط تلقائياً)

        Returns:
            str: نص CSS جاهز للاستخدام
        """
        # إذا لم يتم تمرير خط Cairo، قم بتحميله
        if cairo_font is None:
            cairo_font = FontSizeManager.load_cairo_font()

        font_sizes = FontSizeManager.get_font_sizes(size_name)

        css = f"""
            QWidget {{
                background-color: #F5F6F7;
                font-family: '{cairo_font}', 'Segoe UI', Tahoma, Arial;
                font-size: {font_sizes['base']}px;
            }}

            /* شريط الأدوات / الأقسام */
            #toolbarFrame, #summaryFrame, #tableFrame {{
                background-color: #FFFFFF;
                border: 1px solid #DDE1E4;
                border-radius: 4px;
            }}

            #filterLabel {{
                font-weight: 600;
                color: #37474F;
                margin-right: 4px;
                font-size: {font_sizes['filter_label']}px;
            }}

            #filterCombo {{
                padding: 4px 6px;
                border: 1px solid #C3C7CA;
                border-radius: 3px;
                background: #FFFFFF;
                min-width: 85px;
                font-size: {font_sizes['filter_combo']}px;
            }}

            #searchInput {{
                padding: 4px 10px;
                border: 1px solid #C3C7CA;
                border-radius: 14px;
                font-size: {font_sizes['search_input']}px;
                background-color: #FFFFFF;
            }}
            #searchInput:focus {{
                border: 1px solid #5B8DEF;
                background: #FFFFFF;
            }}

            /* أزرار مسطحة بألوان هادئة */
            #primaryButton, #groupButton, #secondaryButton {{
                background-color: #FFFFFF;
                color: #2F3A40;
                border: 1px solid #B5BCC0;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: 600;
                font-size: {font_sizes['buttons']}px;
            }}
            #primaryButton:hover, #groupButton:hover, #secondaryButton:hover {{
                background-color: #F0F3F5;
            }}
            #primaryButton:pressed, #groupButton:pressed, #secondaryButton:pressed {{
                background-color: #E2E6E9;
            }}

            /* تخصيص تمييز أنماط مختلفة عبر ظل خفيف فقط */
            #primaryButton {{ border-color: #8E44AD; color: #4A2F63; }}
            #groupButton {{ border-color: #2980B9; color: #1F5375; }}
            #secondaryButton {{ border-color: #229954; color: #1B5E33; }}

            /* الجدول */
            QTableWidget {{
                background: #FFFFFF;
                border: 1px solid #DDE1E4;
                gridline-color: #E3E6E8;
                font-size: {font_sizes['table']}px;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid #EEF0F1;
            }}
            QTableWidget::item:selected {{
                background-color: #5B8DEF;
                color: #FFFFFF;
            }}
            QHeaderView::section {{
                background: #ECEFF1;
                color: #37474F;
                padding: 4px 6px;
                border: 1px solid #D0D5D8;
                font-weight: 600;
                font-size: {font_sizes['table_header']}px;
            }}

            /* ملخص الإحصائيات */
            #summaryTitle {{
                font-size: {font_sizes['summary_title']}px;
                font-weight: 600;
                color: #37474F;
            }}
            #summaryLabel {{
                font-size: {font_sizes['summary_label']}px;
                color: #455A64;
            }}
            #summaryValue, #summaryValueSuccess, #summaryValueWarning {{
                font-size: {font_sizes['summary_value']}px;
                font-weight: 700;
                padding: 2px 4px;
            }}
            #summaryValueSuccess {{ color: #1B5E20; }}
            #summaryValueWarning {{ color: #B35C00; }}
            #statLabel {{
                font-size: {font_sizes['stat_label']}px;
                color: #546E7A;
            }}
        """

        return css.strip()

    @staticmethod
    def get_size_display_name(size_name):
        """
        الحصول على اسم العرض لحجم الخط

        Args:
            size_name (str): اسم حجم الخط

        Returns:
            str: اسم العرض
        """
        display_names = {
            "صغير جدا": "صغير جداً",
            "صغير": "صغير",
            "متوسط": "متوسط",
            "كبير": "كبير",
            "كبير جدا": "كبير جداً"
        }
        return display_names.get(size_name, size_name)

    @staticmethod
    def load_cairo_font():
        """
        تحميل خط Cairo وإرجاع اسم عائلة الخط

        Returns:
            str: اسم عائلة خط Cairo أو الخط الافتراضي
        """
        try:
            from PyQt5.QtGui import QFontDatabase
            from pathlib import Path
            import config

            # مسار مجلد الخطوط الصحيح
            font_dir = config.RESOURCES_DIR / "fonts"

            # تحميل خطوط Cairo
            font_db = QFontDatabase()
            id_medium = font_db.addApplicationFont(str(font_dir / "Cairo-Medium.ttf"))
            id_bold = font_db.addApplicationFont(str(font_dir / "Cairo-Bold.ttf"))

            # الحصول على اسم عائلة الخط
            families = font_db.applicationFontFamilies(id_medium)
            cairo_family = families[0] if families else "Arial"

            return cairo_family

        except Exception as e:
            print(f"فشل في تحميل خط Cairo، استخدام الخط الافتراضي: {e}")
            return "Arial"


# دالة مساعدة للتوافق مع الكود القديم
def get_font_sizes(size_name):
    """
    دالة مساعدة للحصول على أحجام الخطوط (للتوافق مع الكود القديم)

    Args:
        size_name (str): اسم حجم الخط المطلوب

    Returns:
        dict: قاموس يحتوي على أحجام الخطوط لكل عنصر
    """
    return FontSizeManager.get_font_sizes(size_name)
