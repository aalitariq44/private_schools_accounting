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
    QPushButton, QMessageBox, QFrame
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
        self.setWindowTitle(f"تعديل الراتب #{salary_id}")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        self.load_salary_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        # المبلغ المدفوع
        self.paid_amount_input = QDoubleSpinBox()
        self.paid_amount_input.setRange(0, 1e9)
        self.paid_amount_input.setDecimals(2)
        self.paid_amount_input.setSuffix(" دينار")
        form.addRow("المبلغ المدفوع:", self.paid_amount_input)
        # تاريخ الدفع
        self.payment_date_input = QDateEdit()
        self.payment_date_input.setCalendarPopup(True)
        form.addRow("تاريخ الدفع:", self.payment_date_input)
        # فترة الراتب من
        self.from_date_input = QDateEdit()
        self.from_date_input.setCalendarPopup(True)
        form.addRow("من تاريخ:", self.from_date_input)
        # إلى
        self.to_date_input = QDateEdit()
        self.to_date_input.setCalendarPopup(True)
        form.addRow("إلى تاريخ:", self.to_date_input)
        # الملاحظات
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("نص الملاحظات...")
        form.addRow("ملاحظات:", self.notes_input)
        layout.addLayout(form)
        # الأزرار
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.addStretch()
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        self.save_btn = QPushButton("حفظ التعديلات")
        self.save_btn.clicked.connect(self.save_changes)
        btn_layout.addWidget(self.save_btn)
        layout.addWidget(btn_frame)

    def load_salary_data(self):
        try:
            query = "SELECT * FROM salaries WHERE id = ?"
            rows = db_manager.execute_query(query, (self.salary_id,))
            if not rows:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على بيانات الراتب.")
                self.reject()
                return
            self.salary_data = rows[0]
            # تعبئة الحقول
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
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الراتب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في جلب بيانات الراتب:\n{e}")
            self.reject()

    def save_changes(self):
        if self.from_date_input.date() > self.to_date_input.date():
            QMessageBox.warning(self, "تحذير", "تاريخ البداية يجب أن يكون قبل تاريخ النهاية.")
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
