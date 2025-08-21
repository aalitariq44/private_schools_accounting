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
from PyQt5.QtGui import QFont, QFontDatabase

import config
from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation

# استيراد نوافذ إدارة الموظفين
from .add_employee_dialog import AddEmployeeDialog
from .edit_employee_dialog import EditEmployeeDialog
from ..shared.salary_details_dialog import SalaryDetailsDialog


class EmployeesPage(QWidget):
    """صفحة إدارة الموظفين"""
    
    # إشارات النافذة
    page_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_employees = []
        
        self.setup_cairo_font()
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_schools()
        
        log_user_action("فتح صفحة إدارة الموظفين")

    def setup_cairo_font(self):
        """تحميل وتطبيق خط Cairo"""
        try:
            font_db = QFontDatabase()
            font_dir = config.RESOURCES_DIR / "fonts"
            
            id_medium = font_db.addApplicationFont(str(font_dir / "Cairo-Medium.ttf"))
            id_bold = font_db.addApplicationFont(str(font_dir / "Cairo-Bold.ttf"))
            
            families = font_db.applicationFontFamilies(id_medium)
            self.cairo_family = families[0] if families else "Arial"
            
            logging.info(f"تم تحميل خط Cairo بنجاح: {self.cairo_family}")
            
        except Exception as e:
            logging.warning(f"فشل في تحميل خط Cairo، استخدام الخط الافتراضي: {e}")
            self.cairo_family = "Arial"

    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            self.create_toolbar(layout)
            self.create_employees_table(layout)
            self.create_summary(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة الموظفين: {e}")
            raise
    
    def create_employees_table(self, layout):
        """إنشاء جدول الموظفين"""
        try:
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")
            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)

            self.employees_table = QTableWidget()
            self.employees_table.setObjectName("dataTable")

            columns = ["المعرف", "الاسم", "المدرسة", "المهنة", "الراتب الشهري", "رقم الهاتف", "ملاحظات"]
            self.employees_table.setColumnCount(len(columns))
            self.employees_table.setHorizontalHeaderLabels(columns)

            self.employees_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.employees_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.employees_table.setAlternatingRowColors(True)
            self.employees_table.setSortingEnabled(True)

            header = self.employees_table.horizontalHeader()
            header.setStretchLastSection(True)
            for i in range(len(columns)):
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

            self.employees_table.setStyleSheet("QTableWidget::item { padding: 0px; }")
            # إخفاء عمود المعرف من العرض
            self.employees_table.setColumnHidden(0, True)

            self.employees_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.employees_table.customContextMenuRequested.connect(self.show_context_menu)
            self.employees_table.doubleClicked.connect(self.show_employee_details)

            table_layout.addWidget(self.employees_table)
            layout.addWidget(table_frame)

        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول الموظفين: {e}")
            raise
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات والفلاتر"""
        try:
            toolbar_frame = QFrame()
            toolbar_frame.setObjectName("toolbarFrame")
            toolbar_layout = QVBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(15, 10, 15, 10)
            toolbar_layout.setSpacing(10)

            filters_layout = QHBoxLayout()
            
            school_label = QLabel("المدرسة:")
            school_label.setObjectName("filterLabel")
            filters_layout.addWidget(school_label)
            self.school_combo = QComboBox()
            self.school_combo.setObjectName("filterCombo")
            self.school_combo.setMinimumWidth(200)
            filters_layout.addWidget(self.school_combo)

            job_label = QLabel("المهنة:")
            job_label.setObjectName("filterLabel")
            filters_layout.addWidget(job_label)
            self.job_combo = QComboBox()
            self.job_combo.setObjectName("filterCombo")
            self.job_combo.setMinimumWidth(150)
            # expanded job filters
            self.job_combo.addItems([
                "جميع المهن",
                "محاسب", "كاتب", "عامل", "عامل نظافة", "حارس ليلي", "حارس أمن", "سائق",
                "مساعد", "مساعد إداري", "فني صيانة", "عامل مختبر", "مشرف", "مرشد طلابي",
                "أمينة مكتبة", "أمين مكتبة", "ممرض",
                "مخصص"
            ])
            filters_layout.addWidget(self.job_combo)
            
            filters_layout.addStretch()
            toolbar_layout.addLayout(filters_layout)

            actions_layout = QHBoxLayout()
            search_label = QLabel("البحث:")
            search_label.setObjectName("filterLabel")
            actions_layout.addWidget(search_label)
            self.search_input = QLineEdit()
            self.search_input.setObjectName("searchInput")
            self.search_input.setPlaceholderText("ابحث في أسماء الموظفين...")
            self.search_input.setMinimumWidth(300)
            actions_layout.addWidget(self.search_input)
            actions_layout.addStretch()

            self.add_employee_button = QPushButton("إضافة موظف")
            self.add_employee_button.setObjectName("primaryButton")
            actions_layout.addWidget(self.add_employee_button)

            self.print_list_button = QPushButton("طباعة القائمة")
            self.print_list_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.print_list_button)

            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.refresh_button)

            self.clear_filters_button = QPushButton("مسح الفلاتر")
            self.clear_filters_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.clear_filters_button)
            
            toolbar_layout.addLayout(actions_layout)
            layout.addWidget(toolbar_frame)
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
            raise

    def create_summary(self, layout):
        """إنشاء ملخص الموظفين"""
        try:
            summary_frame = QFrame()
            summary_frame.setObjectName("summaryFrame")
            summary_layout = QHBoxLayout(summary_frame)
            summary_layout.setContentsMargins(15, 10, 15, 10)

            numbers_layout = QVBoxLayout()
            summary_title = QLabel("ملخص الموظفين")
            summary_title.setObjectName("summaryTitle")
            numbers_layout.addWidget(summary_title)
            
            numbers_grid = QHBoxLayout()
            total_layout = QVBoxLayout()
            total_layout.setAlignment(Qt.AlignCenter)
            self.total_employees_label = QLabel("إجمالي الموظفين")
            self.total_employees_label.setAlignment(Qt.AlignCenter)
            self.total_employees_label.setObjectName("summaryLabel")
            total_layout.addWidget(self.total_employees_label)
            self.total_employees_value = QLabel("0")
            self.total_employees_value.setAlignment(Qt.AlignCenter)
            self.total_employees_value.setObjectName("summaryValue")
            total_layout.addWidget(self.total_employees_value)
            numbers_grid.addLayout(total_layout)
            numbers_layout.addLayout(numbers_grid)
            summary_layout.addLayout(numbers_layout)

            stats_layout = QVBoxLayout()
            self.displayed_count_label = QLabel("عدد الموظفين المعروضين: 0")
            self.displayed_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.displayed_count_label)
            summary_layout.addLayout(stats_layout)

            self.last_update_label = QLabel("آخر تحديث: --")
            self.last_update_label.setObjectName("statLabel")
            summary_layout.addWidget(self.last_update_label)
            
            layout.addWidget(summary_frame)
        except Exception as e:
            logging.error(f"خطأ في إنشاء ملخص الموظفين: {e}")
            raise
    
    def setup_styles(self):
        """إعداد تنسيقات الصفحة"""
        try:
            cairo_font = f"'{self.cairo_family}', 'Cairo', 'Segoe UI', Tahoma, Arial"
            
            style = """
                QWidget {{
                    background-color: #F8F9FA;
                    font-family: {font_family};
                    font-size: 16px;
                }}
                #toolbarFrame {{
                    background-color: white;
                    border: 1px solid #E9ECEF;
                    border-radius: 8px;
                    margin-bottom: 10px;
                }}
                #filterLabel {{
                    font-weight: bold;
                    color: #2C3E50;
                    margin-right: 5px;
                    font-size: 16px;
                    font-family: {font_family};
                }}
                #filterCombo, #searchInput {{
                    padding: 8px 12px;
                    border: 1px solid #BDC3C7;
                    border-radius: 6px;
                    font-size: 16px;
                    background-color: white;
                    font-family: {font_family};
                }}
                #primaryButton {{
                    background-color: #16A085; /* Green color for employees */
                    border: none;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 16px;
                    font-family: {font_family};
                }}
                #secondaryButton {{
                    background-color: #27AE60;
                    border: none;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 16px;
                    font-family: {font_family};
                }}
                QTableWidget {{
                    background-color: white;
                    border: 1px solid #E9ECEF;
                    border-radius: 8px;
                    font-size: 16px;
                    font-family: {font_family};
                }}
                QTableWidget::item {{
                    padding: 12px;
                    border-bottom: 1px solid #E9ECEF;
                }}
                QTableWidget::item:selected {{
                    background-color: #3498DB;
                    color: white;
                }}
                QHeaderView::section {{
                    background-color: #16A085; /* Green color for employees */
                    color: white;
                    padding: 12px;
                    border: none;
                    font-weight: bold;
                    font-size: 16px;
                    font-family: {font_family};
                }}
                #summaryFrame {{
                    background-color: white;
                    border: 1px solid #E9ECEF;
                    border-radius: 8px;
                    padding: 10px;
                }}
                #summaryTitle {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin-bottom: 10px;
                }}
                #summaryLabel {{
                    font-size: 16px;
                    color: #7F8C8D;
                }}
                #summaryValue {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #2980B9;
                }}
                #statLabel {{
                    font-size: 14px;
                    color: #7F8C8D;
                }}
            """.format(font_family=cairo_font)
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الستايل: {e}")
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            self.add_employee_button.clicked.connect(self.add_employee)
            self.print_list_button.clicked.connect(self.print_employees_list)
            self.refresh_button.clicked.connect(self.refresh)
            self.clear_filters_button.clicked.connect(self.clear_filters)
            
            self.school_combo.currentTextChanged.connect(self.apply_filters)
            self.job_combo.currentTextChanged.connect(self.apply_filters)
            self.search_input.textChanged.connect(self.apply_filters)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")

    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            self.school_combo.clear()
            self.school_combo.addItem("جميع المدارس", None)
            
            query = "SELECT id, name_ar FROM schools ORDER BY name_ar"
            schools = db_manager.execute_query(query)
            
            if schools:
                for school in schools:
                    self.school_combo.addItem(school['name_ar'], school['id'])
            
            self.refresh()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")

    def load_employees(self):
        """تحميل قائمة الموظفين"""
        try:
            query = """
                SELECT e.id, e.name, s.name_ar as school_name,
                       e.job_type, e.monthly_salary, e.phone, e.notes
                FROM employees e
                LEFT JOIN schools s ON e.school_id = s.id
                WHERE 1=1
            """
            params = []
            
            selected_school_id = self.school_combo.currentData()
            if selected_school_id:
                query += " AND e.school_id = ?"
                params.append(selected_school_id)

            selected_job = self.job_combo.currentText()
            if selected_job and selected_job != "جميع المهن":
                if selected_job == 'مخصص':
                    # عرض الموظفين الذين مهنتهم غير موجودة ضمن الوظائف الافتراضية
                    default_jobs = [
                        "محاسب", "كاتب", "عامل", "عامل نظافة", "حارس ليلي", "حارس أمن", "سائق",
                        "مساعد", "مساعد إداري", "فني صيانة", "عامل مختبر", "مشرف", "مرشد طلابي",
                        "أمينة مكتبة", "أمين مكتبة", "ممرض"
                    ]
                    placeholders = ", ".join("?" for _ in default_jobs)
                    query += f" AND e.job_type NOT IN ({placeholders})"
                    params.extend(default_jobs)
                else:
                    query += " AND e.job_type = ?"
                    params.append(selected_job)
            
            search_text = self.search_input.text().strip()
            if search_text:
                query += " AND e.name LIKE ?"
                params.append(f"%{search_text}%")
            
            query += " ORDER BY e.name"
            
            self.current_employees = db_manager.execute_query(query, tuple(params))
            
            self.populate_table()
            self.update_stats()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الموظفين: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل بيانات الموظفين:\n{str(e)}")

    def populate_table(self):
        """ملء جدول الموظفين بالبيانات"""
        try:
            self.employees_table.setRowCount(0)
            
            if not self.current_employees:
                self.displayed_count_label.setText("عدد الموظفين المعروضين: 0")
                return
            
            for row_idx, employee in enumerate(self.current_employees):
                self.employees_table.insertRow(row_idx)
                
                items = [
                    str(employee['id']),
                    employee['name'] or "",
                    employee['school_name'] or "",
                    employee['job_type'] or "",
                    f"{employee['monthly_salary']:,.0f} د.ع" if employee['monthly_salary'] else "0 د.ع",
                    employee['phone'] or "",
                    employee['notes'] or ""
                ]
                
                for col_idx, item_text in enumerate(items):
                    item = QTableWidgetItem(item_text)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.employees_table.setItem(row_idx, col_idx, item)
            
            self.displayed_count_label.setText(f"عدد الموظفين المعروضين: {len(self.current_employees)}")
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول الموظفين: {e}")

    def update_stats(self):
        """تحديث الإحصائيات"""
        try:
            total_employees_count = len(self.current_employees)
            
            self.total_employees_value.setText(str(total_employees_count))
            self.displayed_count_label.setText(f"عدد الموظفين المعروضين: {total_employees_count}")
            
            from datetime import datetime
            self.last_update_label.setText(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث الإحصائيات: {e}")

    def apply_filters(self):
        """تطبيق الفلاتر وإعادة تحميل البيانات"""
        self.load_employees()

    def refresh(self):
        """تحديث البيانات"""
        log_user_action("تحديث صفحة الموظفين")
        self.load_employees()
            
    def clear_filters(self):
        """مسح جميع الفلاتر"""
        self.school_combo.setCurrentIndex(0)
        self.job_combo.setCurrentIndex(0)
        self.search_input.clear()
        self.apply_filters()
        log_user_action("مسح فلاتر صفحة الموظفين")

    def add_employee(self):
        """إضافة موظف جديد"""
        try:
            dialog = AddEmployeeDialog(self)
            if dialog.exec_() == dialog.Accepted:
                self.refresh()
                log_user_action("إضافة موظف جديد", "نجح")
        except Exception as e:
            logging.error(f"خطأ في إضافة موظف: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في إضافة موظف:\n{e}")

    def edit_employee_by_id(self, employee_id):
        """تعديل الموظف المحدد"""
        try:
            dialog = EditEmployeeDialog(employee_id, self)
            if dialog.exec_() == dialog.Accepted:
                self.refresh()
                log_user_action(f"تعديل بيانات الموظف {employee_id}", "نجح")
        except Exception as e:
            logging.error(f"خطأ في تعديل موظف: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تعديل الموظف:\n{e}")

    def delete_employee(self, employee_id):
        """حذف الموظف المحدد مع رواتبه"""
        try:
            # أولاً، التحقق من وجود رواتب للموظف
            salary_query = "SELECT COUNT(*) as count FROM salaries WHERE staff_type = 'employee' AND staff_id = ?"
            salary_result = db_manager.execute_query(salary_query, (employee_id,))
            salary_count = salary_result[0]['count'] if salary_result else 0
            
            # إعداد رسالة التحذير
            if salary_count > 0:
                warning_message = f"""هل أنت متأكد من حذف هذا الموظف؟

