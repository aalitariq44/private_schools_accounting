#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إضافة مصروف جديد
"""

import logging
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QLabel, QMessageBox, QGroupBox, QFrame
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation


class AddExpenseDialog(QDialog):
    """نافذة إضافة مصروف جديد"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة مصروف جديد")
        self.setModal(True)
        self.resize(550, 700)
        
        self.setup_ui()
        self.setup_styles()
        self.load_schools()
        
        # تركيز على حقل الوصف
        self.title_input.setFocus()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            # رأس النافذة
            self.create_header(layout)
            
            # معلومات المصروف الأساسية
            self.create_basic_info_section(layout)
            
            
            # تفاصيل إضافية
            self.create_additional_details_section(layout)
            
            # أزرار الحفظ والإلغاء
            self.create_buttons_section(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة إضافة المصروف: {e}")
            raise
    
    def create_header(self, layout):
        """إنشاء رأس النافذة"""
        try:
            header_frame = QFrame()
            header_frame.setObjectName("headerFrame")
            
            header_layout = QVBoxLayout(header_frame)
            
            desc_label = QLabel("يرجى ملء جميع الحقول المطلوبة لإضافة المصروف")
            desc_label.setObjectName("dialogDesc")
            desc_label.setStyleSheet("color: black;")
            header_layout.addWidget(desc_label)
            
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء رأس النافذة: {e}")
    
    def create_basic_info_section(self, layout):
        """إنشاء قسم المعلومات الأساسية"""
        try:
            group_box = QGroupBox("المعلومات الأساسية")
            group_box.setObjectName("sectionGroupBox")
            
            form_layout = QFormLayout(group_box)
            form_layout.setContentsMargins(15, 20, 15, 15)
            form_layout.setSpacing(12)
            
            # وصف المصروف
            self.title_input = QLineEdit()
            self.title_input.setObjectName("requiredInput")
            self.title_input.setPlaceholderText("أدخل وصف المصروف...")
            form_layout.addRow("الوصف *:", self.title_input)
            
            # المبلغ
            self.amount_input = QDoubleSpinBox()
            self.amount_input.setObjectName("amountInput")
            self.amount_input.setRange(0.01, 999999999.99)
            self.amount_input.setDecimals(2)
            self.amount_input.setSuffix(" د.ع")
            self.amount_input.setValue(0.0)
            form_layout.addRow("المبلغ *:", self.amount_input)
            
            # المدرسة
            self.school_combo = QComboBox()
            self.school_combo.setObjectName("requiredCombo")
            form_layout.addRow("المدرسة *:", self.school_combo)
            
            # تاريخ المصروف
            self.expense_date = QDateEdit()
            self.expense_date.setObjectName("dateInput")
            self.expense_date.setDate(QDate.currentDate())
            self.expense_date.setCalendarPopup(True)
            form_layout.addRow("التاريخ *:", self.expense_date)
            
            # فئة المصروف
            self.category_combo = QComboBox()
            self.category_combo.setObjectName("requiredCombo")
            self.category_combo.addItems([
                "-- اختر الفئة --", "الرواتب", "المواد التعليمية", "الخدمات", 
                "الصيانة", "الكهرباء والماء", "النظافة", "المكتبية", 
                "النقل", "التأمين", "أخرى"
            ])
            form_layout.addRow("الفئة *:", self.category_combo)
            
            layout.addWidget(group_box)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم المعلومات الأساسية: {e}")
    
    
    def create_additional_details_section(self, layout):
        """إنشاء قسم التفاصيل الإضافية"""
        try:
            group_box = QGroupBox("تفاصيل إضافية")
            group_box.setObjectName("sectionGroupBox")
            
            form_layout = QFormLayout(group_box)
            form_layout.setContentsMargins(15, 20, 15, 15)
            form_layout.setSpacing(12)
            
            
            # الملاحظات
            self.notes_input = QTextEdit()
            self.notes_input.setObjectName("notesInput")
            self.notes_input.setPlaceholderText("أضف أي ملاحظات إضافية حول هذا المصروف...")
            self.notes_input.setMaximumHeight(100)
            form_layout.addRow("الملاحظات:", self.notes_input)
            
            layout.addWidget(group_box)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم التفاصيل الإضافية: {e}")
    
    def create_buttons_section(self, layout):
        """إنشاء قسم الأزرار"""
        try:
            buttons_frame = QFrame()
            buttons_layout = QHBoxLayout(buttons_frame)
            buttons_layout.setContentsMargins(0, 15, 0, 0)
            buttons_layout.setSpacing(10)
            
            buttons_layout.addStretch()
            
            # زر الإلغاء
            self.cancel_button = QPushButton("إلغاء")
            self.cancel_button.setObjectName("cancelButton")
            self.cancel_button.clicked.connect(self.reject)
            buttons_layout.addWidget(self.cancel_button)
            
            # زر الحفظ
            self.save_button = QPushButton("حفظ المصروف")
            self.save_button.setObjectName("saveButton")
            self.save_button.clicked.connect(self.save_expense)
            buttons_layout.addWidget(self.save_button)
            
            layout.addWidget(buttons_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الأزرار: {e}")
    
    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            self.school_combo.clear()
            self.school_combo.addItem("عام", None)  # إضافة خيار عام
            
            # جلب المدارس من قاعدة البيانات
            query = "SELECT id, name_ar FROM schools ORDER BY name_ar"
            schools = db_manager.execute_query(query)
            
            if schools:
                for school in schools:
                    self.school_combo.addItem(school['name_ar'], school['id'])
            else:
                # إذا لم توجد مدارس، يمكن على الأقل إضافة مصروفات عامة
                pass  # الخيار "عام" موجود بالفعل
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.warning(self, "خطأ", f"خطأ في تحميل قائمة المدارس:\n{str(e)}")
    
    def validate_inputs(self):
        """التحقق من صحة البيانات المدخلة"""
        try:
            errors = []
            
            # التحقق من الوصف
            if not self.title_input.text().strip():
                errors.append("يجب إدخال وصف المصروف")
            
            # التحقق من المبلغ
            if self.amount_input.value() <= 0:
                errors.append("يجب إدخال مبلغ أكبر من الصفر")
            
            # لا حاجة للتحقق من المدرسة لأن "عام" خيار صالح
            
            # التحقق من الفئة
            if self.category_combo.currentIndex() == 0:
                errors.append("يجب اختيار فئة المصروف")
            
            return errors
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من البيانات: {e}")
            return [f"خطأ في التحقق من البيانات: {str(e)}"]
    
    def save_expense(self):
        """حفظ بيانات المصروف الجديد"""
        try:
            # التحقق من صحة البيانات
            errors = self.validate_inputs()
            if errors:
                QMessageBox.warning(self, "خطأ في البيانات", "\n".join(errors))
                return
            
            # تحضير البيانات
            expense_data = {
                'school_id': self.school_combo.currentData(),
                'expense_type': self.category_combo.currentText(),
                'amount': self.amount_input.value(),
                'expense_date': self.expense_date.date().toPyDate(),
                'description': self.title_input.text().strip(),
                'notes': self.notes_input.toPlainText().strip() or None
            }
            
            # إدراج البيانات في قاعدة البيانات
            insert_query = """
                INSERT INTO expenses 
                (school_id, expense_type, amount, expense_date, description, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            params = (
                expense_data['school_id'],
                expense_data['expense_type'],
                expense_data['amount'],
                expense_data['expense_date'],
                expense_data['description'],
                expense_data['notes']
            )
            
            # تنفيذ الاستعلام
            result = db_manager.execute_update(insert_query, params)
            
            if result > 0:
                QMessageBox.information(self, "نجح", "تم حفظ المصروف بنجاح")
                log_user_action("إضافة مصروف جديد", "نجح")
                log_database_operation("إدراج مصروف", "نجح")
                self.accept()
            else:
                QMessageBox.warning(self, "خطأ", "لم يتم حفظ المصروف")
                
        except Exception as e:
            logging.error(f"خطأ في حفظ المصروف: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ المصروف:\n{str(e)}")
    
    def setup_styles(self):
        """إعداد تنسيقات النافذة"""
        try:
            style = """
                QDialog {
                    background-color: #F8F9FA;
                    font-family: 'Segoe UI', Tahoma, Arial;
                }
                
                #headerFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #DC3545, stop:1 #C82333);
                    border-radius: 10px;
                    color: white;
                    margin-bottom: 15px;
                }
                
                #dialogTitle {
                    font-size: 20px;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 5px;
                }
                
                #dialogDesc {
                    font-size: 18px;
                    color: #F8E5E5;
                }
                
                #sectionGroupBox {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    background-color: white;
                    border: 2px solid #E9ECEF;
                    border-radius: 8px;
                    margin: 5px 0px;
                    padding-top: 10px;
                }
                
                #requiredInput, #optionalInput {
                    padding: 10px;
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    font-size: 18px;
                    background-color: white;
                }
                
                #requiredInput {
                    border-color: #DC3545;
                }
                
                #requiredInput:focus {
                    border-color: #C82333;
                    outline: none;
                }
                
                #requiredCombo, #optionalCombo {
                    padding: 8px;
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    font-size: 18px;
                    background-color: white;
                    min-height: 20px;
                }
                
                #requiredCombo {
                    border-color: #DC3545;
                }
                
                #amountInput {
                    padding: 10px;
                    border: 2px solid #DC3545;
                    border-radius: 6px;
                    font-size: 18px;
                    background-color: white;
                    font-weight: bold;
                }
                
                #dateInput {
                    padding: 8px;
                    border: 2px solid #DC3545;
                    border-radius: 6px;
                    font-size: 18px;
                    background-color: white;
                }
                
                #notesInput {
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    font-size: 18px;
                    background-color: white;
                    padding: 8px;
                }
                
                #saveButton {
                    background-color: #DC3545;
                    color: white;
                    border: none;
                    padding: 12px 30px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 18px;
                    min-width: 140px;
                }
                
                #saveButton:hover {
                    background-color: #C82333;
                }
                
                #cancelButton {
                    background-color: #6C757D;
                    color: white;
                    border: none;
                    padding: 12px 30px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 18px;
                    min-width: 120px;
                }
                
                #cancelButton:hover {
                    background-color: #5A6268;
                }
                
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                }
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد تنسيقات النافذة: {e}")
