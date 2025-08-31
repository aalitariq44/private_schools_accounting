#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة تعديل بيانات الراتب
"""
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QDoubleSpinBox, QDateEdit, QTextEdit,
    QPushButton, QMessageBox, QFrame, QScrollArea, QWidget, QComboBox
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal

from core.database.connection import db_manager
from core.utils.logger import log_user_action

class EditSalaryDialog(QDialog):
    """نافذة تعديل بيانات الراتب"""
    salary_updated = pyqtSignal()

    def __init__(self, salary_id, parent=None):
        super().__init__(parent)
        self.salary_id = salary_id
        self.salary_data = None
        self.staff_list = []
        self.setWindowTitle(f"تعديل الراتب #{salary_id}")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        self.setup_connections()
        self.load_salary_data()
        self.apply_responsive_design()

    def setup_ui(self):
        self.setWindowTitle(f"تعديل الراتب #{self.salary_id}")
        self.setModal(True)
        self.resize(640, 520)
        self.setMinimumSize(480, 420)

        # ستايل موحد
        self.setStyleSheet("""
            QDialog { background:#f5f7fa; font-family:'Segoe UI', Arial, sans-serif; }
            QLabel { color:#1f2d3d; font-weight:600; margin:4px 0; }
            QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit {
                padding:6px 8px; border:1px solid #c0c6ce; border-radius:6px; background:#ffffff;
                min-height: 32px; }
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTextEdit:focus {
                border:1px solid #357abd; background:#f0f7ff; }
            QPushButton { background:#357abd; color:#fff; border:none; padding:8px 18px; border-radius:6px; font-weight:600;
                min-height: 36px; }
            QPushButton:hover { background:#4b8fcc; }
            QPushButton:pressed { background:#2d6399; }
            QPushButton#cancel_btn { background:#c0392b; }
            QPushButton#cancel_btn:hover { background:#d35445; }
            QLabel#salaryLabel { color:#27ae60; font-weight:600; }
            QLabel#daysLabel { color:#c0392b; font-weight:600; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(15)

        # عنوان النافذة
        title_label = QLabel(f"تعديل الراتب #{self.salary_id}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("background:#357abd; color:#fff; padding:10px; border-radius:6px; font-weight:700; font-size:16px;")
        content_layout.addWidget(title_label)

        # قسم بيانات الموظف
        staff_widget = self.create_staff_group()
        content_layout.addWidget(staff_widget)

        # قسم تفاصيل الراتب
        salary_widget = self.create_salary_section()
        content_layout.addWidget(salary_widget)

        # قسم فترة الراتب
        period_widget = self.create_period_section()
        content_layout.addWidget(period_widget)

        # قسم الملاحظات
        notes_widget = self.create_notes_section()
        content_layout.addWidget(notes_widget)

        # الأزرار
        buttons_layout = self.create_buttons_section()
        content_layout.addLayout(buttons_layout)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
    def setup_connections(self):
        """إعداد الاتصالات والأحداث"""
        self.from_date_input.dateChanged.connect(self.calculate_days)
        self.to_date_input.dateChanged.connect(self.calculate_days)
        
    def calculate_days(self):
        """حساب عدد الأيام بين التاريخين"""
        from_date = self.from_date_input.date()
        to_date = self.to_date_input.date()
        
        if from_date <= to_date:
            days = from_date.daysTo(to_date) + 1  # +1 لتضمين اليوم الأخير
            self.days_count_label.setText(f"{days} يوم")
            self.days_count_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.days_count_label.setText("تاريخ غير صحيح!")
            self.days_count_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def create_staff_group(self):
        """إنشاء قسم بيانات الموظف/المعلم"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        # عنوان القسم
        title_label = QLabel("بيانات الموظف/المعلم")
        title_label.setStyleSheet("font-weight: bold; color: #357abd; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # نموذج البيانات
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.school_combo = QComboBox()
        self.school_combo.setEnabled(False)  # مقفل
        form_layout.addRow("المدرسة:", self.school_combo)
        
        self.staff_type_combo = QComboBox()
        self.staff_type_combo.setEnabled(False)  # مقفل
        form_layout.addRow("نوع الموظف:", self.staff_type_combo)
        
        self.staff_combo = QComboBox()
        self.staff_combo.setEnabled(False)  # مقفل
        form_layout.addRow("الموظف/المعلم:", self.staff_combo)
        
        self.base_salary_label = QLabel("0.00 دينار")
        self.base_salary_label.setObjectName("salaryLabel")
        form_layout.addRow("الراتب المسجل:", self.base_salary_label)
        
        layout.addLayout(form_layout)
        return widget
    
    def create_salary_section(self):
        """إنشاء قسم تفاصيل الراتب"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        # عنوان القسم
        title_label = QLabel("تفاصيل الراتب")
        title_label.setStyleSheet("font-weight: bold; color: #357abd; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # نموذج البيانات
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.paid_amount_input = QDoubleSpinBox()
        self.paid_amount_input.setRange(0, 999999999)
        self.paid_amount_input.setDecimals(2)
        self.paid_amount_input.setSuffix(" دينار")
        form_layout.addRow("المبلغ المدفوع:", self.paid_amount_input)
        
        self.payment_date_input = QDateEdit()
        self.payment_date_input.setCalendarPopup(True)
        form_layout.addRow("تاريخ الدفع:", self.payment_date_input)
        
        layout.addLayout(form_layout)
        return widget
    
    def create_period_section(self):
        """إنشاء قسم فترة الراتب"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        # عنوان القسم
        title_label = QLabel("فترة الراتب")
        title_label.setStyleSheet("font-weight: bold; color: #357abd; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # نموذج البيانات
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.from_date_input = QDateEdit()
        self.from_date_input.setCalendarPopup(True)
        form_layout.addRow("من تاريخ:", self.from_date_input)
        
        self.to_date_input = QDateEdit()
        self.to_date_input.setCalendarPopup(True)
        form_layout.addRow("إلى تاريخ:", self.to_date_input)
        
        self.days_count_label = QLabel("30 يوم")
        self.days_count_label.setObjectName("daysLabel")
        form_layout.addRow("عدد الأيام:", self.days_count_label)
        
        layout.addLayout(form_layout)
        return widget
    
    def create_notes_section(self):
        """إنشاء قسم الملاحظات"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        # عنوان القسم
        title_label = QLabel("ملاحظات")
        title_label.setStyleSheet("font-weight: bold; color: #357abd; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # حقل الملاحظات
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("ملاحظات إضافية...")
        layout.addWidget(self.notes_input)
        
        return widget
    
    def create_buttons_section(self):
        """إنشاء قسم الأزرار"""
        layout = QHBoxLayout()
        layout.addStretch()
        
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("حفظ التعديلات")
        self.save_btn.clicked.connect(self.save_changes)
        layout.addWidget(self.save_btn)
        
        return layout

    def apply_responsive_design(self):
        """ضبط الحجم والخط حسب دقة الشاشة"""
        try:
            from PyQt5.QtWidgets import QApplication, QPushButton
            screen = QApplication.primaryScreen().availableGeometry() if QApplication.primaryScreen() else None
            if not screen:
                return
            sw, sh = screen.width(), screen.height()
            target_w = min(760, int(sw * 0.82))
            target_h = min(680, int(sh * 0.85))
            self.resize(target_w, target_h)

            scale = min(sw / 1920.0, sh / 1080.0)
            base = 14
            point_size = max(10, int(base * (0.9 + scale * 0.6)))
            f = self.font()
            f.setPointSize(point_size)
            self.setFont(f)

            if sw <= 1366:
                for btn in self.findChildren(QPushButton):
                    btn.setMinimumHeight(32)
        except Exception as e:
            logging.warning(f"Responsive design adjustment failed (salary edit): {e}")

    def load_salary_data(self):
        try:
            query = "SELECT * FROM salaries WHERE id = ?"
            rows = db_manager.execute_query(query, (self.salary_id,))
            if not rows:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على بيانات الراتب.")
                self.reject()
                return
            self.salary_data = rows[0]
            
            # جلب بيانات الموظف والمدرسة
            staff_type = self.salary_data['staff_type']
            staff_id = self.salary_data['staff_id']
            school_id = self.salary_data['school_id']
            base_salary = self.salary_data['base_salary'] or 0
            
            # جلب اسم المدرسة
            school_name = ""
            if school_id:
                school_query = "SELECT name_ar FROM schools WHERE id = ?"
                school_rows = db_manager.execute_query(school_query, (school_id,))
                if school_rows:
                    school_name = school_rows[0]['name_ar']
            
            # جلب اسم الموظف
            staff_name = ""
            if staff_type and staff_id:
                if staff_type == 'teacher':
                    staff_query = "SELECT name FROM teachers WHERE id = ?"
                elif staff_type == 'employee':
                    staff_query = "SELECT name FROM employees WHERE id = ?"
                else:
                    staff_query = None
                
                if staff_query:
                    staff_rows = db_manager.execute_query(staff_query, (staff_id,))
                    if staff_rows:
                        staff_name = staff_rows[0]['name']
            
            # تعبئة الحقول المقفلة
            self.school_combo.clear()
            self.school_combo.addItem(school_name or "غير محدد", school_id)
            
            self.staff_type_combo.clear()
            type_display = "معلم" if staff_type == "teacher" else "موظف"
            self.staff_type_combo.addItem(type_display, staff_type)
            
            self.staff_combo.clear()
            display_text = f"{staff_name} - {school_name or 'غير محدد'} ({type_display})"
            self.staff_combo.addItem(display_text)
            
            self.base_salary_label.setText(f"{base_salary:.2f} دينار")
            
            # تعبئة الحقول الأخرى
            # المبلغ المدفوع
            paid = self.salary_data['paid_amount'] or 0
            self.paid_amount_input.setValue(float(paid))
            # تاريخ الدفع
            pay_date = self.salary_data['payment_date']
            if pay_date:
                self.payment_date_input.setDate(QDate.fromString(pay_date, Qt.ISODate))
            # فترة الراتب من
            from_d = self.salary_data['from_date']
            if from_d:
                self.from_date_input.setDate(QDate.fromString(from_d, Qt.ISODate))
            # فترة الراتب إلى
            to_d = self.salary_data['to_date']
            if to_d:
                self.to_date_input.setDate(QDate.fromString(to_d, Qt.ISODate))
            # الملاحظات
            notes = self.salary_data['notes']
            self.notes_input.setPlainText(notes or '')
            
            # حساب الأيام
            self.calculate_days()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الراتب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في جلب بيانات الراتب:\n{e}")
            self.reject()

    def save_changes(self):
        if self.from_date_input.date() > self.to_date_input.date():
            QMessageBox.warning(self, "تحذير", "تاريخ البداية يجب أن يكون قبل تاريخ النهاية.")
            return
        if self.paid_amount_input.value() <= 0:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال مبلغ صحيح")
            return
        days = self.from_date_input.date().daysTo(self.to_date_input.date()) + 1
        payment_date = self.payment_date_input.date().toString(Qt.ISODate)
        notes = self.notes_input.toPlainText().strip() or None
        try:
            query = ("UPDATE salaries SET paid_amount = ?, from_date = ?, to_date = ?, "
                     "days_count = ?, payment_date = ?, notes = ? WHERE id = ?")
            params = (
                self.paid_amount_input.value(),
                self.from_date_input.date().toString(Qt.ISODate),
                self.to_date_input.date().toString(Qt.ISODate),
                days,
                payment_date,
                notes,
                self.salary_id
            )
            db_manager.execute_update(query, params)
            log_user_action(f"تعديل الراتب {self.salary_id}", f"المبلغ: {self.paid_amount_input.value()}")
            QMessageBox.information(self, "نجح", "تم حفظ التعديلات بنجاح.")
            self.salary_updated.emit()
            self.accept()
        except Exception as e:
            logging.error(f"خطأ في حفظ التعديلات: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ التعديلات:\n{e}")
