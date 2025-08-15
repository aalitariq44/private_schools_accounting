# -*- coding: utf-8 -*-
"""
طباعة PDF مباشرة بطريقة بسيطة
"""

import logging
import os
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QTextDocument

def print_pdf_direct(pdf_path, parent=None):
    """طباعة PDF مباشرة باستخدام نافذة النظام"""
    try:
        if not os.path.exists(pdf_path):
            QMessageBox.warning(parent, "خطأ", "ملف PDF غير موجود")
            return False
        
        # محاولة طباعة مباشرة باستخدام الأمر النظام
        if os.name == 'nt':  # Windows
            try:
                import subprocess
                # طباعة صامتة باستخدام print command
                result = subprocess.run([
                    'powershell', '-Command', 
                    f'Start-Process -FilePath "{pdf_path}" -Verb Print -WindowStyle Hidden'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    QMessageBox.information(parent, "تم إرسال الطباعة", 
                        "تم إرسال الملف للطباعة!\n\n"
                        "تحقق من طابعتك الافتراضية.")
                    return True
                else:
                    raise Exception("فشل في الطباعة الصامتة")
                    
            except Exception as e:
                logging.error(f"فشل في الطباعة المباشرة: {e}")
                # العودة للطريقة اليدوية
                return print_pdf_with_dialog(pdf_path, parent)
        else:
            # Linux/Mac - طباعة مباشرة
            try:
                import subprocess
                subprocess.run(['lp', pdf_path], check=True)
                QMessageBox.information(parent, "تم إرسال الطباعة", "تم إرسال الملف للطباعة!")
                return True
            except:
                return print_pdf_with_dialog(pdf_path, parent)
                
    except Exception as e:
        logging.error(f"خطأ في طباعة PDF مباشرة: {e}")
        QMessageBox.warning(parent, "خطأ", f"حدث خطأ في الطباعة: {str(e)}")
        return False

def print_pdf_with_dialog(pdf_path, parent=None):
    """طباعة PDF مع نافذة اختيار الطابعة"""
    try:
        from core.printing.safe_print_manager import SafePrintDialog
        
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setOrientation(QPrinter.Portrait)
        
        def handle_print_request(printer_obj):
            """معالجة طلب الطباعة"""
            try:
                # محاولة طباعة الملف
                if os.name == 'nt':  # Windows
                    import subprocess
                    subprocess.run([
                        'powershell', '-Command', 
                        f'Start-Process -FilePath "{pdf_path}" -Verb Print'
                    ])
                else:
                    import subprocess
                    subprocess.run(['lp', pdf_path])
                
                QMessageBox.information(parent, "تم إرسال الطباعة", 
                    "تم إرسال الملف للطباعة بنجاح!")
                    
            except Exception as e:
                logging.error(f"خطأ في تنفيذ الطباعة: {e}")
                QMessageBox.information(parent, "معلومات", 
                    f"تم إنشاء الإيصال في:\n{pdf_path}\n\n"
                    "يمكنك فتحه وطباعته يدوياً")
        
        # استخدام نافذة الطباعة الآمنة
        safe_dialog = SafePrintDialog(printer, parent)
        safe_dialog.print_requested.connect(handle_print_request)
        success = safe_dialog.show_print_dialog()
        
        return success
        
    except Exception as e:
        logging.error(f"خطأ في طباعة PDF مع نافذة: {e}")
        QMessageBox.information(parent, "معلومات", 
            f"تم إنشاء الإيصال في:\n{pdf_path}\n\n"
            "يمكنك فتحه وطباعته يدوياً")
        return False
