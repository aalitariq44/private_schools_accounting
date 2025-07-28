# -*- coding: utf-8 -*-
"""
مدير الطباعة الرئيسي
"""

import logging
from typing import Dict, Any, Optional
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QTextDocument

from .print_config import PrintSettings, TemplateType
from .template_manager import TemplateManager
from .simple_print_preview import SimplePrintPreviewDialog

# محاولة استيراد محرك الويب الحديث
try:
    from .web_print_manager import WebPrintManager
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False
    logging.warning("محرك الويب الحديث غير متوفر، سيتم استخدام المحرك التقليدي")

class PrintManager:
    """إدارة عمليات الطباعة"""
    
    def __init__(self, parent=None, use_web_engine=True):
        self.parent = parent
        self.template_manager = TemplateManager()
        self.settings = self.template_manager.config.load_settings_from_config()
        self.use_web_engine = use_web_engine and WEB_ENGINE_AVAILABLE
        
        if self.use_web_engine:
            self.web_print_manager = WebPrintManager(parent)
            logging.info("تم تفعيل محرك الويب الحديث للطباعة")
        else:
            logging.info("تم تفعيل محرك الطباعة التقليدي")

    def print_document(self, template_type: TemplateType, data: Dict[str, Any], settings: Optional[PrintSettings] = None):
        """طباعة مستند"""
        current_settings = settings or self.settings
        
        html_content = self.template_manager.render_template(template_type, data)
        if not html_content:
            logging.error("فشل في تقديم القالب، لا يمكن الطباعة")
            return

        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setOrientation(QPrinter.Portrait)
        
        dialog = QPrintDialog(printer, self.parent)
        if dialog.exec_() == QPrintDialog.Accepted:
            doc = QTextDocument()
            doc.setHtml(html_content)
            doc.print_(printer)

    def preview_document(self, template_type: TemplateType, data: Dict[str, Any], settings: Optional[PrintSettings] = None):
        """معاينة مستند قبل الطباعة"""
        if self.use_web_engine:
            # استخدام محرك الويب الحديث
            self.web_print_manager.preview_document(template_type, data, settings)
        else:
            # استخدام المحرك التقليدي
            self._legacy_preview_document(template_type, data, settings)
    
    def _legacy_preview_document(self, template_type: TemplateType, data: Dict[str, Any], settings: Optional[PrintSettings] = None):
        """معاينة مستند باستخدام المحرك التقليدي"""
        current_settings = settings or self.settings
        
        html_content = self.template_manager.render_template(template_type, data)
        if not html_content:
            logging.error("فشل في تقديم القالب، لا يمكن المعاينة")
            return
            
        dialog = SimplePrintPreviewDialog(html_content, self.parent)
        dialog.exec_()
    
    def toggle_engine(self):
        """تبديل محرك الطباعة"""
        if WEB_ENGINE_AVAILABLE:
            self.use_web_engine = not self.use_web_engine
            if self.use_web_engine and not hasattr(self, 'web_print_manager'):
                self.web_print_manager = WebPrintManager(self.parent)
            
            engine_name = "الحديث" if self.use_web_engine else "التقليدي"
            logging.info(f"تم تغيير محرك الطباعة إلى: {engine_name}")
            return True
        return False

# Convenience functions for printing different templates

def print_students_list(students, filter_info=None, parent=None, use_web_engine=True):
    """طباعة قائمة الطلاب مع معاينة"""
    pm = PrintManager(parent, use_web_engine)
    data = {'students': students}
    if filter_info:
        data['filter_info'] = filter_info
    pm.preview_document(TemplateType.STUDENTS_LIST, data)


def print_student_report(data, parent=None, use_web_engine=True):
    """طباعة تقرير طالب مع معاينة"""
    pm = PrintManager(parent, use_web_engine)
    pm.preview_document(TemplateType.STUDENT_REPORT, data)


def print_payment_receipt(data, parent=None, use_web_engine=True):
    """طباعة إيصال دفع مع معاينة"""
    pm = PrintManager(parent, use_web_engine)
    # Ensure data is wrapped under 'receipt' key for the template
    payload = {'receipt': data} if not isinstance(data, dict) or 'receipt' not in data else data
    pm.preview_document(TemplateType.PAYMENT_RECEIPT, payload)


def print_financial_report(data, date_range=None, parent=None, use_web_engine=True):
    """طباعة التقرير المالي مع معاينة"""
    pm = PrintManager(parent, use_web_engine)
    payload = data.copy() if isinstance(data, dict) else {}
    if date_range:
        payload['date_range'] = date_range
    pm.preview_document(TemplateType.FINANCIAL_REPORT, payload)
