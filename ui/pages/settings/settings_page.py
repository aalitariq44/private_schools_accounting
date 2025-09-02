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
    QDialog, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QFontDatabase

from core.database.connection import db_manager
from core.utils.logger import log_user_action
from core.utils.settings_manager import settings_manager
from .change_password_dialog import ChangePasswordDialog

# استيراد وحدة أحجام الخطوط
from ...font_sizes import FontSizeManager
from ...ui_settings_manager import ui_settings_manager


class SettingsPage(QWidget):
    """صفحة الإعدادات"""
    
    # إشارات
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # الحصول على حجم الخط المحفوظ من إعدادات UI
        self.current_font_size = ui_settings_manager.get_font_size("settings")
        
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
            
            # اعدادات المدارس المتقدمة
            self.create_advanced_section(scroll_layout)
            
            # إعدادات النسخ الاحتياطي المحلي
            self.create_local_backup_section(scroll_layout)
            
            # مساحة مرنة
            scroll_layout.addItem(
                QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            )
            
            scroll_widget.setLayout(scroll_layout)
            scroll_area.setWidget(scroll_widget)
            
            main_layout.addWidget(scroll_area)
            
            self.setLayout(main_layout)
            
            # ربط تغيير حجم الخط
            self.font_size_combo.currentTextChanged.connect(self.change_font_size)
            
            # تحديث القائمة المنسدلة لحجم الخط
            self.update_font_size_combo()
            
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
            
            # فلتر حجم الخط
            font_size_label = QLabel("حجم الخط:")
            font_size_label.setObjectName("filterLabel")
            header_layout.addWidget(font_size_label)
            
            self.font_size_combo = QComboBox()
            self.font_size_combo.setObjectName("filterCombo")
            self.font_size_combo.addItems(FontSizeManager.get_available_sizes())
            self.font_size_combo.setCurrentText(self.current_font_size)
            self.font_size_combo.setMinimumWidth(100)
            header_layout.addWidget(self.font_size_combo)
            
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
                logging.info(f"إرسال إشارة settings_changed من صفحة الإعدادات")
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
            
            # تحميل مسار النسخ الاحتياطي المحلي
            backup_path = self.get_backup_path()
            if backup_path:
                self.backup_path_display.setText(backup_path)
            else:
                self.backup_path_display.setText("لم يتم تحديد مسار")
            
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
        """إنشاء قسم اعدادات المدارس المتقدمة"""
        try:
            # إطار اعدادات المدارس المتقدمة
            advanced_group = QGroupBox("اعدادات المدارس المتقدمة")
            advanced_group.setObjectName("settingsGroup")
            advanced_layout = QGridLayout()
            advanced_layout.setSpacing(8)
            
            # تسمية اعدادات المدارس المتقدمة
            advanced_label = QLabel("إدارة المدارس:")
            advanced_label.setFont(QFont("Arial", 11))
            
            # زر اعدادات المدارس المتقدمة
            advanced_btn = QPushButton("اعدادات المدارس المتقدمة")
            advanced_btn.setObjectName("advancedButton")
            advanced_btn.setMinimumHeight(30)
            advanced_btn.clicked.connect(self.open_advanced_settings)
            
            # نص توضيحي
            info_label = QLabel("* إدارة المدارس واعدادات المدارس المتقدمة")
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
            logging.error(f"خطأ في إنشاء قسم اعدادات المدارس المتقدمة: {e}")
    
    def create_local_backup_section(self, layout):
        """إنشاء قسم إعدادات النسخ الاحتياطي المحلي"""
        try:
            # إطار النسخ الاحتياطي المحلي
            backup_group = QGroupBox("إعدادات النسخ الاحتياطي المحلي")
            backup_group.setObjectName("settingsGroup")
            backup_layout = QGridLayout()
            backup_layout.setSpacing(8)
            
            # تسمية مسار النسخ الاحتياطي
            backup_path_label = QLabel("مسار النسخ الاحتياطي المحلي:")
            backup_path_label.setFont(QFont("Arial", 11))
            
            # حقل عرض المسار
            self.backup_path_display = QLabel("لم يتم تحديد مسار")
            self.backup_path_display.setObjectName("backupPathDisplay")
            self.backup_path_display.setFont(QFont("Arial", 10))
            self.backup_path_display.setStyleSheet("""
                QLabel#backupPathDisplay {
                    background-color: #F8F9FA;
                    border: 1px solid #DEE2E6;
                    border-radius: 4px;
                    padding: 8px;
                    color: #495057;
                }
            """)
            
            # زر اختيار المسار
            select_path_btn = QPushButton("اختيار المجلد")
            select_path_btn.setObjectName("secondaryButton")
            select_path_btn.setMinimumHeight(30)
            select_path_btn.clicked.connect(self.select_backup_path)
            
            # زر فتح مجلد النسخ الاحتياطية
            open_folder_btn = QPushButton("فتح مجلد النسخ الاحتياطية")
            open_folder_btn.setObjectName("secondaryButton")
            open_folder_btn.setMinimumHeight(30)
            open_folder_btn.clicked.connect(self.open_backup_folder)
            
            # زر إنشاء نسخة احتياطية محلية
            create_local_backup_btn = QPushButton("إنشاء نسخة احتياطية محلية")
            create_local_backup_btn.setObjectName("primaryButton")
            create_local_backup_btn.setMinimumHeight(30)
            create_local_backup_btn.clicked.connect(self.create_local_backup)
            
            # زر عرض النسخ الاحتياطية المحلية
            view_local_backups_btn = QPushButton("عرض النسخ الاحتياطية المحلية")
            view_local_backups_btn.setObjectName("secondaryButton")
            view_local_backups_btn.setMinimumHeight(30)
            view_local_backups_btn.clicked.connect(self.view_local_backups)
            
            # إضافة العناصر للتخطيط
            backup_layout.addWidget(backup_path_label, 0, 0)
            backup_layout.addWidget(self.backup_path_display, 1, 0, 1, 2)
            backup_layout.addWidget(select_path_btn, 2, 0)
            backup_layout.addWidget(open_folder_btn, 2, 1)
            backup_layout.addWidget(create_local_backup_btn, 3, 0)
            backup_layout.addWidget(view_local_backups_btn, 3, 1)
            
            # إضافة مساحة مرنة
            backup_layout.setColumnStretch(2, 1)
            
            backup_group.setLayout(backup_layout)
            layout.addWidget(backup_group)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم النسخ الاحتياطي المحلي: {e}")
    
    def open_advanced_settings(self):
        """فتح نافذة اعدادات المدارس المتقدمة"""
        try:
            from .advanced_settings_dialog import show_advanced_settings
            show_advanced_settings(self)
        except Exception as e:
            logging.error(f"خطأ في فتح اعدادات المدارس المتقدمة: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في فتح اعدادات المدارس المتقدمة: {str(e)}")
    
    def change_font_size(self):
        """تغيير حجم الخط في الصفحة"""
        try:
            selected_size = self.font_size_combo.currentText()
            
            if selected_size != self.current_font_size:
                self.current_font_size = selected_size
                
                # إعادة إعداد التنسيقات
                self.setup_styles()
                
                # حفظ حجم الخط الجديد في إعدادات UI
                success = ui_settings_manager.set_font_size("settings", selected_size)
                
                log_user_action(f"تغيير حجم الخط إلى: {selected_size}")
                
                # إجبار إعادة رسم الصفحة
                self.update()
                
                # تحديث القائمة المنسدلة
                self.update_font_size_combo()
                
        except Exception as e:
            logging.error(f"خطأ في تغيير حجم الخط: {e}")
    
    def update_font_size_combo(self):
        """تحديث القائمة المنسدلة لحجم الخط"""
        try:
            if hasattr(self, 'font_size_combo'):
                self.font_size_combo.blockSignals(True)  # منع إرسال الإشارات أثناء التحديث
                self.font_size_combo.setCurrentText(self.current_font_size)
                self.font_size_combo.blockSignals(False)  # إعادة تفعيل الإشارات
        except Exception as e:
            logging.error(f"خطأ في تحديث القائمة المنسدلة: {e}")
    
    def select_backup_path(self):
        """اختيار مسار النسخ الاحتياطي المحلي"""
        try:
            # فتح نافذة اختيار المجلد
            folder_path = QFileDialog.getExistingDirectory(
                self,
                "اختيار مجلد النسخ الاحتياطي",
                "",  # مسار افتراضي فارغ
                QFileDialog.ShowDirsOnly
            )
            
            if folder_path:
                # حفظ المسار في قاعدة البيانات
                if self.save_backup_path(folder_path):
                    # تحديث العرض
                    self.backup_path_display.setText(folder_path)
                    QMessageBox.information(self, "نجح", "تم حفظ مسار النسخ الاحتياطي بنجاح")
                    log_user_action(f"تم تحديد مسار النسخ الاحتياطي المحلي: {folder_path}")
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في حفظ مسار النسخ الاحتياطي")
            
        except Exception as e:
            logging.error(f"خطأ في اختيار مسار النسخ الاحتياطي: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في اختيار المسار: {str(e)}")
    
    def open_backup_folder(self):
        """فتح مجلد النسخ الاحتياطية"""
        try:
            # الحصول على المسار المحفوظ
            backup_path = self.get_backup_path()
            
            if backup_path and os.path.exists(backup_path):
                # فتح المجلد باستخدام مستكشف الملفات
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    # استخدام os.startfile لفتح المجلد بشكل صحيح في Windows
                    os.startfile(backup_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", backup_path])
                else:  # Linux
                    subprocess.run(["xdg-open", backup_path])
                
                log_user_action(f"تم فتح مجلد النسخ الاحتياطية: {backup_path}")
            else:
                QMessageBox.warning(self, "تحذير", "لم يتم تحديد مسار صحيح للنسخ الاحتياطي أو المجلد غير موجود")
            
        except Exception as e:
            logging.error(f"خطأ في فتح مجلد النسخ الاحتياطية: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح المجلد: {str(e)}")
    
    def save_backup_path(self, path: str) -> bool:
        """حفظ مسار النسخ الاحتياطي في قاعدة البيانات"""
        try:
            # استخدام execute_update لحفظ في app_settings
            query = """
                INSERT OR REPLACE INTO app_settings (setting_key, setting_value)
                VALUES (?, ?)
            """
            db_manager.execute_update(query, ("local_backup_path", path))
            return True
        except Exception as e:
            logging.error(f"خطأ في حفظ مسار النسخ الاحتياطي: {e}")
            return False
    
    def get_backup_path(self) -> str:
        """الحصول على مسار النسخ الاحتياطي من قاعدة البيانات"""
        try:
            query = "SELECT setting_value FROM app_settings WHERE setting_key = ?"
            result = db_manager.execute_fetch_one(query, ("local_backup_path",))
            return result[0] if result else ""
        except Exception as e:
            logging.error(f"خطأ في الحصول على مسار النسخ الاحتياطي: {e}")
            return ""
    
    def create_local_backup(self):
        """إنشاء نسخة احتياطية محلية"""
        try:
            # الحصول على المسار المحفوظ
            backup_path = self.get_backup_path()
            
            if not backup_path:
                QMessageBox.warning(self, "تحذير", "يرجى تحديد مسار النسخ الاحتياطي أولاً")
                return
            
            if not os.path.exists(backup_path):
                QMessageBox.warning(self, "تحذير", "مسار النسخ الاحتياطي غير موجود")
                return
            
            # إنشاء حوار لإدخال الوصف
            from PyQt5.QtWidgets import QInputDialog
            description, ok = QInputDialog.getText(
                self,
                "وصف النسخة الاحتياطية",
                "أدخل وصفاً للنسخة الاحتياطية (اختياري):"
            )
            
            if not ok:
                return
            
            # إنشاء النسخة الاحتياطية
            from core.backup.local_backup_manager import local_backup_manager
            success, message = local_backup_manager.create_local_backup(backup_path, description)
            
            if success:
                QMessageBox.information(self, "نجح", message)
                log_user_action(f"تم إنشاء نسخة احتياطية محلية: {message}")
            else:
                QMessageBox.critical(self, "خطأ", message)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء النسخة الاحتياطية المحلية: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في إنشاء النسخة الاحتياطية: {str(e)}")
    
    def view_local_backups(self):
        """عرض النسخ الاحتياطية المحلية"""
        try:
            # الحصول على المسار المحفوظ
            backup_path = self.get_backup_path()
            
            if not backup_path:
                QMessageBox.warning(self, "تحذير", "يرجى تحديد مسار النسخ الاحتياطي أولاً")
                return
            
            if not os.path.exists(backup_path):
                QMessageBox.warning(self, "تحذير", "مسار النسخ الاحتياطي غير موجود")
                return
            
            # الحصول على قائمة النسخ الاحتياطية
            from core.backup.local_backup_manager import local_backup_manager
            backups = local_backup_manager.list_local_backups(backup_path)
            
            if not backups:
                QMessageBox.information(self, "معلومات", "لا توجد نسخ احتياطية محلية في المسار المحدد")
                return
            
            # إنشاء نافذة لعرض النسخ الاحتياطية
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton
            
            dialog = QDialog(self)
            dialog.setWindowTitle("النسخ الاحتياطية المحلية")
            dialog.setModal(True)
            dialog.resize(800, 400)
            
            layout = QVBoxLayout(dialog)
            
            # جدول النسخ الاحتياطية
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["التاريخ", "الوصف", "الحجم", "اسم الملف"])
            table.setAlternatingRowColors(True)
            
            # ملء الجدول
            table.setRowCount(len(backups))
            for row, backup in enumerate(backups):
                table.setItem(row, 0, QTableWidgetItem(backup.get('date', 'غير محدد')))
                table.setItem(row, 1, QTableWidgetItem(backup.get('description', 'بدون وصف')))
                table.setItem(row, 2, QTableWidgetItem(f"{backup.get('file_size', 0)} بايت"))
                table.setItem(row, 3, QTableWidgetItem(backup.get('filename', '')))
            
            # ضبط عرض الأعمدة
            table.resizeColumnsToContents()
            
            layout.addWidget(table)
            
            # أزرار التحكم
            buttons_layout = QHBoxLayout()
            
            restore_btn = QPushButton("استعادة المحدد")
            restore_btn.clicked.connect(lambda: self.restore_selected_backup(table, backups, dialog))
            
            close_btn = QPushButton("إغلاق")
            close_btn.clicked.connect(dialog.accept)
            
            buttons_layout.addWidget(restore_btn)
            buttons_layout.addStretch()
            buttons_layout.addWidget(close_btn)
            
            layout.addLayout(buttons_layout)
            
            dialog.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض النسخ الاحتياطية المحلية: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في عرض النسخ الاحتياطية: {str(e)}")
    
    def restore_selected_backup(self, table, backups, dialog):
        """استعادة النسخة الاحتياطية المحددة"""
        try:
            current_row = table.currentRow()
            if current_row < 0:
                QMessageBox.warning(dialog, "تحذير", "يرجى تحديد نسخة احتياطية للاستعادة")
                return
            
            backup = backups[current_row]
            backup_file_path = backup.get('file_path', '')
            
            if not backup_file_path:
                QMessageBox.critical(dialog, "خطأ", "مسار ملف النسخة الاحتياطية غير صحيح")
                return
            
            # تأكيد الاستعادة
            reply = QMessageBox.question(
                dialog,
                "تأكيد الاستعادة",
                "هل أنت متأكد من استعادة هذه النسخة الاحتياطية؟\nسيتم استبدال قاعدة البيانات الحالية.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                from core.backup.local_backup_manager import local_backup_manager
                success, message = local_backup_manager.restore_local_backup(backup_file_path)
                
                if success:
                    QMessageBox.information(dialog, "نجح", message)
                    log_user_action(f"تم استعادة نسخة احتياطية محلية: {backup.get('filename', '')}")
                    dialog.accept()
                else:
                    QMessageBox.critical(dialog, "خطأ", message)
            
        except Exception as e:
            logging.error(f"خطأ في استعادة النسخة الاحتياطية: {e}")
            QMessageBox.critical(dialog, "خطأ", f"حدث خطأ في الاستعادة: {str(e)}")
    
    def setup_styles(self):
        """إعداد أنماط الصفحة"""
        try:
            # استخدام FontSizeManager لإنشاء CSS
            style = FontSizeManager.generate_css_styles(self.current_font_size)
            
            # تطبيق التنسيقات على الصفحة
            self.setStyleSheet(style)
            
            # إجبار إعادة رسم جميع المكونات
            self.update()
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الأنماط: {e}")
