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
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # إعداد النافذة
            self.setWindowTitle("تسجيل الدخول - حسابات المدارس الأهلية")
            self.setMinimumSize(500, 400) # حجم قابل للتعديل بدلاً من ثابت
            self.setModal(True)
            self.setLayoutDirection(Qt.RightToLeft)
            
            # التخطيط الرئيسي
            main_layout = QVBoxLayout(self)
            main_layout.setSpacing(20)
            main_layout.setContentsMargins(40, 40, 40, 40)
            main_layout.setAlignment(Qt.AlignCenter)

            # عنوان النافذة
            title_label = QLabel("تسجيل الدخول")
            title_label.setObjectName("titleLabel")
            title_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(title_label)

            main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

            # نموذج تسجيل الدخول
            self.create_login_form(main_layout)
            
            main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

            # الأزرار
            self.create_buttons(main_layout)
            
            # تركيز على حقل كلمة المرور
            QTimer.singleShot(100, self.password_input.setFocus)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة تسجيل الدخول: {e}")
            raise
    
    def create_login_form(self, layout):
        """إنشاء نموذج تسجيل الدخول"""
        try:
            # إطار النموذج
            form_frame = QFrame()
            form_frame.setObjectName("formFrame")
            form_layout = QVBoxLayout(form_frame)
            form_layout.setSpacing(15)
            form_layout.setContentsMargins(25, 25, 25, 25)
            
            # اسم المستخدم (مخفي لأن هناك مستخدم واحد فقط)
            self.username_input = QLineEdit()
            self.username_input.setText("admin")  # المستخدم الافتراضي
            self.username_input.setVisible(False)  # مخفي
            
            # تسمية كلمة المرور
            password_label = QLabel("كلمة المرور:")
            password_label.setObjectName("fieldLabel")
            form_layout.addWidget(password_label)
            
            # حقل كلمة المرور
            self.password_input = QLineEdit()
            self.password_input.setObjectName("passwordInput")
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_input.setPlaceholderText("أدخل كلمة المرور...")
            # تعيين كلمة المرور الافتراضية للتطوير فقط
            if config.DEBUG_MODE:
                self.password_input.setText("123456")
            self.password_input.returnPressed.connect(self.login)
            form_layout.addWidget(self.password_input)
            
            # خيار إظهار كلمة المرور
            self.show_password_checkbox = QCheckBox("إظهار كلمة المرور")
            self.show_password_checkbox.setObjectName("showPasswordCheckbox")
            self.show_password_checkbox.toggled.connect(self.toggle_password_visibility)
            form_layout.addWidget(self.show_password_checkbox)
            
            # رسالة الخطأ
            self.error_label = QLabel()
            self.error_label.setObjectName("errorLabel")
            self.error_label.setAlignment(Qt.AlignCenter)
            self.error_label.setWordWrap(True)
            self.error_label.hide()
            form_layout.addWidget(self.error_label)
            
            layout.addWidget(form_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء نموذج تسجيل الدخول: {e}")
            raise
    
    def create_buttons(self, layout):
        """إنشاء الأزرار"""
        try:
            # حاوي الأزرار
            buttons_container = QFrame()
            buttons_layout = QHBoxLayout(buttons_container)
            buttons_layout.setSpacing(15)
            buttons_layout.setContentsMargins(0, 0, 0, 0)
            
            # زر الإلغاء
            self.cancel_button = QPushButton("إلغاء")
            self.cancel_button.setObjectName("cancelButton")
            self.cancel_button.clicked.connect(self.reject)
            buttons_layout.addWidget(self.cancel_button)
            
            # زر تسجيل الدخول
            self.login_button = QPushButton("تسجيل الدخول")
            self.login_button.setObjectName("loginButton")
            self.login_button.clicked.connect(self.login)
            self.login_button.setDefault(True)
            buttons_layout.addWidget(self.login_button)
            
            layout.addWidget(buttons_container)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الأزرار: {e}")
            raise
    
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
                    self.show_error(f"كلمة مرور خاطئة. المحاولات المتبقية: {remaining}")
                
                # تنظيف حقل كلمة المرور
                self.password_input.clear()
                self.password_input.setFocus()
                
        except Exception as e:
            logging.error(f"خطأ في تسجيل الدخول: {e}")
            self.show_error("حدث خطأ في تسجيل الدخول")
    
    def show_error(self, message: str):
        """عرض رسالة خطأ"""
        try:
            self.error_label.setText(message)
            self.error_label.show()
            
            # إخفاء الرسالة بعد 5 ثواني
            QTimer.singleShot(5000, self.error_label.hide)
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة الخطأ: {e}")
    
    def setup_styles(self):
        """إعداد تنسيقات النافذة"""
        try:
            font_size = "18px"
            style = f"""
                QDialog {{
                    background-color: #ECF0F1;
                    font-family: 'Segoe UI', Tahoma, Arial;
                }}
                
                #titleLabel {{
                    font-size: 18px; /* حجم أكبر للعنوان الرئيسي */
                    font-weight: bold;
                    color: #2C3E50;
                    margin-bottom: 20px;
                }}
                
                #formFrame {{
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                    border: 1px solid #BDC3C7;
                }}
                
                #fieldLabel {{
                    font-size: {font_size};
                    font-weight: bold;
                    color: #2C3E50;
                    margin-bottom: 5px;
                }}
                
                #passwordInput {{
                    padding: 12px;
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    font-size: {font_size};
                    background-color: white;
                    min-width: 300px;
                }}
                
                #passwordInput:focus {{
                    border-color: #3498DB;
                    outline: none;
                }}
                
                #showPasswordCheckbox {{
                    font-size: 18px; /* حجم أصغر قليلاً لخانة الاختيار */
                    color: #7F8C8D;
                    margin-top: 10px;
                }}
                
                #errorLabel {{
                    color: #E74C3C;
                    font-size: 18px; /* حجم أصغر لرسالة الخطأ */
                    font-weight: bold;
                    margin-top: 10px;
                    padding: 8px;
                    background-color: #FADBD8;
                    border: 1px solid #E74C3C;
                    border-radius: 4px;
                }}
                
                QPushButton {{
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-size: {font_size};
                    font-weight: bold;
                    min-width: 140px;
                }}

                #loginButton {{
                    background-color: #3498DB;
                    color: white;
                }}
                
                #loginButton:hover {{
                    background-color: #2980B9;
                }}
                
                #loginButton:pressed {{
                    background-color: #21618C;
                }}
                
                #cancelButton {{
                    background-color: #95A5A6;
                    color: white;
                }}
                
                #cancelButton:hover {{
                    background-color: #7F8C8D;
                }}
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد التنسيقات: {e}")
    
    def keyPressEvent(self, event):
        """معالجة ضغط المفاتيح"""
        try:
            if event.key() == Qt.Key_Escape:
                self.reject()
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.login()
            else:
                super().keyPressEvent(event)
                
        except Exception as e:
            logging.error(f"خطأ في معالجة ضغط المفاتيح: {e}")
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """معالجة إغلاق النافذة"""
        try:
            auth_logger.log_security_event("تم إلغاء تسجيل الدخول")
            event.accept()
            
        except Exception as e:
            logging.error(f"خطأ في إغلاق نافذة تسجيل الدخول: {e}")
            event.accept()
