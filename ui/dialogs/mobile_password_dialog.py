#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة حوار تعيين كلمة مرور التطبيق المحمول (تصميم مبسط)
"""

import logging
import json
import config
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
        
        # حفظ محلياً
        if settings_manager.set_mobile_password(pwd):
            # رفع إلى Supabase
            if self._upload_to_supabase(pwd):
                QMessageBox.information(self, "نجح", "تم حفظ كلمة المرور ورفعها إلى التخزين السحابي")
                self.accept()
            else:
                QMessageBox.warning(self, "تحذير", "تم حفظ كلمة المرور محلياً ولكن فشل في رفعها إلى التخزين السحابي")
                self.accept()
        else:
            QMessageBox.critical(self, "خطأ", "فشل في حفظ كلمة المرور")

    def _upload_to_supabase(self, password):
        """رفع كلمة المرور إلى Supabase كملف JSON"""
        try:
            from supabase import create_client
            
            # إنشاء اتصال Supabase
            supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            bucket = config.SUPABASE_BUCKET
            
            # الحصول على اسم المؤسسة
            org_name = settings_manager.get_organization_name()
            if not org_name:
                logging.error("اسم المؤسسة غير محدد")
                return False
            
            # إنشاء بيانات JSON
            mobile_data = {
                "organization_name": org_name,
                "mobile_password": password,
                "last_updated": "2025-08-22T00:00:00Z"
            }
            
            # تحويل إلى JSON
            json_data = json.dumps(mobile_data, ensure_ascii=False, indent=2)
            json_bytes = json_data.encode('utf-8')
            
            # تحديد مسار الملف في Supabase
            # المسار: backups/{org_name}/mobile_access.json
            safe_org_name = "".join(c for c in org_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_org_name = safe_org_name.replace(' ', '_')
            file_path = f"backups/{safe_org_name}/mobile_access.json"
            
            # رفع الملف
            upload_result = supabase.storage.from_(bucket).upload(
                file_path, 
                json_bytes,
                file_options={"content-type": "application/json", "upsert": "true"}
            )
            
            if upload_result:
                logging.info(f"تم رفع ملف كلمة مرور التطبيق المحمول إلى: {file_path}")
                return True
            else:
                logging.error("فشل في رفع ملف كلمة مرور التطبيق المحمول")
                return False
                
        except ImportError:
            logging.error("مكتبة Supabase غير متوفرة")
            return False
        except Exception as e:
            logging.error(f"خطأ في رفع كلمة المرور إلى Supabase: {e}")
            return False


def show_mobile_password_dialog(parent=None):
    dialog = MobilePasswordDialog(parent)
    return dialog.exec_()
