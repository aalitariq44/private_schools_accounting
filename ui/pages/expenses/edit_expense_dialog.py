#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة تعديل بيانات المصروف
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


class EditExpenseDialog(QDialog):
    """نافذة تعديل بيانات المصروف"""
    
    def __init__(self, expense_id, parent=None):
        super().__init__(parent)
        self.expense_id = expense_id
        self.expense_data = None
        
        self.setWindowTitle("تعديل بيانات المصروف")
        self.setModal(True)
        self.resize(550, 700)
        
        self.setup_ui()
        self.setup_styles()
        self.load_schools()
        self.load_expense_data()
        
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
            
            # معلومات المصروف الأساسية
            self.create_basic_info_section(layout)
            
            
            # تفاصيل إضافية
            self.create_additional_details_section(layout)
            
            # أزرار الحفظ والإلغاء
            self.create_buttons_section(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة تعديل المصروف: {e}")
            raise
    
    def create_header(self, layout):
        """إنشاء رأس النافذة"""
        try:
            header_frame = QFrame()
            header_frame.setObjectName("headerFrame")
            
            header_layout = QVBoxLayout(header_frame)
            header_layout.setContentsMargins(20, 15, 20, 15)
            
            title_label = QLabel(f"تعديل بيانات المصروف #{self.expense_id}")
            title_label.setObjectName("dialogTitle")
            title_label.setStyleSheet("color: black;")
            header_layout.addWidget(title_label)
            
            desc_label = QLabel("يرجى تعديل البيانات حسب الحاجة")
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
            
            # زر الحذف
            self.delete_button = QPushButton("حذف المصروف")
            self.delete_button.setObjectName("deleteButton")
            self.delete_button.clicked.connect(self.delete_expense)
            buttons_layout.addWidget(self.delete_button)
            
            # زر الحفظ
            self.save_button = QPushButton("حفظ التعديلات")
            self.save_button.setObjectName("saveButton")
            self.save_button.clicked.connect(self.save_changes)
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
    
    def load_expense_data(self):
        """تحميل بيانات المصروف الحالي"""
        try:
            # جلب بيانات المصروف
            query = """
                SELECT e.*, s.name_ar as school_name
                FROM expenses e
                LEFT JOIN schools s ON e.school_id = s.id
                WHERE e.id = ?
            """
            result = db_manager.execute_query(query, (self.expense_id,))
            
            if not result:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على بيانات المصروف")
                self.reject()
                return
            
            self.expense_data = result[0]

            # ملء الحقول بالبيانات الحالية
            # إعداد نوع المصروف والوصف
            self.category_combo.setCurrentText(self.expense_data['expense_type'] or "")
            self.title_input.setText(self.expense_data['description'] or "")
            # المبلغ والتواريخ والملاحظات
            self.amount_input.setValue(float(self.expense_data['amount'] or 0))
            self.expense_date.setDate(QDate(datetime.strptime(
                self.expense_data['expense_date'], '%Y-%m-%d').date()))
            self.notes_input.setPlainText(self.expense_data['notes'] or "")
            # المدرسة
            school_index = self.school_combo.findData(self.expense_data['school_id'])
            if school_index >= 0:
                self.school_combo.setCurrentIndex(school_index)
            
            
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات المصروف: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في تحميل بيانات المصروف:\n{str(e)}")
            self.reject()
    
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
            
            # التحقق من المدرسة
            if not self.school_combo.currentData():
                errors.append("يجب اختيار المدرسة")
            
            # التحقق من الفئة
            if self.category_combo.currentIndex() == 0:
                errors.append("يجب اختيار فئة المصروف")
            
            return errors
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من البيانات: {e}")
            return [f"خطأ في التحقق من البيانات: {str(e)}"]
    
    def save_changes(self):
        """حفظ التعديلات"""
        try:
            # التحقق من صحة البيانات
            errors = self.validate_inputs()
            if errors:
                QMessageBox.warning(self, "خطأ في البيانات", "\n".join(errors))
                return
            
            # تحضير البيانات المحدثة
            updated_data = {
                'expense_type': self.category_combo.currentText(),
                'amount': self.amount_input.value(),
                'description': self.title_input.text().strip(),
                'expense_date': self.expense_date.date().toPyDate(),
                'notes': self.notes_input.toPlainText().strip() or None,
                'school_id': self.school_combo.currentData()
            }
            
            # تحديث البيانات في قاعدة البيانات
            update_query = """
                UPDATE expenses 
                SET expense_type = ?, amount = ?, description = ?, expense_date = ?, 
                    notes = ?, school_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            
            params = (
                updated_data['expense_type'],
                updated_data['amount'],
                updated_data['description'],
                updated_data['expense_date'],
                updated_data['notes'],
                updated_data['school_id'],
                self.expense_id
            )
            
            # تنفيذ الاستعلام
            result = db_manager.execute_update(update_query, params)
            
            if result > 0:
                QMessageBox.information(self, "نجح", "تم حفظ التعديلات بنجاح")
                log_user_action(f"تعديل بيانات المصروف {self.expense_id}", "نجح")
                log_database_operation("تحديث مصروف", "نجح")
                self.accept()
            else:
                QMessageBox.warning(self, "خطأ", "لم يتم حفظ التعديلات")
                
        except Exception as e:
            logging.error(f"خطأ في حفظ التعديلات: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ التعديلات:\n{str(e)}")
    
    def delete_expense(self):
        """حذف المصروف"""
        try:
            # تأكيد الحذف
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                "هل أنت متأكد من حذف هذا المصروف؟\nسيتم حذف جميع البيانات المرتبطة به.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # حذف المصروف من قاعدة البيانات
                delete_query = "DELETE FROM expenses WHERE id = ?"
                result = db_manager.execute_update(delete_query, (self.expense_id,))
                
                if result > 0:
                    QMessageBox.information(self, "نجح", "تم حذف المصروف بنجاح")
                    log_user_action(f"حذف المصروف {self.expense_id}", "نجح")
                    log_database_operation("حذف مصروف", "نجح")
                    self.accept()
                else:
                    QMessageBox.warning(self, "خطأ", "لم يتم حذف المصروف")
                    
        except Exception as e:
            logging.error(f"خطأ في حذف المصروف: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حذف المصروف:\n{str(e)}")
    
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
                        stop:0 #FD7E14, stop:1 #E8590C);
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
                    color: #FEF1E8;
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
                    border-color: #FD7E14;
                }
                
                #requiredInput:focus {
                    border-color: #E8590C;
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
                    border-color: #FD7E14;
                }
                
                #amountInput {
                    padding: 10px;
                    border: 2px solid #FD7E14;
                    border-radius: 6px;
                    font-size: 18px;
                    background-color: white;
                    font-weight: bold;
                }
                
                #dateInput {
                    padding: 8px;
                    border: 2px solid #FD7E14;
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
                    min-width: 140px;
                }
                
                #saveButton:hover {
                    background-color: #218838;
                }
                
                #deleteButton {
                    background-color: #DC3545;
                    color: white;
                    border: none;
                    padding: 12px 30px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 18px;
                    min-width: 120px;
                }
                
                #deleteButton:hover {
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
