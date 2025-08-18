#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
                            QPushButton, QFrame, QMessageBox, QFileDialog,
                            QGroupBox, QSpinBox, QScrollArea, QWidget)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon
import shutil
import uuid
from datetime import datetime
import logging

# Import the database manager
from core.database.connection import db_manager

class AddStudentDialog(QDialog):
    student_added = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.photo_path = None
        self.setup_ui()
        self.load_schools()
        self.update_grades_for_school() # Call after loading schools to populate grades initially
        self.setup_connections()
        
    def setup_ui(self):
        self.setWindowTitle("إضافة طالب جديد")
        self.setModal(True)
        self.resize(800, 900)
        
        # تطبيق الستايل مع تحسينات
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
            
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox {
                padding: 12px 15px;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: white;
                font-size: 18px;
                min-height: 30px;
                margin: 5px 0px;
            }
            
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus {
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
            
            QPushButton#photo_btn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #2ecc71);
                min-width: 100px;
            }
            
            QPushButton#cancel_btn {
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
        """)
        
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
        title_label = QLabel("إضافة طالب جديد")
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
        
        # مجموعة المعلومات الأساسية
        basic_info_group = QGroupBox("المعلومات الأساسية")
        basic_layout = QFormLayout(basic_info_group)
        basic_layout.setSpacing(15)
        
        # الحقول الأساسية
        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText("أدخل الاسم الكامل للطالب")
        basic_layout.addRow("الاسم الكامل:", self.full_name_edit)
        
        # الجنس
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["ذكر", "أنثى"])
        basic_layout.addRow("الجنس:", self.gender_combo)
        
        content_layout.addWidget(basic_info_group)
        
        # مجموعة المعلومات الأكاديمية
        academic_info_group = QGroupBox("المعلومات الأكاديمية")
        academic_layout = QFormLayout(academic_info_group)
        academic_layout.setSpacing(15)
        
        # المدرسة
        self.school_combo = QComboBox()
        self.school_combo.setPlaceholderText("اختر المدرسة")
        academic_layout.addRow("المدرسة:", self.school_combo)
        
        # الصف
        self.grade_combo = QComboBox()
        self.grade_combo.setPlaceholderText("اختر الصف")
        academic_layout.addRow("الصف:", self.grade_combo)
        
        # الشعبة
        self.section_combo = QComboBox()
        self.section_combo.addItems(["أ", "ب", "ج", "د", "ه", "و", "ز", "ح", "ط", "ي"])
        self.section_combo.setPlaceholderText("اختر الشعبة")
        academic_layout.addRow("الشعبة:", self.section_combo)
        
        # المبلغ الإجمالي
        self.total_fee_edit = QLineEdit()
        self.total_fee_edit.setPlaceholderText("المبلغ الإجمالي بالدينار")
        academic_layout.addRow("الرسوم الدراسية:", self.total_fee_edit)
        
        # تاريخ المباشرة
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        academic_layout.addRow("تاريخ المباشرة:", self.start_date_edit)
        
        # الحالة
        self.status_combo = QComboBox()
        self.status_combo.addItems(["نشط", "منقطع", "متخرج", "منتقل"])
        academic_layout.addRow("الحالة:", self.status_combo)
        
        content_layout.addWidget(academic_info_group)
        
        # مجموعة معلومات الاتصال وولي الأمر
        contact_info_group = QGroupBox("معلومات الاتصال وولي الأمر")
        contact_layout = QFormLayout(contact_info_group)
        contact_layout.setSpacing(15)
        
        # الهاتف
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("رقم هاتف الطالب")
        contact_layout.addRow("هاتف الطالب:", self.phone_edit)
        
        content_layout.addWidget(contact_info_group)
        
        # أزرار العمل
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.save_btn = QPushButton("حفظ الطالب")
        buttons_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancel_btn")
        buttons_layout.addWidget(self.cancel_btn)
        
        content_layout.addLayout(buttons_layout)
        
        # إضافة المحتوى إلى scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
    def setup_connections(self):
        """ربط الإشارات"""
        self.save_btn.clicked.connect(self.save_student)
        self.cancel_btn.clicked.connect(self.reject)
        self.school_combo.currentTextChanged.connect(self.update_grades_for_school)
        
    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            query = "SELECT id, name_ar, school_types FROM schools ORDER BY name_ar"
            schools = db_manager.execute_query(query)
            
            self.school_combo.clear()
            self.school_combo.addItem("اختر المدرسة", None)
            
            for school in schools:
                school_data = {
                    'id': school['id'],
                    'name': school['name_ar'],
                    'types': school['school_types']
                }
                self.school_combo.addItem(school['name_ar'], school_data)
            
            # Select the first school if available to trigger grade population
            if schools:
                self.school_combo.setCurrentIndex(1) # Select the first actual school, skipping "اختر المدرسة"
                
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل المدارس:\\n{str(e)}")
    
    def update_grades_for_school(self):
        """تحديث قائمة الصفوف بناءً على نوع المدرسة المختارة"""
        try:
            self.grade_combo.clear()
            
            if self.school_combo.currentIndex() <= 0:
                logging.info("No school selected or 'اختر المدرسة' is selected. Clearing grades.")
                return
                
            school_data = self.school_combo.currentData()
            if not school_data:
                logging.warning("No school data found for selected school.")
                return
            
            logging.info(f"Selected school data: {school_data}")
            school_types_str = school_data.get('types', '')
            logging.info(f"Raw school types string: '{school_types_str}'")
            
            # تحليل أنواع المدرسة
            school_types = []
            if school_types_str:
                try:
                    # Try to parse as JSON array
                    parsed_types = json.loads(school_types_str)
                    if isinstance(parsed_types, list):
                        school_types = parsed_types
                    else:
                        # If not a list, treat as a single string
                        school_types = [school_types_str]
                except json.JSONDecodeError:
                    # If not a valid JSON, assume it's a comma-separated string
                    school_types = [t.strip() for t in school_types_str.split(',') if t.strip()]
            
            logging.info(f"Parsed school types list: {school_types}")
            
            # قائمة الصفوف
            all_grades = []
            
            # إضافة الصفوف حسب نوع المدرسة
            if "ابتدائية" in school_types:
                all_grades.extend([
                    "الأول الابتدائي", "الثاني الابتدائي", "الثالث الابتدائي",
                    "الرابع الابتدائي", "الخامس الابتدائي", "السادس الابتدائي"
                ])
            
            if "متوسطة" in school_types:
                all_grades.extend([
                    "الأول المتوسط", "الثاني المتوسط", "الثالث المتوسط"
                ])
            
            if "إعدادية" in school_types or "ثانوية" in school_types: # Assuming "ثانوية" is also covered by "إعدادية"
                all_grades.extend([
                    "الرابع العلمي", "الرابع الأدبي",
                    "الخامس العلمي", "الخامس الأدبي", 
                    "السادس العلمي", "السادس الأدبي"
                ])
            
            logging.info(f"Grades to be added: {all_grades}")
            
            # إضافة الصفوف إلى القائمة
            self.grade_combo.addItem("اختر الصف", None)
            for grade in all_grades:
                self.grade_combo.addItem(grade, grade)
                
        except Exception as e:
            logging.error(f"خطأ في تحديث الصفوف: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحديث الصفوف:\\n{str(e)}")
    
    def validate_inputs(self):
        """التحقق من صحة البيانات المدخلة"""
        errors = []
        
        # التحقق من الحقول المطلوبة
        if not self.full_name_edit.text().strip():
            errors.append("الاسم الكامل للطالب مطلوب")
            
        if self.school_combo.currentIndex() <= 0:
            errors.append("يجب اختيار المدرسة")
            
        if self.grade_combo.currentIndex() <= 0:
            errors.append("يجب اختيار الصف")
            
        if self.section_combo.currentIndex() < 0: # Check if an item is selected
            errors.append("الشعبة مطلوبة")
        
        # التحقق من الرسوم
        total_fee_text = self.total_fee_edit.text().strip()
        if not total_fee_text:
            errors.append("الرسوم الدراسية مطلوبة")
        else:
            try:
                float(total_fee_text)
            except ValueError:
                errors.append("يجب أن يكون الرسوم الدراسية رقماً صحيحاً")
        
        return errors
    
    def check_student_limit(self):
        """فحص حد الطلاب في النسخة التجريبية"""
        try:
            query = "SELECT COUNT(*) FROM students WHERE status != 'محذوف'"
            result = db_manager.execute_query(query)
            if result and result[0][0] >= 10:
                return False
            return True
        except Exception as e:
            logging.error(f"خطأ في فحص عدد الطلاب: {e}")
            return True

    def save_student(self):
        """حفظ بيانات الطالب"""
        # فحص حد الطلاب في النسخة التجريبية
        if not self.check_student_limit():
            QMessageBox.warning(
                self, 
                "النسخة التجريبية", 
                "هذه نسخة تجريبية لا يمكن إضافة أكثر من 10 طلاب.\n\n"
                "لشراء النسخة الكاملة اتصل بالرقم التالي:\n"
                "07710995922"
            )
            return
        
        # التحقق من صحة البيانات
        errors = self.validate_inputs()
        if errors:
            QMessageBox.warning(self, "خطأ في البيانات", "\\n".join(errors))
            return
        
        try:
            school_data = self.school_combo.currentData()
            
            # إدراج البيانات الأساسية
            insert_query = """
                INSERT INTO students (
                    name, school_id, grade,
                    section, gender, phone,
                    total_fee, start_date, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            total_fee = 0.0
            if self.total_fee_edit.text().strip():
                total_fee = float(self.total_fee_edit.text().strip())
            
            student_data = (
                self.full_name_edit.text().strip(),
                school_data['id'],
                self.grade_combo.currentData(),
                self.section_combo.currentText(),
                self.gender_combo.currentText(),
                self.phone_edit.text().strip(),
                total_fee,
                self.start_date_edit.date().toString("yyyy-MM-dd"),
                self.status_combo.currentText()
            )
            
            student_id = db_manager.execute_insert(insert_query, student_data)
            
            QMessageBox.information(self, "نجح", "تم إضافة الطالب بنجاح!")
            self.student_added.emit()
            self.accept()
            
        except Exception as e:
            logging.error(f"خطأ في حفظ الطالب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ البيانات:\\n{str(e)}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # تطبيق الخط العربي
    font = QFont("Arial", 24)
    app.setFont(font)
    
    dialog = AddStudentDialog()
    dialog.show()
    
    sys.exit(app.exec_())
