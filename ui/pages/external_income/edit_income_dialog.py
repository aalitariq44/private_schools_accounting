#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة تعديل بيانات الوارد الخارجي
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


class EditIncomeDialog(QDialog):
    """نافذة تعديل بيانات الوارد الخارجي"""
    
    def __init__(self, income_id, parent=None):
        super().__init__(parent)
        self.income_id = income_id
        self.income_data = None

        self.setWindowTitle("تعديل بيانات الوارد الخارجي")
        self.setModal(True)
        self.resize(640, 560)
        self.setMinimumSize(460, 480)

        self.setup_ui()
        self.load_schools()
        self.load_income_data()
        self.apply_responsive_design()

        if hasattr(self, 'income_type_input'):
            self.income_type_input.setFocus()
    
    def setup_ui(self):
        """إعداد الواجهة بتصميم متجاوب مع ScrollArea."""
        try:
            self.setStyleSheet("""
                QDialog { background:#f5f7fa; font-family:'Segoe UI', Arial, sans-serif; }
                QLabel { color:#1f2d3d; font-weight:600; margin:4px 0; }
                QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit {
                    padding:6px 8px; border:1px solid #c0c6ce; border-radius:6px; background:#ffffff; }
                QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTextEdit:focus {
                    border:1px solid #2d8a4b; background:#f3fff6; }
                QPushButton { background:#2d8a4b; color:#fff; border:none; padding:8px 18px; border-radius:6px; font-weight:600; }
                QPushButton:hover { background:#3fa760; }
                QPushButton:pressed { background:#277a42; }
                QPushButton#cancel_btn { background:#c0392b; }
                QPushButton#cancel_btn:hover { background:#d35445; }
                QPushButton#delete_btn { background:#dc3545; }
                QPushButton#delete_btn:hover { background:#c82333; }
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

            self.create_header(content_layout)
            self.create_basic_info_section(content_layout)
            self.create_additional_details_section(content_layout)
            self.create_buttons_section(content_layout)

            scroll.setWidget(content)
            main_layout.addWidget(scroll)
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة تعديل الوارد: {e}")
            raise
    
    def create_header(self, layout):
        try:
            title = QLabel(f"تعديل بيانات الوارد الخارجي #{self.income_id}")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("background:#2d8a4b; color:#fff; padding:10px; border-radius:6px; font-weight:700;")
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

            self.income_type_input = QLineEdit(); self.income_type_input.setPlaceholderText("أدخل عنوان الوارد")
            form.addRow("عنوان الوارد *:", self.income_type_input)

            self.description_input = QLineEdit(); self.description_input.setPlaceholderText("أدخل وصف الوارد")
            form.addRow("الوصف:", self.description_input)

            self.amount_input = QDoubleSpinBox(); self.amount_input.setRange(0.01, 999999999.99); self.amount_input.setDecimals(2); self.amount_input.setSuffix(" د.ع")
            form.addRow("المبلغ *:", self.amount_input)

            self.school_combo = QComboBox(); self.school_combo.setPlaceholderText("اختر المدرسة")
            form.addRow("المدرسة *:", self.school_combo)

            self.income_date = QDateEdit(); self.income_date.setDate(QDate.currentDate()); self.income_date.setCalendarPopup(True)
            form.addRow("التاريخ *:", self.income_date)

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

            self.category_combo = QComboBox(); self.category_combo.addItems([
                "-- اختر الفئة --", "الحانوت", "النقل", "الأنشطة", "التبرعات", "إيجارات", "أخرى"
            ])
            form.addRow("الفئة:", self.category_combo)

            self.notes_input = QTextEdit(); self.notes_input.setPlaceholderText("ملاحظات إضافية..."); self.notes_input.setMaximumHeight(100)
            form.addRow("الملاحظات:", self.notes_input)

            layout.addLayout(form)
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم التفاصيل الإضافية: {e}")
    
    def create_buttons_section(self, layout):
        try:
            btns = QHBoxLayout(); btns.addStretch()
            self.save_button = QPushButton("حفظ التعديلات")
            self.delete_button = QPushButton("حذف الوارد"); self.delete_button.setObjectName("delete_btn")
            self.cancel_button = QPushButton("إلغاء"); self.cancel_button.setObjectName("cancel_btn")
            self.save_button.clicked.connect(self.save_changes)
            self.delete_button.clicked.connect(self.delete_income)
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
                # إذا لم توجد مدارس، يمكن على الأقل إضافة واردات عامة
                pass  # الخيار "عام" موجود بالفعل
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.warning(self, "خطأ", f"خطأ في تحميل قائمة المدارس:\n{str(e)}")
    
    def load_income_data(self):
        """تحميل بيانات الوارد الحالي"""
        try:
            # جلب بيانات الوارد
            query = """
                SELECT ei.id, ei.income_type, ei.amount, ei.description, ei.category,
                       ei.income_date, ei.notes, ei.school_id, s.name_ar as school_name
                FROM external_income ei
                LEFT JOIN schools s ON ei.school_id = s.id
                WHERE ei.id = ?
            """
            result = db_manager.execute_query(query, (self.income_id,))
            
            if not result:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على بيانات الوارد")
                self.reject()
                return
            
            self.income_data = result[0]
            
            # ملء الحقول بالبيانات الحالية
            self.income_type_input.setText(self.income_data['income_type'] or "")
            self.description_input.setText(self.income_data['description'] or "")
            self.amount_input.setValue(float(self.income_data['amount'] or 0))
            self.notes_input.setPlainText(self.income_data['notes'] or "")
            
            # تعيين تاريخ الوارد
            if self.income_data['income_date']:
                income_date = datetime.strptime(self.income_data['income_date'], '%Y-%m-%d').date()
                self.income_date.setDate(QDate(income_date))
            
            # تعيين المدرسة
            school_index = self.school_combo.findData(self.income_data['school_id'])
            if school_index >= 0:
                self.school_combo.setCurrentIndex(school_index)
            
            # تعيين الفئة
            if self.income_data['category']:
                category_index = self.category_combo.findText(self.income_data['category'])
                if category_index >= 0:
                    self.category_combo.setCurrentIndex(category_index)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الوارد: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في تحميل بيانات الوارد:\n{str(e)}")
            self.reject()
    
    def validate_inputs(self):
        """التحقق من صحة البيانات المدخلة"""
        try:
            errors = []
            
            # التحقق من عنوان الوارد
            if not self.income_type_input.text().strip():
                errors.append("يجب إدخال عنوان الوارد")
            
            # التحقق من المبلغ
            if self.amount_input.value() <= 0:
                errors.append("يجب إدخال مبلغ أكبر من الصفر")
            
            # لا حاجة للتحقق من المدرسة لأن "عام" خيار صالح
            
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
                'income_type': self.income_type_input.text().strip(),
                'description': self.description_input.text().strip() or None,
                'amount': self.amount_input.value(),
                'category': self.category_combo.currentText() if self.category_combo.currentIndex() > 0 else 'أخرى',
                'income_date': self.income_date.date().toPyDate(),
                'notes': self.notes_input.toPlainText().strip() or None,
                'school_id': self.school_combo.currentData()
            }
            
            # تحديث البيانات في قاعدة البيانات
            update_query = """
                UPDATE external_income 
                SET income_type = ?, description = ?, amount = ?, category = ?, 
                    income_date = ?, notes = ?, school_id = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            
            params = (
                updated_data['income_type'],
                updated_data['description'],
                updated_data['amount'],
                updated_data['category'],
                updated_data['income_date'],
                updated_data['notes'],
                updated_data['school_id'],
                self.income_id
            )
            
            # تنفيذ الاستعلام
            result = db_manager.execute_update(update_query, params)
            
            if result > 0:
                QMessageBox.information(self, "نجح", "تم حفظ التعديلات بنجاح")
                log_user_action(f"تعديل بيانات الوارد الخارجي {self.income_id}", "نجح")
                log_database_operation("تحديث وارد خارجي", "نجح")
                self.accept()
            else:
                QMessageBox.warning(self, "خطأ", "لم يتم حفظ التعديلات")
                
        except Exception as e:
            logging.error(f"خطأ في حفظ التعديلات: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ التعديلات:\n{str(e)}")
    
    def delete_income(self):
        """حذف الوارد"""
        try:
            # تأكيد الحذف
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                "هل أنت متأكد من حذف هذا الوارد؟\nسيتم حذف جميع البيانات المرتبطة به.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # حذف الوارد من قاعدة البيانات
                delete_query = "DELETE FROM external_income WHERE id = ?"
                result = db_manager.execute_update(delete_query, (self.income_id,))
                
                if result > 0:
                    QMessageBox.information(self, "نجح", "تم حذف الوارد بنجاح")
                    log_user_action(f"حذف الوارد الخارجي {self.income_id}", "نجح")
                    log_database_operation("حذف وارد خارجي", "نجح")
                    self.accept()
                else:
                    QMessageBox.warning(self, "خطأ", "لم يتم حذف الوارد")
                    
        except Exception as e:
            logging.error(f"خطأ في حذف الوارد: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حذف الوارد:\n{str(e)}")
    
    # حذف setup_styles لصالح التصميم الجديد

    def apply_responsive_design(self):
        try:
            from PyQt5.QtWidgets import QApplication, QGroupBox, QPushButton
            screen = QApplication.primaryScreen().availableGeometry() if QApplication.primaryScreen() else None
            if not screen:
                return
            sw, sh = screen.width(), screen.height()
            target_w = min(720, int(sw * 0.82))
            target_h = min(620, int(sh * 0.85))
            self.resize(target_w, target_h)

            scale = min(sw / 1920.0, sh / 1080.0)
            base = 14
            point_size = max(10, int(base * (0.9 + scale * 0.6)))
            f = self.font(); f.setPointSize(point_size); self.setFont(f)

            if sw <= 1366:
                for btn in self.findChildren(QPushButton):
                    btn.setMinimumHeight(32)
        except Exception as e:
            logging.warning(f"Responsive design adjustment failed (income edit): {e}")
