# -*- coding: utf-8 -*-
"""
مدير الطباعة الرئيسي
"""

import logging
from typing import Dict, Any, Optional
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QTextDocument

from .print_config import PrintSettings, TemplateType
from .template_manager import TemplateManager
from .simple_print_preview import SimplePrintPreviewDialog

class PrintManager:
    """إدارة عمليات الطباعة"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.template_manager = TemplateManager()
        self.settings = self.template_manager.config.load_settings_from_config()

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
        current_settings = settings or self.settings
        
        html_content = self.template_manager.render_template(template_type, data)
        if not html_content:
            logging.error("فشل في تقديم القالب، لا يمكن المعاينة")
            return
            
        dialog = SimplePrintPreviewDialog(html_content, self.parent)
        dialog.exec_()

# Convenience functions for printing different templates

def print_students_list(students, filter_info=None, parent=None):
    """طباعة قائمة الطلاب مع معاينة"""
    pm = PrintManager(parent)
    data = {'students': students}
    if filter_info:
        data['filter_info'] = filter_info
    pm.preview_document(TemplateType.STUDENTS_LIST, data)


def print_student_report(data, parent=None):
    """طباعة تقرير طالب مع معاينة"""
    pm = PrintManager(parent)
    pm.preview_document(TemplateType.STUDENT_REPORT, data)


def print_payment_receipt(data, parent=None):
    """طباعة إيصال دفع مع معاينة"""
    pm = PrintManager(parent)
    # Ensure data is wrapped under 'receipt' key for the template
    payload = {'receipt': data} if not isinstance(data, dict) or 'receipt' not in data else data
    pm.preview_document(TemplateType.PAYMENT_RECEIPT, payload)


def print_financial_report(data, date_range=None, parent=None):
    """طباعة التقرير المالي مع معاينة"""
    pm = PrintManager(parent)
    payload = data.copy() if isinstance(data, dict) else {}
    if date_range:
        payload['date_range'] = date_range
    pm.preview_document(TemplateType.FINANCIAL_REPORT, payload)
