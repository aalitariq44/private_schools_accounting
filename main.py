#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نقطة البداية الرئيسية لتطبيق حسابات المدارس الأهلية
"""

import sys
import os
import logging
from pathlib import Path

# إضافة مسار المشروع إلى Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QDir, QTranslator, QLocale
from PyQt5.QtGui import QFont, QIcon, QFontDatabase

# استيراد إعدادات المشروع
import config
from core.utils.logger import setup_logging
from core.database.connection import DatabaseManager
from core.auth.login_manager import AuthManager
from ui.auth.login_window import LoginWindow
from app.main_window import MainWindow

# Monkey-patch hashlib to ignore deprecated 'usedforsecurity' keyword
import hashlib
# Patch hashlib.new to remove 'usedforsecurity' if present
_orig_hashlib_new = hashlib.new
def _patched_hashlib_new(name, data=b'', **kwargs):
    kwargs.pop('usedforsecurity', None)
    return _orig_hashlib_new(name, data, **kwargs)
hashlib.new = _patched_hashlib_new
# Patch md5 constructor to ignore 'usedforsecurity'
_orig_md5 = hashlib.md5
def _patched_md5(data=b'', **kwargs):
    kwargs.pop('usedforsecurity', None)
    return _orig_md5(data)
hashlib.md5 = _patched_md5
# Patch openssl_md5 if available
if hasattr(hashlib, 'openssl_md5'):
    _orig_openssl_md5 = hashlib.openssl_md5
    def _patched_openssl_md5(data=b'', **kwargs):
        return _orig_openssl_md5(data)
    hashlib.openssl_md5 = _patched_openssl_md5


class SchoolAccountingApp:
    """الفئة الرئيسية للتطبيق"""
    
    def __init__(self):
        """تهيئة التطبيق"""
        self.app = None
        self.main_window = None
        self.login_window = None
        self.setup_logging()
        
    def setup_logging(self):
        """إعداد نظام التسجيل"""
        try:
            setup_logging()
            logging.info("تم تشغيل التطبيق")
        except Exception as e:
            print(f"خطأ في إعداد نظام التسجيل: {e}")
    
    def setup_application(self):
        """إعداد تطبيق Qt"""
        try:
            # إنشاء تطبيق Qt
            self.app = QApplication(sys.argv)
            
            # إعداد خصائص التطبيق
            self.app.setApplicationName(config.APP_NAME)
            self.app.setApplicationVersion(config.APP_VERSION)
            self.app.setOrganizationName(config.APP_ORGANIZATION)
            
            # إعداد الخط العربي (تحميل وتعيين الخط الافتراضي)
            self.setup_arabic_font()
            
            # إعداد اتجاه التطبيق (من اليمين إلى اليسار)
            self.app.setLayoutDirection(Qt.RightToLeft)
            
            # إعداد أيقونة التطبيق
            self.setup_app_icon()
            
            return True
            
        except Exception as e:
            logging.error(f"خطأ في إعداد التطبيق: {e}")
            return False
    
    def setup_arabic_font(self):
        """إعداد الخط العربي"""
        try:
            # تحميل خطوط Cairo
            font_db = QFontDatabase()
            font_dir = config.RESOURCES_DIR / "fonts"
            id_medium = font_db.addApplicationFont(str(font_dir / "Cairo-Medium.ttf"))
            id_bold = font_db.addApplicationFont(str(font_dir / "Cairo-Bold.ttf"))
            # اختيار اسم العائلة بعد التحميل
            families = font_db.applicationFontFamilies(id_medium)
            cairo_family = families[0] if families else "Cairo"
            # ضبط الخط الافتراضي للتطبيق
            app_font = QFont(cairo_family, 10)
            self.app.setFont(app_font)
            
        except Exception as e:
            logging.warning(f"تحذير: لم يتم تطبيق الخط العربي: {e}")
    
    def setup_app_icon(self):
        """إعداد أيقونة التطبيق"""
        try:
            icon_path = config.RESOURCES_DIR / "images" / "icons" / "logo.png"
            if icon_path.exists():
                self.app.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            logging.warning(f"تحذير: لم يتم تحميل أيقونة التطبيق: {e}")
    
    def setup_database(self):
        """إعداد قاعدة البيانات"""
        try:
            db_manager = DatabaseManager()
            if db_manager.initialize_database():
                logging.info("تم إعداد قاعدة البيانات بنجاح")
                return True
            else:
                error_msg = "فشل في إنشاء جداول قاعدة البيانات"
                logging.error(error_msg)
                self.show_error_dialog("خطأ", error_msg)
                return False
        except Exception as e:
            logging.error(f"خطأ في إعداد قاعدة البيانات: {e}", exc_info=True)
            self.show_error_dialog("خطأ", f"خطأ في إعداد قاعدة البيانات: {e}")
            return False
    
    def show_error_dialog(self, title, message):
        """عرض رسالة خطأ"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setLayoutDirection(Qt.RightToLeft)
        msg.exec_()
    
    def authenticate_user(self):
        """مصادقة المستخدم"""
        try:
            auth_manager = AuthManager()
            
            # التحقق من وجود مستخدم في النظام
            if not auth_manager.has_users():
                # إعداد كلمة مرور أولى واسم المؤسسة
                from ui.auth.first_setup_dialog import FirstSetupDialog
                setup_dialog = FirstSetupDialog()
                
                if setup_dialog.exec_() == setup_dialog.Accepted:
                    password = setup_dialog.get_password()
                    organization_name = setup_dialog.get_organization_name()
                    
                    # إنشاء المستخدم الأول
                    if auth_manager.create_first_user(password):
                        logging.info("تم إنشاء المستخدم الأول بنجاح")
                        
                        # حفظ اسم المؤسسة إذا لم يكن محفوظاً بالفعل
                        from core.utils.settings_manager import settings_manager
                        if not settings_manager.get_organization_name() and organization_name:
                            settings_manager.set_organization_name(organization_name)
                            logging.info(f"تم حفظ اسم المؤسسة: {organization_name}")
                        
                    else:
                        self.show_error_dialog("خطأ", "فشل في إنشاء المستخدم الأول")
                        return False
                else:
                    return False
            else:
                # التحقق من وجود اسم المؤسسة للمستخدمين الحاليين
                from core.utils.settings_manager import settings_manager
                if not settings_manager.get_organization_name():
                    # إذا لم يكن اسم المؤسسة محفوظاً، اطلب من المستخدم إدخاله
                    from PyQt5.QtWidgets import QInputDialog
                    organization_name, ok = QInputDialog.getText(
                        None, 
                        "اسم المؤسسة", 
                        "يرجى إدخال اسم المؤسسة:",
                        text=""
                    )
                    
                    if ok and organization_name.strip():
                        settings_manager.set_organization_name(organization_name.strip())
                        logging.info(f"تم تحديث اسم المؤسسة: {organization_name.strip()}")
                    else:
                        self.show_error_dialog("خطأ", "يجب إدخال اسم المؤسسة للمتابعة")
                        return False
            
            # عرض نافذة تسجيل الدخول
            self.login_window = LoginWindow()
            
            if self.login_window.exec_() == self.login_window.Accepted:
                logging.info("تم تسجيل الدخول بنجاح")
                return True
            else:
                return False
                
        except Exception as e:
            logging.error(f"خطأ في مصادقة المستخدم: {e}")
            self.show_error_dialog("خطأ", f"حدث خطأ في تسجيل الدخول: {str(e)}")
            return False
    
    def run(self):
        """تشغيل التطبيق"""
        try:
            # إعداد التطبيق
            if not self.setup_application():
                self.show_error_dialog("خطأ", "فشل في إعداد التطبيق")
                return 1
            
            # إعداد قاعدة البيانات
            if not self.setup_database():
                self.show_error_dialog("خطأ", "فشل في إعداد قاعدة البيانات")
                return 1
            
            # مصادقة المستخدم
            if not self.authenticate_user():
                logging.info("تم إلغاء تسجيل الدخول")
                return 0
            
            # عرض النافذة الرئيسية
            self.main_window = MainWindow()
            self.main_window.show()
            
            logging.info("تم تشغيل التطبيق الرئيسي")
            
            # تشغيل حلقة التطبيق
            return self.app.exec_()
            
        except Exception as e:
            logging.critical(f"خطأ حرج في تشغيل التطبيق: {e}")
            if self.app:
                self.show_error_dialog("خطأ حرج", f"حدث خطأ حرج: {str(e)}")
            else:
                print(f"خطأ حرج: {e}")
            return 1
        
        finally:
            # تنظيف الموارد
            logging.info("إغلاق التطبيق")


def main():
    """الدالة الرئيسية"""
    try:
        # إنشاء وتشغيل التطبيق
        app = SchoolAccountingApp()
        exit_code = app.run()
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nتم إيقاف التطبيق بواسطة المستخدم")
        sys.exit(0)
        
    except Exception as e:
        print(f"خطأ في تشغيل التطبيق: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
