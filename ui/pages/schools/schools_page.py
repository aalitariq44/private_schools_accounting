#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة المدارس
"""

import logging
import json
import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QMenu, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation
from .add_school_dialog import AddSchoolDialog
from .edit_school_dialog import EditSchoolDialog
import config


class SchoolsPage(QWidget):
    """صفحة إدارة المدارس"""
    
    # إشارات مخصصة
    school_added = pyqtSignal(dict)
    school_updated = pyqtSignal(dict)
    school_deleted = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styles()
        self.load_schools()
        
        log_user_action("تم فتح صفحة المدارس")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            main_layout = QVBoxLayout()
            # هوامش ومسافات مضغوطة لتناسب الشاشات الأصغر
            main_layout.setContentsMargins(8, 8, 8, 8)
            main_layout.setSpacing(8)
            
            # شريط الأدوات العلوي
            self.create_toolbar(main_layout)
            
            # جدول المدارس
            self.create_schools_table(main_layout)
            
            # شريط الحالة السفلي
            self.create_status_bar(main_layout)
            
            self.setLayout(main_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة المدارس: {e}")
            raise
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات"""
        try:
            toolbar_frame = QFrame()
            toolbar_frame.setObjectName("toolbarFrame")
            
            toolbar_layout = QHBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(8, 6, 8, 6)
            toolbar_layout.setSpacing(6)
            
            # عنوان الصفحة
            title_label = QLabel("إدارة المدارس")
            title_label.setObjectName("pageTitle")
            toolbar_layout.addWidget(title_label)
            
            # مساحة مرنة
            toolbar_layout.addStretch()
            
            # حقل البحث
            search_label = QLabel("البحث:")
            search_label.setObjectName("searchLabel")
            toolbar_layout.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setObjectName("searchInput")
            self.search_input.setPlaceholderText("ابحث في المدارس...")
            self.search_input.setMaximumWidth(200)
            self.search_input.textChanged.connect(self.filter_schools)
            toolbar_layout.addWidget(self.search_input)
            
            # أزرار الإجراءات
            # تم إزالة زر إضافة مدرسة للمستخدم العادي
            # الآن يتوفر فقط في الإعدادات المتقدمة
            
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("refreshButton")
            self.refresh_button.clicked.connect(self.refresh)
            toolbar_layout.addWidget(self.refresh_button)
            
            layout.addWidget(toolbar_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
            raise
    
    def create_schools_table(self, layout):
        """إنشاء جدول المدارس"""
        try:
            # إطار الجدول
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")
            
            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)  # إزالة الهوامش تمامًا

            # إنشاء الجدول
            self.schools_table = QTableWidget()
            self.schools_table.setObjectName("schoolsTable")
            self.schools_table.setStyleSheet("QTableWidget::item { padding: 0px; }")  # إزالة الحشو لإظهار أزرار الإجراءات بشكل صحيح
            
            # إعداد أعمدة الجدول
            columns = ["المعرف", "الشعار", "الاسم بالعربية", "الاسم بالإنجليزية", "نوع المدرسة", "المدير", "الهاتف"]
            self.schools_table.setColumnCount(len(columns))
            self.schools_table.setHorizontalHeaderLabels(columns)
            
            # إعداد خصائص الجدول
            self.schools_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.schools_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.schools_table.setAlternatingRowColors(True)
            self.schools_table.setSortingEnabled(True)
            
            # إعداد حجم الأعمدة
            header = self.schools_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # المعرف
            header.setSectionResizeMode(1, QHeaderView.Fixed)  # الشعار
            header.setSectionResizeMode(2, QHeaderView.Stretch)  # الاسم بالعربية
            header.setSectionResizeMode(3, QHeaderView.Stretch)  # الاسم بالإنجليزية
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # نوع المدرسة
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # المدير
            header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # الهاتف
            
            # تحديد عرض عمود الشعار
            self.schools_table.setColumnWidth(1, 80)  # عرض عمود الشعار
            
            # زيادة ارتفاع الصفوف لعرض الشعار بشكل مناسب
            self.schools_table.verticalHeader().setDefaultSectionSize(60)
            # ربط إشارات الجدول
            self.schools_table.cellDoubleClicked.connect(self.edit_school)
            self.schools_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.schools_table.customContextMenuRequested.connect(self.show_context_menu)
            
            table_layout.addWidget(self.schools_table)
            layout.addWidget(table_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول المدارس: {e}")
            raise
    
    def create_status_bar(self, layout):
        """إنشاء شريط الحالة"""
        try:
            status_frame = QFrame()
            status_frame.setObjectName("statusFrame")
            
            status_layout = QHBoxLayout(status_frame)
            status_layout.setContentsMargins(8, 4, 8, 4)
            status_layout.setSpacing(6)
            
            # عداد المدارس
            self.schools_count_label = QLabel("العدد: 0")
            self.schools_count_label.setObjectName("countLabel")
            status_layout.addWidget(self.schools_count_label)
            
            # مساحة مرنة
            status_layout.addStretch()
            
            # حالة آخر تحديث
            self.last_update_label = QLabel("آخر تحديث: --")
            self.last_update_label.setObjectName("updateLabel")
            status_layout.addWidget(self.last_update_label)
            
            layout.addWidget(status_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الحالة: {e}")
            raise
    
    def load_schools(self):
        """تحميل المدارس من قاعدة البيانات"""
        try:
            # تنظيف الجدول
            self.schools_table.setRowCount(0)
            
            # استعلام جميع المدارس
            query = """
                SELECT id, name_ar, name_en, school_types, principal_name, 
                       phone, address, logo_path, created_at
                FROM schools 
                ORDER BY id
            """
            
            schools = db_manager.execute_query(query)
            
            # ملء الجدول
            for row_idx, school in enumerate(schools):
                self.schools_table.insertRow(row_idx)
                
                # المعرف
                id_item = QTableWidgetItem(str(school['id']))
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                self.schools_table.setItem(row_idx, 0, id_item)
                
                # الشعار
                logo_widget = self.create_logo_widget(school['logo_path'])
                self.schools_table.setCellWidget(row_idx, 1, logo_widget)
                
                # الاسم بالعربية
                name_ar_item = QTableWidgetItem(school['name_ar'] or "")
                name_ar_item.setFlags(name_ar_item.flags() & ~Qt.ItemIsEditable)
                self.schools_table.setItem(row_idx, 2, name_ar_item)
                
                # الاسم بالإنجليزية
                name_en_item = QTableWidgetItem(school['name_en'] or "")
                name_en_item.setFlags(name_en_item.flags() & ~Qt.ItemIsEditable)
                self.schools_table.setItem(row_idx, 3, name_en_item)
                
                # نوع المدرسة
                school_types = self.parse_school_types(school['school_types'])
                types_text = ", ".join(school_types)
                types_item = QTableWidgetItem(types_text)
                types_item.setFlags(types_item.flags() & ~Qt.ItemIsEditable)
                self.schools_table.setItem(row_idx, 4, types_item)
                
                # المدير
                principal_item = QTableWidgetItem(school['principal_name'] or "")
                principal_item.setFlags(principal_item.flags() & ~Qt.ItemIsEditable)
                self.schools_table.setItem(row_idx, 5, principal_item)
                
                # الهاتف
                phone_item = QTableWidgetItem(school['phone'] or "")
                phone_item.setFlags(phone_item.flags() & ~Qt.ItemIsEditable)
                self.schools_table.setItem(row_idx, 6, phone_item)
                
            
            # فرز حسب المعرف افتراضيا
            self.schools_table.sortItems(0, Qt.AscendingOrder)
            # تحديث العداد
            self.update_schools_count()
            
            # تحديث وقت آخر تحديث
            self.update_last_update_time()
            
            log_database_operation("تحميل", "schools", f"تم تحميل {len(schools)} مدرسة")
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            self.show_error_message("خطأ في تحميل البيانات", str(e))
    
    def parse_school_types(self, types_json: str) -> list:
        """تحليل أنواع المدرسة من JSON"""
        try:
            if not types_json:
                return []
            
            types = json.loads(types_json)
            if isinstance(types, list):
                return types
            else:
                return [types_json]  # في حالة كان نص عادي
                
        except (json.JSONDecodeError, TypeError):
            return [types_json] if types_json else []
    
    def create_logo_widget(self, logo_path: str) -> QLabel:
        """إنشاء ويدجت عرض الشعار"""
        try:
            logo_label = QLabel()
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet("""
                QLabel {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background-color: #f8f9fa;
                    padding: 2px;
                }
            """)
            
            # مسار الشعار الافتراضي
            default_logo = config.RESOURCES_DIR / "images" / "logo.png"
            
            # تحديد المسار المراد استخدامه
            if logo_path and Path(logo_path).exists():
                pixmap_path = logo_path
            else:
                pixmap_path = str(default_logo)
            
            # تحميل وتحجيم الصورة
            if Path(pixmap_path).exists():
                pixmap = QPixmap(pixmap_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    logo_label.setPixmap(scaled_pixmap)
                else:
                    logo_label.setText("لا يوجد شعار")
                    logo_label.setStyleSheet("""
                        QLabel {
                            border: 1px solid #ddd;
                            border-radius: 4px;
                            background-color: #f8f9fa;
                            color: #666;
                            font-size: 10px;
                            padding: 2px;
                        }
                    """)
            else:
                logo_label.setText("لا يوجد شعار")
                logo_label.setStyleSheet("""
                    QLabel {
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        background-color: #f8f9fa;
                        color: #666;
                        font-size: 10px;
                        padding: 2px;
                    }
                """)
                
            return logo_label
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء ويدجت الشعار: {e}")
            # إرجاع label فارغ في حالة الخطأ
            label = QLabel("خطأ")
            label.setAlignment(Qt.AlignCenter)
            return label
    
    
    def show_context_menu(self, position):
        """عرض القائمة السياقية (للمستخدم العادي - بدون حذف)"""
        try:
            if self.schools_table.itemAt(position) is None:
                return
            
            menu = QMenu(self)
            
            # الحصول على المدرسة المحددة
            current_row = self.schools_table.currentRow()
            if current_row < 0:
                return
            
            school_id = int(self.schools_table.item(current_row, 0).text())
            
            # إضافة إجراءات القائمة (بدون حذف للمستخدم العادي)
            edit_action = menu.addAction("تعديل المدرسة")
            edit_action.triggered.connect(lambda: self.edit_school_by_id(school_id))
            
            # تم إزالة خيار حذف المدرسة للمستخدم العادي
            # الآن متوفر فقط في الإعدادات المتقدمة
            
            menu.addSeparator()
            
            details_action = menu.addAction("عرض التفاصيل")
            details_action.triggered.connect(lambda: self.show_school_details(school_id))
            
            view_students_action = menu.addAction("عرض الطلاب")
            view_students_action.triggered.connect(lambda: self.view_school_students(school_id))
            
            # عرض القائمة
            menu.exec_(self.schools_table.mapToGlobal(position))
            
        except Exception as e:
            logging.error(f"خطأ في عرض القائمة السياقية: {e}")
    
    def filter_schools(self):
        """تصفية المدارس حسب النص المدخل"""
        try:
            search_text = self.search_input.text().strip().lower()
            
            for row in range(self.schools_table.rowCount()):
                # البحث في جميع الأعمدة النصية (تخطي عمود الشعار)
                row_visible = False
                
                # البحث في الأعمدة: 0=المعرف، 2=الاسم بالعربية، 3=الاسم بالإنجليزية، 4=نوع المدرسة، 5=المدير، 6=الهاتف
                search_columns = [0, 2, 3, 4, 5, 6]
                for col in search_columns:
                    item = self.schools_table.item(row, col)
                    if item and search_text in item.text().lower():
                        row_visible = True
                        break
                
                self.schools_table.setRowHidden(row, not row_visible)
            
            # تحديث العداد
            self.update_schools_count()
            
        except Exception as e:
            logging.error(f"خطأ في تصفية المدارس: {e}")
    
    def update_schools_count(self):
        """تحديث عداد المدارس"""
        try:
            total_count = self.schools_table.rowCount()
            visible_count = 0
            
            for row in range(total_count):
                if not self.schools_table.isRowHidden(row):
                    visible_count += 1
            
            if visible_count == total_count:
                self.schools_count_label.setText(f"العدد: {total_count}")
            else:
                self.schools_count_label.setText(f"العدد: {visible_count} من {total_count}")
                
        except Exception as e:
            logging.error(f"خطأ في تحديث عداد المدارس: {e}")
    
    def update_last_update_time(self):
        """تحديث وقت آخر تحديث"""
        try:
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_update_label.setText(f"آخر تحديث: {current_time}")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث وقت آخر تحديث: {e}")
    
    def add_school(self):
        """إضافة مدرسة جديدة"""
        try:
            dialog = AddSchoolDialog(self)
            dialog.school_added.connect(self.on_school_added)
            dialog.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في فتح نافذة إضافة مدرسة: {e}")
            self.show_error_message("خطأ", f"حدث خطأ في فتح نافذة إضافة المدرسة: {str(e)}")
    
    def on_school_added(self, school_data):
        """معالجة إضافة مدرسة جديدة"""
        try:
            log_user_action("تم إضافة مدرسة جديدة", school_data.get('name_ar', ''))
            self.refresh()
            
        except Exception as e:
            logging.error(f"خطأ في معالجة إضافة المدرسة: {e}")
    
    def edit_school(self, row, column):
        """تعديل مدرسة عند الضغط المزدوج"""
        try:
            if row >= 0:
                school_id = int(self.schools_table.item(row, 0).text())
                self.edit_school_by_id(school_id)
                
        except Exception as e:
            logging.error(f"خطأ في تعديل المدرسة: {e}")
    
    def edit_school_by_id(self, school_id: int):
        """تعديل مدرسة بالمعرف"""
        try:
            # الحصول على بيانات المدرسة
            query = """
                SELECT id, name_ar, name_en, principal_name, phone, address, school_types, logo_path, created_at
                FROM schools WHERE id = ?
            """
            
            result = db_manager.execute_query(query, (school_id,))
            if result:
                school_data = {
                    'id': result[0]['id'],
                    'name_ar': result[0]['name_ar'],
                    'name_en': result[0]['name_en'],
                    'principal_name': result[0]['principal_name'],
                    'phone': result[0]['phone'],
                    'address': result[0]['address'],
                    'school_types': result[0]['school_types'],
                    'logo_path': result[0]['logo_path'],
                    'created_at': result[0]['created_at']
                }
                
                # فتح نافذة التعديل
                dialog = EditSchoolDialog(school_data, self, enable_name_ar_edit=False)
                dialog.school_updated.connect(self.on_school_updated)
                dialog.exec_()
            else:
                self.show_error_message("خطأ", "لم يتم العثور على المدرسة")
            
        except Exception as e:
            logging.error(f"خطأ في تعديل المدرسة {school_id}: {e}")
            self.show_error_message("خطأ", f"حدث خطأ في تعديل المدرسة: {str(e)}")
    
    def on_school_updated(self, school_data):
        """معالجة تحديث بيانات مدرسة"""
        try:
            log_user_action("تم تحديث بيانات مدرسة", school_data.get('name_ar', ''))
            self.refresh()
            
        except Exception as e:
            logging.error(f"خطأ في معالجة تحديث المدرسة: {e}")
    
    def delete_school_by_id(self, school_id: int):
        """حذف مدرسة بالمعرف"""
        try:
            # التحقق من وجود طلاب في المدرسة
            students_query = "SELECT COUNT(*) as count FROM students WHERE school_id = ?"
            students_result = db_manager.execute_query(students_query, (school_id,))
            students_count = students_result[0]['count'] if students_result else 0
            
            # رسالة التأكيد
            if students_count > 0:
                reply = QMessageBox.question(
                    self,
                    "تأكيد الحذف",
                    f"تحتوي هذه المدرسة على {students_count} طالب.\n"
                    "سيتم حذف جميع الطلاب والبيانات المرتبطة بهم.\n"
                    "هل تريد المتابعة؟",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
            else:
                reply = QMessageBox.question(
                    self,
                    "تأكيد الحذف",
                    "هل تريد حذف هذه المدرسة؟",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
            
            if reply == QMessageBox.Yes:
                # حذف المدرسة
                delete_query = "DELETE FROM schools WHERE id = ?"
                affected_rows = db_manager.execute_update(delete_query, (school_id,))
                
                if affected_rows > 0:
                    self.show_success_message("نجح الحذف", "تم حذف المدرسة بنجاح")
                    self.refresh()
                    self.school_deleted.emit(school_id)
                    log_database_operation("حذف", "schools", f"حذف المدرسة {school_id}")
                else:
                    self.show_error_message("خطأ في الحذف", "لم يتم حذف المدرسة")
            
        except Exception as e:
            logging.error(f"خطأ في حذف المدرسة {school_id}: {e}")
            self.show_error_message("خطأ في الحذف", str(e))
    
    def show_school_details(self, school_id: int):
        """عرض تفاصيل المدرسة"""
        try:
            # سيتم تطوير نافذة تفاصيل المدرسة لاحقاً
            self.show_info_message("قيد التطوير", f"نافذة تفاصيل المدرسة {school_id} قيد التطوير")
            log_user_action("طلب عرض تفاصيل مدرسة", f"المعرف: {school_id}")
            
        except Exception as e:
            logging.error(f"خطأ في عرض تفاصيل المدرسة {school_id}: {e}")
    
    def view_school_students(self, school_id: int):
        """عرض طلاب المدرسة"""
        try:
            # الانتقال إلى صفحة الطلاب مع تصفية المدرسة
            from PyQt5.QtWidgets import QApplication
            main_window = QApplication.activeWindow()
            if main_window and hasattr(main_window, 'navigate_to_page'):
                main_window.navigate_to_page('students')
                # سيتم إضافة تصفية المدرسة لاحقاً
            
            log_user_action("طلب عرض طلاب المدرسة", f"المعرف: {school_id}")
            
        except Exception as e:
            logging.error(f"خطأ في عرض طلاب المدرسة {school_id}: {e}")
    
    def refresh(self):
        """تحديث الصفحة"""
        try:
            self.load_schools()
            self.search_input.clear()
            log_user_action("تم تحديث صفحة المدارس")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث صفحة المدارس: {e}")
    
    def show_success_message(self, title: str, message: str):
        """عرض رسالة نجاح"""
        try:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle(title)
            msg.setText(message)
            msg.setLayoutDirection(Qt.RightToLeft)
            msg.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة النجاح: {e}")
    
    def show_error_message(self, title: str, message: str):
        """عرض رسالة خطأ"""
        try:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle(title)
            msg.setText(message)
            msg.setLayoutDirection(Qt.RightToLeft)
            msg.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة الخطأ: {e}")
    
    def show_info_message(self, title: str, message: str):
        """عرض رسالة معلومات"""
        try:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle(title)
            msg.setText(message)
            msg.setLayoutDirection(Qt.RightToLeft)
            msg.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة المعلومات: {e}")
    
    def setup_styles(self):
        """إعداد تنسيقات الصفحة"""
        try:
            style = """
                QWidget { background: #F5F6F7; }
                #toolbarFrame {
                    background-color: #FFFFFF;
                    border: 1px solid #DDE1E4;
                    border-radius: 6px;
                    margin-bottom: 8px;
                }
                #pageTitle {
                    font-size: 13px;
                    font-weight: 600;
                    color: #2C3E50;
                }
                #searchLabel {
                    font-size: 12px;
                    color: #5F6B73;
                    margin-right: 4px;
                }
                #searchInput {
                    padding: 6px 10px; /* Slightly more padding */
                    border: 1px solid #C5CBD0;
                    border-radius: 5px; /* Slightly more rounded */
                    font-size: 13px; /* Slightly larger font */
                    background-color: #FFFFFF;
                    min-width: 180px;
                }
                #searchInput:focus { border:1px solid #007BFF; } /* Primary blue on focus */
                #refreshButton {
                    background:#007BFF; /* Primary blue */
                    color:#FFFFFF;
                    border:1px solid #007BFF;
                    padding:6px 12px; /* Slightly larger padding */
                    border-radius:5px; /* Slightly more rounded */
                    font-size:13px; /* Slightly larger font */
                    font-weight:600;
                    min-width:110px; /* Consistent width with dashboard buttons */
                    transition: all 0.3s ease; /* Smooth transition for hover effects */
                }
                #refreshButton:hover {
                    background:#0056B3; /* Darker blue on hover */
                    border:1px solid #0056B3;
                }
                #refreshButton:pressed {
                    background:#004085; /* Even darker on pressed */
                    border:1px solid #004085;
                }
                #tableFrame {
                    background-color: #FFFFFF;
                    border: 1px solid #DDE1E4;
                    border-radius: 6px;
                }
                #schoolsTable { border:none; background:#FFFFFF; gridline-color:#E2E5E8; font-size:12px; selection-background-color:#2F6ED1; selection-color:#FFFFFF; }
                #schoolsTable::item { padding:0px; }
                #schoolsTable QHeaderView::section {
                    background:#E0E0E0; /* Lighter grey for a cleaner look */
                    color:#2C3E50;
                    padding:6px 8px; /* Slightly more padding */
                    font-size:13px; /* Slightly larger font */
                    font-weight:700; /* Bolder font */
                    border:1px solid #C5CBD0; /* Slightly darker border */
                    border-bottom:2px solid #007BFF; /* Highlight bottom border with primary blue */
                }
                #statusFrame {
                    background:#FFFFFF;
                    border:1px solid #DDE1E4;
                    border-radius:6px;
                    margin-top:8px;
                    padding:4px 8px;
                }
                #countLabel, #updateLabel { font-size:12px; color:#5F6B73; }
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد تنسيقات الصفحة: {e}")
