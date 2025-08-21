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
    QSplitter, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
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
        self.load_data()
        
        log_user_action("تم فتح صفحة إنشاء هويات الطلاب")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # عنوان الصفحة
        self.create_header(layout)
        
        
        # خيارات الفلترة والاختيار
        self.create_filter_section(layout)
        
        # جدول الطلاب
        self.create_students_table(layout)
        
        # أزرار الإجراءات
        self.create_action_buttons(layout)
    
    def create_header(self, layout):
        """إنشاء رأس الصفحة"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        
        # أيقونة ومعلومات الصفحة
        title_layout = QVBoxLayout()
        
        title = QLabel("إنشاء هويات الطلاب")
        title.setObjectName("pageTitle")
        title_layout.addWidget(title)
        
        subtitle = QLabel("إنشاء PDF لهويّات طلابية قابلة للطباعة")
        subtitle.setObjectName("pageSubtitle")
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # زر المساعدة
        help_btn = QPushButton("؟")
        help_btn.setObjectName("helpButton")
        help_btn.setFixedSize(30, 30)
        help_btn.clicked.connect(self.show_help)
        header_layout.addWidget(help_btn)
        
        layout.addWidget(header_frame)
    
    def create_id_settings(self, layout):
        """إنشاء إعدادات الهوية"""
        settings_group = QGroupBox("إعدادات الهوية")
        settings_layout = QFormLayout(settings_group)
        
        # اسم المدرسة
        self.school_name_edit = QLineEdit()
        # تحميل اسم المدرسة من الإعدادات
        default_school_name = settings_manager.get_organization_name() or ""
        self.school_name_edit.setText(default_school_name)
        self.school_name_edit.setPlaceholderText("اسم المدرسة الذي سيظهر على الهوية")
        settings_layout.addRow("اسم المدرسة:", self.school_name_edit)
        
        # عنوان الهوية
        self.id_title_edit = QLineEdit("هوية طالب")
        self.id_title_edit.setPlaceholderText("النص الذي سيظهر كعنوان للهوية")
        settings_layout.addRow("عنوان الهوية:", self.id_title_edit)
        
        layout.addWidget(settings_group)
    
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
        columns = ["اختيار", "الاسم", "الصف", "المدرسة", "القسم", "رقم الهاتف"]
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
        
        layout.addWidget(buttons_frame)
    
    def load_data(self):
        """تحميل بيانات الطلاب"""
        try:
            # تحميل بيانات الطلاب من قاعدة البيانات
            query = """
                SELECT s.id, s.name, s.grade, s.section, s.phone, 
                       sc.name_ar as school_name
                FROM students s
                LEFT JOIN schools sc ON s.school_id = sc.id
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
                        'school_name': row[5] or 'غير محدد'
                    }
                    
                    self.students_data.append(student)
                    schools.add(student['school_name'])
                    if student['grade']:
                        grades.add(student['grade'])
                
                # تحديث فلاتر المدارس والصفوف
                self.update_filters(schools, grades)
                
                # تطبيق الفلاتر وعرض البيانات
                self.apply_filters()
                
                log_database_operation("تحميل بيانات الطلاب لإنشاء الهويات", success=True)
                
            else:
                self.students_data = []
                self.filtered_students = []
                self.update_table()
                
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الطلاب: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل البيانات:\n{str(e)}")
    
    def update_filters(self, schools, grades):
        """تحديث قوائم الفلاتر"""
        # تحديث فلتر المدارس
        self.school_filter.clear()
        self.school_filter.addItem("الكل")
        for school in sorted(schools):
            self.school_filter.addItem(school)
        
        # تحديث فلتر الصفوف
        self.grade_filter.clear()
        self.grade_filter.addItem("الكل")
        for grade in sorted(grades):
            self.grade_filter.addItem(grade)
    
    def apply_filters(self):
        """تطبيق الفلاتر على بيانات الطلاب"""
        school_filter = self.school_filter.currentText()
        grade_filter = self.grade_filter.currentText()
        
        self.filtered_students = []
        
        for student in self.students_data:
            # فلتر المدرسة
            if school_filter != "الكل" and student['school_name'] != school_filter:
                continue
            
            # فلتر الصف
            if grade_filter != "الكل" and student['grade'] != grade_filter:
                continue
            
            self.filtered_students.append(student)
        
        self.update_table()
        self.update_selected_count()
    
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
        
        # الحصول على إعدادات الهوية
        school_name = self.school_name_edit.text().strip()
        custom_title = self.id_title_edit.text().strip()
        
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
            'school_name': self.school_name_edit.text() or 'مدرسة النموذج'
        }]
        
        # إنشاء ملف معاينة مؤقت
        temp_dir = Path.home() / "Documents"
        preview_path = temp_dir / f"preview_student_id_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        try:
            school_name = self.school_name_edit.text().strip()
            custom_title = self.id_title_edit.text().strip()
            
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
