# -*- coding: utf-8 -*-
"""
نظام الطباعة المتقدم
يدعم محركين للطباعة:
1. المحرك التقليدي (QTextDocument) 
2. المحرك الحديث (QWebEngineView) - يوفر دعماً كاملاً لـ CSS الحديث
"""

from .print_config import (
    PaperSize,
    PrintOrientation,
    PrintQuality,
    TemplateType,
    PrintSettings,
    PrintConfig
)
from .template_manager import TemplateManager
from .print_manager import PrintManager
from .print_utils import (
    apply_print_styles,
    PrintHelper,
    QuickPrintMixin
)
from .simple_print_preview import SimplePrintPreviewDialog

# محاولة استيراد محرك الويب الحديث
try:
    from .web_print_manager import (
        WebPrintManager,
        web_print_payment_receipt,
        web_print_students_list,
        web_print_student_report,
        web_print_financial_report
    )
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False

__all__ = [
    'PaperSize', 'PrintOrientation', 'PrintQuality', 'TemplateType',
    'PrintSettings', 'PrintConfig', 'TemplateManager', 'PrintManager',
    'apply_print_styles', 'PrintHelper', 'QuickPrintMixin',
    'SimplePrintPreviewDialog', 'WEB_ENGINE_AVAILABLE'
]

if WEB_ENGINE_AVAILABLE:
    __all__.extend([
        'WebPrintManager',
        'web_print_payment_receipt',
        'web_print_students_list', 
        'web_print_student_report',
        'web_print_financial_report'
    ])
