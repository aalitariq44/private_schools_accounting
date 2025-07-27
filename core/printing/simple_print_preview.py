# -*- coding: utf-8 -*-
"""
مربع حوار بسيط لمعاينة الطباعة
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
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
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            doc = QTextDocument()
            doc.setHtml(self.html_content)
            doc.print_(printer)
            self.accept()
