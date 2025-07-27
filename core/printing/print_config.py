#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعدادات وتكوين الطباعة
"""

import os
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path
import config


class PaperSize(Enum):
    """أحجام الورق المدعومة"""
    A4 = "A4"
    A3 = "A3"
    LETTER = "Letter"
    LEGAL = "Legal"


class PrintOrientation(Enum):
    """اتجاهات الطباعة"""
    PORTRAIT = "Portrait"  # عمودي
    LANDSCAPE = "Landscape"  # أفقي


class PrintQuality(Enum):
    """جودة الطباعة"""
    DRAFT = "Draft"  # مسودة
    NORMAL = "Normal"  # عادي
    HIGH = "High"  # عالي


class TemplateType(Enum):
    """أنواع قوالب الطباعة"""
    STUDENT_REPORT = "student_report"
    STUDENT_LIST = "student_list"
    STUDENTS_LIST = "student_list"  # alias for plural usage
    FINANCIAL_REPORT = "financial_report"
    PAYMENT_RECEIPT = "payment_receipt"
    SALARY_SLIP = "salary_slip"
    STAFF_REPORT = "staff_report"
    SCHOOL_REPORT = "school_report"
    CUSTOM = "custom"


@dataclass
class PrintSettings:
    """إعدادات الطباعة"""
    paper_size: PaperSize = PaperSize.A4
    orientation: PrintOrientation = PrintOrientation.PORTRAIT
    quality: PrintQuality = PrintQuality.NORMAL
    margins: Dict[str, int] = None  # بالميليمتر
    font_family: str = "Arial"
    font_size: int = 12
    header_enabled: bool = True
    footer_enabled: bool = True
    page_numbers: bool = True
    watermark: Optional[str] = None

    def __post_init__(self):
        if self.margins is None:
            self.margins = {
                "top": 20,
                "bottom": 20,
                "left": 20,
                "right": 20
            }
    @property
    def margins_mm(self):
        """Alias for margins in tuple form (top, bottom, left, right)"""
        return (
            self.margins.get('top', 0),
            self.margins.get('bottom', 0),
            self.margins.get('left', 0),
            self.margins.get('right', 0)
        )

    @margins_mm.setter
    def margins_mm(self, values):
        """Set margins from tuple/list of (top, bottom, left, right)"""
        if isinstance(values, (list, tuple)) and len(values) == 4:
            self.margins = {
                'top': values[0],
                'bottom': values[1],
                'left': values[2],
                'right': values[3]
            }

    @property
    def show_header(self):
        """Alias for header_enabled"""
        return self.header_enabled

    @show_header.setter
    def show_header(self, value):
        self.header_enabled = bool(value)

    @property
    def show_footer(self):
        """Alias for footer_enabled"""
        return self.footer_enabled

    @show_footer.setter
    def show_footer(self, value):
        self.footer_enabled = bool(value)


class PrintConfig:
    """مدير إعدادات الطباعة"""
    
    def __init__(self):
        self.settings = PrintSettings()
        # Use the configured resources directory for templates
        resources_dir = Path(config.RESOURCES_DIR)
        self.templates_path = str(resources_dir / 'print_templates')
        # إنشاء مجلد القوالب إذا لم يكن موجوداً
        os.makedirs(self.templates_path, exist_ok=True)
    
    def get_template_path(self, template_type: TemplateType) -> str:
        """الحصول على مسار القالب"""
        return os.path.join(self.templates_path, f"{template_type.value}.html")
    
    def get_default_settings(self) -> PrintSettings:
        """الحصول على الإعدادات الافتراضية"""
        return PrintSettings()
    
    def load_settings_from_config(self) -> PrintSettings:
        """تحميل إعدادات الطباعة من ملف الإعدادات"""
        try:
            # يمكن تحميل الإعدادات من ملف JSON أو قاعدة البيانات
            return self.settings
        except Exception:
            return self.get_default_settings()
    
    def save_settings(self, settings: PrintSettings) -> bool:
        """حفظ إعدادات الطباعة"""
        try:
            self.settings = settings
            # يمكن حفظ الإعدادات في ملف JSON أو قاعدة البيانات
            return True
        except Exception:
            return False
    
    def get_paper_size_mm(self, paper_size: PaperSize) -> tuple:
        """الحصول على أبعاد الورق بالميليمتر"""
        sizes = {
            PaperSize.A4: (210, 297),
            PaperSize.A3: (297, 420),
            PaperSize.LETTER: (216, 279),
            PaperSize.LEGAL: (216, 356)
        }
        return sizes.get(paper_size, (210, 297))
    
    def get_supported_fonts(self) -> list:
        """الحصول على قائمة الخطوط المدعومة"""
        return [
            "Arial",
            "Times New Roman", 
            "Calibri",
            "Verdana",
            "Tahoma",
            "Georgia",
            "Comic Sans MS"
        ]
