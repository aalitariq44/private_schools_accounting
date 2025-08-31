#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة تعديل بيانات المصروف
"""

import logging
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QLabel, QMessageBox, QFrame,
    QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation


class EditExpenseDialog(QDialog):
    """نافذة تعديل بيانات المصروف"""
    
    def __init__(self, expense_id, parent=None):
        super().__init__(parent)
        self.expense_id = expense_id
        self.expense_data = None

        self.setWindowTitle("تعديل بيانات المصروف")
        self.setModal(True)
        self.resize(660, 600)
        self.setMinimumSize(480, 500)

        self.setup_ui()
        self.load_schools()
        self.load_expense_data()
        self.apply_responsive_design()

        if hasattr(self, 'title_input'):
            self.title_input.setFocus()
    
    def setup_ui(self):
        try:
            self.setStyleSheet("""
                QDialog { background:#f5f7fa; font-family:'Segoe UI', Arial, sans-serif; }
                QLabel { color:#1f2d3d; font-weight:600; margin:4px 0; }
                QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit {
                    padding:6px 8px; border:1px solid #c0c6ce; border-radius:6px; background:#ffffff; }
                QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTextEdit:focus {
                    border:1px solid #c83d30; background:#fff4f3; }
                QPushButton { background:#c83d30; color:#fff; border:none; padding:8px 18px; border-radius:6px; font-weight:600; }
                QPushButton:hover { background:#d7574b; }
                QPushButton:pressed { background:#b73226; }
                QPushButton#cancel_btn { background:#6c757d; }
                QPushButton#cancel_btn:hover { background:#5a6268; }
                QPushButton#delete_btn { background:#dc3545; }
                QPushButton#delete_btn:hover { background:#c82333; }
                QScrollArea { border:none; }
            """)

            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(6, 6, 6, 6)
            main_layout.setSpacing(6)

            scroll = QScrollArea(); scroll.setWidgetResizable(True)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            content = QWidget()
            content_layout = QVBoxLayout(content)
            content_layout.setContentsMargins(12, 12, 12, 12)
            content_layout.setSpacing(12)

            self.create_header(content_layout)
            self.create_basic_info_section(content_layout)
            self.create_additional_details_section(content_layout)
            self.create_buttons_section(content_layout)

            scroll.setWidget(content)
            main_layout.addWidget(scroll)
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة تعديل المصروف: {e}")
            raise
    
    def create_header(self, layout):
        try:
            title = QLabel(f"تعديل بيانات المصروف #{self.expense_id}")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("background:#c83d30; color:#fff; padding:10px; border-radius:6px; font-weight:700;")
            layout.addWidget(title)
        except Exception as e:
            logging.error(f"خطأ في إنشاء رأس النافذة: {e}")
    
    def create_basic_info_section(self, layout):
        try:
            basic_label = QLabel("المعلومات الأساسية")
            basic_label.setStyleSheet("font-weight:600; margin:4px 0;")
            layout.addWidget(basic_label)

            form = QFormLayout()
            form.setSpacing(8)
            form.setLabelAlignment(Qt.AlignRight)

            self.title_input = QLineEdit(); self.title_input.setPlaceholderText("أدخل وصف المصروف")
            form.addRow("الوصف *:", self.title_input)

            self.amount_input = QDoubleSpinBox(); self.amount_input.setRange(0.01, 999999999.99); self.amount_input.setDecimals(2); self.amount_input.setSuffix(" د.ع")
            form.addRow("المبلغ *:", self.amount_input)

            self.school_combo = QComboBox(); self.school_combo.setPlaceholderText("اختر المدرسة")
            form.addRow("المدرسة *:", self.school_combo)

            self.expense_date = QDateEdit(); self.expense_date.setDate(QDate.currentDate()); self.expense_date.setCalendarPopup(True)
            form.addRow("التاريخ *:", self.expense_date)

            self.category_combo = QComboBox(); self.category_combo.addItems([
                "-- اختر الفئة --", "الرواتب", "المواد التعليمية", "الخدمات", "الصيانة", "الكهرباء والماء", "النظافة", "المكتبية", "النقل", "التأمين", "أخرى"
            ])
            form.addRow("الفئة *:", self.category_combo)

            layout.addLayout(form)
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم المعلومات الأساسية: {e}")
    
    
    def create_additional_details_section(self, layout):
        try:
            details_label = QLabel("تفاصيل إضافية")
            details_label.setStyleSheet("font-weight:600; margin:4px 0;")
            layout.addWidget(details_label)

            form = QFormLayout()
            form.setSpacing(8)
            form.setLabelAlignment(Qt.AlignRight)

            self.notes_input = QTextEdit(); self.notes_input.setPlaceholderText("ملاحظات إضافية..."); self.notes_input.setMaximumHeight(100)
            form.addRow("الملاحظات:", self.notes_input)

            layout.addLayout(form)
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم التفاصيل الإضافية: {e}")
    
    def create_buttons_section(self, layout):
        try:
            btns = QHBoxLayout(); btns.addStretch()
            self.save_button = QPushButton("حفظ التعديلات")
            self.delete_button = QPushButton("حذف المصروف"); self.delete_button.setObjectName("delete_btn")
            self.cancel_button = QPushButton("إلغاء"); self.cancel_button.setObjectName("cancel_btn")
            self.save_button.clicked.connect(self.save_changes)
            self.delete_button.clicked.connect(self.delete_expense)
            self.cancel_button.clicked.connect(self.reject)
            btns.addWidget(self.save_button); btns.addWidget(self.delete_button); btns.addWidget(self.cancel_button)
            layout.addLayout(btns)
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الأزرار: {e}")
    
    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            self.school_combo.clear()
            self.school_combo.addItem("عام", None)  # إضافة خيار عام
            
            # جلب المدارس من قاعدة البيانات
            query = "SELECT id, name_ar FROM schools ORDER BY name_ar"
            schools = db_manager.execute_query(query)
            
            if schools:
                for school in schools:
                    self.school_combo.addItem(school['name_ar'], school['id'])
            else:
                # إذا لم توجد مدارس، يمكن على الأقل إضافة مصروفات عامة
                pass  # الخيار "عام" موجود بالفعل
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.warning(self, "خطأ", f"خطأ في تحميل قائمة المدارس:\n{str(e)}")
    
    def load_expense_data(self):
        """تحميل بيانات المصروف الحالي"""
        try:
            # جلب بيانات المصروف
            query = """
                SELECT e.*, s.name_ar as school_name
                FROM expenses e
                LEFT JOIN schools s ON e.school_id = s.id
                WHERE e.id = ?
            """
            result = db_manager.execute_query(query, (self.expense_id,))
            
            if not result:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على بيانات المصروف")
                self.reject()
                return
            
            self.expense_data = result[0]

            # ملء الحقول بالبيانات الحالية
            # إعداد نوع المصروف والوصف
            self.category_combo.setCurrentText(self.expense_data['expense_type'] or "")
            self.title_input.setText(self.expense_data['description'] or "")
            # المبلغ والتواريخ والملاحظات
            self.amount_input.setValue(float(self.expense_data['amount'] or 0))
            self.expense_date.setDate(QDate(datetime.strptime(
                self.expense_data['expense_date'], '%Y-%m-%d').date()))
            self.notes_input.setPlainText(self.expense_data['notes'] or "")
            # المدرسة
            if self.expense_data['school_id'] is None:
                # إذا كان المصروف عام، اختر خيار "عام"
                school_index = self.school_combo.findData(None)
            else:
                school_index = self.school_combo.findData(self.expense_data['school_id'])
            
            if school_index >= 0:
                self.school_combo.setCurrentIndex(school_index)
            
            
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات المصروف: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في تحميل بيانات المصروف:\n{str(e)}")
            self.reject()
    
    def validate_inputs(self):
        """التحقق من صحة البيانات المدخلة"""
        try:
            errors = []
            
            # التحقق من الوصف
            if not self.title_input.text().strip():
                errors.append("يجب إدخال وصف المصروف")
            
            # التحقق من المبلغ
            if self.amount_input.value() <= 0:
                errors.append("يجب إدخال مبلغ أكبر من الصفر")
            
            # لا حاجة للتحقق من المدرسة لأن "عام" خيار صالح
            
            # التحقق من الفئة
            if self.category_combo.currentIndex() == 0:
                errors.append("يجب اختيار فئة المصروف")
            
            return errors
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من البيانات: {e}")
            return [f"خطأ في التحقق من البيانات: {str(e)}"]
    
    def save_changes(self):
        """حفظ التعديلات"""
        try:
            # التحقق من صحة البيانات
            errors = self.validate_inputs()
            if errors:
                QMessageBox.warning(self, "خطأ في البيانات", "\n".join(errors))
                return
            
            # تحضير البيانات المحدثة
            updated_data = {
                'expense_type': self.category_combo.currentText(),
                'amount': self.amount_input.value(),
                'description': self.title_input.text().strip(),
                'expense_date': self.expense_date.date().toPyDate(),
                'notes': self.notes_input.toPlainText().strip() or None,
                'school_id': self.school_combo.currentData()
            }
            
            # تحديث البيانات في قاعدة البيانات
            update_query = """
                UPDATE expenses 
                SET expense_type = ?, amount = ?, description = ?, expense_date = ?, 
                    notes = ?, school_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            
            params = (
                updated_data['expense_type'],
                updated_data['amount'],
                updated_data['description'],
                updated_data['expense_date'],
                updated_data['notes'],
                updated_data['school_id'],
                self.expense_id
            )
            
            # تنفيذ الاستعلام
            result = db_manager.execute_update(update_query, params)
            
            if result > 0:
                QMessageBox.information(self, "نجح", "تم حفظ التعديلات بنجاح")
                log_user_action(f"تعديل بيانات المصروف {self.expense_id}", "نجح")
                log_database_operation("تحديث مصروف", "نجح")
                self.accept()
            else:
                QMessageBox.warning(self, "خطأ", "لم يتم حفظ التعديلات")
                
        except Exception as e:
            logging.error(f"خطأ في حفظ التعديلات: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ التعديلات:\n{str(e)}")
    
    def delete_expense(self):
        """حذف المصروف"""
        try:
            # تأكيد الحذف
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                "هل أنت متأكد من حذف هذا المصروف؟\nسيتم حذف جميع البيانات المرتبطة به.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # حذف المصروف من قاعدة البيانات
                delete_query = "DELETE FROM expenses WHERE id = ?"
                result = db_manager.execute_update(delete_query, (self.expense_id,))
                
                if result > 0:
                    QMessageBox.information(self, "نجح", "تم حذف المصروف بنجاح")
                    log_user_action(f"حذف المصروف {self.expense_id}", "نجح")
                    log_database_operation("حذف مصروف", "نجح")
                    self.accept()
                else:
                    QMessageBox.warning(self, "خطأ", "لم يتم حذف المصروف")
                    
        except Exception as e:
            logging.error(f"خطأ في حذف المصروف: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حذف المصروف:\n{str(e)}")
    
    def apply_responsive_design(self):
        try:
            from PyQt5.QtWidgets import QApplication, QGroupBox, QPushButton
            screen = QApplication.primaryScreen().availableGeometry() if QApplication.primaryScreen() else None
            if not screen:
                return
            sw, sh = screen.width(), screen.height()
            target_w = min(740, int(sw * 0.82))
            target_h = min(640, int(sh * 0.85))
            self.resize(target_w, target_h)

            scale = min(sw / 1920.0, sh / 1080.0)
            base = 14
            point_size = max(10, int(base * (0.9 + scale * 0.6)))
            f = self.font(); f.setPointSize(point_size); self.setFont(f)

            if sw <= 1366:
                for btn in self.findChildren(QPushButton):
                    btn.setMinimumHeight(32)
        except Exception as e:
            logging.warning(f"Responsive design adjustment failed (expense edit): {e}")
