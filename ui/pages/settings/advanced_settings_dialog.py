#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة الإعدادات المتقدمة
"""

import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from core.database.connection import db_manager
from core.utils.logger import log_user_action
from ui.pages.schools.add_school_dialog import AddSchoolDialog
from ui.pages.schools.edit_school_dialog import EditSchoolDialog


class AdvancedSettingsDialog(QDialog):
    """نافذة الإعدادات المتقدمة"""
    
    # إشارات
    school_added = pyqtSignal(dict)
    school_updated = pyqtSignal(dict)
    school_deleted = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("الإعدادات المتقدمة - إدارة المدارس")
        self.setModal(True)
        self.resize(1000, 700)  # حجم أكبر للنافذة
        
        self.setup_ui()
        self.setup_styles()
        self.load_schools()
        
        log_user_action("فتح نافذة الإعدادات المتقدمة")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            layout = QVBoxLayout()
            layout.setContentsMargins(25, 25, 25, 25)
            layout.setSpacing(20)
            
            # العنوان مع تحسين التصميم
            title_label = QLabel("🏫 إدارة المدارس - الإعدادات المتقدمة")
            title_label.setFont(QFont("Arial", 18, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                QLabel {
                    color: #2c3e50;
                    padding: 15px;
                    background-color: #ecf0f1;
                    border-radius: 8px;
                    border: 2px solid #bdc3c7;
                }
            """)
            layout.addWidget(title_label)
            
            # شريط الأدوات
            self.create_toolbar(layout)
            
            # جدول المدارس
            self.create_schools_table(layout)
            
            # شريط الحالة
            self.create_status_bar(layout)
            
            # أزرار النافذة
            self.create_dialog_buttons(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة الإعدادات المتقدمة: {e}")
            raise
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات"""
        try:
            toolbar_frame = QFrame()
            toolbar_frame.setObjectName("toolbarFrame")
            toolbar_layout = QHBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(15, 15, 15, 15)
            toolbar_layout.setSpacing(15)
            
            # أيقونة ونص البحث
            search_icon = QLabel("🔍")
            search_icon.setFont(QFont("Arial", 14))
            toolbar_layout.addWidget(search_icon)
            
            search_label = QLabel("البحث:")
            search_label.setFont(QFont("Arial", 11, QFont.Bold))
            toolbar_layout.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("ابحث في المدارس بالاسم أو الهاتف...")
            self.search_input.setMinimumWidth(250)
            self.search_input.setMinimumHeight(35)
            self.search_input.textChanged.connect(self.filter_schools)
            toolbar_layout.addWidget(self.search_input)
            
            # مساحة مرنة
            toolbar_layout.addStretch()
            
            # أزرار الإجراءات مع تحسينات
            self.add_button = QPushButton("➕ إضافة مدرسة")
            self.add_button.setObjectName("primaryButton")
            self.add_button.setMinimumSize(130, 40)
            self.add_button.clicked.connect(self.add_school)
            toolbar_layout.addWidget(self.add_button)
            
            self.refresh_button = QPushButton("🔄 تحديث")
            self.refresh_button.setObjectName("secondaryButton")
            self.refresh_button.setMinimumSize(100, 40)
            self.refresh_button.clicked.connect(self.load_schools)
            toolbar_layout.addWidget(self.refresh_button)
            
            layout.addWidget(toolbar_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
    
    def create_schools_table(self, layout):
        """إنشاء جدول المدارس"""
        try:
            # إطار الجدول مع تحسينات
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")
            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)
            
            self.schools_table = QTableWidget()
            self.schools_table.setObjectName("schoolsTable")
            
            # إعداد أعمدة الجدول
            columns = ["الرقم", "الاسم بالعربية", "الاسم بالإنجليزية", "نوع المدرسة", "المدير", "الهاتف", "الإجراءات"]
            self.schools_table.setColumnCount(len(columns))
            self.schools_table.setHorizontalHeaderLabels(columns)
            
            # إعداد خصائص الجدول
            self.schools_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.schools_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.schools_table.setAlternatingRowColors(True)
            self.schools_table.setSortingEnabled(True)
            self.schools_table.setShowGrid(True)
            
            # إعداد حجم الأعمدة مع تحسينات
            header = self.schools_table.horizontalHeader()
            header.setStretchLastSection(False)
            header.setSectionResizeMode(0, QHeaderView.Fixed)  # الرقم
            header.setSectionResizeMode(1, QHeaderView.Stretch)  # الاسم بالعربية
            header.setSectionResizeMode(2, QHeaderView.Stretch)  # الاسم بالإنجليزية
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # نوع المدرسة
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # المدير
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # الهاتف
            header.setSectionResizeMode(6, QHeaderView.Fixed)  # الإجراءات
            
            # تحديد عرض أعمدة محددة
            self.schools_table.setColumnWidth(0, 60)  # الرقم
            self.schools_table.setColumnWidth(6, 180)  # الإجراءات
            
            # زيادة ارتفاع الصفوف لجعل الأزرار تظهر بشكل مناسب
            self.schools_table.verticalHeader().setDefaultSectionSize(55)
            self.schools_table.verticalHeader().setVisible(False)
            
            table_layout.addWidget(self.schools_table)
            layout.addWidget(table_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول المدارس: {e}")
    
    def create_status_bar(self, layout):
        """إنشاء شريط الحالة"""
        try:
            status_frame = QFrame()
            status_frame.setObjectName("statusFrame")
            status_layout = QHBoxLayout(status_frame)
            status_layout.setContentsMargins(15, 10, 15, 10)
            
            # عداد المدارس
            self.schools_count_label = QLabel("📊 العدد: 0")
            self.schools_count_label.setObjectName("countLabel")
            self.schools_count_label.setFont(QFont("Arial", 10, QFont.Bold))
            status_layout.addWidget(self.schools_count_label)
            
            # مساحة مرنة
            status_layout.addStretch()
            
            # حالة آخر تحديث
            self.last_update_label = QLabel("🕒 آخر تحديث: --")
            self.last_update_label.setObjectName("updateLabel")
            self.last_update_label.setFont(QFont("Arial", 10))
            status_layout.addWidget(self.last_update_label)
            
            layout.addWidget(status_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الحالة: {e}")
    
    def create_dialog_buttons(self, layout):
        """إنشاء أزرار النافذة"""
        try:
            buttons_frame = QFrame()
            buttons_frame.setObjectName("buttonsFrame")
            buttons_layout = QHBoxLayout(buttons_frame)
            buttons_layout.setContentsMargins(15, 15, 15, 15)
            buttons_layout.addStretch()
            
            close_button = QPushButton("❌ إغلاق")
            close_button.setObjectName("closeButton")
            close_button.setMinimumSize(120, 40)
            close_button.clicked.connect(self.accept)
            buttons_layout.addWidget(close_button)
            
            layout.addWidget(buttons_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء أزرار النافذة: {e}")
    
    def load_schools(self):
        """تحميل المدارس من قاعدة البيانات"""
        try:
            self.schools_table.setRowCount(0)
            
            query = """
                SELECT id, name_ar, name_en, school_types, phone
                FROM schools 
                ORDER BY name_ar
            """
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                schools = cursor.fetchall()
                
                self.schools_table.setRowCount(len(schools))
                
                for row, school in enumerate(schools):
                    # البيانات الأساسية
                    items = [
                        str(school[0]),  # المعرف
                        school[1] or "",  # الاسم بالعربية
                        school[2] or "",  # الاسم بالإنجليزية
                        school[3] or "",  # نوع المدرسة
                        "",  # المدير - فارغ
                        school[4] or ""   # الهاتف
                    ]
                    
                    for col, item_text in enumerate(items):
                        item = QTableWidgetItem(item_text)
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setFont(QFont("Arial", 10))
                        self.schools_table.setItem(row, col, item)
                    
                    # أزرار الإجراءات
                    actions_widget = self.create_actions_widget(school[0])
                    self.schools_table.setCellWidget(row, 6, actions_widget)
                
                # تحديث شريط الحالة
                self.schools_count_label.setText(f"📊 العدد: {len(schools)} مدرسة")
                
                current_time = datetime.now().strftime("%H:%M:%S")
                self.last_update_label.setText(f"🕒 آخر تحديث: {current_time}")
                
                log_user_action(f"تم تحميل {len(schools)} مدرسة في الإعدادات المتقدمة")
                
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في تحميل البيانات: {str(e)}")
    
    def create_actions_widget(self, school_id: int):
        """إنشاء ويدجت الإجراءات لكل صف"""
        try:
            widget = QFrame()
            widget.setObjectName("actionsWidget")
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(8, 5, 8, 5)
            layout.setSpacing(8)
            
            # زر التعديل مع تحسينات
            edit_btn = QPushButton("✏️ تعديل")
            edit_btn.setObjectName("editButton")
            edit_btn.setMinimumSize(75, 35)
            edit_btn.setToolTip("تعديل بيانات المدرسة")
            edit_btn.clicked.connect(lambda: self.edit_school(school_id))
            layout.addWidget(edit_btn)
            
            # زر الحذف مع تحسينات
            delete_btn = QPushButton("🗑️ حذف")
            delete_btn.setObjectName("deleteButton")
            delete_btn.setMinimumSize(75, 35)
            delete_btn.setToolTip("حذف المدرسة نهائياً")
            delete_btn.clicked.connect(lambda: self.delete_school(school_id))
            layout.addWidget(delete_btn)
            
            return widget
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء ويدجت الإجراءات: {e}")
            return QFrame()
    
    def filter_schools(self):
        """تصفية المدارس حسب النص المدخل"""
        try:
            search_text = self.search_input.text().strip().lower()
            
            for row in range(self.schools_table.rowCount()):
                row_visible = False
                
                for col in [1, 2, 3, 5]:  # من الاسم إلى الهاتف، مستثنى المدير
                    item = self.schools_table.item(row, col)
                    if item and search_text in item.text().lower():
                        row_visible = True
                        break
                
                self.schools_table.setRowHidden(row, not row_visible)
                
        except Exception as e:
            logging.error(f"خطأ في تصفية المدارس: {e}")
    
    def add_school(self):
        """إضافة مدرسة جديدة"""
        try:
            dialog = AddSchoolDialog(self)
            dialog.school_added.connect(self.on_school_added)
            dialog.exec_()
                    
        except Exception as e:
            logging.error(f"خطأ في إضافة مدرسة: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في إضافة المدرسة: {str(e)}")
    
    def on_school_added(self, school_data):
        """معالجة إضافة مدرسة جديدة"""
        try:
            self.school_added.emit(school_data)
            self.load_schools()
            log_user_action(f"تم إضافة مدرسة جديدة في الإعدادات المتقدمة: {school_data.get('name_ar', 'غير محدد')}")
        except Exception as e:
            logging.error(f"خطأ في معالجة إضافة المدرسة: {e}")
    
    def edit_school(self, school_id: int):
        """تعديل مدرسة"""
        try:
            # الحصول على بيانات المدرسة أولاً
            query = """
                SELECT id, name_ar, name_en, phone, address, 
                       school_types, logo_path, created_at
                FROM schools WHERE id = ?
            """
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (school_id,))
                result = cursor.fetchone()
                
                if not result:
                    QMessageBox.warning(self, "تحذير", "المدرسة غير موجودة")
                    return
                
                # تحويل النتيجة إلى قاموس
                school_data = {
                    'id': result[0],
                    'name_ar': result[1],
                    'name_en': result[2],
                    'phone': result[3],
                    'address': result[4],
                    'school_types': result[5],
                    'logo_path': result[6],
                    'created_at': result[7]
                }
                
                # فتح نافذة التعديل مع البيانات
                dialog = EditSchoolDialog(school_data, self, enable_name_ar_edit=True)
                dialog.school_updated.connect(self.on_school_updated)
                dialog.exec_()
                    
        except Exception as e:
            logging.error(f"خطأ في تعديل مدرسة: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في تعديل المدرسة: {str(e)}")
    
    def on_school_updated(self, school_data):
        """معالجة تحديث بيانات مدرسة"""
        try:
            self.school_updated.emit(school_data)
            self.load_schools()
            QMessageBox.information(self, "نجح", "تم تحديث المدرسة بنجاح")
            log_user_action(f"تم تحديث مدرسة في الإعدادات المتقدمة: {school_data.get('name_ar', 'غير محدد')}")
        except Exception as e:
            logging.error(f"خطأ في معالجة تحديث المدرسة: {e}")
    
    def delete_school(self, school_id: int):
        """حذف مدرسة"""
        try:
            # الحصول على اسم المدرسة للتأكيد
            query = "SELECT name_ar FROM schools WHERE id = ?"
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (school_id,))
                result = cursor.fetchone()
                
                if not result:
                    QMessageBox.warning(self, "تحذير", "المدرسة غير موجودة")
                    return
                
                school_name = result[0]
                
                # التحقق من وجود طلاب في المدرسة
                students_query = "SELECT COUNT(*) FROM students WHERE school_id = ?"
                cursor.execute(students_query, (school_id,))
                students_count = cursor.fetchone()[0]
                
                if students_count > 0:
                    QMessageBox.warning(
                        self,
                        "لا يمكن الحذف",
                        f"لا يمكن حذف المدرسة '{school_name}' لأنها تحتوي على {students_count} طالب.\n\n"
                        "يجب حذف جميع الطلاب من المدرسة أولاً قبل حذف المدرسة."
                    )
                    return
                
                # تأكيد الحذف
                reply = QMessageBox.question(
                    self,
                    "تأكيد الحذف",
                    f"هل تريد حذف المدرسة '{school_name}'؟\n\n"
                    "تحذير: سيتم حذف جميع البيانات المرتبطة بهذه المدرسة.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # حذف المدرسة
                    delete_query = "DELETE FROM schools WHERE id = ?"
                    cursor.execute(delete_query, (school_id,))
                    conn.commit()
                    
                    self.school_deleted.emit(school_id)
                    self.load_schools()
                    
                    QMessageBox.information(self, "نجح", f"تم حذف المدرسة '{school_name}' بنجاح")
                    log_user_action(f"تم حذف مدرسة: {school_name}")
                    
        except Exception as e:
            logging.error(f"خطأ في حذف مدرسة: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في حذف المدرسة: {str(e)}")
    
    def setup_styles(self):
        """إعداد الأنماط"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border-radius: 10px;
            }
            
            #toolbarFrame {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 5px;
            }
            
            #tableFrame {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
            
            #statusFrame {
                background-color: #e9ecef;
                border: 1px solid #ced4da;
                border-radius: 6px;
            }
            
            #buttonsFrame {
                background-color: #f8f9fa;
            }
            
            QTableWidget {
                border: none;
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #e9ecef;
                font-size: 11px;
            }
            
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #e9ecef;
            }
            
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            
            QTableWidget::horizontalHeader {
                background-color: #343a40;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px;
            }
            
            QTableWidget::horizontalHeader::section {
                background-color: #495057;
                color: white;
                font-weight: bold;
                border: 1px solid #6c757d;
                padding: 8px;
            }
            
            QPushButton#primaryButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #218838;
            }
            
            QPushButton#primaryButton:pressed {
                background-color: #1e7e34;
            }
            
            QPushButton#secondaryButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton#secondaryButton:hover {
                background-color: #5a6268;
            }
            
            QPushButton#secondaryButton:pressed {
                background-color: #545b62;
            }
            
            QPushButton#editButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            
            QPushButton#editButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton#deleteButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            
            QPushButton#deleteButton:hover {
                background-color: #c82333;
            }
            
            QPushButton#closeButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton#closeButton:hover {
                background-color: #5a6268;
            }
            
            QLineEdit {
                border: 2px solid #ced4da;
                padding: 8px 12px;
                border-radius: 6px;
                background-color: white;
                font-size: 11px;
            }
            
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
            
            #countLabel {
                color: #28a745;
                font-weight: bold;
            }
            
            #updateLabel {
                color: #6c757d;
            }
            
            #actionsWidget {
                border: none;
                background-color: transparent;
            }
        """)


def show_advanced_settings(parent=None):
    """عرض نافذة الإعدادات المتقدمة"""
    try:
        # عرض نافذة الإعدادات المتقدمة مباشرة بدون طلب كلمة مرور
        dialog = AdvancedSettingsDialog(parent)
        return dialog.exec_()
        
    except Exception as e:
        logging.error(f"خطأ في عرض الإعدادات المتقدمة: {e}")
        QMessageBox.critical(parent, "خطأ", f"خطأ في فتح الإعدادات المتقدمة: {str(e)}")
        return None
