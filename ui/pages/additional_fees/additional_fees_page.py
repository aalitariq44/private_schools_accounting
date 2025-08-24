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
    QCheckBox, QTextEdit, QAction, QDialog, QFileDialog
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
            # تقليل الهوامش والمسافات لتناسب دقة 1366x768
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(8)
            
            # العنوان الرئيسي
            self.create_page_header(layout)
            
            # شريط الأدوات والفلاتر
            self.create_toolbar(layout)
            
            # جدول الرسوم الإضافية
            self.create_fees_table(layout)
            
            # إنشاء عناصر الملخص (لكن سنخفيها لإتاحة مساحة أكبر كما طلب المستخدم)
            self.create_summary(layout)
            if hasattr(self, 'summary_frame'):
                self.summary_frame.setVisible(False)
            
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
            header_layout.setContentsMargins(10, 8, 10, 8)
            
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
            
            # زر إحصائيات مفصلة بدلاً من الإحصائيات الظاهرة الدائمة لتوفير مساحة
            self.detailed_stats_button = QPushButton("احصائيات مفصلة")
            self.detailed_stats_button.setObjectName("secondaryButton")
            header_layout.addWidget(self.detailed_stats_button)
            
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
            actions_layout.setSpacing(6)
            
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
            self.fees_table.setStyleSheet("QTableWidget::item { padding: 2px; }")
            
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
            # تخزين المرجع حتى نتمكن من إخفائه لاحقاً
            self.summary_frame = summary_frame
            
            summary_layout = QHBoxLayout(summary_frame)
            summary_layout.setContentsMargins(8, 6, 8, 6)
            
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
            
            # لا نضيف الإطار إلى التخطيط الرئيسي لتوفير المساحة على الصفحة
            # layout.addWidget(summary_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء ملخص الرسوم: {e}")
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            # ربط أزرار العمليات
            self.export_fees_button.clicked.connect(self.export_fees)
            self.refresh_button.clicked.connect(self.refresh)
            self.clear_filters_button.clicked.connect(self.clear_filters)
            if hasattr(self, 'detailed_stats_button'):
                self.detailed_stats_button.clicked.connect(self.show_detailed_stats)
            
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
            
            # فلتر نوع الرسم (مع دعم الرسوم المخصصة)
            selected_fee_type = self.fee_type_combo.currentText()
            if selected_fee_type and selected_fee_type != "جميع الأنواع":
                # عند اختيار الرسوم المخصصة، عرض أي نوع رسم غير الأنواع الافتراضية
                if selected_fee_type == "رسم مخصص":
                    # استبعاد الأنواع الافتراضية
                    default_types = ['رسوم التسجيل', 'الزي المدرسي', 'الكتب', 'القرطاسية']
                    placeholders = ','.join('?' for _ in default_types)
                    query += f" AND af.fee_type NOT IN ({placeholders})"
                    params.extend(default_types)
                else:
                    # أنواع الرسم المحددة
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
            stats = self.compute_stats()
            # تحديث الملصقات إذا كانت موجودة (قد تكون مخفية)
            if hasattr(self, 'total_amount_value'):
                self.total_amount_value.setText(f"{stats['total_amount']:,.0f} د.ع")
            if hasattr(self, 'collected_value'):
                self.collected_value.setText(f"{stats['collected_amount']:,.0f} د.ع")
            if hasattr(self, 'pending_summary_value'):
                self.pending_summary_value.setText(f"{stats['pending_amount']:,.0f} د.ع")
            if hasattr(self, 'total_fees_label'):
                self.total_fees_label.setText(f"إجمالي الرسوم: {stats['fees_count']}")
            if hasattr(self, 'collected_amount_label'):
                self.collected_amount_label.setText(f"المحصل: {stats['collected_amount']:,.0f} د.ع")
            if hasattr(self, 'pending_fees_label'):
                self.pending_fees_label.setText(f"المستحق: {stats['pending_amount']:,.0f} د.ع")
            if hasattr(self, 'registration_fees_label'):
                self.registration_fees_label.setText(f"رسوم تسجيل: {stats['type_amounts']['رسوم التسجيل']:,.0f} د.ع")
            if hasattr(self, 'uniform_fees_label'):
                self.uniform_fees_label.setText(f"الزي المدرسي: {stats['type_amounts']['الزي المدرسي']:,.0f} د.ع")
            if hasattr(self, 'books_fees_label'):
                self.books_fees_label.setText(f"الكتب: {stats['type_amounts']['الكتب']:,.0f} د.ع")
            if hasattr(self, 'stationery_fees_label'):
                self.stationery_fees_label.setText(f"القرطاسية: {stats['type_amounts']['القرطاسية']:,.0f} د.ع")
            if hasattr(self, 'custom_fees_label'):
                self.custom_fees_label.setText(f"رسم مخصص: {stats['type_amounts']['رسم مخصص']:,.0f} د.ع")
            if hasattr(self, 'pending_count_label'):
                self.pending_count_label.setText(f"الرسوم غير المدفوعة: {stats['pending_count']}")
            if hasattr(self, 'collected_count_label'):
                self.collected_count_label.setText(f"الرسوم المدفوعة: {stats['collected_count']}")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث ملخص الرسوم: {e}")

    def compute_stats(self):
        """حساب الإحصائيات وتجميعها في قاموس لإعادة الاستخدام"""
        total_amount = 0
        collected_amount = 0
        pending_amount = 0
        pending_count = 0
        collected_count = 0
        amounts_list = []

        type_amounts = {
            "رسوم التسجيل": 0,
            "الزي المدرسي": 0,
            "الكتب": 0,
            "القرطاسية": 0,
            "رسم مخصص": 0
        }

        for fee in self.current_fees:
            amount = fee[4] or 0
            paid = fee[5]
            fee_type = fee[3] or ""
            amounts_list.append(amount)
            total_amount += amount
            if paid:
                collected_amount += amount
                collected_count += 1
                if fee_type in type_amounts:
                    type_amounts[fee_type] += amount
            else:
                pending_amount += amount
                pending_count += 1

        avg_amount = (total_amount / len(self.current_fees)) if self.current_fees else 0
        max_amount = max(amounts_list) if amounts_list else 0
        min_amount = min(amounts_list) if amounts_list else 0

        stats = {
            'total_amount': total_amount,
            'collected_amount': collected_amount,
            'pending_amount': pending_amount,
            'pending_count': pending_count,
            'collected_count': collected_count,
            'fees_count': len(self.current_fees),
            'type_amounts': type_amounts,
            'avg_amount': avg_amount,
            'max_amount': max_amount,
            'min_amount': min_amount
        }
        self.stats_data = stats
        return stats

    def show_detailed_stats(self):
        """عرض نافذة منبثقة تحتوي على جميع الإحصائيات بالتفصيل"""
        try:
            stats = self.compute_stats()
            dialog = QDialog(self)
            dialog.setWindowTitle("الإحصائيات التفصيلية للرسوم الإضافية")
            dialog.resize(450, 520)
            layout = QVBoxLayout(dialog)

            # عنوان
            title = QLabel("ملخص تفصيلي")
            title.setStyleSheet("font-weight:700;font-size:14px;margin-bottom:4px;")
            layout.addWidget(title)

            # أرقام عامة
            general = QTextEdit()
            general.setReadOnly(True)
            general.setStyleSheet("background:#FAFAFA;border:1px solid #DDD;font-family:'{}';font-size:12px;".format(self.cairo_family))
            lines = []
            lines.append(f"عدد السجلات: {stats['fees_count']}")
            lines.append(f"إجمالي المبالغ: {stats['total_amount']:,.0f} د.ع")
            lines.append(f"المبالغ المحصلة: {stats['collected_amount']:,.0f} د.ع")
            lines.append(f"المبالغ المستحقة: {stats['pending_amount']:,.0f} د.ع")
            lines.append(f"عدد الرسوم المدفوعة: {stats['collected_count']}")
            lines.append(f"عدد الرسوم غير المدفوعة: {stats['pending_count']}")
            lines.append("")
            lines.append(f"متوسط المبلغ: {stats['avg_amount']:,.2f} د.ع")
            lines.append(f"أعلى مبلغ: {stats['max_amount']:,.0f} د.ع")
            lines.append(f"أقل مبلغ: {stats['min_amount']:,.0f} د.ع")
            lines.append("")
            lines.append("إجمالي حسب النوع (مدفوع):")
            for t, val in stats['type_amounts'].items():
                lines.append(f" - {t}: {val:,.0f} د.ع")
            general.setPlainText("\n".join(lines))
            layout.addWidget(general)

            close_btn = QPushButton("إغلاق")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn, alignment=Qt.AlignRight)

            dialog.exec_()
        except Exception as e:
            logging.error(f"خطأ في عرض الإحصائيات التفصيلية: {e}")

    
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
        """عرض قائمة السياق للجدول لتحويل الحالة بين مدفوع وغير مدفوع"""
        index = self.fees_table.indexAt(position)
        row = index.row()
        if row < 0:
            return
        fee = self.current_fees[row]
        fee_id = fee[0]
        paid = fee[5]
        # only allow marking unpaid fees as paid
        if paid:
            return
        menu = QMenu(self)
        mark_action = QAction("تعيين كمدفوع", self)
        mark_action.triggered.connect(lambda _, fid=fee_id: self.change_payment_status(fid, True))
        menu.addAction(mark_action)
        menu.exec_(self.fees_table.viewport().mapToGlobal(position))
    
    def change_payment_status(self, fee_id, paid):
        """تغيير حالة الدفع لرسم إضافي بعد التأكيد"""
        action = "مدفوع" if paid else "غير مدفوع"
        reply = QMessageBox.question(
            self, "تأكيد",
            f"هل أنت متأكد من تعيين الرسم #{fee_id} ك{action}؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            if paid:
                payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    "UPDATE additional_fees SET paid = 1, payment_date = ? WHERE id = ?",
                    (payment_date, fee_id)
                )
            else:
                cursor.execute(
                    "UPDATE additional_fees SET paid = 0, payment_date = NULL WHERE id = ?",
                    (fee_id,)
                )
            conn.commit()
            QMessageBox.information(self, "نجح", f"تم تحديث حالة الدفع بنجاح إلى {action}")
            self.load_fees()
        except Exception as e:
            logging.error(f"خطأ في تغيير حالة الدفع: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تغيير حالة الدفع: {e}")
        finally:
            conn.close()
    
    def export_fees(self):
        """تصدير تقرير الرسوم"""
        try:
            from datetime import datetime
            import csv
            import os
            
            if not self.current_fees:
                QMessageBox.warning(self, "تحذير", "لا توجد بيانات للتصدير")
                return
            
            # تحديد اسم الملف الافتراضي
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"Additional_Fees_Report_{timestamp}.csv"
            
            # فتح نافذة حفظ الملف
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "حفظ تقرير الرسوم الإضافية",
                default_filename,
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if not filename:
                return  # المستخدم ألغى العملية
            
            # التأكد من امتداد الملف
            if not filename.lower().endswith('.csv'):
                filename += '.csv'
            
            # حساب الإحصائيات
            total_amount = sum(fee[4] or 0 for fee in self.current_fees)
            paid_fees = [fee for fee in self.current_fees if fee[5]]  # الرسوم المدفوعة
            unpaid_fees = [fee for fee in self.current_fees if not fee[5]]  # الرسوم غير المدفوعة
            total_paid = sum(fee[4] or 0 for fee in paid_fees)
            total_unpaid = sum(fee[4] or 0 for fee in unpaid_fees)
            
            # إنشاء التقرير بتنسيق محسن للـ Excel
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                
                # كتابة معلومات التقرير
                writer.writerow([f"تقرير الرسوم الإضافية - {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
                writer.writerow([f"إجمالي عدد الرسوم: {len(self.current_fees)}"])
                writer.writerow([f"إجمالي المبلغ: {total_amount:,.2f} د.ع"])
                writer.writerow([f"المبلغ المدفوع: {total_paid:,.2f} د.ع"])
                writer.writerow([f"المبلغ المتبقي: {total_unpaid:,.2f} د.ع"])
                writer.writerow([])  # سطر فارغ
                
                # كتابة رأس الجدول
                headers = ["ID", "Student Name", "School", "Fee Type", "Amount (IQD)", "Status", "Payment Date", "Notes", "Created Date"]
                writer.writerow(headers)
                
                # كتابة البيانات
                for fee in self.current_fees:
                    # (id, student_name, school_name, fee_type, amount, paid, payment_date, notes, created_at)
                    row = [
                        fee[0] or '',  # ID
                        fee[1] or '',  # Student Name
                        fee[2] or 'General',  # School
                        fee[3] or '',  # Fee Type
                        f"{fee[4] or 0:,.2f}",  # Amount
                        "Paid" if fee[5] else "Unpaid",  # Status
                        fee[6] or '',  # Payment Date
                        fee[7] or '',  # Notes
                        fee[8] or ''   # Created Date
                    ]
                    writer.writerow(row)
                
                # إضافة إحصائيات في النهاية
                writer.writerow([])  # سطر فارغ
                writer.writerow(['Statistics:'])
                writer.writerow(['Total Records:', len(self.current_fees)])
                writer.writerow(['Total Amount:', f"{total_amount:,.2f} IQD"])
                writer.writerow(['Paid Amount:', f"{total_paid:,.2f} IQD"])
                writer.writerow(['Unpaid Amount:', f"{total_unpaid:,.2f} IQD"])
                writer.writerow(['Paid Fees Count:', len(paid_fees)])
                writer.writerow(['Unpaid Fees Count:', len(unpaid_fees)])
                if self.current_fees:
                    avg_amount = total_amount / len(self.current_fees)
                    writer.writerow(['Average Amount:', f"{avg_amount:,.2f} IQD"])
                    amounts = [fee[4] or 0 for fee in self.current_fees]
                    writer.writerow(['Max Amount:', f"{max(amounts):,.2f} IQD"])
                    writer.writerow(['Min Amount:', f"{min(amounts):,.2f} IQD"])
            
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
            
            log_user_action("تصدير تقرير الرسوم الإضافية", "نجح")
            
        except Exception as e:
            logging.error(f"خطأ في تصدير التقرير: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تصدير التقرير:\n{str(e)}")
    
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
            
            # تصميم مبسط متوافق مع الشاشات الصغيرة – إزالة التدرجات، تقليل الأحجام
            style = """
                QWidget {{
                    background-color: #F5F6F7;
                    font-family: {font_family};
                    font-size: 13px;
                }}

                /* رأس الصفحة مبسط */
                #headerFrame {{
                    background: #FFFFFF;
                    border: 1px solid #DDE1E4;
                    border-radius: 4px;
                    margin-bottom: 6px;
                }}
                #pageTitle {{
                    font-size: 14px;
                    font-weight: 700;
                    color: #37474F;
                    margin: 0;
                }}
                #pageDesc {{
                    font-size: 11px;
                    color: #607D8B;
                    margin-top: 2px;
                }}
                #quickStat {{
                    background: #F0F3F5;
                    color: #37474F;
                    border: 1px solid #D0D5D8;
                    padding: 4px 10px;
                    border-radius: 14px;
                    font-size: 11px;
                    font-weight: 600;
                }}

                /* إطارات عامة */
                #toolbarFrame, #summaryFrame, #tableFrame {{
                    background: #FFFFFF;
                    border: 1px solid #DDE1E4;
                    border-radius: 4px;
                }}

                #filterLabel {{
                    font-weight: 600;
                    color: #37474F;
                    margin-right: 4px;
                    font-size: 12px;
                }}
                #filterCombo, #searchInput {{
                    padding: 4px 6px;
                    border: 1px solid #C3C7CA;
                    border-radius: 3px;
                    background: #FFFFFF;
                    min-width: 90px;
                    font-size: 12px;
                }}
                #searchInput {{
                    border-radius: 14px;
                    padding: 4px 10px;
                }}
                #searchInput:focus, #filterCombo:focus {{
                    border: 1px solid #5B8DEF;
                }}

                /* الأزرار المسطحة */
                #primaryButton, #secondaryButton {{
                    background: #FFFFFF;
                    color: #2F3A40;
                    border: 1px solid #B5BCC0;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: 600;
                    font-size: 12px;
                }}
                #primaryButton:hover, #secondaryButton:hover {{
                    background: #F0F3F5;
                }}
                #primaryButton:pressed, #secondaryButton:pressed {{
                    background: #E2E6E9;
                }}
                #secondaryButton {{ border-color: #2980B9; color: #1F5375; }}

                /* الجدول */
                QTableWidget {{
                    background: #FFFFFF;
                    border: 1px solid #DDE1E4;
                    gridline-color: #E3E6E8;
                    font-size: 12px;
                }}
                QTableWidget::item {{
                    border-bottom: 1px solid #EEF0F1;
                }}
                QTableWidget::item:selected {{
                    background: #5B8DEF;
                    color: #FFFFFF;
                }}
                QHeaderView::section {{
                    background: #ECEFF1;
                    color: #37474F;
                    padding: 4px 6px;
                    border: 1px solid #D0D5D8;
                    font-weight: 600;
                    font-size: 12px;
                }}

                /* الملخص */
                #summaryTitle {{
                    font-size: 13px;
                    font-weight: 600;
                    color: #37474F;
                }}
                #summaryLabel {{
                    font-size: 11px;
                    color: #455A64;
                }}
                #summaryValue, #summaryValueSuccess, #summaryValueWarning {{
                    font-size: 14px;
                    font-weight: 700;
                    padding: 2px 4px;
                }}
                #summaryValueSuccess { color: #1B5E20; }
                #summaryValueWarning { color: #B35C00; }
                #statLabel {{
                    font-size: 11px;
                    color: #546E7A;
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

