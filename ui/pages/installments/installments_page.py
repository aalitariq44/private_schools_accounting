#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة الأقساط
"""

import logging
import json
from datetime import datetime, date
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QMenu, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QProgressBar, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon, QFontDatabase

import config
from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation

# استيراد وحدة أحجام الخطوط
from ...font_sizes import FontSizeManager
from ...ui_settings_manager import ui_settings_manager




class InstallmentsPage(QWidget):
    """صفحة إدارة الأقساط"""
    
    # إشارات النافذة
    page_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_installments = []
        self.selected_school_id = None
        self.selected_student_id = None
        
        # الحصول على حجم الخط المحفوظ من إعدادات UI
        self.current_font_size = ui_settings_manager.get_font_size("installments")
        
        # قراءة إعدادات رؤية الإحصائيات
        self.statistics_visible = ui_settings_manager.get_statistics_visible("installments")
        
        # تحميل وتطبيق خط Cairo
        self.setup_cairo_font()
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_initial_data()
        
        log_user_action("فتح صفحة إدارة الأقساط")
    
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
            # تقليل الهوامش والمسافات لتناسب الشاشات الصغيرة (1366x768)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(8)
            
            # شريط الأدوات والفلاتر
            self.create_toolbar(layout)
            
            # جدول الأقساط
            self.create_installments_table(layout)
            
            # إحصائيات وملخص مالي
            self.create_financial_summary(layout)
            
            self.setLayout(layout)
            
            # تحديث القائمة المنسدلة لحجم الخط
            self.update_font_size_combo()
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة الأقساط: {e}")
            raise
    
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
            
            # أزرار العمليات في الشريط الأول
            self.generate_report_button = QPushButton("تقرير مالي")
            self.generate_report_button.setObjectName("secondaryButton")
            filters_layout.addWidget(self.generate_report_button)
            
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("secondaryButton")
            filters_layout.addWidget(self.refresh_button)
            
            self.clear_filters_button = QPushButton("مسح الفلاتر")
            self.clear_filters_button.setObjectName("secondaryButton")
            filters_layout.addWidget(self.clear_filters_button)
            
            filters_layout.addStretch()
            
            toolbar_layout.addLayout(filters_layout)
            
            # الصف الثاني - فلاتر التاريخ والعمليات
            actions_layout = QHBoxLayout()
            actions_layout.setSpacing(6)
            
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
            
            # زر تبديل رؤية الإحصائيات
            self.toggle_stats_button = QPushButton("إخفاء الإحصائيات" if self.statistics_visible else "إظهار الإحصائيات")
            self.toggle_stats_button.setObjectName("secondaryButton")
            self.toggle_stats_button.clicked.connect(self.toggle_statistics_visibility)
            actions_layout.addWidget(self.toggle_stats_button)
            
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
                "رقم الوصل", "الطالب", "المدرسة", "المبلغ",
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
            header.resizeSection(0, 80)   # رقم الوصل
            header.resizeSection(1, 160)  # الطالب
            header.resizeSection(2, 130)  # المدرسة
            header.resizeSection(3, 120)  # المبلغ
            header.resizeSection(4, 110)  # تاريخ الدفع
            header.resizeSection(5, 110)  # وقت الدفع
            header.resizeSection(6, 200)  # ملاحظات
            
            # إخفاء العمود الأول (المعرف) - تم تغيير المعرف إلى رقم الوصل، لذا لا داعي لإخفائه
            # self.installments_table.setColumnHidden(0, True)
            
            # ربط الأحداث
            
            self.installments_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.installments_table.customContextMenuRequested.connect(self.show_context_menu)
            # Remove extra padding to match row height of students table
            self.installments_table.setStyleSheet("QTableWidget::item { padding: 2px; }")
            
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
            self.summary_frame = summary_frame  # إضافة هذا السطر لتعيين الخاصية
            
            summary_layout = QHBoxLayout(summary_frame)
            summary_layout.setContentsMargins(8, 6, 8, 6)
            
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
            
            # تطبيق حالة الرؤية
            self.summary_frame.setVisible(self.statistics_visible)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الملخص المالي: {e}")
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            # ربط أزرار العمليات
            self.generate_report_button.clicked.connect(self.generate_report)
            self.refresh_button.clicked.connect(self.refresh)
            self.clear_filters_button.clicked.connect(self.clear_filters)
            
            # ربط الفلاتر
            # ربط فلتر المدرسة والطالب باستخدام currentIndexChanged لالتقاط التغيير بشكل موثوق
            self.school_combo.currentIndexChanged.connect(self.on_school_changed)
            self.student_combo.currentIndexChanged.connect(self.apply_filters)
            self.due_date_from.dateChanged.connect(self.apply_filters)
            self.due_date_to.dateChanged.connect(self.apply_filters)
            
            # ربط تغيير حجم الخط
            self.font_size_combo.currentTextChanged.connect(self.change_font_size)
            
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
                # رقم الوصل (id)
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
    
    def clear_filters(self):
        """مسح جميع الفلاتر وإعادة تعيينها إلى الوضع الافتراضي"""
        try:
            self.school_combo.setCurrentIndex(0) # "جميع المدارس"
            self.student_combo.setCurrentIndex(0) # "جميع الطلاب"
            self.due_date_from.setDate(QDate.currentDate().addDays(-30))
            self.due_date_to.setDate(QDate.currentDate().addDays(30))
            self.apply_filters()
            log_user_action("مسح فلاتر صفحة الأقساط")
        except Exception as e:
            logging.error(f"خطأ في مسح الفلاتر: {e}")
    
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
            print(f"DEBUG: إعداد التنسيقات لحجم الخط: {self.current_font_size}")

            # استخدام FontSizeManager لإنشاء CSS
            style = FontSizeManager.generate_css_styles(self.current_font_size)
            print(f"DEBUG: طول CSS المولد: {len(style)}")

            # تطبيق التنسيقات على الصفحة
            self.setStyleSheet(style)

            # إجبار إعادة رسم جميع المكونات
            self.update()
            if hasattr(self, 'installments_table'):
                self.installments_table.update()
            if hasattr(self, 'summary_frame'):
                self.summary_frame.update()

            print("DEBUG: تم تطبيق التنسيقات بنجاح")

        except Exception as e:
            logging.error(f"خطأ في إعداد الستايل: {e}")
            print(f"DEBUG: خطأ في إعداد الستايل: {e}")
    
    def change_font_size(self):
        """تغيير حجم الخط في الصفحة"""
        try:
            selected_size = self.font_size_combo.currentText()
            print(f"DEBUG: تغيير حجم الخط من {self.current_font_size} إلى {selected_size}")

            if selected_size != self.current_font_size:
                self.current_font_size = selected_size

                # إعادة إعداد التنسيقات
                self.setup_styles()

                # حفظ حجم الخط الجديد في إعدادات UI
                success = ui_settings_manager.set_font_size("installments", selected_size)
                print(f"DEBUG: حفظ حجم الخط: {'نجح' if success else 'فشل'}")

                log_user_action(f"تغيير حجم الخط إلى: {selected_size}")

                # إجبار إعادة رسم الصفحة
                self.update()

                # تحديث القائمة المنسدلة
                self.update_font_size_combo()

        except Exception as e:
            logging.error(f"خطأ في تغيير حجم الخط: {e}")
            print(f"DEBUG: خطأ في تغيير حجم الخط: {e}")
    
    def update_font_size_combo(self):
        """تحديث القائمة المنسدلة لحجم الخط"""
        try:
            if hasattr(self, 'font_size_combo'):
                self.font_size_combo.blockSignals(True)  # منع إرسال الإشارات أثناء التحديث
                self.font_size_combo.setCurrentText(self.current_font_size)
                self.font_size_combo.blockSignals(False)  # إعادة تفعيل الإشارات
                print(f"DEBUG: تم تحديث القائمة المنسدلة إلى: {self.current_font_size}")
        except Exception as e:
            logging.error(f"خطأ في تحديث القائمة المنسدلة: {e}")
            print(f"DEBUG: خطأ في تحديث القائمة المنسدلة: {e}")
    
    def toggle_statistics_visibility(self):
        """تبديل رؤية نافذة الإحصائيات"""
        try:
            # تبديل حالة الرؤية
            self.statistics_visible = not self.statistics_visible
            
            # تطبيق التغيير على الواجهة
            if hasattr(self, 'summary_frame'):
                self.summary_frame.setVisible(self.statistics_visible)
            
            # تحديث نص الزر
            if hasattr(self, 'toggle_stats_button'):
                if self.statistics_visible:
                    self.toggle_stats_button.setText("إخفاء الإحصائيات")
                else:
                    self.toggle_stats_button.setText("إظهار الإحصائيات")
            
            # حفظ الإعداد الجديد
            success = ui_settings_manager.set_statistics_visible("installments", self.statistics_visible)
            print(f"DEBUG: حفظ حالة رؤية الإحصائيات: {'نجح' if success else 'فشل'}")
            
            log_user_action(f"تبديل رؤية الإحصائيات إلى: {'مرئي' if self.statistics_visible else 'مخفي'}")
            
        except Exception as e:
            logging.error(f"خطأ في تبديل رؤية الإحصائيات: {e}")
            print(f"DEBUG: خطأ في تبديل رؤية الإحصائيات: {e}")

    def add_installment(self):
        """إضافة قسط جديد"""
        try:
            log_user_action("إضافة قسط جديد")
            
        except Exception as e:
            logging.error(f"خطأ في إضافة قسط: {e}")
