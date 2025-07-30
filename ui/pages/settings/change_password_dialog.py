#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
حوار تغيير كلمة المرور
"""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QLabel, QPushButton, QLineEdit, 
    QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from core.auth.login_manager import auth_manager
from core.utils.logger import log_user_action
import config


class ChangePasswordDialog(QDialog):
    """حوار تغيير كلمة المرور"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            self.setWindowTitle("تغيير كلمة المرور")
            self.setModal(True)
            self.setFixedSize(400, 350)
            self.setLayoutDirection(Qt.RightToLeft)
            
            # التخطيط الرئيسي
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(20)
            
            # العنوان
            self.create_header(main_layout)
            
            # نموذج تغيير كلمة المرور
            self.create_password_form(main_layout)
            
            # الأزرار
            self.create_buttons(main_layout)
            
            self.setLayout(main_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد حوار تغيير كلمة المرور: {e}")
    
    def create_header(self, layout):
        """إنشاء رأس الحوار"""
        try:
            header_frame = QFrame()
            header_frame.setObjectName("headerFrame")
            header_layout = QVBoxLayout()
            
            # العنوان
            title_label = QLabel("تغيير كلمة المرور")
            title_label.setObjectName("dialogTitle")
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title_label.setFont(title_font)
            title_label.setAlignment(Qt.AlignCenter)
            
            # الوصف
            desc_label = QLabel("يرجى إدخال كلمة المرور الحالية والجديدة")
            desc_label.setObjectName("dialogDescription")
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setWordWrap(True)
            
            header_layout.addWidget(title_label)
            header_layout.addWidget(desc_label)
            
            header_frame.setLayout(header_layout)
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء رأس الحوار: {e}")
    
    def create_password_form(self, layout):
        """إنشاء نموذج تغيير كلمة المرور"""
        try:
            form_frame = QFrame()
            form_frame.setObjectName("formFrame")
            form_layout = QGridLayout()
            form_layout.setSpacing(15)
            
            # كلمة المرور الحالية
            current_label = QLabel("كلمة المرور الحالية:")
            current_label.setFont(QFont("Arial", 10))
            
            self.current_password_edit = QLineEdit()
            self.current_password_edit.setEchoMode(QLineEdit.Password)
            self.current_password_edit.setMinimumHeight(35)
            self.current_password_edit.setPlaceholderText("أدخل كلمة المرور الحالية")
            
            # كلمة المرور الجديدة
            new_label = QLabel("كلمة المرور الجديدة:")
            new_label.setFont(QFont("Arial", 10))
            
            self.new_password_edit = QLineEdit()
            self.new_password_edit.setEchoMode(QLineEdit.Password)
            self.new_password_edit.setMinimumHeight(35)
            self.new_password_edit.setPlaceholderText("أدخل كلمة المرور الجديدة")
            
            # تأكيد كلمة المرور الجديدة
            confirm_label = QLabel("تأكيد كلمة المرور:")
            confirm_label.setFont(QFont("Arial", 10))
            
            self.confirm_password_edit = QLineEdit()
            self.confirm_password_edit.setEchoMode(QLineEdit.Password)
            self.confirm_password_edit.setMinimumHeight(35)
            self.confirm_password_edit.setPlaceholderText("أعد إدخال كلمة المرور الجديدة")
            
            # خيار إظهار كلمات المرور
            self.show_passwords_check = QCheckBox("إظهار كلمات المرور")
            self.show_passwords_check.stateChanged.connect(self.toggle_password_visibility)
            
            # معلومات متطلبات كلمة المرور
            requirements_label = QLabel(f"يجب أن تكون كلمة المرور {config.PASSWORD_MIN_LENGTH} أحرف على الأقل")
            requirements_label.setObjectName("requirementsLabel")
            requirements_label.setWordWrap(True)
            
            # إضافة العناصر للتخطيط
            form_layout.addWidget(current_label, 0, 0)
            form_layout.addWidget(self.current_password_edit, 0, 1)
            
            form_layout.addWidget(new_label, 1, 0)
            form_layout.addWidget(self.new_password_edit, 1, 1)
            
            form_layout.addWidget(confirm_label, 2, 0)
            form_layout.addWidget(self.confirm_password_edit, 2, 1)
            
            form_layout.addWidget(self.show_passwords_check, 3, 1)
            form_layout.addWidget(requirements_label, 4, 0, 1, 2)
            
            form_frame.setLayout(form_layout)
            layout.addWidget(form_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء نموذج كلمة المرور: {e}")
    
    def create_buttons(self, layout):
        """إنشاء أزرار الحوار"""
        try:
            buttons_frame = QFrame()
            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(10)
            
            # زر الإلغاء
            cancel_btn = QPushButton("إلغاء")
            cancel_btn.setObjectName("cancelButton")
            cancel_btn.setMinimumHeight(40)
            cancel_btn.setMinimumWidth(100)
            cancel_btn.clicked.connect(self.reject)
            
            # زر الحفظ
            save_btn = QPushButton("حفظ")
            save_btn.setObjectName("saveButton")
            save_btn.setMinimumHeight(40)
            save_btn.setMinimumWidth(100)
            save_btn.clicked.connect(self.save_password)
            save_btn.setDefault(True)
            
            buttons_layout.addStretch()
            buttons_layout.addWidget(cancel_btn)
            buttons_layout.addWidget(save_btn)
            
            buttons_frame.setLayout(buttons_layout)
            layout.addWidget(buttons_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء أزرار الحوار: {e}")
    
    def toggle_password_visibility(self, state):
        """تبديل إظهار/إخفاء كلمات المرور"""
        try:
            if state == Qt.Checked:
                echo_mode = QLineEdit.Normal
            else:
                echo_mode = QLineEdit.Password
            
            self.current_password_edit.setEchoMode(echo_mode)
            self.new_password_edit.setEchoMode(echo_mode)
            self.confirm_password_edit.setEchoMode(echo_mode)
            
        except Exception as e:
            logging.error(f"خطأ في تبديل إظهار كلمات المرور: {e}")
    
    def validate_passwords(self):
        """التحقق من صحة كلمات المرور"""
        try:
            current_password = self.current_password_edit.text().strip()
            new_password = self.new_password_edit.text().strip()
            confirm_password = self.confirm_password_edit.text().strip()
            
            # التحقق من وجود كلمة المرور الحالية
            if not current_password:
                QMessageBox.warning(self, "تحذير", "يرجى إدخال كلمة المرور الحالية")
                self.current_password_edit.setFocus()
                return False
            
            # التحقق من وجود كلمة المرور الجديدة
            if not new_password:
                QMessageBox.warning(self, "تحذير", "يرجى إدخال كلمة المرور الجديدة")
                self.new_password_edit.setFocus()
                return False
            
            # التحقق من طول كلمة المرور الجديدة
            if len(new_password) < config.PASSWORD_MIN_LENGTH:
                QMessageBox.warning(
                    self, 
                    "تحذير", 
                    f"يجب أن تكون كلمة المرور الجديدة {config.PASSWORD_MIN_LENGTH} أحرف على الأقل"
                )
                self.new_password_edit.setFocus()
                return False
            
            # التحقق من تطابق كلمة المرور الجديدة مع التأكيد
            if new_password != confirm_password:
                QMessageBox.warning(self, "تحذير", "كلمة المرور الجديدة غير متطابقة مع التأكيد")
                self.confirm_password_edit.setFocus()
                return False
            
            # التحقق من أن كلمة المرور الجديدة مختلفة عن الحالية
            if current_password == new_password:
                QMessageBox.warning(self, "تحذير", "كلمة المرور الجديدة يجب أن تكون مختلفة عن الحالية")
                self.new_password_edit.setFocus()
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من كلمات المرور: {e}")
            return False
    
    def save_password(self):
        """حفظ كلمة المرور الجديدة"""
        try:
            # التحقق من صحة البيانات
            if not self.validate_passwords():
                return
            
            current_password = self.current_password_edit.text().strip()
            new_password = self.new_password_edit.text().strip()
            
            # تغيير كلمة المرور
            if auth_manager.change_password(current_password, new_password):
                log_user_action("تم تغيير كلمة المرور بنجاح")
                self.accept()
            else:
                QMessageBox.critical(self, "خطأ", "كلمة المرور الحالية غير صحيحة أو فشل في تغيير كلمة المرور")
            
        except Exception as e:
            logging.error(f"خطأ في حفظ كلمة المرور: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تغيير كلمة المرور: {str(e)}")
    
    def setup_styles(self):
        """إعداد أنماط الحوار"""
        try:
            self.setStyleSheet("""
                QDialog {
                    background-color: #f8f9fa;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }
                
                #dialogTitle {
                    color: #2c3e50;
                    padding: 10px 0;
                }
                
                #dialogDescription {
                    color: #7f8c8d;
                    font-size: 11px;
                    padding: 5px 0;
                }
                
                #formFrame {
                    background-color: white;
                    border: 1px solid #bdc3c7;
                    border-radius: 8px;
                    padding: 20px;
                }
                
                QLabel {
                    color: #2c3e50;
                    font-weight: 500;
                }
                
                #requirementsLabel {
                    color: #7f8c8d;
                    font-size: 10px;
                    font-style: italic;
                }
                
                QLineEdit {
                    border: 2px solid #bdc3c7;
                    border-radius: 6px;
                    padding: 8px;
                    background-color: white;
                    color: #2c3e50;
                    font-size: 11px;
                }
                
                QLineEdit:focus {
                    border-color: #3498db;
                }
                
                QCheckBox {
                    color: #2c3e50;
                    font-size: 10px;
                    spacing: 8px;
                }
                
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                
                QCheckBox::indicator:unchecked {
                    border: 2px solid #bdc3c7;
                    border-radius: 3px;
                    background-color: white;
                }
                
                QCheckBox::indicator:checked {
                    border: 2px solid #3498db;
                    border-radius: 3px;
                    background-color: #3498db;
                    image: url(:/icons/check.png);
                }
                
                QPushButton#saveButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                }
                
                QPushButton#saveButton:hover {
                    background-color: #219a52;
                }
                
                QPushButton#saveButton:pressed {
                    background-color: #1e8449;
                }
                
                QPushButton#cancelButton {
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                }
                
                QPushButton#cancelButton:hover {
                    background-color: #7f8c8d;
                }
                
                QPushButton#cancelButton:pressed {
                    background-color: #566573;
                }
            """)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد أنماط الحوار: {e}")
