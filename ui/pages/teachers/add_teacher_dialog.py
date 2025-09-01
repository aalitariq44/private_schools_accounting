#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""نافذة إضافة معلم جديد (تصميم متجاوب مبسط مطابق لنوافذ الطلاب)"""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox,
    QDoubleSpinBox, QTextEdit, QMessageBox,
    QScrollArea, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from core.database.connection import db_manager
from core.utils.logger import log_database_operation


class AddTeacherDialog(QDialog):
    """نافذة إضافة معلم جديد بتصميم متجاوب"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self.load_schools()
        self.apply_responsive_design()

    # ---------------- UI -----------------
    def setup_ui(self):
        """تهيئة عناصر الواجهة (تصميم مبسط يشبه واجهات الطلاب)."""
        self.setWindowTitle("إضافة معلم جديد")
        self.setModal(True)
        self.resize(640, 560)
        self.setMinimumSize(460, 480)

        # ستايل خفيف ومتجاوب
        self.setStyleSheet("""
            QDialog { background:#f5f7fa; font-family:'Segoe UI', Arial, sans-serif; }
            QLabel { color:#1f2d3d; font-weight:600; margin:4px 0; }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
                padding:6px 8px; border:1px solid #c0c6ce; border-radius:6px; background:#ffffff; }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
                border:1px solid #357abd; background:#f0f7ff; }
            QPushButton { background:#357abd; color:#fff; border:none; padding:8px 18px; border-radius:6px; font-weight:600; }
            QPushButton:hover { background:#4b8fcc; }
            QPushButton:pressed { background:#2d6399; }
            QPushButton#cancel_btn { background:#c0392b; }
            QPushButton#cancel_btn:hover { background:#d35445; }
            QScrollArea { border:none; }
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
        content_layout.setSpacing(12)

        title = QLabel("إضافة معلم جديد")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background:#357abd; color:#fff; padding:10px; border-radius:6px; font-weight:700;")
        content_layout.addWidget(title)

        # المعلومات الأساسية
        basic_label = QLabel("المعلومات الأساسية")
        basic_label.setStyleSheet("font-weight:600; margin:4px 0;")
        content_layout.addWidget(basic_label)

        basic_form = QFormLayout()
        basic_form.setSpacing(8)
        basic_form.setLabelAlignment(Qt.AlignRight)

        self.name_input = QLineEdit(); self.name_input.setPlaceholderText("أدخل اسم المعلم")
        basic_form.addRow("الاسم *:", self.name_input)

        self.school_combo = QComboBox(); self.school_combo.setPlaceholderText("اختر المدرسة")
        basic_form.addRow("المدرسة *:", self.school_combo)
        content_layout.addLayout(basic_form)

        # معلومات التدريس
        teach_label = QLabel("معلومات التدريس")
        teach_label.setStyleSheet("font-weight:600; margin:4px 0;")
        content_layout.addWidget(teach_label)

        teach_form = QFormLayout()
        teach_form.setSpacing(8)
        teach_form.setLabelAlignment(Qt.AlignRight)

        self.class_hours_input = QSpinBox(); self.class_hours_input.setRange(0, 50); self.class_hours_input.setSuffix(" حصة")
        teach_form.addRow("عدد الحصص:", self.class_hours_input)

        self.salary_input = QDoubleSpinBox(); self.salary_input.setRange(0, 999999); self.salary_input.setDecimals(2); self.salary_input.setSuffix(" د.ع")
        teach_form.addRow("الراتب الشهري *:", self.salary_input)
        content_layout.addLayout(teach_form)

        # الاتصال والملاحظات
        contact_label = QLabel("الاتصال والملاحظات")
        contact_label.setStyleSheet("font-weight:600; margin:4px 0;")
        content_layout.addWidget(contact_label)

        contact_form = QFormLayout()
        contact_form.setSpacing(8)
        contact_form.setLabelAlignment(Qt.AlignRight)

        self.phone_input = QLineEdit(); self.phone_input.setPlaceholderText("05xxxxxxxx")
        contact_form.addRow("رقم الهاتف:", self.phone_input)

        self.notes_input = QTextEdit(); self.notes_input.setPlaceholderText("ملاحظات إضافية..."); self.notes_input.setMaximumHeight(90)
        contact_form.addRow("ملاحظات:", self.notes_input)
        content_layout.addLayout(contact_form)

        # الأزرار
        btns = QHBoxLayout(); btns.addStretch()
        self.add_btn = QPushButton("حفظ المعلم")
        self.cancel_btn = QPushButton("إلغاء"); self.cancel_btn.setObjectName("cancel_btn")
        btns.addWidget(self.add_btn); btns.addWidget(self.cancel_btn)
        content_layout.addLayout(btns)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    # ------------- Connections & Responsive -------------
    def setup_connections(self):
        self.add_btn.clicked.connect(self.add_teacher)
        self.cancel_btn.clicked.connect(self.reject)

    def apply_responsive_design(self):
        """ضبط الحجم والخط حسب دقة الشاشة (مشابه للطلاب)."""
        try:
            from PyQt5.QtWidgets import QApplication, QGroupBox
            screen = QApplication.primaryScreen().availableGeometry() if QApplication.primaryScreen() else None
            if not screen:
                return
            sw, sh = screen.width(), screen.height()
            target_w = min(720, int(sw * 0.82))
            target_h = min(630, int(sh * 0.85))
            self.resize(target_w, target_h)

            scale = min(sw / 1920.0, sh / 1080.0)
            base = 14
            point_size = max(10, int(base * (0.9 + scale * 0.6)))
            f = self.font(); f.setPointSize(point_size); self.setFont(f)

            if sw <= 1366:
                for btn in self.findChildren(QPushButton):
                    btn.setMinimumHeight(32)
        except Exception as e:
            logging.warning(f"Responsive design adjustment failed (teacher add): {e}")

    # ------------- Data Loading & Validation -------------
    def load_schools(self):
        try:
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT id, name_ar FROM schools ORDER BY name_ar")
                schools = cursor.fetchall()
                self.school_combo.clear()
                self.school_combo.addItem("اختر المدرسة", None)
                for s in schools:
                    self.school_combo.addItem(s['name_ar'], s['id'])
                if schools:
                    self.school_combo.setCurrentIndex(1)
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل المدارس:\n{e}")

    def validate_data(self):
        try:
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم المعلم")
                self.name_input.setFocus(); return False
            if self.school_combo.currentIndex() <= 0 or self.school_combo.currentData() is None:
                QMessageBox.warning(self, "خطأ", "يرجى اختيار المدرسة")
                self.school_combo.setFocus(); return False
            if self.salary_input.value() <= 0:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال راتب شهري صحيح")
                self.salary_input.setFocus(); return False
            phone = self.phone_input.text().strip()
            if phone and not phone.replace(' ', '').replace('-', '').isdigit():
                QMessageBox.warning(self, "خطأ", "رقم الهاتف غير صحيح")
                self.phone_input.setFocus(); return False
            return True
        except Exception as e:
            logging.error(f"خطأ في التحقق من البيانات: {e}")
            return False

    # ------------- Save Operation -------------
    def add_teacher(self):
        if not self.validate_data():
            return
        try:
            # التحقق من عدد المعلمين (نسخة تجريبية)
            result = db_manager.execute_fetch_one("SELECT COUNT(*) as count FROM teachers")
            teachers_count = result['count'] if result else 0
            
            if teachers_count >= 4:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("نسخة تجريبية")
                msg.setText("هذه نسخة تجريبية ولا يمكن إضافة أكثر من 4 معلمين")
                msg.setInformativeText(
                    "واتساب: 07859371349\n"
                    "تليجرام: @tech_solu"
                )
                msg.setLayoutDirection(Qt.RightToLeft)
                msg.exec_()
                return
            
            teacher_data = {
                'name': self.name_input.text().strip(),
                'school_id': self.school_combo.currentData(),
                'class_hours': self.class_hours_input.value(),
                'monthly_salary': self.salary_input.value(),
                'phone': self.phone_input.text().strip() or None,
                'notes': self.notes_input.toPlainText().strip() or None
            }
            with db_manager.get_cursor() as cursor:
                cursor.execute(
                    """INSERT INTO teachers (name, school_id, class_hours, monthly_salary, phone, notes)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        teacher_data['name'],
                        teacher_data['school_id'],
                        teacher_data['class_hours'],
                        teacher_data['monthly_salary'],
                        teacher_data['phone'],
                        teacher_data['notes']
                    )
                )
                teacher_id = cursor.lastrowid
                log_database_operation("إضافة معلم", "teachers", teacher_id)
            QMessageBox.information(self, "نجح", "تم إضافة المعلم بنجاح!")
            self.accept()
        except Exception as e:
            logging.error(f"خطأ في إضافة المعلم: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في إضافة المعلم:\n{e}")
