#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إضافة مجموعة طلاب
"""

import sys
import logging
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
    QPushButton, QFrame, QMessageBox, QGroupBox, 
    QScrollArea, QWidget, QSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon

from core.database.connection import db_manager
from core.utils.logger import log_user_action

class AddGroupStudentsDialog(QDialog):
    """نافذة إضافة مجموعة طلاب"""
    
    students_added = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.students_data = []  # قائمة لحفظ بيانات الطلاب
        self.setup_ui()
        self.load_schools()
        self.setup_connections()
        self.add_student_row()  # إضافة أول صف للطلاب
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("إضافة مجموعة طلاب")
        self.setModal(True)
        self.resize(1000, 700)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # إنشاء منطقة التمرير
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # إعداد المعلومات المشتركة
        self.create_shared_info_section(scroll_layout)
        
        # إعداد قسم الطلاب
        self.create_students_section(scroll_layout)
        
        # أزرار العمليات
        self.create_buttons_section(scroll_layout)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
        self.setup_styles()
        
    def create_shared_info_section(self, layout):
        """إنشاء قسم المعلومات المشتركة"""
        shared_frame = QGroupBox("المعلومات المشتركة")
        shared_frame.setObjectName("sharedFrame")
        
        shared_layout = QGridLayout()
        shared_layout.setSpacing(15)
        
        # اسم المدرسة
        self.school_combo = QComboBox()
        self.school_combo.setObjectName("inputCombo")
        
        # الصف
        self.grade_combo = QComboBox()
        self.grade_combo.setObjectName("inputCombo")
        self.grade_combo.addItem("اختر الصف", None)
        
        # الشعبة (قائمة منسدلة)
        self.section_combo = QComboBox()
        self.section_combo.setObjectName("inputCombo")
        # إضافة خيار افتراضي
        self.section_combo.addItem("اختر الشعبة", None)
        # الأحرف الأبجدية العشرة
        for letter in ["أ","ب","ج","د","ه","و","ز","ح","ط","ي"]:
            self.section_combo.addItem(letter, letter)
        
        # الرسوم الدراسية
        self.total_fee_input = QSpinBox()
        self.total_fee_input.setObjectName("inputField")
        self.total_fee_input.setRange(0, 10000000)
        self.total_fee_input.setSuffix(" د.ع")
        
        # تاريخ المباشرة
        self.start_date_input = QDateEdit()
        self.start_date_input.setObjectName("inputField")
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setCalendarPopup(True)
        
        # الحالة
        self.status_combo = QComboBox()
        self.status_combo.setObjectName("inputCombo")
        self.status_combo.addItems(["نشط", "منقطع", "متخرج", "محول"])
        
        # الجنس
        self.gender_combo = QComboBox()
        self.gender_combo.setObjectName("inputCombo")
        self.gender_combo.addItems(["ذكر", "أنثى"])

        # توزيع الحقول في صفين أفقيين
        # الصف الأول: المدرسة، الصف، الشعبة، الرسوم الدراسية
        shared_layout.addWidget(QLabel("المدرسة:"), 0, 0)
        shared_layout.addWidget(self.school_combo, 0, 1)
        shared_layout.addWidget(QLabel("الصف:"), 0, 2)
        shared_layout.addWidget(self.grade_combo, 0, 3)
        shared_layout.addWidget(QLabel("الشعبة:"), 0, 4)
        shared_layout.addWidget(self.section_combo, 0, 5)
        shared_layout.addWidget(QLabel("الرسوم الدراسية:"), 0, 6)
        shared_layout.addWidget(self.total_fee_input, 0, 7)
        # الصف الثاني: تاريخ المباشرة، الحالة، الجنس
        shared_layout.addWidget(QLabel("تاريخ المباشرة:"), 1, 0)
        shared_layout.addWidget(self.start_date_input, 1, 1)
        shared_layout.addWidget(QLabel("الحالة:"), 1, 2)
        shared_layout.addWidget(self.status_combo, 1, 3)
        shared_layout.addWidget(QLabel("الجنس:"), 1, 4)
        shared_layout.addWidget(self.gender_combo, 1, 5)
        
        shared_frame.setLayout(shared_layout)
        layout.addWidget(shared_frame)
        
    def create_students_section(self, layout):
        """إنشاء قسم الطلاب"""
        students_frame = QGroupBox("بيانات الطلاب")
        students_frame.setObjectName("studentsFrame")
        
        students_layout = QVBoxLayout()
        
        # عداد الطلاب
        counter_layout = QHBoxLayout()
        self.students_count_label = QLabel("عدد الطلاب: 0")
        self.students_count_label.setObjectName("countLabel")
        counter_layout.addWidget(self.students_count_label)
        counter_layout.addStretch()
        
        # زر إضافة طالب جديد
        self.add_student_btn = QPushButton("+ إضافة طالب")
        self.add_student_btn.setObjectName("addButton")
        counter_layout.addWidget(self.add_student_btn)
        
        students_layout.addLayout(counter_layout)
        
        # جدول الطلاب
        self.students_table = QTableWidget()
        self.students_table.setObjectName("studentsTable")
        self.students_table.setColumnCount(3)
        self.students_table.setHorizontalHeaderLabels(["اسم الطالب", "رقم الهاتف", "حذف"])
        
        # إعداد الجدول
        header = self.students_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        self.students_table.setAlternatingRowColors(True)
        self.students_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        students_layout.addWidget(self.students_table)
        
        students_frame.setLayout(students_layout)
        layout.addWidget(students_frame)
        
    def create_buttons_section(self, layout):
        """إنشاء قسم الأزرار"""
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # زر الإلغاء
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancelButton")
        buttons_layout.addWidget(self.cancel_btn)
        
        # زر الحفظ
        self.save_btn = QPushButton("حفظ المجموعة")
        self.save_btn.setObjectName("saveButton")
        buttons_layout.addWidget(self.save_btn)
        
        layout.addLayout(buttons_layout)
        
    def setup_connections(self):
        """إعداد الاتصالات"""
        self.add_student_btn.clicked.connect(self.add_student_row)
        self.save_btn.clicked.connect(self.save_students_group)
        self.cancel_btn.clicked.connect(self.reject)
        self.school_combo.currentTextChanged.connect(self.update_grades_for_school)
        
    def load_schools(self):
        """تحميل المدارس"""
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
                
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المدارس: {e}")
            
    def update_grades_for_school(self):
        """تحديث الصفوف حسب المدرسة المختارة"""
        try:
            self.grade_combo.clear()
            
            if self.school_combo.currentIndex() <= 0:
                self.grade_combo.addItem("اختر الصف", None)
                return
                
            school_data = self.school_combo.currentData()
            if not school_data:
                self.grade_combo.addItem("اختر الصف", None)
                return
            
            school_types_str = school_data.get('types', '')
            
            # تحليل أنواع المدرسة
            school_types = []
            if school_types_str:
                try:
                    # محاولة تحليل JSON
                    parsed_types = json.loads(school_types_str)
                    if isinstance(parsed_types, list):
                        school_types = parsed_types
                    else:
                        school_types = [school_types_str]
                except json.JSONDecodeError:
                    # إذا لم يكن JSON صحيح، نعامله كنص مفصول بفواصل
                    school_types = [t.strip() for t in school_types_str.split(',') if t.strip()]
            
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
            
            if "إعدادية" in school_types or "ثانوية" in school_types:
                all_grades.extend([
                    "الرابع العلمي", "الرابع الأدبي",
                    "الخامس العلمي", "الخامس الأدبي", 
                    "السادس العلمي", "السادس الأدبي"
                ])
            
            # إضافة الصفوف إلى القائمة
            self.grade_combo.addItem("اختر الصف", None)
            for grade in all_grades:
                self.grade_combo.addItem(grade, grade)
                
        except Exception as e:
            logging.error(f"خطأ في تحديث الصفوف: {e}")
            
    def add_student_row(self):
        """إضافة صف طالب جديد"""
        try:
            row_count = self.students_table.rowCount()
            self.students_table.insertRow(row_count)
            
            # عمود اسم الطالب
            name_input = QLineEdit()
            name_input.setObjectName("studentNameInput")
            name_input.setPlaceholderText("اسم الطالب الكامل...")
            self.students_table.setCellWidget(row_count, 0, name_input)
            
            # عمود رقم الهاتف
            phone_input = QLineEdit()
            phone_input.setObjectName("studentPhoneInput")
            phone_input.setPlaceholderText("07xxxxxxxx")
            phone_input.setMaxLength(11)  # حد أقصى للأرقام العراقية
            self.students_table.setCellWidget(row_count, 1, phone_input)
            
            # زر الحذف
            delete_btn = QPushButton("حذف")
            delete_btn.setObjectName("deleteButton")
            delete_btn.clicked.connect(lambda: self.delete_student_row(row_count))
            self.students_table.setCellWidget(row_count, 2, delete_btn)
            
            # تحديث العداد
            self.update_students_count()
            
            # التركيز على حقل الاسم الجديد
            name_input.setFocus()
            
        except Exception as e:
            logging.error(f"خطأ في إضافة صف طالب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في إضافة صف طالب: {e}")
            
    def delete_student_row(self, row):
        """حذف صف طالب"""
        try:
            if row < 0 or row >= self.students_table.rowCount():
                return
                
            # إظهار رسالة تأكيد
            reply = QMessageBox.question(
                self, "تأكيد الحذف", 
                "هل تريد حذف هذا الطالب من القائمة؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.students_table.removeRow(row)
                self.update_students_count()
                self.reconnect_delete_buttons()
                
        except Exception as e:
            logging.error(f"خطأ في حذف صف الطالب: {e}")
            
    def reconnect_delete_buttons(self):
        """إعادة ربط أزرار الحذف"""
        try:
            for i in range(self.students_table.rowCount()):
                delete_btn = self.students_table.cellWidget(i, 2)
                if delete_btn:
                    delete_btn.clicked.disconnect()
                    delete_btn.clicked.connect(lambda checked, row=i: self.delete_student_row(row))
        except Exception as e:
            logging.error(f"خطأ في إعادة ربط أزرار الحذف: {e}")
            
    def update_students_count(self):
        """تحديث عداد الطلاب"""
        count = self.students_table.rowCount()
        self.students_count_label.setText(f"عدد الطلاب: {count}")
        
    def validate_shared_data(self):
        """التحقق من صحة البيانات المشتركة"""
        if self.school_combo.currentData() is None:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار المدرسة")
            return False
            
        if self.grade_combo.currentData() is None:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار الصف")
            return False
            
        if self.section_combo.currentData() is None:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار الشعبة")
            return False
            
        if self.total_fee_input.value() <= 0:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال الرسوم الدراسية")
            return False
            
        return True
        
    def validate_students_data(self):
        """التحقق من صحة بيانات الطلاب"""
        if self.students_table.rowCount() == 0:
            QMessageBox.warning(self, "تحذير", "يرجى إضافة طالب واحد على الأقل")
            return False
            
        # التحقق من أسماء الطلاب
        names_list = []
        for row in range(self.students_table.rowCount()):
            name_widget = self.students_table.cellWidget(row, 0)
            if name_widget:
                name = name_widget.text().strip()
                if not name:
                    QMessageBox.warning(self, "تحذير", f"يرجى إدخال اسم الطالب في الصف {row + 1}")
                    name_widget.setFocus()
                    return False
                
                # التحقق من تكرار الأسماء
                if name in names_list:
                    QMessageBox.warning(self, "تحذير", f"اسم الطالب '{name}' مكرر. يرجى التأكد من الأسماء")
                    name_widget.setFocus()
                    return False
                
                names_list.append(name)
                
        return True
        
    def save_students_group(self):
        """حفظ مجموعة الطلاب"""
        try:
            # التحقق من صحة البيانات
            if not self.validate_shared_data() or not self.validate_students_data():
                return
                
            # جمع البيانات المشتركة
            shared_data = {
                'school_id': self.school_combo.currentData()['id'],
                'grade': self.grade_combo.currentData(),
                'section': self.section_combo.currentData(),
                'total_fee': self.total_fee_input.value(),
                'start_date': self.start_date_input.date().toString('yyyy-MM-dd'),
                'status': self.status_combo.currentText(),
                'gender': self.gender_combo.currentText()
            }
            
            # جمع بيانات الطلاب
            students_list = []
            for row in range(self.students_table.rowCount()):
                name_widget = self.students_table.cellWidget(row, 0)
                phone_widget = self.students_table.cellWidget(row, 1)
                
                if name_widget:
                    student = {
                        'name': name_widget.text().strip(),
                        'phone': phone_widget.text().strip() if phone_widget else ""
                    }
                    students_list.append(student)
            
            # حفظ الطلاب في قاعدة البيانات
            success_count = 0
            for student in students_list:
                try:
                    query = """
                        INSERT INTO students (
                            name, school_id, grade, section, phone, 
                            total_fee, start_date, status, gender
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    values = (
                        student['name'],
                        shared_data['school_id'],
                        shared_data['grade'],
                        shared_data['section'],
                        student['phone'],
                        shared_data['total_fee'],
                        shared_data['start_date'],
                        shared_data['status'],
                        shared_data['gender']
                    )
                    
                    db_manager.execute_query(query, values)
                    success_count += 1
                    
                except Exception as e:
                    logging.error(f"خطأ في حفظ الطالب {student['name']}: {e}")
                    
            if success_count > 0:
                school_name = self.school_combo.currentData()['name']
                grade = self.grade_combo.currentData()
                section = self.section_combo.currentData()
                
                success_message = f"""تم إضافة {success_count} طالب بنجاح
                
المدرسة: {school_name}
الصف: {grade}
الشعبة: {section}
الرسوم: {self.total_fee_input.value():,.0f} د.ع"""
                
                QMessageBox.information(self, "نجح", success_message)
                
                log_user_action(f"إضافة مجموعة طلاب - {success_count} طالب - {school_name} - {grade}{section}")
                self.students_added.emit()
                self.accept()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في إضافة أي طالب")
                
        except Exception as e:
            logging.error(f"خطأ في حفظ مجموعة الطلاب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ مجموعة الطلاب: {e}")
            
    def setup_styles(self):
        """إعداد التنسيقات"""
        style = """
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9ff, stop:1 #e8f0ff);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: #f8f9ff;
            }
            
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 14px;
                margin: 5px 0px;
            }
            
            #countLabel {
                font-size: 16px;
                color: #27ae60;
                font-weight: bold;
            }
            
            QLineEdit, QComboBox, QDateEdit, QSpinBox {
                padding: 8px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
                min-height: 25px;
                margin: 3px 0px;
            }
            
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
                border-color: #3498db;
                background-color: #f8fbff;
            }
            
            #studentNameInput, #studentPhoneInput {
                font-size: 13px;
                padding: 5px 8px;
                min-height: 20px;
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
                margin: 5px 3px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            
            #addButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #2ecc71);
                min-width: 120px;
            }
            
            #addButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2ecc71, stop:1 #27ae60);
            }
            
            #deleteButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                min-width: 60px;
                padding: 5px 10px;
                font-size: 12px;
            }
            
            #deleteButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ec7063, stop:1 #e74c3c);
            }
            
            #cancelButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #95a5a6, stop:1 #7f8c8d);
            }
            
            #cancelButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a6b4b5, stop:1 #95a5a6);
            }
            
            #saveButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #2ecc71);
                min-width: 150px;
                font-size: 16px;
                padding: 12px 25px;
            }
            
            #saveButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2ecc71, stop:1 #27ae60);
            }
            
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #e3f2fd;
                gridline-color: #ecf0f1;
            }
            
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34495e, stop:1 #2c3e50);
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
        """
        
        self.setStyleSheet(style)
