#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة الأقساط
"""

import logging
import json
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QMenu, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QProgressBar, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation




class InstallmentsPage(QWidget):
    """صفحة إدارة الأقساط"""
    
    # إشارات النافذة
    page_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_installments = []
        self.selected_school_id = None
        self.selected_student_id = None
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_initial_data()
        
        log_user_action("فتح صفحة إدارة الأقساط")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            # العنوان الرئيسي
            self.create_page_header(layout)
            
            # شريط الأدوات والفلاتر
            self.create_toolbar(layout)
            
            # جدول الأقساط
            self.create_installments_table(layout)
            
            # إحصائيات وملخص مالي
            self.create_financial_summary(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة الأقساط: {e}")
            raise
    
    def create_page_header(self, layout):
        """إنشاء رأس الصفحة"""
        try:
            header_frame = QFrame()
            header_frame.setObjectName("headerFrame")
            
            header_layout = QHBoxLayout(header_frame)
            header_layout.setContentsMargins(20, 15, 20, 15)
            
            # العنوان والوصف
            text_layout = QVBoxLayout()
            
            title_label = QLabel("إدارة الأقساط")
            title_label.setObjectName("pageTitle")
            title_label.setStyleSheet("color: black;")
            text_layout.addWidget(title_label)
            
            desc_label = QLabel("إدارة أقساط الطلاب والمدفوعات والمتابعة المالية")
            desc_label.setObjectName("pageDesc")
            desc_label.setStyleSheet("color: black;")
            text_layout.addWidget(desc_label)
            
            header_layout.addLayout(text_layout)
            header_layout.addStretch()
            
            # إحصائيات سريعة في الرأس
            stats_layout = QHBoxLayout()
            
            self.total_installments_label = QLabel("إجمالي الأقساط: 0")
            self.total_installments_label.setObjectName("quickStat")
            stats_layout.addWidget(self.total_installments_label)
            
            # ... سابقاً كان يعرض المدفوع والمستحق وتمت إزالته
            
            header_layout.addLayout(stats_layout)
            
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
            toolbar_layout.setSpacing(10)
            
            # الصف الأول - فلاتر أساسية
            filters_layout = QHBoxLayout()
            
            # اختيار المدرسة
            school_label = QLabel("المدرسة:")
            school_label.setObjectName("filterLabel")
            filters_layout.addWidget(school_label)
            
            self.school_combo = QComboBox()
            self.school_combo.setObjectName("filterCombo")
            self.school_combo.setMinimumWidth(200)
            filters_layout.addWidget(self.school_combo)
            
            # اختيار الطالب
            student_label = QLabel("الطالب:")
            student_label.setObjectName("filterLabel")
            filters_layout.addWidget(student_label)
            
            self.student_combo = QComboBox()
            self.student_combo.setObjectName("filterCombo")
            self.student_combo.setMinimumWidth(200)
            filters_layout.addWidget(self.student_combo)
            
            
            filters_layout.addStretch()
            
            toolbar_layout.addLayout(filters_layout)
            
            # الصف الثاني - فلاتر التاريخ والعمليات
            actions_layout = QHBoxLayout()
            
            # فلتر تاريخ الاستحقاق
            due_date_label = QLabel("تاريخ الاستحقاق من:")
            due_date_label.setObjectName("filterLabel")
            actions_layout.addWidget(due_date_label)
            
            self.due_date_from = QDateEdit()
            self.due_date_from.setObjectName("dateInput")
            self.due_date_from.setDate(QDate.currentDate().addDays(-30))
            self.due_date_from.setCalendarPopup(True)
            actions_layout.addWidget(self.due_date_from)
            
            to_label = QLabel("إلى:")
            to_label.setObjectName("filterLabel")
            actions_layout.addWidget(to_label)
            
            self.due_date_to = QDateEdit()
            self.due_date_to.setObjectName("dateInput")
            self.due_date_to.setDate(QDate.currentDate().addDays(30))
            self.due_date_to.setCalendarPopup(True)
            actions_layout.addWidget(self.due_date_to)
            
            actions_layout.addStretch()
            
            # أزرار العمليات
            self.generate_report_button = QPushButton("تقرير مالي")
            self.generate_report_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.generate_report_button)
            
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("refreshButton")
            actions_layout.addWidget(self.refresh_button)
            
            toolbar_layout.addLayout(actions_layout)
            
            layout.addWidget(toolbar_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
            raise
    
    def create_installments_table(self, layout):
        """إنشاء جدول الأقساط"""
        try:
            # إطار الجدول
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")
            
            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)
            
            # إنشاء الجدول
            self.installments_table = QTableWidget()
            self.installments_table.setObjectName("dataTable")
            
            # إعداد الأعمدة بناءً على المخطط الجديد
            columns = [
                "المعرف", "الطالب", "المدرسة", "المبلغ",
                "تاريخ الدفع", "وقت الدفع", "ملاحظات"
            ]
            
            self.installments_table.setColumnCount(len(columns))
            self.installments_table.setHorizontalHeaderLabels(columns)
            
            # إعداد خصائص الجدول
            self.installments_table.setAlternatingRowColors(True)
            self.installments_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.installments_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.installments_table.setSortingEnabled(True)
            self.installments_table.setShowGrid(False)
            
            # تخصيص عرض الأعمدة
            header = self.installments_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.setDefaultSectionSize(120)
            header.resizeSection(0, 80)   # المعرف
            header.resizeSection(1, 160)  # الطالب
            header.resizeSection(2, 130)  # المدرسة
            header.resizeSection(3, 120)  # المبلغ
            header.resizeSection(4, 110)  # تاريخ الدفع
            header.resizeSection(5, 110)  # وقت الدفع
            header.resizeSection(6, 200)  # ملاحظات
            
            # إخفاء العمود الأول (المعرف) 
            self.installments_table.setColumnHidden(0, True)
            
            # ربط الأحداث
            
            self.installments_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.installments_table.customContextMenuRequested.connect(self.show_context_menu)
            
            table_layout.addWidget(self.installments_table)
            layout.addWidget(table_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول الأقساط: {e}")
            raise
    
    def create_financial_summary(self, layout):
        """إنشاء ملخص مالي"""
        try:
            summary_frame = QFrame()
            summary_frame.setObjectName("summaryFrame")
            
            summary_layout = QHBoxLayout(summary_frame)
            summary_layout.setContentsMargins(15, 10, 15, 10)
            
            # ملخص الأرقام
            numbers_layout = QVBoxLayout()
            
            summary_title = QLabel("الملخص المالي")
            summary_title.setObjectName("summaryTitle")
            numbers_layout.addWidget(summary_title)
            
            # لوحة الملخص: إجمالي الأقساط وعددها
            numbers_grid = QHBoxLayout()
            total_layout = QVBoxLayout()
            self.total_amount_label = QLabel("مجموع الأقساط:")
            self.total_amount_label.setObjectName("summaryLabel")
            total_layout.addWidget(self.total_amount_label)
            self.total_amount_value = QLabel("0 د.ع")
            self.total_amount_value.setObjectName("summaryValue")
            total_layout.addWidget(self.total_amount_value)
            numbers_grid.addLayout(total_layout)
            numbers_layout.addLayout(numbers_grid)
            summary_layout.addLayout(numbers_layout)
            # عدد الأقساط المعروضة
            self.displayed_count_label = QLabel("عدد الأقساط المعروضة: 0")
            self.displayed_count_label.setObjectName("statLabel")
            summary_layout.addWidget(self.displayed_count_label)
            
            # ... تمت إزالة شريط التقدم والإحصائيات المتفرعة
            
            # ... تمت إزالة إحصائيات الحالة بسبب حذف الأعمدة
            
            layout.addWidget(summary_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الملخص المالي: {e}")
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            # ربط أزرار العمليات
            self.generate_report_button.clicked.connect(self.generate_report)
            self.refresh_button.clicked.connect(self.refresh)
            
            # ربط الفلاتر
            # ربط فلتر المدرسة والطالب باستخدام currentIndexChanged لالتقاط التغيير بشكل موثوق
            self.school_combo.currentIndexChanged.connect(self.on_school_changed)
            self.student_combo.currentIndexChanged.connect(self.apply_filters)
            self.due_date_from.dateChanged.connect(self.apply_filters)
            self.due_date_to.dateChanged.connect(self.apply_filters)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def load_initial_data(self):
        """تحميل البيانات الأولية"""
        try:
            self.load_schools()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل البيانات الأولية: {e}")
    
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
                    self.school_combo.addItem(school[1], school[0])
            
            # تحميل الطلاب والأقساط بعد تحميل المدارس
            self.load_students()
            self.refresh()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
    
    def load_students(self):
        """تحميل قائمة الطلاب حسب المدرسة المحددة"""
        try:
            self.student_combo.clear()
            self.student_combo.addItem("جميع الطلاب", None)
            
            selected_school_id = self.school_combo.currentData()
            
            # بناء الاستعلام
            if selected_school_id:
                query = """
                    SELECT id, name as full_name
                    FROM students 
                    WHERE school_id = ? AND status = 'نشط'
                    ORDER BY name
                """
                params = [selected_school_id]
            else:
                query = """
                    SELECT id, name as full_name
                    FROM students 
                    WHERE status = 'نشط'
                    ORDER BY name
                """
                params = []
            
            students = db_manager.execute_query(query, params)
            
            if students:
                for student in students:
                    self.student_combo.addItem(student[1], student[0])
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الطلاب: {e}")
    
    def on_school_changed(self):
        """معالج تغيير المدرسة"""
        try:
            self.load_students()
            self.apply_filters()
            
        except Exception as e:
            logging.error(f"خطأ في معالج تغيير المدرسة: {e}")
    
    def load_installments(self):
        """تحميل قائمة الأقساط"""
        try:
            # بناء الاستعلام مع الفلاتر
            query = """
                SELECT i.id, s.name as student_name, sc.name_ar as school_name,
                       i.amount, i.payment_date, i.payment_time, i.notes
                FROM installments i
                LEFT JOIN students s ON i.student_id = s.id
                LEFT JOIN schools sc ON s.school_id = sc.id
                WHERE 1=1
            """
            params = []
            
            # فلتر المدرسة
            selected_school_id = self.school_combo.currentData()
            if selected_school_id:
                query += " AND s.school_id = ?"
                params.append(selected_school_id)
            
            # فلتر الطالب
            selected_student_id = self.student_combo.currentData()
            if selected_student_id:
                query += " AND i.student_id = ?"
                params.append(selected_student_id)
            
            
            query += " ORDER BY i.payment_date DESC, i.created_at DESC"
            
            # تنفيذ الاستعلام
            installments = db_manager.execute_query(query, params)
            
            self.current_installments = installments or []
            self.populate_installments_table()
            # تحديث الملخص المالي بمجموع الأقساط
            self.update_financial_summary()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الأقساط: {e}")
            self.show_error_message("خطأ في التحميل", f"حدث خطأ في تحميل بيانات الأقساط: {str(e)}")
    
    def populate_installments_table(self):
        """ملء جدول الأقساط"""
        try:
            self.installments_table.setRowCount(len(self.current_installments))
            
            for row, installment in enumerate(self.current_installments):
                # المعرف (مخفي)
                self.installments_table.setItem(row, 0, QTableWidgetItem(str(installment[0])))
                # الطالب
                self.installments_table.setItem(row, 1, QTableWidgetItem(installment[1] or ""))
                # المدرسة
                self.installments_table.setItem(row, 2, QTableWidgetItem(installment[2] or ""))
                # المبلغ
                amount = installment[3] or 0
                self.installments_table.setItem(row, 3, QTableWidgetItem(f"{amount:,.2f}"))
                # تاريخ الدفع
                payment_date = installment[4] or ""
                self.installments_table.setItem(row, 4, QTableWidgetItem(str(payment_date)))
                # وقت الدفع
                payment_time = installment[5] or ""
                self.installments_table.setItem(row, 5, QTableWidgetItem(str(payment_time)))
                # الملاحظات
                notes = installment[6] or ""
                self.installments_table.setItem(row, 6, QTableWidgetItem(notes))
            
            # تحديث إحصائية العدد المعروض
            self.displayed_count_label.setText(f"عدد الأقساط المعروضة: {len(self.current_installments)}")
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول الأقساط: {e}")
    
    def update_financial_summary(self):
        """تحديث الملخص المالي"""
        # تبسيط الملخص المالي: مجموع قيمة الأقساط وعددها
        total_amount = sum((inst[3] or 0) for inst in self.current_installments)
        # تحديث عرض المجموع
        self.total_amount_value.setText(f"{total_amount:,.2f} د.ع")
        # تحديث عدد الأقساط في رأس الصفحة
        self.total_installments_label.setText(f"إجمالي الأقساط: {len(self.current_installments)}")
    
    def apply_filters(self):
        """تطبيق الفلاتر وإعادة تحميل البيانات"""
        try:
            self.load_installments()
            
        except Exception as e:
            logging.error(f"خطأ في تطبيق الفلاتر: {e}")
    
    def refresh(self):
        """تحديث البيانات"""
        try:
            log_user_action("تحديث صفحة الأقساط")
            self.load_installments()
            
        except Exception as e:
            logging.error(f"خطأ في تحديث صفحة الأقساط: {e}")
    
    def show_context_menu(self, position):
        """عرض قائمة السياق للجدول"""
        try:
            if self.installments_table.itemAt(position):
                menu = QMenu()
                
                
                
                
                
                menu.addSeparator()
                
                
                
                
                
                menu.exec_(self.installments_table.mapToGlobal(position))
            
        except Exception as e:
            logging.error(f"خطأ في عرض قائمة السياق: {e}")
    
    
    
    
    
    
    
    
    
    
    
    
    
    def generate_report(self):
        """إنتاج تقرير مالي"""
        try:
            self.show_info_message("قيد التطوير", "ميزة التقارير المالية قيد التطوير")
            log_user_action("طلب إنتاج تقرير مالي")
            
        except Exception as e:
            logging.error(f"خطأ في إنتاج التقرير: {e}")
    
    def show_info_message(self, title: str, message: str):
        """عرض رسالة معلومات"""
        try:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة المعلومات: {e}")
    
    def show_error_message(self, title: str, message: str):
        """عرض رسالة خطأ"""
        try:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة الخطأ: {e}")
    
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
                        stop:0 #E74C3C, stop:1 #C0392B);
                    border-radius: 10px;
                    color: white;
                    margin-bottom: 10px;
                }
                
                #pageTitle {
                    font-size: 24px;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 5px;
                }
                
                #pageDesc {
                    font-size: 18px;
                    color: #FADBD8;
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
                }
                
                #filterCombo, #dateInput {
                    padding: 6px 10px;
                    border: 1px solid #BDC3C7;
                    border-radius: 4px;
                    background-color: white;
                    min-width: 100px;
                }
                
                #filterCombo:focus, #dateInput:focus {
                    border-color: #E74C3C;
                    outline: none;
                }
                
                /* الأزرار */
                #primaryButton {
                    background-color: #E74C3C;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                }
                
                #primaryButton:hover {
                    background-color: #C0392B;
                }
                
                #successButton {
                    background-color: #27AE60;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                }
                
                #successButton:hover {
                    background-color: #229954;
                }
                
                #secondaryButton {
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
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
                }
                
                #refreshButton:hover {
                    background-color: #7F8C8D;
                }
                
                /* إطار الجدول */
                #tableFrame {
                    background-color: white;
                    border: 1px solid #E9ECEF;
                    border-radius: 8px;
                }
                
                /* الجدول */
                #dataTable {
                    background-color: white;
                    border: none;
                    border-radius: 6px;
                    gridline-color: #E9ECEF;
                }
                
                #dataTable::item {
                    padding: 8px;
                    border-bottom: 1px solid #F1F2F6;
                }
                
                #dataTable::item:selected {
                    background-color: #FADBD8;
                    color: #C0392B;
                }
                
                #dataTable::item:alternate {
                    background-color: #FAFAFA;
                }
                
                QHeaderView::section {
                    background-color: #34495E;
                    color: white;
                    padding: 10px 8px;
                    border: none;
                    font-weight: bold;
                    font-size: 18px;
                }
                
                QHeaderView::section:hover {
                    background-color: #2C3E50;
                }
                
                /* إطار الملخص المالي */
                #summaryFrame {
                    background-color: white;
                    border: 1px solid #E9ECEF;
                    border-radius: 8px;
                    margin-top: 10px;
                }
                
                #summaryTitle {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin-bottom: 10px;
                }
                
                #summaryLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #7F8C8D;
                    text-align: center;
                }
                
                #summaryValue {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    text-align: center;
                }
                
                #summaryValueSuccess {
                    font-size: 18px;
                    font-weight: bold;
                    color: #27AE60;
                    text-align: center;
                }
                
                #summaryValueWarning {
                    font-size: 18px;
                    font-weight: bold;
                    color: #F39C12;
                    text-align: center;
                }
                
                #summaryValueDanger {
                    font-size: 18px;
                    font-weight: bold;
                    color: #E74C3C;
                    text-align: center;
                }
                
                #statLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin: 2px 0;
                }
                
                /* شريط التقدم */
                #progressBar {
                    border: 2px solid #BDC3C7;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                    color: white;
                }
                
                #progressBar::chunk {
                    background-color: #27AE60;
                    border-radius: 6px;
                }
                
                /* أشرطة التمرير */
                QScrollBar:vertical {
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
            logging.error(f"خطأ في إعداد تنسيقات صفحة الأقساط: {e}")
