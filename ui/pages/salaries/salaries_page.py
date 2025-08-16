#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة الرواتب
"""

import logging
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QComboBox, QDateEdit, QGroupBox, QFormLayout, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont

from core.database.connection import db_manager
from core.utils.logger import log_user_action

# استيراد نوافذ إدارة الرواتب
from .add_salary_dialog import AddSalaryDialog
from .edit_salary_dialog import EditSalaryDialog


class SalariesPage(QWidget):
    """صفحة إدارة الرواتب"""
    
    def __init__(self):
        super().__init__()
        self.current_salaries = []
        self.setup_ui()
        self.setup_connections()
        self.load_schools()
        self.load_persons_list()
        self.load_salaries()
        self.update_statistics()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(20)
            
            # إنشاء splitter لتقسيم المساحة
            splitter = QSplitter(Qt.Horizontal)
            
            # الجانب الأيسر - الجدول والبحث
            left_widget = QWidget()
            left_layout = QVBoxLayout(left_widget)
            left_layout.setContentsMargins(0, 0, 0, 0)
            
            # شريط البحث والفلترة
            self.create_search_bar(left_layout)
            
            # جدول الرواتب
            self.create_salaries_table(left_layout)
            
            # شريط الأدوات
            self.create_toolbar(left_layout)
            
            # الجانب الأيمن - الإحصائيات
            right_widget = QWidget()
            right_layout = QVBoxLayout(right_widget)
            right_layout.setContentsMargins(10, 0, 0, 0)
            
            # مجموعة الإحصائيات
            self.create_statistics_panel(right_layout)
            
            # إضافة الأجزاء للـ splitter
            splitter.addWidget(left_widget)
            splitter.addWidget(right_widget)
            splitter.setSizes([800, 300])  # نسبة المساحة
            
            layout.addWidget(splitter)
            self.setLayout(layout)
            self.setup_styles()
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة الرواتب: {e}")
            raise
    
    def create_search_bar(self, layout):
        """إنشاء شريط البحث والفلترة"""
        try:
            # إطار شريط البحث
            search_frame = QFrame()
            search_frame.setObjectName("searchFrame")
            
            search_layout = QHBoxLayout(search_frame)
            search_layout.setContentsMargins(15, 10, 15, 10)
            search_layout.setSpacing(10)
            
            # حقل البحث
            search_label = QLabel("البحث:")
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("البحث باسم الموظف/المعلم...")
            self.search_input.setMinimumWidth(200)
            
            # فلتر المدرسة
            school_label = QLabel("المدرسة:")
            self.school_filter = QComboBox()
            self.school_filter.addItem("جميع المدارس", "")
            self.school_filter.setMinimumWidth(150)
            
            # فلتر نوع الموظف
            type_label = QLabel("النوع:")
            self.type_filter = QComboBox()
            self.type_filter.addItem("الكل", "")
            self.type_filter.addItem("المعلمين", "teacher")
            self.type_filter.addItem("الموظفين", "employee")
            self.type_filter.setMinimumWidth(120)
            
            # فلتر الشخص المحدد
            person_label = QLabel("الشخص:")
            self.person_filter = QComboBox()
            self.person_filter.addItem("الجميع", "")
            self.person_filter.setMinimumWidth(200)
            
            # فلتر التاريخ - من (افتراضي من 2025-01-01)
            from_label = QLabel("من تاريخ:")
            self.from_date_filter = QDateEdit()
            # تعيين افتراضيًا إلى 1 يناير 2025
            self.from_date_filter.setDate(QDate(2025, 1, 1))
            self.from_date_filter.setCalendarPopup(True)
            self.from_date_filter.setMinimumWidth(120)
            
            # فلتر التاريخ - إلى (افتراضي حتى 31 ديسمبر 2040)
            to_label = QLabel("إلى تاريخ:")
            self.to_date_filter = QDateEdit()
            # تعيين افتراضيًا إلى 31 ديسمبر 2040
            self.to_date_filter.setDate(QDate(2040, 12, 31))
            self.to_date_filter.setCalendarPopup(True)
            self.to_date_filter.setMinimumWidth(120)
            
            # زر مسح البحث
            self.clear_search_btn = QPushButton("مسح الفلاتر")
            self.clear_search_btn.setObjectName("clearButton")
            self.clear_search_btn.setMinimumWidth(100)
            
            # ترتيب العناصر
            search_layout.addWidget(search_label)
            search_layout.addWidget(self.search_input)
            search_layout.addWidget(school_label)
            search_layout.addWidget(self.school_filter)
            search_layout.addWidget(type_label)
            search_layout.addWidget(self.type_filter)
            search_layout.addWidget(person_label)
            search_layout.addWidget(self.person_filter)
            search_layout.addWidget(from_label)
            search_layout.addWidget(self.from_date_filter)
            search_layout.addWidget(to_label)
            search_layout.addWidget(self.to_date_filter)
            search_layout.addWidget(self.clear_search_btn)
            search_layout.addStretch()
            
            layout.addWidget(search_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط البحث: {e}")
            raise
    
    def create_salaries_table(self, layout):
        """إنشاء جدول الرواتب"""
        try:
            # إطار الجدول
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")
            
            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)
            
            # عنوان الجدول
            table_header = QLabel("سجل الرواتب")
            table_header.setObjectName("tableHeader")
            table_layout.addWidget(table_header)
            
            # الجدول
            self.salaries_table = QTableWidget()
            self.salaries_table.setObjectName("dataTable")
            
            # إعداد أعمدة الجدول
            columns = [
                "اسم الموظف/المعلم", "المدرسة", "النوع", "الراتب المسجل", 
                "المبلغ المدفوع", "فترة الراتب", "عدد الأيام", 
                "تاريخ الدفع", "ملاحظات"
            ]
            self.salaries_table.setColumnCount(len(columns))
            self.salaries_table.setHorizontalHeaderLabels(columns)
            
            # إعداد خصائص الجدول
            self.salaries_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.salaries_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.salaries_table.setAlternatingRowColors(True)
            self.salaries_table.setSortingEnabled(True)
            
            # تكوين عرض الأعمدة
            header = self.salaries_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.resizeSection(0, 180)  # الاسم
            header.resizeSection(1, 140)  # المدرسة
            header.resizeSection(2, 80)   # النوع
            header.resizeSection(3, 120)  # الراتب المسجل
            header.resizeSection(4, 120)  # المبلغ المدفوع
            header.resizeSection(5, 150)  # فترة الراتب
            header.resizeSection(6, 80)   # عدد الأيام
            header.resizeSection(7, 120)  # تاريخ الدفع
            
            table_layout.addWidget(self.salaries_table)
            layout.addWidget(table_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول الرواتب: {e}")
            raise
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات"""
        try:
            toolbar_frame = QFrame()
            toolbar_frame.setObjectName("toolbarFrame")
            
            toolbar_layout = QHBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(15, 10, 15, 10)
            toolbar_layout.setSpacing(10)
            
            # أزرار العمليات
            self.add_btn = QPushButton("إضافة راتب")
            self.add_btn.setObjectName("primaryButton")
            self.add_btn.setMinimumWidth(120)
            
            self.refresh_btn = QPushButton("تحديث")
            self.refresh_btn.setObjectName("secondaryButton")
            self.refresh_btn.setMinimumWidth(100)
            # زر تعديل راتب
            self.edit_btn = QPushButton("تعديل راتب")
            self.edit_btn.setObjectName("secondaryButton")
            self.edit_btn.setMinimumWidth(120)
            # زر حذف راتب
            self.delete_btn = QPushButton("حذف راتب")
            self.delete_btn.setObjectName("secondaryButton")
            self.delete_btn.setMinimumWidth(120)
            
            # معلومات العدد
            self.count_label = QLabel("إجمالي الرواتب: 0")
            self.count_label.setObjectName("statsLabel")
            
            # ترتيب العناصر
            toolbar_layout.addWidget(self.add_btn)
            toolbar_layout.addWidget(self.edit_btn)
            toolbar_layout.addWidget(self.delete_btn)
            toolbar_layout.addWidget(self.refresh_btn)
            toolbar_layout.addStretch()
            toolbar_layout.addWidget(self.count_label)
            
            layout.addWidget(toolbar_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
            raise
    
    def create_statistics_panel(self, layout):
        """إنشاء لوحة الإحصائيات"""
        try:
            # إحصائيات عامة
            general_stats_group = QGroupBox("إحصائيات عامة")
            general_layout = QFormLayout()
            
            self.total_salaries_label = QLabel("0")
            self.total_amount_label = QLabel("0.00 دينار")
            self.teachers_count_label = QLabel("0")
            self.employees_count_label = QLabel("0")
            
            general_layout.addRow("إجمالي الرواتب:", self.total_salaries_label)
            general_layout.addRow("إجمالي المبالغ:", self.total_amount_label)
            general_layout.addRow("رواتب المعلمين:", self.teachers_count_label)
            general_layout.addRow("رواتب الموظفين:", self.employees_count_label)
            
            general_stats_group.setLayout(general_layout)
            layout.addWidget(general_stats_group)
            
            # إحصائيات الشهر الحالي
            monthly_stats_group = QGroupBox("إحصائيات الشهر الحالي")
            monthly_layout = QFormLayout()
            
            self.monthly_count_label = QLabel("0")
            self.monthly_amount_label = QLabel("0.00 دينار")
            self.monthly_teachers_label = QLabel("0")
            self.monthly_employees_label = QLabel("0")
            
            monthly_layout.addRow("عدد الرواتب:", self.monthly_count_label)
            monthly_layout.addRow("إجمالي المبالغ:", self.monthly_amount_label)
            monthly_layout.addRow("رواتب المعلمين:", self.monthly_teachers_label)
            monthly_layout.addRow("رواتب الموظفين:", self.monthly_employees_label)
            
            monthly_stats_group.setLayout(monthly_layout)
            layout.addWidget(monthly_stats_group)
            
            # إضافة مساحة فارغة
            layout.addStretch()
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء لوحة الإحصائيات: {e}")
            raise
    
    def setup_connections(self):
        """إعداد الاتصالات والأحداث"""
        try:
            # أحداث البحث والفلترة
            self.search_input.textChanged.connect(self.apply_filters)
            self.school_filter.currentTextChanged.connect(self.load_persons_list)
            self.school_filter.currentTextChanged.connect(self.apply_filters)
            self.type_filter.currentTextChanged.connect(self.load_persons_list)
            self.type_filter.currentTextChanged.connect(self.apply_filters)
            self.person_filter.currentTextChanged.connect(self.apply_filters)
            self.from_date_filter.dateChanged.connect(self.apply_filters)
            self.to_date_filter.dateChanged.connect(self.apply_filters)
            self.clear_search_btn.clicked.connect(self.clear_filters)
            
            # أحداث الأزرار
            self.add_btn.clicked.connect(self.add_salary)
            self.refresh_btn.clicked.connect(self.refresh_data)
            self.edit_btn.clicked.connect(self.handle_edit_selected)
            self.delete_btn.clicked.connect(self.handle_delete_selected)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الاتصالات: {e}")
    
    def setup_styles(self):
        """إعداد أنماط العرض"""
        try:
            self.setStyleSheet("""
                QFrame#searchFrame {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                }
                
                QFrame#tableFrame {
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    background-color: white;
                }
                
                QLabel#tableHeader {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding: 15px;
                    background-color: #ecf0f1;
                    border-bottom: 1px solid #bdc3c7;
                }
                
                QTableWidget#dataTable {
                    border: none;
                    gridline-color: #dee2e6;
                    selection-background-color: #3498db;
                    alternate-background-color: #f8f9fa;
                }
                
                QFrame#toolbarFrame {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                }
                
                QPushButton#primaryButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                
                QPushButton#primaryButton:hover {
                    background-color: #0056b3;
                }
                
                QPushButton#secondaryButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                
                QPushButton#secondaryButton:hover {
                    background-color: #545b62;
                }
                
                QPushButton#clearButton {
                    background-color: #ffc107;
                    color: #212529;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                
                QPushButton#clearButton:hover {
                    background-color: #e0a800;
                }
                
                QLabel#statsLabel {
                    color: #6c757d;
                    font-weight: bold;
                }
                
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #2c3e50;
                }
                
                QComboBox, QLineEdit, QDateEdit {
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    padding: 5px;
                    background-color: white;
                }
                
                QComboBox:focus, QLineEdit:focus, QDateEdit:focus {
                    border-color: #007bff;
                    outline: none;
                }
            """)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الأنماط: {e}")
    
    def load_schools(self):
        """تحميل قائمة المدارس للفلتر"""
        try:
            self.school_filter.clear()
            self.school_filter.addItem("جميع المدارس", "")
            
            query = "SELECT id, name_ar FROM schools ORDER BY name_ar"
            
            with db_manager.get_cursor() as cursor:
                cursor.execute(query)
                schools = cursor.fetchall()
                
                for school in schools:
                    self.school_filter.addItem(school['name_ar'], school['id'])
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
    
    def load_persons_list(self):
        """تحميل قائمة الأشخاص (معلمين وموظفين) للفلتر"""
        try:
            self.person_filter.clear()
            self.person_filter.addItem("الجميع", "")
            
            school_id = self.school_filter.currentData()
            staff_type = self.type_filter.currentData()
            
            # بناء شروط الفلتر
            conditions = []
            params = []
            
            if school_id:
                conditions.append("school_id = ?")
                params.append(school_id)
            
            condition_str = ""
            if conditions:
                condition_str = " WHERE " + " AND ".join(conditions)
            
            persons = []
            
            # تحميل المعلمين إذا لم يتم تحديد نوع أو تم تحديد معلمين
            if not staff_type or staff_type == "teacher":
                teacher_query = f"""
                    SELECT t.id, t.name, s.name_ar as school_name, 'teacher' as type
                    FROM teachers t
                    LEFT JOIN schools s ON t.school_id = s.id
                    {condition_str.replace("school_id", "t.school_id")}
                    ORDER BY t.name
                """
                
                with db_manager.get_cursor() as cursor:
                    if params:
                        cursor.execute(teacher_query, params)
                    else:
                        cursor.execute(teacher_query)
                    teachers = cursor.fetchall()
                    
                    for teacher in teachers:
                        persons.append({
                            'id': teacher['id'],
                            'name': teacher['name'],
                            'school': teacher['school_name'] or 'غير محدد',
                            'type': 'teacher',
                            'type_ar': 'معلم'
                        })
            
            # تحميل الموظفين إذا لم يتم تحديد نوع أو تم تحديد موظفين
            if not staff_type or staff_type == "employee":
                employee_query = f"""
                    SELECT e.id, e.name, s.name_ar as school_name, 'employee' as type
                    FROM employees e
                    LEFT JOIN schools s ON e.school_id = s.id
                    {condition_str.replace("school_id", "e.school_id")}
                    ORDER BY e.name
                """
                
                with db_manager.get_cursor() as cursor:
                    if params:
                        cursor.execute(employee_query, params)
                    else:
                        cursor.execute(employee_query)
                    employees = cursor.fetchall()
                    
                    for employee in employees:
                        persons.append({
                            'id': employee['id'],
                            'name': employee['name'],
                            'school': employee['school_name'] or 'غير محدد',
                            'type': 'employee',
                            'type_ar': 'موظف'
                        })
            
            # ترتيب الأشخاص حسب الاسم
            persons.sort(key=lambda x: x['name'])
            
            # إضافة الأشخاص للقائمة
            for person in persons:
                display_text = f"{person['name']} - {person['school']} ({person['type_ar']})"
                person_key = f"{person['type']}_{person['id']}"
                self.person_filter.addItem(display_text, person_key)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل قائمة الأشخاص: {e}")
    
    def load_salaries(self):
        """تحميل بيانات الرواتب"""
        try:
            query = """
                SELECT s.*, 
                       CASE s.staff_type 
                           WHEN 'teacher' THEN 'معلم'
                           WHEN 'employee' THEN 'موظف'
                           ELSE s.staff_type
                       END as staff_type_ar,
                       sch.name_ar as school_name
                FROM salaries s
                LEFT JOIN schools sch ON s.school_id = sch.id
                ORDER BY s.payment_date DESC, s.created_at DESC
            """
            
            with db_manager.get_cursor() as cursor:
                cursor.execute(query)
                salaries = cursor.fetchall()
                
                self.current_salaries = salaries
                self.apply_filters()
                
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الرواتب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات الرواتب:\n{e}")
    
    def apply_filters(self):
        """تطبيق الفلاتر على البيانات"""
        try:
            search_text = self.search_input.text().strip().lower()
            school_id = self.school_filter.currentData()
            staff_type = self.type_filter.currentData()
            person_key = self.person_filter.currentData()
            from_date = self.from_date_filter.date().toPyDate()
            to_date = self.to_date_filter.date().toPyDate()
            
            filtered_salaries = []
            
            for salary in self.current_salaries:
                # فلتر البحث بالاسم
                if search_text and search_text not in (salary['staff_name'] or '').lower():
                    continue
                
                # فلتر المدرسة
                if school_id and salary['school_id'] != school_id:
                    continue
                
                # فلتر نوع الموظف
                if staff_type and salary['staff_type'] != staff_type:
                    continue
                
                # فلتر الشخص المحدد
                if person_key:
                    person_type, person_id = person_key.split('_')
                    if salary['staff_type'] != person_type or salary['staff_id'] != int(person_id):
                        continue
                
                # فلتر التاريخ (يُطبق فقط إذا تم تغيير النطاق عن القيم القصوى)
                payment_date = datetime.strptime(salary['payment_date'], '%Y-%m-%d').date()
                # الحصول على القيم القصوى للفلتر
                min_date = self.from_date_filter.minimumDate().toPyDate()
                max_date = self.to_date_filter.maximumDate().toPyDate()
                # إذا لم تكن التواريخ في القيمة الافتراضية القصوى، طبق الفلتر
                if not (from_date == min_date and to_date == max_date):
                    if payment_date < from_date or payment_date > to_date:
                        continue
                
                filtered_salaries.append(salary)
            
            self.populate_table(filtered_salaries)
            
        except Exception as e:
            logging.error(f"خطأ في تطبيق الفلاتر: {e}")
    
    def populate_table(self, salaries):
        """ملء الجدول بالبيانات"""
        try:
            self.salaries_table.setRowCount(len(salaries))
            
            for row, salary in enumerate(salaries):
                # اسم الموظف/المعلم
                self.salaries_table.setItem(row, 0, QTableWidgetItem(salary['staff_name'] or ''))
                
                # المدرسة
                self.salaries_table.setItem(row, 1, QTableWidgetItem(salary['school_name'] or 'غير محدد'))
                
                # النوع
                self.salaries_table.setItem(row, 2, QTableWidgetItem(salary['staff_type_ar'] or ''))
                
                # الراتب المسجل
                base_salary = f"{float(salary['base_salary']):.2f}" if salary['base_salary'] else "0.00"
                self.salaries_table.setItem(row, 3, QTableWidgetItem(base_salary))
                
                # المبلغ المدفوع
                paid_amount = f"{float(salary['paid_amount']):.2f}" if salary['paid_amount'] else "0.00"
                self.salaries_table.setItem(row, 4, QTableWidgetItem(paid_amount))
                
                # فترة الراتب
                from_date = salary['from_date'] or ''
                to_date = salary['to_date'] or ''
                period = f"{from_date} إلى {to_date}" if from_date and to_date else "غير محدد"
                self.salaries_table.setItem(row, 5, QTableWidgetItem(period))
                
                # عدد الأيام
                days_count = str(salary['days_count']) if salary['days_count'] else "0"
                self.salaries_table.setItem(row, 6, QTableWidgetItem(days_count))
                
                # تاريخ الدفع
                self.salaries_table.setItem(row, 7, QTableWidgetItem(salary['payment_date'] or ''))
                
                # الملاحظات
                self.salaries_table.setItem(row, 8, QTableWidgetItem(salary['notes'] or ''))
                
                # إخفاء ID في البيانات (مخزن على عمود اسم الموظف)
                self.salaries_table.item(row, 0).setData(Qt.UserRole, salary['id'])
            
            # تحديث العداد
            self.count_label.setText(f"إجمالي الرواتب: {len(salaries)}")
            
            # تعديل أعمدة الجدول
            self.salaries_table.resizeColumnsToContents()
            
        except Exception as e:
            logging.error(f"خطأ في ملء الجدول: {e}")
    
    def update_statistics(self):
        """تحديث الإحصائيات"""
        try:
            with db_manager.get_cursor() as cursor:
                # إحصائيات عامة
                cursor.execute("SELECT COUNT(*) as count FROM salaries")
                total_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT SUM(paid_amount) as total FROM salaries")
                total_amount = cursor.fetchone()['total'] or 0
                
                cursor.execute("SELECT COUNT(*) as count FROM salaries WHERE staff_type = 'teacher'")
                teachers_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM salaries WHERE staff_type = 'employee'")
                employees_count = cursor.fetchone()['count']
                
                # إحصائيات الشهر الحالي
                current_month = datetime.now().strftime('%Y-%m')
                
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM salaries 
                    WHERE strftime('%Y-%m', payment_date) = ?
                """, (current_month,))
                monthly_count = cursor.fetchone()['count']
                
                cursor.execute("""
                    SELECT SUM(paid_amount) as total 
                    FROM salaries 
                    WHERE strftime('%Y-%m', payment_date) = ?
                """, (current_month,))
                monthly_amount = cursor.fetchone()['total'] or 0
                
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM salaries 
                    WHERE staff_type = 'teacher' AND strftime('%Y-%m', payment_date) = ?
                """, (current_month,))
                monthly_teachers = cursor.fetchone()['count']
                
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM salaries 
                    WHERE staff_type = 'employee' AND strftime('%Y-%m', payment_date) = ?
                """, (current_month,))
                monthly_employees = cursor.fetchone()['count']
                
                # تحديث التسميات
                self.total_salaries_label.setText(str(total_count))
                self.total_amount_label.setText(f"{total_amount:.2f} دينار")
                self.teachers_count_label.setText(str(teachers_count))
                self.employees_count_label.setText(str(employees_count))
                
                self.monthly_count_label.setText(str(monthly_count))
                self.monthly_amount_label.setText(f"{monthly_amount:.2f} دينار")
                self.monthly_teachers_label.setText(str(monthly_teachers))
                self.monthly_employees_label.setText(str(monthly_employees))
                
        except Exception as e:
            logging.error(f"خطأ في تحديث الإحصائيات: {e}")
    
    def clear_filters(self):
        """مسح جميع الفلاتر"""
        try:
            self.search_input.clear()
            self.school_filter.setCurrentIndex(0)
            self.type_filter.setCurrentIndex(0)
            self.person_filter.setCurrentIndex(0)
            # إعادة تعيين النطاق إلى 1 يناير 2025 حتى 31 ديسمبر 2040
            self.from_date_filter.setDate(QDate(2025, 1, 1))
            self.to_date_filter.setDate(QDate(2040, 12, 31))
            self.apply_filters()
            
        except Exception as e:
            logging.error(f"خطأ في مسح الفلاتر: {e}")
    
    def add_salary(self):
        """إضافة راتب جديد"""
        try:
            dialog = AddSalaryDialog(self)
            dialog.salary_added.connect(self.refresh_data)
            dialog.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في إضافة راتب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في فتح نافذة إضافة راتب:\n{e}")
    
    def handle_edit_selected(self):
        """معالجة تعديل الراتب المحدد في الجدول"""
        row = self.salaries_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار راتب للتعديل.")
            return
        salary_id = self.salaries_table.item(row, 0).data(Qt.UserRole)
        # فتح نافذة تعديل الراتب
        dialog = EditSalaryDialog(salary_id, self)
        dialog.salary_updated.connect(self.refresh_data)
        dialog.exec_()

    def handle_delete_selected(self):
        """معالجة حذف الراتب المحدد في الجدول"""
        row = self.salaries_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار راتب للحذف.")
            return
        salary_id = self.salaries_table.item(row, 0).data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            "هل أنت متأكد من حذف هذا الراتب؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            affected = db_manager.execute_update("DELETE FROM salaries WHERE id = ?", (salary_id,))
            if affected > 0:
                QMessageBox.information(self, "نجح", "تم حذف الراتب بنجاح")
                self.refresh_data()
                log_user_action(f"حذف الراتب {salary_id}", "نجح")
            else:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على الراتب")
    
    def refresh_data(self):
        """تحديث البيانات"""
        try:
            self.load_persons_list()  # تحديث قائمة الأشخاص
            self.load_salaries()
            self.update_statistics()
            
        except Exception as e:
            logging.error(f"خطأ في تحديث البيانات: {e}")
    
