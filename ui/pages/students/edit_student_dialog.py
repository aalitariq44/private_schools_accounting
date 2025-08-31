#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
                            QPushButton, QFrame, QMessageBox, QFileDialog,
                            QGroupBox, QSpinBox, QScrollArea, QWidget, QApplication)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon
import shutil
import uuid
from datetime import datetime
import logging

# Import the database manager
from core.database.connection import db_manager

class EditStudentDialog(QDialog):
    student_updated = pyqtSignal()
    
    def __init__(self, student_id, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.photo_path = None  # Not used in this version, but kept for consistency
        # تهيئة الواجهة والبيانات (تصميم مبسط فقط بدون تغيير الوظائف)
        self.setup_ui()
        self.setup_connections()  # Connect signals first
        self.load_schools()  # Load schools (may trigger update_grades_for_school)
        self.load_student_data()  # Populate fields
        self.apply_responsive_design()  # Responsive sizing (تصميم فقط)
        
    def setup_ui(self):
        """تهيئة الواجهة (تصميم مبسط متوافق مع الشاشات الصغيرة). الوظائف دون تغيير."""
        self.setWindowTitle("تعديل بيانات الطالب")
        self.setModal(True)
        self.resize(700, 600)
        self.setMinimumSize(480, 520)

        self.setStyleSheet("""
            QDialog { background:#f5f7fa; font-family:'Segoe UI', Arial, sans-serif; }
            QLabel { color:#1f2d3d; font-weight:600; margin:4px 0; }
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox {
                padding:6px 8px; border:1px solid #c0c6ce; border-radius:6px; background:#fff; }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus {
                border:1px solid #357abd; background:#f0f7ff; }
            QPushButton { background:#357abd; color:#fff; border:none; padding:8px 18px; border-radius:6px; font-weight:600; }
            QPushButton:hover { background:#4b8fcc; }
            QPushButton:pressed { background:#2d6399; }
            QPushButton#cancel_btn { background:#c0392b; }
            QPushButton#cancel_btn:hover { background:#d35445; }
            QScrollArea { border:none; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)

        title_label = QLabel("تعديل بيانات الطالب")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("background:#357abd; color:#fff; padding:10px; border-radius:6px; font-weight:700;")
        content_layout.addWidget(title_label)

        # المعلومات الأساسية
        basic_layout = QFormLayout()
        basic_layout.setSpacing(8); basic_layout.setLabelAlignment(Qt.AlignRight)
        self.full_name_edit = QLineEdit(); self.full_name_edit.setPlaceholderText("أدخل الاسم الكامل للطالب")
        basic_layout.addRow("الاسم الكامل:", self.full_name_edit)
        self.gender_combo = QComboBox(); self.gender_combo.addItems(["ذكر", "أنثى"])
        basic_layout.addRow("الجنس:", self.gender_combo)
        content_layout.addLayout(basic_layout)

        # المعلومات الأكاديمية
        academic_layout = QFormLayout()
        academic_layout.setSpacing(8); academic_layout.setLabelAlignment(Qt.AlignRight)
        self.school_combo = QComboBox(); self.school_combo.setPlaceholderText("اختر المدرسة")
        academic_layout.addRow("المدرسة:", self.school_combo)
        self.grade_combo = QComboBox(); self.grade_combo.setPlaceholderText("اختر الصف")
        academic_layout.addRow("الصف:", self.grade_combo)
        self.section_combo = QComboBox(); self.section_combo.addItems(["أ", "ب", "ج", "د", "ه", "و", "ز", "ح", "ط", "ي"])
        academic_layout.addRow("الشعبة:", self.section_combo)
        self.total_fee_edit = QLineEdit(); self.total_fee_edit.setPlaceholderText("المبلغ الإجمالي بالدينار")
        academic_layout.addRow("الرسوم الدراسية:", self.total_fee_edit)
        self.start_date_edit = QDateEdit(); self.start_date_edit.setDate(QDate.currentDate()); self.start_date_edit.setCalendarPopup(True); self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        academic_layout.addRow("تاريخ المباشرة:", self.start_date_edit)
        self.status_combo = QComboBox(); self.status_combo.addItems(["نشط", "منقطع", "متخرج", "منتقل"])
        academic_layout.addRow("الحالة:", self.status_combo)
        content_layout.addLayout(academic_layout)

        # معلومات الاتصال
        contact_layout = QFormLayout()
        contact_layout.setSpacing(8); contact_layout.setLabelAlignment(Qt.AlignRight)
        self.phone_edit = QLineEdit(); self.phone_edit.setPlaceholderText("رقم هاتف الطالب")
        contact_layout.addRow("هاتف الطالب:", self.phone_edit)
        content_layout.addLayout(contact_layout)

        buttons_layout = QHBoxLayout(); buttons_layout.addStretch()
        self.save_btn = QPushButton("حفظ التعديلات")
        self.cancel_btn = QPushButton("إلغاء"); self.cancel_btn.setObjectName("cancel_btn")
        buttons_layout.addWidget(self.save_btn); buttons_layout.addWidget(self.cancel_btn)
        content_layout.addLayout(buttons_layout)

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def apply_responsive_design(self):
        """ضبط تلقائي للحجم والخط حسب دقة الشاشة (تصميم فقط)."""
        try:
            screen = QApplication.primaryScreen().availableGeometry() if QApplication.primaryScreen() else None
            if not screen:
                return
            sw, sh = screen.width(), screen.height()
            target_w = min(720, int(sw * 0.85))
            target_h = min(640, int(sh * 0.88))
            self.resize(target_w, target_h)
            scale = min(sw / 1920.0, sh / 1080.0)
            base = 14
            point_size = max(10, int(base * (0.9 + scale * 0.6)))
            f = self.font(); f.setPointSize(point_size); self.setFont(f)
            if sw <= 1366:
                for btn in self.findChildren(QPushButton):
                    btn.setMinimumHeight(32)
        except Exception as e:
            logging.warning(f"Responsive design adjustment failed (edit dialog): {e}")
        
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
    
    def load_student_data(self):
        """تحميل بيانات الطالب الحالي وتعبئة الحقول"""
        try:
            query = "SELECT * FROM students WHERE id = ?"
            student = db_manager.execute_fetch_one(query, (self.student_id,))
            
            if student:
                self.full_name_edit.setText(student['name'])
                
                # Set gender
                index = self.gender_combo.findText(student['gender'])
                if index != -1:
                    self.gender_combo.setCurrentIndex(index)
                
                # Set school and grade, blocking signals to prevent premature updates
                self.school_combo.blockSignals(True)
                school_id = student['school_id']
                for i in range(self.school_combo.count()):
                    school_data = self.school_combo.itemData(i)
                    if school_data and school_data['id'] == school_id:
                        self.school_combo.setCurrentIndex(i)
                        break
                
                # Populate grades based on selected school after setting the school
                self.update_grades_for_school() 
                index = self.grade_combo.findText(student['grade'])
                if index != -1:
                    self.grade_combo.setCurrentIndex(index)
                self.school_combo.blockSignals(False)
                
                # Set section
                index = self.section_combo.findText(student['section'])
                if index != -1:
                    self.section_combo.setCurrentIndex(index)
                
                self.total_fee_edit.setText(str(student['total_fee']))
                
                # Set start date
                start_date = QDate.fromString(student['start_date'], "yyyy-MM-dd")
                self.start_date_edit.setDate(start_date)
                
                # Set status
                index = self.status_combo.findText(student['status'])
                if index != -1:
                    self.status_combo.setCurrentIndex(index)
                
                self.phone_edit.setText(student['phone'])
            else:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على بيانات الطالب.")
                self.reject()
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الطالب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تحميل بيانات الطالب:\\n{str(e)}")
    
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
                    "مستمع",
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
            errors.append("القسط الكلي مطلوب")
        else:
            try:
                float(total_fee_text)
            except ValueError:
                errors.append("يجب أن يكون القسط الكلي رقماً صحيحاً")
        
        return errors
    
    def save_student(self):
        """حفظ بيانات الطالب"""
        # التحقق من صحة البيانات
        errors = self.validate_inputs()
        if errors:
            QMessageBox.warning(self, "خطأ في البيانات", "\\n".join(errors))
            return
        
        # التحقق من الحالة إذا كانت غير نشط
        selected_status = self.status_combo.currentText()
        if selected_status != "نشط":
            reply = QMessageBox.question(
                self, 
                "تأكيد الحالة", 
                f"الحالة المختارة هي '{selected_status}'. هل أنت متأكد من حفظ الطالب بهذه الحالة؟",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        try:
            school_data = self.school_combo.currentData()
            
            # تحديث البيانات الأساسية
            update_query = """
                UPDATE students SET
                    name = ?, school_id = ?, grade = ?,
                    section = ?, gender = ?, phone = ?,
                    total_fee = ?, start_date = ?, status = ?
                WHERE id = ?
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
                self.status_combo.currentText(),
                self.student_id # WHERE clause
            )
            
            db_manager.execute_query(update_query, student_data)
            
            QMessageBox.information(self, "نجح", "تم تحديث بيانات الطالب بنجاح!")
            self.student_updated.emit()
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
    
    # For testing, provide a dummy student_id
    # You would typically pass a real student ID from the calling context
    dialog = EditStudentDialog(student_id=1) 
    dialog.show()
    
    sys.exit(app.exec_())
