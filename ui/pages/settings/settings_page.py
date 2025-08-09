#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إعدادات التطبيق
"""

import logging
import os
import config
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QLabel, QPushButton, QComboBox, QGroupBox,
    QMessageBox, QScrollArea, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QFontDatabase

from core.database.connection import db_manager
from core.utils.logger import log_user_action
from core.utils.settings_manager import settings_manager
from .change_password_dialog import ChangePasswordDialog


class SettingsPage(QWidget):
    """صفحة الإعدادات"""
    
    # إشارات
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # إعداد خط Cairo
        self.setup_cairo_font()
        self.setup_ui()
        self.setup_styles()
        self.load_settings()
        
        log_user_action("دخول صفحة الإعدادات")
    
    def setup_cairo_font(self):
        """إعداد خط Cairo"""
        try:
            font_path = os.path.join(config.FONTS_DIR, "Cairo-Medium.ttf")
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        self.setFont(QFont(families[0], 18))
                        logging.info("تم تحميل خط Cairo بنجاح في صفحة الإعدادات")
                        return
            # بديل
            self.setFont(QFont("Arial", 18))
            logging.warning("تم استخدام خط Arial كبديل لخط Cairo في صفحة الإعدادات")
        except Exception as e:
            logging.error(f"خطأ في إعداد خط Cairo في صفحة الإعدادات: {e}")
            self.setFont(QFont("Arial", 18))
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(20)
            
            # العنوان
            self.create_header(main_layout)
            
            # منطقة التمرير
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout()
            scroll_layout.setSpacing(20)
            
            # إعدادات العام الدراسي
            self.create_academic_year_section(scroll_layout)
            
            # إعدادات الأمان
            self.create_security_section(scroll_layout)
            
            # مساحة مرنة
            scroll_layout.addItem(
                QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            )
            
            scroll_widget.setLayout(scroll_layout)
            scroll_area.setWidget(scroll_widget)
            
            main_layout.addWidget(scroll_area)
            
            self.setLayout(main_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة الإعدادات: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في إعداد الصفحة: {str(e)}")
    
    def create_header(self, layout):
        """إنشاء رأس الصفحة"""
        try:
            header_frame = QFrame()
            header_frame.setObjectName("headerFrame")
            header_layout = QHBoxLayout()
            
            # العنوان
            title_label = QLabel("إعدادات التطبيق")
            title_label.setObjectName("pageTitle")
            title_font = QFont()
            title_font.setPointSize(18)
            title_font.setBold(True)
            title_label.setFont(title_font)
            
            header_layout.addWidget(title_label)
            header_layout.addStretch()
            
            header_frame.setLayout(header_layout)
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء رأس الصفحة: {e}")
    
    def create_academic_year_section(self, layout):
        """إنشاء قسم إعدادات العام الدراسي"""
        try:
            # إطار العام الدراسي
            academic_group = QGroupBox("إعدادات العام الدراسي")
            academic_group.setObjectName("settingsGroup")
            academic_layout = QGridLayout()
            academic_layout.setSpacing(15)
            
            # تسمية العام الدراسي
            year_label = QLabel("العام الدراسي الحالي:")
            year_label.setFont(QFont("Arial", 11))
            
            # قائمة الأعوام الدراسية
            self.academic_year_combo = QComboBox()
            self.academic_year_combo.setMinimumHeight(35)
            self.academic_year_combo.setFont(QFont("Arial", 11))
            
            # ملء قائمة الأعوام
            self.populate_academic_years()
            
            # زر الحفظ
            save_year_btn = QPushButton("حفظ العام الدراسي")
            save_year_btn.setObjectName("primaryButton")
            save_year_btn.setMinimumHeight(40)
            save_year_btn.clicked.connect(self.save_academic_year)
            
            # إضافة العناصر للتخطيط
            academic_layout.addWidget(year_label, 0, 0)
            academic_layout.addWidget(self.academic_year_combo, 0, 1)
            academic_layout.addWidget(save_year_btn, 1, 1)
            
            # إضافة مساحة مرنة
            academic_layout.setColumnStretch(2, 1)
            
            academic_group.setLayout(academic_layout)
            layout.addWidget(academic_group)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم العام الدراسي: {e}")
    
    def create_security_section(self, layout):
        """إنشاء قسم إعدادات الأمان"""
        try:
            # إطار الأمان
            security_group = QGroupBox("إعدادات الأمان")
            security_group.setObjectName("settingsGroup")
            security_layout = QGridLayout()
            security_layout.setSpacing(15)
            
            # تسمية كلمة المرور
            password_label = QLabel("كلمة المرور:")
            password_label.setFont(QFont("Arial", 11))
            
            # زر تغيير كلمة المرور
            change_password_btn = QPushButton("تغيير كلمة المرور")
            change_password_btn.setObjectName("secondaryButton")
            change_password_btn.setMinimumHeight(40)
            change_password_btn.clicked.connect(self.change_password)
            
            # إضافة العناصر للتخطيط
            security_layout.addWidget(password_label, 0, 0)
            security_layout.addWidget(change_password_btn, 0, 1)
            
            # إضافة مساحة مرنة
            security_layout.setColumnStretch(2, 1)
            
            security_group.setLayout(security_layout)
            layout.addWidget(security_group)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الأمان: {e}")
    
    def populate_academic_years(self):
        """ملء قائمة الأعوام الدراسية"""
        try:
            self.academic_year_combo.clear()
            
            # إنشاء قائمة الأعوام من 2024 إلى 2041
            for year in range(2024, 2042):
                year_text = f"{year} - {year + 1}"
                self.academic_year_combo.addItem(year_text, year)
            
            # تحديد العام الحالي إذا كان محفوظاً
            current_year = self.get_current_academic_year()
            if current_year:
                index = self.academic_year_combo.findText(current_year)
                if index >= 0:
                    self.academic_year_combo.setCurrentIndex(index)
            
        except Exception as e:
            logging.error(f"خطأ في ملء قائمة الأعوام الدراسية: {e}")
    
    def get_current_academic_year(self):
        """الحصول على العام الدراسي الحالي من قاعدة البيانات"""
        try:
            return settings_manager.get_academic_year()
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على العام الدراسي الحالي: {e}")
            return None
    
    def save_academic_year(self):
        """حفظ العام الدراسي المحدد"""
        try:
            selected_year = self.academic_year_combo.currentText()
            
            if not selected_year:
                QMessageBox.warning(self, "تحذير", "يرجى اختيار العام الدراسي")
                return
            
            # حفظ باستخدام مدير الإعدادات
            if settings_manager.set_academic_year(selected_year):
                QMessageBox.information(self, "نجح", "تم حفظ العام الدراسي بنجاح")
                log_user_action(f"تم تحديث العام الدراسي إلى: {selected_year}")
                self.settings_changed.emit()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في حفظ العام الدراسي")
            
        except Exception as e:
            logging.error(f"خطأ في حفظ العام الدراسي: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ العام الدراسي: {str(e)}")
    
    def change_password(self):
        """تغيير كلمة المرور"""
        try:
            dialog = ChangePasswordDialog(self)
            if dialog.exec_() == dialog.Accepted:
                QMessageBox.information(self, "نجح", "تم تغيير كلمة المرور بنجاح")
                log_user_action("تم تغيير كلمة المرور")
            
        except Exception as e:
            logging.error(f"خطأ في تغيير كلمة المرور: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تغيير كلمة المرور: {str(e)}")
    
    def load_settings(self):
        """تحميل الإعدادات من قاعدة البيانات"""
        try:
            # تحميل العام الدراسي الحالي
            current_year = self.get_current_academic_year()
            if current_year:
                index = self.academic_year_combo.findText(current_year)
                if index >= 0:
                    self.academic_year_combo.setCurrentIndex(index)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الإعدادات: {e}")
    
    def setup_styles(self):
        """إعداد أنماط الصفحة"""
        try:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f8f9fa;
                    font-family: 'Cairo', Arial, sans-serif;
                    font-size: 18px;
                }
                
                #pageTitle {
                    color: #2c3e50;
                    padding: 10px 0;
                }
                
                QGroupBox {
                    font-size: 14px;
                    font-weight: bold;
                    color: #34495e;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding-top: 15px;
                    background-color: white;
                }
                
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 10px 0 10px;
                    background-color: white;
                }
                
                QLabel {
                    color: #2c3e50;
                    font-weight: 500;
                }
                
                QComboBox {
                    border: 2px solid #bdc3c7;
                    border-radius: 6px;
                    padding: 8px;
                    background-color: white;
                    color: #2c3e50;
                    min-width: 200px;
                }
                
                QComboBox:focus {
                    border-color: #3498db;
                }
                
                QComboBox::drop-down {
                    border: none;
                    width: 30px;
                }
                
                QComboBox::down-arrow {
                    image: none;
                    border: 5px solid transparent;
                    border-top: 8px solid #7f8c8d;
                    margin-right: 5px;
                }
                
                QPushButton#primaryButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                    min-width: 150px;
                }
                
                QPushButton#primaryButton:hover {
                    background-color: #2980b9;
                }
                
                QPushButton#primaryButton:pressed {
                    background-color: #21618c;
                }
                
                QPushButton#secondaryButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                    min-width: 150px;
                }
                
                QPushButton#secondaryButton:hover {
                    background-color: #c0392b;
                }
                
                QPushButton#secondaryButton:pressed {
                    background-color: #a93226;
                }
                
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                
                QScrollBar:vertical {
                    border: none;
                    background-color: #ecf0f1;
                    width: 12px;
                    border-radius: 6px;
                }
                
                QScrollBar::handle:vertical {
                    background-color: #bdc3c7;
                    border-radius: 6px;
                    min-height: 30px;
                }
                
                QScrollBar::handle:vertical:hover {
                    background-color: #95a5a6;
                }
            """)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الأنماط: {e}")
