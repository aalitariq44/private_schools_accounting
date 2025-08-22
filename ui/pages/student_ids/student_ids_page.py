#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إنشاء هويات الطلاب
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QMenu, QComboBox, QCheckBox, QGroupBox, QFormLayout,
    QFileDialog, QProgressDialog, QApplication, QSizePolicy,
    QSplitter, QScrollArea, QDialog, QDateEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer, QDate
from PyQt5.QtGui import QFont, QIcon, QPixmap, QCursor

import config
from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation
from core.pdf.student_id_generator import generate_student_ids_pdf
from core.utils.settings_manager import settings_manager


class IDGenerationThread(QThread):
    """خيط منفصل لإنشاء PDF الهويات"""
    
    progress_updated = pyqtSignal(int, str)
    generation_completed = pyqtSignal(bool, str)
    
    def __init__(self, students_data, output_path, school_name, custom_title):
        super().__init__()
        self.students_data = students_data
        self.output_path = output_path
        self.school_name = school_name
        self.custom_title = custom_title
    
    def run(self):
        """تشغيل عملية إنشاء PDF"""
        try:
            self.progress_updated.emit(10, "بدء إنشاء الهويات...")
            
            # إنشاء PDF
            success = generate_student_ids_pdf(
                self.students_data,
                self.output_path,
                self.school_name,
                self.custom_title
            )
            
            self.progress_updated.emit(100, "تم اكتمال إنشاء الهويات")
            
            if success:
                self.generation_completed.emit(True, f"تم إنشاء {len(self.students_data)} هوية بنجاح")
            else:
                self.generation_completed.emit(False, "فشل في إنشاء الهويات")
                
        except Exception as e:
            logging.error(f"خطأ في إنشاء الهويات: {e}")
            self.generation_completed.emit(False, f"خطأ في إنشاء الهويات: {str(e)}")


