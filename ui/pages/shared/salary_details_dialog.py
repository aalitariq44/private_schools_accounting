#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة تفاصيل الرواتب للمعلمين والموظفين
"""

import logging
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QDateEdit, QDoubleSpinBox, QTextEdit, QGroupBox,
    QGridLayout, QSpacerItem, QSizePolicy, QFormLayout,
    QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from core.database.connection import db_manager
from core.utils.logger import log_user_action


class SalaryDetailsDialog(QDialog):
    """نافذة تفاصيل الرواتب"""
    
    def __init__(self, person_type, person_id, person_name, parent=None):
        super().__init__(parent)
        self.person_type = person_type  # 'teacher' or 'employee'
        self.person_id = person_id
        self.person_name = person_name
        self.salaries_data = []
        self.person_data = {}
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_person_data()
        self.load_salary_data()
        
        log_user_action(f"فتح تفاصيل رواتب {self.person_type} {person_name}")

    def setup_ui(self):
        """إعداد واجهة المستخدم بتصميم عصري مشابه لـ add_salary_dialog"""
        self.setWindowTitle(f"تفاصيل رواتب {self.person_name}")
        self.setModal(True)
        self.resize(1600, 800)
        self.setMinimumWidth(1200)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Scroll area لدعم الشاشات الصغيرة
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        # عنوان النافذة
        self.create_header(content_layout)
        
        # قسم الإحصائيات
        self.create_statistics_section(content_layout)
        
        # تخطيط أفقي للجدول ونموذج الإضافة
        content_main_layout = QHBoxLayout()
        
        # جدول الرواتب
        self.create_salaries_table(content_main_layout)
        
        # نموذج إضافة راتب
        self.create_add_salary_form(content_main_layout)
        
        content_layout.addLayout(content_main_layout)
        
        # أزرار النافذة
        self.create_dialog_buttons(content_layout)

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def create_header(self, layout):
        """إنشاء رأس النافذة بتصميم عصري"""
        # عنوان النافذة الرئيسي
        title_label = QLabel(f"تفاصيل رواتب: {self.person_name}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # معلومات الشخص
        info_frame = QFrame()
        info_frame.setObjectName("headerFrame")
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(20, 15, 20, 15)
        
        # النوع
        type_label = QLabel(f"النوع: {'معلم' if self.person_type == 'teacher' else 'موظف'}")
        type_label.setObjectName("infoLabel")
        info_layout.addWidget(type_label)
        
        info_layout.addStretch()
        
        # المدرسة
        self.school_label = QLabel("المدرسة: جاري التحميل...")
        self.school_label.setObjectName("infoLabel")
        info_layout.addWidget(self.school_label)
        
        info_layout.addStretch()
        
        # الراتب المسجل
        self.registered_salary_label = QLabel("الراتب المسجل: جاري التحميل...")
        self.registered_salary_label.setObjectName("salaryInfoLabel")
        info_layout.addWidget(self.registered_salary_label)
        
        layout.addWidget(info_frame)

    def create_statistics_section(self, layout):
        """إنشاء قسم الإحصائيات التفصيلية"""
        stats_group = QGroupBox("إحصائيات الرواتب")
        stats_layout = QHBoxLayout(stats_group)
        stats_layout.setContentsMargins(15, 20, 15, 15)
        
        # العمود الأول - إحصائيات العدد
        count_frame = QFrame()
        count_frame.setObjectName("statsFrame")
        count_layout = QVBoxLayout(count_frame)
        
        count_title = QLabel("إحصائيات العدد")
        count_title.setObjectName("statsTitle")
        count_layout.addWidget(count_title)
        
        self.total_salaries_count_label = QLabel("إجمالي عدد الرواتب: 0")
        self.total_salaries_count_label.setObjectName("statLabel")
        count_layout.addWidget(self.total_salaries_count_label)
        
        self.current_year_count_label = QLabel("رواتب هذا العام: 0")
        self.current_year_count_label.setObjectName("statLabel")
        count_layout.addWidget(self.current_year_count_label)
        
        self.current_month_count_label = QLabel("رواتب هذا الشهر: 0")
        self.current_month_count_label.setObjectName("statLabel")
        count_layout.addWidget(self.current_month_count_label)
        
        stats_layout.addWidget(count_frame)
        
        # العمود الثاني - إحصائيات المبالغ
        amount_frame = QFrame()
        amount_frame.setObjectName("statsFrame")
        amount_layout = QVBoxLayout(amount_frame)
        
        amount_title = QLabel("إحصائيات المبالغ")
        amount_title.setObjectName("statsTitle")
        amount_layout.addWidget(amount_title)
        
        self.total_amount_label = QLabel("إجمالي المبالغ: 0.00 د.ع")
        self.total_amount_label.setObjectName("amountLabel")
        amount_layout.addWidget(self.total_amount_label)
        
        self.current_year_amount_label = QLabel("مبالغ هذا العام: 0.00 د.ع")
        self.current_year_amount_label.setObjectName("statLabel")
        amount_layout.addWidget(self.current_year_amount_label)
        
        self.current_month_amount_label = QLabel("مبالغ هذا الشهر: 0.00 د.ع")
        self.current_month_amount_label.setObjectName("statLabel")
        amount_layout.addWidget(self.current_month_amount_label)
        
        stats_layout.addWidget(amount_frame)
        
        # العمود الثالث - متوسطات وتفاصيل أخرى
        avg_frame = QFrame()
        avg_frame.setObjectName("statsFrame")
        avg_layout = QVBoxLayout(avg_frame)
        
        avg_title = QLabel("متوسطات وتفاصيل")
        avg_title.setObjectName("statsTitle")
        avg_layout.addWidget(avg_title)
        
        self.average_salary_label = QLabel("متوسط الراتب: 0.00 د.ع")
        self.average_salary_label.setObjectName("statLabel")
        avg_layout.addWidget(self.average_salary_label)
        
        self.last_salary_date_label = QLabel("آخر راتب: --")
        self.last_salary_date_label.setObjectName("statLabel")
        avg_layout.addWidget(self.last_salary_date_label)
        
        self.highest_salary_label = QLabel("أعلى راتب: 0.00 د.ع")
        self.highest_salary_label.setObjectName("statLabel")
        avg_layout.addWidget(self.highest_salary_label)
        
        stats_layout.addWidget(avg_frame)
        
        layout.addWidget(stats_group)

    def create_salaries_table(self, layout):
        """إنشاء جدول الرواتب بتصميم محسن"""
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        table_title = QLabel("سجل الرواتب")
        table_title.setObjectName("sectionTitle")
        table_layout.addWidget(table_title)
        
        self.salaries_table = QTableWidget()
        self.salaries_table.setObjectName("salariesTable")
        
        columns = ["المعرف", "تاريخ الدفع", "المبلغ المدفوع", "الراتب الأساسي", "من تاريخ", "إلى تاريخ", "عدد الأيام", "الملاحظات"]
        self.salaries_table.setColumnCount(len(columns))
        self.salaries_table.setHorizontalHeaderLabels(columns)
        
        self.salaries_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.salaries_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.salaries_table.setAlternatingRowColors(True)
        self.salaries_table.setSortingEnabled(True)
        
        # إخفاء عمود المعرف
        self.salaries_table.setColumnHidden(0, True)
        
        # تحسين عرض الأعمدة
        header = self.salaries_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        # تعيين عرض الأعمدة
        self.salaries_table.setColumnWidth(1, 120)  # تاريخ الدفع
        self.salaries_table.setColumnWidth(2, 150)  # المبلغ المدفوع
        self.salaries_table.setColumnWidth(3, 150)  # الراتب الأساسي
        self.salaries_table.setColumnWidth(4, 120)  # من تاريخ
        self.salaries_table.setColumnWidth(5, 120)  # إلى تاريخ
        self.salaries_table.setColumnWidth(6, 100)  # عدد الأيام
        
        table_layout.addWidget(self.salaries_table)
        layout.addWidget(table_frame)

    def create_add_salary_form(self, layout):
        """إنشاء نموذج إضافة راتب بتصميم مشابه لـ add_salary_dialog"""
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_frame.setMaximumWidth(400)
        form_frame.setMinimumWidth(350)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(15, 15, 15, 15)
        
        # عنوان النموذج
        form_title = QLabel("إضافة راتب جديد")
        form_title.setAlignment(Qt.AlignCenter)
        form_title.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #229954);
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 15px;
            }
        """)
        form_layout.addWidget(form_title)
        
        # مجموعة تفاصيل الراتب
        salary_group = self.create_salary_details_group()
        form_layout.addWidget(salary_group)
        
        # مجموعة فترة الراتب
        period_group = self.create_period_details_group()
        form_layout.addWidget(period_group)
        
        # مجموعة الملاحظات
        notes_group = self.create_notes_details_group()
        form_layout.addWidget(notes_group)
        
        # زر الإضافة
        self.add_salary_button = QPushButton("إضافة راتب")
        self.add_salary_button.setObjectName("addSalaryButton")
        self.add_salary_button.setMinimumSize(120, 40)
        form_layout.addWidget(self.add_salary_button)
        
        # مساحة فارغة
        form_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        layout.addWidget(form_frame)

    def create_salary_details_group(self):
        """إنشاء مجموعة تفاصيل الراتب"""
        group = QGroupBox("تفاصيل الراتب")
        layout = QFormLayout()
        layout.setSpacing(10)
        
        # المبلغ المدفوع
        self.amount_edit = QDoubleSpinBox()
        self.amount_edit.setRange(0, 999999999)
        self.amount_edit.setDecimals(2)
        self.amount_edit.setSuffix(" د.ع")
        self.amount_edit.setMinimumWidth(150)
        layout.addRow("المبلغ المدفوع:", self.amount_edit)
        
        # تاريخ الدفع
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMinimumWidth(150)
        layout.addRow("تاريخ الدفع:", self.date_edit)
        
        # الراتب الأساسي (يتم تعبئته تلقائياً)
        self.base_salary_edit = QDoubleSpinBox()
        self.base_salary_edit.setRange(0, 999999999)
        self.base_salary_edit.setDecimals(2)
        self.base_salary_edit.setSuffix(" د.ع")
        self.base_salary_edit.setMinimumWidth(150)
        self.base_salary_edit.setReadOnly(True)  # غير قابل للتعديل
        base_salary_label = QLabel("الراتب الأساسي (تلقائي):")
        base_salary_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addRow(base_salary_label, self.base_salary_edit)
        
        group.setLayout(layout)
        return group

    def create_period_details_group(self):
        """إنشاء مجموعة فترة الراتب"""
        group = QGroupBox("فترة الراتب")
        layout = QFormLayout()
        layout.setSpacing(10)
        
        # من تاريخ
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.from_date_edit.setCalendarPopup(True)
        self.from_date_edit.setMinimumWidth(150)
        layout.addRow("من تاريخ:", self.from_date_edit)
        
        # إلى تاريخ
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setDate(QDate.currentDate())
        self.to_date_edit.setCalendarPopup(True)
        self.to_date_edit.setMinimumWidth(150)
        layout.addRow("إلى تاريخ:", self.to_date_edit)
        
        # عدد الأيام (محسوب تلقائياً)
        self.days_count_label = QLabel("30 يوم")
        self.days_count_label.setObjectName("daysLabel")
        layout.addRow("عدد الأيام:", self.days_count_label)
        
        group.setLayout(layout)
        return group

    def create_notes_details_group(self):
        """إنشاء مجموعة الملاحظات"""
        group = QGroupBox("ملاحظات")
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("أدخل أي ملاحظات إضافية...")
        layout.addWidget(self.notes_edit)
        
        group.setLayout(layout)
        return group

    def create_dialog_buttons(self, layout):
        """إنشاء أزرار النافذة بتصميم محسن"""
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # زر طباعة التقرير
        self.print_report_button = QPushButton("طباعة تقرير الرواتب")
        self.print_report_button.setObjectName("printButton")
        self.print_report_button.setMinimumSize(160, 35)
        buttons_layout.addWidget(self.print_report_button)
        
        # زر تحديث
        self.refresh_button = QPushButton("تحديث")
        self.refresh_button.setObjectName("secondaryButton")
        self.refresh_button.setMinimumSize(100, 35)
        buttons_layout.addWidget(self.refresh_button)
        
        # زر إغلاق
        self.close_button = QPushButton("إغلاق")
        self.close_button.setObjectName("closeButton")
        self.close_button.setMinimumSize(100, 35)
        buttons_layout.addWidget(self.close_button)
        
        layout.addLayout(buttons_layout)

    def setup_styles(self):
        """إعداد الأنماط بتصميم عصري مشابه لـ add_salary_dialog"""
        style = """
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9ff, stop:1 #e8f0ff);
                font-family: 'Segoe UI', 'Cairo', Arial, sans-serif;
                font-size: 14px;
            }
            
            #headerFrame {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 10px;
            }
            
            #infoLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
            }
            
            #salaryInfoLabel {
                color: #27ae60;
                font-weight: bold;
                font-size: 16px;
                padding: 5px;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 12px;
                margin: 15px 0px;
                padding-top: 20px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 14px;
            }
            
            #statsFrame {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            
            #statsTitle {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
                padding-bottom: 8px;
                border-bottom: 2px solid #3498db;
            }
            
            #statLabel {
                font-size: 14px;
                color: #34495e;
                margin: 5px 0px;
                padding: 3px;
            }
            
            #amountLabel {
                font-size: 16px;
                font-weight: bold;
                color: #27ae60;
                margin: 5px 0px;
                padding: 5px;
            }
            
            #tableFrame, #formFrame {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
            
            #sectionTitle {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
                padding-bottom: 5px;
                border-bottom: 2px solid #3498db;
            }
            
            #salariesTable {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                font-size: 13px;
                gridline-color: #e9ecef;
            }
            
            #salariesTable::item {
                padding: 10px;
                border-bottom: 1px solid #e9ecef;
            }
            
            #salariesTable::item:selected {
                background-color: #3498db;
                color: white;
            }
            
            #salariesTable::item:alternate {
                background-color: #f8f9fa;
            }
            
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 14px;
                margin: 5px 0px;
            }
            
            QLineEdit, QDoubleSpinBox, QDateEdit, QTextEdit {
                padding: 12px 15px;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: white;
                font-size: 14px;
                min-height: 25px;
                margin: 5px 0px;
            }

            QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTextEdit:focus {
                border-color: #3498db;
                background-color: #f8fbff;
            }
            
            QDoubleSpinBox:read-only {
                background-color: #f0f0f0;
                color: #666666;
                border: 2px solid #cccccc;
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
                margin: 8px 4px;
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }

            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #1f618d);
            }
            
            #addSalaryButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #229954);
            }
            
            #addSalaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2ecc71, stop:1 #27ae60);
            }
            
            #printButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9b59b6, stop:1 #8e44ad);
            }
            
            #printButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #af7ac5, stop:1 #9b59b6);
            }
            
            #secondaryButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
            }
            
            #closeButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #95a5a6, stop:1 #7f8c8d);
            }
            
            #closeButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #bdc3c7, stop:1 #95a5a6);
            }
            
            #daysLabel {
                color: #e74c3c;
                font-weight: bold;
                font-size: 14px;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """
        self.setStyleSheet(style)

    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        self.add_salary_button.clicked.connect(self.add_salary)
        self.refresh_button.clicked.connect(self.load_salary_data)
        self.close_button.clicked.connect(self.accept)
        self.print_report_button.clicked.connect(self.print_salary_report)
        
        # ربط حساب الأيام والراتب تلقائياً (بدون ربط تغيير الراتب الأساسي)
        self.from_date_edit.dateChanged.connect(self.calculate_days)
        self.to_date_edit.dateChanged.connect(self.calculate_days)

    def load_person_data(self):
        """تحميل بيانات الشخص (معلم أو موظف)"""
        try:
            table_name = "teachers" if self.person_type == "teacher" else "employees"
            
            query = f"""
                SELECT name, monthly_salary, school_id,
                       (SELECT name_ar FROM schools WHERE id = {table_name}.school_id) as school_name
                FROM {table_name}
                WHERE id = ?
            """
            
            result = db_manager.execute_query(query, (self.person_id,))
            
            if result:
                row = result[0]
                self.person_data = dict(row)  # تحويل sqlite3.Row إلى dictionary
                # تحديث معلومات الرأس
                school_name = self.person_data.get('school_name', 'غير محدد')
                self.school_label.setText(f"المدرسة: {school_name}")
                
                salary = float(self.person_data.get('monthly_salary', 0) or 0)
                self.registered_salary_label.setText(f"الراتب المسجل: {salary:,.0f} د.ع")
                
                # تعبئة الراتب الأساسي في النموذج (غير قابل للتعديل)
                self.base_salary_edit.setValue(salary)
                self.base_salary_edit.setReadOnly(True)  # جعله غير قابل للتعديل
                self.amount_edit.setValue(salary)  # كقيمة افتراضية قابلة للتعديل
            else:
                self.person_data = {}
                self.school_label.setText("المدرسة: غير محدد")
                self.registered_salary_label.setText("الراتب المسجل: 0.00 د.ع")
                self.base_salary_edit.setValue(0)
                self.base_salary_edit.setReadOnly(True)
                
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الشخص: {e}")
            self.person_data = {}
            self.school_label.setText("المدرسة: خطأ في التحميل")
            self.registered_salary_label.setText("الراتب المسجل: خطأ في التحميل")
            self.base_salary_edit.setValue(0)
            self.base_salary_edit.setReadOnly(True)

    def load_salary_data(self):
        """تحميل بيانات الرواتب"""
        try:
            staff_type = "teacher" if self.person_type == "teacher" else "employee"
            
            query = """
                SELECT id, payment_date, paid_amount, base_salary, 
                       from_date, to_date, days_count, notes
                FROM salaries
                WHERE staff_type = ? AND staff_id = ?
                ORDER BY payment_date DESC
            """
            
            results = db_manager.execute_query(query, (staff_type, self.person_id))
            # تحويل كل sqlite3.Row إلى dictionary
            self.salaries_data = [dict(row) for row in results] if results else []
            self.populate_salaries_table()
            self.update_statistics()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الرواتب: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل بيانات الرواتب:\n{str(e)}")
            self.salaries_data = []

    def update_statistics(self):
        """تحديث الإحصائيات التفصيلية"""
        try:
            if not self.salaries_data:
                # إذا لم توجد بيانات، اعرض القيم الافتراضية
                self.total_salaries_count_label.setText("إجمالي عدد الرواتب: 0")
                self.current_year_count_label.setText("رواتب هذا العام: 0")
                self.current_month_count_label.setText("رواتب هذا الشهر: 0")
                self.total_amount_label.setText("إجمالي المبالغ: 0.00 د.ع")
                self.current_year_amount_label.setText("مبالغ هذا العام: 0.00 د.ع")
                self.current_month_amount_label.setText("مبالغ هذا الشهر: 0.00 د.ع")
                self.average_salary_label.setText("متوسط الراتب: 0.00 د.ع")
                self.last_salary_date_label.setText("آخر راتب: --")
                self.highest_salary_label.setText("أعلى راتب: 0.00 د.ع")
                return
            
            # تواريخ مهمة للحسابات
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            # متغيرات للحسابات
            total_count = len(self.salaries_data)
            total_amount = 0
            current_year_count = 0
            current_year_amount = 0
            current_month_count = 0
            current_month_amount = 0
            highest_salary = 0
            last_salary_date = None
            
            for salary in self.salaries_data:
                # تحويل القيم إلى أرقام مع التعامل مع القيم المفقودة
                paid_amount = salary.get('paid_amount', 0)
                if paid_amount is None:
                    paid_amount = 0
                
                try:
                    amount = float(paid_amount)
                except (ValueError, TypeError):
                    amount = 0
                
                total_amount += amount
                
                if amount > highest_salary:
                    highest_salary = amount
                
                # تحليل التاريخ
                payment_date_str = salary.get('payment_date', '')
                if payment_date_str:
                    try:
                        if isinstance(payment_date_str, str):
                            payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d')
                        else:
                            # إذا كان التاريخ كائن datetime بالفعل
                            payment_date = payment_date_str
                        
                        # أحدث راتب
                        if last_salary_date is None or payment_date > last_salary_date:
                            last_salary_date = payment_date
                        
                        # رواتب هذا العام
                        if payment_date.year == current_year:
                            current_year_count += 1
                            current_year_amount += amount
                            
                            # رواتب هذا الشهر
                            if payment_date.month == current_month:
                                current_month_count += 1
                                current_month_amount += amount
                                
                    except (ValueError, AttributeError) as e:
                        logging.debug(f"خطأ في تحليل التاريخ {payment_date_str}: {e}")
                        continue
            
            # حساب المتوسط
            average_salary = total_amount / total_count if total_count > 0 else 0
            
            # تحديث عرض الإحصائيات
            self.total_salaries_count_label.setText(f"إجمالي عدد الرواتب: {total_count}")
            self.current_year_count_label.setText(f"رواتب هذا العام: {current_year_count}")
            self.current_month_count_label.setText(f"رواتب هذا الشهر: {current_month_count}")
            
            self.total_amount_label.setText(f"إجمالي المبالغ: {total_amount:,.0f} د.ع")
            self.current_year_amount_label.setText(f"مبالغ هذا العام: {current_year_amount:,.0f} د.ع")
            self.current_month_amount_label.setText(f"مبالغ هذا الشهر: {current_month_amount:,.0f} د.ع")
            
            self.average_salary_label.setText(f"متوسط الراتب: {average_salary:,.0f} د.ع")
            self.highest_salary_label.setText(f"أعلى راتب: {highest_salary:,.0f} د.ع")
            
            if last_salary_date:
                self.last_salary_date_label.setText(f"آخر راتب: {last_salary_date.strftime('%Y-%m-%d')}")
            else:
                self.last_salary_date_label.setText("آخر راتب: --")
                
        except Exception as e:
            logging.error(f"خطأ في تحديث الإحصائيات: {e}")
            # في حالة الخطأ، أظهر القيم الافتراضية
            self.total_salaries_count_label.setText("إجمالي عدد الرواتب: خطأ")
            self.current_year_count_label.setText("رواتب هذا العام: خطأ")
            self.current_month_count_label.setText("رواتب هذا الشهر: خطأ")
            self.total_amount_label.setText("إجمالي المبالغ: خطأ")
            self.current_year_amount_label.setText("مبالغ هذا العام: خطأ")
            self.current_month_amount_label.setText("مبالغ هذا الشهر: خطأ")
            self.average_salary_label.setText("متوسط الراتب: خطأ")
            self.last_salary_date_label.setText("آخر راتب: خطأ")
            self.highest_salary_label.setText("أعلى راتب: خطأ")

    def populate_salaries_table(self):
        """ملء جدول الرواتب"""
        try:
            self.salaries_table.setRowCount(0)
            
            if not self.salaries_data:
                return
            
            for row_idx, salary in enumerate(self.salaries_data):
                self.salaries_table.insertRow(row_idx)
                
                # تنسيق التواريخ
                payment_date = salary.get('payment_date', '')
                from_date = salary.get('from_date', '')
                to_date = salary.get('to_date', '')
                
                # تحويل التواريخ إلى تنسيق قابل للقراءة
                def format_date(date_str):
                    if not date_str:
                        return ""
                    try:
                        if isinstance(date_str, str):
                            return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
                        else:
                            return date_str.strftime('%Y-%m-%d') if hasattr(date_str, 'strftime') else str(date_str)
                    except:
                        return str(date_str)
                
                payment_date = format_date(payment_date)
                from_date = format_date(from_date)
                to_date = format_date(to_date)
                
                # تحويل المبالغ مع التعامل مع القيم المفقودة
                def format_amount(amount):
                    if amount is None:
                        return "0 د.ع"
                    try:
                        return f"{float(amount):,.0f} د.ع"
                    except (ValueError, TypeError):
                        return "0 د.ع"
                
                paid_amount = format_amount(salary.get('paid_amount'))
                base_salary = format_amount(salary.get('base_salary'))
                
                items = [
                    str(salary.get('id', '')),
                    payment_date,
                    paid_amount,
                    base_salary,
                    from_date,
                    to_date,
                    str(salary.get('days_count', '') or ''),
                    salary.get('notes', '') or ""
                ]
                
                for col_idx, item_text in enumerate(items):
                    item = QTableWidgetItem(item_text)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
                    # تلوين الأموال بألوان مختلفة
                    if col_idx == 2:  # المبلغ المدفوع
                        item.setBackground(QColor(144, 238, 144))  # lightGreen
                    elif col_idx == 3:  # الراتب الأساسي
                        item.setBackground(QColor(173, 216, 230))  # lightBlue
                    
                    self.salaries_table.setItem(row_idx, col_idx, item)
            
            # تحسين عرض الأعمدة
            header = self.salaries_table.horizontalHeader()
            for i in range(1, self.salaries_table.columnCount()):
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول الرواتب: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في ملء جدول الرواتب:\n{str(e)}")

    def validate_salary_inputs(self):
        """التحقق من صحة البيانات المدخلة"""
        # التحقق من المبلغ المدفوع
        if self.amount_edit.value() <= 0:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال مبلغ صحيح للمبلغ المدفوع")
            return False
        
        # التحقق من الراتب الأساسي (يجب أن يكون موجود من البيانات المسجلة)
        if self.base_salary_edit.value() <= 0:
            QMessageBox.warning(self, "تحذير", "الراتب الأساسي غير محدد. يرجى التأكد من تسجيل راتب للشخص في بياناته الأساسية")
            return False
        
        # التحقق من صحة التواريخ
        from_date = self.from_date_edit.date()
        to_date = self.to_date_edit.date()
        
        if from_date > to_date:
            QMessageBox.warning(self, "تحذير", "تاريخ البداية يجب أن يكون قبل تاريخ النهاية")
            return False
        
        return True

    def add_salary(self):
        """إضافة راتب جديد بأسلوب مشابه لـ add_salary_dialog"""
        try:
            if not self.validate_salary_inputs():
                return
            
            # تأكيد الإضافة
            reply = QMessageBox.question(
                self, "تأكيد الإضافة",
                f"هل تريد إضافة راتب بمبلغ {self.amount_edit.value():,.2f} د.ع؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # حساب عدد الأيام
            from_date_q = self.from_date_edit.date()
            to_date_q = self.to_date_edit.date()
            days_count = from_date_q.daysTo(to_date_q) + 1
            
            # تحضير البيانات
            staff_type = "teacher" if self.person_type == "teacher" else "employee"
            school_id = self.person_data.get('school_id')
            
            from_date = from_date_q.toString(Qt.ISODate)
            to_date = to_date_q.toString(Qt.ISODate)
            payment_date = self.date_edit.date().toString(Qt.ISODate)
            payment_time = datetime.now().strftime("%H:%M:%S")
            
            # إدراج البيانات في قاعدة البيانات
            with db_manager.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO salaries 
                    (staff_type, staff_id, base_salary, paid_amount, 
                     from_date, to_date, days_count, payment_date, payment_time, notes, school_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    staff_type,
                    self.person_id,
                    self.base_salary_edit.value(),
                    self.amount_edit.value(),
                    from_date,
                    to_date,
                    days_count,
                    payment_date,
                    payment_time,
                    self.notes_edit.toPlainText().strip() or None,
                    school_id
                ))
            
            # تسجيل العملية
            log_user_action(
                f"إضافة راتب {staff_type}",
                f"الاسم: {self.person_name}, المبلغ: {self.amount_edit.value()}, المدرسة: {self.person_data.get('school_name', 'غير محدد')}"
            )
            
            QMessageBox.information(self, "نجح", "تم إضافة الراتب بنجاح")
            self.clear_form()
            self.load_salary_data()
            
        except Exception as e:
            logging.error(f"خطأ في إضافة راتب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في إضافة الراتب:\n{str(e)}")

    def clear_form(self):
        """مسح نموذج الإدخال"""
        self.date_edit.setDate(QDate.currentDate())
        # استخدام الراتب المسجل كقيمة افتراضية
        base_salary = float(self.person_data.get('monthly_salary', 0) or 0)
        self.amount_edit.setValue(base_salary)
        self.base_salary_edit.setValue(base_salary)
        self.base_salary_edit.setReadOnly(True)  # تأكد من أنه غير قابل للتعديل
        self.from_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.to_date_edit.setDate(QDate.currentDate())
        self.notes_edit.clear()
        self.calculate_days()

    def calculate_days(self):
        """حساب عدد الأيام بناءً على التواريخ مع تحديث العرض"""
        try:
            from_date = self.from_date_edit.date()
            to_date = self.to_date_edit.date()
            
            if from_date <= to_date:
                days = from_date.daysTo(to_date) + 1  # +1 لتضمين اليوم الأخير
                self.days_count_label.setText(f"{days} يوم")
                self.days_count_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                
                # حساب الراتب التلقائي
                self.calculate_salary()
            else:
                self.days_count_label.setText("تاريخ غير صحيح!")
                self.days_count_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            
        except Exception as e:
            logging.debug(f"خطأ في حساب الأيام: {e}")

    def calculate_salary(self):
        """حساب الراتب بناءً على الراتب الأساسي وعدد الأيام"""
        try:
            base_salary = self.base_salary_edit.value()
            
            # استخراج عدد الأيام من النص
            days_text = self.days_count_label.text().replace(" يوم", "").replace("تاريخ غير صحيح!", "0")
            
            try:
                days = int(days_text)
            except ValueError:
                days = 30  # قيمة افتراضية
            
            if base_salary > 0 and days > 0:
                # حساب الراتب اليومي (الراتب الشهري / 30)
                daily_salary = base_salary / 30
                calculated_amount = daily_salary * days
                
                # تحديث المبلغ المدفوع فقط إذا كان فارغاً أو يساوي الحساب السابق
                current_amount = self.amount_edit.value()
                if current_amount == 0 or abs(current_amount - calculated_amount) < 0.01:
                    self.amount_edit.setValue(calculated_amount)
            
        except (ValueError, ZeroDivisionError) as e:
            logging.debug(f"خطأ في حساب الراتب: {e}")

    def print_salary_report(self):
        """طباعة تقرير مفصل عن رواتب الشخص"""
        try:
            # محاولة استيراد وحدة الطباعة
            try:
                from ui.components.printing.salary_report_printer import SalaryReportPrinter
                printer = SalaryReportPrinter()
                printer.print_person_salary_report(
                    person_type=self.person_type,
                    person_id=self.person_id,
                    person_name=self.person_name,
                    person_data=self.person_data,
                    salaries_data=self.salaries_data
                )
            except ImportError:
                # في حالة عدم وجود وحدة الطباعة، اعرض تقرير أساسي
                total_amount = sum(float(s.get('paid_amount', 0) or 0) for s in self.salaries_data)
                QMessageBox.information(
                    self, "تقرير الرواتب", 
                    f"تقرير رواتب: {self.person_name}\n"
                    f"النوع: {'معلم' if self.person_type == 'teacher' else 'موظف'}\n"
                    f"إجمالي الرواتب: {len(self.salaries_data)}\n"
                    f"المجموع الكلي: {total_amount:,.0f} د.ع\n"
                    f"الراتب المسجل: {float(self.person_data.get('monthly_salary', 0) or 0):,.0f} د.ع\n\n"
                    "ميزة طباعة التقارير المفصلة ستكون متاحة قريباً."
                )
            
        except Exception as e:
            logging.error(f"خطأ في طباعة التقرير: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في طباعة التقرير:\n{str(e)}")

    def showEvent(self, event):
        """ضمان تكبير النافذة دائماً عند عرضها حتى لو حاول النظام استرجاع حجم سابق"""
        super().showEvent(event)
        try:
            if not self.isMaximized():
                self.setWindowState(self.windowState() | Qt.WindowMaximized)
        except Exception as e:
            logging.debug(f"تعذر فرض التكبير: {e}")
