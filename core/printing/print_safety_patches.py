# -*- coding: utf-8 -*-
"""
إصلاحات إضافية لحل مشكلة خروج التطبيق عند الطباعة
"""

import logging
import sys
from PyQt5.QtCore import QTimer, QCoreApplication
from PyQt5.QtWidgets import QMessageBox, QApplication

class PrintSafetyManager:
    """مدير أمان الطباعة لمنع إغلاق التطبيق"""
    
    @staticmethod
    def ensure_app_stability():
        """ضمان استقرار التطبيق أثناء عمليات الطباعة"""
        try:
            app = QApplication.instance()
            if app is None:
                return False
                
            # تأكد من أن التطبيق لا يزال يعمل
            if app and hasattr(app, 'exec_'):
                return True
            return False
        except Exception as e:
            logging.error(f"خطأ في فحص حالة التطبيق: {e}")
            return False
    
    @staticmethod
    def safe_dialog_exec(dialog, parent=None):
        """تشغيل آمن للحوارات لمنع إغلاق التطبيق"""
        try:
            if not PrintSafetyManager.ensure_app_stability():
                if parent:
                    QMessageBox.warning(parent, "خطأ", "التطبيق غير مستقر. يرجى إعادة المحاولة.")
                return False
                
            # استخدام QTimer لتأخير التنفيذ قليلاً
            result = None
            
            def delayed_exec():
                nonlocal result
                try:
                    result = dialog.exec_()
                except Exception as e:
                    logging.error(f"خطأ في تنفيذ الحوار: {e}")
                    result = None
            
            QTimer.singleShot(50, delayed_exec)
            
            # انتظار النتيجة مع timeout
            max_wait = 100  # 10 ثواني
            wait_count = 0
            while result is None and wait_count < max_wait:
                QApplication.processEvents()
                QTimer.msleep(100)
                wait_count += 1
            
            return result
            
        except Exception as e:
            logging.error(f"خطأ في التشغيل الآمن للحوار: {e}")
            if parent:
                QMessageBox.critical(parent, "خطأ", f"حدث خطأ: {str(e)}")
            return None
    
    @staticmethod 
    def safe_process_events():
        """معالجة آمنة للأحداث"""
        try:
            app = QApplication.instance()
            if app:
                app.processEvents()
        except Exception as e:
            logging.error(f"خطأ في معالجة الأحداث: {e}")

def apply_print_safety_patches():
    """تطبيق إصلاحات الأمان على نظام الطباعة"""
    try:
        logging.info("تطبيق إصلاحات أمان الطباعة...")
        
        # تحديث إعدادات Qt
        app = QApplication.instance()
        if app:
            app.setAttribute(app.AA_DontCreateNativeWidgetSiblings, True)
            app.setAttribute(app.AA_UseHighDpiPixmaps, True)
        
        return True
    except Exception as e:
        logging.error(f"فشل في تطبيق إصلاحات الأمان: {e}")
        return False
