#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة حوار تعيين كلمة مرور التطبيق المحمول (تصميم مبسط)
"""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)

from core.utils.settings_manager import settings_manager


class MobilePasswordDialog(QDialog):
    """نافذة حوار تعيين كلمة مرور التطبيق المحمول (تصميم مبسط)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("كلمة مرور التطبيق المحمول")
        self.resize(350, 200)

        # واجهة المستخدم
        self.current_password_display = QLabel()
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self._setup_ui()
        self._load_current_password()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        layout.addWidget(QLabel("كلمة المرور الحالية:"))
        layout.addWidget(self.current_password_display)

        layout.addWidget(QLabel("كلمة المرور الجديدة:"))
        layout.addWidget(self.new_password_input)

        layout.addWidget(QLabel("تأكيد كلمة المرور:"))
        layout.addWidget(self.confirm_password_input)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self._save_password)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _load_current_password(self):
        try:
            pwd = settings_manager.get_mobile_password()
            text = "*" * len(pwd) if pwd else "غير محددة"
            self.current_password_display.setText(text)
        except Exception as e:
            logging.error(f"خطأ في تحميل كلمة المرور الحالية: {e}")
            self.current_password_display.setText("خطأ")

    def _save_password(self):
        pwd = self.new_password_input.text().strip()
        conf = self.confirm_password_input.text().strip()
        if not pwd:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال كلمة مرور جديدة")
            return
        if pwd != conf:
            QMessageBox.warning(self, "تحذير", "كلمة المرور غير متطابقة")
            return
        if settings_manager.set_mobile_password(pwd):
            QMessageBox.information(self, "نجح", "تم حفظ كلمة المرور")
            self.accept()
        else:
            QMessageBox.critical(self, "خطأ", "فشل في حفظ كلمة المرور")


def show_mobile_password_dialog(parent=None):
    dialog = MobilePasswordDialog(parent)
    return dialog.exec_()
