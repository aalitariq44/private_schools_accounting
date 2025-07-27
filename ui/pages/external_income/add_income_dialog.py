#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إضافة وارد خارجي جديد
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


class AddIncomeDialog(QDialog):
    """نافذة إضافة وارد خارجي جديد"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة وارد خارجي جديد")
        self.setModal(True)
        self.resize(500, 600)
        
        self.setup_ui()
        self.setup_styles()
        self.load_schools()
        
        # تركيز على حقل العنوان
        self.title_input.setFocus()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            # رأس النافذة
            self.create_header(layout)
            
            # معلومات الوارد الأساسية
            self.create_basic_info_section(layout)
            
            # تفاصيل إضافية
            self.create_additional_details_section(layout)
            
            # أزرار الحفظ والإلغاء
            self.create_buttons_section(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة إضافة الوارد: {e}")
            raise
    
    def create_header(self, layout):
        """إنشاء رأس النافذة"""
        try:
            header_frame = QFrame()
            header_frame.setObjectName("headerFrame")
            
            header_layout = QVBoxLayout(header_frame)
            header_layout.setContentsMargins(20, 15, 20, 15)
            
            title_label = QLabel("إضافة وارد خارجي جديد")
            title_label.setObjectName("dialogTitle")
            title_label.setStyleSheet("color: black;")
            header_layout.addWidget(title_label)
            
            desc_label = QLabel("يرجى ملء جميع الحقول المطلوبة لإضافة الوارد الخارجي")
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
            
            # عنوان الوارد
            self.title_input = QLineEdit()
            self.title_input.setObjectName("requiredInput")
            self.title_input.setPlaceholderText("أدخل عنوان الوارد...")
            form_layout.addRow("العنوان *:", self.title_input)
            
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
            
            # تاريخ الوارد
            self.income_date = QDateEdit()
            self.income_date.setObjectName("dateInput")
            self.income_date.setDate(QDate.currentDate())
            self.income_date.setCalendarPopup(True)
            form_layout.addRow("التاريخ *:", self.income_date)
            
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
            
            
            # فئة الوارد
            self.category_combo = QComboBox()
            self.category_combo.setObjectName("optionalCombo")
            self.category_combo.addItems([
                "-- اختر الفئة --", "الحانوت", "النقل", "الأنشطة", 
                "التبرعات", "إيجارات", "أخرى"
            ])
            form_layout.addRow("الفئة:", self.category_combo)
            
            # الملاحظات
            self.notes_input = QTextEdit()
            self.notes_input.setObjectName("notesInput")
            self.notes_input.setPlaceholderText("أضف أي ملاحظات إضافية حول هذا الوارد...")
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
            self.save_button = QPushButton("حفظ الوارد")
            self.save_button.setObjectName("saveButton")
            self.save_button.clicked.connect(self.save_income)
            buttons_layout.addWidget(self.save_button)
            
            layout.addWidget(buttons_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الأزرار: {e}")
    
    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            self.school_combo.clear()
            
            # جلب المدارس من قاعدة البيانات
            query = "SELECT id, name_ar FROM schools ORDER BY name_ar"
            schools = db_manager.execute_query(query)
            
            if schools:
                for school in schools:
                    self.school_combo.addItem(school['name_ar'], school['id'])
            else:
                self.school_combo.addItem("لا توجد مدارس", None)
                self.save_button.setEnabled(False)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.warning(self, "خطأ", f"خطأ في تحميل قائمة المدارس:\n{str(e)}")
    
    def validate_inputs(self):
        """التحقق من صحة البيانات المدخلة"""
        try:
            errors = []
            
            # التحقق من العنوان
            if not self.title_input.text().strip():
                errors.append("يجب إدخال عنوان الوارد")
            
            # التحقق من المبلغ
            if self.amount_input.value() <= 0:
                errors.append("يجب إدخال مبلغ أكبر من الصفر")
            
            # التحقق من المدرسة
            if not self.school_combo.currentData():
                errors.append("يجب اختيار المدرسة")
            
            return errors
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من البيانات: {e}")
            return [f"خطأ في التحقق من البيانات: {str(e)}"]
    
    def save_income(self):
        """حفظ بيانات الوارد الجديد"""
        try:
            # التحقق من صحة البيانات
            errors = self.validate_inputs()
            if errors:
                QMessageBox.warning(self, "خطأ في البيانات", "\n".join(errors))
                return
            
            # تحضير البيانات
            income_data = {
                'school_id': self.school_combo.currentData(),
                'title': self.title_input.text().strip(),
                'amount': self.amount_input.value(),
                'category': self.category_combo.currentText() if self.category_combo.currentIndex() > 0 else None,
                'income_date': self.income_date.date().toPyDate(),
                'notes': self.notes_input.toPlainText().strip() or None
            }
            
            # إدراج البيانات في قاعدة البيانات
            insert_query = """
                INSERT INTO external_income 
                (school_id, title, amount, category, income_date, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            params = (
                income_data['school_id'],
                income_data['title'],
                income_data['amount'],
                income_data['category'],
                income_data['income_date'],
                income_data['notes']
            )
            
            # تنفيذ الاستعلام
            result = db_manager.execute_update(insert_query, params)
            
            if result > 0:
                QMessageBox.information(self, "نجح", "تم حفظ الوارد الخارجي بنجاح")
                log_user_action("إضافة وارد خارجي جديد", "نجح")
                log_database_operation("إدراج وارد خارجي", "نجح")
                self.accept()
            else:
                QMessageBox.warning(self, "خطأ", "لم يتم حفظ الوارد")
                
        except Exception as e:
            logging.error(f"خطأ في حفظ الوارد: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ الوارد:\n{str(e)}")
    
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
                        stop:0 #28A745, stop:1 #20924C);
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
                    color: #E8F5E8;
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
                    border-color: #28A745;
                }
                
                #requiredInput:focus {
                    border-color: #20924C;
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
                    border-color: #28A745;
                }
                
                #amountInput {
                    padding: 10px;
                    border: 2px solid #28A745;
                    border-radius: 6px;
                    font-size: 18px;
                    background-color: white;
                    font-weight: bold;
                }
                
                #dateInput {
                    padding: 8px;
                    border: 2px solid #28A745;
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
                    background-color: #28A745;
                    color: white;
                    border: none;
                    padding: 12px 30px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 18px;
                    min-width: 120px;
                }
                
                #saveButton:hover {
                    background-color: #218838;
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
