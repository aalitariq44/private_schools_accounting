#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة الإعدادات المتقدمة
"""

import logging
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
        self.resize(800, 600)
        
        self.setup_ui()
        self.setup_styles()
        self.load_schools()
        
        log_user_action("فتح نافذة الإعدادات المتقدمة")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            # العنوان
            title_label = QLabel("إدارة المدارس - الإعدادات المتقدمة")
            title_label.setFont(QFont("Arial", 16, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)
            
            # شريط الأدوات
            self.create_toolbar(layout)
            
            # جدول المدارس
            self.create_schools_table(layout)
            
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
            toolbar_layout = QHBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(0, 0, 0, 0)
            
            # حقل البحث
            search_label = QLabel("البحث:")
            toolbar_layout.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("ابحث في المدارس...")
            self.search_input.setMaximumWidth(200)
            self.search_input.textChanged.connect(self.filter_schools)
            toolbar_layout.addWidget(self.search_input)
            
            # مساحة مرنة
            toolbar_layout.addStretch()
            
            # أزرار الإجراءات
            self.add_button = QPushButton("إضافة مدرسة")
            self.add_button.clicked.connect(self.add_school)
            toolbar_layout.addWidget(self.add_button)
            
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.clicked.connect(self.load_schools)
            toolbar_layout.addWidget(self.refresh_button)
            
            layout.addWidget(toolbar_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
    
    def create_schools_table(self, layout):
        """إنشاء جدول المدارس"""
        try:
            self.schools_table = QTableWidget()
            
            # إعداد أعمدة الجدول
            columns = ["المعرف", "الاسم بالعربية", "الاسم بالإنجليزية", "نوع المدرسة", "المدير", "الهاتف", "الإجراءات"]
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
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
            
            # زيادة ارتفاع الصفوف
            self.schools_table.verticalHeader().setDefaultSectionSize(40)
            
            layout.addWidget(self.schools_table)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول المدارس: {e}")
    
    def create_dialog_buttons(self, layout):
        """إنشاء أزرار النافذة"""
        try:
            buttons_frame = QFrame()
            buttons_layout = QHBoxLayout(buttons_frame)
            buttons_layout.addStretch()
            
            close_button = QPushButton("إغلاق")
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
                SELECT id, name_ar, name_en, school_types, principal_name, phone
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
                        school[4] or "",  # المدير
                        school[5] or ""   # الهاتف
                    ]
                    
                    for col, item_text in enumerate(items):
                        item = QTableWidgetItem(item_text)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.schools_table.setItem(row, col, item)
                    
                    # أزرار الإجراءات
                    actions_widget = self.create_actions_widget(school[0])
                    self.schools_table.setCellWidget(row, 6, actions_widget)
                
                log_user_action(f"تم تحميل {len(schools)} مدرسة في الإعدادات المتقدمة")
                
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في تحميل البيانات: {str(e)}")
    
    def create_actions_widget(self, school_id: int):
        """إنشاء ويدجت الإجراءات لكل صف"""
        try:
            widget = QFrame()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(5, 2, 5, 2)
            layout.setSpacing(5)
            
            # زر التعديل
            edit_btn = QPushButton("تعديل")
            edit_btn.setMaximumSize(60, 25)
            edit_btn.clicked.connect(lambda: self.edit_school(school_id))
            layout.addWidget(edit_btn)
            
            # زر الحذف
            delete_btn = QPushButton("حذف")
            delete_btn.setMaximumSize(60, 25)
            delete_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; }")
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
                
                for col in range(1, 6):  # من الاسم إلى الهاتف
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
            if dialog.exec_() == QDialog.Accepted:
                school_data = dialog.get_school_data()
                if school_data:
                    self.school_added.emit(school_data)
                    self.load_schools()
                    QMessageBox.information(self, "نجح", "تم إضافة المدرسة بنجاح")
                    log_user_action(f"تم إضافة مدرسة جديدة: {school_data.get('name_ar', 'غير محدد')}")
                    
        except Exception as e:
            logging.error(f"خطأ في إضافة مدرسة: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في إضافة المدرسة: {str(e)}")
    
    def edit_school(self, school_id: int):
        """تعديل مدرسة"""
        try:
            dialog = EditSchoolDialog(school_id, self)
            if dialog.exec_() == QDialog.Accepted:
                school_data = dialog.get_school_data()
                if school_data:
                    self.school_updated.emit(school_data)
                    self.load_schools()
                    QMessageBox.information(self, "نجح", "تم تحديث المدرسة بنجاح")
                    log_user_action(f"تم تحديث مدرسة: {school_data.get('name_ar', 'غير محدد')}")
                    
        except Exception as e:
            logging.error(f"خطأ في تعديل مدرسة: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في تعديل المدرسة: {str(e)}")
    
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
            }
            
            QTableWidget {
                border: 1px solid #dee2e6;
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #dee2e6;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #dee2e6;
            }
            
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton:pressed {
                background-color: #004085;
            }
            
            QLineEdit {
                border: 1px solid #ced4da;
                padding: 8px;
                border-radius: 4px;
                background-color: white;
            }
            
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
        """)


def show_advanced_settings(parent=None):
    """عرض نافذة الإعدادات المتقدمة مع التحقق من كلمة المرور"""
    try:
        # طلب كلمة المرور
        password, ok = QInputDialog.getText(
            parent,
            "كلمة المرور المطلوبة",
            "أدخل كلمة المرور للوصول إلى الإعدادات المتقدمة:",
            QLineEdit.Password
        )
        
        if not ok:
            return None
        
        # التحقق من كلمة المرور
        if password != "ali4000ali90004444":
            QMessageBox.warning(parent, "خطأ", "كلمة المرور غير صحيحة")
            return None
        
        # عرض نافذة الإعدادات المتقدمة
        dialog = AdvancedSettingsDialog(parent)
        return dialog.exec_()
        
    except Exception as e:
        logging.error(f"خطأ في عرض الإعدادات المتقدمة: {e}")
        QMessageBox.critical(parent, "خطأ", f"خطأ في فتح الإعدادات المتقدمة: {str(e)}")
        return None
