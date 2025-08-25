# -*- coding: utf-8 -*-
"""
نافذة اختيار نوع الطباعة
"""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QRadioButton, QButtonGroup, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon


class PrintTypeDialog(QDialog):
    """نافذة اختيار نوع الطباعة"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_type = None
        self.setup_ui()
        self.setup_styles()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("اختيار نوع الطباعة")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        # التخطيط الرئيسي
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # العنوان
        title_label = QLabel("اختر نوع الطباعة المفضل")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # فاصل
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # خيارات الطباعة
        options_frame = QFrame()
        options_layout = QVBoxLayout(options_frame)
        options_layout.setSpacing(15)
        
        # مجموعة الأزرار
        self.button_group = QButtonGroup()
        
        # خيار HTML/PDF
        self.html_radio = QRadioButton("طباعة HTML/PDF")
        self.html_radio.setObjectName("optionRadio")
        self.html_radio.setChecked(True)  # الخيار الافتراضي
        self.button_group.addButton(self.html_radio, 1)
        options_layout.addWidget(self.html_radio)
        
        html_desc = QLabel("• معاينة سريعة في المتصفح\n• تنسيق HTML تقليدي\n• إمكانية الطباعة المباشرة")
        html_desc.setObjectName("descLabel")
        options_layout.addWidget(html_desc)
        
        # خيار Word
        self.word_radio = QRadioButton("إنشاء ملف Word")
        self.word_radio.setObjectName("optionRadio")
        self.button_group.addButton(self.word_radio, 2)
        options_layout.addWidget(self.word_radio)
        
        word_desc = QLabel("• إنشاء ملف Word (.docx) قابل للتعديل\n• فتح تلقائي في Microsoft Word\n• إمكانية الحفظ والتخصيص")
        word_desc.setObjectName("descLabel")
        options_layout.addWidget(word_desc)
        
        layout.addWidget(options_frame)
        
        # فاصل
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator2)
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        buttons_layout.addStretch()
        
        self.ok_button = QPushButton("موافق")
        self.ok_button.setObjectName("okButton")
        self.ok_button.clicked.connect(self.accept_selection)
        self.ok_button.setDefault(True)
        buttons_layout.addWidget(self.ok_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def setup_styles(self):
        """إعداد التنسيقات"""
        style = """
            QDialog {
                background-color: #f5f5f5;
                font-family: Arial, sans-serif;
            }
            
            #titleLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
            
            #optionRadio {
                font-size: 14px;
                font-weight: bold;
                color: #34495e;
                padding: 5px;
            }
            
            #optionRadio::indicator {
                width: 18px;
                height: 18px;
            }
            
            #optionRadio::indicator:unchecked {
                border: 2px solid #bdc3c7;
                background-color: white;
                border-radius: 9px;
            }
            
            #optionRadio::indicator:checked {
                border: 2px solid #3498db;
                background-color: #3498db;
                border-radius: 9px;
            }
            
            #optionRadio::indicator:checked:pressed {
                background-color: #2980b9;
            }
            
            #descLabel {
                font-size: 12px;
                color: #7f8c8d;
                margin-left: 25px;
                margin-bottom: 10px;
                line-height: 1.4;
            }
            
            #okButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 80px;
            }
            
            #okButton:hover {
                background-color: #229954;
            }
            
            #okButton:pressed {
                background-color: #1e8449;
            }
            
            #cancelButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 80px;
            }
            
            #cancelButton:hover {
                background-color: #7f8c8d;
            }
            
            #cancelButton:pressed {
                background-color: #707b7c;
            }
        """
        
        self.setStyleSheet(style)
    
    def accept_selection(self):
        """قبول الاختيار والإغلاق"""
        if self.html_radio.isChecked():
            self.selected_type = "html"
        elif self.word_radio.isChecked():
            self.selected_type = "word"
        else:
            self.selected_type = "html"  # افتراضي
        
        self.accept()
    
    def get_selected_type(self):
        """الحصول على نوع الطباعة المختار"""
        return self.selected_type


# دالة مساعدة لعرض نافذة اختيار نوع الطباعة
def show_print_type_dialog(parent=None):
    """عرض نافذة اختيار نوع الطباعة وإرجاع النوع المختار"""
    dialog = PrintTypeDialog(parent)
    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_selected_type()
    return None
