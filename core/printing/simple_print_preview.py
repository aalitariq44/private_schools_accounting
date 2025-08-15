# -*- coding: utf-8 -*-
"""
مربع حوار بسيط لمعاينة الطباعة
"""

import logging
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QMessageBox
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument

class SimplePrintPreviewDialog(QDialog):
    """مربع حوار بسيط لمعاينة الطباعة"""
    def __init__(self, html_content, parent=None):
        super().__init__(parent)
        self.html_content = html_content
        self.setWindowTitle("معاينة الطباعة")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)
        
        self.text_browser = QTextBrowser()
        self.text_browser.setHtml(self.html_content)
        layout.addWidget(self.text_browser)
        
        self.print_button = QPushButton("طباعة")
        self.print_button.clicked.connect(self.print_document)
        layout.addWidget(self.print_button)

    def print_document(self):
        """طباعة المستند"""
        try:
            from .safe_print_manager import SafePrintDialog
            from PyQt5.QtPrintSupport import QPrinter
            from PyQt5.QtGui import QTextDocument
            
            printer = QPrinter(QPrinter.HighResolution)
            
            def handle_print_request(printer_obj):
                """معالجة طلب الطباعة"""
                try:
                    doc = QTextDocument()
                    doc.setHtml(self.html_content)
                    doc.print_(printer_obj)
                    self.accept()
                except Exception as e:
                    logging.error(f"خطأ في طباعة المستند: {e}")
                    QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الطباعة: {str(e)}")
            
            # استخدام نافذة الطباعة الآمنة
            safe_dialog = SafePrintDialog(printer, self)
            safe_dialog.print_requested.connect(handle_print_request)
            safe_dialog.show_print_dialog()
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الطباعة: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في الطباعة: {str(e)}")
