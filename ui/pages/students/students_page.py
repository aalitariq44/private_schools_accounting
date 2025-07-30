#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة الطلاب - محدثة
"""

import logging
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QMenu, QComboBox, QDateEdit, QSpinBox, QAction, QDialog,
    QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation
from core.printing.print_manager import print_students_list  # استيراد دالة الطباعة

# استيراد نوافذ إدارة الطلاب
from .add_student_dialog import AddStudentDialog
from .edit_student_dialog import EditStudentDialog
from .add_group_students_dialog import AddGroupStudentsDialog


class StudentsPage(QWidget):
    """صفحة إدارة الطلاب"""
    
    # إشارات النافذة
    page_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_students = []
        self.selected_school_id = None
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_schools()
        
        log_user_action("فتح صفحة إدارة الطلاب")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            
            # شريط الأدوات والفلاتر
            self.create_toolbar(layout)
            
            # جدول الطلاب
            self.create_students_table(layout)
            
            # ملخص الطلاب
            self.create_summary(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة الطلاب: {e}")
            raise
    
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات والفلاتر"""
        try:
            toolbar_frame = QFrame()
            toolbar_frame.setObjectName("toolbarFrame")
            
            toolbar_layout = QVBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(15, 10, 15, 10)
            toolbar_layout.setSpacing(10)
            
            # الصف الأول - فلاتر أساسية
            filters_layout = QHBoxLayout()
            
            # فلتر المدرسة
            school_label = QLabel("المدرسة:")
            school_label.setObjectName("filterLabel")
            filters_layout.addWidget(school_label)
            
            self.school_combo = QComboBox()
            self.school_combo.setObjectName("filterCombo")
            self.school_combo.setMinimumWidth(200)
            filters_layout.addWidget(self.school_combo)
            
            # فلتر الصف
            grade_label = QLabel("الصف:")
            grade_label.setObjectName("filterLabel")
            filters_layout.addWidget(grade_label)
            
            self.grade_combo = QComboBox()
            self.grade_combo.setObjectName("filterCombo")
            self.grade_combo.addItems(["جميع الصفوف", "الأول الابتدائي", "الثاني الابتدائي", 
                                      "الثالث الابتدائي", "الرابع الابتدائي", "الخامس الابتدائي", 
                                      "السادس الابتدائي", "الأول المتوسط", "الثاني المتوسط", 
                                      "الثالث المتوسط", "الرابع العلمي", "الرابع الأدبي",
                                      "الخامس العلمي", "الخامس الأدبي", "السادس العلمي", "السادس الأدبي"])
            filters_layout.addWidget(self.grade_combo)
            
            # فلتر الحالة
            status_label = QLabel("الحالة:")
            status_label.setObjectName("filterLabel")
            filters_layout.addWidget(status_label)
            
            self.status_combo = QComboBox()
            self.status_combo.setObjectName("filterCombo")
            self.status_combo.addItems(["جميع الحالات", "نشط", "منقطع", "متخرج", "محول"])
            filters_layout.addWidget(self.status_combo)
            
            # فلتر الجنس
            gender_label = QLabel("الجنس:")
            gender_label.setObjectName("filterLabel")
            filters_layout.addWidget(gender_label)
            self.gender_combo = QComboBox()
            self.gender_combo.setObjectName("filterCombo")
            self.gender_combo.addItems(["جميع الطلاب", "ذكر", "أنثى"])
            filters_layout.addWidget(self.gender_combo)
            
            filters_layout.addStretch()
            
            toolbar_layout.addLayout(filters_layout)
            
            # الصف الثاني - البحث والعمليات
            actions_layout = QHBoxLayout()
            
            # مربع البحث
            search_label = QLabel("البحث:")
            search_label.setObjectName("filterLabel")
            actions_layout.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setObjectName("searchInput")
            self.search_input.setPlaceholderText("ابحث في أسماء الطلاب...")
            self.search_input.setMinimumWidth(300)
            actions_layout.addWidget(self.search_input)
            
            actions_layout.addStretch()
            
            # أزرار العمليات
            self.add_student_button = QPushButton("إضافة طالب")
            self.add_student_button.setObjectName("primaryButton")
            actions_layout.addWidget(self.add_student_button)
            
            self.add_group_students_button = QPushButton("إضافة مجموعة طلاب")
            self.add_group_students_button.setObjectName("groupButton")
            actions_layout.addWidget(self.add_group_students_button)
            
            self.print_list_button = QPushButton("طباعة قائمة الطلاب")
            self.print_list_button.setObjectName("secondaryButton")  # Use secondary style for different color
            actions_layout.addWidget(self.print_list_button)
            
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("refreshButton")
            actions_layout.addWidget(self.refresh_button)
            
            self.clear_filters_button = QPushButton("مسح الفلاتر")
            self.clear_filters_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.clear_filters_button)
            
            toolbar_layout.addLayout(actions_layout)
            
            layout.addWidget(toolbar_frame)
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
            raise
    
    def create_students_table(self, layout):
        """إنشاء جدول الطلاب"""
        try:
            # إطار الجدول
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")

            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)  # إزالة الهوامش تمامًا

            # الجدول
            self.students_table = QTableWidget()
            self.students_table.setObjectName("dataTable")

            # إعداد أعمدة الجدول
            columns = ["المعرف", "الاسم", "المدرسة", "الصف", "الشعبة", "الجنس", "الهاتف", "الحالة", "الرسوم الدراسية", "الإجراءات"]
            self.students_table.setColumnCount(len(columns))
            self.students_table.setHorizontalHeaderLabels(columns)

            # إعداد خصائص الجدول
            self.students_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.students_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.students_table.setAlternatingRowColors(True)
            self.students_table.setSortingEnabled(True)

            # إعداد حجم الأعمدة
            header = self.students_table.horizontalHeader()
            header.setStretchLastSection(True)
            for i in range(len(columns) - 1):
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

            # إزالة الحشوات داخل الصفوف
            self.students_table.setStyleSheet("QTableWidget::item { padding: 0px; }")

            # ربط الأحداث
            self.students_table.cellDoubleClicked.connect(self.edit_student)
            self.students_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.students_table.customContextMenuRequested.connect(self.show_context_menu)

            table_layout.addWidget(self.students_table)
            layout.addWidget(table_frame)

        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول الطلاب: {e}")
            raise
    
    def create_summary(self, layout):
        """إنشاء ملخص الطلاب"""
        try:
            summary_frame = QFrame()
            summary_frame.setObjectName("summaryFrame")
            
            summary_layout = QHBoxLayout(summary_frame)
            summary_layout.setContentsMargins(15, 10, 15, 10)
            
            # ملخص الأرقام
            numbers_layout = QVBoxLayout()
            
            summary_title = QLabel("ملخص الطلاب")
            summary_title.setObjectName("summaryTitle")
            numbers_layout.addWidget(summary_title)
            
            numbers_grid = QHBoxLayout()
            
            # إجمالي الطلاب
            total_layout = QVBoxLayout()
            self.total_students_label = QLabel("إجمالي الطلاب")
            self.total_students_label.setObjectName("summaryLabel")
            total_layout.addWidget(self.total_students_label)
            
            self.total_students_value = QLabel("0")
            self.total_students_value.setObjectName("summaryValue")
            total_layout.addWidget(self.total_students_value)
            numbers_grid.addLayout(total_layout)
            
            # الطلاب النشطون
            active_layout = QVBoxLayout()
            self.active_students_label = QLabel("النشطون")
            self.active_students_label.setObjectName("summaryLabel")
            active_layout.addWidget(self.active_students_label)
            
            self.active_students_value = QLabel("0")
            self.active_students_value.setObjectName("summaryValueSuccess")
            active_layout.addWidget(self.active_students_value)
            numbers_grid.addLayout(active_layout)
            
            # الطلاب غير النشطين (منقطع، متخرج، محول)
            inactive_layout = QVBoxLayout()
            self.inactive_students_label = QLabel("غير النشطين")
            self.inactive_students_label.setObjectName("summaryLabel")
            inactive_layout.addWidget(self.inactive_students_label)
            
            self.inactive_students_value = QLabel("0")
            self.inactive_students_value.setObjectName("summaryValueWarning")
            inactive_layout.addWidget(self.inactive_students_value)
            numbers_grid.addLayout(inactive_layout)
            
            numbers_layout.addLayout(numbers_grid)
            summary_layout.addLayout(numbers_layout)
            
            # إحصائيات أخرى
            stats_layout = QVBoxLayout()
            
            self.displayed_count_label = QLabel("عدد الطلاب المعروضين: 0")
            self.displayed_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.displayed_count_label)
            
            self.male_students_label = QLabel("الذكور: 0")
            self.male_students_label.setObjectName("statLabel")
            stats_layout.addWidget(self.male_students_label)
            
            self.female_students_label = QLabel("الإناث: 0")
            self.female_students_label.setObjectName("statLabel")
            stats_layout.addWidget(self.female_students_label)
            
            summary_layout.addLayout(stats_layout)
            
            # معلومات آخر تحديث
            self.last_update_label = QLabel("آخر تحديث: --")
            self.last_update_label.setObjectName("statLabel")
            summary_layout.addWidget(self.last_update_label)
            
            layout.addWidget(summary_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء ملخص الطلاب: {e}")
            raise
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            # ربط أزرار العمليات
            self.add_student_button.clicked.connect(self.add_student)
            self.add_group_students_button.clicked.connect(self.add_group_students)
            self.print_list_button.clicked.connect(self.print_student_list)
            self.refresh_button.clicked.connect(self.refresh)
            self.clear_filters_button.clicked.connect(self.clear_filters)
            
            # ربط الفلاتر
            self.school_combo.currentTextChanged.connect(self.apply_filters)
            self.grade_combo.currentTextChanged.connect(self.apply_filters)
            self.status_combo.currentTextChanged.connect(self.apply_filters)
            self.gender_combo.currentTextChanged.connect(self.apply_filters)
            self.search_input.textChanged.connect(self.apply_filters)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            self.school_combo.clear()
            self.school_combo.addItem("جميع المدارس", None)
            
            # جلب المدارس من قاعدة البيانات
            query = "SELECT id, name_ar FROM schools ORDER BY name_ar"
            schools = db_manager.execute_query(query)
            
            if schools:
                for school in schools:
                    self.school_combo.addItem(school['name_ar'], school['id'])
            
            # تحميل الطلاب بعد تحميل المدارس
            self.refresh()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
    
    def load_students(self):
        """تحميل قائمة الطلاب"""
        try:
            # بناء الاستعلام مع الفلاتر
            query = """
                SELECT s.id, s.name, sc.name_ar as school_name,
                       s.grade, s.section, s.gender,
                       s.phone, s.status, s.start_date, s.total_fee
                FROM students s
                LEFT JOIN schools sc ON s.school_id = sc.id
                WHERE 1=1
            """
            params = []
            
            # فلتر المدرسة
            selected_school_id = self.school_combo.currentData()
            if selected_school_id:
                query += " AND s.school_id = ?"
                params.append(selected_school_id)
            
            # فلتر الصف
            selected_grade = self.grade_combo.currentText()
            if selected_grade and selected_grade != "جميع الصفوف":
                query += " AND s.grade = ?"
                params.append(selected_grade)
            
            # فلتر الحالة
            selected_status = self.status_combo.currentText()
            if selected_status and selected_status != "جميع الحالات":
                query += " AND s.status = ?"
                params.append(selected_status)
            
            # فلتر الجنس
            selected_gender = self.gender_combo.currentText()
            if selected_gender and selected_gender != "جميع الطلاب":
                query += " AND s.gender = ?"
                params.append(selected_gender)
            
            # فلتر البحث
            search_text = self.search_input.text().strip()
            if search_text:
                query += " AND s.name LIKE ?"
                params.append(f"%{search_text}%")
            
            query += " ORDER BY s.name"
            
            # تنفيذ الاستعلام
            self.current_students = db_manager.execute_query(query, tuple(params))
            
            # ملء الجدول
            self.fill_students_table()
            
            # تحديث الإحصائيات
            self.update_stats()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الطلاب: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل بيانات الطلاب:\\n{str(e)}")
    
    def fill_students_table(self):
        """ملء جدول الطلاب بالبيانات"""
        try:
            # تنظيف الجدول
            self.students_table.setRowCount(0)
            
            if not self.current_students:
                self.displayed_count_label.setText("عدد الطلاب المعروضين: 0")
                return
            
            # ملء الجدول
            for row_idx, student in enumerate(self.current_students):
                self.students_table.insertRow(row_idx)
                
                # البيانات الأساسية
                items = [
                    str(student['id']),
                    student['name'] or "",
                    student['school_name'] or "",
                    student['grade'] or "",
                    student['section'] or "",
                    student['gender'] or "",
                    student['phone'] or "",
                    student['status'] or "",
                    str(student['total_fee']) if student['total_fee'] else "0"
                ]
                
                for col_idx, item_text in enumerate(items):
                    item = QTableWidgetItem(item_text)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.students_table.setItem(row_idx, col_idx, item)
                
                # أزرار الإجراءات
                actions_widget = self.create_actions_widget(student['id'])
                self.students_table.setCellWidget(row_idx, 9, actions_widget)
            
            # تحديث العداد
            self.displayed_count_label.setText(f"عدد الطلاب المعروضين: {len(self.current_students)}")
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول الطلاب: {e}")
    
    def create_actions_widget(self, student_id):
        """إنشاء ويدجت الإجراءات لكل صف"""
        try:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)  # إزالة الهوامش لتحسين استخدام المساحة
            layout.setSpacing(10)  # تقليل التباعد بين الأزرار

            # زر التعديل
            edit_btn = QPushButton("تعديل")
            edit_btn.setObjectName("editButton")
            edit_btn.setFixedSize(120, 40)  # ضبط حجم الزر بشكل ثابت
            edit_btn.clicked.connect(lambda: self.edit_student_by_id(student_id))
            layout.addWidget(edit_btn)

            # زر الحذف
            delete_btn = QPushButton("حذف")
            delete_btn.setObjectName("deleteButton")
            delete_btn.setFixedSize(120, 40)  # ضبط حجم الزر بشكل ثابت
            delete_btn.clicked.connect(lambda: self.delete_student(student_id))
            layout.addWidget(delete_btn)

            # زر التفاصيل
            details_btn = QPushButton("تفاصيل")
            details_btn.setObjectName("detailsButton")
            details_btn.setFixedSize(120, 40)  # ضبط حجم الزر بشكل ثابت
            details_btn.clicked.connect(lambda: self.show_student_details(student_id))
            layout.addWidget(details_btn)

            return widget

        except Exception as e:
            logging.error(f"خطأ في إنشاء ويدجت الإجراءات: {e}")
            return QWidget()
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        try:
            # إحصائيات عامة
            # حساب الإجماليات للطلاب المعروضين
            total_students_count = len(self.current_students)
            active_students_count = 0
            inactive_students_count = 0
            male_students_count = 0
            female_students_count = 0
            
            for student in self.current_students:
                status = student['status']
                gender = student['gender']
                
                if status == 'نشط':
                    active_students_count += 1
                else:
                    inactive_students_count += 1
                
                if gender == 'ذكر':
                    male_students_count += 1
                elif gender == 'أنثى':
                    female_students_count += 1
            
            # تحديث الملصقات الرئيسية
            self.total_students_value.setText(str(total_students_count))
            self.active_students_value.setText(str(active_students_count))
            self.inactive_students_value.setText(str(inactive_students_count))
            
            
            # تحديث الإحصائيات الأخرى
            self.displayed_count_label.setText(f"عدد الطلاب المعروضين: {total_students_count}")
            self.male_students_label.setText(f"الذكور: {male_students_count}")
            self.female_students_label.setText(f"الإناث: {female_students_count}")
            
            # تحديث وقت آخر تحديث
            from datetime import datetime
            self.last_update_label.setText(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث الإحصائيات: {e}")
            # تعيين قيم افتراضية في حالة الخطأ
            self.total_students_label.setText("--")
            self.active_students_label.setText("--")
            self.inactive_students_label.setText("--")
            self.displayed_count_label.setText("--")
            self.male_students_label.setText("--")
            self.female_students_label.setText("--")
    
    def apply_filters(self):
        """تطبيق الفلاتر وإعادة تحميل البيانات"""
        try:
            self.load_students()
            
        except Exception as e:
            logging.error(f"خطأ في تطبيق الفلاتر: {e}")
    
    def refresh(self):
        """تحديث البيانات"""
        try:
            log_user_action("تحديث صفحة الطلاب")
            self.load_students()
            
        except Exception as e:
            logging.error(f"خطأ في تحديث صفحة الطلاب: {e}")
            
    def clear_filters(self):
        """مسح جميع الفلاتر وإعادة تعيينها إلى الوضع الافتراضي"""
        try:
            self.school_combo.setCurrentIndex(0) # "جميع المدارس"
            self.grade_combo.setCurrentIndex(0) # "جميع الصفوف"
            self.status_combo.setCurrentIndex(0) # "جميع الحالات"
            self.gender_combo.setCurrentIndex(0) # "جميع الطلاب"
            self.search_input.clear()
            self.apply_filters()
            log_user_action("مسح فلاتر صفحة الطلاب")
        except Exception as e:
            logging.error(f"خطأ في مسح الفلاتر: {e}")
            
    def print_student_list(self):
        """طباعة قائمة الطلاب مع المعاينة والفلترة"""
        try:
            log_user_action("طباعة قائمة الطلاب")
            # إعداد معلومات الفلاتر
            filters = []
            school = self.school_combo.currentText()
            if school and school != "جميع المدارس":
                filters.append(f"المدرسة: {school}")
            grade = self.grade_combo.currentText()
            if grade and grade != "جميع الصفوف":
                filters.append(f"الصف: {grade}")
            status = self.status_combo.currentText()
            if status and status != "جميع الحالات":
                filters.append(f"الحالة: {status}")
            gender = self.gender_combo.currentText()
            if gender and gender != "جميع الطلاب":
                filters.append(f"الجنس: {gender}")
            search = self.search_input.text().strip()
            if search:
                filters.append(f"بحث: {search}")
            filter_info = "؛ ".join(filters) if filters else None
            # استدعاء دالة الطباعة مع المعاينة
            print_students_list(self.current_students, filter_info, parent=self)
        except Exception as e:
            logging.error(f"خطأ في طباعة قائمة الطلاب: {e}")
    
    def show_context_menu(self, position):
        """عرض قائمة السياق للجدول"""
        try:
            if self.students_table.itemAt(position) is None:
                return
            
            menu = QMenu(self)
            
            edit_action = QAction("تعديل", self)
            edit_action.triggered.connect(lambda: self.edit_student(self.students_table.currentRow()))
            menu.addAction(edit_action)
            
            delete_action = QAction("حذف", self)
            delete_action.triggered.connect(lambda: self.delete_student_by_row(self.students_table.currentRow()))
            menu.addAction(delete_action)
            
            menu.exec_(self.students_table.mapToGlobal(position))
            
        except Exception as e:
            logging.error(f"خطأ في عرض قائمة السياق: {e}")
    
    def setup_styles(self):
        """إعداد تنسيقات الصفحة"""
        try:
            style = """
                /* الإطار الرئيسي */
                QWidget {
                    background-color: #F8F9FA;
                    font-family: 'Segoe UI', Tahoma, Arial;
                    font-size: 18px;
                }
                
                /* رأس الصفحة */
                #headerFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #9B59B6, stop:1 #8E44AD);
                    border-radius: 10px;
                    color: white;
                    margin-bottom: 10px;
                }
                
                #pageTitle {
                    font-size: 18px;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 5px;
                }
                
                #pageDesc {
                    font-size: 18px;
                    color: #E8DAEF;
                }
                
                #quickStat {
                    font-size: 18px;
                    font-weight: bold;
                    color: white;
                    background-color: rgba(255, 255, 255, 0.2);
                    padding: 5px 10px;
                    border-radius: 15px;
                    margin: 0 5px;
                }
                
                /* شريط الأدوات */
                #toolbarFrame {
                    background-color: white;
                    border: 1px solid #E9ECEF;
                    border-radius: 8px;
                    margin-bottom: 10px;
                }
                
                #filterLabel {
                    font-weight: bold;
                    color: #2C3E50;
                    margin-right: 5px;
                    font-size: 18px; /* Adjusted to match additional_fees_page.py */
                }
                
                #filterCombo {
                    padding: 6px 10px;
                    border: 1px solid #BDC3C7;
                    border-radius: 4px;
                    background-color: white;
                    min-width: 100px;
                    font-size: 18px; /* Adjusted to match additional_fees_page.py */
                }
                
                #filterCombo:focus { /* Added focus style */
                    border-color: #9B59B6;
                    outline: none;
                }
                
                #searchInput {
                    padding: 8px 12px;
                    border: 2px solid #9B59B6;
                    border-radius: 6px;
                    font-size: 18px;
                    background-color: white;
                }
                
                #searchInput:focus { /* Added focus style */
                    border-color: #8E44AD;
                    outline: none;
                }
                
                /* الأزرار */
                #primaryButton {
                    background-color: #9B59B6;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                    font-size: 18px; /* Adjusted to match additional_fees_page.py */
                }
                
                #primaryButton:hover {
                    background-color: #8E44AD;
                }
                
                #groupButton {
                    background-color: #9B59B6;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 150px;
                    font-size: 18px;
                }
                
                #groupButton:hover {
                    background-color: #8E44AD;
                }
                
                #secondaryButton { /* Added secondaryButton style */
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                    font-size: 18px; /* Adjusted to match additional_fees_page.py */
                }
                
                #secondaryButton:hover {
                    background-color: #2980B9;
                }
                
                #refreshButton {
                    background-color: #95A5A6;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 18px; /* Adjusted to match additional_fees_page.py */
                }
                
                #refreshButton:hover {
                    background-color: #7F8C8D;
                }
                
                #editButton, #deleteButton, #detailsButton {
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-size: 18px; /* Adjusted to match additional_fees_page.py */
                    font-weight: bold;
                    border: none;
                    margin: 2px;
                }
                
                #editButton {
                    background-color: #3498DB;
                    color: white;
                }
                
                #deleteButton {
                    background-color: #E74C3C;
                    color: white;
                }
                
                #detailsButton {
                    background-color: #9B59B6;
                    color: white;
                }
                
                /* الجدول */
                QTableWidget {
                    background-color: white;
                    border: none; /* Adjusted to match additional_fees_page.py */
                    border-radius: 6px; /* Adjusted to match additional_fees_page.py */
                    gridline-color: #E9ECEF;
                    font-size: 18px; /* Adjusted to match additional_fees_page.py */
                    margin: 10px 0px;
                }
                
                QTableWidget::item {
                    padding: 8px; /* Adjusted to match additional_fees_page.py */
                    border-bottom: 1px solid #F1F2F6; /* Adjusted to match additional_fees_page.py */
                    font-size: 18px; /* Adjusted to match additional_fees_page.py */
                }
                
                QTableWidget::item:selected {
                    background-color: #E8DAEF; /* Adjusted to match additional_fees_page.py */
                    color: #6C3483; /* Adjusted to match additional_fees_page.py */
                }
                
                QHeaderView::section {
                    background-color: #34495E; /* Adjusted to match additional_fees_page.py */
                    color: white;
                    padding: 10px 8px; /* Adjusted to match additional_fees_page.py */
                    font-weight: bold;
                    font-size: 18px; /* Adjusted to match additional_fees_page.py */
                    border: none;
                    border-right: 1px solid #2C3E50; /* Adjusted to match additional_fees_page.py */
                }
                
                /* إحصائيات */
                #statsFrame { /* Renamed from statsFrame to summaryFrame for consistency */
                    background-color: white;
                    border: 1px solid #E9ECEF; /* Adjusted to match additional_fees_page.py */
                    border-radius: 8px; /* Adjusted to match additional_fees_page.py */
                    margin-top: 10px; /* Adjusted to match additional_fees_page.py */
                }
                
                #summaryTitle { /* Added summaryTitle style */
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin-bottom: 10px;
                }
                
                #summaryLabel { /* Added summaryLabel style */
                    font-size: 18px;
                    font-weight: bold;
                    color: #7F8C8D;
                    text-align: center;
                }
                
                #summaryValue { /* Added summaryValue style */
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    text-align: center;
                }
                
                #summaryValueSuccess { /* Added summaryValueSuccess style */
                    font-size: 18px;
                    font-weight: bold;
                    color: #27AE60;
                    text-align: center;
                }
                
                #summaryValueWarning { /* Added summaryValueWarning style */
                    font-size: 18px;
                    font-weight: bold;
                    color: #F39C12;
                    text-align: center;
                }
                
                #countLabel { /* Renamed from countLabel to statLabel for consistency */
                    font-size: 18px; /* Adjusted to match additional_fees_page.py */
                    font-weight: bold;
                    color: #2C3E50;
                    margin: 2px 0; /* Adjusted to match additional_fees_page.py */
                }
                
                /* أشرطة التمرير */
                QScrollBar:vertical { /* Added scrollbar styles */
                    background-color: #F1F2F6;
                    width: 12px;
                    border-radius: 6px;
                }
                
                QScrollBar::handle:vertical {
                    background-color: #BDC3C7;
                    border-radius: 6px;
                    min-height: 20px;
                }
                
                QScrollBar::handle:vertical:hover {
                    background-color: #95A5A6;
                }
                
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                }
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الستايل: {e}")
    
    def add_student(self):
        """إضافة طالب جديد"""
        try:
            dialog = AddStudentDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh()
                log_user_action("إضافة طالب جديد", "نجح")
                
        except Exception as e:
            logging.error(f"خطأ في إضافة طالب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة إضافة الطالب:\\n{str(e)}")
    
    def add_group_students(self):
        """إضافة مجموعة طلاب"""
        try:
            dialog = AddGroupStudentsDialog(self)
            dialog.students_added.connect(self.refresh)
            if dialog.exec_() == QDialog.Accepted:
                log_user_action("إضافة مجموعة طلاب", "نجح")
                
        except Exception as e:
            logging.error(f"خطأ في إضافة مجموعة طلاب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة إضافة مجموعة الطلاب:\\n{str(e)}")
    
    def edit_student(self, row):
        """تعديل بيانات طالب"""
        try:
            if row < 0 or row >= self.students_table.rowCount():
                return
            
            # الحصول على ID الطالب من الصف المحدد
            student_id_item = self.students_table.item(row, 0)
            if not student_id_item:
                return
            
            student_id = int(student_id_item.text())
            self.edit_student_by_id(student_id)
                
        except Exception as e:
            logging.error(f"خطأ في تعديل الطالب: {e}")
    
    def edit_student_by_id(self, student_id):
        """تعديل طالب بواسطة المعرف"""
        try:
            dialog = EditStudentDialog(student_id, self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh()
                log_user_action(f"تعديل بيانات الطالب {student_id}", "نجح")
                
        except Exception as e:
            logging.error(f"خطأ في تعديل الطالب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تعديل الطالب:\\n{str(e)}")
    
    def delete_student(self, student_id):
        """حذف طالب"""
        try:
            # تأكيد الحذف
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                "هل أنت متأكد من حذف هذا الطالب؟\\nسيتم حذف جميع البيانات المرتبطة به.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # حذف الطالب من قاعدة البيانات
                query = "DELETE FROM students WHERE id = ?"
                affected_rows = db_manager.execute_update(query, (student_id,))
                
                if affected_rows > 0:
                    QMessageBox.information(self, "نجح", "تم حذف الطالب بنجاح")
                    self.refresh()
                    log_user_action(f"حذف الطالب {student_id}", "نجح")
                else:
                    QMessageBox.warning(self, "خطأ", "لم يتم العثور على الطالب")
                    
        except Exception as e:
            logging.error(f"خطأ في حذف الطالب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حذف الطالب:\\n{str(e)}")
    
    def delete_student_by_row(self, row):
        """حذف طالب بواسطة رقم الصف"""
        try:
            if row < 0 or row >= self.students_table.rowCount():
                return
            
            student_id_item = self.students_table.item(row, 0)
            if not student_id_item:
                return
            
            student_id = int(student_id_item.text())
            self.delete_student(student_id)
            
        except Exception as e:
            logging.error(f"خطأ في حذف الطالب: {e}")
    
    def show_student_details(self, student_id):
        """عرض صفحة تفاصيل الطالب الشاملة"""
        try:
            from .student_details_page import StudentDetailsPage
            
            # إنشاء صفحة التفاصيل
            details_page = StudentDetailsPage(student_id)
            
            # ربط إشارة الرجوع
            details_page.back_requested.connect(lambda: self.close_details_page(details_page))
            details_page.student_updated.connect(self.refresh)
            
            # الحصول على النافذة الرئيسية وإضافة الصفحة
            main_window = self.get_main_window()
            if main_window:
                # إخفاء الشريط الجانبي مؤقتاً لإعطاء مساحة أكبر
                main_window.show_page_widget(details_page)
            else:
                # عرض في نافذة منفصلة إذا لم نجد النافذة الرئيسية
                dialog = QDialog(self)
                dialog.setWindowTitle(f"تفاصيل الطالب")
                dialog.setModal(True)
                dialog.resize(1200, 800)
                
                layout = QVBoxLayout(dialog)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(details_page)
                
                # ربط إشارة الرجوع لإغلاق النافذة
                details_page.back_requested.connect(dialog.accept)
                
                dialog.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض تفاصيل الطالب: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في عرض تفاصيل الطالب: {str(e)}")
    
    def close_details_page(self, details_page):
        """إغلاق صفحة التفاصيل والعودة لصفحة الطلاب"""
        try:
            main_window = self.get_main_window()
            if main_window:
                main_window.show_students_page()
            
        except Exception as e:
            logging.error(f"خطأ في إغلاق صفحة التفاصيل: {e}")
    
    def get_main_window(self):
        """الحصول على النافذة الرئيسية"""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'show_page_widget'):
                    return parent
                parent = parent.parent()
            return None
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على النافذة الرئيسية: {e}")
            return None
