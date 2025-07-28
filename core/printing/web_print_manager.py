# -*- coding: utf-8 -*-
"""
مدير الطباعة المحدث باستخدام محرك الويب الحديث (QWebEngineView)
"""

import logging
import os
import tempfile
from typing import Dict, Any, Optional
from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtPrintSupport import QPrinter

from .print_config import PrintSettings, TemplateType
from .template_manager import TemplateManager


class WebPrintPage(QWebEnginePage):
    """صفحة ويب مخصصة للطباعة"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        """التعامل مع رسائل الكونسول من JavaScript"""
        logging.debug(f"JS Console: {message}")


class WebPrintPreviewDialog(QDialog):
    """مربع حوار معاينة الطباعة باستخدام محرك الويب الحديث"""
    
    def __init__(self, html_content: str, parent=None):
        super().__init__(parent)
        self.html_content = html_content
        self.temp_file_path = None
        self.setup_ui()
        self.load_content()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("معاينة الطباعة - محرك ويب حديث")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        
        layout = QVBoxLayout(self)
        
        # محرك الويب للمعاينة
        self.web_view = QWebEngineView()
        self.web_page = WebPrintPage()
        self.web_view.setPage(self.web_page)
        layout.addWidget(self.web_view)
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        
        self.print_button = QPushButton("طباعة")
        self.print_button.clicked.connect(self.print_document)
        buttons_layout.addWidget(self.print_button)
        
        self.save_pdf_button = QPushButton("حفظ كـ PDF")
        self.save_pdf_button.clicked.connect(self.save_as_pdf)
        buttons_layout.addWidget(self.save_pdf_button)
        
        self.close_button = QPushButton("إغلاق")
        self.close_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.close_button)
        
        layout.addLayout(buttons_layout)
    
    def load_content(self):
        """تحميل المحتوى في محرك الويب"""
        try:
            # إنشاء ملف مؤقت للـ HTML
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', 
                                           encoding='utf-8', delete=False) as temp_file:
                temp_file.write(self.html_content)
                self.temp_file_path = temp_file.name
            
            # تحميل الملف في محرك الويب
            file_url = QUrl.fromLocalFile(os.path.abspath(self.temp_file_path))
            self.web_view.load(file_url)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المحتوى: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المحتوى: {e}")
    
    def print_document(self):
        """طباعة المستند"""
        try:
            # استخدام طباعة محرك الويب الحديث
            self.web_page.print(QPrinter(), self._on_print_finished)
        except Exception as e:
            logging.error(f"خطأ في الطباعة: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في الطباعة: {e}")
    
    def _on_print_finished(self, success):
        """مُستدعى عند انتهاء الطباعة"""
        if success:
            QMessageBox.information(self, "نجح", "تمت الطباعة بنجاح")
            self.accept()
        else:
            QMessageBox.warning(self, "تحذير", "فشلت عملية الطباعة")
    
    def save_as_pdf(self):
        """حفظ كملف PDF"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "حفظ كـ PDF", "receipt.pdf", "PDF Files (*.pdf)"
            )
            
            if file_path:
                self.web_page.printToPdf(file_path)
                QMessageBox.information(self, "نجح", f"تم حفظ الملف في: {file_path}")
                
        except Exception as e:
            logging.error(f"خطأ في حفظ PDF: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ PDF: {e}")
    
    def closeEvent(self, event):
        """تنظيف الملفات المؤقتة عند الإغلاق"""
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            try:
                os.unlink(self.temp_file_path)
            except Exception as e:
                logging.warning(f"فشل في حذف الملف المؤقت: {e}")
        event.accept()


class WebPrintManager:
    """مدير الطباعة المحدث باستخدام محرك الويب الحديث"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.template_manager = TemplateManager()
        self.settings = self.template_manager.config.load_settings_from_config()
    
    def preview_document(self, template_type: TemplateType, data: Dict[str, Any], 
                        settings: Optional[PrintSettings] = None):
        """معاينة مستند باستخدام محرك الويب الحديث"""
        try:
            current_settings = settings or self.settings
            
            html_content = self.template_manager.render_template(template_type, data)
            if not html_content:
                logging.error("فشل في تقديم القالب، لا يمكن المعاينة")
                QMessageBox.critical(self.parent, "خطأ", "فشل في تقديم القالب")
                return
            
            # إضافة معلومات إضافية للقالب
            enhanced_html = self._enhance_html_for_print(html_content)
            
            dialog = WebPrintPreviewDialog(enhanced_html, self.parent)
            dialog.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في معاينة المستند: {e}")
            QMessageBox.critical(self.parent, "خطأ", f"فشل في المعاينة: {e}")
    
    def _enhance_html_for_print(self, html_content: str) -> str:
        """تحسين HTML للطباعة بمحرك ويب حديث"""
        # إضافة تحسينات CSS للطباعة
        enhanced_css = """
        <style>
        /* تحسينات إضافية للطباعة بمحرك ويب حديث */
        @media print {
            body {
                -webkit-print-color-adjust: exact !important;
                color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            
            .receipt {
                box-shadow: none !important;
                border: 2px solid #333 !important;
            }
            
            .info-table {
                border-collapse: collapse !important;
            }
            
            .info-table td, .info-table th {
                border: 1px solid #333 !important;
                -webkit-print-color-adjust: exact !important;
            }
        }
        
        /* تحسينات للعرض على الشاشة */
        @media screen {
            body {
                padding: 20px;
                background: #f5f5f5;
            }
            
            .receipt {
                background: white;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
        }
        </style>
        """
        
        # إدراج CSS المحسن قبل </head>
        if "</head>" in html_content:
            html_content = html_content.replace("</head>", enhanced_css + "</head>")
        else:
            # إذا لم يوجد head، أضف في البداية
            html_content = enhanced_css + html_content
        
        return html_content


# دوال مساعدة محدّثة
def web_print_payment_receipt(data, parent=None):
    """طباعة إيصال دفع باستخدام محرك الويب الحديث"""
    pm = WebPrintManager(parent)
    payload = {'receipt': data} if not isinstance(data, dict) or 'receipt' not in data else data
    pm.preview_document(TemplateType.PAYMENT_RECEIPT, payload)


def web_print_students_list(students, filter_info=None, parent=None):
    """طباعة قائمة الطلاب باستخدام محرك الويب الحديث"""
    pm = WebPrintManager(parent)
    data = {'students': students}
    if filter_info:
        data['filter_info'] = filter_info
    pm.preview_document(TemplateType.STUDENTS_LIST, data)


def web_print_student_report(data, parent=None):
    """طباعة تقرير طالب باستخدام محرك الويب الحديث"""
    pm = WebPrintManager(parent)
    pm.preview_document(TemplateType.STUDENT_REPORT, data)


def web_print_financial_report(data, date_range=None, parent=None):
    """طباعة التقرير المالي باستخدام محرك الويب الحديث"""
    pm = WebPrintManager(parent)
    payload = data.copy() if isinstance(data, dict) else {}
    if date_range:
        payload['date_range'] = date_range
    pm.preview_document(TemplateType.FINANCIAL_REPORT, payload)
