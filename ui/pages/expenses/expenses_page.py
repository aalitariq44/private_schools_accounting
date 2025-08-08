#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة المصروفات
"""

import logging
import json
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QMenu, QComboBox, QDateEdit, QAction, QDialog,
    QSpinBox, QTextEdit, QFormLayout, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation

from .add_expense_dialog import AddExpenseDialog
from .edit_expense_dialog import EditExpenseDialog


class ExpensesPage(QWidget):
    """صفحة إدارة المصروفات"""
    
    # إشارات النافذة
    page_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_expenses = []
        self.selected_school_id = None
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_schools()
        self.create_expenses_table_if_not_exists()
        
        log_user_action("فتح صفحة إدارة المصروفات")
    
    def create_expenses_table_if_not_exists(self):
        """إنشاء جدول المصروفات إذا لم يكن موجوداً"""
        try:
            create_table_query = """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    school_id INTEGER NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    category VARCHAR(100),
                    expense_date DATE NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (school_id) REFERENCES schools(id)
                )
            """
            db_manager.execute_update(create_table_query)
            log_database_operation("إنشاء جدول المصروفات", "نجح")
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول المصروفات: {e}")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            # رأس الصفحة
            self.create_header(layout)

            # شريط الأدوات والفلاتر
            self.create_toolbar(layout)

            # جدول المصروفات
            self.create_expenses_table(layout)

            # إحصائيات مفصلة
            self.create_detailed_stats(layout)

            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة المصروفات: {e}")
            raise
    
    def create_header(self, layout):
        """إنشاء رأس الصفحة"""
        try:
            header_frame = QFrame()
            header_frame.setObjectName("headerFrame")
            
            header_layout = QHBoxLayout(header_frame)
            header_layout.setContentsMargins(20, 15, 20, 15)
            
            # عنوان ووصف الصفحة (عمودي)
            title_layout = QVBoxLayout()
            title_label = QLabel("إدارة المصروفات")
            title_label.setObjectName("pageTitle")
            title_label.setStyleSheet("color: black;")
            title_layout.addWidget(title_label)
            desc_label = QLabel("تسجيل وإدارة جميع مصروفات المدرسة")
            desc_label.setObjectName("pageDesc")
            desc_label.setStyleSheet("color: black;")
            title_layout.addWidget(desc_label)

            # إحصائيات موجزة (أفقي)
            stats_layout = QHBoxLayout()
            stats_layout.setContentsMargins(0, 0, 0, 0)
            self.monthly_total_label = QLabel("إجمالي هذا الشهر: 0 دينار")
            self.monthly_total_label.setObjectName("summaryStatLabel")
            stats_layout.addWidget(self.monthly_total_label)
            self.yearly_total_label = QLabel("إجمالي هذا العام: 0 دينار")
            self.yearly_total_label.setObjectName("summaryStatLabel")
            stats_layout.addWidget(self.yearly_total_label)
            self.displayed_count_label = QLabel("عدد المصروفات المعروضة: 0")
            self.displayed_count_label.setObjectName("summaryStatLabel")
            stats_layout.addWidget(self.displayed_count_label)
            stats_layout.addStretch()
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("refreshButton")
            stats_layout.addWidget(self.refresh_button)

            # تخطيط رئيسي أفقي: يسار (العنوان والوصف) - يمين (الإحصائيات)
            main_header_layout = QHBoxLayout()
            main_header_layout.setContentsMargins(0, 0, 0, 0)
            main_header_layout.addLayout(title_layout)
            main_header_layout.addStretch()
            main_header_layout.addLayout(stats_layout)

            header_layout.addLayout(main_header_layout)
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء رأس الصفحة: {e}")
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات والفلاتر"""
        try:
            toolbar_frame = QFrame()
            toolbar_frame.setObjectName("toolbarFrame")
            
            toolbar_layout = QVBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(15, 10, 15, 10)
            toolbar_layout.setSpacing(10) # Added spacing between rows
            
            # الصف الأول - فلاتر أساسية
            filters_layout = QHBoxLayout()
            
            # فلتر المدرسة
            school_label = QLabel("المدرسة:")
            school_label.setObjectName("filterLabel")
            filters_layout.addWidget(school_label)
            
            self.school_combo = QComboBox()
            self.school_combo.setObjectName("filterCombo")
            filters_layout.addWidget(self.school_combo)
            
            # فلتر النوع
            category_label = QLabel("النوع:")
            category_label.setObjectName("filterLabel")
            filters_layout.addWidget(category_label)
            
            self.category_combo = QComboBox()
            self.category_combo.setObjectName("filterCombo")
            self.category_combo.addItems([
                "جميع الأنواع", "الرواتب", "المواد التعليمية", "الخدمات", 
                "الصيانة", "الكهرباء والماء", "النظافة", "المكتبية", 
                "النقل", "التأمين", "أخرى"
            ])
            filters_layout.addWidget(self.category_combo)
            
            
            # فلتر التاريخ
            date_label = QLabel("من تاريخ:")
            date_label.setObjectName("filterLabel")
            filters_layout.addWidget(date_label)
            
            self.start_date = QDateEdit()
            self.start_date.setObjectName("filterDate")
            self.start_date.setDate(QDate.currentDate().addMonths(-1))
            self.start_date.setCalendarPopup(True)
            filters_layout.addWidget(self.start_date)
            
            to_date_label = QLabel("إلى تاريخ:")
            to_date_label.setObjectName("filterLabel")
            filters_layout.addWidget(to_date_label)
            
            self.end_date = QDateEdit()
            self.end_date.setObjectName("filterDate")
            self.end_date.setDate(QDate.currentDate())
            self.end_date.setCalendarPopup(True)
            filters_layout.addWidget(self.end_date)
            
            filters_layout.addStretch() # Add stretch to push items to left
            toolbar_layout.addLayout(filters_layout)
            
            # الصف الثاني - البحث وأزرار العمليات
            actions_layout = QHBoxLayout()
            
            # مربع البحث
            search_label = QLabel("البحث:")
            search_label.setObjectName("filterLabel")
            actions_layout.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setObjectName("searchInput")
            self.search_input.setPlaceholderText("ابحث في العناوين والملاحظات...")
            actions_layout.addWidget(self.search_input)
            
            actions_layout.addStretch() # Add stretch to push buttons to right
            
            # أزرار العمليات
            self.add_expense_button = QPushButton("إضافة مصروف")
            self.add_expense_button.setObjectName("primaryButton")
            actions_layout.addWidget(self.add_expense_button)
            
            self.clear_filters_button = QPushButton("مسح الفلاتر")
            self.clear_filters_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.clear_filters_button)
            
            self.export_button = QPushButton("تصدير التقرير")
            self.export_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.export_button)
            
            toolbar_layout.addLayout(actions_layout)
            
            layout.addWidget(toolbar_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
            raise
    
    
    def create_expenses_table(self, layout):
        """إنشاء جدول المصروفات"""
        try:
            # إطار الجدول
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")

            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)  # إزالة الهوامش تمامًا

            # الجدول
            self.expenses_table = QTableWidget()
            self.expenses_table.setObjectName("dataTable")
            self.expenses_table.setStyleSheet("QTableWidget::item { padding: 0px; }")  # إزالة الحشو لإظهار أزرار الإجراءات بشكل صحيح

            # إعداد أعمدة الجدول
            columns = ["المعرف", "النوع", "المبلغ", "الوصف", "التاريخ", "المدرسة", "الملاحظات", "الإجراءات"]
            self.expenses_table.setColumnCount(len(columns))
            self.expenses_table.setHorizontalHeaderLabels(columns)

            # إعداد خصائص الجدول
            self.expenses_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.expenses_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.expenses_table.setAlternatingRowColors(True)
            self.expenses_table.setSortingEnabled(True)

            # إعداد حجم الأعمدة
            header = self.expenses_table.horizontalHeader()
            header.setStretchLastSection(True)
            for i in range(len(columns) - 1):
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

            # ربط الأحداث
            self.expenses_table.cellDoubleClicked.connect(self.edit_expense)
            self.expenses_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.expenses_table.customContextMenuRequested.connect(self.show_context_menu)

            table_layout.addWidget(self.expenses_table)
            layout.addWidget(table_frame)

        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول المصروفات: {e}")
            raise
    
    def create_detailed_stats(self, layout):
        """إنشاء الإحصائيات المفصلة"""
        try:
            stats_frame = QFrame()
            stats_frame.setObjectName("detailedStatsFrame")
            
            stats_layout = QHBoxLayout(stats_frame)
            stats_layout.setContentsMargins(15, 10, 15, 10)
            
            # إحصائيات تفصيلية
            self.total_expenses_label = QLabel("إجمالي المصروفات: 0")
            self.total_expenses_label.setObjectName("detailStatLabel")
            stats_layout.addWidget(self.total_expenses_label)
            
            self.average_expense_label = QLabel("متوسط المصروف: 0 دينار")
            self.average_expense_label.setObjectName("detailStatLabel")
            stats_layout.addWidget(self.average_expense_label)
            
            self.max_expense_label = QLabel("أكبر مصروف: 0 دينار")
            self.max_expense_label.setObjectName("detailStatLabel")
            stats_layout.addWidget(self.max_expense_label)
            
            stats_layout.addStretch()
            
            # معلومات آخر تحديث
            self.last_update_label = QLabel("آخر تحديث: --")
            self.last_update_label.setObjectName("detailStatLabel")
            stats_layout.addWidget(self.last_update_label)
            
            layout.addWidget(stats_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الإحصائيات المفصلة: {e}")
            raise
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            # ربط أزرار العمليات
            self.add_expense_button.clicked.connect(self.add_expense)
            self.refresh_button.clicked.connect(self.refresh)
            self.export_button.clicked.connect(self.export_report)
            
            # ربط زر مسح التصفيات
            self.clear_filters_button.clicked.connect(self.clear_filters)
            # ربط الفلاتر
            self.school_combo.currentTextChanged.connect(self.apply_filters)
            self.category_combo.currentTextChanged.connect(self.apply_filters)
            self.start_date.dateChanged.connect(self.apply_filters)
            self.end_date.dateChanged.connect(self.apply_filters)
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
            else:
                self.school_combo.addItem("لا توجد مدارس", None)
    
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
    
    def load_expenses(self):
        """تحميل قائمة المصروفات"""
        try:
            # بناء الاستعلام مع الفلاتر
            query = """
                SELECT e.id, e.expense_type, e.amount, e.description, e.expense_date,
                       e.notes, s.name_ar as school_name, e.created_at
                FROM expenses e
                LEFT JOIN schools s ON e.school_id = s.id
                WHERE 1=1
            """
            params = []
            
            # فلتر المدرسة
            selected_school_id = self.school_combo.currentData()
            if selected_school_id:
                query += " AND e.school_id = ?"
                params.append(selected_school_id)
            
            # فلتر النوع
            selected_category = self.category_combo.currentText()
            if selected_category and selected_category != "جميع الأنواع":
                query += " AND e.expense_type = ?"
                params.append(selected_category)
            
            
            # فلتر التاريخ
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            query += " AND e.expense_date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
            
            # فلتر البحث
            search_text = self.search_input.text().strip()
            if search_text:
                query += " AND (e.expense_type LIKE ? OR e.notes LIKE ?)"
                params.extend([f"%{search_text}%", f"%{search_text}%"])
            
            query += " ORDER BY e.expense_date DESC, e.created_at DESC"
            
            # تنفيذ الاستعلام
            self.current_expenses = db_manager.execute_query(query, tuple(params))
            
            # ملء الجدول
            self.fill_expenses_table()
            
            # تحديث الإحصائيات
            self.update_stats()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المصروفات: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل بيانات المصروفات:\n{str(e)}")
    
    def fill_expenses_table(self):
        """ملء جدول المصروفات بالبيانات"""
        try:
            # تنظيف الجدول
            self.expenses_table.setRowCount(0)
            
            if not self.current_expenses:
                self.displayed_count_label.setText("عدد المصروفات المعروضة: 0")
                return
            
            # ملء الجدول
            for row_idx, expense in enumerate(self.current_expenses):
                self.expenses_table.insertRow(row_idx)
                
                # البيانات الأساسية
                items = [
                    str(expense['id']),
                    expense['expense_type'] or "",
                    f"{expense['amount']:,.2f} د.ع",
                    expense['description'] or "",
                    expense['expense_date'] or "",
                    expense['school_name'] or "",
                    (expense['notes'] or "")[:50] + ("..." if len(expense['notes'] or "") > 50 else "")
                ]
                
                for col_idx, item_text in enumerate(items):
                    item = QTableWidgetItem(item_text)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
                    # تنسيق خاص للمبلغ
                    if col_idx == 2:  # عمود المبلغ
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    self.expenses_table.setItem(row_idx, col_idx, item)
                
                # أزرار الإجراءات
                actions_widget = self.create_actions_widget(expense['id'])
                self.expenses_table.setCellWidget(row_idx, 7, actions_widget)
            
            # تحديث العداد
            self.displayed_count_label.setText(f"عدد المصروفات المعروضة: {len(self.current_expenses)}")
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول المصروفات: {e}")
    
    def create_actions_widget(self, expense_id):
        """إنشاء ويدجت الإجراءات لكل صف"""
        try:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(5, 2, 5, 2)
            layout.setSpacing(5)

            # زر التعديل
            edit_btn = QPushButton("تعديل")
            edit_btn.setObjectName("editButton")
            edit_btn.setFixedSize(80, 30)
            edit_btn.clicked.connect(lambda: self.edit_expense_by_id(expense_id))
            layout.addWidget(edit_btn)

            # زر الحذف
            delete_btn = QPushButton("حذف")
            delete_btn.setObjectName("deleteButton")
            delete_btn.setFixedSize(80, 30)
            delete_btn.clicked.connect(lambda: self.delete_expense(expense_id))
            layout.addWidget(delete_btn)

            return widget

        except Exception as e:
            logging.error(f"خطأ في إنشاء ويدجت الإجراءات: {e}")
            return QWidget()
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        try:
            # إحصائيات المصروفات المعروضة
            total_displayed = sum(expense['amount'] for expense in self.current_expenses)
            count_displayed = len(self.current_expenses)
            avg_displayed = total_displayed / count_displayed if count_displayed > 0 else 0
            max_displayed = max([expense['amount'] for expense in self.current_expenses], default=0)
            
            # إحصائيات الشهر الحالي
            current_month = datetime.now().month
            current_year = datetime.now().year
            monthly_query = """
                SELECT COALESCE(SUM(amount), 0) FROM expenses 
                WHERE strftime('%Y', expense_date) = ? AND strftime('%m', expense_date) = ?
            """
            monthly_result = db_manager.execute_query(monthly_query, (str(current_year), f"{current_month:02d}"))
            monthly_total = monthly_result[0][0] if monthly_result else 0
            
            # إحصائيات السنة الحالية
            yearly_query = """
                SELECT COALESCE(SUM(amount), 0) FROM expenses 
                WHERE strftime('%Y', expense_date) = ?
            """
            yearly_result = db_manager.execute_query(yearly_query, (str(current_year),))
            yearly_total = yearly_result[0][0] if yearly_result else 0
            
            # تحديث التسميات
            self.monthly_total_label.setText(f"إجمالي هذا الشهر: {monthly_total:,.2f} د.ع")
            self.yearly_total_label.setText(f"إجمالي هذا العام: {yearly_total:,.2f} د.ع")
            self.total_expenses_label.setText(f"إجمالي المصروفات المعروضة: {total_displayed:,.2f} د.ع")
            self.average_expense_label.setText(f"متوسط المصروف: {avg_displayed:,.2f} د.ع")
            self.max_expense_label.setText(f"أكبر مصروف: {max_displayed:,.2f} د.ع")
            
            # تحديث وقت آخر تحديث
            self.last_update_label.setText(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث الإحصائيات: {e}")
    
    def apply_filters(self):
        """تطبيق الفلاتر وإعادة تحميل البيانات"""
        try:
            self.load_expenses()
            
        except Exception as e:
            logging.error(f"خطأ في تطبيق الفلاتر: {e}")
    
    def clear_filters(self):
        """مسح جميع التصفيات والعودة للوضع الافتراضي"""
        try:
            # إعادة تعيين الفلاتر للقيم الافتراضية
            self.school_combo.setCurrentIndex(0)
            self.category_combo.setCurrentIndex(0)
            self.start_date.setDate(QDate.currentDate().addMonths(-1))
            self.end_date.setDate(QDate.currentDate())
            self.search_input.clear()
            # إعادة تحميل البيانات
            self.load_expenses()
        except Exception as e:
            logging.error(f"خطأ في مسح التصفيات: {e}")
    
    def refresh(self):
        """تحديث البيانات"""
        try:
            log_user_action("تحديث صفحة المصروفات")
            self.load_expenses()
            
        except Exception as e:
            logging.error(f"خطأ في تحديث صفحة المصروفات: {e}")
    
    def add_expense(self):
        """إضافة مصروف جديد"""
        try:
            dialog = AddExpenseDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh()
                log_user_action("إضافة مصروف جديد", "نجح")
                
        except Exception as e:
            logging.error(f"خطأ في إضافة مصروف: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة إضافة المصروف:\n{str(e)}")
    
    def edit_expense(self, row):
        """تعديل بيانات مصروف"""
        try:
            if row < 0 or row >= self.expenses_table.rowCount():
                return
            
            # الحصول على ID المصروف من الصف المحدد
            expense_id_item = self.expenses_table.item(row, 0)
            if not expense_id_item:
                return
            
            expense_id = int(expense_id_item.text())
            self.edit_expense_by_id(expense_id)
                
        except Exception as e:
            logging.error(f"خطأ في تعديل المصروف: {e}")
    
    def edit_expense_by_id(self, expense_id):
        """تعديل مصروف بواسطة المعرف"""
        try:
            dialog = EditExpenseDialog(expense_id, self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh()
                log_user_action(f"تعديل بيانات المصروف {expense_id}", "نجح")
                
        except Exception as e:
            logging.error(f"خطأ في تعديل المصروف: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تعديل المصروف:\n{str(e)}")
    
    def delete_expense(self, expense_id):
        """حذف مصروف"""
        try:
            # تأكيد الحذف
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                "هل أنت متأكد من حذف هذا المصروف؟\nسيتم حذف جميع البيانات المرتبطة به.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # حذف المصروف من قاعدة البيانات
                query = "DELETE FROM expenses WHERE id = ?"
                affected_rows = db_manager.execute_update(query, (expense_id,))
                
                if affected_rows > 0:
                    QMessageBox.information(self, "نجح", "تم حذف المصروف بنجاح")
                    self.refresh()
                    log_user_action(f"حذف المصروف {expense_id}", "نجح")
                else:
                    QMessageBox.warning(self, "خطأ", "لم يتم العثور على المصروف")
                    
        except Exception as e:
            logging.error(f"خطأ في حذف المصروف: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حذف المصروف:\n{str(e)}")
    
    def export_report(self):
        """تصدير تقرير المصروفات"""
        try:
            from datetime import datetime
            import os
            
            # إنشاء مجلد التصدير إذا لم يكن موجوداً
            export_dir = "data/exports/reports"
            os.makedirs(export_dir, exist_ok=True)
            
            # اسم الملف
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{export_dir}/expenses_report_{timestamp}.csv"
            
            # إنشاء التقرير
            with open(filename, 'w', encoding='utf-8-sig') as f:
                # كتابة الرأس
                f.write("المعرف,النوع,المبلغ,الوصف,التاريخ,المدرسة,الملاحظات\n")
                
                # كتابة البيانات
                for expense in self.current_expenses:
                    f.write(f"{expense['id']},{expense['expense_type']},{expense['amount']},{expense['description']},"
                           f"{expense['expense_date']},{expense['school_name']},\"{expense['notes'] or ''}\"\n")
            
            QMessageBox.information(self, "نجح", f"تم تصدير التقرير بنجاح:\n{filename}")
            log_user_action("تصدير تقرير المصروفات", "نجح")
            
        except Exception as e:
            logging.error(f"خطأ في تصدير التقرير: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تصدير التقرير:\n{str(e)}")
    
    def show_context_menu(self, position):
        """عرض قائمة السياق للجدول"""
        try:
            if self.expenses_table.itemAt(position) is None:
                return
            
            menu = QMenu(self)
            
            edit_action = QAction("تعديل", self)
            edit_action.triggered.connect(lambda: self.edit_expense(self.expenses_table.currentRow()))
            menu.addAction(edit_action)
            
            delete_action = QAction("حذف", self)
            delete_action.triggered.connect(lambda: self.delete_expense_by_row(self.expenses_table.currentRow()))
            menu.addAction(delete_action)
            
            menu.exec_(self.expenses_table.mapToGlobal(position))
            
        except Exception as e:
            logging.error(f"خطأ في عرض قائمة السياق: {e}")
    
    def delete_expense_by_row(self, row):
        """حذف مصروف بواسطة رقم الصف"""
        try:
            if row < 0 or row >= self.expenses_table.rowCount():
                return
            
            expense_id_item = self.expenses_table.item(row, 0)
            if not expense_id_item:
                return
            
            expense_id = int(expense_id_item.text())
            self.delete_expense(expense_id)
            
        except Exception as e:
            logging.error(f"خطأ في حذف المصروف: {e}")
    
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
                        stop:0 #DC3545, stop:1 #C82333);
                    border-radius: 15px;
                    color: white;
                    margin-bottom: 15px;
                    padding: 10px;
                }
                
                #pageTitle {
                    font-size: 18px;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 8px;
                }
                
                #pageDesc {
                    font-size: 18px;
                    color: #F8E5E5;
                }
                
                /* شريط الأدوات */
                #toolbarFrame {
                    background-color: white;
                    border: 2px solid #E9ECEF;
                    border-radius: 12px;
                    margin-bottom: 15px;
                    padding: 10px;
                }
                
                #filterLabel {
                    font-weight: bold;
                    color: #2C3E50;
                    margin-right: 8px;
                    font-size: 18px;
                }
                
                #filterCombo, #filterDate {
                    padding: 8px 12px;
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    background-color: white;
                    min-width: 120px;
                    font-size: 18px;
                    margin: 3px;
                }
                
                #searchInput {
                    padding: 8px 15px;
                    border: 2px solid #DC3545;
                    border-radius: 8px;
                    font-size: 18px;
                    background-color: white;
                    margin: 3px;
                    min-width: 250px; /* Increased min-width for search input */
                }
                
                /* الأزرار */
                #primaryButton {
                    background-color: #DC3545;
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    border-radius: 8px;
                    font-weight: bold;
                    min-width: 140px;
                    font-size: 18px;
                    margin: 3px;
                }
                
                #primaryButton:hover {
                    background-color: #C82333;
                }
                
                #secondaryButton {
                    background-color: #6C757D;
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    border-radius: 8px;
                    font-weight: bold;
                    min-width: 140px;
                    font-size: 18px;
                    margin: 3px;
                }
                
                #refreshButton {
                    background-color: #FFC107;
                    color: #212529;
                    border: none;
                    padding: 12px 25px;
                    border-radius: 8px;
                    font-weight: bold;
                    min-width: 100px;
                    font-size: 18px;
                    margin: 3px;
                }
                
                #editButton, #deleteButton {
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 18px;
                    font-weight: bold;
                    border: none;
                    margin: 1px;
                }
                
                #editButton {
                    background-color: #17A2B8;
                    color: white;
                }
                
                #deleteButton {
                    background-color: #DC3545;
                    color: white;
                }
                
                /* الجدول */
                QTableWidget {
                    background-color: white;
                    border: 2px solid #E9ECEF;
                    border-radius: 12px;
                    gridline-color: #E9ECEF;
                    font-size: 18px;
                    margin: 10px 0px;
                }
                
                QTableWidget::item {
                    padding: 12px 8px;
                    border-bottom: 1px solid #E9ECEF;
                    font-size: 18px;
                }
                
                QTableWidget::item:selected {
                    background-color: #F8E5E5;
                    color: #721C24;
                }
                
                QHeaderView::section {
                    background-color: #DC3545;
                    color: white;
                    padding: 12px 8px;
                    font-weight: bold;
                    font-size: 18px;
                    border: none;
                    border-right: 1px solid #C82333;
                }
                
                /* الإحصائيات */
                #summaryStatsFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #F8F9FA, stop:1 #E9ECEF);
                    border: 2px solid #DEE2E6;
                    border-radius: 12px;
                    margin-bottom: 15px;
                    padding: 15px;
                }
                
                #summaryStatLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #DC3545;
                    background-color: white;
                    padding: 10px 20px;
                    border-radius: 20px;
                    margin: 5px;
                    border: 2px solid #DC3545;
                }
                
                #detailedStatsFrame {
                    background-color: white;
                    border: 2px solid #E9ECEF;
                    border-radius: 12px;
                    margin-top: 15px;
                    padding: 15px;
                }
                
                #detailStatLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #495057;
                    margin: 5px;
                }
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الستايل: {e}")
