#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إضافة معلم جديد
"""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, 
    QSpinBox, QDoubleSpinBox, QTextEdit, QMessageBox,
    QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from core.database.connection import db_manager
from core.utils.logger import log_database_operation


class AddTeacherDialog(QDialog):
    """نافذة إضافة معلم جديد"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styles()
        self.load_schools()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            self.setWindowTitle("إضافة معلم جديد")
            self.setModal(True)
            # set larger size to match student dialog
            self.resize(800, 900)
            
            # التخطيط الرئيسي
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(20)
            
            # عنوان النافذة
            title_label = QLabel("إضافة معلم جديد")
            title_label.setObjectName("dialogTitle")
            layout.addWidget(title_label)
            
            # نموذج البيانات
            self.create_form(layout)
            
            # أزرار العمليات
            self.create_buttons(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد نافذة إضافة معلم: {e}")
            raise
    
    def create_form(self, layout):
        """إنشاء نموذج البيانات"""
        try:
            form_frame = QFrame()
            form_frame.setObjectName("formFrame")
            
            form_layout = QFormLayout(form_frame)
            form_layout.setSpacing(15)
            form_layout.setContentsMargins(20, 20, 20, 20)
            
            # الاسم
            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("أدخل اسم المعلم")
            form_layout.addRow("الاسم *:", self.name_input)
            
            # المدرسة
            self.school_combo = QComboBox()
            self.school_combo.setMinimumWidth(200)
            form_layout.addRow("المدرسة *:", self.school_combo)
            
            # عدد الحصص
            self.class_hours_input = QSpinBox()
            self.class_hours_input.setRange(0, 50)
            self.class_hours_input.setValue(0)
            self.class_hours_input.setSuffix(" حصة")
            form_layout.addRow("عدد الحصص:", self.class_hours_input)
            
            # الراتب الشهري
            self.salary_input = QDoubleSpinBox()
            self.salary_input.setRange(0, 999999)
            self.salary_input.setDecimals(2)
            self.salary_input.setSuffix(" د.ع")
            form_layout.addRow("الراتب الشهري *:", self.salary_input)
            
            # رقم الهاتف
            self.phone_input = QLineEdit()
            self.phone_input.setPlaceholderText("05xxxxxxxx")
            form_layout.addRow("رقم الهاتف:", self.phone_input)
            
            # الملاحظات
            self.notes_input = QTextEdit()
            self.notes_input.setMaximumHeight(80)
            self.notes_input.setPlaceholderText("ملاحظات إضافية...")
            form_layout.addRow("ملاحظات:", self.notes_input)
            
            layout.addWidget(form_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء نموذج البيانات: {e}")
            raise
    
    def create_buttons(self, layout):
        """إنشاء أزرار العمليات"""
        try:
            buttons_frame = QFrame()
            buttons_layout = QHBoxLayout(buttons_frame)
            buttons_layout.setContentsMargins(0, 10, 0, 0)
            
            # زر الإضافة
            self.add_btn = QPushButton("إضافة المعلم")
            self.add_btn.setObjectName("primaryButton")
            self.add_btn.setMinimumWidth(120)
            
            # زر الإلغاء
            self.cancel_btn = QPushButton("إلغاء")
            self.cancel_btn.setObjectName("secondaryButton")
            self.cancel_btn.setMinimumWidth(100)
            
            buttons_layout.addStretch()
            buttons_layout.addWidget(self.add_btn)
            buttons_layout.addWidget(self.cancel_btn)
            
            layout.addWidget(buttons_frame)
            
            # ربط الأحداث
            self.add_btn.clicked.connect(self.add_teacher)
            self.cancel_btn.clicked.connect(self.reject)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الأزرار: {e}")
            raise
    
    def setup_styles(self):
        """إعداد أنماط العرض"""
        try:
            # Use student dialog styles
            self.setStyleSheet("""
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
            """)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الأنماط: {e}")
    
    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT id, name_ar FROM schools ORDER BY name_ar")
                schools = cursor.fetchall()
                
                self.school_combo.clear()
                for school in schools:
                    self.school_combo.addItem(school['name_ar'], school['id'])
                    
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المدارس:\n{e}")
    
    def validate_data(self):
        """التحقق من صحة البيانات"""
        try:
            # التحقق من الحقول المطلوبة
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم المعلم")
                self.name_input.setFocus()
                return False
                
            if self.school_combo.currentData() is None:
                QMessageBox.warning(self, "خطأ", "يرجى اختيار المدرسة")
                self.school_combo.setFocus()
                return False
                
            if self.salary_input.value() <= 0:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال راتب شهري صحيح")
                self.salary_input.setFocus()
                return False
            
            # التحقق من رقم الهاتف إذا تم إدخاله
            phone = self.phone_input.text().strip()
            if phone and not phone.replace(' ', '').replace('-', '').isdigit():
                QMessageBox.warning(self, "خطأ", "رقم الهاتف غير صحيح")
                self.phone_input.setFocus()
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من البيانات: {e}")
            return False
    
    def check_teacher_limit(self):
        """فحص حد المعلمين في النسخة التجريبية"""
        try:
            query = "SELECT COUNT(*) FROM teachers"
            result = db_manager.execute_query(query)
            if result and result[0][0] >= 4:
                return False
            return True
        except Exception as e:
            logging.error(f"خطأ في فحص عدد المعلمين: {e}")
            return True

    def add_teacher(self):
        """إضافة المعلم"""
        try:
            # فحص حد المعلمين في النسخة التجريبية
            if not self.check_teacher_limit():
                QMessageBox.warning(
                    self, 
                    "النسخة التجريبية", 
                    "هذه نسخة تجريبية لا يمكن إضافة أكثر من 4 معلمين.\n\n"
                    "لشراء النسخة الكاملة اتصل بالرقم التالي:\n"
                    "07710995922"
                )
                return
            
            if not self.validate_data():
                return
                
            # جمع البيانات
            teacher_data = {
                'name': self.name_input.text().strip(),
                'school_id': self.school_combo.currentData(),
                'class_hours': self.class_hours_input.value(),
                'monthly_salary': self.salary_input.value(),
                'phone': self.phone_input.text().strip() or None,
                'notes': self.notes_input.toPlainText().strip() or None
            }
            
            # إدراج البيانات
            with db_manager.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO teachers (name, school_id, class_hours, monthly_salary, phone, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    teacher_data['name'],
                    teacher_data['school_id'],
                    teacher_data['class_hours'],
                    teacher_data['monthly_salary'],
                    teacher_data['phone'],
                    teacher_data['notes']
                ))
                
                teacher_id = cursor.lastrowid
                
                log_database_operation("إضافة معلم", "teachers", teacher_id)
                
            QMessageBox.information(self, "نجح", "تم إضافة المعلم بنجاح")
            self.accept()
            
        except Exception as e:
            logging.error(f"خطأ في إضافة المعلم: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في إضافة المعلم:\n{e}")
