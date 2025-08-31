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
    QMenu, QComboBox, QDateEdit, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QFontDatabase

import config
from core.database.connection import db_manager
from core.utils.logger import log_user_action

# استيراد نوافذ إدارة الرواتب
from .add_salary_dialog import AddSalaryDialog
from .edit_salary_dialog import EditSalaryDialog

# استيراد وحدة أحجام الخطوط
from ...font_sizes import FontSizeManager
from ...ui_settings_manager import ui_settings_manager


# Subclass QTableWidgetItem for numeric sorting of ID column
class NumericTableWidgetItem(QTableWidgetItem):
    """QTableWidgetItem subclass for numeric sorting based on integer value."""
    def __lt__(self, other):
        try:
            return int(self.text()) < int(other.text())
        except ValueError:
            return self.text() < other.text()


class SalariesPage(QWidget):
    """صفحة إدارة الرواتب"""
    
    def __init__(self):
        super().__init__()
        self.current_salaries = []
        
        # الحصول على حجم الخط المحفوظ من إعدادات UI
        self.current_font_size = ui_settings_manager.get_font_size("salaries")
        
        self.setup_cairo_font()
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_schools()
        self.load_persons_list()
        self.refresh()

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
            # ضبط حجم الخط الافتراضي الأصغر الملائم للتصميم المبسط
            self.setFont(QFont(self.cairo_family, 13))
            
        except Exception as e:
            logging.warning(f"فشل في تحميل خط Cairo، استخدام الخط الافتراضي: {e}")
            self.cairo_family = "Arial"
            self.setFont(QFont(self.cairo_family, 13))

    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            layout = QVBoxLayout(self)
            # تقليل الهوامش والمسافات لتكثيف المحتوى على الشاشات الصغيرة
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(8)
            
            self.create_toolbar(layout)
            self.create_salaries_table(layout)
            self.create_summary(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة الرواتب: {e}")
            raise
    
    def create_salaries_table(self, layout):
        """إنشاء جدول الرواتب"""
        try:
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")
            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)

            self.salaries_table = QTableWidget()
            self.salaries_table.setObjectName("dataTable")

            columns = ["المعرف", "الاسم", "المدرسة", "النوع", "الراتب المسجل", "المدفوع", "فترة الراتب", "تاريخ الدفع", "ملاحظات"]
            self.salaries_table.setColumnCount(len(columns))
            self.salaries_table.setHorizontalHeaderLabels(columns)

            self.salaries_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.salaries_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.salaries_table.setAlternatingRowColors(True)
            self.salaries_table.setSortingEnabled(True)

            header = self.salaries_table.horizontalHeader()
            header.setStretchLastSection(True)
            for i in range(len(columns)):
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

            self.salaries_table.setStyleSheet("QTableWidget::item { padding: 0px; }")
            self.salaries_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.salaries_table.customContextMenuRequested.connect(self.show_context_menu)
            self.salaries_table.doubleClicked.connect(self.on_table_double_click)

            table_layout.addWidget(self.salaries_table)
            layout.addWidget(table_frame)

        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول الرواتب: {e}")
            raise
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات والفلاتر"""
        try:
            toolbar_frame = QFrame()
            toolbar_frame.setObjectName("toolbarFrame")
            toolbar_layout = QVBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(8, 6, 8, 6)
            toolbar_layout.setSpacing(6)

            filters_layout = QHBoxLayout()
            
            school_label = QLabel("المدرسة:")
            school_label.setObjectName("filterLabel")
            filters_layout.addWidget(school_label)
            self.school_combo = QComboBox()
            self.school_combo.setObjectName("filterCombo")
            filters_layout.addWidget(self.school_combo)

            type_label = QLabel("النوع:")
            type_label.setObjectName("filterLabel")
            filters_layout.addWidget(type_label)
            self.type_combo = QComboBox()
            self.type_combo.addItems(["الكل", "معلم", "موظف"])
            self.type_combo.setObjectName("filterCombo")
            filters_layout.addWidget(self.type_combo)

            person_label = QLabel("الشخص:")
            person_label.setObjectName("filterLabel")
            filters_layout.addWidget(person_label)
            self.person_combo = QComboBox()
            self.person_combo.setObjectName("filterCombo")
            self.person_combo.setMinimumWidth(200)
            filters_layout.addWidget(self.person_combo)

            from_label = QLabel("من:")
            from_label.setObjectName("filterLabel")
            filters_layout.addWidget(from_label)
            self.from_date_edit = QDateEdit(calendarPopup=True)
            self.from_date_edit.setDate(QDate(2024, 1, 1))
            self.from_date_edit.setObjectName("filterCombo")
            filters_layout.addWidget(self.from_date_edit)

            to_label = QLabel("إلى:")
            to_label.setObjectName("filterLabel")
            filters_layout.addWidget(to_label)
            self.to_date_edit = QDateEdit(calendarPopup=True)
            self.to_date_edit.setDate(QDate(2040, 12, 31))
            self.to_date_edit.setObjectName("filterCombo")
            filters_layout.addWidget(self.to_date_edit)

            filters_layout.addStretch()
            toolbar_layout.addLayout(filters_layout)

            actions_layout = QHBoxLayout()
            search_label = QLabel("البحث:")
            search_label.setObjectName("filterLabel")
            actions_layout.addWidget(search_label)
            self.search_input = QLineEdit()
            self.search_input.setObjectName("searchInput")
            self.search_input.setPlaceholderText("ابحث...")
            actions_layout.addWidget(self.search_input)
            
            # فلتر حجم الخط
            font_size_label = QLabel("حجم الخط:")
            font_size_label.setObjectName("filterLabel")
            actions_layout.addWidget(font_size_label)
            
            self.font_size_combo = QComboBox()
            self.font_size_combo.setObjectName("filterCombo")
            self.font_size_combo.addItems(FontSizeManager.get_available_sizes())
            self.font_size_combo.setCurrentText(self.current_font_size)
            self.font_size_combo.setMinimumWidth(100)
            actions_layout.addWidget(self.font_size_combo)
            
            actions_layout.addStretch()

            self.add_button = QPushButton("إضافة راتب")
            self.add_button.setObjectName("primaryButton")
            actions_layout.addWidget(self.add_button)

            self.print_button = QPushButton("طباعة")
            self.print_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.print_button)

            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.refresh_button)

            self.clear_button = QPushButton("مسح الفلاتر")
            self.clear_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.clear_button)
            
            toolbar_layout.addLayout(actions_layout)
            layout.addWidget(toolbar_frame)
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
            raise

    def create_summary(self, layout):
        """إنشاء ملخص الإحصائيات المفصل"""
        try:
            summary_frame = QFrame()
            summary_frame.setObjectName("summaryFrame")
            summary_layout = QHBoxLayout(summary_frame)
            summary_layout.setContentsMargins(8, 6, 8, 6)
            
            def create_stat_box(title, value_widget):
                box = QVBoxLayout()
                box.setAlignment(Qt.AlignCenter)
                title_label = QLabel(title)
                title_label.setObjectName("summaryLabel")
                title_label.setAlignment(Qt.AlignCenter)
                value_widget.setAlignment(Qt.AlignCenter)
                box.addWidget(title_label)
                box.addWidget(value_widget)
                return box

            # General Stats
            self.total_paid_value = QLabel("0 د.ع")
            self.total_paid_value.setObjectName("summaryValue")
            summary_layout.addLayout(create_stat_box("إجمالي المدفوع", self.total_paid_value))

            self.payments_count_value = QLabel("0")
            self.payments_count_value.setObjectName("summaryValue")
            summary_layout.addLayout(create_stat_box("عدد الدفعات", self.payments_count_value))

            self.avg_salary_value = QLabel("0 د.ع")
            self.avg_salary_value.setObjectName("summaryValue")
            summary_layout.addLayout(create_stat_box("متوسط الراتب", self.avg_salary_value))

            # Teacher Stats
            self.teachers_total_value = QLabel("0 د.ع")
            self.teachers_total_value.setObjectName("summaryValueSuccess")
            summary_layout.addLayout(create_stat_box("مدفوعات المعلمين", self.teachers_total_value))

            # Employee Stats
            self.employees_total_value = QLabel("0 د.ع")
            self.employees_total_value.setObjectName("summaryValueWarning")
            summary_layout.addLayout(create_stat_box("مدفوعات الموظفين", self.employees_total_value))

            self.last_update_label = QLabel("آخر تحديث: --")
            self.last_update_label.setObjectName("statLabel")
            summary_layout.addStretch()
            summary_layout.addWidget(self.last_update_label)

            layout.addWidget(summary_frame)
        except Exception as e:
            logging.error(f"خطأ في إنشاء ملخص الرواتب: {e}")
            raise
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            self.add_button.clicked.connect(self.add_salary)
            self.refresh_button.clicked.connect(self.refresh)
            self.clear_button.clicked.connect(self.clear_filters)
            
            self.search_input.textChanged.connect(self.apply_filters)
            self.school_combo.currentTextChanged.connect(self.load_persons_list)
            self.school_combo.currentTextChanged.connect(self.apply_filters)
            self.type_combo.currentTextChanged.connect(self.load_persons_list)
            self.type_combo.currentTextChanged.connect(self.apply_filters)
            self.person_combo.currentTextChanged.connect(self.apply_filters)
            self.from_date_edit.dateChanged.connect(self.apply_filters)
            self.to_date_edit.dateChanged.connect(self.apply_filters)
            
            # ربط تغيير حجم الخط
            if hasattr(self, 'font_size_combo'):
                self.font_size_combo.currentTextChanged.connect(self.change_font_size)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def setup_styles(self):
        """إعداد تنسيقات الصفحة"""
        try:
            # استخدام FontSizeManager لإنشاء CSS
            style = FontSizeManager.generate_css_styles(self.current_font_size)
            
            # تطبيق التنسيقات على الصفحة
            self.setStyleSheet(style)
            
            # إجبار إعادة رسم جميع المكونات
            self.update()
            if hasattr(self, 'salaries_table'):
                self.salaries_table.update()
            if hasattr(self, 'summary_frame'):
                self.summary_frame.update()
            
        except Exception as e:
            logging.error(f"خطأ في إعداد تنسيقات صفحة الرواتب: {e}")
    
    def change_font_size(self):
        """تغيير حجم الخط في الصفحة"""
        try:
            if not hasattr(self, 'font_size_combo'):
                return
                
            selected_size = self.font_size_combo.currentText()
            
            if selected_size != self.current_font_size:
                self.current_font_size = selected_size
                
                # إعادة إعداد التنسيقات
                self.setup_styles()
                
                # حفظ حجم الخط الجديد في إعدادات UI
                ui_settings_manager.set_font_size('salaries', selected_size)
                
                # إجبار إعادة رسم الصفحة
                self.update()
                
                # تحديث القائمة المنسدلة
                self.update_font_size_combo()
                
        except Exception as e:
            logging.error(f"خطأ في تغيير حجم الخط: {e}")
    
    def update_font_size_combo(self):
        """تحديث القائمة المنسدلة لحجم الخط"""
        try:
            if hasattr(self, 'font_size_combo'):
                self.font_size_combo.blockSignals(True)  # منع إرسال الإشارات أثناء التحديث
                self.font_size_combo.setCurrentText(self.current_font_size)
                self.font_size_combo.blockSignals(False)  # إعادة تفعيل الإشارات
        except Exception as e:
            logging.error(f"خطأ في تحديث القائمة المنسدلة: {e}")
    
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
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
    
    def load_persons_list(self):
        """تحميل قائمة الأشخاص (معلمين وموظفين) للفلتر"""
        try:
            self.person_combo.clear()
            self.person_combo.addItem("الجميع", None)
            
            school_id = self.school_combo.currentData()
            staff_type = self.type_combo.currentText()
            if staff_type == "الكل": staff_type = None

            persons = []
            if not staff_type or staff_type == "معلم":
                query = "SELECT id, name FROM teachers"
                if school_id: query += f" WHERE school_id = {school_id}"
                teachers = db_manager.execute_query(query)
                if teachers: persons.extend([{'id': t['id'], 'name': t['name'], 'type': 'teacher'} for t in teachers])

            if not staff_type or staff_type == "موظف":
                query = "SELECT id, name FROM employees"
                if school_id: query += f" WHERE school_id = {school_id}"
                employees = db_manager.execute_query(query)
                if employees: persons.extend([{'id': e['id'], 'name': e['name'], 'type': 'employee'} for e in employees])

            persons.sort(key=lambda x: x['name'])
            for person in persons:
                type_ar = "معلم" if person['type'] == 'teacher' else "موظف"
                display_text = f"{person['name']} ({type_ar})"
                person_key = f"{person['type']}_{person['id']}"
                self.person_combo.addItem(display_text, person_key)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل قائمة الأشخاص: {e}")
    
    def load_salaries(self):
        """تحميل وتصفية بيانات الرواتب"""
        try:
            query = """
                SELECT s.id, s.paid_amount, s.payment_date, s.from_date, s.to_date, s.notes,
                       s.staff_type, s.staff_id,
                       COALESCE(t.name, e.name) as staff_name,
                       COALESCE(t.monthly_salary, e.monthly_salary) as base_salary,
                       sch.name_ar as school_name
                FROM salaries s
                LEFT JOIN schools sch ON s.school_id = sch.id
                LEFT JOIN teachers t ON s.staff_id = t.id AND s.staff_type = 'teacher'
                LEFT JOIN employees e ON s.staff_id = e.id AND s.staff_type = 'employee'
                WHERE 1=1
            """
            params = []

            school_id = self.school_combo.currentData()
            if school_id:
                query += " AND s.school_id = ?"
                params.append(school_id)

            staff_type = self.type_combo.currentText()
            if staff_type and staff_type != "الكل":
                type_en = 'teacher' if staff_type == 'معلم' else 'employee'
                query += " AND s.staff_type = ?"
                params.append(type_en)

            person_key = self.person_combo.currentData()
            if person_key:
                p_type, p_id = person_key.split('_')
                query += " AND s.staff_type = ? AND s.staff_id = ?"
                params.extend([p_type, int(p_id)])

            from_date = self.from_date_edit.date().toString("yyyy-MM-dd")
            to_date = self.to_date_edit.date().toString("yyyy-MM-dd")
            query += " AND s.payment_date BETWEEN ? AND ?"
            params.extend([from_date, to_date])

            search_text = self.search_input.text().strip()
            if search_text:
                query += " AND (t.name LIKE ? OR e.name LIKE ?)"
                params.extend([f"%{search_text}%", f"%{search_text}%"])

            query += " ORDER BY s.id DESC"
            
            self.current_salaries = db_manager.execute_query(query, tuple(params))
            self.populate_table()
            self.update_statistics()

        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الرواتب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات الرواتب:\n{e}")

    def apply_filters(self):
        """إعادة تحميل البيانات عند تغيير الفلاتر"""
        self.load_salaries()
    
    def populate_table(self):
        """ملء جدول الرواتب بالبيانات"""
        try:
            self.salaries_table.setRowCount(0)
            if not self.current_salaries: return

            for row_idx, salary in enumerate(self.current_salaries):
                self.salaries_table.insertRow(row_idx)
                
                type_ar = "معلم" if salary['staff_type'] == 'teacher' else "موظف"
                period = f"{salary['from_date']} إلى {salary['to_date']}"
                
                items = [
                    str(salary['id']),
                    salary['staff_name'] or "",
                    salary['school_name'] or "",
                    type_ar,
                    f"{salary['base_salary']:,.0f} د.ع" if salary['base_salary'] else "0 د.ع",
                    f"{salary['paid_amount']:,.0f} د.ع",
                    period,
                    salary['payment_date'],
                    salary['notes'] or ""
                ]
                
                for col_idx, item_text in enumerate(items):
                    item = QTableWidgetItem(item_text)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    if col_idx == 0:  # ID column
                        item = NumericTableWidgetItem(item_text)  # Use numeric item for ID
                    self.salaries_table.setItem(row_idx, col_idx, item)
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول الرواتب: {e}")
    
    def update_statistics(self):
        """تحديث الإحصائيات بناءً على البيانات المصفاة"""
        try:
            salaries = self.current_salaries
            total_paid = sum(s['paid_amount'] for s in salaries)
            count = len(salaries)
            avg_salary = total_paid / count if count > 0 else 0
            teachers_total = sum(s['paid_amount'] for s in salaries if s['staff_type'] == 'teacher')
            employees_total = sum(s['paid_amount'] for s in salaries if s['staff_type'] == 'employee')

            self.total_paid_value.setText(f"{total_paid:,.0f} د.ع")
            self.payments_count_value.setText(str(count))
            self.avg_salary_value.setText(f"{avg_salary:,.0f} د.ع")
            self.teachers_total_value.setText(f"{teachers_total:,.0f} د.ع")
            self.employees_total_value.setText(f"{employees_total:,.0f} د.ع")
            
            self.last_update_label.setText(f"آخر تحديث: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            logging.error(f"خطأ في تحديث الإحصائيات: {e}")
    
    def clear_filters(self):
        """مسح جميع الفلاتر"""
        try:
            self.search_input.clear()
            self.school_combo.setCurrentIndex(0)
            self.type_combo.setCurrentIndex(0)
            self.person_combo.setCurrentIndex(0)
            self.from_date_edit.setDate(QDate(2024, 1, 1))
            self.to_date_edit.setDate(QDate(2040, 12, 31))
            self.apply_filters()
        except Exception as e:
            logging.error(f"خطأ في مسح الفلاتر: {e}")
    
    def add_salary(self):
        """إضافة راتب جديد"""
        try:
            dialog = AddSalaryDialog(self)
            if dialog.exec_() == dialog.Accepted:
                self.refresh()
                log_user_action("إضافة راتب جديد", "نجح")
        except Exception as e:
            logging.error(f"خطأ في إضافة راتب: {e}")

    def edit_salary_by_id(self, salary_id):
        """تعديل الراتب المحدد"""
        try:
            dialog = EditSalaryDialog(salary_id, self)
            if dialog.exec_() == dialog.Accepted:
                self.refresh()
                log_user_action(f"تعديل الراتب {salary_id}", "نجح")
        except Exception as e:
            logging.error(f"خطأ في تعديل راتب: {e}")

    def delete_salary_by_id(self, salary_id):
        """حذف الراتب المحدد"""
        try:
            reply = QMessageBox.question(self, "تأكيد الحذف", "هل أنت متأكد؟", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                query = "DELETE FROM salaries WHERE id = ?"
                if db_manager.execute_update(query, (salary_id,)) > 0:
                    QMessageBox.information(self, "نجح", "تم الحذف بنجاح")
                    self.refresh()
                    log_user_action(f"حذف الراتب {salary_id}", "نجح")
        except Exception as e:
            logging.error(f"خطأ في حذف راتب: {e}")

    def refresh(self):
        """تحديث البيانات"""
        log_user_action("تحديث صفحة الرواتب")
        self.load_salaries()

    def on_table_double_click(self, index):
        """التعامل مع النقر المزدوج على صف في الجدول"""
        try:
            row = index.row()
            if row < 0: return
            salary_id = int(self.salaries_table.item(row, 0).text())
            self.edit_salary_by_id(salary_id)
        except Exception as e:
            logging.error(f"خطأ في النقر المزدوج: {e}")

    def show_context_menu(self, position):
        """عرض قائمة السياق للجدول"""
        try:
            if self.salaries_table.itemAt(position) is None: return
            row = self.salaries_table.currentRow()
            if row < 0: return
            salary_id = int(self.salaries_table.item(row, 0).text())
            
            menu = QMenu(self)
            edit_action = QAction("تعديل", self)
            edit_action.triggered.connect(lambda: self.edit_salary_by_id(salary_id))
            menu.addAction(edit_action)
            
            delete_action = QAction("حذف", self)
            delete_action.triggered.connect(lambda: self.delete_salary_by_id(salary_id))
            menu.addAction(delete_action)
            
            menu.exec_(self.salaries_table.mapToGlobal(position))
        except Exception as e:
            logging.error(f"خطأ في عرض قائمة السياق: {e}")
