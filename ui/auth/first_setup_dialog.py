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
            self.setWindowTitle("الإعداد الأولي - كلمة المرور")
            # سنضبط الحجم النهائي بعد تهيئة كل شيء لتفادي التشوه عند الظهور الأول
            self.setMinimumSize(360, 260)
            self.setModal(True)
            self.setLayoutDirection(Qt.RightToLeft)
            
            # تعطيل زر الإغلاق
            self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
            
            # التخطيط الرئيسي
            main_layout = QVBoxLayout()
            main_layout.setSpacing(15)
            main_layout.setContentsMargins(20, 20, 20, 20)
            
            # قسم الواجهة (مبسطة)
            self.create_simple_header(main_layout)
            self.create_password_section(main_layout)
            
            # الأزرار
            self.create_buttons(main_layout)
            
            self.setLayout(main_layout)

            # ضبط الحجم بعد دورة الحدث الأولى لضمان حساب sizeHint بعد تلميع الأنماط
            QTimer.singleShot(0, self.finalize_size)
            
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

    def create_simple_header(self, layout):
        """إنشاء رأس مبسط"""
        try:
            header_frame = QFrame()
            header_frame.setObjectName("headerFrame")
            header_layout = QVBoxLayout(header_frame)
            header_layout.setAlignment(Qt.AlignCenter)

            title = QLabel("الإعداد الأولي")
            title.setObjectName("welcomeLabel")
            title.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(title)

            info = QLabel("قم بتعيين كلمة مرور للدخول إلى النظام")
            info.setObjectName("infoLabel")
            info.setAlignment(Qt.AlignCenter)
            info.setWordWrap(True)
            header_layout.addWidget(info)

            layout.addWidget(header_frame)
        except Exception as e:
            logging.error(f"خطأ في إنشاء الرأس المبسط: {e}")
            raise
    
    def create_password_section(self, layout):
        """إنشاء قسم إدخال كلمة المرور"""
        try:
            # إطار كلمة المرور
            password_frame = QFrame()
            password_frame.setObjectName("passwordFrame")
            password_layout = QVBoxLayout(password_frame)
            password_layout.setSpacing(15)
            
            # اسم المؤسسة (ثابت - نسخة تجريبية)
            org_row = QHBoxLayout()
            org_label_title = QLabel("اسم المؤسسة:")
            org_label_title.setObjectName("fieldLabel")
            org_row.addWidget(org_label_title)
            self.organization_input = QLineEdit("Trial version")
            self.organization_input.setObjectName("organizationInput")
            self.organization_input.setReadOnly(True)
            self.organization_input.setEnabled(False)
            self.organization_input.setToolTip("لا يمكن تعديل اسم المؤسسة في النسخة التجريبية")
            org_row.addWidget(self.organization_input)
            password_layout.addLayout(org_row)
            
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
            # اسم المؤسسة ثابت في النسخة التجريبية
            organization_name = "Trial version"
            password1 = self.password1_input.text().strip()
            password2 = self.password2_input.text().strip()
            
            # تنظيف رسالة التحقق
            self.validation_label.clear()
            
            # (لا حاجة للتحقق من اسم المؤسسة لأنه ثابت)
            
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
            organization_name = "Trial version"
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
        return getattr(self, 'organization_name', '')
    
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
                    background-color: #F7F9FA;
                    font-family: 'Segoe UI', Tahoma, Arial;
                }
                
                #headerFrame {
                    background-color: transparent;
                    padding: 5px;
                }
                
                #welcomeLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #1F2D3A;
                    margin: 4px 0;
                }
                
                #infoLabel {
                    font-size: 13px;
                    color: #5E6B74;
                    margin-bottom: 4px;
                }
                
                #passwordFrame {
                    background-color: #FFFFFF;
                    border-radius: 8px;
                    padding: 15px;
                    border: 1px solid #D9E1E6;
                }
                
                #fieldLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #1F2D3A;
                    margin-bottom: 2px;
                }
                
                #passwordInput {
                    padding: 8px;
                    border: 1px solid #C3CDD4;
                    border-radius: 5px;
                    font-size: 14px;
                    background-color: white;
                }
                
                #organizationInput {
                    padding: 6px;
                    border: 1px solid #E0E6EA;
                    border-radius: 4px;
                    font-size: 13px;
                    background-color: #F0F3F5;
                    color: #56616A;
                }
                
                #passwordInput:focus, #organizationInput:focus {
                    border-color: #2D8CFF;
                    outline: none;
                }
                
                #validationLabel {
                    font-size: 13px;
                    font-weight: bold;
                    margin-top: 4px;
                }
                
                #saveButton {
                    background-color: #28A745;
                    color: white;
                    border: none;
                    padding: 10px 18px;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 120px;
                }
                
                #saveButton:hover {
                    background-color: #218838;
                }
                
                #saveButton:disabled {
                    background-color: #DEE2E6;
                    color: #8A959C;
                }
                
                #cancelButton {
                    background-color: #DC3545;
                    color: white;
                    border: none;
                    padding: 10px 18px;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 100px;
                }
                
                #cancelButton:hover {
                    background-color: #C82333;
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

    def finalize_size(self):
        """ضبط الحجم النهائي بعد اكتمال بناء الواجهة لمنع الوميض/التشوه"""
        try:
            self.adjustSize()
            # تثبيت الحجم حسب التلميح النهائي فقط (يمكنك إزالة التثبيت إذا رغبت بالسماح بالتكبير)
            self.setFixedSize(self.sizeHint())
        except Exception as e:
            logging.error(f"خطأ في finalize_size: {e}")
