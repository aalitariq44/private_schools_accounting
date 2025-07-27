#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة الواردات الخارجية
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

from .add_income_dialog import AddIncomeDialog
from .edit_income_dialog import EditIncomeDialog


class ExternalIncomePage(QWidget):
    """صفحة إدارة الواردات الخارجية"""

    # إشارات النافذة
    page_loaded = pyqtSignal()


    def __init__(self):
        super().__init__()
        self.current_incomes = []
        self.selected_school_id = None
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_schools()
        self.create_income_table_if_not_exists()
        
        log_user_action("فتح صفحة إدارة الواردات الخارجية")
    
    def create_income_table_if_not_exists(self):
        """إنشاء جدول الواردات الخارجية إذا لم يكن موجوداً"""
        try:
            create_table_query = """
                CREATE TABLE IF NOT EXISTS external_income (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    school_id INTEGER NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    category VARCHAR(100),
                    income_date DATE NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (school_id) REFERENCES schools(id)
                )
            """
            db_manager.execute_update(create_table_query)
            log_database_operation("إنشاء جدول الواردات الخارجية", "نجح")
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول الواردات الخارجية: {e}")
    
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

            # جدول الواردات
            self.create_income_table(layout)

            # إحصائيات مفصلة
            self.create_detailed_stats(layout)

            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة الواردات الخارجية: {e}")
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
            title_label = QLabel("إدارة الواردات الخارجية")
            title_label.setObjectName("pageTitle")
            title_label.setStyleSheet("color: black;")
            title_layout.addWidget(title_label)
            desc_label = QLabel("تسجيل وإدارة جميع الواردات الخارجية للمدرسة")
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
            self.displayed_count_label = QLabel("عدد الواردات المعروضة: 0")
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
            
            toolbar_layout = QHBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(15, 10, 15, 10)
            
            # فلاتر البحث
            filters_layout = QHBoxLayout()
            
            # فلتر المدرسة
            school_label = QLabel("المدرسة:")
            school_label.setObjectName("filterLabel")
            filters_layout.addWidget(school_label)
            
            self.school_combo = QComboBox()
            self.school_combo.setObjectName("filterCombo")
            filters_layout.addWidget(self.school_combo)
            
            # فلتر الفئة
            category_label = QLabel("الفئة:")
            category_label.setObjectName("filterLabel")
            filters_layout.addWidget(category_label)
            
            self.category_combo = QComboBox()
            self.category_combo.setObjectName("filterCombo")
            self.category_combo.addItems([
                "جميع الفئات", "الحانوت", "النقل", "الأنشطة", 
                "التبرعات", "إيجارات", "أخرى"
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
            
            # مربع البحث
            search_label = QLabel("البحث:")
            search_label.setObjectName("filterLabel")
            filters_layout.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setObjectName("searchInput")
            self.search_input.setPlaceholderText("ابحث في العناوين والملاحظات...")
            filters_layout.addWidget(self.search_input)
            
            toolbar_layout.addLayout(filters_layout)
            toolbar_layout.addStretch()
            
            # أزرار العمليات
            actions_layout = QHBoxLayout()
            
            self.add_income_button = QPushButton("إضافة وارد")
            self.add_income_button.setObjectName("primaryButton")
            actions_layout.addWidget(self.add_income_button)
            # زر مسح التصفيات
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
    
    def create_summary_stats(self, layout):
        """إنشاء الإحصائيات الموجزة"""
        try:
            stats_frame = QFrame()
            stats_frame.setObjectName("summaryStatsFrame")
            
            stats_layout = QHBoxLayout(stats_frame)
            stats_layout.setContentsMargins(20, 15, 20, 15)
            
            # إجمالي الواردات هذا الشهر
            self.monthly_total_label = QLabel("إجمالي هذا الشهر: 0 دينار")
            self.monthly_total_label.setObjectName("summaryStatLabel")
            stats_layout.addWidget(self.monthly_total_label)
            
            # إجمالي الواردات هذا العام
            self.yearly_total_label = QLabel("إجمالي هذا العام: 0 دينار")
            self.yearly_total_label.setObjectName("summaryStatLabel")
            stats_layout.addWidget(self.yearly_total_label)
            
            # عدد الواردات المعروضة
            self.displayed_count_label = QLabel("عدد الواردات المعروضة: 0")
            self.displayed_count_label.setObjectName("summaryStatLabel")
            stats_layout.addWidget(self.displayed_count_label)
            
            stats_layout.addStretch()
            
            # زر التحديث
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("refreshButton")
            stats_layout.addWidget(self.refresh_button)
            
            layout.addWidget(stats_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الإحصائيات الموجزة: {e}")
            raise
    
    def create_income_table(self, layout):
        """إنشاء جدول الواردات"""
        try:
            # إطار الجدول
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")

            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)  # إزالة الهوامش تمامًا

            # الجدول
            self.income_table = QTableWidget()
            self.income_table.setObjectName("dataTable")
            self.income_table.setStyleSheet("QTableWidget::item { padding: 0px; }")  # إزالة الحشو لإظهار أزرار الإجراءات بشكل صحيح

            # إعداد أعمدة الجدول
            columns = ["المعرف", "العنوان", "المبلغ", "الفئة", "التاريخ", "المدرسة", "الملاحظات", "الإجراءات"]
            self.income_table.setColumnCount(len(columns))
            self.income_table.setHorizontalHeaderLabels(columns)

            # إعداد خصائص الجدول
            self.income_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.income_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.income_table.setAlternatingRowColors(True)
            self.income_table.setSortingEnabled(True)

            # إعداد حجم الأعمدة
            header = self.income_table.horizontalHeader()
            header.setStretchLastSection(True)
            for i in range(len(columns) - 1):
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

            # ربط الأحداث
            self.income_table.cellDoubleClicked.connect(self.edit_income)
            self.income_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.income_table.customContextMenuRequested.connect(self.show_context_menu)

            table_layout.addWidget(self.income_table)
            layout.addWidget(table_frame)

        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول الواردات: {e}")
            raise
    
    def create_detailed_stats(self, layout):
        """إنشاء الإحصائيات المفصلة"""
        try:
            stats_frame = QFrame()
            stats_frame.setObjectName("detailedStatsFrame")
            
            stats_layout = QHBoxLayout(stats_frame)
            stats_layout.setContentsMargins(15, 10, 15, 10)
            
            # إحصائيات تفصيلية
            self.total_incomes_label = QLabel("إجمالي الواردات: 0")
            self.total_incomes_label.setObjectName("detailStatLabel")
            stats_layout.addWidget(self.total_incomes_label)
            
            self.average_income_label = QLabel("متوسط الوارد: 0 دينار")
            self.average_income_label.setObjectName("detailStatLabel")
            stats_layout.addWidget(self.average_income_label)
            
            self.max_income_label = QLabel("أكبر وارد: 0 دينار")
            self.max_income_label.setObjectName("detailStatLabel")
            stats_layout.addWidget(self.max_income_label)
            
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
            self.add_income_button.clicked.connect(self.add_income)
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
            
            # تحميل الواردات بعد تحميل المدارس
            self.refresh()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
    
    def load_incomes(self):
        """تحميل قائمة الواردات"""
        try:
            # بناء الاستعلام مع الفلاتر
            query = """
                SELECT ei.id, ei.title, ei.amount, ei.category,
                       ei.income_date, ei.notes, s.name_ar as school_name,
                       ei.created_at
                FROM external_income ei
                LEFT JOIN schools s ON ei.school_id = s.id
                WHERE 1=1
            """
            params = []
            
            # فلتر المدرسة
            selected_school_id = self.school_combo.currentData()
            if selected_school_id:
                query += " AND ei.school_id = ?"
                params.append(selected_school_id)
            
            # فلتر الفئة
            selected_category = self.category_combo.currentText()
            if selected_category and selected_category != "جميع الفئات":
                query += " AND ei.category = ?"
                params.append(selected_category)
            
            # فلتر التاريخ
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            query += " AND ei.income_date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
            
            # فلتر البحث
            search_text = self.search_input.text().strip()
            if search_text:
                query += " AND (ei.title LIKE ? OR ei.notes LIKE ?)"
                params.extend([f"%{search_text}%", f"%{search_text}%"])
            
            query += " ORDER BY ei.income_date DESC, ei.created_at DESC"
            
            # تنفيذ الاستعلام
            self.current_incomes = db_manager.execute_query(query, tuple(params))
            
            # ملء الجدول
            self.fill_income_table()
            
            # تحديث الإحصائيات
            self.update_stats()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الواردات: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل بيانات الواردات:\n{str(e)}")
    
    def fill_income_table(self):
        """ملء جدول الواردات بالبيانات"""
        try:
            # تنظيف الجدول
            self.income_table.setRowCount(0)
            
            if not self.current_incomes:
                self.displayed_count_label.setText("عدد الواردات المعروضة: 0")
                return
            
            # ملء الجدول
            for row_idx, income in enumerate(self.current_incomes):
                self.income_table.insertRow(row_idx)
                
                # البيانات الأساسية
                items = [
                    str(income['id']),
                    income['title'] or "",
                    f"{income['amount']:,.2f} د.ع",
                    income['category'] or "",
                    income['income_date'] or "",
                    income['school_name'] or "",
                    (income['notes'] or "")[:50] + ("..." if len(income['notes'] or "") > 50 else "")
                ]
                
                for col_idx, item_text in enumerate(items):
                    item = QTableWidgetItem(item_text)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
                    # تنسيق خاص للمبلغ
                    if col_idx == 2:  # عمود المبلغ
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    self.income_table.setItem(row_idx, col_idx, item)
                
                # أزرار الإجراءات
                actions_widget = self.create_actions_widget(income['id'])
                self.income_table.setCellWidget(row_idx, 7, actions_widget)
            
            # تحديث العداد
            self.displayed_count_label.setText(f"عدد الواردات المعروضة: {len(self.current_incomes)}")
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول الواردات: {e}")
    
    def create_actions_widget(self, income_id):
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
            edit_btn.clicked.connect(lambda: self.edit_income_by_id(income_id))
            layout.addWidget(edit_btn)

            # زر الحذف
            delete_btn = QPushButton("حذف")
            delete_btn.setObjectName("deleteButton")
            delete_btn.setFixedSize(80, 30)
            delete_btn.clicked.connect(lambda: self.delete_income(income_id))
            layout.addWidget(delete_btn)

            return widget

        except Exception as e:
            logging.error(f"خطأ في إنشاء ويدجت الإجراءات: {e}")
            return QWidget()
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        try:
            # إحصائيات الواردات المعروضة
            total_displayed = sum(income['amount'] for income in self.current_incomes)
            count_displayed = len(self.current_incomes)
            avg_displayed = total_displayed / count_displayed if count_displayed > 0 else 0
            max_displayed = max([income['amount'] for income in self.current_incomes], default=0)
            
            # إحصائيات الشهر الحالي
            current_month = datetime.now().month
            current_year = datetime.now().year
            monthly_query = """
                SELECT COALESCE(SUM(amount), 0) FROM external_income 
                WHERE strftime('%Y', income_date) = ? AND strftime('%m', income_date) = ?
            """
            monthly_result = db_manager.execute_query(monthly_query, (str(current_year), f"{current_month:02d}"))
            monthly_total = monthly_result[0][0] if monthly_result else 0
            
            # إحصائيات السنة الحالية
            yearly_query = """
                SELECT COALESCE(SUM(amount), 0) FROM external_income 
                WHERE strftime('%Y', income_date) = ?
            """
            yearly_result = db_manager.execute_query(yearly_query, (str(current_year),))
            yearly_total = yearly_result[0][0] if yearly_result else 0
            
            # تحديث التسميات
            self.monthly_total_label.setText(f"إجمالي هذا الشهر: {monthly_total:,.2f} د.ع")
            self.yearly_total_label.setText(f"إجمالي هذا العام: {yearly_total:,.2f} د.ع")
            self.total_incomes_label.setText(f"إجمالي الواردات المعروضة: {total_displayed:,.2f} د.ع")
            self.average_income_label.setText(f"متوسط الوارد: {avg_displayed:,.2f} د.ع")
            self.max_income_label.setText(f"أكبر وارد: {max_displayed:,.2f} د.ع")
            
            # تحديث وقت آخر تحديث
            self.last_update_label.setText(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث الإحصائيات: {e}")
    
    def apply_filters(self):
        """تطبيق الفلاتر وإعادة تحميل البيانات"""
        try:
            self.load_incomes()
            
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
            self.load_incomes()
        except Exception as e:
            logging.error(f"خطأ في مسح التصفيات: {e}")
    
    def refresh(self):
        """تحديث البيانات"""
        try:
            log_user_action("تحديث صفحة الواردات الخارجية")
            self.load_incomes()
            
        except Exception as e:
            logging.error(f"خطأ في تحديث صفحة الواردات الخارجية: {e}")
    
    def add_income(self):
        """إضافة وارد جديد"""
        try:
            dialog = AddIncomeDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh()
                log_user_action("إضافة وارد خارجي جديد", "نجح")
                
        except Exception as e:
            logging.error(f"خطأ في إضافة وارد: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة إضافة الوارد:\n{str(e)}")
    
    def edit_income(self, row):
        """تعديل بيانات وارد"""
        try:
            if row < 0 or row >= self.income_table.rowCount():
                return
            
            # الحصول على ID الوارد من الصف المحدد
            income_id_item = self.income_table.item(row, 0)
            if not income_id_item:
                return
            
            income_id = int(income_id_item.text())
            self.edit_income_by_id(income_id)
                
        except Exception as e:
            logging.error(f"خطأ في تعديل الوارد: {e}")
    
    def edit_income_by_id(self, income_id):
        """تعديل وارد بواسطة المعرف"""
        try:
            dialog = EditIncomeDialog(income_id, self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh()
                log_user_action(f"تعديل بيانات الوارد {income_id}", "نجح")
                
        except Exception as e:
            logging.error(f"خطأ في تعديل الوارد: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تعديل الوارد:\n{str(e)}")
    
    def delete_income(self, income_id):
        """حذف وارد"""
        try:
            # تأكيد الحذف
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                "هل أنت متأكد من حذف هذا الوارد؟\nسيتم حذف جميع البيانات المرتبطة به.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # حذف الوارد من قاعدة البيانات
                query = "DELETE FROM external_income WHERE id = ?"
                affected_rows = db_manager.execute_update(query, (income_id,))
                
                if affected_rows > 0:
                    QMessageBox.information(self, "نجح", "تم حذف الوارد بنجاح")
                    self.refresh()
                    log_user_action(f"حذف الوارد {income_id}", "نجح")
                else:
                    QMessageBox.warning(self, "خطأ", "لم يتم العثور على الوارد")
                    
        except Exception as e:
            logging.error(f"خطأ في حذف الوارد: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حذف الوارد:\n{str(e)}")
    
    def export_report(self):
        """تصدير تقرير الواردات"""
        try:
            from datetime import datetime
            import os
            
            # إنشاء مجلد التصدير إذا لم يكن موجوداً
            export_dir = "data/exports/reports"
            os.makedirs(export_dir, exist_ok=True)
            
            # اسم الملف
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{export_dir}/external_income_report_{timestamp}.csv"
            
            # إنشاء التقرير
            with open(filename, 'w', encoding='utf-8-sig') as f:
                # كتابة الرأس
                f.write("المعرف,العنوان,المبلغ,الفئة,التاريخ,المدرسة,الملاحظات\n")
                
                # كتابة البيانات
                for income in self.current_incomes:
                    f.write(f"{income['id']},{income['title']},{income['amount']},"
                           f"{income['category']},{income['income_date']},{income['school_name']},"
                           f"\"{income['notes'] or ''}\"\n")
            
            QMessageBox.information(self, "نجح", f"تم تصدير التقرير بنجاح:\n{filename}")
            log_user_action("تصدير تقرير الواردات الخارجية", "نجح")
            
        except Exception as e:
            logging.error(f"خطأ في تصدير التقرير: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تصدير التقرير:\n{str(e)}")
    
    def show_context_menu(self, position):
        """عرض قائمة السياق للجدول"""
        try:
            if self.income_table.itemAt(position) is None:
                return
            
            menu = QMenu(self)
            
            edit_action = QAction("تعديل", self)
            edit_action.triggered.connect(lambda: self.edit_income(self.income_table.currentRow()))
            menu.addAction(edit_action)
            
            delete_action = QAction("حذف", self)
            delete_action.triggered.connect(lambda: self.delete_income_by_row(self.income_table.currentRow()))
            menu.addAction(delete_action)
            
            menu.exec_(self.income_table.mapToGlobal(position))
            
        except Exception as e:
            logging.error(f"خطأ في عرض قائمة السياق: {e}")
    
    def delete_income_by_row(self, row):
        """حذف وارد بواسطة رقم الصف"""
        try:
            if row < 0 or row >= self.income_table.rowCount():
                return
            
            income_id_item = self.income_table.item(row, 0)
            if not income_id_item:
                return
            
            income_id = int(income_id_item.text())
            self.delete_income(income_id)
            
        except Exception as e:
            logging.error(f"خطأ في حذف الوارد: {e}")
    
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
                        stop:0 #28A745, stop:1 #20924C);
                    border-radius: 15px;
                    color: white;
                    margin-bottom: 15px;
                    padding: 20px;
                }
                
                #pageTitle {
                    font-size: 18px;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 8px;
                }
                
                #pageDesc {
                    font-size: 18px;
                    color: #E8F5E8;
                }
                
                /* شريط الأدوات */
                #toolbarFrame {
                    background-color: white;
                    border: 2px solid #E9ECEF;
                    border-radius: 12px;
                    margin-bottom: 15px;
                    padding: 15px;
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
                    border: 2px solid #28A745;
                    border-radius: 8px;
                    font-size: 18px;
                    background-color: white;
                    margin: 3px;
                    min-width: 200px;
                }
                
                /* الأزرار */
                #primaryButton {
                    background-color: #28A745;
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
                    background-color: #218838;
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
                    background-color: #E8F5E8;
                    color: #155724;
                }
                
                QHeaderView::section {
                    background-color: #28A745;
                    color: white;
                    padding: 12px 8px;
                    font-weight: bold;
                    font-size: 18px;
                    border: none;
                    border-right: 1px solid #20924C;
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
                    color: #28A745;
                    background-color: white;
                    padding: 10px 20px;
                    border-radius: 20px;
                    margin: 5px;
                    border: 2px solid #28A745;
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
