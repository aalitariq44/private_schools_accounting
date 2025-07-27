#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إضافة مدرسة جديدة
"""

import logging
import json
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QCheckBox, QGroupBox,
    QFileDialog, QMessageBox, QFrame, QWidget, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon

import config
from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation


class AddSchoolDialog(QDialog):
    """نافذة إضافة مدرسة جديدة"""
    
    # إشارة عند إضافة مدرسة بنجاح
    school_added = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logo_path = None
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        
        log_user_action("فتح نافذة إضافة مدرسة")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # إعداد النافذة
            self.setWindowTitle("إضافة مدرسة جديدة")
            self.setFixedSize(600, 700)
            self.setModal(True)
            self.setLayoutDirection(Qt.RightToLeft)
            
            # التخطيط الرئيسي
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(15)
            
            # عنوان النافذة
            self.create_header(main_layout)
            
            # منطقة التمرير للنموذج
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            form_widget = QWidget()
            form_layout = QVBoxLayout(form_widget)
            
            # المعلومات الأساسية
            self.create_basic_info_section(form_layout)
            
            # معلومات الاتصال
            self.create_contact_info_section(form_layout)
            
            # نوع المدرسة
            self.create_school_type_section(form_layout)
            
            # الشعار
            self.create_logo_section(form_layout)
            
            scroll_area.setWidget(form_widget)
            main_layout.addWidget(scroll_area)
            
            # الأزرار
            self.create_buttons(main_layout)
            
            self.setLayout(main_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة إضافة المدرسة: {e}")
            raise
    
    def create_header(self, layout):
        """إنشاء رأس النافذة"""
        try:
            header_frame = QFrame()
            header_frame.setObjectName("headerFrame")
            
            header_layout = QHBoxLayout(header_frame)
            header_layout.setContentsMargins(15, 15, 15, 15)
            
            # أيقونة
            icon_label = QLabel()
            icon_label.setFixedSize(48, 48)
            icon_label.setStyleSheet("""
                QLabel {
                    background-color: #3498DB;
                    border-radius: 24px;
                    border: 3px solid #2980B9;
                }
            """)
            header_layout.addWidget(icon_label)
            
            # العنوان والوصف
            text_layout = QVBoxLayout()
            
            title_label = QLabel("إضافة مدرسة جديدة")
            title_label.setObjectName("headerTitle")
            text_layout.addWidget(title_label)
            
            desc_label = QLabel("أدخل معلومات المدرسة الجديدة")
            desc_label.setObjectName("headerDesc")
            text_layout.addWidget(desc_label)
            
            header_layout.addLayout(text_layout)
            header_layout.addStretch()
            
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء رأس النافذة: {e}")
    
    def create_basic_info_section(self, layout):
        """إنشاء قسم المعلومات الأساسية"""
        try:
            group = QGroupBox("المعلومات الأساسية")
            group.setObjectName("formGroup")
            
            grid_layout = QGridLayout(group)
            grid_layout.setSpacing(10)
            
            # الاسم بالعربية
            name_ar_label = QLabel("اسم المدرسة بالعربية *:")
            name_ar_label.setObjectName("fieldLabel")
            self.name_ar_input = QLineEdit()
            self.name_ar_input.setObjectName("requiredInput")
            self.name_ar_input.setPlaceholderText("مثال: مدرسة النجاح الأهلية")
            
            grid_layout.addWidget(name_ar_label, 0, 0)
            grid_layout.addWidget(self.name_ar_input, 0, 1)
            
            # الاسم بالإنجليزية
            name_en_label = QLabel("اسم المدرسة بالإنجليزية:")
            name_en_label.setObjectName("fieldLabel")
            self.name_en_input = QLineEdit()
            self.name_en_input.setObjectName("normalInput")
            self.name_en_input.setPlaceholderText("Example: Success Private School")
            
            grid_layout.addWidget(name_en_label, 1, 0)
            grid_layout.addWidget(self.name_en_input, 1, 1)
            
            # اسم المدير
            principal_label = QLabel("اسم المدير *:")
            principal_label.setObjectName("fieldLabel")
            self.principal_input = QLineEdit()
            self.principal_input.setObjectName("requiredInput")
            self.principal_input.setPlaceholderText("مثال: أحمد محمد علي")
            
            grid_layout.addWidget(principal_label, 2, 0)
            grid_layout.addWidget(self.principal_input, 2, 1)
            
            layout.addWidget(group)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم المعلومات الأساسية: {e}")
    
    def create_contact_info_section(self, layout):
        """إنشاء قسم معلومات الاتصال"""
        try:
            group = QGroupBox("معلومات الاتصال")
            group.setObjectName("formGroup")
            
            grid_layout = QGridLayout(group)
            grid_layout.setSpacing(10)
            
            # رقم الهاتف
            phone_label = QLabel("رقم الهاتف:")
            phone_label.setObjectName("fieldLabel")
            self.phone_input = QLineEdit()
            self.phone_input.setObjectName("normalInput")
            self.phone_input.setPlaceholderText("مثال: 07901234567")
            
            grid_layout.addWidget(phone_label, 0, 0)
            grid_layout.addWidget(self.phone_input, 0, 1)
            
            # العنوان
            address_label = QLabel("عنوان المدرسة:")
            address_label.setObjectName("fieldLabel")
            self.address_input = QTextEdit()
            self.address_input.setObjectName("normalInput")
            self.address_input.setPlaceholderText("مثال: بغداد - الكرادة - شارع الجامعات")
            self.address_input.setMaximumHeight(80)
            
            grid_layout.addWidget(address_label, 1, 0)
            grid_layout.addWidget(self.address_input, 1, 1)
            
            layout.addWidget(group)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم معلومات الاتصال: {e}")
    
    def create_school_type_section(self, layout):
        """إنشاء قسم نوع المدرسة"""
        try:
            group = QGroupBox("نوع المدرسة *")
            group.setObjectName("formGroup")
            
            types_layout = QVBoxLayout(group)
            
            # نص توضيحي
            info_label = QLabel("اختر نوع أو أكثر من أنواع المدارس:")
            info_label.setObjectName("infoLabel")
            types_layout.addWidget(info_label)
            
            # خيارات نوع المدرسة
            self.primary_checkbox = QCheckBox("ابتدائية (الصفوف 1-6)")
            self.primary_checkbox.setObjectName("typeCheckbox")
            
            self.middle_checkbox = QCheckBox("متوسطة (الصفوف 1-3 متوسط)")
            self.middle_checkbox.setObjectName("typeCheckbox")
            
            self.high_checkbox = QCheckBox("إعدادية (الصفوف 4-6 إعدادي)")
            self.high_checkbox.setObjectName("typeCheckbox")
            
            types_layout.addWidget(self.primary_checkbox)
            types_layout.addWidget(self.middle_checkbox)
            types_layout.addWidget(self.high_checkbox)
            
            # رسالة التحقق
            self.type_validation_label = QLabel()
            self.type_validation_label.setObjectName("validationLabel")
            types_layout.addWidget(self.type_validation_label)
            
            layout.addWidget(group)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم نوع المدرسة: {e}")
    
    def create_logo_section(self, layout):
        """إنشاء قسم الشعار"""
        try:
            group = QGroupBox("شعار المدرسة")
            group.setObjectName("formGroup")
            
            logo_layout = QVBoxLayout(group)
            
            # منطقة عرض الشعار
            logo_frame = QFrame()
            logo_frame.setObjectName("logoFrame")
            logo_frame.setFixedHeight(150)
            
            logo_frame_layout = QVBoxLayout(logo_frame)
            logo_frame_layout.setAlignment(Qt.AlignCenter)
            
            self.logo_label = QLabel("لا يوجد شعار")
            self.logo_label.setAlignment(Qt.AlignCenter)
            self.logo_label.setObjectName("logoLabel")
            logo_frame_layout.addWidget(self.logo_label)
            
            logo_layout.addWidget(logo_frame)
            
            # أزرار إدارة الشعار
            logo_buttons_layout = QHBoxLayout()
            
            self.select_logo_button = QPushButton("اختيار شعار")
            self.select_logo_button.setObjectName("logoButton")
            self.select_logo_button.clicked.connect(self.select_logo)
            
            self.remove_logo_button = QPushButton("إزالة الشعار")
            self.remove_logo_button.setObjectName("logoButton")
            self.remove_logo_button.clicked.connect(self.remove_logo)
            self.remove_logo_button.setEnabled(False)
            
            logo_buttons_layout.addWidget(self.select_logo_button)
            logo_buttons_layout.addWidget(self.remove_logo_button)
            logo_buttons_layout.addStretch()
            
            logo_layout.addLayout(logo_buttons_layout)
            
            # نص توضيحي
            logo_info = QLabel("الأنواع المدعومة: PNG, JPG, JPEG (الحد الأقصى: 2 ميجابايت)")
            logo_info.setObjectName("infoLabel")
            logo_layout.addWidget(logo_info)
            
            layout.addWidget(group)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الشعار: {e}")
    
    def create_buttons(self, layout):
        """إنشاء أزرار النافذة"""
        try:
            buttons_frame = QFrame()
            buttons_frame.setObjectName("buttonsFrame")
            
            buttons_layout = QHBoxLayout(buttons_frame)
            buttons_layout.setContentsMargins(0, 10, 0, 0)
            
            # زر الإلغاء
            self.cancel_button = QPushButton("إلغاء")
            self.cancel_button.setObjectName("cancelButton")
            self.cancel_button.clicked.connect(self.reject)
            
            # زر الحفظ
            self.save_button = QPushButton("حفظ المدرسة")
            self.save_button.setObjectName("saveButton")
            self.save_button.clicked.connect(self.save_school)
            
            # رسالة التحقق العامة
            self.validation_message = QLabel()
            self.validation_message.setObjectName("validationMessage")
            self.validation_message.setWordWrap(True)
            
            buttons_layout.addWidget(self.validation_message)
            buttons_layout.addStretch()
            buttons_layout.addWidget(self.cancel_button)
            buttons_layout.addWidget(self.save_button)
            
            layout.addWidget(buttons_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الأزرار: {e}")
    
    def setup_connections(self):
        """ربط الإشارات"""
        try:
            # ربط التحقق من صحة البيانات
            self.name_ar_input.textChanged.connect(self.validate_form)
            self.principal_input.textChanged.connect(self.validate_form)
            self.primary_checkbox.toggled.connect(self.validate_form)
            self.middle_checkbox.toggled.connect(self.validate_form)
            self.high_checkbox.toggled.connect(self.validate_form)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def validate_form(self):
        """التحقق من صحة البيانات"""
        try:
            errors = []
            
            # التحقق من الاسم بالعربية
            if not self.name_ar_input.text().strip():
                errors.append("اسم المدرسة بالعربية مطلوب")
            
            # التحقق من اسم المدير
            if not self.principal_input.text().strip():
                errors.append("اسم المدير مطلوب")
            
            # التحقق من نوع المدرسة
            if not (self.primary_checkbox.isChecked() or 
                    self.middle_checkbox.isChecked() or 
                    self.high_checkbox.isChecked()):
                errors.append("يجب اختيار نوع واحد على الأقل للمدرسة")
            
            # عرض الأخطاء أو مسحها
            if errors:
                self.validation_message.setText("• " + "\n• ".join(errors))
                self.validation_message.setStyleSheet("color: #E74C3C;")
                self.save_button.setEnabled(False)
            else:
                self.validation_message.clear()
                self.save_button.setEnabled(True)
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من صحة النموذج: {e}")
    
    def select_logo(self):
        """اختيار شعار المدرسة"""
        try:
            file_dialog = QFileDialog(self)
            file_dialog.setNameFilter("ملفات الصور (*.png *.jpg *.jpeg)")
            file_dialog.setFileMode(QFileDialog.ExistingFile)
            file_dialog.setViewMode(QFileDialog.Detail)
            
            if file_dialog.exec_():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    logo_path = selected_files[0]
                    
                    # التحقق من حجم الملف (2 ميجابايت كحد أقصى)
                    file_size = os.path.getsize(logo_path)
                    if file_size > 2 * 1024 * 1024:  # 2 ميجابايت
                        QMessageBox.warning(
                            self,
                            "حجم كبير",
                            "حجم الملف كبير جداً. الحد الأقصى المسموح 2 ميجابايت."
                        )
                        return
                    
                    # تحميل وعرض الصورة
                    pixmap = QPixmap(logo_path)
                    if not pixmap.isNull():
                        # تغيير حجم الصورة للعرض
                        scaled_pixmap = pixmap.scaled(
                            120, 120, 
                            Qt.KeepAspectRatio, 
                            Qt.SmoothTransformation
                        )
                        
                        self.logo_label.setPixmap(scaled_pixmap)
                        self.logo_path = logo_path
                        self.remove_logo_button.setEnabled(True)
                        
                        log_user_action("تم اختيار شعار للمدرسة", os.path.basename(logo_path))
                    else:
                        QMessageBox.warning(
                            self,
                            "ملف غير صالح",
                            "الملف المحدد ليس صورة صالحة."
                        )
            
        except Exception as e:
            logging.error(f"خطأ في اختيار الشعار: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في اختيار الشعار: {str(e)}")
    
    def remove_logo(self):
        """إزالة شعار المدرسة"""
        try:
            self.logo_label.clear()
            self.logo_label.setText("لا يوجد شعار")
            self.logo_path = None
            self.remove_logo_button.setEnabled(False)
            
            log_user_action("تم إزالة شعار المدرسة")
            
        except Exception as e:
            logging.error(f"خطأ في إزالة الشعار: {e}")
    
    def get_school_types(self):
        """الحصول على أنواع المدرسة المحددة"""
        try:
            types = []
            
            if self.primary_checkbox.isChecked():
                types.append("ابتدائية")
            
            if self.middle_checkbox.isChecked():
                types.append("متوسطة")
            
            if self.high_checkbox.isChecked():
                types.append("إعدادية")
            
            return types
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على أنواع المدرسة: {e}")
            return []
    
    def copy_logo_to_uploads(self):
        """نسخ الشعار إلى مجلد الرفوعات"""
        try:
            if not self.logo_path:
                return None
            
            # إنشاء مجلد الشعارات إذا لم يوجد
            logos_dir = config.UPLOADS_DIR / "school_logos"
            logos_dir.mkdir(exist_ok=True)
            
            # إنشاء اسم فريد للملف
            import uuid
            from pathlib import Path
            
            file_extension = Path(self.logo_path).suffix
            new_filename = f"school_logo_{uuid.uuid4().hex[:8]}{file_extension}"
            new_path = logos_dir / new_filename
            
            # نسخ الملف
            import shutil
            shutil.copy2(self.logo_path, new_path)
            
            return str(new_path.relative_to(config.BASE_DIR))
            
        except Exception as e:
            logging.error(f"خطأ في نسخ الشعار: {e}")
            return None
    
    def save_school(self):
        """حفظ المدرسة في قاعدة البيانات"""
        try:
            # التحقق النهائي من البيانات
            if not self.name_ar_input.text().strip():
                QMessageBox.warning(self, "خطأ", "اسم المدرسة بالعربية مطلوب")
                return
            
            if not self.principal_input.text().strip():
                QMessageBox.warning(self, "خطأ", "اسم المدير مطلوب")
                return
            
            school_types = self.get_school_types()
            if not school_types:
                QMessageBox.warning(self, "خطأ", "يجب اختيار نوع واحد على الأقل للمدرسة")
                return
            
            # نسخ الشعار إذا وُجد
            logo_path = self.copy_logo_to_uploads()
            
            # تحضير البيانات
            school_data = {
                'name_ar': self.name_ar_input.text().strip(),
                'name_en': self.name_en_input.text().strip() or None,
                'principal_name': self.principal_input.text().strip(),
                'phone': self.phone_input.text().strip() or None,
                'address': self.address_input.toPlainText().strip() or None,
                'school_types': ",".join(school_types), # Store as comma-separated string
                'logo_path': logo_path
            }
            
            # إدخال البيانات في قاعدة البيانات
            insert_query = """
                INSERT INTO schools (name_ar, name_en, principal_name, phone, address, school_types, logo_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            school_id = db_manager.execute_insert(
                insert_query,
                (school_data['name_ar'], school_data['name_en'], school_data['principal_name'],
                 school_data['phone'], school_data['address'], school_data['school_types'],
                 school_data['logo_path'])
            )
            
            if school_id:
                # إضافة المعرف للبيانات
                school_data['id'] = school_id
                
                # إرسال إشارة النجاح
                self.school_added.emit(school_data)
                
                # تسجيل العملية
                log_database_operation("إدخال", "schools", f"مدرسة جديدة: {school_data['name_ar']}")
                log_user_action("تم إضافة مدرسة جديدة", school_data['name_ar'])
                
                # رسالة نجاح
                QMessageBox.information(
                    self,
                    "تم الحفظ",
                    f"تم إضافة المدرسة '{school_data['name_ar']}' بنجاح"
                )
                
                self.accept()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في حفظ المدرسة")
            
        except Exception as e:
            logging.error(f"خطأ في حفظ المدرسة: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ المدرسة: {str(e)}")
    
    def setup_styles(self):
        """إعداد تنسيقات النافذة"""
        try:
            style = """
                QDialog {
                    background-color: #F8F9FA;
                    font-family: 'Segoe UI', Tahoma, Arial;
                }
                
                #headerFrame {
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid #E9ECEF;
                    margin-bottom: 10px;
                }
                
                #headerTitle {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin-bottom: 5px;
                }
                
                #headerDesc {
                    font-size: 18px;
                    color: #7F8C8D;
                }
                
                #formGroup {
                    font-weight: bold;
                    color: #2C3E50;
                    border: 1px solid #BDC3C7;
                    border-radius: 6px;
                    margin-bottom: 10px;
                    padding: 10px;
                    background-color: white;
                }
                
                #fieldLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin-bottom: 5px;
                }
                
                #requiredInput {
                    padding: 8px 12px;
                    border: 2px solid #3498DB;
                    border-radius: 4px;
                    font-size: 18px;
                    background-color: white;
                }
                
                #requiredInput:focus {
                    border-color: #2980B9;
                    outline: none;
                }
                
                #normalInput {
                    padding: 8px 12px;
                    border: 1px solid #BDC3C7;
                    border-radius: 4px;
                    font-size: 18px;
                    background-color: white;
                }
                
                #normalInput:focus {
                    border-color: #3498DB;
                    outline: none;
                }
                
                #typeCheckbox {
                    font-size: 18px;
                    color: #2C3E50;
                    spacing: 8px;
                }
                
                #typeCheckbox::indicator {
                    width: 18px;
                    height: 18px;
                }
                
                #typeCheckbox::indicator:unchecked {
                    border: 2px solid #BDC3C7;
                    border-radius: 3px;
                    background-color: white;
                }
                
                #typeCheckbox::indicator:checked {
                    border: 2px solid #27AE60;
                    border-radius: 3px;
                    background-color: #27AE60;
                    image: url(none);
                }
                
                #logoFrame {
                    border: 2px dashed #BDC3C7;
                    border-radius: 6px;
                    background-color: #FAFAFA;
                }
                
                #logoLabel {
                    color: #7F8C8D;
                    font-size: 12px;
                }
                
                #logoButton {
                    background-color: #95A5A6;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                }
                
                #logoButton:hover {
                    background-color: #7F8C8D;
                }
                
                #infoLabel {
                    font-size: 11px;
                    color: #7F8C8D;
                    font-style: italic;
                }
                
                #validationLabel, #validationMessage {
                    font-size: 11px;
                    font-weight: bold;
                    margin-top: 5px;
                }
                
                #buttonsFrame {
                    border-top: 1px solid #E9ECEF;
                    margin-top: 10px;
                }
                
                #saveButton {
                    background-color: #27AE60;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-size: 18px;
                    font-weight: bold;
                    min-width: 120px;
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
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-size: 18px;
                    font-weight: bold;
                    min-width: 80px;
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
            if event.key() == Qt.Key_Escape:
                self.reject()
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                if self.save_button.isEnabled():
                    self.save_school()
            else:
                super().keyPressEvent(event)
                
        except Exception as e:
            logging.error(f"خطأ في معالجة ضغط المفاتيح: {e}")
            super().keyPressEvent(event)
