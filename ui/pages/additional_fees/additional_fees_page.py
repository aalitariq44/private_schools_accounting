#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة الرسوم الإضافية
"""

import logging
import json
import os
import sqlite3
from datetime import datetime, date
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QMenu, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QTextEdit, QAction, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon, QFontDatabase

import config
from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation
from .add_additional_fee_dialog import AddAdditionalFeeDialog

# استخدام مسار قاعدة البيانات من الإعدادات
db_path = str(config.DATABASE_PATH)




class AdditionalFeesPage(QWidget):
    """صفحة إدارة الرسوم الإضافية"""
    
    # إشارات النافذة
    page_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_fees = []
        self.selected_school_id = None
        self.selected_student_id = None
        
        # تحميل وتطبيق خط Cairo
        self.setup_cairo_font()
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_initial_data()
        
        log_user_action("فتح صفحة إدارة الرسوم الإضافية")
    
    def setup_cairo_font(self):
        """تحميل وتطبيق خط Cairo"""
        try:
            font_db = QFontDatabase()
            font_dir = config.RESOURCES_DIR / "fonts"
            
            # تحميل خطوط Cairo
            id_medium = font_db.addApplicationFont(str(font_dir / "Cairo-Medium.ttf"))
            id_bold = font_db.addApplicationFont(str(font_dir / "Cairo-Bold.ttf"))
            
            # الحصول على اسم عائلة الخط
            families = font_db.applicationFontFamilies(id_medium)
            self.cairo_family = families[0] if families else "Arial"
            
            logging.info(f"تم تحميل خط Cairo بنجاح: {self.cairo_family}")
            
        except Exception as e:
            logging.warning(f"فشل في تحميل خط Cairo، استخدام الخط الافتراضي: {e}")
            self.cairo_family = "Arial"
    
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
            
            # جدول الرسوم الإضافية
            self.create_fees_table(layout)
            
            # إحصائيات وملخص
            self.create_summary(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة الرسوم الإضافية: {e}")
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
            
            title_label = QLabel("إدارة الرسوم الإضافية")
            title_label.setObjectName("pageTitle")
            title_label.setStyleSheet("color: black;")
            text_layout.addWidget(title_label)
            
            desc_label = QLabel("عرض الرسوم الإضافية مثل رسوم التسجيل، الزي المدرسي، الكتب، وغيرها")
            desc_label.setObjectName("pageDesc")
            desc_label.setStyleSheet("color: black;")
            text_layout.addWidget(desc_label)
            
            header_layout.addLayout(text_layout)
            header_layout.addStretch()
            
            # إحصائيات سريعة في الرأس
            stats_layout = QHBoxLayout()
            
            self.total_fees_label = QLabel("إجمالي الرسوم: 0")
            self.total_fees_label.setObjectName("quickStat")
            stats_layout.addWidget(self.total_fees_label)
            
            self.collected_amount_label = QLabel("المحصل: 0 د.ع")
            self.collected_amount_label.setObjectName("quickStat")
            stats_layout.addWidget(self.collected_amount_label)
            
            self.pending_fees_label = QLabel("المستحق: 0 د.ع")
            self.pending_fees_label.setObjectName("quickStat")
            stats_layout.addWidget(self.pending_fees_label)
            
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
            
            # نوع الرسم
            fee_type_label = QLabel("نوع الرسم:")
            fee_type_label.setObjectName("filterLabel")
            filters_layout.addWidget(fee_type_label)
            
            self.fee_type_combo = QComboBox()
            self.fee_type_combo.setObjectName("filterCombo")
            self.fee_type_combo.addItems([
                "جميع الأنواع", "رسوم التسجيل", "الزي المدرسي", "الكتب", 
                "القرطاسية", "رسم مخصص"
            ])
            filters_layout.addWidget(self.fee_type_combo)
            
            # فلتر الحالة
            status_label = QLabel("حالة الدفع:")
            status_label.setObjectName("filterLabel")
            filters_layout.addWidget(status_label)
            
            self.status_combo = QComboBox()
            self.status_combo.setObjectName("filterCombo")
            self.status_combo.addItems(["الكل", "مدفوع", "غير مدفوع"])
            filters_layout.addWidget(self.status_combo)
            
            filters_layout.addStretch()
            
            toolbar_layout.addLayout(filters_layout)
            
            # الصف الثاني - البحث والعمليات
            actions_layout = QHBoxLayout()
            
            # البحث
            search_label = QLabel("البحث:")
            search_label.setObjectName("filterLabel")
            actions_layout.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setObjectName("searchInput")
            self.search_input.setPlaceholderText("ابحث في الملاحظات أو اسم الطالب...")
            self.search_input.setMinimumWidth(300)
            actions_layout.addWidget(self.search_input)
            
            actions_layout.addStretch()
            
            # أزرار العمليات
            self.export_fees_button = QPushButton("تصدير التقرير")
            self.export_fees_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.export_fees_button)
            
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.refresh_button)
            
            self.clear_filters_button = QPushButton("مسح الفلاتر")
            self.clear_filters_button.setObjectName("secondaryButton") # Using secondaryButton style for consistency
            actions_layout.addWidget(self.clear_filters_button)
            
            toolbar_layout.addLayout(actions_layout)
            
            layout.addWidget(toolbar_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
            raise
    
    def create_fees_table(self, layout):
        """إنشاء جدول الرسوم الإضافية"""
        try:
            # إطار الجدول
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")
            
            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)
            
            # إنشاء الجدول
            self.fees_table = QTableWidget()
            self.fees_table.setObjectName("dataTable")
            
            # إعداد الأعمدة
            columns = [
                "المعرف", "الطالب", "المدرسة", "نوع الرسم", "المبلغ",
                "حالة الدفع", "تاريخ الدفع", "ملاحظات", "تاريخ الإنشاء"
            ]
            
            self.fees_table.setColumnCount(len(columns))
            self.fees_table.setHorizontalHeaderLabels(columns)
            
            # إعداد خصائص الجدول
            self.fees_table.setAlternatingRowColors(True)
            self.fees_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.fees_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.fees_table.setSortingEnabled(True)
            self.fees_table.setShowGrid(False)
            self.fees_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # منع التعديل المباشر
            
            # تخصيص عرض الأعمدة
            header = self.fees_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.setDefaultSectionSize(130)
            header.resizeSection(0, 80)   # المعرف
            header.resizeSection(1, 180)  # الطالب
            header.resizeSection(2, 150)  # المدرسة
            header.resizeSection(3, 120)  # نوع الرسم
            header.resizeSection(4, 110)  # المبلغ
            header.resizeSection(5, 100)  # حالة الدفع
            header.resizeSection(6, 120)  # تاريخ الدفع
            header.resizeSection(7, 200)  # ملاحظات
            
            # إخفاء العمود الأول (المعرف) 
            self.fees_table.setColumnHidden(0, True)
            
            # ربط الأحداث
            self.fees_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.fees_table.customContextMenuRequested.connect(self.show_context_menu)
            # إزالة الحشوات داخل الصفوف لتوحيد ارتفاع الصفوف مع صفحة الطلاب
            self.fees_table.setStyleSheet("QTableWidget::item { padding: 0px; }")
            
            table_layout.addWidget(self.fees_table)
            layout.addWidget(table_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول الرسوم الإضافية: {e}")
            raise
    
    def create_summary(self, layout):
        """إنشاء ملخص الرسوم"""
        try:
            summary_frame = QFrame()
            summary_frame.setObjectName("summaryFrame")
            
            summary_layout = QHBoxLayout(summary_frame)
            summary_layout.setContentsMargins(15, 10, 15, 10)
            
            # ملخص الأرقام
            numbers_layout = QVBoxLayout()
            
            summary_title = QLabel("ملخص الرسوم الإضافية")
            summary_title.setObjectName("summaryTitle")
            numbers_layout.addWidget(summary_title)
            
            numbers_grid = QHBoxLayout()
            
            # إجمالي المبالغ
            total_layout = QVBoxLayout()
            self.total_amount_label = QLabel("إجمالي المبالغ")
            self.total_amount_label.setObjectName("summaryLabel")
            total_layout.addWidget(self.total_amount_label)
            
            self.total_amount_value = QLabel("0 د.ع")
            self.total_amount_value.setObjectName("summaryValue")
            total_layout.addWidget(self.total_amount_value)
            numbers_grid.addLayout(total_layout)
            
            # المبالغ المحصلة
            collected_layout = QVBoxLayout()
            self.collected_label = QLabel("المحصل")
            self.collected_label.setObjectName("summaryLabel")
            collected_layout.addWidget(self.collected_label)
            
            self.collected_value = QLabel("0 د.ع")
            self.collected_value.setObjectName("summaryValueSuccess")
            collected_layout.addWidget(self.collected_value)
            numbers_grid.addLayout(collected_layout)
            
            # المبالغ المستحقة
            pending_layout = QVBoxLayout()
            self.pending_summary_label = QLabel("المستحق")
            self.pending_summary_label.setObjectName("summaryLabel")
            pending_layout.addWidget(self.pending_summary_label)
            
            self.pending_summary_value = QLabel("0 د.ع")
            self.pending_summary_value.setObjectName("summaryValueWarning")
            pending_layout.addWidget(self.pending_summary_value)
            numbers_grid.addLayout(pending_layout)
            
            numbers_layout.addLayout(numbers_grid)
            summary_layout.addLayout(numbers_layout)
            
            # إحصائيات حسب النوع
            types_layout = QVBoxLayout()
            
            types_title = QLabel("إحصائيات حسب النوع (المدفوع)")
            types_title.setObjectName("summaryLabel")
            types_layout.addWidget(types_title)
            
            self.registration_fees_label = QLabel("رسوم تسجيل: 0 د.ع")
            self.registration_fees_label.setObjectName("statLabel")
            types_layout.addWidget(self.registration_fees_label)

            self.uniform_fees_label = QLabel("الزي المدرسي: 0 د.ع")
            self.uniform_fees_label.setObjectName("statLabel")
            types_layout.addWidget(self.uniform_fees_label)

            self.books_fees_label = QLabel("الكتب: 0 د.ع")
            self.books_fees_label.setObjectName("statLabel")
            types_layout.addWidget(self.books_fees_label)
            
            self.stationery_fees_label = QLabel("القرطاسية: 0 د.ع")
            self.stationery_fees_label.setObjectName("statLabel")
            types_layout.addWidget(self.stationery_fees_label)

            self.custom_fees_label = QLabel("رسم مخصص: 0 د.ع")
            self.custom_fees_label.setObjectName("statLabel")
            types_layout.addWidget(self.custom_fees_label)
            
            summary_layout.addLayout(types_layout)
            
            # إحصائيات أخرى
            stats_layout = QVBoxLayout()
            
            self.displayed_count_label = QLabel("عدد الرسوم المعروضة: 0")
            self.displayed_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.displayed_count_label)
            
            self.pending_count_label = QLabel("الرسوم غير المدفوعة: 0")
            self.pending_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.pending_count_label)
            
            self.collected_count_label = QLabel("الرسوم المدفوعة: 0")
            self.collected_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.collected_count_label)
            
            summary_layout.addLayout(stats_layout)
            
            layout.addWidget(summary_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء ملخص الرسوم: {e}")
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            # ربط أزرار العمليات
            self.export_fees_button.clicked.connect(self.export_fees)
            self.refresh_button.clicked.connect(self.refresh)
            self.clear_filters_button.clicked.connect(self.clear_filters)
            
            # ربط الفلاتر
            self.school_combo.currentTextChanged.connect(self.on_school_changed)
            self.student_combo.currentTextChanged.connect(self.apply_filters)
            self.fee_type_combo.currentTextChanged.connect(self.apply_filters)
            self.status_combo.currentTextChanged.connect(self.apply_filters)
            self.search_input.textChanged.connect(self.apply_filters)
            
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
            
            # تحميل الطلاب والرسوم بعد تحميل المدارس
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
                    SELECT id, name 
                    FROM students 
                    WHERE school_id = ? AND status = 'نشط'
                    ORDER BY name
                """
                params = [selected_school_id]
            else:
                query = """
                    SELECT id, name 
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
    
    def load_fees(self):
        """تحميل قائمة الرسوم الإضافية"""
        try:
            # بناء الاستعلام مع الفلاتر
            query = """
                SELECT 
                    af.id, 
                    s.name as student_name, 
                    sc.name_ar as school_name,
                    af.fee_type, 
                    af.amount, 
                    af.paid, 
                    af.payment_date, 
                    af.notes,
                    af.created_at
                FROM additional_fees af
                JOIN students s ON af.student_id = s.id
                JOIN schools sc ON s.school_id = sc.id
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
                query += " AND af.student_id = ?"
                params.append(selected_student_id)
            
            # فلتر نوع الرسم
            selected_fee_type = self.fee_type_combo.currentText()
            if selected_fee_type and selected_fee_type != "جميع الأنواع":
                query += " AND af.fee_type = ?"
                params.append(selected_fee_type)
            
            # فلتر الحالة
            selected_status = self.status_combo.currentText()
            if selected_status and selected_status != "الكل":
                paid_status = 1 if selected_status == "مدفوع" else 0
                query += " AND af.paid = ?"
                params.append(paid_status)
            
            # فلتر البحث
            search_text = self.search_input.text().strip()
            if search_text:
                query += " AND (af.notes LIKE ? OR s.name LIKE ?)"
                search_param = f"%{search_text}%"
                params.extend([search_param, search_param])
            
            query += " ORDER BY af.created_at DESC"
            
            # تنفيذ الاستعلام
            fees = db_manager.execute_query(query, params)
            
            self.current_fees = fees or []
            self.populate_fees_table()
            self.update_summary()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الرسوم الإضافية: {e}")
            self.show_error_message("خطأ في التحميل", f"حدث خطأ في تحميل بيانات الرسوم الإضافية: {str(e)}")
    
    def populate_fees_table(self):
        """ملء جدول الرسوم الإضافية"""
        try:
            self.fees_table.setRowCount(len(self.current_fees))
            
            for row, fee in enumerate(self.current_fees):
                # (id, student_name, school_name, fee_type, amount, paid, payment_date, notes, created_at)
                
                # المعرف (مخفي)
                self.fees_table.setItem(row, 0, QTableWidgetItem(str(fee[0])))
                
                # الطالب
                self.fees_table.setItem(row, 1, QTableWidgetItem(fee[1] or ""))
                
                # المدرسة
                self.fees_table.setItem(row, 2, QTableWidgetItem(fee[2] or ""))
                
                # نوع الرسم
                self.fees_table.setItem(row, 3, QTableWidgetItem(fee[3] or ""))
                
                # المبلغ
                amount = fee[4] or 0
                self.fees_table.setItem(row, 4, QTableWidgetItem(f"{amount:,.0f}"))
                
                # حالة الدفع
                paid = fee[5]
                status_text = "مدفوع" if paid else "غير مدفوع"
                status_item = QTableWidgetItem(status_text)
                status_item.setTextAlignment(Qt.AlignCenter)
                if paid:
                    status_item.setBackground(Qt.green)
                else:
                    status_item.setBackground(Qt.yellow)
                    status_item.setForeground(Qt.red)
                self.fees_table.setItem(row, 5, status_item)

                # تاريخ الدفع
                payment_date = fee[6] or ""
                self.fees_table.setItem(row, 6, QTableWidgetItem(str(payment_date)))

                # الملاحظات
                notes = fee[7] or ""
                self.fees_table.setItem(row, 7, QTableWidgetItem(notes))

                # تاريخ الإنشاء
                created_at = fee[8]
                formatted_date = ""
                if created_at:
                    try:
                        date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")
                    except:
                        formatted_date = str(created_at)[:16]
                self.fees_table.setItem(row, 8, QTableWidgetItem(formatted_date))

            # تحديث إحصائية العدد المعروض
            self.displayed_count_label.setText(f"عدد الرسوم المعروضة: {len(self.current_fees)}")
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول الرسوم الإضافية: {e}")
    
    def update_summary(self):
        """تحديث ملخص الرسوم"""
        try:
            # حساب الإجماليات للرسوم المعروضة
            total_amount = 0
            collected_amount = 0
            pending_amount = 0
            pending_count = 0
            collected_count = 0
            
            # إحصائيات حسب النوع
            type_amounts = {
                "رسوم التسجيل": 0,
                "الزي المدرسي": 0,
                "الكتب": 0,
                "القرطاسية": 0,
                "رسم مخصص": 0
            }
            
            for fee in self.current_fees:
                # (id, student_name, school_name, fee_type, amount, paid, payment_date, notes, created_at)
                amount = fee[4] or 0
                paid = fee[5]
                fee_type = fee[3] or ""
                
                total_amount += amount
                
                if paid:
                    collected_amount += amount
                    collected_count += 1
                    if fee_type in type_amounts:
                        type_amounts[fee_type] += amount
                else:
                    pending_amount += amount
                    pending_count += 1
            
            # تحديث الملصقات الرئيسية
            self.total_amount_value.setText(f"{total_amount:,.0f} د.ع")
            self.collected_value.setText(f"{collected_amount:,.0f} د.ع")
            self.pending_summary_value.setText(f"{pending_amount:,.0f} د.ع")
            
            # تحديث ملصقات الرأس
            self.total_fees_label.setText(f"إجمالي الرسوم: {len(self.current_fees)}")
            self.collected_amount_label.setText(f"المحصل: {collected_amount:,.0f} د.ع")
            self.pending_fees_label.setText(f"المستحق: {pending_amount:,.0f} د.ع")
            
            # تحديث الإحصائيات حسب النوع
            self.registration_fees_label.setText(f"رسوم تسجيل: {type_amounts['رسوم التسجيل']:,.0f} د.ع")
            self.uniform_fees_label.setText(f"الزي المدرسي: {type_amounts['الزي المدرسي']:,.0f} د.ع")
            self.books_fees_label.setText(f"الكتب: {type_amounts['الكتب']:,.0f} د.ع")
            self.stationery_fees_label.setText(f"القرطاسية: {type_amounts['القرطاسية']:,.0f} د.ع")
            self.custom_fees_label.setText(f"رسم مخصص: {type_amounts['رسم مخصص']:,.0f} د.ع")

            # تحديث الإحصائيات الأخرى
            self.pending_count_label.setText(f"الرسوم غير المدفوعة: {pending_count}")
            self.collected_count_label.setText(f"الرسوم المدفوعة: {collected_count}")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث ملخص الرسوم: {e}")
    
    def apply_filters(self):
        """تطبيق الفلاتر وإعادة تحميل البيانات"""
        try:
            self.load_fees()
            
        except Exception as e:
            logging.error(f"خطأ في تطبيق الفلاتر: {e}")
    
    def refresh(self):
        """تحديث البيانات"""
        try:
            log_user_action("تحديث صفحة الرسوم الإضافية")
            self.load_fees()
            
        except Exception as e:
            logging.error(f"خطأ في تحديث صفحة الرسوم الإضافية: {e}")
    
    def clear_filters(self):
        """مسح جميع الفلاتر وإعادة تعيينها إلى الوضع الافتراضي"""
        try:
            self.school_combo.setCurrentIndex(0) # "جميع المدارس"
            self.student_combo.setCurrentIndex(0) # "جميع الطلاب"
            self.fee_type_combo.setCurrentIndex(0) # "جميع الأنواع"
            self.status_combo.setCurrentIndex(0) # "الكل"
            self.search_input.clear()
            self.apply_filters()
            log_user_action("مسح فلاتر صفحة الرسوم الإضافية")
        except Exception as e:
            logging.error(f"خطأ في مسح الفلاتر: {e}")
    
    def show_context_menu(self, position):
        """عرض قائمة السياق للجدول - تم تعطيلها"""
        # تم تعطيل قائمة السياق بناء على الطلب
        pass
    
    def export_fees(self):
        """تصدير تقرير الرسوم"""
        try:
            self.show_info_message("قيد التطوير", "ميزة تصدير تقرير الرسوم قيد التطوير")
            log_user_action("طلب تصدير تقرير الرسوم")
            
        except Exception as e:
            logging.error(f"خطأ في تصدير التقرير: {e}")
    
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
            # استخدام خط Cairo المحمل
            cairo_font = f"'{self.cairo_family}', 'Cairo', 'Segoe UI', Tahoma, Arial"
            
            style = """
                /* الإطار الرئيسي */
                QWidget {{
                    background-color: #F8F9FA;
                    font-family: {font_family};
                    font-size: 16px;
                }}
                
                /* رأس الصفحة */
                #headerFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #2E86AB, stop:1 #A23B72);
                    border-radius: 10px;
                    color: white;
                    margin-bottom: 10px;
                }}
                
                #pageTitle {{
                    font-size: 18px;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 5px;
                    font-family: {font_family};
                }}
                
                #pageDesc {{
                    font-size: 16px;
                    color: #E8DAEF;
                    font-family: {font_family};
                }}
                
                /* شريط الأدوات */
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
                
                #filterCombo {{
                    padding: 6px 10px;
                    border: 1px solid #BDC3C7;
                    border-radius: 4px;
                    background-color: white;
                    min-width: 100px;
                    font-size: 16px;
                    font-family: {font_family};
                }}
                
                /* الأزرار */
                #primaryButton {{
                    background-color: #9B59B6;
                    border: 2px solid #8E44AD;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 16px;
                    font-family: {font_family};
                }}
                
                #secondaryButton {{
                    background-color: #3498DB;
                    border: 2px solid #2980B9;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 16px;
                    font-family: {font_family};
                }}
                
                /* الجدول */
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
                    font-family: {font_family};
                }}

                QTableWidget::item:selected {{
                    background-color: #2E86AB;
                    color: white;
                }}
                
                QHeaderView::section {{
                    background-color: #9B59B6;
                    color: white;
                    padding: 12px;
                    border: none;
                    font-weight: bold;
                    font-size: 16px;
                    font-family: {font_family};
                }}
            """.format(font_family=cairo_font)
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الستايل: {e}")
    
    def add_fee(self):
        """إضافة رسم إضافي جديد"""
        try:
            log_user_action("إضافة رسم إضافي جديد")
            dialog = AddAdditionalFeeDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                fee_type = dialog.fee_name_edit.text().strip()
                default_amount = dialog.amount_spin.value()
                description = dialog.description_edit.toPlainText().strip()
                
                if not fee_type:
                    QMessageBox.warning(self, "تحذير", "يرجى إدخال نوع الرسم")
                    return
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                try:
                    cursor.execute("""
                        INSERT INTO additional_fees (fee_type, default_amount, description)
                        VALUES (?, ?, ?)
                    """, (fee_type, default_amount, description))
                    
                    conn.commit()
                    QMessageBox.information(self, "نجح", "تم إضافة الرسم بنجاح")
                    self.load_fees()
                    
                except sqlite3.Error as e:
                    QMessageBox.critical(self, "خطأ", f"فشل في إضافة الرسم: {e}")
                finally:
                    conn.close()
                    
        except Exception as e:
            logging.error(f"خطأ في إضافة رسم إضافي: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {e}")

    def edit_fee(self):
        """تعديل رسم إضافي"""
        current_row = self.fees_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار رسم للتعديل")
            return
            
        try:
            log_user_action("تعديل رسم إضافي")
            fee_id = int(self.fees_table.item(current_row, 0).text())
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM additional_fees WHERE id = ?", (fee_id,))
            fee_data = cursor.fetchone()
            
            if not fee_data:
                QMessageBox.warning(self, "تحذير", "لم يتم العثور على الرسم")
                return
                
            dialog = AddAdditionalFeeDialog(self)
            dialog.setWindowTitle("تعديل رسم إضافي")
            dialog.fee_name_edit.setText(fee_data[1])
            dialog.amount_spin.setValue(fee_data[2])
            dialog.description_edit.setPlainText(fee_data[3] or "")
            
            if dialog.exec_() == QDialog.Accepted:
                fee_type = dialog.fee_name_edit.text().strip()
                default_amount = dialog.amount_spin.value()
                description = dialog.description_edit.toPlainText().strip()
                
                if not fee_type:
                    QMessageBox.warning(self, "تحذير", "يرجى إدخال نوع الرسم")
                    return
                
                try:
                    cursor.execute("""
                        UPDATE additional_fees 
                        SET fee_type = ?, default_amount = ?, description = ?
                        WHERE id = ?
                    """, (fee_type, default_amount, description, fee_id))
                    
                    conn.commit()
                    QMessageBox.information(self, "نجح", "تم تعديل الرسم بنجاح")
                    self.load_fees()
                    
                except sqlite3.Error as e:
                    QMessageBox.critical(self, "خطأ", f"فشل في تعديل الرسم: {e}")
                finally:
                    conn.close()
                    
        except Exception as e:
            logging.error(f"خطأ في تعديل رسم إضافي: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {e}")

    def delete_fee(self):
        """حذف رسم إضافي"""
        current_row = self.fees_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار رسم للحذف")
            return
            
        try:
            log_user_action("حذف رسم إضافي")
            fee_id = int(self.fees_table.item(current_row, 0).text())
            fee_type = self.fees_table.item(current_row, 1).text()
            
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                f"هل أنت متأكد من حذف الرسم '{fee_type}'؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                try:
                    cursor.execute("DELETE FROM additional_fees WHERE id = ?", (fee_id,))
                    conn.commit()
                    QMessageBox.information(self, "نجح", "تم حذف الرسم بنجاح")
                    self.load_fees()
                    
                except sqlite3.Error as e:
                    QMessageBox.critical(self, "خطأ", f"فشل في حذف الرسم: {e}")
                finally:
                    conn.close()
                    
        except Exception as e:
            logging.error(f"خطأ في حذف رسم إضافي: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {e}")

    def assign_fees_to_students(self):
        """تعيين رسوم للطلاب"""
        try:
            log_user_action("تعيين رسوم للطلاب")
            # dialog = AssignFeesDialog(self)  # هذا سيتم إضافته لاحقاً
            # dialog.exec_()
            QMessageBox.information(self, "معلومات", "ميزة تعيين الرسوم للطلاب ستكون متاحة قريباً")
            
        except Exception as e:
            logging.error(f"خطأ في تعيين رسوم للطلاب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {e}")

    def refresh_data(self):
        """تحديث البيانات"""
        try:
            log_user_action("تحديث بيانات الرسوم الإضافية")
            self.load_fees()
            
        except Exception as e:
            logging.error(f"خطأ في تحديث بيانات الرسوم الإضافية: {e}")

