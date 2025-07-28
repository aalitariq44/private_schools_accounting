# -*- coding: utf-8 -*-
"""
مدير الطباعة الرئيسي - يدعم مسارين:
1. HTML (QWebEngineView) - للتقارير البسيطة
2. ReportLab - للوصولات والفواتير الدقيقة
"""

import logging
from typing import Dict, Any, Optional
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QTextDocument

from .print_config import PrintSettings, TemplateType, PrintMethod, TEMPLATE_PRINT_METHODS
from .template_manager import TemplateManager
from .simple_print_preview import SimplePrintPreviewDialog

# محاولة استيراد محرك الويب الحديث
try:
    from .web_print_manager import WebPrintManager
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False
    logging.warning("محرك الويب الحديث غير متوفر، سيتم استخدام المحرك التقليدي")

# محاولة استيراد مدير ReportLab
try:
    from .reportlab_print_manager import ReportLabPrintManager
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab غير متوفر، سيتم استخدام مسار HTML فقط")

class PrintManager:
    """إدارة عمليات الطباعة - يدعم مسارين: HTML و ReportLab"""
    
    def __init__(self, parent=None, use_web_engine=True):
        self.parent = parent
        self.template_manager = TemplateManager()
        self.settings = self.template_manager.config.load_settings_from_config()
        self.use_web_engine = use_web_engine and WEB_ENGINE_AVAILABLE
        
        # إعداد مدير HTML
        if self.use_web_engine:
            self.web_print_manager = WebPrintManager(parent)
            logging.info("تم تفعيل محرك الويب الحديث للطباعة")
        else:
            logging.info("تم تفعيل محرك الطباعة التقليدي")
        
        # إعداد مدير ReportLab
        if REPORTLAB_AVAILABLE:
            self.reportlab_manager = ReportLabPrintManager()
            logging.info("تم تفعيل مدير ReportLab للطباعة")
        else:
            self.reportlab_manager = None
    
    def get_print_method(self, template_type: TemplateType) -> PrintMethod:
        """تحديد طريقة الطباعة المناسبة للقالب"""
        return TEMPLATE_PRINT_METHODS.get(template_type, PrintMethod.HTML_WEB_ENGINE)
    
    def preview_document(self, template_type: TemplateType, data: Dict[str, Any], settings: Optional[PrintSettings] = None):
        """معاينة مستند قبل الطباعة - يختار المسار المناسب تلقائياً"""
        print_method = self.get_print_method(template_type)
        
        if print_method == PrintMethod.REPORTLAB_CANVAS:
            return self._preview_reportlab_document(template_type, data, settings)
        else:
            return self._preview_html_document(template_type, data, settings)
    
    def _preview_html_document(self, template_type: TemplateType, data: Dict[str, Any], settings: Optional[PrintSettings] = None):
        """معاينة مستند HTML"""
        if self.use_web_engine:
            # استخدام محرك الويب الحديث
            self.web_print_manager.preview_document(template_type, data, settings)
        else:
            # استخدام المحرك التقليدي
            self._legacy_preview_document(template_type, data, settings)
    
    def _preview_reportlab_document(self, template_type: TemplateType, data: Dict[str, Any], settings: Optional[PrintSettings] = None):
        """معاينة مستند ReportLab"""
        if not self.reportlab_manager:
            logging.error("ReportLab غير متوفر، سيتم التبديل إلى مسار HTML")
            return self._preview_html_document(template_type, data, settings)
        
        try:
            if template_type == TemplateType.INSTALLMENT_RECEIPT:
                pdf_path = self.reportlab_manager.preview_installment_receipt(data)
                self._open_pdf_preview(pdf_path)
            elif template_type == TemplateType.PAYMENT_RECEIPT:
                # يمكن استخدام نفس الدالة لإيصالات الدفع العامة
                pdf_path = self.reportlab_manager.preview_installment_receipt(data)
                self._open_pdf_preview(pdf_path)
            else:
                logging.warning(f"نوع القالب {template_type.value} غير مدعوم في ReportLab، سيتم التبديل إلى HTML")
                return self._preview_html_document(template_type, data, settings)
                
        except Exception as e:
            logging.error(f"خطأ في معاينة ReportLab: {e}")
            return self._preview_html_document(template_type, data, settings)
    
    def _open_pdf_preview(self, pdf_path: str):
        """فتح معاينة PDF"""
        try:
            import os
            import subprocess
            
            if os.path.exists(pdf_path):
                # فتح الملف بالتطبيق الافتراضي
                if os.name == 'nt':  # Windows
                    os.startfile(pdf_path)
                elif os.name == 'posix':  # Linux/Mac
                    subprocess.run(['xdg-open', pdf_path])
                    
                logging.info(f"تم فتح معاينة PDF: {pdf_path}")
            else:
                logging.error(f"ملف PDF غير موجود: {pdf_path}")
                
        except Exception as e:
            logging.error(f"خطأ في فتح معاينة PDF: {e}")
    
    def print_document(self, template_type: TemplateType, data: Dict[str, Any], settings: Optional[PrintSettings] = None):
        """طباعة مستند - يختار المسار المناسب تلقائياً"""
        print_method = self.get_print_method(template_type)
        
        if print_method == PrintMethod.REPORTLAB_CANVAS:
            return self._print_reportlab_document(template_type, data, settings)
        else:
            return self._print_html_document(template_type, data, settings)
    
    def _print_html_document(self, template_type: TemplateType, data: Dict[str, Any], settings: Optional[PrintSettings] = None):
        """طباعة مستند HTML"""
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
    
    def _print_reportlab_document(self, template_type: TemplateType, data: Dict[str, Any], settings: Optional[PrintSettings] = None):
        """طباعة مستند ReportLab"""
        if not self.reportlab_manager:
            logging.error("ReportLab غير متوفر، سيتم التبديل إلى مسار HTML")
            return self._print_html_document(template_type, data, settings)
        
        try:
            if template_type in [TemplateType.INSTALLMENT_RECEIPT, TemplateType.PAYMENT_RECEIPT]:
                pdf_path = self.reportlab_manager.create_installment_receipt(data)
                self._open_pdf_preview(pdf_path)
                logging.info(f"تم إنشاء PDF للطباعة: {pdf_path}")
            else:
                logging.warning(f"نوع القالب {template_type.value} غير مدعوم في ReportLab")
                
        except Exception as e:
            logging.error(f"خطأ في طباعة ReportLab: {e}")
            return self._print_html_document(template_type, data, settings)
    
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


def print_installment_receipt(data, parent=None, use_web_engine=True):
    """طباعة إيصال دفع قسط مع معاينة - يستخدم ReportLab تلقائياً"""
    pm = PrintManager(parent, use_web_engine)
    # Ensure data is wrapped under 'receipt' key for the template
    payload = {'receipt': data} if not isinstance(data, dict) or 'receipt' not in data else data
    pm.preview_document(TemplateType.INSTALLMENT_RECEIPT, payload)


def print_payment_receipt(data, parent=None, use_web_engine=True):
    """طباعة إيصال دفع مع معاينة - يمكن أن يستخدم ReportLab أو HTML حسب التكوين"""
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
