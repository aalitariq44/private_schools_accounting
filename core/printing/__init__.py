# -*- coding: utf-8 -*-
"""
نظام الطباعة المزدوج المتقدم
يدعم ثلاثة محركات للطباعة:
1. المحرك التقليدي (QTextDocument) 
2. المحرك الحديث (QWebEngineView) - يوفر دعماً كاملاً لـ CSS الحديث
3. محرك ReportLab - للوصولات والفواتير الدقيقة مع دعم العربية
"""

from .print_config import (
    PaperSize,
    PrintOrientation,
    PrintQuality,
    TemplateType,
    PrintSettings,
    PrintConfig,
    PrintMethod,
    TEMPLATE_PRINT_METHODS
)
from .template_manager import TemplateManager
from .print_manager import (
    PrintManager,
    print_student_report,
    print_students_list,
    print_payment_receipt,
    print_installment_receipt,
    print_financial_report
)
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

# محاولة استيراد محرك ReportLab
try:
    from .reportlab_print_manager import ReportLabPrintManager
    from .quick_print import (
        QuickPrintInterface,
        quick_print_installment,
        quick_print_student_report
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

__all__ = [
    'PaperSize', 'PrintOrientation', 'PrintQuality', 'TemplateType',
    'PrintSettings', 'PrintConfig', 'PrintMethod', 'TEMPLATE_PRINT_METHODS',
    'TemplateManager', 'PrintManager',
    'print_student_report', 'print_students_list', 'print_payment_receipt',
    'print_installment_receipt', 'print_financial_report',
    'apply_print_styles', 'PrintHelper', 'QuickPrintMixin',
    'SimplePrintPreviewDialog', 'WEB_ENGINE_AVAILABLE', 'REPORTLAB_AVAILABLE'
]

if WEB_ENGINE_AVAILABLE:
    __all__.extend([
        'WebPrintManager',
        'web_print_payment_receipt',
        'web_print_students_list', 
        'web_print_student_report',
        'web_print_financial_report'
    ])

if REPORTLAB_AVAILABLE:
    __all__.extend([
        'ReportLabPrintManager',
        'QuickPrintInterface',
        'quick_print_installment',
        'quick_print_student_report'
    ])
