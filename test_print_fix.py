# -*- coding: utf-8 -*-
"""
اختبار إصلاحات الطباعة الآمنة
"""

import sys
import os
import logging
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt
from core.printing.safe_print_manager import SafePrintManager, SafePrintDialog
from PyQt5.QtPrintSupport import QPrinter

class TestPrintWindow(QMainWindow):
    """نافذة اختبار الطباعة الآمنة"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار إصلاحات الطباعة")
        self.setGeometry(200, 200, 400, 300)
        
        # إعداد واجهة المستخدم
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # زر اختبار الطباعة الآمنة
        test_safe_print_btn = QPushButton("اختبار الطباعة الآمنة")
        test_safe_print_btn.clicked.connect(self.test_safe_print)
        layout.addWidget(test_safe_print_btn)
        
        # زر اختبار نافذة الطباعة الآمنة
        test_safe_dialog_btn = QPushButton("اختبار نافذة الطباعة الآمنة")
        test_safe_dialog_btn.clicked.connect(self.test_safe_dialog)
        layout.addWidget(test_safe_dialog_btn)
        
        # زر اختبار الطباعة التقليدية (للمقارنة)
        test_traditional_btn = QPushButton("اختبار الطباعة التقليدية")
        test_traditional_btn.clicked.connect(self.test_traditional_print)
        layout.addWidget(test_traditional_btn)
        
    def test_safe_print(self):
        """اختبار المدير الآمن للطباعة"""
        try:
            from PyQt5.QtWebEngineWidgets import QWebEngineView
            
            # إنشاء محتوى ويب بسيط للاختبار
            web_view = QWebEngineView()
            html_content = """
            <html>
            <head><title>اختبار الطباعة</title></head>
            <body style="direction: rtl; font-family: Arial;">
                <h1>اختبار الطباعة الآمنة</h1>
                <p>هذا اختبار للتأكد من أن الطباعة تعمل دون إغلاق التطبيق</p>
                <p>تاريخ الاختبار: 15 أغسطس 2025</p>
            </body>
            </html>
            """
            web_view.setHtml(html_content)
            
            # استخدام المدير الآمن
            safe_manager = SafePrintManager(self)
            success = safe_manager.safe_print_with_dialog(web_view)
            
            if success:
                QMessageBox.information(self, "نجح", "تم الاختبار الآمن بنجاح!")
            else:
                QMessageBox.information(self, "تم الإلغاء", "تم إلغاء الاختبار")
                
        except Exception as e:
            logging.error(f"خطأ في اختبار الطباعة الآمنة: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في الاختبار: {str(e)}")
    
    def test_safe_dialog(self):
        """اختبار نافذة الطباعة الآمنة فقط"""
        try:
            printer = QPrinter(QPrinter.HighResolution)
            
            def handle_print_request(printer_obj):
                QMessageBox.information(self, "نجح", "تم استلام طلب الطباعة بنجاح!")
            
            safe_dialog = SafePrintDialog(printer, self)
            safe_dialog.print_requested.connect(handle_print_request)
            result = safe_dialog.show_print_dialog()
            
            if not result:
                QMessageBox.information(self, "تم الإلغاء", "تم إلغاء نافذة الطباعة")
                
        except Exception as e:
            logging.error(f"خطأ في اختبار نافذة الطباعة: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في الاختبار: {str(e)}")
    
    def test_traditional_print(self):
        """اختبار الطباعة التقليدية (للمقارنة)"""
        try:
            from PyQt5.QtPrintSupport import QPrintDialog
            
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec_() == QPrintDialog.Accepted:
                QMessageBox.information(self, "نجح", "الطباعة التقليدية نجحت")
            else:
                QMessageBox.information(self, "تم الإلغاء", "تم إلغاء الطباعة التقليدية")
                
        except Exception as e:
            logging.error(f"خطأ في الطباعة التقليدية: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في الاختبار: {str(e)}")

def main():
    """دالة الاختبار الرئيسية"""
    app = QApplication(sys.argv)
    
    # إعداد خصائص التطبيق
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings, True)
    
    window = TestPrintWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
