#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة تفعيل الترخيص
"""

import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTextEdit, QProgressBar,
                            QMessageBox, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap
import logging

from .license_manager import LicenseManager


class ActivationWorker(QThread):
    """خيط عمل للتحقق من التفعيل"""
    
    finished = pyqtSignal(bool, dict, str)
    
    def __init__(self, activation_code: str):
        super().__init__()
        self.activation_code = activation_code
        self.license_manager = LicenseManager()
    
    def run(self):
        """تشغيل عملية التحقق من التفعيل"""
        try:
            is_valid, license_info, message = self.license_manager.verify_activation_code_online(
                self.activation_code
            )
            self.finished.emit(is_valid, license_info, message)
        except Exception as e:
            self.finished.emit(False, {}, f"خطأ غير متوقع: {str(e)}")


class ActivationDialog(QDialog):
    """نافذة تفعيل الترخيص"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.worker = None
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("تفعيل الترخيص - حسابات المدارس الأهلية")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # التخطيط الرئيسي
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # عنوان النافذة
        title_label = QLabel("تفعيل الترخيص")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # فاصل
        separator = QFrame()
        separator.setFrameStyle(QFrame.HLine | QFrame.Sunken)
        layout.addWidget(separator)
        
        # نص تفسيري
        info_label = QLabel(
            "يرجى إدخال رمز التفعيل الخاص بك.\\n"
            "إذا لم يكن لديك رمز تفعيل، يرجى التواصل معنا عبر:"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #7f8c8d; line-height: 1.4;")
        layout.addWidget(info_label)
        
        # نص معلومات التواصل
        contact_label = QLabel(
            "واتساب: 07859371349"
            "تليجرام: @tech_solu"
        )
        contact_label.setAlignment(Qt.AlignCenter)
        contact_label.setWordWrap(True)
        contact_label.setStyleSheet("color: #3498db; font-weight: bold; line-height: 1.4;")
        layout.addWidget(contact_label)
        
        # حقل إدخال رمز التفعيل
        activation_layout = QVBoxLayout()
        
        activation_label = QLabel("رمز التفعيل:")
        activation_label.setFont(QFont("Arial", 10, QFont.Bold))
        activation_layout.addWidget(activation_label)
        
        self.activation_input = QLineEdit()
        self.activation_input.setPlaceholderText("أدخل رمز التفعيل هنا...")
        self.activation_input.setFont(QFont("Courier", 12))
        self.activation_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                font-family: 'Courier New', monospace;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        activation_layout.addWidget(self.activation_input)
        
        layout.addLayout(activation_layout)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # شريط تقدم لا نهائي
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                text-align: center;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # منطقة الرسائل
        self.message_area = QTextEdit()
        self.message_area.setMaximumHeight(80)
        self.message_area.setVisible(False)
        self.message_area.setReadOnly(True)
        self.message_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                background-color: #f8f9fa;
                padding: 8px;
            }
        """)
        layout.addWidget(self.message_area)
        
        # الأزرار
        buttons_layout = QHBoxLayout()
        
        # زر الإلغاء
        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        buttons_layout.addWidget(self.cancel_button)
        
        # مساحة فارغة
        buttons_layout.addStretch()
        
        # زر التفعيل
        self.activate_button = QPushButton("تفعيل")
        self.activate_button.setMinimumHeight(40)
        self.activate_button.setDefault(True)
        self.activate_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        buttons_layout.addWidget(self.activate_button)
        
        layout.addLayout(buttons_layout)
        
        # تعيين التركيز على حقل الإدخال
        self.activation_input.setFocus()
    
    def setup_connections(self):
        """إعداد الاتصالات"""
        self.activate_button.clicked.connect(self.start_activation)
        self.cancel_button.clicked.connect(self.reject)
        self.activation_input.returnPressed.connect(self.start_activation)
        self.activation_input.textChanged.connect(self.on_text_changed)
    
    def on_text_changed(self):
        """تغيير حالة زر التفعيل حسب محتوى النص"""
        has_text = bool(self.activation_input.text().strip())
        self.activate_button.setEnabled(has_text and not self.progress_bar.isVisible())
    
    def start_activation(self):
        """بدء عملية التفعيل"""
        activation_code = self.activation_input.text().strip()
        
        if not activation_code:
            self.show_error_message("يرجى إدخال رمز التفعيل")
            return
        
        # إخفاء الرسائل السابقة وإظهار شريط التقدم
        self.message_area.setVisible(False)
        self.progress_bar.setVisible(True)
        self.activate_button.setEnabled(False)
        self.activation_input.setEnabled(False)
        
        # بدء خيط العمل
        self.worker = ActivationWorker(activation_code)
        self.worker.finished.connect(self.on_activation_finished)
        self.worker.start()
    
    def on_activation_finished(self, success: bool, license_info: dict, message: str):
        """انتهاء عملية التفعيل"""
        # إخفاء شريط التقدم
        self.progress_bar.setVisible(False)
        self.activate_button.setEnabled(True)
        self.activation_input.setEnabled(True)
        
        if success:
            self.show_success_message(message)
            # إغلاق النافذة بعد ثانيتين
            QTimer.singleShot(2000, self.accept)
        else:
            self.show_error_message(message)
            self.activation_input.setFocus()
            self.activation_input.selectAll()
    
    def show_success_message(self, message: str):
        """عرض رسالة نجاح"""
        self.message_area.setVisible(True)
        self.message_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #27ae60;
                border-radius: 6px;
                background-color: #d5f4e6;
                padding: 8px;
                color: #155724;
            }
        """)
        self.message_area.setPlainText(f"✓ {message}")
    
    def show_error_message(self, message: str):
        """عرض رسالة خطأ"""
        self.message_area.setVisible(True)
        self.message_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e74c3c;
                border-radius: 6px;
                background-color: #f8d7da;
                padding: 8px;
                color: #721c24;
            }
        """)
        self.message_area.setPlainText(f"✗ {message}")
    
    def closeEvent(self, event):
        """معالجة إغلاق النافذة"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, 
                "تأكيد الإغلاق",
                "عملية التفعيل جارية. هل تريد الإلغاء؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.worker:
                    self.worker.terminate()
                    self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def show_activation_dialog(parent=None) -> bool:
    """
    عرض نافذة التفعيل
    Returns: True إذا تم التفعيل بنجاح، False خلاف ذلك
    """
    dialog = ActivationDialog(parent)
    result = dialog.exec_()
    return result == QDialog.Accepted
