#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف إعداد سريع لدعم التصميم المتجاوب في صفحات التطبيق
"""

import os
import sys
from pathlib import Path

def update_ui_pages_for_responsive():
    """تحديث ملفات الصفحات لدعم التصميم المتجاوب"""
    
    base_dir = Path(__file__).parent
    ui_pages_dir = base_dir / "ui" / "pages"
    
    # إنشاء مجلدات الصفحات إذا لم تكن موجودة
    pages_to_create = [
        "dashboard",
        "schools", 
        "students",
        "teachers",
        "employees",
        "installments",
        "additional_fees",
        "external_income", 
        "expenses",
        "salaries",
        "backup",
        "settings"
    ]
    
    for page_name in pages_to_create:
        page_dir = ui_pages_dir / page_name
        page_dir.mkdir(parents=True, exist_ok=True)
        
        # إنشاء ملف __init__.py
        init_file = page_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("", encoding='utf-8')
        
        # إنشاء ملف الصفحة الأساسي
        page_file = page_dir / f"{page_name}_page.py"
        if not page_file.exists():
            content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة {page_name} - متجاوبة مع أحجام الشاشات المختلفة
"""

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt
from core.utils.responsive_design import responsive


class {page_name.title().replace('_', '')}Page(QWidget):
    """صفحة {page_name}"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.apply_responsive_styles()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(
                responsive.get_padding(20),
                responsive.get_padding(20), 
                responsive.get_padding(20),
                responsive.get_padding(20)
            )
            main_layout.setSpacing(responsive.get_padding(15))
            
            # العنوان
            title_label = QLabel("صفحة {page_name}")
            title_label.setObjectName("pageTitle")
            title_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(title_label)
            
            # منطقة المحتوى
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            
            # إضافة محتوى تجريبي
            info_label = QLabel("هذه صفحة تجريبية - سيتم تطويرها لاحقاً")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("color: #7F8C8D; font-size: 16px;")
            content_layout.addWidget(info_label)
            
            # منطقة قابلة للتمرير
            scroll_area = QScrollArea()
            scroll_area.setWidget(content_widget)
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            main_layout.addWidget(scroll_area)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة {page_name}: {{e}}")
    
    def apply_responsive_styles(self):
        """تطبيق التنسيقات المتجاوبة"""
        try:
            style_vars = responsive.get_responsive_stylesheet_vars()
            
            style = f"""
                #pageTitle {{
                    font-size: {{style_vars['title_font_size']}}px;
                    font-weight: bold;
                    color: #2C3E50;
                    padding: {{style_vars['base_padding']}}px;
                }}
                
                QScrollArea {{
                    border: none;
                    background-color: transparent;
                }}
                
                QScrollBar:vertical {{
                    background-color: #ECF0F1;
                    width: {{style_vars['scrollbar_width']}}px;
                    border: none;
                }}
                
                QScrollBar::handle:vertical {{
                    background-color: #BDC3C7;
                    border-radius: {{style_vars['border_radius']}}px;
                }}
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في تطبيق التنسيقات المتجاوبة لصفحة {page_name}: {{e}}")
'''
            page_file.write_text(content, encoding='utf-8')
            print(f"تم إنشاء صفحة: {page_name}")
    
    print("تم إنشاء جميع الصفحات بنجاح!")


if __name__ == "__main__":
    update_ui_pages_for_responsive()