⚠️ تحذير: سيتم حذف جميع الرواتب المرتبطة بهذا الموظف أيضاً!

عدد الرواتب المسجلة: {salary_count}

هذا الإجراء لا يمكن التراجع عنه."""
            else:
                warning_message = "هل أنت متأكد من حذف هذا الموظف؟"
            
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                warning_message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # بدء عملية الحذف باستخدام transaction
                with db_manager.get_cursor() as cursor:
                    # حذف الرواتب أولاً
                    cursor.execute("DELETE FROM salaries WHERE staff_type = 'employee' AND staff_id = ?", (employee_id,))
                    deleted_salaries = cursor.rowcount
                    
                    # ثم حذف الموظف
                    cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
                    affected_rows = cursor.rowcount
                    
                    if affected_rows > 0:
                        success_message = "تم حذف الموظف بنجاح"
                        if deleted_salaries > 0:
                            success_message += f"\nتم حذف {deleted_salaries} راتب مرتبط بالموظف"
                        
                        QMessageBox.information(self, "نجح", success_message)
                        self.refresh()
                        log_user_action(f"حذف الموظف {employee_id} مع {deleted_salaries} راتب", "نجح")
                    else:
                        QMessageBox.warning(self, "خطأ", "لم يتم العثور على الموظف")
                
        except Exception as e:
            logging.error(f"خطأ في حذف موظف: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في حذف الموظف:\n{e}")

    def show_context_menu(self, position):
        """عرض قائمة السياق"""
        try:
            if self.employees_table.itemAt(position) is None: return
            current_row = self.employees_table.currentRow()
            if current_row < 0: return
            employee_id_item = self.employees_table.item(current_row, 0)
            if not employee_id_item: return
            employee_id = int(employee_id_item.text())
            employee_name = self.employees_table.item(current_row, 1).text()
            
            menu = QMenu(self)
            
            details_action = QAction("عرض تفاصيل الرواتب", self)
            details_action.triggered.connect(lambda: self.show_employee_salary_details(employee_id, employee_name))
            menu.addAction(details_action)
            
            menu.addSeparator()
            
            edit_action = QAction("تعديل", self)
            edit_action.triggered.connect(lambda: self.edit_employee_by_id(employee_id))
            menu.addAction(edit_action)
            
            delete_action = QAction("حذف", self)
            delete_action.triggered.connect(lambda: self.delete_employee(employee_id))
            menu.addAction(delete_action)
            
            menu.exec_(self.employees_table.mapToGlobal(position))
        except Exception as e:
            logging.error(f"خطأ في قائمة السياق: {e}")

    def print_employees_list(self):
        """طباعة قائمة الموظفين مع المعاينة والفلترة"""
        try:
            log_user_action("طباعة قائمة الموظفين")
            filters = []
            school = self.school_combo.currentText()
            if school and school != "جميع المدارس":
                filters.append(f"المدرسة: {school}")
            
            search = self.search_input.text().strip()
            if search:
                filters.append(f"بحث: {search}")
            
            filter_info = "؛ ".join(filters) if filters else None
            
            from core.printing.print_manager import print_employees_list
            print_employees_list(self.current_employees, filter_info, parent=self)
        except Exception as e:
            logging.error(f"خطأ في طباعة قائمة الموظفين: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في طباعة قائمة الموظفين:\n{e}")

    def show_employee_details(self):
        """عرض تفاصيل الموظف عند الضغط المزدوج"""
        try:
            current_row = self.employees_table.currentRow()
            if current_row < 0:
                return
            
            employee_id_item = self.employees_table.item(current_row, 0)
            employee_name_item = self.employees_table.item(current_row, 1)
            
            if not employee_id_item or not employee_name_item:
                return
            
            employee_id = int(employee_id_item.text())
            employee_name = employee_name_item.text()
            
            self.show_employee_salary_details(employee_id, employee_name)
            
        except Exception as e:
            logging.error(f"خطأ في عرض تفاصيل الموظف: {e}")

    def show_employee_salary_details(self, employee_id, employee_name):
        """عرض نافذة تفاصيل رواتب الموظف"""
        try:
            dialog = SalaryDetailsDialog("employee", employee_id, employee_name, self)
            dialog.exec_()
        except Exception as e:
            logging.error(f"خطأ في عرض تفاصيل رواتب الموظف: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في عرض تفاصيل الرواتب:\n{e}")