class StudentIDsPage(QWidget):
    """صفحة إنشاء هويات الطلاب"""
    
    def __init__(self):
        super().__init__()
        self.students_data = []
        self.filtered_students = []
        self.current_school_filter = "الكل"
        self.current_grade_filter = "الكل"
        self.selected_students = set()
        
        self.setup_ui()
        self.setup_styles()
        self.load_data()
        
        log_user_action("تم فتح صفحة إنشاء هويات الطلاب")
    
    def setup_styles(self):
        """إعداد أنماط CSS للواجهة"""
        style = """
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QDateEdit[objectName="birthdateEdit"] {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                color: #495057;
            }
            
            QDateEdit[objectName="birthdateEdit"]:hover {
                border-color: #007bff;
                background-color: #fff;
            }
            
            QDateEdit[objectName="birthdateEdit"]:focus {
                border-color: #007bff;
                box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
                background-color: #fff;
            }
            
            QTableWidget {
                gridline-color: #dee2e6;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
                color: #495057;
            }
        """
        self.setStyleSheet(style)
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        
        # خيارات الفلترة والاختيار
        self.create_filter_section(layout)
        
        # جدول الطلاب
        self.create_students_table(layout)
        
        # أزرار الإجراءات
        self.create_action_buttons(layout)
    
    # Header removed as per request
    

    
    def create_filter_section(self, layout):
        """إنشاء قسم الفلترة والاختيار"""
        filter_frame = QFrame()
        filter_frame.setObjectName("filterFrame")
        filter_layout = QVBoxLayout(filter_frame)
        
        # خيارات الفلترة
        filter_options_layout = QHBoxLayout()
        
        # فلتر المدرسة
        school_label = QLabel("المدرسة:")
        self.school_filter = QComboBox()
        self.school_filter.currentTextChanged.connect(self.apply_filters)
        filter_options_layout.addWidget(school_label)
        filter_options_layout.addWidget(self.school_filter)
        
        # فلتر الصف
        grade_label = QLabel("الصف:")
        self.grade_filter = QComboBox()
        self.grade_filter.currentTextChanged.connect(self.apply_filters)
        filter_options_layout.addWidget(grade_label)
        filter_options_layout.addWidget(self.grade_filter)
        
        # إضافة حقل بحث بالاسم
        search_label = QLabel("بحث:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("اسم الطالب")
        self.search_input.textChanged.connect(self.apply_filters)
        filter_options_layout.addWidget(search_label)
        filter_options_layout.addWidget(self.search_input)
        
        # زر لمسح الفلاتر
        clear_filters_btn = QPushButton("مسح الفلاتر")
        clear_filters_btn.clicked.connect(self.clear_filters)
        filter_options_layout.addWidget(clear_filters_btn)
        
        filter_options_layout.addStretch()
        filter_layout.addLayout(filter_options_layout)
        
        # خيارات الاختيار
        selection_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("اختيار الكل")
        self.select_all_btn.clicked.connect(self.select_all_students)
        selection_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("إلغاء اختيار الكل")
        self.deselect_all_btn.clicked.connect(self.deselect_all_students)
        selection_layout.addWidget(self.deselect_all_btn)
        
        self.invert_selection_btn = QPushButton("عكس الاختيار")
        self.invert_selection_btn.clicked.connect(self.invert_selection)
        selection_layout.addWidget(self.invert_selection_btn)
        
        selection_layout.addStretch()
        
        # عدد الطلاب المختارين
        self.selected_count_label = QLabel("الطلاب المختارون: 0")
        self.selected_count_label.setObjectName("selectedCountLabel")
        selection_layout.addWidget(self.selected_count_label)
        # Add label for total displayed students
        self.displayed_count_label = QLabel("عدد الطلاب المعروضين: 0")
        self.displayed_count_label.setObjectName("displayedCountLabel")
        selection_layout.addWidget(self.displayed_count_label)
        
        filter_layout.addLayout(selection_layout)
        layout.addWidget(filter_frame)
    
    def create_students_table(self, layout):
        """إنشاء جدول الطلاب"""
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        table_layout = QVBoxLayout(table_frame)
        
        # إنشاء الجدول
        self.students_table = QTableWidget()
        self.students_table.setObjectName("studentsTable")
        
        # إعداد أعمدة الجدول
        columns = ["اختيار", "الاسم", "الصف", "المدرسة", "القسم", "رقم الهاتف", "تاريخ الميلاد"]
        self.students_table.setColumnCount(len(columns))
        self.students_table.setHorizontalHeaderLabels(columns)
        
        # إعداد خصائص الجدول
        self.students_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.students_table.setAlternatingRowColors(True)
        self.students_table.setSortingEnabled(True)
        
        # تعديل حجم الأعمدة
        header = self.students_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # عمود الاختيار
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # الاسم
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # الصف
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # المدرسة
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # القسم
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # الهاتف
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # تاريخ الميلاد
        
        self.students_table.setColumnWidth(0, 60)  # عرض عمود الاختيار
        
        table_layout.addWidget(self.students_table)
        layout.addWidget(table_frame)
    
    def create_action_buttons(self, layout):
        """إنشاء أزرار الإجراءات"""
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        
        # زر تحديث البيانات
        refresh_btn = QPushButton("تحديث البيانات")
        refresh_btn.setObjectName("refreshButton")
        refresh_btn.clicked.connect(self.refresh_data)
        buttons_layout.addWidget(refresh_btn)
        
        buttons_layout.addStretch()
        
        # زر إنشاء الهويات
        self.generate_btn = QPushButton("إنشاء PDF الهويات")
        self.generate_btn.setObjectName("generateButton")
        self.generate_btn.clicked.connect(self.generate_student_ids)
        buttons_layout.addWidget(self.generate_btn)
        
        # زر معاينة قالب
        preview_btn = QPushButton("معاينة القالب")
        preview_btn.setObjectName("previewButton")
        preview_btn.clicked.connect(self.preview_template)
        buttons_layout.addWidget(preview_btn)
        
        # زر إدارة القوالب
        template_btn = QPushButton("إدارة القوالب")
        template_btn.setObjectName("templateButton")
        template_btn.clicked.connect(self.manage_templates)
        buttons_layout.addWidget(template_btn)
        
        layout.addWidget(buttons_frame)
    
    def load_data(self):
        """تحميل بيانات الطلاب"""
        try:
            # تحميل بيانات الطلاب من قاعدة البيانات
            query = """
                SELECT s.id, s.name, s.grade, s.section, s.phone, s.birthdate,
                       sc.name_ar as school_name
                FROM students s
                LEFT JOIN schools sc ON s.school_id = sc.id
                WHERE s.status = 'نشط'
                ORDER BY s.name
            """
            
            result = db_manager.execute_query(query)
            
            if result:
                self.students_data = []
                schools = set()
                grades = set()
                
                for row in result:
                    student = {
                        'id': row[0],
                        'name': row[1] or '',
                        'grade': row[2] or '',
                        'section': row[3] or '',
                        'phone': row[4] or '',
                        'birthdate': row[5] or '',
                        'school_name': row[6] or 'غير محدد'
                    }
                    
                    self.students_data.append(student)
                    schools.add(student['school_name'])
                    if student['grade']:
                        grades.add(student['grade'])
                
                # تحديث فلاتر المدارس والصفوف
                self.update_filters(schools, grades)
                
                # تطبيق الفلاتر وعرض البيانات
                self.apply_filters()
                
                log_database_operation("تحميل بيانات الطلاب", "students", "لإنشاء الهويات")
                
            else:
                self.students_data = []
                self.filtered_students = []
                self.update_table()
                
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الطلاب: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل البيانات:\n{str(e)}")
    
    def sort_grades(self, grades):
        """ترتيب الصفوف حسب المراحل التعليمية"""
        # تعريف ترتيب الصفوف
        grade_order = {
            # الابتدائي
            'الأول الابتدائي': 1,
            'الثاني الابتدائي': 2,
            'الثالث الابتدائي': 3,
            'الرابع الابتدائي': 4,
            'الخامس الابتدائي': 5,
            'السادس الابتدائي': 6,
            
            # المتوسط
            'الأول المتوسط': 7,
            'الثاني المتوسط': 8,
            'الثالث المتوسط': 9,
            
            # الإعدادي
            'الرابع العلمي': 10,
            'الرابع الأدبي': 11,
            'الخامس العلمي': 12,
            'الخامس الأدبي': 13,
            'السادس العلمي': 14,
            'السادس الأدبي': 15
        }
        
        # فلترة الصفوف لإزالة Grade 1 والصفوف غير المعرَّفة
        filtered_grades = []
        for grade in grades:
            if grade and grade != 'Grade 1' and grade in grade_order:
                filtered_grades.append(grade)
        
        # ترتيب الصفوف
        return sorted(filtered_grades, key=lambda x: grade_order.get(x, 999))
    
    def update_filters(self, schools, grades):
        """تحديث قوائم الفلاتر"""
        # تحديث فلتر المدارس
        self.school_filter.clear()
        self.school_filter.addItem("الكل")
        for school in sorted(schools):
            self.school_filter.addItem(school)
        
        # تحديث فلتر الصفوف مع ترتيب مخصص
        self.grade_filter.clear()
        self.grade_filter.addItem("الكل")
        sorted_grades = self.sort_grades(grades)
        for grade in sorted_grades:
            self.grade_filter.addItem(grade)
    
    def apply_filters(self):
        """تطبيق الفلاتر على بيانات الطلاب"""
        school_filter = self.school_filter.currentText()
        grade_filter = self.grade_filter.currentText()
        # إضافة فلتر البحث بالنص
        search_text = self.search_input.text().strip().lower()
        
        self.filtered_students = []
        
        for student in self.students_data:
            # فلتر المدرسة
            if school_filter != "الكل" and student['school_name'] != school_filter:
                continue
            
            # فلتر الصف
            if grade_filter != "الكل" and student['grade'] != grade_filter:
                continue
            # فلتر البحث بالاسم
            if search_text and search_text not in student['name'].lower():
                continue
            
            self.filtered_students.append(student)
        
        self.update_table()
        self.update_selected_count()
        self.update_displayed_count()  # Update displayed students count
    
    def update_table(self):
        """تحديث جدول الطلاب"""
        self.students_table.setRowCount(len(self.filtered_students))
        
        for row, student in enumerate(self.filtered_students):
            # عمود الاختيار
            checkbox = QCheckBox()
            checkbox.setChecked(student['id'] in self.selected_students)
            checkbox.stateChanged.connect(
                lambda state, student_id=student['id']: self.toggle_student_selection(student_id, state)
            )
            self.students_table.setCellWidget(row, 0, checkbox)
            
            # باقي الأعمدة
            self.students_table.setItem(row, 1, QTableWidgetItem(student['name']))
            self.students_table.setItem(row, 2, QTableWidgetItem(student['grade']))
            self.students_table.setItem(row, 3, QTableWidgetItem(student['school_name']))
            self.students_table.setItem(row, 4, QTableWidgetItem(student['section']))
            self.students_table.setItem(row, 5, QTableWidgetItem(student['phone']))
            
            # عمود تاريخ الميلاد مع زر لتعديل التاريخ
            # استخدام QLabel لعرض التاريخ أو فراغ
            birthdate_label = QLabel()
            birthdate_label.setObjectName("birthdateLabel")
            birthdate_label.setStyleSheet("padding: 4px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px;")
            
            # عرض التاريخ إن وجد، وإلا عرض فراغ
            if student['birthdate']:
                birthdate_label.setText(student['birthdate'])
            else:
                birthdate_label.setText("")
            
            # زر تعديل التاريخ
            edit_btn = QPushButton("✏")
            edit_btn.setFixedWidth(25)
            edit_btn.clicked.connect(
                lambda _, student_id=student['id'], row_idx=row: self.edit_birthdate(student_id, row_idx)
            )
            
            # تجميع ويدجت الخلية
            container = QWidget()
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.addWidget(birthdate_label)
            h_layout.addWidget(edit_btn)
            self.students_table.setCellWidget(row, 6, container)
    
    def edit_birthdate(self, student_id, row_idx):
        """فتح نافذة تعديل تاريخ الميلاد"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QDialogButtonBox
        
        # البحث عن بيانات الطالب
        student = None
        for s in self.filtered_students:
            if s['id'] == student_id:
                student = s
                break
        
        if not student:
            return
        
        # إنشاء نافذة التعديل
        dialog = QDialog(self)
        dialog.setWindowTitle(f"تعديل تاريخ ميلاد: {student['name']}")
        dialog.setModal(True)
        dialog.resize(300, 150)
        
        layout = QVBoxLayout(dialog)
        
        # حقل تاريخ الميلاد
        birthdate_edit = QDateEdit()
        birthdate_edit.setCalendarPopup(True)
        birthdate_edit.setDisplayFormat("yyyy-MM-dd")
        birthdate_edit.setMaximumDate(QDate.currentDate())
        
        # تعيين التاريخ الحالي إن وجد
        if student['birthdate']:
            try:
                date = QDate.fromString(student['birthdate'], "yyyy-MM-dd")
                if date.isValid():
                    birthdate_edit.setDate(date)
                else:
                    birthdate_edit.setDate(QDate.currentDate().addYears(-10))
            except:
                birthdate_edit.setDate(QDate.currentDate().addYears(-10))
        else:
            birthdate_edit.setDate(QDate.currentDate().addYears(-10))
        
        layout.addWidget(QLabel("تاريخ الميلاد:"))
        layout.addWidget(birthdate_edit)
        
        # أزرار الحفظ والإلغاء
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # عرض النافذة
        if dialog.exec_() == QDialog.Accepted:
            new_date = birthdate_edit.date()
            self.update_student_birthdate_from_dialog(student_id, new_date, row_idx)
    
    def update_student_birthdate_from_dialog(self, student_id, date, row_idx):
        """تحديث تاريخ ميلاد الطالب من نافذة التعديل"""
        try:
            birthdate_str = date.toString("yyyy-MM-dd")
            
            # تحديث قاعدة البيانات
            update_query = "UPDATE students SET birthdate = ? WHERE id = ?"
            result = db_manager.execute_update(update_query, (birthdate_str, student_id))
            
            if result:
                # تحديث البيانات في الذاكرة
                for student in self.students_data:
                    if student['id'] == student_id:
                        student['birthdate'] = birthdate_str
                        break
                
                for student in self.filtered_students:
                    if student['id'] == student_id:
                        student['birthdate'] = birthdate_str
                        break
                
                # تحديث عرض الجدول
                container = self.students_table.cellWidget(row_idx, 6)
                if container:
                    label = container.findChild(QLabel)
                    if label:
                        label.setText(birthdate_str)
                
                log_user_action(f"تحديث تاريخ ميلاد الطالب {student_id} إلى {birthdate_str}")
                QMessageBox.information(self, "نجح", "تم تحديث تاريخ الميلاد بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "فشل في تحديث تاريخ الميلاد")
                
        except Exception as e:
            logging.error(f"خطأ في تحديث تاريخ الميلاد: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في تحديث تاريخ الميلاد: {str(e)}")

    def update_student_birthdate(self, student_id, date):
        """تحديث تاريخ ميلاد الطالب في قاعدة البيانات والذاكرة"""
        try:
            birthdate_str = date.toString("yyyy-MM-dd")
            
            # تحديث قاعدة البيانات
            update_query = "UPDATE students SET birthdate = ? WHERE id = ?"
            result = db_manager.execute_update(update_query, (birthdate_str, student_id))
            
            if result:
                # تحديث البيانات في الذاكرة
                for student in self.students_data:
                    if student['id'] == student_id:
                        student['birthdate'] = birthdate_str
                        break
                
                for student in self.filtered_students:
                    if student['id'] == student_id:
                        student['birthdate'] = birthdate_str
                        break
                
                log_user_action(f"تحديث تاريخ ميلاد الطالب {student_id} إلى {birthdate_str}")
            else:
                QMessageBox.warning(self, "خطأ", "فشل في تحديث تاريخ الميلاد")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث تاريخ الميلاد: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في تحديث تاريخ الميلاد: {str(e)}")
    
    def toggle_student_selection(self, student_id, state):
        """تغيير حالة اختيار الطالب"""
        if state == Qt.Checked:
            self.selected_students.add(student_id)
        else:
            self.selected_students.discard(student_id)
        
        self.update_selected_count()
    
    def select_all_students(self):
        """اختيار جميع الطلاب المرئيين"""
        for student in self.filtered_students:
            self.selected_students.add(student['id'])
        self.update_table()
        self.update_selected_count()
    
    def deselect_all_students(self):
        """إلغاء اختيار جميع الطلاب"""
        self.selected_students.clear()
        self.update_table()
        self.update_selected_count()
    
    def invert_selection(self):
        """عكس الاختيار"""
        for student in self.filtered_students:
            if student['id'] in self.selected_students:
                self.selected_students.remove(student['id'])
            else:
                self.selected_students.add(student['id'])
        self.update_table()
        self.update_selected_count()
    
    def update_selected_count(self):
        """تحديث عداد الطلاب المختارين"""
        count = len(self.selected_students)
        self.selected_count_label.setText(f"الطلاب المختارون: {count}")
        
        # تمكين/تعطيل زر الإنشاء
        self.generate_btn.setEnabled(count > 0)
    
    def update_displayed_count(self):
        """تحديث عداد الطلاب المعروضين"""
        count = len(self.filtered_students)
        self.displayed_count_label.setText(f"عدد الطلاب المعروضين: {count}")
    
    def clear_filters(self):
        """إعادة تعيين جميع الفلاتر"""
        # إعادة تعيين فلتر المدرسة والصف وحق البحث
        self.school_filter.setCurrentIndex(0)
        self.grade_filter.setCurrentIndex(0)
        self.search_input.clear()
        # إعادة تطبيق الفلاتر
        self.apply_filters()
    
    def refresh_data(self):
        """تحديث البيانات"""
        self.load_data()
    
    def generate_student_ids(self):
        """إنشاء PDF الهويات للطلاب المختارين"""
        if not self.selected_students:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار طالب واحد على الأقل")
            return
        
        # الحصول على بيانات الطلاب المختارين
        selected_data = []
        for student in self.students_data:
            if student['id'] in self.selected_students:
                selected_data.append(student)
        
        # اختيار مكان حفظ الملف
        default_filename = f"student_ids_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "حفظ PDF الهويات",
            default_filename,
            "ملفات PDF (*.pdf)"
        )
        
        if not output_path:
            return
        
        # الحصول على إعدادات الهوية الافتراضية
        school_name = settings_manager.get_organization_name() or "مدرسة"
        custom_title = "هوية طالب"
        
        # إنشاء نافذة التقدم
        progress_dialog = QProgressDialog("جاري إنشاء الهويات...", "إلغاء", 0, 100, self)
        progress_dialog.setWindowTitle("إنشاء الهويات")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()
        
        # بدء عملية الإنشاء في خيط منفصل
        self.generation_thread = IDGenerationThread(
            selected_data, output_path, school_name, custom_title
        )
        
        self.generation_thread.progress_updated.connect(
            lambda value, text: (
                progress_dialog.setValue(value),
                progress_dialog.setLabelText(text)
            )
        )
        
        self.generation_thread.generation_completed.connect(
            lambda success, message: self.on_generation_completed(
                success, message, output_path, progress_dialog
            )
        )
        
        progress_dialog.canceled.connect(self.generation_thread.terminate)
        self.generation_thread.start()
    
    def on_generation_completed(self, success, message, output_path, progress_dialog):
        """معالجة اكتمال إنشاء الهويات"""
        progress_dialog.close()
        
        if success:
            # رسالة نجح
            reply = QMessageBox.question(
                self,
                "نجح الإنشاء",
                f"{message}\n\nهل تريد فتح الملف؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                try:
                    # فتح الملف بالبرنامج الافتراضي
                    import subprocess
                    subprocess.Popen([output_path], shell=True)
                except Exception as e:
                    logging.warning(f"فشل في فتح الملف: {e}")
                    QMessageBox.information(
                        self,
                        "معلومات",
                        f"تم حفظ الملف في:\n{output_path}"
                    )
            
            log_user_action(f"تم إنشاء {len(self.selected_students)} هوية طالب")
            
        else:
            QMessageBox.critical(self, "خطأ", message)
    
    def preview_template(self):
        """معاينة قالب الهوية"""
        # إنشاء هوية تجريبية للمعاينة
        sample_data = [{
            'name': 'أحمد محمد علي السامرائي',
            'grade': 'الصف الثالث الابتدائي',
            'school_name': settings_manager.get_organization_name() or "مدرسة النموذج"
        }]
        
        # إنشاء ملف معاينة مؤقت
        temp_dir = Path.home() / "Documents"
        preview_path = temp_dir / f"preview_student_id_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        try:
            school_name = settings_manager.get_organization_name() or "مدرسة"
            custom_title = "هوية طالب"
            
            success = generate_student_ids_pdf(
                sample_data,
                str(preview_path),
                school_name,
                custom_title
            )
            
            if success:
                # فتح المعاينة
                import subprocess
                subprocess.Popen([str(preview_path)], shell=True)
            else:
                QMessageBox.warning(self, "خطأ", "فشل في إنشاء المعاينة")
                
        except Exception as e:
            logging.error(f"خطأ في معاينة القالب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في المعاينة:\n{str(e)}")
    
    def manage_templates(self):
        """إدارة القوالب"""
        # إنشاء نافذة إدارة القوالب
        dialog = QMessageBox(self)
        dialog.setWindowTitle("إدارة القوالب")
        dialog.setIcon(QMessageBox.Information)
        
        template_actions = [
            ("محرر القوالب المرئي", self.open_visual_editor),
            ("حفظ القالب الحالي", self.save_current_template),
            ("تصدير القالب إلى JSON", self.export_template),
            ("استيراد قالب من JSON", self.import_template),
            ("إعادة تعيين القالب الافتراضي", self.reset_template)
        ]
        
        action_text = "اختر إجراءاً:\n\n"
        for i, (name, _) in enumerate(template_actions, 1):
            action_text += f"{i}. {name}\n"
        
        dialog.setText(action_text)
        
        # إضافة أزرار مخصصة
        for name, action in template_actions:
            btn = dialog.addButton(name, QMessageBox.ActionRole)
            btn.clicked.connect(action)
        
        dialog.addButton("إلغاء", QMessageBox.RejectRole)
        dialog.exec_()
    
    def open_visual_editor(self):
        """فتح محرر القوالب المرئي"""
        try:
            from ui.dialogs.template_editor import TemplateEditor
            
            editor = TemplateEditor(self)
            result = editor.exec_()
            
            if result == QDialog.Accepted:
                QMessageBox.information(self, "نجح", "تم تحديث القالب بنجاح")
                
        except ImportError:
            QMessageBox.warning(self, "خطأ", "محرر القوالب المرئي غير متوفر")
        except Exception as e:
            logging.error(f"خطأ في فتح محرر القوالب: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في فتح محرر القوالب:\n{str(e)}")
    
    def save_current_template(self):
        """حفظ القالب الحالي"""
        try:
            from templates.id_template import save_template_as_json
            
            template_dir = Path(__file__).parent.parent.parent.parent / "templates"
            template_file = template_dir / "id_template.json"
            
            save_template_as_json(template_file)
            QMessageBox.information(self, "نجح", f"تم حفظ القالب في:\n{template_file}")
            
        except Exception as e:
            logging.error(f"خطأ في حفظ القالب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ القالب:\n{str(e)}")
    
    def export_template(self):
        """تصدير القالب إلى ملف JSON"""
        try:
            from templates.id_template import save_template_as_json
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "تصدير القالب",
                f"id_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "ملفات JSON (*.json)"
            )
            
            if file_path:
                save_template_as_json(file_path)
                QMessageBox.information(self, "نجح", f"تم تصدير القالب إلى:\n{file_path}")
                
        except Exception as e:
            logging.error(f"خطأ في تصدير القالب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تصدير القالب:\n{str(e)}")
    
    def import_template(self):
        """استيراد قالب من ملف JSON"""
        try:
            from templates.id_template import load_template_from_json
            
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "استيراد القالب",
                "",
                "ملفات JSON (*.json)"
            )
            
            if file_path:
                success = load_template_from_json(file_path)
                if success:
                    QMessageBox.information(self, "نجح", "تم استيراد القالب بنجاح")
                else:
                    QMessageBox.warning(self, "خطأ", "فشل في استيراد القالب")
                    
        except Exception as e:
            logging.error(f"خطأ في استيراد القالب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في استيراد القالب:\n{str(e)}")
    
    def reset_template(self):
        """إعادة تعيين القالب الافتراضي"""
        reply = QMessageBox.question(
            self,
            "تأكيد",
            "هل أنت متأكد من إعادة تعيين القالب إلى الإعدادات الافتراضية؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                from templates.id_template import ensure_default_template
                ensure_default_template()
                QMessageBox.information(self, "نجح", "تم إعادة تعيين القالب الافتراضي")
                
            except Exception as e:
                logging.error(f"خطأ في إعادة تعيين القالب: {e}")
                QMessageBox.critical(self, "خطأ", f"فشل في إعادة تعيين القالب:\n{str(e)}")
    
    def show_help(self):
        """عرض نافذة المساعدة"""
        help_text = """
        <h3>نظام إنشاء هويات الطلاب</h3>
        
        <p><b>الهدف:</b> إنشاء ملف PDF يحتوي على هويات طلابية قابلة للطباعة</p>
        
        <p><b>المميزات:</b></p>
        <ul>
        <li>حجم الهوية: ISO ID-1 (حجم بطاقة ماستر كارد)</li>
        <li>تخطيط A4: 10 هويات في الصفحة الواحدة (2×5)</li>
        <li>علامات قطع للمساعدة في القص</li>
        <li>قالب قابل للتعديل</li>
        </ul>
        
        <p><b>محتوى الهوية:</b></p>
        <ul>
        <li>اسم المدرسة</li>
        <li>اسم الطالب</li>
        <li>الصف الدراسي</li>
        <li>العام الدراسي: 2025-2026</li>
        <li>مربع فارغ للصورة</li>
        <li>خانة QR (مؤقتة)</li>
        <li>خانة تاريخ الميلاد (للكتابة اليدوية)</li>
        </ul>
        
        <p><b>كيفية الاستخدام:</b></p>
        <ol>
        <li>اختر المدرسة والصف (أو الكل)</li>
        <li>حدد الطلاب المطلوبين</li>
        <li>أدخل اسم المدرسة وعنوان الهوية</li>
        <li>اضغط "إنشاء PDF الهويات"</li>
        <li>احفظ الملف في المكان المطلوب</li>
        </ol>
        """
        
        QMessageBox.information(self, "المساعدة - إنشاء هويات الطلاب", help_text)
