#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إضافة رسم إضافي جديد
"""

import logging
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QPushButton, QLineEdit, QDateEdit, QTextEdit, QComboBox,
    QMessageBox, QFrame, QDoubleSpinBox, QCheckBox, QGroupBox, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation


class AddAdditionalFeeDialog(QDialog):
    """نافذة إضافة رسم إضافي جديد"""
    
    def __init__(self, student_id, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.setup_defaults()
        
        log_user_action(f"فتح نافذة إضافة رسم إضافي للطالب: {student_id}")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            self.setWindowTitle("إضافة رسم إضافي")
            self.setModal(True)
            self.resize(800, 900) # Adjusted size to match add_student_dialog
            
            # التخطيط الرئيسي
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(10, 10, 10, 10)
            
            # إضافة scroll area للشاشات الصغيرة
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            # المحتوى الرئيسي داخل scroll area
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setSpacing(20)
            content_layout.setContentsMargins(25, 25, 25, 25)
            
            # عنوان النافذة
            title_label = QLabel("إضافة رسم إضافي جديد")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #3498db, stop:1 #2980b9);
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    font-size: 18px;
                    font-weight: bold;
                }
            """)
            content_layout.addWidget(title_label)
            
            # مجموعة معلومات الرسم
            fee_info_group = QGroupBox("معلومات الرسم")
            fee_layout = QFormLayout(fee_info_group)
            fee_layout.setSpacing(15)
            
            # نوع الرسم
            self.fee_type_combo = QComboBox()
            self.fee_type_combo.setObjectName("feeTypeCombo")
            self.fee_type_combo.addItems([
                "رسوم التسجيل",
                "الزي المدرسي",
                "الكتب",
                "القرطاسية",
                "رسوم النقل",
                "رسوم الأنشطة",
                "رسم مخصص"
            ])
            fee_layout.addRow("نوع الرسم:", self.fee_type_combo)
            
            # رسم مخصص
            self.custom_fee_input = QLineEdit()
            self.custom_fee_input.setObjectName("customFeeInput")
            self.custom_fee_input.setPlaceholderText("أدخل نوع الرسم المخصص...")
            self.custom_fee_input.setVisible(False)
            fee_layout.addRow("النوع المخصص:", self.custom_fee_input)
            
            # مبلغ الرسم
            self.amount_input = QDoubleSpinBox()
            self.amount_input.setObjectName("amountInput")
            self.amount_input.setMinimum(0.0)
            self.amount_input.setMaximum(9999999.0)
            self.amount_input.setDecimals(0)
            self.amount_input.setSuffix(" د.ع")
            self.amount_input.setValue(0.0)
            fee_layout.addRow("مبلغ الرسم:", self.amount_input)
            
            # حالة الدفع
            self.paid_checkbox = QCheckBox("تم الدفع")
            self.paid_checkbox.setObjectName("paidCheckbox")
            fee_layout.addRow("حالة الدفع:", self.paid_checkbox)
            
            # تاريخ الدفع
            self.payment_date = QDateEdit()
            self.payment_date.setObjectName("dateInput")
            self.payment_date.setCalendarPopup(True)
            self.payment_date.setDisplayFormat("yyyy-MM-dd")
            self.payment_date.setEnabled(False)
            fee_layout.addRow("تاريخ الدفع:", self.payment_date)
            
            # الملاحظات
            self.notes_input = QTextEdit()
            self.notes_input.setObjectName("notesInput")
            self.notes_input.setMaximumHeight(80)
            self.notes_input.setPlaceholderText("أدخل أي ملاحظات إضافية...")
            fee_layout.addRow("الملاحظات:", self.notes_input)
            
            content_layout.addWidget(fee_info_group)
            
            # أزرار العمليات
            buttons_layout = QHBoxLayout()
            buttons_layout.addStretch()
            
            self.save_button = QPushButton("حفظ الرسم")
            self.save_button.setObjectName("saveButton")
            buttons_layout.addWidget(self.save_button)
            
            self.cancel_button = QPushButton("إلغاء")
            self.cancel_button.setObjectName("cancelButton")
            buttons_layout.addWidget(self.cancel_button)
            
            content_layout.addLayout(buttons_layout)
            
            # إضافة المحتوى إلى scroll area
            scroll_area.setWidget(content_widget)
            main_layout.addWidget(scroll_area)
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة نافذة إضافة الرسم الإضافي: {e}")
            raise
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            self.save_button.clicked.connect(self.save_additional_fee)
            self.cancel_button.clicked.connect(self.reject)
            
            # إظهار/إخفاء حقل الرسم المخصص
            self.fee_type_combo.currentTextChanged.connect(self.on_fee_type_changed)
            
            # تفعيل/تعطيل تاريخ الدفع
            self.paid_checkbox.toggled.connect(self.on_paid_toggled)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def setup_defaults(self):
        """إعداد القيم الافتراضية"""
        try:
            # تعيين تاريخ الدفع الحالي
            current_date = QDate.currentDate()
            self.payment_date.setDate(current_date)
            
            # تركيز على نوع الرسم
            self.fee_type_combo.setFocus()
            
        except Exception as e:
            logging.error(f"خطأ في إعداد القيم الافتراضية: {e}")
    
    def on_fee_type_changed(self, fee_type):
        """معالج تغيير نوع الرسم"""
        try:
            if fee_type == "رسم مخصص":
                self.custom_fee_input.setVisible(True)
                self.custom_fee_input.setFocus()
            else:
                self.custom_fee_input.setVisible(False)
                self.custom_fee_input.clear()
            
        except Exception as e:
            logging.error(f"خطأ في معالج تغيير نوع الرسم: {e}")
    
    def on_paid_toggled(self, checked):
        """معالج تغيير حالة الدفع"""
        try:
            self.payment_date.setEnabled(checked)
            if checked:
                # تعيين تاريخ الدفع الحالي
                self.payment_date.setDate(QDate.currentDate())
            
        except Exception as e:
            logging.error(f"خطأ في معالج تغيير حالة الدفع: {e}")
    
    def validate_input(self):
        """التحقق من صحة البيانات المدخلة"""
        try:
            # التحقق من نوع الرسم
            fee_type = self.fee_type_combo.currentText()
            if fee_type == "رسم مخصص":
                custom_fee = self.custom_fee_input.text().strip()
                if not custom_fee:
                    QMessageBox.warning(self, "خطأ", "يجب إدخال نوع الرسم المخصص")
                    self.custom_fee_input.setFocus()
                    return False
            
            # التحقق من المبلغ
            amount = self.amount_input.value()
            if amount <= 0:
                QMessageBox.warning(self, "خطأ", "يجب إدخال مبلغ صحيح")
                self.amount_input.setFocus()
                return False
            
            # التحقق من تاريخ الدفع إذا كان مدفوعاً
            if self.paid_checkbox.isChecked():
                payment_date = self.payment_date.date().toPyDate()
                if payment_date > date.today():
                    reply = QMessageBox.question(
                        self, "تأكيد",
                        "تاريخ الدفع في المستقبل. هل تريد المتابعة؟",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        self.payment_date.setFocus()
                        return False
            
            return True
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من البيانات: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في التحقق من البيانات: {str(e)}")
            return False
    
    def save_additional_fee(self):
        """حفظ الرسم الإضافي الجديد"""
        try:
            if not self.validate_input():
                return
            
            # جمع البيانات
            fee_type = self.fee_type_combo.currentText()
            if fee_type == "رسم مخصص":
                fee_type = self.custom_fee_input.text().strip()
            
            amount = self.amount_input.value()
            paid = self.paid_checkbox.isChecked()
            payment_date = self.payment_date.date().toString("yyyy-MM-dd") if paid else None
            notes = self.notes_input.toPlainText().strip()
            
            # تحديد الحالة
            status = 'محصل' if paid else 'غير محصل'
            
            # إدراج الرسم في قاعدة البيانات مع الحقول الصحيحة
            query = """
                INSERT INTO additional_fees 
                (student_id, fee_type, amount, paid, payment_date, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                self.student_id, fee_type, amount,
                paid, payment_date, notes if notes else None
            )
            
            result = db_manager.execute_query(query, params)
            
            if result is not None:
                # تسجيل العملية
                log_database_operation(
                    "إضافة",
                    "additional_fees",
                    f"إضافة رسم إضافي جديد - الطالب: {self.student_id}, "
                    f"النوع: {fee_type}, المبلغ: {amount}"
                )
                log_user_action(
                    f"إضافة رسم إضافي ({fee_type}) بمبلغ {amount:,.0f} د.ع للطالب: {self.student_id}"
                )
                
                QMessageBox.information(self, "نجح", "تم حفظ الرسم الإضافي بنجاح")
                self.accept()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في حفظ الرسم الإضافي")
            
        except Exception as e:
            logging.error(f"خطأ في حفظ الرسم الإضافي: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في حفظ الرسم الإضافي: {str(e)}")
    
    def setup_styles(self):
        """إعداد التنسيقات"""
        try:
            style = """
                QDialog {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #f8f9ff, stop:1 #e8f0ff);
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                QLabel {
                    color: #2c3e50;
                    font-weight: bold;
                    font-size:18px;
                    margin: 5px 0px;
                }
                
                QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
                    padding: 12px 15px;
                    border: 2px solid #bdc3c7;
                    border-radius: 10px;
                    background-color: white;
                    font-size: 18px;
                    min-height: 30px;
                    margin: 5px 0px;
                }
                
                QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                    border-color: #3498db;
                    background-color: #f8fbff;
                }
                
                QComboBox::drop-down {
                    border: none;
                    width: 30px;
                }
                
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3498db, stop:1 #2980b9);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 18px;
                    min-width: 120px;
                    margin: 8px 4px;
                }
                
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5dade2, stop:1 #3498db);
                }
                
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2980b9, stop:1 #1f618d);
                }
                
                QPushButton#cancelButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e74c3c, stop:1 #c0392b);
                }
                
                QGroupBox {
                    font-weight: bold;
                    font-size: 18px;
                    color: #2c3e50;
                    border: 2px solid #bdc3c7;
                    border-radius: 12px;
                    margin: 15px 0px;
                    padding-top: 20px;
                }
                
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 20px;
                    padding: 0 10px 0 10px;
                    background-color: #3498db;
                    color: white;
                    border-radius: 6px;
                    padding: 8px 15px;
                    font-size: 18px;
                }
                
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                
                /* صندوق الاختيار */
                #paidCheckbox {
                    font-size: 18px; /* Increased font size */
                    font-weight: bold;
                    color: #27AE60;
                    margin: 5px 0px; /* Added margin for consistency */
                }
                
                #paidCheckbox::indicator {
                    width: 22px; /* Slightly larger indicator */
                    height: 22px;
                }
                
                #paidCheckbox::indicator:unchecked {
                    border: 2px solid #bdc3c7; /* Consistent border color */
                    border-radius: 6px; /* More rounded corners */
                    background-color: white;
                }
                
                #paidCheckbox::indicator:checked {
                    border: 2px solid #27AE60;
                    border-radius: 6px;
                    background-color: #27AE60;
                    image: url(:/icons/check.png); /* Assuming this path is correct */
                }
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد التنسيقات: {e}")
