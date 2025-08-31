#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة المعلمين
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

# استيراد وحدة أحجام الخطوط
from ...font_sizes import FontSizeManager
from ...ui_settings_manager import ui_settings_manager

# استيراد نوافذ إدارة المعلمين
from .add_teacher_dialog import AddTeacherDialog
from .edit_teacher_dialog import EditTeacherDialog
from ..shared.salary_details_dialog import SalaryDetailsDialog


class TeachersPage(QWidget):
    """صفحة إدارة المعلمين"""
    
    # إشارات النافذة
    page_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_teachers = []
        self.selected_school_id = None
        
        # الحصول على حجم الخط المحفوظ من إعدادات UI
        self.current_font_size = ui_settings_manager.get_font_size("teachers")
        
        # الحصول على حالة رؤية نافذة الإحصائيات
        self.statistics_visible = ui_settings_manager.get_statistics_visible("teachers")
        
        self.setup_cairo_font()
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_schools()
        
        log_user_action("فتح صفحة إدارة المعلمين")

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
            # التخطيط الرئيسي
            layout = QVBoxLayout()
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(8)
            
            # شريط الأدوات والفلاتر
            self.create_toolbar(layout)
            
            # جدول المعلمين
            self.create_teachers_table(layout)
            
            # ملخص المعلمين
            self.create_summary(layout)
            
            self.setLayout(layout)
            
            # تحديث القائمة المنسدلة لحجم الخط
            self.update_font_size_combo()
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة المعلمين: {e}")
            raise
    
    def create_teachers_table(self, layout):
        """إنشاء جدول المعلمين"""
        try:
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")

            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)

            self.teachers_table = QTableWidget()
            self.teachers_table.setObjectName("dataTable")

            columns = ["المعرف", "الاسم", "المدرسة", "عدد الحصص", "الراتب الشهري", "رقم الهاتف", "ملاحظات"]
            self.teachers_table.setColumnCount(len(columns))
            self.teachers_table.setHorizontalHeaderLabels(columns)

            self.teachers_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.teachers_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.teachers_table.setAlternatingRowColors(True)
            self.teachers_table.setSortingEnabled(True)

            header = self.teachers_table.horizontalHeader()
            header.setStretchLastSection(True)
            for i in range(len(columns)):
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

            self.teachers_table.setStyleSheet("QTableWidget::item { padding: 0px; }")
            # إخفاء عمود المعرف من العرض
            self.teachers_table.setColumnHidden(0, True)

            self.teachers_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.teachers_table.customContextMenuRequested.connect(self.show_context_menu)
            self.teachers_table.doubleClicked.connect(self.show_teacher_details)

            table_layout.addWidget(self.teachers_table)
            layout.addWidget(table_frame)

        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول المعلمين: {e}")
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
            self.school_combo.setMinimumWidth(200)
            filters_layout.addWidget(self.school_combo)
            
            filters_layout.addStretch()
            
            toolbar_layout.addLayout(filters_layout)
            
            actions_layout = QHBoxLayout()
            
            search_label = QLabel("البحث:")
            search_label.setObjectName("filterLabel")
            actions_layout.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setObjectName("searchInput")
            self.search_input.setPlaceholderText("ابحث في أسماء المعلمين...")
            self.search_input.setMinimumWidth(300)
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
            
            # زر تبديل رؤية الإحصائيات
            self.toggle_stats_button = QPushButton("إخفاء الإحصائيات" if self.statistics_visible else "إظهار الإحصائيات")
            self.toggle_stats_button.setObjectName("secondaryButton")
            self.toggle_stats_button.clicked.connect(self.toggle_statistics_visibility)
            actions_layout.addWidget(self.toggle_stats_button)
            
            actions_layout.addStretch()
            
            self.add_teacher_button = QPushButton("إضافة معلم")
            self.add_teacher_button.setObjectName("primaryButton")
            actions_layout.addWidget(self.add_teacher_button)
            
            self.print_list_button = QPushButton("طباعة قائمة المعلمين")
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
        """إنشاء ملخص المعلمين"""
        try:
            summary_frame = QFrame()
            summary_frame.setObjectName("summaryFrame")
            self.summary_frame = summary_frame  # إضافة هذا السطر لتعيين الخاصية
            
            summary_layout = QHBoxLayout(summary_frame)
            summary_layout.setContentsMargins(15, 10, 15, 10)
            
            numbers_layout = QVBoxLayout()
            
            summary_title = QLabel("ملخص المعلمين")
            summary_title.setObjectName("summaryTitle")
            numbers_layout.addWidget(summary_title)
            
            numbers_grid = QHBoxLayout()
            
            total_layout = QVBoxLayout()
            total_layout.setAlignment(Qt.AlignCenter)
            self.total_teachers_label = QLabel("إجمالي المعلمين")
            self.total_teachers_label.setAlignment(Qt.AlignCenter)
            self.total_teachers_label.setObjectName("summaryLabel")
            total_layout.addWidget(self.total_teachers_label)
            
            self.total_teachers_value = QLabel("0")
            self.total_teachers_value.setAlignment(Qt.AlignCenter)
            self.total_teachers_value.setObjectName("summaryValue")
            total_layout.addWidget(self.total_teachers_value)
            numbers_grid.addLayout(total_layout)
            
            numbers_layout.addLayout(numbers_grid)
            summary_layout.addLayout(numbers_layout)
            
            stats_layout = QVBoxLayout()
            
            self.displayed_count_label = QLabel("عدد المعلمين المعروضين: 0")
            self.displayed_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.displayed_count_label)
            
            summary_layout.addLayout(stats_layout)
            
            self.last_update_label = QLabel("آخر تحديث: --")
            self.last_update_label.setObjectName("statLabel")
            summary_layout.addWidget(self.last_update_label)
            
            layout.addWidget(summary_frame)
            
            # تطبيق حالة الرؤية
            self.summary_frame.setVisible(self.statistics_visible)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء ملخص المعلمين: {e}")
            raise
    
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
            if hasattr(self, 'teachers_table'):
                self.teachers_table.update()
            if hasattr(self, 'summary_frame'):
                self.summary_frame.update()

            print("DEBUG: تم تطبيق التنسيقات بنجاح")

        except Exception as e:
            logging.error(f"خطأ في إعداد الستايل: {e}")
            print(f"DEBUG: خطأ في إعداد الستايل: {e}")

    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            self.add_teacher_button.clicked.connect(self.add_teacher)
            self.print_list_button.clicked.connect(self.print_teachers_list)
            self.refresh_button.clicked.connect(self.refresh)
            self.clear_filters_button.clicked.connect(self.clear_filters)
            
            self.school_combo.currentTextChanged.connect(self.apply_filters)
            self.search_input.textChanged.connect(self.apply_filters)
            
            # ربط تغيير حجم الخط
            self.font_size_combo.currentTextChanged.connect(self.change_font_size)
            
            # ربط زر تبديل الإحصائيات (تم الربط مسبقاً في create_toolbar)
            
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

    def load_teachers(self):
        """تحميل قائمة المعلمين"""
        try:
            query = """
                SELECT t.id, t.name, s.name_ar as school_name,
                       t.class_hours, t.monthly_salary, t.phone, t.notes
                FROM teachers t
                LEFT JOIN schools s ON t.school_id = s.id
                WHERE 1=1
            """
            params = []
            
            selected_school_id = self.school_combo.currentData()
            if selected_school_id:
                query += " AND t.school_id = ?"
                params.append(selected_school_id)
            
            search_text = self.search_input.text().strip()
            if search_text:
                query += " AND t.name LIKE ?"
                params.append(f"%{search_text}%")
            
            query += " ORDER BY t.name"
            
            self.current_teachers = db_manager.execute_query(query, tuple(params))
            
            self.populate_table()
            self.update_stats()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المعلمين: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل بيانات المعلمين:\n{str(e)}")

    def populate_table(self):
        """ملء جدول المعلمين بالبيانات"""
        try:
            self.teachers_table.setRowCount(0)
            
            if not self.current_teachers:
                self.displayed_count_label.setText("عدد المعلمين المعروضين: 0")
                return
            
            for row_idx, teacher in enumerate(self.current_teachers):
                self.teachers_table.insertRow(row_idx)
                
                items = [
                    str(teacher['id']),
                    teacher['name'] or "",
                    teacher['school_name'] or "",
                    str(teacher['class_hours'] or 0),
                    f"{teacher['monthly_salary']:,.0f} د.ع" if teacher['monthly_salary'] else "0 د.ع",
                    teacher['phone'] or "",
                    teacher['notes'] or ""
                ]
                
                for col_idx, item_text in enumerate(items):
                    item = QTableWidgetItem(item_text)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.teachers_table.setItem(row_idx, col_idx, item)
            
            self.displayed_count_label.setText(f"عدد المعلمين المعروضين: {len(self.current_teachers)}")
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول المعلمين: {e}")

    def update_stats(self):
        """تحديث الإحصائيات"""
        try:
            total_teachers_count = len(self.current_teachers)
            
            self.total_teachers_value.setText(str(total_teachers_count))
            self.displayed_count_label.setText(f"عدد المعلمين المعروضين: {total_teachers_count}")
            
            from datetime import datetime
            self.last_update_label.setText(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث الإحصائيات: {e}")

    def apply_filters(self):
        """تطبيق الفلاتر وإعادة تحميل البيانات"""
        try:
            self.load_teachers()
        except Exception as e:
            logging.error(f"خطأ في تطبيق الفلاتر: {e}")

    def refresh(self):
        """تحديث البيانات"""
        try:
            log_user_action("تحديث صفحة المعلمين")
            self.load_teachers()
        except Exception as e:
            logging.error(f"خطأ في تحديث صفحة المعلمين: {e}")
            
    def clear_filters(self):
        """مسح جميع الفلاتر"""
        try:
            self.school_combo.setCurrentIndex(0)
            self.search_input.clear()
            self.apply_filters()
            log_user_action("مسح فلاتر صفحة المعلمين")
        except Exception as e:
            logging.error(f"خطأ في مسح الفلاتر: {e}")
    
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
                success = ui_settings_manager.set_font_size("teachers", selected_size)
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
            success = ui_settings_manager.set_statistics_visible("teachers", self.statistics_visible)
            print(f"DEBUG: حفظ حالة رؤية الإحصائيات: {'نجح' if success else 'فشل'}")
            
            log_user_action(f"تبديل رؤية الإحصائيات إلى: {'مرئي' if self.statistics_visible else 'مخفي'}")
            
        except Exception as e:
            logging.error(f"خطأ في تبديل رؤية الإحصائيات: {e}")
            print(f"DEBUG: خطأ في تبديل رؤية الإحصائيات: {e}")

    def add_teacher(self):
        """إضافة معلم جديد"""
        try:
            dialog = AddTeacherDialog(self)
            if dialog.exec_() == dialog.Accepted:
                self.refresh()
                log_user_action("إضافة معلم جديد", "نجح")
                
        except Exception as e:
            logging.error(f"خطأ في إضافة معلم: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في إضافة معلم:\n{e}")

    def edit_teacher_by_id(self, teacher_id):
        """تعديل المعلم المحدد"""
        try:
            dialog = EditTeacherDialog(teacher_id, self)
            if dialog.exec_() == dialog.Accepted:
                self.refresh()
                log_user_action(f"تعديل بيانات المعلم {teacher_id}", "نجح")
                
        except Exception as e:
            logging.error(f"خطأ في تعديل معلم: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تعديل المعلم:\n{e}")

    def delete_teacher(self, teacher_id):
        """حذف المعلم المحدد مع رواتبه"""
        try:
            # أولاً، التحقق من وجود رواتب للمعلم
            salary_query = "SELECT COUNT(*) as count FROM salaries WHERE staff_type = 'teacher' AND staff_id = ?"
            salary_result = db_manager.execute_query(salary_query, (teacher_id,))
            salary_count = salary_result[0]['count'] if salary_result else 0
            
            # إعداد رسالة التحذير
            if salary_count > 0:
                warning_message = f"""هل أنت متأكد من حذف هذا المعلم؟

⚠️ تحذير: سيتم حذف جميع الرواتب المرتبطة بهذا المعلم أيضاً!

عدد الرواتب المسجلة: {salary_count}

هذا الإجراء لا يمكن التراجع عنه."""
            else:
                warning_message = "هل أنت متأكد من حذف هذا المعلم؟"
            
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
                    cursor.execute("DELETE FROM salaries WHERE staff_type = 'teacher' AND staff_id = ?", (teacher_id,))
                    deleted_salaries = cursor.rowcount
                    
                    # ثم حذف المعلم
                    cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
                    affected_rows = cursor.rowcount
                    
                    if affected_rows > 0:
                        success_message = "تم حذف المعلم بنجاح"
                        if deleted_salaries > 0:
                            success_message += f"\nتم حذف {deleted_salaries} راتب مرتبط بالمعلم"
                        
                        QMessageBox.information(self, "نجح", success_message)
                        self.refresh()
                        log_user_action(f"حذف المعلم {teacher_id} مع {deleted_salaries} راتب", "نجح")
                    else:
                        QMessageBox.warning(self, "خطأ", "لم يتم العثور على المعلم")
                
        except Exception as e:
            logging.error(f"خطأ في حذف معلم: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في حذف المعلم:\n{e}")

    def show_context_menu(self, position):
        """عرض قائمة السياق"""
        try:
            if self.teachers_table.itemAt(position) is None:
                return
            
            current_row = self.teachers_table.currentRow()
            if current_row < 0:
                return

            teacher_id_item = self.teachers_table.item(current_row, 0)
            teacher_name_item = self.teachers_table.item(current_row, 1)
            if not teacher_id_item or not teacher_name_item:
                return
            
            teacher_id = int(teacher_id_item.text())
            teacher_name = teacher_name_item.text()
            
            menu = QMenu(self)
            
            details_action = QAction("عرض تفاصيل الرواتب", self)
            details_action.triggered.connect(lambda: self.show_teacher_salary_details(teacher_id, teacher_name))
            menu.addAction(details_action)
            
            menu.addSeparator()
            
            edit_action = QAction("تعديل", self)
            edit_action.triggered.connect(lambda: self.edit_teacher_by_id(teacher_id))
            menu.addAction(edit_action)
            
            delete_action = QAction("حذف", self)
            delete_action.triggered.connect(lambda: self.delete_teacher(teacher_id))
            menu.addAction(delete_action)
            
            menu.exec_(self.teachers_table.mapToGlobal(position))
            
        except Exception as e:
            logging.error(f"خطأ في قائمة السياق: {e}")

    def print_teachers_list(self):
        """طباعة قائمة المعلمين مع المعاينة والفلترة"""
        try:
            log_user_action("طباعة قائمة المعلمين")
            
            filters = []
            school = self.school_combo.currentText()
            if school and school != "جميع المدارس":
                filters.append(f"المدرسة: {school}")
            
            search = self.search_input.text().strip()
            if search:
                filters.append(f"بحث: {search}")
            
            filter_info = "؛ ".join(filters) if filters else None
            
            from core.printing.print_manager import print_teachers_list
            print_teachers_list(self.current_teachers, filter_info, parent=self)
            
        except Exception as e:
            logging.error(f"خطأ في طباعة قائمة المعلمين: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في طباعة قائمة المعلمين:\n{e}")

    def show_teacher_details(self):
        """عرض تفاصيل المعلم عند الضغط المزدوج"""
        try:
            current_row = self.teachers_table.currentRow()
            if current_row < 0:
                return
            
            teacher_id_item = self.teachers_table.item(current_row, 0)
            teacher_name_item = self.teachers_table.item(current_row, 1)
            
            if not teacher_id_item or not teacher_name_item:
                return
            
            teacher_id = int(teacher_id_item.text())
            teacher_name = teacher_name_item.text()
            
            self.show_teacher_salary_details(teacher_id, teacher_name)
            
        except Exception as e:
            logging.error(f"خطأ في عرض تفاصيل المعلم: {e}")

    def show_teacher_salary_details(self, teacher_id, teacher_name):
        """عرض نافذة تفاصيل رواتب المعلم"""
        try:
            dialog = SalaryDetailsDialog("teacher", teacher_id, teacher_name, self)
            dialog.exec_()
        except Exception as e:
            logging.error(f"خطأ في عرض تفاصيل رواتب المعلم: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في عرض تفاصيل الرواتب:\n{e}")
