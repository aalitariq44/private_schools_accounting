#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إعداد كلمة المرور الأولى
"""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon

import config
from core.utils.logger import auth_logger


class FirstSetupDialog(QDialog):
    """نافذة إعداد كلمة المرور الأولى"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.password = None
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # إعداد النافذة
            self.setWindowTitle("إعداد أولي - حسابات المدارس الأهلية")
            self.setFixedSize(450, 350)
            self.setModal(True)
            self.setLayoutDirection(Qt.RightToLeft)
            
            # تعطيل زر الإغلاق
            self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
            
            # التخطيط الرئيسي
            main_layout = QVBoxLayout()
            main_layout.setSpacing(20)
            main_layout.setContentsMargins(30, 30, 30, 30)
            
            # عنوان الترحيب
            self.create_header(main_layout)
            
            # قسم إدخال كلمة المرور
            self.create_password_section(main_layout)
            
            # الأزرار
            self.create_buttons(main_layout)
            
            self.setLayout(main_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة الإعداد الأولي: {e}")
            raise
    
    def create_header(self, layout):
        """إنشاء رأس النافذة"""
        try:
            # إطار الرأس
            header_frame = QFrame()
            header_frame.setObjectName("headerFrame")
            header_layout = QVBoxLayout(header_frame)
            header_layout.setAlignment(Qt.AlignCenter)
            
            # أيقونة التطبيق (إذا توفرت)
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFixedSize(80, 80)
            icon_label.setStyleSheet("""
                QLabel {
                    background-color: #3498DB;
                    border-radius: 40px;
                    border: 3px solid #2C3E50;
                }
            """)
            header_layout.addWidget(icon_label)
            
            # عنوان الترحيب
            welcome_label = QLabel("مرحباً بك!")
            welcome_label.setObjectName("welcomeLabel")
            welcome_label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(welcome_label)
            
            # نص توضيحي
            info_label = QLabel("يرجى إعداد كلمة مرور للدخول إلى النظام")
            info_label.setObjectName("infoLabel")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setWordWrap(True)
            header_layout.addWidget(info_label)
            
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء رأس النافذة: {e}")
            raise
    
    def create_password_section(self, layout):
        """إنشاء قسم إدخال كلمة المرور"""
        try:
            # إطار كلمة المرور
            password_frame = QFrame()
            password_frame.setObjectName("passwordFrame")
            password_layout = QVBoxLayout(password_frame)
            password_layout.setSpacing(15)
            
            # كلمة المرور الأولى
            password1_label = QLabel("كلمة المرور:")
            password1_label.setObjectName("fieldLabel")
            password_layout.addWidget(password1_label)
            
            self.password1_input = QLineEdit()
            self.password1_input.setObjectName("passwordInput")
            self.password1_input.setEchoMode(QLineEdit.Password)
            self.password1_input.setPlaceholderText("أدخل كلمة المرور...")
            self.password1_input.textChanged.connect(self.validate_inputs)
            password_layout.addWidget(self.password1_input)
            
            # تأكيد كلمة المرور
            password2_label = QLabel("تأكيد كلمة المرور:")
            password2_label.setObjectName("fieldLabel")
            password_layout.addWidget(password2_label)
            
            self.password2_input = QLineEdit()
            self.password2_input.setObjectName("passwordInput")
            self.password2_input.setEchoMode(QLineEdit.Password)
            self.password2_input.setPlaceholderText("أعد كتابة كلمة المرور...")
            self.password2_input.textChanged.connect(self.validate_inputs)
            password_layout.addWidget(self.password2_input)
            
            # رسالة التحقق
            self.validation_label = QLabel()
            self.validation_label.setObjectName("validationLabel")
            self.validation_label.setAlignment(Qt.AlignCenter)
            self.validation_label.setWordWrap(True)
            password_layout.addWidget(self.validation_label)
            
            layout.addWidget(password_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم كلمة المرور: {e}")
            raise
    
    def create_buttons(self, layout):
        """إنشاء الأزرار"""
        try:
            # إطار الأزرار
            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(15)
            
            # زر الإلغاء
            self.cancel_button = QPushButton("إلغاء")
            self.cancel_button.setObjectName("cancelButton")
            self.cancel_button.clicked.connect(self.reject)
            buttons_layout.addWidget(self.cancel_button)
            
            # زر الحفظ
            self.save_button = QPushButton("حفظ وإنشاء الحساب")
            self.save_button.setObjectName("saveButton")
            self.save_button.clicked.connect(self.save_password)
            self.save_button.setEnabled(False)
            buttons_layout.addWidget(self.save_button)
            
            layout.addLayout(buttons_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الأزرار: {e}")
            raise
    
    def validate_inputs(self):
        """التحقق من صحة المدخلات"""
        try:
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
        """حفظ كلمة المرور"""
        try:
            password = self.password1_input.text().strip()
            
            if len(password) < config.PASSWORD_MIN_LENGTH:
                self.show_error("كلمة المرور قصيرة جداً")
                return
            
            if password != self.password2_input.text().strip():
                self.show_error("كلمتا المرور غير متطابقتين")
                return
            
            self.password = password
            auth_logger.log_security_event("تم إعداد كلمة المرور الأولى")
            self.accept()
            
        except Exception as e:
            logging.error(f"خطأ في حفظ كلمة المرور: {e}")
            self.show_error("حدث خطأ في حفظ كلمة المرور")
    
    def get_password(self) -> str:
        """الحصول على كلمة المرور"""
        return self.password
    
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
                QDialog {
                    background-color: #ECF0F1;
                    font-family: 'Segoe UI', Tahoma, Arial;
                }
                
                #headerFrame {
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                    border: 1px solid #BDC3C7;
                }
                
                #welcomeLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin: 10px 0;
                }
                
                #infoLabel {
                    font-size: 18px;
                    color: #7F8C8D;
                    margin-bottom: 10px;
                }
                
                #passwordFrame {
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                    border: 1px solid #BDC3C7;
                }
                
                #fieldLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin-bottom: 5px;
                }
                
                #passwordInput {
                    padding: 12px;
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    font-size: 18px;
                    background-color: white;
                }
                
                #passwordInput:focus {
                    border-color: #3498DB;
                    outline: none;
                }
                
                #validationLabel {
                    font-size: 18px;
                    font-weight: bold;
                    margin-top: 5px;
                }
                
                #saveButton {
                    background-color: #27AE60;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-size: 18px;
                    font-weight: bold;
                    min-width: 150px;
                }
                
                #saveButton:hover {
                    background-color: #229954;
                }
                
                #saveButton:disabled {
                    background-color: #BDC3C7;
                    color: #7F8C8D;
                }
                
                #cancelButton {
                    background-color: #E74C3C;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-size: 18px;
                    font-weight: bold;
                    min-width: 100px;
                }
                
                #cancelButton:hover {
                    background-color: #C0392B;
                }
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
