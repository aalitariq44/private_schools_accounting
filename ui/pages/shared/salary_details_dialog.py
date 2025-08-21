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
    QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

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
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_salary_data()
        
        log_user_action(f"فتح تفاصيل رواتب {self.person_type} {person_name}")

    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle(f"تفاصيل رواتب {self.person_name}")
        self.setModal(True)
        self.resize(1400, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # عنوان النافذة
        self.create_header(layout)
        
        # تخطيط أفقي للجدول ونموذج الإضافة
        content_layout = QHBoxLayout()
        
        # جدول الرواتب
        self.create_salaries_table(content_layout)
        
        # نموذج إضافة راتب
        self.create_add_salary_form(content_layout)
        
        layout.addLayout(content_layout)
        
        # أزرار النافذة
        self.create_dialog_buttons(layout)

    def create_header(self, layout):
        """إنشاء رأس النافذة"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel(f"تفاصيل رواتب: {self.person_name}")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        type_label = QLabel(f"النوع: {'معلم' if self.person_type == 'teacher' else 'موظف'}")
        type_label.setObjectName("subtitleLabel")
        type_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(type_label)
        
        layout.addWidget(header_frame)

    def create_salaries_table(self, layout):
        """إنشاء جدول الرواتب"""
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        table_layout = QVBoxLayout(table_frame)
        
        table_title = QLabel("سجل الرواتب")
        table_title.setObjectName("sectionTitle")
        table_layout.addWidget(table_title)
        
        self.salaries_table = QTableWidget()
        self.salaries_table.setObjectName("salariesTable")
        
        columns = ["المعرف", "التاريخ", "المبلغ", "الراتب الأساسي", "من تاريخ", "إلى تاريخ", "عدد الأيام", "الملاحظات"]
        self.salaries_table.setColumnCount(len(columns))
        self.salaries_table.setHorizontalHeaderLabels(columns)
        
        self.salaries_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.salaries_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.salaries_table.setAlternatingRowColors(True)
        self.salaries_table.setSortingEnabled(True)
        
        # إخفاء عمود المعرف
        self.salaries_table.setColumnHidden(0, True)
        
        header = self.salaries_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        table_layout.addWidget(self.salaries_table)
        layout.addWidget(table_frame)

    def create_add_salary_form(self, layout):
        """إنشاء نموذج إضافة راتب"""
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_frame.setMaximumWidth(350)
        form_layout = QVBoxLayout(form_frame)
        
        form_title = QLabel("إضافة راتب جديد")
        form_title.setObjectName("sectionTitle")
        form_layout.addWidget(form_title)
        
        # نموذج الإدخال
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        # التاريخ
        grid_layout.addWidget(QLabel("التاريخ:"), 0, 0)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        grid_layout.addWidget(self.date_edit, 0, 1)
        
        # المبلغ المدفوع
        grid_layout.addWidget(QLabel("المبلغ المدفوع:"), 1, 0)
        self.amount_edit = QDoubleSpinBox()
        self.amount_edit.setRange(0, 999999999)
        self.amount_edit.setSuffix(" د.ع")
        grid_layout.addWidget(self.amount_edit, 1, 1)
        
        # الراتب الأساسي
        grid_layout.addWidget(QLabel("الراتب الأساسي:"), 2, 0)
        self.base_salary_edit = QDoubleSpinBox()
        self.base_salary_edit.setRange(0, 999999999)
        self.base_salary_edit.setSuffix(" د.ع")
        grid_layout.addWidget(self.base_salary_edit, 2, 1)
        
        # من تاريخ
        grid_layout.addWidget(QLabel("من تاريخ:"), 3, 0)
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.from_date_edit.setCalendarPopup(True)
        grid_layout.addWidget(self.from_date_edit, 3, 1)
        
        # إلى تاريخ
        grid_layout.addWidget(QLabel("إلى تاريخ:"), 4, 0)
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setDate(QDate.currentDate())
        self.to_date_edit.setCalendarPopup(True)
        grid_layout.addWidget(self.to_date_edit, 4, 1)
        
        # عدد الأيام
        grid_layout.addWidget(QLabel("عدد الأيام:"), 5, 0)
        self.days_edit = QLineEdit()
        self.days_edit.setText("30")
        grid_layout.addWidget(self.days_edit, 5, 1)
        
        # الملاحظات
        grid_layout.addWidget(QLabel("الملاحظات:"), 6, 0)
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        grid_layout.addWidget(self.notes_edit, 6, 1)
        
        form_layout.addLayout(grid_layout)
        
        # زر الإضافة
        self.add_salary_button = QPushButton("إضافة راتب")
        self.add_salary_button.setObjectName("addButton")
        form_layout.addWidget(self.add_salary_button)
        
        # مساحة فارغة
        form_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        layout.addWidget(form_frame)

    def create_dialog_buttons(self, layout):
        """إنشاء أزرار النافذة"""
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.refresh_button = QPushButton("تحديث")
        self.refresh_button.setObjectName("secondaryButton")
        buttons_layout.addWidget(self.refresh_button)
        
        self.close_button = QPushButton("إغلاق")
        self.close_button.setObjectName("closeButton")
        buttons_layout.addWidget(self.close_button)
        
        layout.addLayout(buttons_layout)

    def setup_styles(self):
        """إعداد الأنماط"""
        style = """
            QDialog {
                background-color: #F8F9FA;
                font-family: 'Cairo', Arial;
                font-size: 14px;
            }
            #headerFrame {
                background-color: white;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
            }
            #titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2C3E50;
                margin-bottom: 5px;
            }
            #subtitleLabel {
                font-size: 14px;
                color: #7F8C8D;
            }
            #tableFrame, #formFrame {
                background-color: white;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            #sectionTitle {
                font-size: 16px;
                font-weight: bold;
                color: #2C3E50;
                margin-bottom: 10px;
                padding-bottom: 5px;
                border-bottom: 2px solid #3498DB;
            }
            #salariesTable {
                background-color: white;
                border: 1px solid #E9ECEF;
                border-radius: 6px;
                font-size: 13px;
            }
            #salariesTable::item {
                padding: 8px;
                border-bottom: 1px solid #E9ECEF;
            }
            #salariesTable::item:selected {
                background-color: #3498DB;
                color: white;
            }
            QHeaderView::section {
                background-color: #3498DB;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QLabel {
                font-size: 14px;
                color: #2C3E50;
            }
            QLineEdit, QDoubleSpinBox, QDateEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                font-size: 14px;
                background-color: white;
            }
            #addButton {
                background-color: #27AE60;
                border: none;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            #addButton:hover {
                background-color: #229954;
            }
            #secondaryButton {
                background-color: #3498DB;
                border: none;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            #closeButton {
                background-color: #95A5A6;
                border: none;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
        """
        self.setStyleSheet(style)

    def setup_connections(self):
        """ربط الإشارات"""
        self.add_salary_button.clicked.connect(self.add_salary)
        self.refresh_button.clicked.connect(self.load_salary_data)
        self.close_button.clicked.connect(self.accept)
        
        # ربط حساب الراتب تلقائياً
        self.base_salary_edit.valueChanged.connect(self.calculate_salary)
        self.days_edit.textChanged.connect(self.calculate_salary)
        self.from_date_edit.dateChanged.connect(self.calculate_days)
        self.to_date_edit.dateChanged.connect(self.calculate_days)

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
            
            self.salaries_data = db_manager.execute_query(query, (staff_type, self.person_id))
            self.populate_salaries_table()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الرواتب: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل بيانات الرواتب:\n{str(e)}")

    def populate_salaries_table(self):
        """ملء جدول الرواتب"""
        try:
            self.salaries_table.setRowCount(0)
            
            if not self.salaries_data:
                return
            
            for row_idx, salary in enumerate(self.salaries_data):
                self.salaries_table.insertRow(row_idx)
                
                # تنسيق التواريخ
                payment_date = salary['payment_date']
                from_date = salary['from_date']
                to_date = salary['to_date']
                
                if isinstance(payment_date, str):
                    try:
                        payment_date = datetime.strptime(payment_date, '%Y-%m-%d').strftime('%Y-%m-%d')
                    except:
                        pass
                
                if isinstance(from_date, str):
                    try:
                        from_date = datetime.strptime(from_date, '%Y-%m-%d').strftime('%Y-%m-%d')
                    except:
                        pass
                
                if isinstance(to_date, str):
                    try:
                        to_date = datetime.strptime(to_date, '%Y-%m-%d').strftime('%Y-%m-%d')
                    except:
                        pass
                
                items = [
                    str(salary['id']),
                    str(payment_date),
                    f"{salary['paid_amount']:,.0f} د.ع" if salary['paid_amount'] else "0 د.ع",
                    f"{salary['base_salary']:,.0f} د.ع" if salary['base_salary'] else "0 د.ع",
                    str(from_date or ""),
                    str(to_date or ""),
                    str(salary['days_count'] or ""),
                    salary['notes'] or ""
                ]
                
                for col_idx, item_text in enumerate(items):
                    item = QTableWidgetItem(item_text)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.salaries_table.setItem(row_idx, col_idx, item)
            
            # تحسين عرض الأعمدة
            header = self.salaries_table.horizontalHeader()
            for i in range(1, self.salaries_table.columnCount()):
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول الرواتب: {e}")

    def add_salary(self):
        """إضافة راتب جديد"""
        try:
            # التحقق من صحة البيانات
            if self.amount_edit.value() <= 0:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال مبلغ مدفوع صحيح")
                return
            
            if self.base_salary_edit.value() <= 0:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال راتب أساسي صحيح")
                return
            
            if not self.days_edit.text().strip():
                QMessageBox.warning(self, "خطأ", "يرجى إدخال عدد الأيام")
                return
            
            try:
                days_count = int(self.days_edit.text())
                if days_count <= 0:
                    raise ValueError()
            except ValueError:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال عدد أيام صحيح")
                return
            
            # تأكيد الإضافة
            reply = QMessageBox.question(
                self, "تأكيد الإضافة",
                f"هل تريد إضافة راتب بمبلغ {self.amount_edit.value():,.0f} د.ع؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # الحصول على school_id من المعلم أو الموظف
            staff_type = "teacher" if self.person_type == "teacher" else "employee"
            table_name = "teachers" if self.person_type == "teacher" else "employees"
            
            school_query = f"SELECT school_id FROM {table_name} WHERE id = ?"
            school_result = db_manager.execute_query(school_query, (self.person_id,))
            
            if not school_result:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على المعلم/الموظف")
                return
            
            school_id = school_result[0]['school_id']
            
            # إدراج البيانات في قاعدة البيانات
            query = """
                INSERT INTO salaries (staff_type, staff_id, base_salary, paid_amount, 
                                    from_date, to_date, days_count, payment_date, notes, school_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                staff_type,
                self.person_id,
                self.base_salary_edit.value(),
                self.amount_edit.value(),
                self.from_date_edit.date().toString('yyyy-MM-dd'),
                self.to_date_edit.date().toString('yyyy-MM-dd'),
                days_count,
                self.date_edit.date().toString('yyyy-MM-dd'),
                self.notes_edit.toPlainText().strip(),
                school_id
            )
            
            affected_rows = db_manager.execute_update(query, params)
            
            if affected_rows > 0:
                QMessageBox.information(self, "نجح", "تم إضافة الراتب بنجاح")
                self.clear_form()
                self.load_salary_data()
                log_user_action(f"إضافة راتب جديد للـ{self.person_type} {self.person_name}", "نجح")
            else:
                QMessageBox.warning(self, "خطأ", "فشل في إضافة الراتب")
            
        except Exception as e:
            logging.error(f"خطأ في إضافة راتب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في إضافة الراتب:\n{str(e)}")

    def clear_form(self):
        """مسح نموذج الإدخال"""
        self.date_edit.setDate(QDate.currentDate())
        self.amount_edit.setValue(0)
        self.base_salary_edit.setValue(0)
        self.from_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.to_date_edit.setDate(QDate.currentDate())
        self.days_edit.setText("30")
        self.notes_edit.clear()

    def calculate_days(self):
        """حساب عدد الأيام بناءً على التواريخ"""
        try:
            from_date = self.from_date_edit.date().toPyDate()
            to_date = self.to_date_edit.date().toPyDate()
            
            if to_date >= from_date:
                days = (to_date - from_date).days + 1
                self.days_edit.setText(str(days))
            
        except Exception as e:
            logging.debug(f"خطأ في حساب الأيام: {e}")

    def calculate_salary(self):
        """حساب الراتب بناءً على الراتب الأساسي وعدد الأيام"""
        try:
            base_salary = self.base_salary_edit.value()
            days_text = self.days_edit.text().strip()
            
            if not days_text or base_salary <= 0:
                return
            
            days = int(days_text)
            if days <= 0:
                return
            
            # حساب الراتب اليومي (الراتب الشهري / 30)
            daily_salary = base_salary / 30
            calculated_amount = daily_salary * days
            
            self.amount_edit.setValue(calculated_amount)
            
        except (ValueError, ZeroDivisionError) as e:
            logging.debug(f"خطأ في حساب الراتب: {e}")
