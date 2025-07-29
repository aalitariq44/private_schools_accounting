#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة المعلمين
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

# استيراد نوافذ إدارة المعلمين
from .add_teacher_dialog import AddTeacherDialog
from .edit_teacher_dialog import EditTeacherDialog


class TeachersPage(QWidget):
    """صفحة إدارة المعلمين"""
    
    # إشارات النافذة
    page_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_teachers = []
        self.selected_school_id = None
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_schools()
        
        log_user_action("فتح صفحة إدارة المعلمين")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(20)
            
            # شريط البحث والفلترة
            self.create_search_bar(layout)
            
            # جدول المعلمين
            self.create_teachers_table(layout)
            
            # شريط الأدوات
            self.create_toolbar(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة المعلمين: {e}")
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
            
            # مربع البحث
            search_label = QLabel("البحث:")
            search_label.setFixedWidth(50)
            
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("البحث بالاسم أو رقم الهاتف...")
            self.search_input.setMinimumWidth(250)
            
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
            search_layout.addStretch()
            search_layout.addWidget(search_label)
            search_layout.addWidget(self.search_input)
            search_layout.addWidget(search_btn)
            search_layout.addWidget(clear_btn)
            
            layout.addWidget(search_frame)
            
            # ربط الأحداث
            search_btn.clicked.connect(self.search_teachers)
            clear_btn.clicked.connect(self.clear_search)
            self.search_input.returnPressed.connect(self.search_teachers)
            # بحث لحظي عند الكتابة بدلاً من استخدام زر البحث
            self.search_input.textChanged.connect(self.search_teachers)
            # إخفاء زر البحث لأنه لم يعد ضروريًا مع البحث اللحظي
            search_btn.hide()
            self.school_filter.currentTextChanged.connect(self.on_school_filter_changed)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط البحث: {e}")
            raise
    
    def create_teachers_table(self, layout):
        """إنشاء جدول المعلمين"""
        try:
            # إطار الجدول
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")
            
            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)
            
            # عنوان الجدول
            table_header = QLabel("قائمة المعلمين")
            table_header.setObjectName("tableHeader")
            table_layout.addWidget(table_header)
            
            # الجدول
            self.teachers_table = QTableWidget()
            self.teachers_table.setObjectName("dataTable")
            
            # إعداد أعمدة الجدول
            columns = ["م", "الاسم", "المدرسة", "عدد الحصص", "الراتب الشهري", "رقم الهاتف", "ملاحظات"]
            self.teachers_table.setColumnCount(len(columns))
            self.teachers_table.setHorizontalHeaderLabels(columns)
            
            # إعداد خصائص الجدول
            self.teachers_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.teachers_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.teachers_table.setAlternatingRowColors(True)
            self.teachers_table.setSortingEnabled(True)
            
            # تكوين عرض الأعمدة
            header = self.teachers_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.resizeSection(0, 50)   # رقم التسلسل
            header.resizeSection(1, 200)  # الاسم
            header.resizeSection(2, 150)  # المدرسة
            header.resizeSection(3, 100)  # عدد الحصص
            header.resizeSection(4, 120)  # الراتب
            header.resizeSection(5, 120)  # الهاتف
            
            table_layout.addWidget(self.teachers_table)
            layout.addWidget(table_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول المعلمين: {e}")
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
            self.add_btn = QPushButton("إضافة معلم")
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
            self.stats_label = QLabel("إجمالي المعلمين: 0")
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
            self.teachers_table.selectionModel().selectionChanged.connect(self.on_selection_changed)
            self.teachers_table.cellDoubleClicked.connect(self.edit_teacher)
            self.teachers_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.teachers_table.customContextMenuRequested.connect(self.show_context_menu)
            
            # أحداث الأزرار
            self.add_btn.clicked.connect(self.add_teacher)
            self.edit_btn.clicked.connect(self.edit_teacher)
            self.delete_btn.clicked.connect(self.delete_teacher)
            self.refresh_btn.clicked.connect(self.refresh_data)
            self.print_btn.clicked.connect(self.print_teachers_list)
            
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
                    
            self.load_teachers()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المدارس:\n{e}")
    
    def load_teachers(self):
        """تحميل بيانات المعلمين"""
        try:
            query = """
                SELECT t.*, s.name_ar as school_name 
                FROM teachers t 
                LEFT JOIN schools s ON t.school_id = s.id 
                ORDER BY t.name
            """
            
            params = []
            
            # تطبيق فلتر المدرسة
            if self.selected_school_id:
                query = """
                    SELECT t.*, s.name_ar as school_name 
                    FROM teachers t 
                    LEFT JOIN schools s ON t.school_id = s.id 
                    WHERE t.school_id = ?
                    ORDER BY t.name
                """
                params = [self.selected_school_id]
            
            with db_manager.get_cursor() as cursor:
                cursor.execute(query, params)
                teachers = cursor.fetchall()
                
                self.current_teachers = teachers
                self.populate_table(teachers)
                self.update_stats()
                
        except Exception as e:
            logging.error(f"خطأ في تحميل المعلمين: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات المعلمين:\n{e}")
    
    def populate_table(self, teachers):
        """ملء الجدول بالبيانات"""
        try:
            self.teachers_table.setRowCount(len(teachers))
            
            for row, teacher in enumerate(teachers):
                # رقم التسلسل
                self.teachers_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                
                # الاسم
                self.teachers_table.setItem(row, 1, QTableWidgetItem(teacher['name'] or ''))
                
                # المدرسة
                self.teachers_table.setItem(row, 2, QTableWidgetItem(teacher['school_name'] or ''))
                
                # عدد الحصص
                self.teachers_table.setItem(row, 3, QTableWidgetItem(str(teacher['class_hours'] or 0)))
                
                # الراتب الشهري
                salary = f"{teacher['monthly_salary']:.2f}" if teacher['monthly_salary'] else "0.00"
                self.teachers_table.setItem(row, 4, QTableWidgetItem(salary))
                
                # رقم الهاتف
                self.teachers_table.setItem(row, 5, QTableWidgetItem(teacher['phone'] or ''))
                
                # الملاحظات
                self.teachers_table.setItem(row, 6, QTableWidgetItem(teacher['notes'] or ''))
                
                # إخفاء ID في البيانات
                self.teachers_table.item(row, 0).setData(Qt.UserRole, teacher['id'])
            
            # تعديل أعمدة الجدول
            self.teachers_table.resizeColumnsToContents()
            
        except Exception as e:
            logging.error(f"خطأ في ملء الجدول: {e}")
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        try:
            count = len(self.current_teachers)
            self.stats_label.setText(f"إجمالي المعلمين: {count}")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث الإحصائيات: {e}")
    
    def on_selection_changed(self):
        """معالج تغيير التحديد"""
        try:
            has_selection = bool(self.teachers_table.selectedItems())
            self.edit_btn.setEnabled(has_selection)
            self.delete_btn.setEnabled(has_selection)
            
        except Exception as e:
            logging.error(f"خطأ في معالج التحديد: {e}")
    
    def on_school_filter_changed(self):
        """معالج تغيير فلتر المدرسة"""
        try:
            self.selected_school_id = self.school_filter.currentData()
            self.load_teachers()
            
        except Exception as e:
            logging.error(f"خطأ في فلتر المدرسة: {e}")
    
    def search_teachers(self):
        """البحث في المعلمين"""
        try:
            search_text = self.search_input.text().strip().lower()
            
            if not search_text:
                self.populate_table(self.current_teachers)
                return
                
            filtered_teachers = []
            for teacher in self.current_teachers:
                if (search_text in (teacher['name'] or '').lower() or
                    search_text in (teacher['phone'] or '').lower()):
                    filtered_teachers.append(teacher)
            
            self.populate_table(filtered_teachers)
            
        except Exception as e:
            logging.error(f"خطأ في البحث: {e}")
    
    def clear_search(self):
        """مسح البحث"""
        try:
            self.search_input.clear()
            self.school_filter.setCurrentIndex(0)
            self.selected_school_id = None
            self.load_teachers()
            
        except Exception as e:
            logging.error(f"خطأ في مسح البحث: {e}")
    
    def add_teacher(self):
        """إضافة معلم جديد"""
        try:
            dialog = AddTeacherDialog(self)
            if dialog.exec_() == dialog.Accepted:
                self.load_teachers()
                log_user_action("إضافة معلم جديد")
                
        except Exception as e:
            logging.error(f"خطأ في إضافة معلم: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في إضافة معلم:\n{e}")
    
    def edit_teacher(self):
        """تعديل المعلم المحدد"""
        try:
            current_row = self.teachers_table.currentRow()
            if current_row < 0:
                return
                
            teacher_id = self.teachers_table.item(current_row, 0).data(Qt.UserRole)
            if not teacher_id:
                return
                
            dialog = EditTeacherDialog(teacher_id, self)
            if dialog.exec_() == dialog.Accepted:
                self.load_teachers()
                log_user_action("تعديل بيانات معلم", str(teacher_id))
                
        except Exception as e:
            logging.error(f"خطأ في تعديل معلم: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تعديل المعلم:\n{e}")
    
    def delete_teacher(self):
        """حذف المعلم المحدد"""
        try:
            current_row = self.teachers_table.currentRow()
            if current_row < 0:
                return
                
            teacher_id = self.teachers_table.item(current_row, 0).data(Qt.UserRole)
            teacher_name = self.teachers_table.item(current_row, 1).text()
            
            # تأكيد الحذف
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                f"هل أنت متأكد من حذف المعلم '{teacher_name}'؟\n\nهذا الإجراء لا يمكن التراجع عنه.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                with db_manager.get_cursor() as cursor:
                    cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
                    
                self.load_teachers()
                log_user_action("حذف معلم", str(teacher_id))
                QMessageBox.information(self, "نجح", "تم حذف المعلم بنجاح")
                
        except Exception as e:
            logging.error(f"خطأ في حذف معلم: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في حذف المعلم:\n{e}")
    
    def refresh_data(self):
        """تحديث البيانات"""
        try:
            self.load_schools()
            log_user_action("تحديث بيانات المعلمين")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث البيانات: {e}")
    
    def show_context_menu(self, position):
        """عرض قائمة السياق"""
        try:
            if self.teachers_table.itemAt(position) is None:
                return
                
            menu = QMenu(self)
            
            edit_action = QAction("تعديل", self)
            edit_action.triggered.connect(self.edit_teacher)
            menu.addAction(edit_action)
            
            delete_action = QAction("حذف", self)
            delete_action.triggered.connect(self.delete_teacher)
            menu.addAction(delete_action)
            
            menu.exec_(self.teachers_table.mapToGlobal(position))
            
        except Exception as e:
            logging.error(f"خطأ في قائمة السياق: {e}")
    
    def print_teachers_list(self):
        """طباعة قائمة المعلمين مع المعاينة والفلترة"""
        try:
            log_user_action("طباعة قائمة المعلمين")
            
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
            from core.printing.print_manager import print_teachers_list
            print_teachers_list(self.current_teachers, filter_info, parent=self)
            
        except Exception as e:
            logging.error(f"خطأ في طباعة قائمة المعلمين: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في طباعة قائمة المعلمين:\n{e}")
