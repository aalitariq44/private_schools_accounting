#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إعداد كلمة المرور الأولى
"""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

import config
from core.utils.logger import auth_logger


class FirstSetupDialog(QDialog):
    """نافذة إعداد كلمة المرور الأولى"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # المتغيرات الداخلية
        self.password = None
        self._existing_org_folders = None  # سيتم جلبها مرة واحدة من Supabase
        self._org_check_in_progress = False
        # بناء الواجهة
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # إعداد النافذة (بدون setFixedSize لتجنب التشوه الأولي)
            self.setWindowTitle("الإعداد الأولي - حسابات المدارس الأهلية")
            self.setMinimumWidth(420)
            self.setModal(True)
            self.setLayoutDirection(Qt.RightToLeft)
            
            # تعطيل زر الإغلاق
            self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
            
            # التخطيط الرئيسي
            main_layout = QVBoxLayout()
            main_layout.setSpacing(15)
            main_layout.setContentsMargins(24, 24, 24, 24)

            # عنوان بسيط
            title_label = QLabel("مرحباً بك! إعداد أول كلمة مرور")
            title_label.setObjectName("dialogTitle")
            title_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(title_label)

            info_label = QLabel("يرجى إدخال كلمة المرور (اسم المؤسسة ثابت: Trial Version).")
            info_label.setObjectName("infoLabel")
            info_label.setWordWrap(True)
            info_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(info_label)

            # إطار الحقول
            form_frame = QFrame()
            form_frame.setObjectName("formFrame")
            form_layout = QVBoxLayout(form_frame)
            form_layout.setSpacing(10)
            form_layout.setContentsMargins(18, 18, 18, 18)

            # اسم المؤسسة
            org_label = QLabel("اسم المؤسسة:")
            org_label.setObjectName("fieldLabel")
            form_layout.addWidget(org_label)

            self.organization_input = QLabel("Trial Version")
            self.organization_input.setObjectName("organizationInput")
            self.organization_input.setStyleSheet("""
                QLabel#organizationInput {
                    padding: 8px 10px;
                    border: 1px solid #C5CCD3;
                    border-radius: 5px;
                    font-size: 14px;
                    background: #F8F9FA;
                    color: #6C757D;
                    font-weight: bold;
                }
            """)
            form_layout.addWidget(self.organization_input)

            # كلمة المرور
            pwd1_label = QLabel("كلمة المرور:")
            pwd1_label.setObjectName("fieldLabel")
            form_layout.addWidget(pwd1_label)

            self.password1_input = QLineEdit()
            self.password1_input.setObjectName("passwordInput")
            self.password1_input.setEchoMode(QLineEdit.Password)
            self.password1_input.setPlaceholderText("أدخل كلمة المرور...")
            self.password1_input.textChanged.connect(self.validate_inputs)
            form_layout.addWidget(self.password1_input)

            # تأكيد كلمة المرور
            pwd2_label = QLabel("تأكيد كلمة المرور:")
            pwd2_label.setObjectName("fieldLabel")
            form_layout.addWidget(pwd2_label)

            self.password2_input = QLineEdit()
            self.password2_input.setObjectName("passwordInput")
            self.password2_input.setEchoMode(QLineEdit.Password)
            self.password2_input.setPlaceholderText("أعد كتابة كلمة المرور...")
            self.password2_input.textChanged.connect(self.validate_inputs)
            form_layout.addWidget(self.password2_input)

            # رسالة التحقق
            self.validation_label = QLabel()
            self.validation_label.setObjectName("validationLabel")
            self.validation_label.setAlignment(Qt.AlignCenter)
            self.validation_label.setWordWrap(True)
            form_layout.addWidget(self.validation_label)

            main_layout.addWidget(form_frame)

            # الأزرار
            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(12)

            self.cancel_button = QPushButton("إلغاء")
            self.cancel_button.setObjectName("cancelButton")
            self.cancel_button.clicked.connect(self.reject)
            buttons_layout.addWidget(self.cancel_button)

            self.save_button = QPushButton("حفظ وإنشاء الحساب")
            self.save_button.setObjectName("saveButton")
            self.save_button.clicked.connect(self.save_password)
            self.save_button.setEnabled(False)
            buttons_layout.addWidget(self.save_button)

            main_layout.addLayout(buttons_layout)
            
            self.setLayout(main_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة الإعداد الأولي: {e}")
            raise
    
    # تم الاستغناء عن create_header و create_password_section و create_buttons في التصميم المبسط
    
    # الدوال القديمة create_password_section و create_buttons أزيلت في النسخة المبسطة للحفاظ على بساطة الكود

    def _sanitize_folder_name(self, name: str) -> str:
        """تحويل اسم المؤسسة إلى اسم مجلد آمن كما في مدير النسخ"""
        import re
        if not name:
            return "organization"
        safe = re.sub(r'[<>:"/\\|?*]', '', name)
        return safe.strip().replace(' ', '_')

    def _load_existing_org_folders(self):
        """جلب أسماء المجلدات (المؤسسات) الموجودة في البكت (يجلب مرة واحدة)."""
        if self._existing_org_folders is not None or self._org_check_in_progress:
            return
        self._org_check_in_progress = True
        try:
            try:
                from supabase import create_client  # type: ignore
            except ImportError:
                self._existing_org_folders = set()
                return
            import config
            supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            # سرد المجلدات داخل backups
            items = supabase.storage.from_(config.SUPABASE_BUCKET).list("backups")
            folders = set()
            if items:
                for it in items:
                    if isinstance(it, dict):
                        name = it.get('name')
                        if name:
                            folders.add(name)
            self._existing_org_folders = folders
        except Exception as e:
            logging.warning(f"تعذر جلب قائمة المؤسسات من Supabase: {e}")
            self._existing_org_folders = set()
        finally:
            self._org_check_in_progress = False
    
    def validate_inputs(self):
        """التحقق من صحة المدخلات"""
        try:
            # اسم المؤسسة ثابت
            organization_name = "Trial Version"
            password1 = self.password1_input.text().strip()
            password2 = self.password2_input.text().strip()
            
            # تنظيف رسالة التحقق
            self.validation_label.clear()
            
            # التحقق من وجود كلمتي المرور
            if not password1 or not password2:
                self.save_button.setEnabled(False)
                return
            
            # التحقق من الطول الأدنى
            if len(password1) < config.PASSWORD_MIN_LENGTH:
                self.validation_label.setText(f"كلمة المرور قصيرة جداً (الحد الأدنى {config.PASSWORD_MIN_LENGTH} أحرف)")
                self.validation_label.setStyleSheet("color: #E74C3C;")
                self.save_button.setEnabled(False)
                return
            
            # التحقق من التطابق
            if password1 != password2:
                self.validation_label.setText("كلمتا المرور غير متطابقتين")
                self.validation_label.setStyleSheet("color: #E74C3C;")
                self.save_button.setEnabled(False)
                return
            
            # كلمة المرور صحيحة
            self.validation_label.setText("كلمة المرور صحيحة ✓")
            self.validation_label.setStyleSheet("color: #27AE60;")
            self.save_button.setEnabled(True)
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من المدخلات: {e}")
            self.save_button.setEnabled(False)
    
    def save_password(self):
        """حفظ كلمة المرور واسم المؤسسة"""
        try:
            # اسم المؤسسة ثابت
            organization_name = "Trial Version"
            password = self.password1_input.text().strip()
            
            # التحقق من كلمة المرور
            if len(password) < config.PASSWORD_MIN_LENGTH:
                self.show_error("كلمة المرور قصيرة جداً")
                return
            
            if password != self.password2_input.text().strip():
                self.show_error("كلمتا المرور غير متطابقتين")
                return
            
            # حفظ اسم المؤسسة في الإعدادات
            try:
                from core.utils.settings_manager import settings_manager
                settings_manager.set_setting('organization_name', organization_name)
                logging.info(f"تم حفظ اسم المؤسسة: {organization_name}")
            except Exception as e:
                logging.error(f"خطأ في حفظ اسم المؤسسة: {e}")
                self.show_error("فشل في حفظ اسم المؤسسة")
                return
            
            self.password = password
            self.organization_name = organization_name
            auth_logger.log_security_event("تم إعداد كلمة المرور الأولى واسم المؤسسة")
            self.accept()
            
        except Exception as e:
            logging.error(f"خطأ في حفظ كلمة المرور: {e}")
            self.show_error("حدث خطأ في حفظ كلمة المرور")
    
    def get_password(self) -> str:
        """الحصول على كلمة المرور"""
        return self.password
    
    def get_organization_name(self) -> str:
        """الحصول على اسم المؤسسة"""
        return "Trial Version"
    
    def show_error(self, message: str):
        """عرض رسالة خطأ"""
        try:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("تحذير")
            msg.setText(message)
            msg.setLayoutDirection(Qt.RightToLeft)
            msg.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة التحذير: {e}")
    
    def setup_styles(self):
        """إعداد تنسيقات النافذة"""
        try:
            style = """
                QDialog { background-color: #F5F7F8; font-family: 'Segoe UI', Tahoma; }
                #dialogTitle { font-size: 17px; font-weight: bold; color: #2C3E50; }
                #infoLabel { font-size: 13px; color: #555; margin-bottom: 4px; }
                #formFrame { background: #FFFFFF; border: 1px solid #D0D7DE; border-radius: 8px; }
                #fieldLabel { font-size: 14px; font-weight: 600; color: #2C3E50; }
                #passwordInput, #organizationInput { padding: 8px 10px; border: 1px solid #C5CCD3; border-radius: 5px; font-size: 14px; background: #FFFFFF; }
                #passwordInput:focus, #organizationInput:focus { border: 1px solid #3498DB; }
                #validationLabel { font-size: 13px; font-weight: 600; margin-top: 4px; }
                QPushButton { border: none; padding: 10px 18px; border-radius: 6px; font-size: 14px; font-weight: 600; }
                #saveButton { background: #27AE60; color: #fff; }
                #saveButton:hover:!disabled { background: #229954; }
                #saveButton:disabled { background: #BFC8CE; color: #7F8C8D; }
                #cancelButton { background: #E74C3C; color: #fff; }
                #cancelButton:hover { background: #C0392B; }
            """
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد التنسيقات: {e}")
    
    def keyPressEvent(self, event):
        """معالجة ضغط المفاتيح"""
        try:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                if self.save_button.isEnabled():
                    self.save_password()
            else:
                super().keyPressEvent(event)
                
        except Exception as e:
            logging.error(f"خطأ في معالجة ضغط المفاتيح: {e}")
            super().keyPressEvent(event)

    def showEvent(self, event):  # إصلاح مشكلة ظهور غير مكتمل حتى يتم تحريك النافذة
        try:
            super().showEvent(event)
            QTimer.singleShot(0, self._finalize_geometry)
        except Exception as e:
            logging.error(f"خطأ في showEvent: {e}")
            super().showEvent(event)

    def _finalize_geometry(self):
        """ضبط الحجم النهائي بعد العرض لمنع التشوه الأولي"""
        try:
            self.adjustSize()
            # تثبيت الحجم الحالي بعد الحساب لضمان ثبات الشكل
            self.setFixedSize(self.size())
        except Exception as e:
            logging.error(f"خطأ في _finalize_geometry: {e}")
