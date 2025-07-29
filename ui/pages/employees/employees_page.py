#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة الموظفين
"""

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QMenu, QComboBox, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation

# استيراد نوافذ إدارة الموظفين
from .add_employee_dialog import AddEmployeeDialog
from .edit_employee_dialog import EditEmployeeDialog


class EmployeesPage(QWidget):
    """صفحة إدارة الموظفين"""
    
    # إشارات النافذة
    page_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_employees = []
        self.selected_school_id = None
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_schools()
        
        log_user_action("فتح صفحة إدارة الموظفين")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(20)
            
            # شريط البحث والفلترة
            self.create_search_bar(layout)
            
            # جدول الموظفين
            self.create_employees_table(layout)
            
            # شريط الأدوات
            self.create_toolbar(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة الموظفين: {e}")
            raise
    
    def create_search_bar(self, layout):
        """إنشاء شريط البحث والفلترة"""
        try:
            search_frame = QFrame()
            search_frame.setObjectName("searchFrame")
            
            search_layout = QHBoxLayout(search_frame)
            search_layout.setContentsMargins(15, 10, 15, 10)
            search_layout.setSpacing(15)
            
            # فلتر المدرسة
            school_label = QLabel("المدرسة:")
            school_label.setFixedWidth(60)
            
            self.school_filter = QComboBox()
            self.school_filter.setMinimumWidth(200)
            self.school_filter.addItem("جميع المدارس", None)
            
            # فلتر المهنة
            job_label = QLabel("المهنة:")
            job_label.setFixedWidth(50)
            
            self.job_filter = QComboBox()
            self.job_filter.setMinimumWidth(150)
            self.job_filter.addItem("جميع المهن", None)
            self.job_filter.addItem("عامل", "عامل")
            self.job_filter.addItem("حارس", "حارس")
            self.job_filter.addItem("كاتب", "كاتب")
            self.job_filter.addItem("مخصص", "مخصص")
            
            # مربع البحث
            search_label = QLabel("البحث:")
            search_label.setFixedWidth(50)
            
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("البحث بالاسم أو رقم الهاتف...")
            self.search_input.setMinimumWidth(200)
            
            # زر البحث
            search_btn = QPushButton("بحث")
            search_btn.setObjectName("primaryButton")
            search_btn.setFixedWidth(80)
            
            # زر مسح البحث
            clear_btn = QPushButton("مسح")
            clear_btn.setFixedWidth(60)
            
            # إضافة العناصر
            search_layout.addWidget(school_label)
            search_layout.addWidget(self.school_filter)
            search_layout.addWidget(job_label)
            search_layout.addWidget(self.job_filter)
            search_layout.addWidget(search_label)
            search_layout.addWidget(self.search_input)
            search_layout.addWidget(search_btn)
            search_layout.addWidget(clear_btn)
            
            layout.addWidget(search_frame)
            
            # ربط الأحداث
            search_btn.clicked.connect(self.search_employees)
            clear_btn.clicked.connect(self.clear_search)
            self.search_input.returnPressed.connect(self.search_employees)
            # بحث لحظي عند الكتابة بدلاً من استخدام زر البحث
            self.search_input.textChanged.connect(self.search_employees)
            # إخفاء زر البحث لأنه لم يعد ضروريًا مع البحث اللحظي
            search_btn.hide()
            self.school_filter.currentTextChanged.connect(self.on_filter_changed)
            self.job_filter.currentTextChanged.connect(self.on_filter_changed)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط البحث: {e}")
            raise
    
    def create_employees_table(self, layout):
        """إنشاء جدول الموظفين"""
        try:
            # إطار الجدول
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")
            
            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)
            
            # عنوان الجدول
            table_header = QLabel("قائمة الموظفين")
            table_header.setObjectName("tableHeader")
            table_layout.addWidget(table_header)
            
            # الجدول
            self.employees_table = QTableWidget()
            self.employees_table.setObjectName("dataTable")
            
            # إعداد أعمدة الجدول
            columns = ["م", "الاسم", "المدرسة", "المهنة", "الراتب الشهري", "رقم الهاتف", "ملاحظات"]
            self.employees_table.setColumnCount(len(columns))
            self.employees_table.setHorizontalHeaderLabels(columns)
            
            # إعداد خصائص الجدول
            self.employees_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.employees_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.employees_table.setAlternatingRowColors(True)
            self.employees_table.setSortingEnabled(True)
            
            # تكوين عرض الأعمدة
            header = self.employees_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.resizeSection(0, 50)   # رقم التسلسل
            header.resizeSection(1, 200)  # الاسم
            header.resizeSection(2, 150)  # المدرسة
            header.resizeSection(3, 100)  # المهنة
            header.resizeSection(4, 120)  # الراتب
            header.resizeSection(5, 120)  # الهاتف
            
            table_layout.addWidget(self.employees_table)
            layout.addWidget(table_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول الموظفين: {e}")
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
            self.add_btn = QPushButton("إضافة موظف")
            self.add_btn.setObjectName("primaryButton")
            self.add_btn.setMinimumWidth(120)
            
            self.edit_btn = QPushButton("تعديل")
            self.edit_btn.setObjectName("secondaryButton")
            self.edit_btn.setMinimumWidth(100)
            self.edit_btn.setEnabled(False)
            
            self.delete_btn = QPushButton("حذف")
            self.delete_btn.setObjectName("dangerButton")
            self.delete_btn.setMinimumWidth(100)
            self.delete_btn.setEnabled(False)
            
            self.refresh_btn = QPushButton("تحديث")
            self.refresh_btn.setObjectName("secondaryButton")
            self.refresh_btn.setMinimumWidth(100)
            
            self.print_btn = QPushButton("طباعة القائمة")
            self.print_btn.setObjectName("primaryButton")
            self.print_btn.setMinimumWidth(120)
            
            # معلومات الإحصائيات
            self.stats_label = QLabel("إجمالي الموظفين: 0")
            self.stats_label.setObjectName("statsLabel")
            
            # ترتيب العناصر
            toolbar_layout.addWidget(self.add_btn)
            toolbar_layout.addWidget(self.edit_btn)
            toolbar_layout.addWidget(self.delete_btn)
            toolbar_layout.addWidget(self.refresh_btn)
            toolbar_layout.addWidget(self.print_btn)
            toolbar_layout.addStretch()
            toolbar_layout.addWidget(self.stats_label)
            
            layout.addWidget(toolbar_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
            raise
    
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
                
                QPushButton#dangerButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                
                QPushButton#dangerButton:hover {
                    background-color: #c82333;
                }
                
                QLabel#statsLabel {
                    color: #6c757d;
                    font-weight: bold;
                }
            """)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الأنماط: {e}")
    
    def setup_connections(self):
        """إعداد الاتصالات والأحداث"""
        try:
            # أحداث الجدول
            self.employees_table.selectionModel().selectionChanged.connect(self.on_selection_changed)
            self.employees_table.cellDoubleClicked.connect(self.edit_employee)
            self.employees_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.employees_table.customContextMenuRequested.connect(self.show_context_menu)
            
            # أحداث الأزرار
            self.add_btn.clicked.connect(self.add_employee)
            self.edit_btn.clicked.connect(self.edit_employee)
            self.delete_btn.clicked.connect(self.delete_employee)
            self.refresh_btn.clicked.connect(self.refresh_data)
            self.print_btn.clicked.connect(self.print_employees_list)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الاتصالات: {e}")
    
    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT id, name_ar FROM schools ORDER BY name_ar")
                schools = cursor.fetchall()
                
                self.school_filter.clear()
                self.school_filter.addItem("جميع المدارس", None)
                
                for school in schools:
                    self.school_filter.addItem(school['name_ar'], school['id'])
                    
            self.load_employees()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المدارس:\n{e}")
    
    def load_employees(self):
        """تحميل بيانات الموظفين"""
        try:
            query = """
                SELECT e.*, s.name_ar as school_name 
                FROM employees e 
                LEFT JOIN schools s ON e.school_id = s.id 
                ORDER BY e.name
            """
            
            params = []
            
            # تطبيق الفلاتر
            conditions = []
            
            if self.selected_school_id:
                conditions.append("e.school_id = ?")
                params.append(self.selected_school_id)
            
            selected_job = self.job_filter.currentData()
            if selected_job:
                conditions.append("e.job_type = ?")
                params.append(selected_job)
            
            if conditions:
                query = query.replace("ORDER BY", f"WHERE {' AND '.join(conditions)} ORDER BY")
            
            with db_manager.get_cursor() as cursor:
                cursor.execute(query, params)
                employees = cursor.fetchall()
                
                self.current_employees = employees
                self.populate_table(employees)
                self.update_stats()
                
        except Exception as e:
            logging.error(f"خطأ في تحميل الموظفين: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات الموظفين:\n{e}")
    
    def populate_table(self, employees):
        """ملء الجدول بالبيانات"""
        try:
            self.employees_table.setRowCount(len(employees))
            
            for row, employee in enumerate(employees):
                # رقم التسلسل
                self.employees_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                
                # الاسم
                self.employees_table.setItem(row, 1, QTableWidgetItem(employee['name'] or ''))
                
                # المدرسة
                self.employees_table.setItem(row, 2, QTableWidgetItem(employee['school_name'] or ''))
                
                # المهنة
                self.employees_table.setItem(row, 3, QTableWidgetItem(employee['job_type'] or ''))
                
                # الراتب الشهري
                salary = f"{employee['monthly_salary']:.2f}" if employee['monthly_salary'] else "0.00"
                self.employees_table.setItem(row, 4, QTableWidgetItem(salary))
                
                # رقم الهاتف
                self.employees_table.setItem(row, 5, QTableWidgetItem(employee['phone'] or ''))
                
                # الملاحظات
                self.employees_table.setItem(row, 6, QTableWidgetItem(employee['notes'] or ''))
                
                # إخفاء ID في البيانات
                self.employees_table.item(row, 0).setData(Qt.UserRole, employee['id'])
            
            # تعديل أعمدة الجدول
            self.employees_table.resizeColumnsToContents()
            
        except Exception as e:
            logging.error(f"خطأ في ملء الجدول: {e}")
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        try:
            count = len(self.current_employees)
            self.stats_label.setText(f"إجمالي الموظفين: {count}")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث الإحصائيات: {e}")
    
    def on_selection_changed(self):
        """معالج تغيير التحديد"""
        try:
            has_selection = bool(self.employees_table.selectedItems())
            self.edit_btn.setEnabled(has_selection)
            self.delete_btn.setEnabled(has_selection)
            
        except Exception as e:
            logging.error(f"خطأ في معالج التحديد: {e}")
    
    def on_filter_changed(self):
        """معالج تغيير الفلاتر"""
        try:
            self.selected_school_id = self.school_filter.currentData()
            self.load_employees()
            
        except Exception as e:
            logging.error(f"خطأ في الفلاتر: {e}")
    
    def search_employees(self):
        """البحث في الموظفين"""
        try:
            search_text = self.search_input.text().strip().lower()
            
            if not search_text:
                self.populate_table(self.current_employees)
                return
                
            filtered_employees = []
            for employee in self.current_employees:
                if (search_text in (employee['name'] or '').lower() or
                    search_text in (employee['phone'] or '').lower()):
                    filtered_employees.append(employee)
            
            self.populate_table(filtered_employees)
            
        except Exception as e:
            logging.error(f"خطأ في البحث: {e}")
    
    def clear_search(self):
        """مسح البحث"""
        try:
            self.search_input.clear()
            self.school_filter.setCurrentIndex(0)
            self.job_filter.setCurrentIndex(0)
            self.selected_school_id = None
            self.load_employees()
            
        except Exception as e:
            logging.error(f"خطأ في مسح البحث: {e}")
    
    def add_employee(self):
        """إضافة موظف جديد"""
        try:
            dialog = AddEmployeeDialog(self)
            if dialog.exec_() == dialog.Accepted:
                self.load_employees()
                log_user_action("إضافة موظف جديد")
                
        except Exception as e:
            logging.error(f"خطأ في إضافة موظف: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في إضافة موظف:\n{e}")
    
    def edit_employee(self):
        """تعديل الموظف المحدد"""
        try:
            current_row = self.employees_table.currentRow()
            if current_row < 0:
                return
                
            employee_id = self.employees_table.item(current_row, 0).data(Qt.UserRole)
            if not employee_id:
                return
                
            dialog = EditEmployeeDialog(employee_id, self)
            if dialog.exec_() == dialog.Accepted:
                self.load_employees()
                log_user_action("تعديل بيانات موظف", employee_id)
                
        except Exception as e:
            logging.error(f"خطأ في تعديل موظف: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تعديل الموظف:\n{e}")
    
    def delete_employee(self):
        """حذف الموظف المحدد"""
        try:
            current_row = self.employees_table.currentRow()
            if current_row < 0:
                return
                
            employee_id = self.employees_table.item(current_row, 0).data(Qt.UserRole)
            employee_name = self.employees_table.item(current_row, 1).text()
            
            # تأكيد الحذف
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                f"هل أنت متأكد من حذف الموظف '{employee_name}'؟\n\nهذا الإجراء لا يمكن التراجع عنه.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                with db_manager.get_cursor() as cursor:
                    cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
                    
                self.load_employees()
                log_user_action("حذف موظف", employee_id)
                QMessageBox.information(self, "نجح", "تم حذف الموظف بنجاح")
                
        except Exception as e:
            logging.error(f"خطأ في حذف موظف: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في حذف الموظف:\n{e}")
    
    def refresh_data(self):
        """تحديث البيانات"""
        try:
            self.load_schools()
            log_user_action("تحديث بيانات الموظفين")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث البيانات: {e}")
    
    def show_context_menu(self, position):
        """عرض قائمة السياق"""
        try:
            if self.employees_table.itemAt(position) is None:
                return
                
            menu = QMenu(self)
            
            edit_action = QAction("تعديل", self)
            edit_action.triggered.connect(self.edit_employee)
            menu.addAction(edit_action)
            
            delete_action = QAction("حذف", self)
            delete_action.triggered.connect(self.delete_employee)
            menu.addAction(delete_action)
            
            menu.exec_(self.employees_table.mapToGlobal(position))
            
        except Exception as e:
            logging.error(f"خطأ في قائمة السياق: {e}")
    
    def print_employees_list(self):
        """طباعة قائمة الموظفين مع المعاينة والفلترة"""
        try:
            log_user_action("طباعة قائمة الموظفين")
            
            # إعداد معلومات الفلاتر
            filters = []
            school = self.school_filter.currentText()
            if school and school != "جميع المدارس":
                filters.append(f"المدرسة: {school}")
            
            search = self.search_input.text().strip()
            if search:
                filters.append(f"بحث: {search}")
            
            filter_info = "؛ ".join(filters) if filters else None
            
            # استدعاء دالة الطباعة مع المعاينة
            from core.printing.print_manager import print_employees_list
            print_employees_list(self.current_employees, filter_info, parent=self)
            
        except Exception as e:
            logging.error(f"خطأ في طباعة قائمة الموظفين: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في طباعة قائمة الموظفين:\n{e}")
