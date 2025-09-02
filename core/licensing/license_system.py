#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام فحص الترخيص عند بدء التطبيق
"""

import sys
import logging
from typing import Tuple
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal

from .license_manager import LicenseManager
from .activation_dialog import show_activation_dialog


class LicenseChecker(QThread):
    """خيط فحص الترخيص في الخلفية"""
    
    check_completed = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.license_manager = LicenseManager()
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """تشغيل فحص الترخيص"""
        try:
            is_valid, message = self.license_manager.validate_license()
            self.check_completed.emit(is_valid, message)
        except Exception as e:
            self.logger.error(f"خطأ في فحص الترخيص: {e}")
            self.check_completed.emit(False, f"خطأ في فحص الترخيص: {str(e)}")


class LicenseSystem:
    """نظام إدارة التراخيص الشامل"""
    
    def __init__(self, app: QApplication = None):
        self.app = app or QApplication.instance()
        self.logger = logging.getLogger(__name__)
        self.license_manager = LicenseManager()
        self.checker = None
    
    def check_license_status(self) -> Tuple[bool, str]:
        """
        فحص حالة الترخيص (متزامن)
        Returns: (is_valid, message)
        """
        try:
            return self.license_manager.validate_license()
        except Exception as e:
            self.logger.error(f"خطأ في فحص الترخيص: {e}")
            return False, f"خطأ في فحص الترخيص: {str(e)}"
    
    def run_license_check(self) -> bool:
        """
        تشغيل فحص الترخيص الكامل
        Returns: True إذا كان الترخيص صالح أو تم تفعيله، False للخروج من التطبيق
        """
        try:
            self.logger.info("بدء فحص نظام التراخيص...")
            
            # فحص الترخيص الحالي
            is_valid, message = self.check_license_status()
            
            if is_valid:
                self.logger.info(f"الترخيص صالح: {message}")
                # تحديث آخر فحص (اختياري)
                try:
                    self.license_manager.update_last_checkin()
                except:
                    pass  # تجاهل أخطاء تحديث آخر فحص
                return True
            
            self.logger.warning(f"الترخيص غير صالح: {message}")
            
            # إظهار نافذة التفعيل
            return self.show_activation_dialog()
            
        except Exception as e:
            self.logger.error(f"خطأ عام في نظام التراخيص: {e}")
            self.show_error_message(
                "خطأ في نظام التراخيص",
                f"حدث خطأ غير متوقع في نظام التراخيص:\\n{str(e)}\\n\\n"
                "يرجى التواصل مع الدعم الفني."
            )
            return False
    
    def show_activation_dialog(self) -> bool:
        """عرض نافذة التفعيل"""
        try:
            self.logger.info("عرض نافذة تفعيل الترخيص")
            
            # عرض رسالة توضيحية
            msg = QMessageBox()
            msg.setWindowTitle("تفعيل الترخيص مطلوب")
            msg.setIcon(QMessageBox.Information)
            msg.setText("يتطلب تفعيل الترخيص للمتابعة")
            msg.setInformativeText(
                "لم يتم العثور على ترخيص صالح لهذا الجهاز.\n"
                "سيتم فتح نافذة التفعيل لإدخال رمز الترخيص."
            )
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Ok)
            
            if msg.exec_() != QMessageBox.Ok:
                return False
            
            # عرض نافذة التفعيل
            success = show_activation_dialog()
            
            if success:
                self.logger.info("تم تفعيل الترخيص بنجاح")
                return True
            else:
                self.logger.warning("تم إلغاء تفعيل الترخيص")
                return False
                
        except Exception as e:
            self.logger.error(f"خطأ في عرض نافذة التفعيل: {e}")
            return False
    
    def show_error_message(self, title: str, message: str):
        """عرض رسالة خطأ"""
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def run_background_check(self, callback=None):
        """تشغيل فحص الترخيص في الخلفية"""
        if self.checker and self.checker.isRunning():
            return
        
        self.checker = LicenseChecker()
        
        def on_check_completed(is_valid, message):
            if callback:
                callback(is_valid, message)
            else:
                if not is_valid:
                    self.logger.warning(f"فشل فحص الترخيص في الخلفية: {message}")
                else:
                    self.logger.debug(f"فحص الترخيص في الخلفية نجح: {message}")
        
        self.checker.check_completed.connect(on_check_completed)
        self.checker.start()
    
    def get_license_info(self):
        """الحصول على معلومات الترخيص الحالي"""
        return self.license_manager.get_license_info()
    
    def is_license_valid(self) -> bool:
        """فحص سريع لصحة الترخيص"""
        is_valid, _ = self.check_license_status()
        return is_valid


def initialize_license_system(app: QApplication = None) -> Tuple[bool, LicenseSystem]:
    """
    تهيئة نظام التراخيص
    Returns: (success, license_system)
    """
    try:
        license_system = LicenseSystem(app)
        success = license_system.run_license_check()
        return success, license_system
    except Exception as e:
        logging.error(f"خطأ في تهيئة نظام التراخيص: {e}")
        return False, None


def quick_license_check() -> bool:
    """فحص سريع للترخيص بدون واجهة المستخدم"""
    try:
        license_manager = LicenseManager()
        is_valid, _ = license_manager.validate_license()
        return is_valid
    except Exception:
        return False
