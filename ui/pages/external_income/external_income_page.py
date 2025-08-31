#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة الواردات الخارجية
"""

import logging
import json
import os
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QMenu, QComboBox, QDateEdit, QAction, QDialog,
    QSpinBox, QTextEdit, QFormLayout, QGroupBox, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon, QFontDatabase

import config
from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation

from .add_income_dialog import AddIncomeDialog
from .edit_income_dialog import EditIncomeDialog

# استيراد وحدة أحجام الخطوط
from ...font_sizes import FontSizeManager
from ...ui_settings_manager import ui_settings_manager


class ExternalIncomePage(QWidget):
    """صفحة إدارة الواردات الخارجية"""

    # إشارات النافذة
    page_loaded = pyqtSignal()


    def __init__(self):
        super().__init__()
        self.current_incomes = []
        self.selected_school_id = None
        
        # الحصول على حجم الخط المحفوظ من إعدادات UI
        self.current_font_size = ui_settings_manager.get_font_size("external_income")
        
        self.setup_cairo_font()
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
                    school_id INTEGER NULL,
                    income_type TEXT NOT NULL,
                    description TEXT,
                    amount DECIMAL(10,2) NOT NULL,
                    category TEXT,
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
            # تقليل الهوامش والمسافات لتناسب الشاشات الصغيرة (1366x768)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(8)
            

            # شريط الأدوات والفلاتر
            self.create_toolbar(layout)

            # جدول الواردات
            self.create_income_table(layout)

            # إحصائيات مفصلة
            self.create_detailed_stats(layout)

            self.setLayout(layout)
            
            # تحديث القائمة المنسدلة لحجم الخط
            self.update_font_size_combo()
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة الواردات الخارجية: {e}")
            raise
    
    def create_header(self, layout):
        """إنشاء رأس الصفحة"""
        try:
            header_frame = QFrame()
            header_frame.setObjectName("headerFrame")
            
            header_layout = QHBoxLayout(header_frame)
            header_layout.setContentsMargins(10, 8, 10, 8)
            

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
            
            toolbar_layout = QVBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(8, 6, 8, 6)
            toolbar_layout.setSpacing(6)
            
            # الصف الأول - فلاتر أساسية
            filters_layout = QHBoxLayout()
            filters_layout.setSpacing(6)
            
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
            # افتراضيًا إلى أقل تاريخ ممكن لعرض جميع السجلات
            self.start_date.setDate(self.start_date.minimumDate())
            self.start_date.setCalendarPopup(True)
            filters_layout.addWidget(self.start_date)
            
            to_date_label = QLabel("إلى تاريخ:")
            to_date_label.setObjectName("filterLabel")
            filters_layout.addWidget(to_date_label)
            
            self.end_date = QDateEdit()
            self.end_date.setObjectName("filterDate")
            # افتراضيًا إلى أعلى تاريخ ممكن لعرض جميع السجلات
            self.end_date.setDate(self.end_date.maximumDate())
            self.end_date.setCalendarPopup(True)
            filters_layout.addWidget(self.end_date)
            
            filters_layout.addStretch() # Add stretch to push items to left
            toolbar_layout.addLayout(filters_layout)
            
            # الصف الثاني - البحث وأزرار العمليات
            actions_layout = QHBoxLayout()
            actions_layout.setSpacing(6)
            
            # مربع البحث
            search_label = QLabel("البحث:")
            search_label.setObjectName("filterLabel")
            actions_layout.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setObjectName("searchInput")
            self.search_input.setPlaceholderText("ابحث في العناوين والأوصاف والملاحظات...")
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
            
            actions_layout.addStretch() # Add stretch to push buttons to right
            
            # أزرار العمليات
            self.add_income_button = QPushButton("إضافة وارد")
            self.add_income_button.setObjectName("primaryButton")
            actions_layout.addWidget(self.add_income_button)
            
            self.clear_filters_button = QPushButton("مسح الفلاتر")
            self.clear_filters_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.clear_filters_button)
            
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("refreshButton")
            actions_layout.addWidget(self.refresh_button)
            
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
            self.income_table.setStyleSheet("QTableWidget::item { padding: 2px; }")  # تقليل الحشو لزيادة عدد الصفوف المرئية

            # إعداد أعمدة الجدول
            columns = ["المعرف", "عنوان الوارد", "الوصف", "المبلغ", "الفئة", "التاريخ", "المدرسة", "الملاحظات"]
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
            stats_layout.setContentsMargins(8, 6, 8, 6)
            
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
            
            # ربط تغيير حجم الخط
            self.font_size_combo.currentTextChanged.connect(self.change_font_size)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            self.school_combo.clear()
            self.school_combo.addItem("الجميع", None)
            self.school_combo.addItem("عام", "general")
            
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
                SELECT ei.id, ei.income_type, ei.amount, ei.description,
                       ei.income_date, ei.notes, s.name_ar as school_name,
                       ei.created_at, ei.category
                FROM external_income ei
                LEFT JOIN schools s ON ei.school_id = s.id
                WHERE 1=1
            """
            params = []
            
            # فلتر المدرسة
            selected_school_id = self.school_combo.currentData()
            if selected_school_id == "general":
                # إظهار الواردات العامة فقط (school_id IS NULL)
                query += " AND ei.school_id IS NULL"
            elif selected_school_id:
                # إظهار واردات مدرسة محددة
                query += " AND ei.school_id = ?"
                params.append(selected_school_id)
            
            # فلتر الفئة
            selected_category = self.category_combo.currentText()
            if selected_category and selected_category != "جميع الفئات":
                query += " AND ei.category = ?"
                params.append(selected_category)
            
            # فلتر التاريخ (يُطبق فقط إذا تم تغيير النطاق عن القيمة الافتراضية)
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            min_date = self.start_date.minimumDate().toPyDate()
            max_date = self.end_date.maximumDate().toPyDate()
            if not (start_date == min_date and end_date == max_date):
                query += " AND ei.income_date BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            
            # فلتر البحث
            search_text = self.search_input.text().strip()
            if search_text:
                query += " AND (ei.income_type LIKE ? OR ei.description LIKE ? OR ei.notes LIKE ?)"
                params.extend([f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"])
            
            # Default sort by newest entries first based on id
            query += " ORDER BY ei.id DESC"
            
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
                return
            
            # ملء الجدول
            for row_idx, income in enumerate(self.current_incomes):
                self.income_table.insertRow(row_idx)
                
                # البيانات الأساسية: id, عنوان الوارد, الوصف, المبلغ, الفئة, التاريخ, المدرسة, الملاحظات
                items = [
                    str(income['id']),
                    income['income_type'] or "",
                    income['description'] or "",
                    f"{income['amount']:,.2f} د.ع",
                    income['category'] or "",
                    income['income_date'] or "",
                    income['school_name'] or "عام",
                    (income['notes'] or "")[:50] + ("..." if len(income['notes'] or "") > 50 else "")
                ]
                
                for col_idx, item_text in enumerate(items):
                    item = QTableWidgetItem(item_text)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
                    # تنسيق خاص للمبلغ
                    if col_idx == 3:  # عمود المبلغ (تغير من 2 إلى 3 بعد إضافة عمود الوصف)
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    self.income_table.setItem(row_idx, col_idx, item)
                
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول الواردات: {e}")
    
    
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
            # إعادة تعيين لتغطية كامل النطاق الزمني
            self.start_date.setDate(self.start_date.minimumDate())
            self.end_date.setDate(self.end_date.maximumDate())
            self.search_input.clear()
            # الحفاظ على حجم الخط الحالي (لا نعيد تعيينه)
            self.font_size_combo.setCurrentText(self.current_font_size)
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
            from PyQt5.QtWidgets import QFileDialog
            import csv
            import os
            
            if not self.current_incomes:
                QMessageBox.warning(self, "تحذير", "لا توجد بيانات للتصدير")
                return
            
            # تحديد اسم الملف الافتراضي
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"External_Income_Report_{timestamp}.csv"
            
            # فتح نافذة حفظ الملف
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "حفظ تقرير الواردات الخارجية",
                default_filename,
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if not filename:
                return  # المستخدم ألغى العملية
            
            # التأكد من امتداد الملف
            if not filename.lower().endswith('.csv'):
                filename += '.csv'
            
            # إنشاء التقرير بتنسيق محسن للـ Excel
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                
                # كتابة معلومات التقرير
                writer.writerow([f"تقرير الواردات الخارجية - {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
                writer.writerow([f"إجمالي عدد الواردات: {len(self.current_incomes)}"])
                writer.writerow([f"إجمالي المبلغ: {sum(income['amount'] for income in self.current_incomes):,.2f} د.ع"])
                writer.writerow([])  # سطر فارغ
                
                # كتابة رأس الجدول
                headers = ["ID", "Income Type", "Description", "Amount (IQD)", "Category", "Date", "School", "Notes"]
                writer.writerow(headers)
                
                # كتابة البيانات
                for income in self.current_incomes:
                    row = [
                        income['id'],
                        income['income_type'] or '',
                        income['description'] or '',
                        f"{income['amount']:,.2f}",
                        income['category'] or '',
                        income['income_date'] or '',
                        income['school_name'] or 'General',
                        income['notes'] or ''
                    ]
                    writer.writerow(row)
                
                # إضافة إحصائيات في النهاية
                writer.writerow([])  # سطر فارغ
                writer.writerow(['Statistics:'])
                writer.writerow(['Total Records:', len(self.current_incomes)])
                writer.writerow(['Total Amount:', f"{sum(income['amount'] for income in self.current_incomes):,.2f} IQD"])
                writer.writerow(['Average Amount:', f"{sum(income['amount'] for income in self.current_incomes) / len(self.current_incomes):,.2f} IQD"])
                writer.writerow(['Max Amount:', f"{max(income['amount'] for income in self.current_incomes):,.2f} IQD"])
                writer.writerow(['Min Amount:', f"{min(income['amount'] for income in self.current_incomes):,.2f} IQD"])
            
            # إظهار رسالة نجح مع خيار فتح الملف
            reply = QMessageBox.question(
                self, "تم بنجاح", 
                f"تم تصدير التقرير بنجاح إلى:\n{filename}\n\nهل تريد فتح الملف الآن؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                try:
                    os.startfile(filename)  # فتح الملف بالبرنامج الافتراضي (Excel)
                except:
                    QMessageBox.information(self, "معلومات", f"تم حفظ الملف في:\n{filename}")
            
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
    
    def change_font_size(self):
        """تغيير حجم الخط في الصفحة"""
        try:
            selected_size = self.font_size_combo.currentText()
            
            if selected_size != self.current_font_size:
                self.current_font_size = selected_size
                
                # إعادة إعداد التنسيقات
                self.setup_styles()
                
                # حفظ حجم الخط الجديد في إعدادات UI
                success = ui_settings_manager.set_font_size("external_income", selected_size)
                
                log_user_action(f"تغيير حجم الخط إلى: {selected_size}")
                
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
    
    def setup_styles(self):
        """إعداد تنسيقات الصفحة"""
        try:
            # استخدام FontSizeManager لإنشاء CSS
            style = FontSizeManager.generate_css_styles(self.current_font_size)
            
            # تطبيق التنسيقات على الصفحة
            self.setStyleSheet(style)
            
            # إجبار إعادة رسم جميع المكونات
            self.update()
            if hasattr(self, 'income_table'):
                self.income_table.update()
            if hasattr(self, 'detailedStatsFrame'):
                self.detailedStatsFrame.update()
            
        except Exception as e:
            logging.error(f"خطأ في إعداد تنسيقات صفحة الواردات الخارجية: {e}")

    def setup_cairo_font(self):
        """إعداد خط Cairo"""
        try:
            font_path = os.path.join(config.FONTS_DIR, "Cairo-Medium.ttf")
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    if font_families:
                        cairo_font = QFont(font_families[0], 18)
                        self.setFont(cairo_font)
                        logging.info("تم تحميل خط Cairo بنجاح في صفحة الواردات الخارجية")
                        return
                        
            # استخدام خط بديل
            fallback_font = QFont("Arial", 18)
            self.setFont(fallback_font)
            logging.warning("تم استخدام خط Arial كبديل لخط Cairo في صفحة الواردات الخارجية")
            
        except Exception as e:
            logging.error(f"خطأ في إعداد خط Cairo في صفحة الواردات الخارجية: {e}")
            fallback_font = QFont("Arial", 18)
            self.setFont(fallback_font)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الستايل: {e}")
