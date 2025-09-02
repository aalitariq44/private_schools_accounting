#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة تسجيل الدخول
"""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QMessageBox, QCheckBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon, QKeySequence

import config
from core.auth.login_manager import auth_manager
from core.utils.logger import auth_logger


class LoginWindow(QDialog):
    """نافذة تسجيل الدخول"""
    
    # إشارة تسجيل دخول ناجح
    login_successful = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.login_attempts = 0
        self.max_attempts = 3
        self.showing_error = False  # متغير لتتبع عرض رسالة الخطأ
        # اسم المستخدم الافتراضي
        self.username_input = QLineEdit()
        self.username_input.setText("admin")
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # إعداد النافذة (بدون setFixedSize لتجنب التشوه الأولي)
            self.setWindowTitle("تسجيل الدخول - حسابات المدارس الأهلية")
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
            title_label = QLabel("تسجيل الدخول")
            title_label.setObjectName("dialogTitle")
            title_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(title_label)

            info_label = QLabel("يرجى إدخال كلمة المرور للدخول إلى النظام.")
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

            # كلمة المرور
            pwd_label = QLabel("كلمة المرور:")
            pwd_label.setObjectName("fieldLabel")
            form_layout.addWidget(pwd_label)

            self.password_input = QLineEdit()
            self.password_input.setObjectName("passwordInput")
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_input.setPlaceholderText("أدخل كلمة المرور...")
            self.password_input.textChanged.connect(self.validate_inputs)
            form_layout.addWidget(self.password_input)

            # خيار إظهار كلمة المرور
            self.show_password_checkbox = QCheckBox("إظهار كلمة المرور")
            self.show_password_checkbox.setObjectName("showPasswordCheckbox")
            self.show_password_checkbox.toggled.connect(self.toggle_password_visibility)
            form_layout.addWidget(self.show_password_checkbox)

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

            self.login_button = QPushButton("تسجيل الدخول")
            self.login_button.setObjectName("loginButton")
            self.login_button.clicked.connect(self.login)
            self.login_button.setEnabled(False)
            buttons_layout.addWidget(self.login_button)

            main_layout.addLayout(buttons_layout)
            
            self.setLayout(main_layout)
            
            # تركيز على حقل كلمة المرور
            QTimer.singleShot(100, self.password_input.setFocus)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة تسجيل الدخول: {e}")
            raise
    
    def validate_inputs(self):
        """التحقق من صحة المدخلات"""
        try:
            password = self.password_input.text().strip()
            
            # إذا كانت هناك رسالة خطأ تُعرض، لا تغطيها لكن تحقق من الزر
            if self.showing_error:
                # فعل الزر إذا كان النص صحيحاً
                if password:
                    self.login_button.setEnabled(True)
                else:
                    self.login_button.setEnabled(False)
                return
            
            # تنظيف رسالة التحقق
            self.validation_label.clear()
            
            # التحقق من وجود كلمة المرور
            if not password:
                self.validation_label.setText("يرجى إدخال كلمة المرور")
                self.validation_label.setStyleSheet("color: #E74C3C;")
                self.login_button.setEnabled(False)
                return
            
            # كلمة المرور صحيحة
            self.validation_label.setText("جاهز للتسجيل ✓")
            self.validation_label.setStyleSheet("color: #27AE60;")
            self.login_button.setEnabled(True)
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من المدخلات: {e}")
            self.login_button.setEnabled(False)
    
    def toggle_password_visibility(self, checked):
        """تبديل إظهار/إخفاء كلمة المرور"""
        try:
            if checked:
                self.password_input.setEchoMode(QLineEdit.Normal)
            else:
                self.password_input.setEchoMode(QLineEdit.Password)
                
        except Exception as e:
            logging.error(f"خطأ في تبديل إظهار كلمة المرور: {e}")
    
    def login(self):
        """محاولة تسجيل الدخول"""
        try:
            username = self.username_input.text().strip()
            password = self.password_input.text().strip()
            
            # التحقق من وجود كلمة المرور
            if not password:
                self.show_error("يرجى إدخال كلمة المرور")
                return
            
            # محاولة المصادقة
            if auth_manager.authenticate(username, password):
                # تسجيل دخول ناجح
                self.login_successful.emit()
                self.accept()
            else:
                # تسجيل دخول فاشل
                self.login_attempts += 1
                
                if self.login_attempts >= self.max_attempts:
                    self.show_error(f"تم تجاوز عدد المحاولات المسموح ({self.max_attempts})")
                    auth_logger.log_security_event("تجاوز عدد محاولات تسجيل الدخول", username)
                    QTimer.singleShot(3000, self.reject)  # إغلاق النافذة بعد 3 ثواني
                else:
                    remaining = self.max_attempts - self.login_attempts
                    self.show_error(f"كلمة المرور خاطئة، يرجى إعادة كتابة كلمة المرور الصحيحة. المحاولات المتبقية: {remaining}")
                
                # تنظيف حقل كلمة المرور
                self.password_input.clear()
                self.password_input.setFocus()
                
        except Exception as e:
            logging.error(f"خطأ في تسجيل الدخول: {e}")
            self.show_error("حدث خطأ في تسجيل الدخول")
    
    def show_error(self, message: str):
        """عرض رسالة خطأ"""
        try:
            self.showing_error = True
            self.validation_label.setText(message)
            self.validation_label.setStyleSheet("color: #E74C3C;")
            self.login_button.setEnabled(False)
            
            # إخفاء الرسالة بعد 5 ثواني وإعادة التحقق من المدخلات
            QTimer.singleShot(5000, lambda: (
                self.validation_label.clear(),
                setattr(self, 'showing_error', False),
                self.validate_inputs()
            ))
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة الخطأ: {e}")
    
    def setup_styles(self):
        """إعداد تنسيقات النافذة"""
        try:
            style = """
                QDialog { background-color: #F5F7F8; font-family: 'Segoe UI', Tahoma; }
                #dialogTitle { font-size: 17px; font-weight: bold; color: #2C3E50; }
                #infoLabel { font-size: 13px; color: #555; margin-bottom: 4px; }
                #formFrame { background: #FFFFFF; border: 1px solid #D0D7DE; border-radius: 8px; }
                #fieldLabel { font-size: 14px; font-weight: 600; color: #2C3E50; }
                #passwordInput { padding: 8px 10px; border: 1px solid #C5CCD3; border-radius: 5px; font-size: 14px; background: #FFFFFF; }
                #passwordInput:focus { border: 1px solid #3498DB; }
                #showPasswordCheckbox { font-size: 13px; color: #555; }
                #validationLabel { font-size: 13px; font-weight: 600; margin-top: 4px; }
                QPushButton { border: none; padding: 10px 18px; border-radius: 6px; font-size: 14px; font-weight: 600; }
                #loginButton { background: #27AE60; color: #fff; }
                #loginButton:hover:!disabled { background: #229954; }
                #loginButton:disabled { background: #BFC8CE; color: #7F8C8D; }
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
                if self.login_button.isEnabled():
                    self.login()
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
