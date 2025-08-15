# -*- coding: utf-8 -*-
"""
إصلاح مشكلة خروج التطبيق عند الطباعة
"""

import logging
import os
import sys
from PyQt5.QtCore import QTimer, pyqtSignal, QThread
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

class SafePrintDialog(QDialog):
    """نافذة طباعة آمنة تمنع إغلاق التطبيق"""
    
    print_requested = pyqtSignal(QPrinter)
    
    def __init__(self, printer, parent=None):
        super().__init__(parent)
        self.printer = printer
        self.print_dialog = None
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("طباعة")
        self.setModal(True)
        
    def show_print_dialog(self):
        """إظهار نافذة الطباعة بطريقة آمنة"""
        try:
            # إنشاء نافذة الطباعة
            self.print_dialog = QPrintDialog(self.printer, self)
            self.print_dialog.setWindowTitle("إعدادات الطباعة")
            
            # ربط الإشارات بطريقة آمنة
            result = self.print_dialog.exec_()
            
            if result == QPrintDialog.Accepted:
                self.print_requested.emit(self.printer)
                return True
            else:
                return False
                
        except Exception as e:
            logging.error(f"خطأ في نافذة الطباعة: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في نافذة الطباعة: {str(e)}")
            return False
            
    def closeEvent(self, event):
        """معالجة إغلاق النافذة"""
        if self.print_dialog:
            self.print_dialog.close()
        event.accept()

class SafePrintManager:
    """مدير طباعة آمن يمنع إغلاق التطبيق"""
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def safe_print_with_dialog(self, web_view, printer=None):
        """طباعة آمنة مع نافذة النظام"""
        try:
            if printer is None:
                printer = QPrinter(QPrinter.HighResolution)
                
            # إعداد الطابعة
            printer.setPageSize(QPrinter.A4)
            printer.setOrientation(QPrinter.Portrait)
            
            # إنشاء نافذة طباعة آمنة
            safe_dialog = SafePrintDialog(printer, self.parent)
            
            def handle_print_request(printer_obj):
                """معالجة طلب الطباعة"""
                try:
                    # استخدام QTimer لتأخير الطباعة قليلاً
                    QTimer.singleShot(100, lambda: self._do_print(web_view, printer_obj))
                except Exception as e:
                    logging.error(f"خطأ في معالجة طلب الطباعة: {e}")
                    
            safe_dialog.print_requested.connect(handle_print_request)
            
            # إظهار النافذة
            return safe_dialog.show_print_dialog()
            
        except Exception as e:
            logging.error(f"خطأ في المدير الآمن للطباعة: {e}")
            QMessageBox.critical(self.parent, "خطأ", f"حدث خطأ في الطباعة: {str(e)}")
            return False
            
    def _do_print(self, web_view, printer):
        """تنفيذ الطباعة الفعلية"""
        try:
            def print_finished(success):
                """عند انتهاء الطباعة"""
                if success:
                    QMessageBox.information(self.parent, "نجح", "تمت الطباعة بنجاح")
                else:
                    QMessageBox.warning(self.parent, "فشل", "فشلت الطباعة")
                    
            # طباعة الصفحة
            if hasattr(web_view, 'page') and hasattr(web_view.page(), 'print'):
                web_view.page().print(printer, print_finished)
            else:
                logging.error("محرك الويب لا يدعم الطباعة")
                QMessageBox.warning(self.parent, "خطأ", "محرك الويب لا يدعم الطباعة")
                
        except Exception as e:
            logging.error(f"خطأ في تنفيذ الطباعة: {e}")
            QMessageBox.critical(self.parent, "خطأ", f"حدث خطأ أثناء الطباعة: {str(e)}")

# دالة مساعدة للطباعة الآمنة
def safe_print_document(web_view, parent=None):
    """طباعة آمنة للمستندات"""
    try:
        manager = SafePrintManager(parent)
        return manager.safe_print_with_dialog(web_view)
    except Exception as e:
        logging.error(f"خطأ في الطباعة الآمنة: {e}")
        if parent:
            QMessageBox.critical(parent, "خطأ", f"حدث خطأ في الطباعة: {str(e)}")
        return False
