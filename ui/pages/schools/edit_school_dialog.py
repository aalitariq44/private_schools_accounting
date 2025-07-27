#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة تعديل مدرسة موجودة
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


class EditSchoolDialog(QDialog):
    """نافذة تعديل مدرسة موجودة"""
    
    # إشارة عند تعديل مدرسة بنجاح
    school_updated = pyqtSignal(dict)
    
    def __init__(self, school_data, parent=None):
        super().__init__(parent)
        self.school_data = school_data
        self.original_logo_path = school_data.get('logo_path')
        self.new_logo_path = None
        self.logo_changed = False
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_school_data()
        
        log_user_action("فتح نافذة تعديل مدرسة", school_data.get('name_ar', ''))
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # إعداد النافذة
            self.setWindowTitle("تعديل بيانات المدرسة")
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
            logging.error(f"خطأ في إعداد واجهة تعديل المدرسة: {e}")
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
                    background-color: #F39C12;
                    border-radius: 24px;
                    border: 3px solid #E67E22;
                }
            """)
            header_layout.addWidget(icon_label)
            
            # العنوان والوصف
            text_layout = QVBoxLayout()
            
            title_label = QLabel("تعديل بيانات المدرسة")
            title_label.setObjectName("headerTitle")
            text_layout.addWidget(title_label)
            
            desc_label = QLabel(f"تعديل معلومات مدرسة: {self.school_data.get('name_ar', '')}")
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
            
            self.select_logo_button = QPushButton("تغيير الشعار")
            self.select_logo_button.setObjectName("logoButton")
            self.select_logo_button.clicked.connect(self.select_logo)
            
            self.remove_logo_button = QPushButton("إزالة الشعار")
            self.remove_logo_button.setObjectName("logoButton")
            self.remove_logo_button.clicked.connect(self.remove_logo)
            
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
            self.save_button = QPushButton("حفظ التعديلات")
            self.save_button.setObjectName("saveButton")
            self.save_button.clicked.connect(self.save_changes)
            
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
    
    def load_school_data(self):
        """تحميل بيانات المدرسة إلى النموذج"""
        try:
            # المعلومات الأساسية
            self.name_ar_input.setText(self.school_data.get('name_ar', ''))
            self.name_en_input.setText(self.school_data.get('name_en', ''))
            self.principal_input.setText(self.school_data.get('principal_name', ''))
            
            # معلومات الاتصال
            self.phone_input.setText(self.school_data.get('phone', ''))
            self.address_input.setPlainText(self.school_data.get('address', ''))
            
            # أنواع المدرسة
            school_types_str = self.school_data.get('school_types', '[]')
            try:
                school_types = json.loads(school_types_str) if school_types_str else []
            except json.JSONDecodeError:
                school_types = []
            
            self.primary_checkbox.setChecked("ابتدائية" in school_types)
            self.middle_checkbox.setChecked("متوسطة" in school_types)
            self.high_checkbox.setChecked("إعدادية" in school_types)
            
            # الشعار
            self.load_current_logo()
            
            # التحقق الأولي من النموذج
            self.validate_form()

            # تعطيل تعديل نوع المدرسة لمنع تغييره
            self.primary_checkbox.setEnabled(False)
            self.middle_checkbox.setEnabled(False)
            self.high_checkbox.setEnabled(False)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات المدرسة: {e}")
    
    def load_current_logo(self):
        """تحميل الشعار الحالي"""
        try:
            logo_path = self.school_data.get('logo_path')
            if logo_path:
                # تكوين المسار الكامل
                full_path = config.BASE_DIR / logo_path
                
                if full_path.exists():
                    pixmap = QPixmap(str(full_path))
                    if not pixmap.isNull():
                        # تغيير حجم الصورة للعرض
                        scaled_pixmap = pixmap.scaled(
                            120, 120, 
                            Qt.KeepAspectRatio, 
                            Qt.SmoothTransformation
                        )
                        
                        self.logo_label.setPixmap(scaled_pixmap)
                        self.remove_logo_button.setEnabled(True)
                        return
            
            # لا يوجد شعار أو الملف غير موجود
            self.logo_label.setText("لا يوجد شعار")
            self.remove_logo_button.setEnabled(False)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الشعار الحالي: {e}")
            self.logo_label.setText("خطأ في تحميل الشعار")
            self.remove_logo_button.setEnabled(False)
    
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
        """اختيار شعار جديد للمدرسة"""
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
                        self.new_logo_path = logo_path
                        self.logo_changed = True
                        self.remove_logo_button.setEnabled(True)
                        
                        log_user_action("تم اختيار شعار جديد للمدرسة", os.path.basename(logo_path))
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
            self.new_logo_path = None
            self.logo_changed = True
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
    
    def copy_new_logo_to_uploads(self):
        """نسخ الشعار الجديد إلى مجلد الرفوعات"""
        try:
            if not self.new_logo_path:
                return None
            
            # إنشاء مجلد الشعارات إذا لم يوجد
            logos_dir = config.UPLOADS_DIR / "school_logos"
            logos_dir.mkdir(exist_ok=True)
            
            # إنشاء اسم فريد للملف
            import uuid
            from pathlib import Path
            
            file_extension = Path(self.new_logo_path).suffix
            new_filename = f"school_logo_{uuid.uuid4().hex[:8]}{file_extension}"
            new_path = logos_dir / new_filename
            
            # نسخ الملف
            import shutil
            shutil.copy2(self.new_logo_path, new_path)
            
            return str(new_path.relative_to(config.BASE_DIR))
            
        except Exception as e:
            logging.error(f"خطأ في نسخ الشعار الجديد: {e}")
            return None
    
    def delete_old_logo(self):
        """حذف الشعار القديم"""
        try:
            old_logo_path = self.original_logo_path
            if old_logo_path:
                full_path = config.BASE_DIR / old_logo_path
                if full_path.exists():
                    full_path.unlink()
                    log_user_action("تم حذف الشعار القديم", old_logo_path)
                    
        except Exception as e:
            logging.error(f"خطأ في حذف الشعار القديم: {e}")
    
    def save_changes(self):
        """حفظ التعديلات في قاعدة البيانات"""
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
            
            # معالجة الشعار
            final_logo_path = self.original_logo_path
            
            if self.logo_changed:
                if self.new_logo_path:
                    # نسخ الشعار الجديد
                    final_logo_path = self.copy_new_logo_to_uploads()
                    # حذف القديم إذا كان موجوداً ومختلفاً
                    if self.original_logo_path and self.original_logo_path != final_logo_path:
                        self.delete_old_logo()
                else:
                    # إزالة الشعار - حذف القديم
                    if self.original_logo_path:
                        self.delete_old_logo()
                    final_logo_path = None
            
            # تحضير البيانات المحدثة
            updated_data = {
                'id': self.school_data['id'],
                'name_ar': self.name_ar_input.text().strip(),
                'name_en': self.name_en_input.text().strip() or None,
                'principal_name': self.principal_input.text().strip(),
                'phone': self.phone_input.text().strip() or None,
                'address': self.address_input.toPlainText().strip() or None,
                'school_types': json.dumps(school_types, ensure_ascii=False),
                'logo_path': final_logo_path
            }
            
            # تحديث البيانات في قاعدة البيانات
            update_query = """
                UPDATE schools 
                SET name_ar = ?, name_en = ?, principal_name = ?, phone = ?, 
                    address = ?, school_types = ?, logo_path = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            
            affected_rows = db_manager.execute_update(
                update_query,
                (updated_data['name_ar'], updated_data['name_en'], updated_data['principal_name'],
                 updated_data['phone'], updated_data['address'], updated_data['school_types'],
                 updated_data['logo_path'], updated_data['id'])
            )
            
            if affected_rows >= 0:
                # إرسال إشارة النجاح
                self.school_updated.emit(updated_data)
                
                # تسجيل العملية
                log_database_operation("تحديث", "schools", f"مدرسة: {updated_data['name_ar']}")
                log_user_action("تم تحديث بيانات مدرسة", updated_data['name_ar'])
                
                # رسالة نجاح
                QMessageBox.information(
                    self,
                    "تم الحفظ",
                    f"تم تحديث بيانات المدرسة '{updated_data['name_ar']}' بنجاح"
                )
                
                self.accept()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في حفظ التعديلات")
        except Exception as e:
            logging.error(f"خطأ في حفظ التعديلات: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ التعديلات: {str(e)}")
    
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
                    border: 2px solid #F39C12;
                    border-radius: 4px;
                    font-size: 18px;
                    background-color: white;
                }
                
                #requiredInput:focus {
                    border-color: #E67E22;
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
                    border-color: #F39C12;
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
                    border: 2px solid #F39C12;
                    border-radius: 3px;
                    background-color: #F39C12;
                    image: url(none);
                }
                
                #logoFrame {
                    border: 2px dashed #BDC3C7;
                    border-radius: 6px;
                    background-color: #FAFAFA;
                }
                
                #logoLabel {
                    color: #7F8C8D;
                    font-size: 18px;
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
                    background-color: #F39C12;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-size: 18px;
                    font-weight: bold;
                    min-width: 120px;
                }
                
                #saveButton:hover {
                    background-color: #E67E22;
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
            