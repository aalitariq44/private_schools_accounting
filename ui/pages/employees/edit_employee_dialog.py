#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""نافذة تعديل بيانات الموظف (تصميم متجاوب مبسط)."""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDoubleSpinBox, QTextEdit, QMessageBox,
    QGroupBox, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from core.database.connection import db_manager
from core.utils.logger import log_database_operation


class EditEmployeeDialog(QDialog):
    """نافذة تعديل موظف بتصميم متجاوب"""

    def __init__(self, employee_id, parent=None):
        super().__init__(parent)
        self.employee_id = employee_id
        self.setup_ui()
        self.setup_connections()
        self.load_schools()
        self.load_employee_data()
        self.apply_responsive_design()

    # -------- UI --------
    def setup_ui(self):
        self.setWindowTitle("تعديل بيانات الموظف")
        self.setModal(True)
        self.resize(640, 560)
        self.setMinimumSize(460, 480)
        self.setStyleSheet("""
            QDialog { background:#f5f7fa; font-family:'Segoe UI', Arial, sans-serif; }
            QLabel { color:#1f2d3d; font-weight:600; margin:4px 0; }
            QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit { padding:6px 8px; border:1px solid #c0c6ce; border-radius:6px; background:#ffffff; }
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QTextEdit:focus { border:1px solid #357abd; background:#f0f7ff; }
            QPushButton { background:#357abd; color:#fff; border:none; padding:8px 18px; border-radius:6px; font-weight:600; }
            QPushButton:hover { background:#4b8fcc; }
            QPushButton:pressed { background:#2d6399; }
            QPushButton#cancel_btn { background:#c0392b; }
            QPushButton#cancel_btn:hover { background:#d35445; }
            QGroupBox { border:1px solid #d3d8de; border-radius:8px; margin-top:12px; font-weight:600; }
            QGroupBox::title { subcontrol-origin: margin; left:8px; padding:2px 8px; background:#357abd; color:#fff; border-radius:4px; }
            QScrollArea { border:none; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QWidget(); content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)

        title = QLabel("تعديل بيانات الموظف")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background:#357abd; color:#fff; padding:10px; border-radius:6px; font-weight:700;")
        content_layout.addWidget(title)

        # Basic group
        basic_group = QGroupBox("المعلومات الأساسية")
        basic_form = QFormLayout(basic_group)
        basic_form.setSpacing(8); basic_form.setLabelAlignment(Qt.AlignRight)
        self.name_input = QLineEdit(); self.name_input.setPlaceholderText("أدخل اسم الموظف")
        basic_form.addRow("الاسم *:", self.name_input)
        self.school_combo = QComboBox(); self.school_combo.setPlaceholderText("اختر المدرسة")
        basic_form.addRow("المدرسة *:", self.school_combo)
        content_layout.addWidget(basic_group)

        # Job group
        job_group = QGroupBox("الوظيفة")
        job_form = QFormLayout(job_group)
        job_form.setSpacing(8); job_form.setLabelAlignment(Qt.AlignRight)
        self.job_combo = QComboBox()
        for job in ["محاسب", "كاتب", "عامل", "عامل نظافة", "حارس ليلي", "حارس أمن", "سائق", "مساعد", "مساعد إداري", "فني صيانة", "عامل مختبر", "مشرف", "مرشد طلابي", "أمينة مكتبة", "أمين مكتبة", "ممرض"]:
            self.job_combo.addItem(job, job)
        self.job_combo.addItem("مخصص", "مخصص")
        job_form.addRow("المهنة *:", self.job_combo)
        self.custom_job_label = QLabel("المهنة المخصصة *:")
        self.custom_job_input = QLineEdit(); self.custom_job_input.setPlaceholderText("أدخل نوع المهنة")
        job_form.addRow(self.custom_job_label, self.custom_job_input)
        self.custom_job_label.hide(); self.custom_job_input.hide()
        self.salary_input = QDoubleSpinBox(); self.salary_input.setRange(0, 999999); self.salary_input.setDecimals(2); self.salary_input.setSuffix(" د.ع")
        job_form.addRow("الراتب الشهري *:", self.salary_input)
        content_layout.addWidget(job_group)

        # Contact group
        contact_group = QGroupBox("الاتصال والملاحظات")
        contact_form = QFormLayout(contact_group)
        contact_form.setSpacing(8); contact_form.setLabelAlignment(Qt.AlignRight)
        self.phone_input = QLineEdit(); self.phone_input.setPlaceholderText("05xxxxxxxx")
        contact_form.addRow("رقم الهاتف:", self.phone_input)
        self.notes_input = QTextEdit(); self.notes_input.setPlaceholderText("ملاحظات إضافية..."); self.notes_input.setMaximumHeight(90)
        contact_form.addRow("ملاحظات:", self.notes_input)
        content_layout.addWidget(contact_group)

        # Buttons
        btns = QHBoxLayout(); btns.addStretch()
        self.save_btn = QPushButton("حفظ التعديلات")
        self.cancel_btn = QPushButton("إلغاء"); self.cancel_btn.setObjectName("cancel_btn")
        btns.addWidget(self.save_btn); btns.addWidget(self.cancel_btn)
        content_layout.addLayout(btns)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    # -------- Connections & Responsive --------
    def setup_connections(self):
        self.save_btn.clicked.connect(self.save_changes)
        self.cancel_btn.clicked.connect(self.reject)
        self.job_combo.currentTextChanged.connect(self.on_job_changed)

    def apply_responsive_design(self):
        try:
            from PyQt5.QtWidgets import QApplication, QGroupBox, QPushButton
            screen = QApplication.primaryScreen().availableGeometry() if QApplication.primaryScreen() else None
            if not screen:
                return
            sw, sh = screen.width(), screen.height()
            target_w = min(720, int(sw * 0.82))
            target_h = min(630, int(sh * 0.85))
            self.resize(target_w, target_h)
            scale = min(sw / 1920.0, sh / 1080.0)
            base = 14
            pt = max(10, int(base * (0.9 + scale * 0.6)))
            f = self.font(); f.setPointSize(pt); self.setFont(f)
            if sw <= 1366:
                for grp in self.findChildren(QGroupBox):
                    lay = grp.layout()
                    if lay:
                        lay.setHorizontalSpacing(6)
                        lay.setVerticalSpacing(6)
                for btn in self.findChildren(QPushButton):
                    btn.setMinimumHeight(32)
        except Exception as e:
            logging.warning(f"Responsive design adjustment failed (employee edit): {e}")

    # -------- Data Loading --------
    def on_job_changed(self, text):
        custom = (text == "مخصص")
        self.custom_job_label.setVisible(custom)
        self.custom_job_input.setVisible(custom)

    def load_schools(self):
        try:
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT id, name_ar FROM schools ORDER BY name_ar")
                schools = cursor.fetchall()
                self.school_combo.clear(); self.school_combo.addItem("اختر المدرسة", None)
                for s in schools:
                    self.school_combo.addItem(s['name_ar'], s['id'])
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل المدارس:\n{e}")

    def load_employee_data(self):
        try:
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT * FROM employees WHERE id = ?", (self.employee_id,))
                employee = cursor.fetchone()
                if not employee:
                    QMessageBox.warning(self, "خطأ", "لم يتم العثور على بيانات الموظف")
                    self.reject(); return
                self.name_input.setText(employee['name'] or '')
                # school
                for i in range(self.school_combo.count()):
                    if self.school_combo.itemData(i) == employee['school_id']:
                        self.school_combo.setCurrentIndex(i); break
                # job
                default_jobs = ["محاسب", "كاتب", "عامل", "عامل نظافة", "حارس ليلي", "حارس أمن", "سائق", "مساعد", "مساعد إداري", "فني صيانة", "عامل مختبر", "مشرف", "مرشد طلابي", "أمينة مكتبة", "أمين مكتبة", "ممرض"]
                job = employee['job_type']
                if job in default_jobs:
                    for i in range(self.job_combo.count()):
                        if self.job_combo.itemData(i) == job:
                            self.job_combo.setCurrentIndex(i); break
                else:
                    for i in range(self.job_combo.count()):
                        if self.job_combo.itemData(i) == "مخصص":
                            self.job_combo.setCurrentIndex(i); break
                    self.custom_job_input.setText(job)
                    self.custom_job_label.show(); self.custom_job_input.show()
                self.salary_input.setValue(employee['monthly_salary'] or 0)
                self.phone_input.setText(employee['phone'] or '')
                self.notes_input.setPlainText(employee['notes'] or '')
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الموظف: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات الموظف:\n{e}")
            self.reject()

    def validate_data(self):
        try:
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم الموظف"); self.name_input.setFocus(); return False
            if self.school_combo.currentIndex() <= 0 or self.school_combo.currentData() is None:
                QMessageBox.warning(self, "خطأ", "يرجى اختيار المدرسة"); self.school_combo.setFocus(); return False
            if self.salary_input.value() <= 0:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال راتب شهري صحيح"); self.salary_input.setFocus(); return False
            if self.job_combo.currentText() == "مخصص" and not self.custom_job_input.text().strip():
                QMessageBox.warning(self, "خطأ", "يرجى إدخال المهنة المخصصة"); self.custom_job_input.setFocus(); return False
            phone = self.phone_input.text().strip()
            if phone and not phone.replace(' ', '').replace('-', '').isdigit():
                QMessageBox.warning(self, "خطأ", "رقم الهاتف غير صحيح"); self.phone_input.setFocus(); return False
            return True
        except Exception as e:
            logging.error(f"خطأ في التحقق من البيانات: {e}")
            return False

    def save_changes(self):
        if not self.validate_data():
            return
        try:
            job_type = self.job_combo.currentData()
            if self.job_combo.currentText() == "مخصص":
                job_type = self.custom_job_input.text().strip()
            data = {
                'name': self.name_input.text().strip(),
                'school_id': self.school_combo.currentData(),
                'job_type': job_type,
                'monthly_salary': self.salary_input.value(),
                'phone': self.phone_input.text().strip() or None,
                'notes': self.notes_input.toPlainText().strip() or None
            }
            with db_manager.get_cursor() as cursor:
                cursor.execute(
                    """UPDATE employees SET name=?, school_id=?, job_type=?, monthly_salary=?, phone=?, notes=?, updated_at=CURRENT_TIMESTAMP WHERE id=?""",
                    (
                        data['name'], data['school_id'], data['job_type'], data['monthly_salary'],
                        data['phone'], data['notes'], self.employee_id
                    )
                )
                log_database_operation("تعديل موظف", "employees", self.employee_id)
            QMessageBox.information(self, "نجح", "تم حفظ التعديلات بنجاح")
            self.accept()
        except Exception as e:
            logging.error(f"خطأ في حفظ التعديلات: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ التعديلات:\n{e}")
