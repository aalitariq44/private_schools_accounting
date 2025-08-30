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
    QMessageBox, QScrollArea, QSpacerItem, QSizePolicy,
    QDialog
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
                        self.setFont(QFont(families[0], 13))
                        logging.info("تم تحميل خط Cairo بنجاح في صفحة الإعدادات")
                        return
            # بديل
            self.setFont(QFont("Arial", 13))
            logging.warning("تم استخدام خط Arial كبديل لخط Cairo في صفحة الإعدادات")
        except Exception as e:
            logging.error(f"خطأ في إعداد خط Cairo في صفحة الإعدادات: {e}")
            self.setFont(QFont("Arial", 13))
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(8, 8, 8, 8)
            main_layout.setSpacing(8)
            
            # العنوان
            self.create_header(main_layout)
            
            # منطقة التمرير
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout()
            scroll_layout.setSpacing(8)
            
            # إعدادات المؤسسة
            self.create_organization_section(scroll_layout)
            
            # إعدادات التطبيق المحمول
            self.create_mobile_app_section(scroll_layout)
            
            # إعدادات العام الدراسي
            self.create_academic_year_section(scroll_layout)
            
            # إعدادات الأمان
            self.create_security_section(scroll_layout)
            
            # الإعدادات المتقدمة
            self.create_advanced_section(scroll_layout)
            
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
            title_font.setPointSize(13)
            title_font.setBold(True)
            title_label.setFont(title_font)
            
            header_layout.addWidget(title_label)
            header_layout.addStretch()
            
            header_frame.setLayout(header_layout)
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء رأس الصفحة: {e}")
    
    def create_organization_section(self, layout):
        """إنشاء قسم إعدادات المؤسسة"""
        try:
            # إطار المؤسسة
            organization_group = QGroupBox("معلومات المؤسسة")
            organization_group.setObjectName("settingsGroup")
            organization_layout = QGridLayout()
            organization_layout.setSpacing(8)
            
            # تسمية اسم المؤسسة
            org_label = QLabel("اسم المؤسسة:")
            org_label.setFont(QFont("Arial", 11))  # يمكن خفضه لاحقاً إذا لزم
            
            # حقل عرض اسم المؤسسة (غير قابل للتعديل)
            self.organization_display = QLabel()
            self.organization_display.setObjectName("organizationName")
            self.organization_display.setFont(QFont("Arial", 11, QFont.Bold))
            self.organization_display.setStyleSheet("""
                QLabel#organizationName {
                    background-color: #F8F9FA;
                    border: 1px solid #DEE2E6;
                    border-radius: 5px;
                    padding: 8px;
                    color: #495057;
                }
            """)
            
            # نص توضيحي
            info_label = QLabel("* اسم المؤسسة لا يمكن تغييره بعد الإعداد الأولي")
            info_label.setFont(QFont("Arial", 9))
            info_label.setStyleSheet("color: #6C757D; font-style: italic;")
            
            # إضافة العناصر للتخطيط
            organization_layout.addWidget(org_label, 0, 0)
            organization_layout.addWidget(self.organization_display, 0, 1)
            organization_layout.addWidget(info_label, 1, 1)
            
            # إضافة مساحة مرنة
            organization_layout.setColumnStretch(2, 1)
            
            organization_group.setLayout(organization_layout)
            layout.addWidget(organization_group)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم المؤسسة: {e}")
    
    def create_mobile_app_section(self, layout):
        """إنشاء قسم إعدادات التطبيق المحمول"""
        try:
            # إطار التطبيق المحمول
            mobile_group = QGroupBox("إعدادات التطبيق المحمول")
            mobile_group.setObjectName("settingsGroup")
            mobile_layout = QGridLayout()
            mobile_layout.setSpacing(8)
            
            # تسمية كلمة المرور
            password_label = QLabel("كلمة مرور تسجيل الدخول في الهاتف:")
            password_label.setFont(QFont("Arial", 11))
            
            # عرض حالة كلمة المرور
            self.mobile_password_display = QLabel()
            self.mobile_password_display.setObjectName("mobilePasswordStatus")
            self.mobile_password_display.setFont(QFont("Arial", 10))
            self.mobile_password_display.setStyleSheet("""
                QLabel#mobilePasswordStatus {
                    background-color: #F8F9FA;
                    border: 1px solid #DEE2E6;
                    border-radius: 5px;
                    padding: 8px;
                    color: #495057;
                }
            """)
            
            # زر إدارة كلمة المرور
            manage_password_btn = QPushButton("إدارة كلمة المرور")
            manage_password_btn.setObjectName("mobileButton")
            manage_password_btn.setMinimumHeight(30)
            manage_password_btn.clicked.connect(self.manage_mobile_password)
            
            # نص توضيحي
            info_label = QLabel("* تُستخدم للوصول إلى بيانات المؤسسة من التطبيق المحمول")
            info_label.setFont(QFont("Arial", 9))
            info_label.setStyleSheet("color: #6C757D; font-style: italic;")
            
            # إضافة العناصر للتخطيط
            mobile_layout.addWidget(password_label, 0, 0)
            mobile_layout.addWidget(self.mobile_password_display, 0, 1)
            mobile_layout.addWidget(manage_password_btn, 1, 1)
            mobile_layout.addWidget(info_label, 2, 1)
            
            # إضافة مساحة مرنة
            mobile_layout.setColumnStretch(2, 1)
            
            mobile_group.setLayout(mobile_layout)
            layout.addWidget(mobile_group)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم التطبيق المحمول: {e}")
    
    def create_academic_year_section(self, layout):
        """إنشاء قسم إعدادات العام الدراسي"""
        try:
            # إطار العام الدراسي
            academic_group = QGroupBox("إعدادات العام الدراسي")
            academic_group.setObjectName("settingsGroup")
            academic_layout = QGridLayout()
            academic_layout.setSpacing(8)
            
            # تسمية العام الدراسي
            year_label = QLabel("العام الدراسي الحالي:")
            year_label.setFont(QFont("Arial", 11))
            
            # قائمة الأعوام الدراسية
            self.academic_year_combo = QComboBox()
            self.academic_year_combo.setMinimumHeight(28)
            self.academic_year_combo.setFont(QFont("Arial", 11))
            
            # ملء قائمة الأعوام
            self.populate_academic_years()
            
            # زر الحفظ
            save_year_btn = QPushButton("حفظ العام الدراسي")
            save_year_btn.setObjectName("primaryButton")
            save_year_btn.setMinimumHeight(30)
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
            security_layout.setSpacing(8)
            
            # تسمية كلمة المرور
            password_label = QLabel("كلمة المرور:")
            password_label.setFont(QFont("Arial", 11))
            
            # زر تغيير كلمة المرور
            change_password_btn = QPushButton("تغيير كلمة المرور")
            change_password_btn.setObjectName("secondaryButton")
            change_password_btn.setMinimumHeight(30)
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
    
    def manage_mobile_password(self):
        """إدارة كلمة مرور التطبيق المحمول"""
        try:
            from ui.dialogs.mobile_password_dialog import show_mobile_password_dialog
            if show_mobile_password_dialog(self) == QDialog.Accepted:
                # تحديث عرض حالة كلمة المرور
                self.load_mobile_password_status()
                log_user_action("تم تحديث كلمة مرور التطبيق المحمول")
            
        except Exception as e:
            logging.error(f"خطأ في إدارة كلمة مرور التطبيق المحمول: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في إدارة كلمة المرور: {str(e)}")
    
    def load_settings(self):
        """تحميل الإعدادات من قاعدة البيانات"""
        try:
            # تحميل اسم المؤسسة
            organization_name = settings_manager.get_organization_name()
            if organization_name:
                self.organization_display.setText(organization_name)
            else:
                self.organization_display.setText("لم يتم تعيين اسم المؤسسة")
            
            # تحميل حالة كلمة مرور التطبيق المحمول
            self.load_mobile_password_status()
            
            # تحميل العام الدراسي الحالي
            current_year = self.get_current_academic_year()
            if current_year:
                index = self.academic_year_combo.findText(current_year)
                if index >= 0:
                    self.academic_year_combo.setCurrentIndex(index)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الإعدادات: {e}")
    
    def load_mobile_password_status(self):
        """تحميل حالة كلمة مرور التطبيق المحمول"""
        try:
            mobile_password = settings_manager.get_mobile_password()
            if mobile_password:
                self.mobile_password_display.setText("محفوظة ✓")
                self.mobile_password_display.setStyleSheet("""
                    QLabel#mobilePasswordStatus {
                        background-color: #d4edda;
                        border: 1px solid #c3e6cb;
                        border-radius: 5px;
                        padding: 8px;
                        color: #155724;
                        font-weight: bold;
                    }
                """)
            else:
                self.mobile_password_display.setText("غير محفوظة")
                self.mobile_password_display.setStyleSheet("""
                    QLabel#mobilePasswordStatus {
                        background-color: #f8d7da;
                        border: 1px solid #f5c6cb;
                        border-radius: 5px;
                        padding: 8px;
                        color: #721c24;
                        font-style: italic;
                    }
                """)
        except Exception as e:
            logging.error(f"خطأ في تحميل حالة كلمة مرور التطبيق المحمول: {e}")
            self.mobile_password_display.setText("خطأ في تحميل البيانات")
            self.mobile_password_display.setStyleSheet("""
                QLabel#mobilePasswordStatus {
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 5px;
                    padding: 8px;
                    color: #721c24;
                }
            """)
    
    def create_advanced_section(self, layout):
        """إنشاء قسم الإعدادات المتقدمة"""
        try:
            # إطار الإعدادات المتقدمة
            advanced_group = QGroupBox("الإعدادات المتقدمة")
            advanced_group.setObjectName("settingsGroup")
            advanced_layout = QGridLayout()
            advanced_layout.setSpacing(8)
            
            # تسمية الإعدادات المتقدمة
            advanced_label = QLabel("إدارة المدارس:")
            advanced_label.setFont(QFont("Arial", 11))
            
            # زر الإعدادات المتقدمة
            advanced_btn = QPushButton("الإعدادات المتقدمة")
            advanced_btn.setObjectName("advancedButton")
            advanced_btn.setMinimumHeight(30)
            advanced_btn.clicked.connect(self.open_advanced_settings)
            
            # نص توضيحي
            info_label = QLabel("* إدارة المدارس والإعدادات المتقدمة")
            info_label.setFont(QFont("Arial", 9))
            info_label.setStyleSheet("color: #6C757D; font-style: italic;")
            
            # إضافة العناصر للتخطيط
            advanced_layout.addWidget(advanced_label, 0, 0)
            advanced_layout.addWidget(advanced_btn, 0, 1)
            advanced_layout.addWidget(info_label, 1, 1)
            
            # إضافة مساحة مرنة
            advanced_layout.setColumnStretch(2, 1)
            
            advanced_group.setLayout(advanced_layout)
            layout.addWidget(advanced_group)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الإعدادات المتقدمة: {e}")
    
    def open_advanced_settings(self):
        """فتح نافذة الإعدادات المتقدمة"""
        try:
            from .advanced_settings_dialog import show_advanced_settings
            show_advanced_settings(self)
        except Exception as e:
            logging.error(f"خطأ في فتح الإعدادات المتقدمة: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في فتح الإعدادات المتقدمة: {str(e)}")
    
    def setup_styles(self):
        """إعداد أنماط الصفحة"""
        try:
            self.setStyleSheet("""
                QWidget { background:#F5F6F7; font-family:'Cairo','Arial'; font-size:13px; }
                #pageTitle { color:#2C3E50; padding:4px 0; font-size:13px; font-weight:600; }
                QGroupBox { font-size:12px; font-weight:600; color:#2C3E50; border:1px solid #DDE1E4; border-radius:6px; margin-top:6px; background:#FFFFFF; padding:8px 8px 10px 8px; }
                QGroupBox::title { subcontrol-origin: margin; left:8px; padding:0 4px; background:#FFFFFF; }
                QLabel { color:#2C3E50; font-weight:500; font-size:12px; }
                QComboBox { border:1px solid #C5CBD0; border-radius:4px; padding:2px 6px; background:#FFFFFF; min-height:24px; font-size:12px; }
                QComboBox:focus { border:1px solid #2F6ED1; }
                QPushButton { background:#FFFFFF; color:#2F6ED1; border:1px solid #C5CBD0; border-radius:4px; padding:4px 10px; font-size:12px; font-weight:600; }
                QPushButton:hover { background:#2F6ED1; color:#FFFFFF; }
                QPushButton:pressed { background:#2559A8; }
                QPushButton#secondaryButton { color:#C0392B; border:1px solid #D19990; }
                QPushButton#secondaryButton:hover { background:#C0392B; color:#FFFFFF; }
                QPushButton#advancedButton { color:#5A2D91; border:1px solid #B9A9D3; }
                QPushButton#advancedButton:hover { background:#5A2D91; color:#FFFFFF; }
                QPushButton#mobileButton { color:#117a8b; border:1px solid #82C8D3; }
                QPushButton#mobileButton:hover { background:#117a8b; color:#FFFFFF; }
                QScrollArea { border:none; background:transparent; }
                QScrollBar:vertical { border:none; background:#E2E5E8; width:10px; border-radius:5px; }
                QScrollBar::handle:vertical { background:#C5CBD0; border-radius:5px; min-height:24px; }
                QScrollBar::handle:vertical:hover { background:#AEB5BA; }
            """)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الأنماط: {e}")
