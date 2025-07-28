#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إضافة قسط جديد
"""

import logging
from datetime import date
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QPushButton, QDateEdit, QTextEdit, QMessageBox, 
    QDoubleSpinBox, QGroupBox, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation


class AddInstallmentDialog(QDialog):
    """نافذة إضافة قسط جديد"""
    installment_saved = pyqtSignal(int)
    
    def __init__(self, student_id, max_amount, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.max_amount = max_amount
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.setup_defaults()
        
        log_user_action(f"فتح نافذة إضافة قسط للطالب: {student_id}")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            self.setWindowTitle("إضافة قسط جديد")
            self.setModal(True)
            self.resize(800, 600)

            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(10, 10, 10, 10)
            
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setSpacing(20)
            content_layout.setContentsMargins(25, 25, 25, 25)
            
            title_label = QLabel("إضافة قسط جديد")
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
            
            installment_info_group = QGroupBox("معلومات القسط")
            form_layout = QFormLayout(installment_info_group)
            form_layout.setSpacing(15)
            
            info_label = QLabel(f"المبلغ المتبقي: <span style='color: #27AE60;'>{self.max_amount:,.0f} د.ع</span>")
            info_label.setAlignment(Qt.AlignCenter)
            form_layout.addRow(info_label)
            
            self.amount_input = QDoubleSpinBox()
            self.amount_input.setMinimum(0.0)
            self.amount_input.setMaximum(self.max_amount)
            self.amount_input.setDecimals(0)
            self.amount_input.setSuffix(" د.ع")
            # جعل حقل المبلغ يظهر فارغًا عند البداية
            self.amount_input.setSpecialValueText("")
            self.amount_input.setValue(0.0)
            form_layout.addRow("مبلغ القسط:", self.amount_input)
            
            self.payment_date = QDateEdit()
            self.payment_date.setCalendarPopup(True)
            self.payment_date.setDisplayFormat("yyyy-MM-dd")
            form_layout.addRow("تاريخ الدفعة:", self.payment_date)
            
            self.notes_input = QTextEdit()
            self.notes_input.setMaximumHeight(80)
            self.notes_input.setPlaceholderText("أدخل أي ملاحظات إضافية...")
            form_layout.addRow("الملاحظات:", self.notes_input)
            
            content_layout.addWidget(installment_info_group)
            
            buttons_layout = QHBoxLayout()
            buttons_layout.addStretch()
            
            self.save_button = QPushButton("حفظ القسط")
            self.save_button.setObjectName("saveButton")
            buttons_layout.addWidget(self.save_button)
            
            self.cancel_button = QPushButton("إلغاء")
            self.cancel_button.setObjectName("cancelButton")
            buttons_layout.addWidget(self.cancel_button)
            
            content_layout.addLayout(buttons_layout)
            
            scroll_area.setWidget(content_widget)
            main_layout.addWidget(scroll_area)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة نافذة إضافة القسط: {e}")
            raise
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            self.save_button.clicked.connect(self.save_installment)
            self.cancel_button.clicked.connect(self.reject)
            self.amount_input.valueChanged.connect(self.validate_amount)
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def setup_defaults(self):
        """إعداد القيم الافتراضية"""
        try:
            self.payment_date.setDate(QDate.currentDate())
            self.amount_input.setFocus()
            self.amount_input.selectAll()
        except Exception as e:
            logging.error(f"خطأ في إعداد القيم الافتراضية: {e}")
    
    def validate_amount(self):
        """التحقق من صحة المبلغ"""
        try:
            amount = self.amount_input.value()
            if amount > self.max_amount:
                self.amount_input.setValue(self.max_amount)
                QMessageBox.warning(
                    self, "تحذير", 
                    f"لا يمكن أن يكون المبلغ أكبر من المتبقي ({self.max_amount:,.0f} د.ع)"
                )
            elif amount <= 0:
                self.amount_input.setValue(1)
        except Exception as e:
            logging.error(f"خطأ في التحقق من المبلغ: {e}")
    
    def validate_input(self):
        """التحقق من صحة البيانات المدخلة"""
        try:
            amount = self.amount_input.value()
            if amount <= 0:
                QMessageBox.warning(self, "خطأ", "يجب إدخال مبلغ صحيح")
                self.amount_input.setFocus()
                return False
            
            if amount > self.max_amount:
                QMessageBox.warning(
                    self, "خطأ", 
                    f"لا يمكن أن يكون المبلغ أكبر من المتبقي ({self.max_amount:,.0f} د.ع)"
                )
                self.amount_input.setFocus()
                return False
            
            payment_date = self.payment_date.date().toPyDate()
            if payment_date > date.today():
                reply = QMessageBox.question(
                    self, "تأكيد",
                    "التاريخ المحدد في المستقبل. هل تريد المتابعة؟",
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
    
    def save_installment(self):
        """حفظ القسط الجديد"""
        try:
            if not self.validate_input():
                return
            
            amount = self.amount_input.value()
            payment_date = self.payment_date.date().toString("yyyy-MM-dd")
            notes = self.notes_input.toPlainText().strip()
            
            # الحصول على الوقت الحالي
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            
            query = """
            INSERT INTO installments (student_id, amount, payment_date, payment_time, notes)
            VALUES (?, ?, ?, ?, ?)
            """
            params = (
                self.student_id,
                amount,
                payment_date,
                current_time,
                notes if notes else None
            )
            
            # use execute_insert to get the new installment ID
            last_installment_id = db_manager.execute_insert(query, params)
            
            if last_installment_id:
                log_database_operation(
                    "إضافة",
                    "installments",
                    f"إضافة قسط جديد - الطالب: {self.student_id}, المبلغ: {amount}"
                )
                log_user_action(f"إضافة قسط بمبلغ {amount:,.0f} د.ع للطالب: {self.student_id}")
                
                QMessageBox.information(self, "نجح", "تم حفظ القسط بنجاح")
                # emit signal with the new installment ID
                self.installment_saved.emit(last_installment_id)
                self.accept()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في حفظ القسط")
        except Exception as e:
            logging.error(f"خطأ في حفظ القسط: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في حفظ القسط: {str(e)}")
    
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
            """
            self.setStyleSheet(style)
        except Exception as e:
            logging.error(f"خطأ في إعداد التنسيقات: {e}")
