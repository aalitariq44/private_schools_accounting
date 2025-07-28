import sys
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox,
                            QPushButton, QFrame, QMessageBox, QGroupBox, QSpinBox,
                            QTextEdit)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import sqlite3
from datetime import datetime, timedelta
import logging

class AddInstallmentDialog(QDialog):
    installment_added = pyqtSignal()
    installment_saved = pyqtSignal(int) # New signal to emit installment_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'database', 'private_schools.db')
        self.setup_ui()
        self.load_data()
        self.setup_connections()
        
    def setup_ui(self):
        self.setWindowTitle("إضافة قسط جديد")
        self.setModal(True)
        self.resize(600, 700)
        
        # تطبيق الستايل
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fff8f8, stop:1 #ffe8e8);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 11px;
            }
            
            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox, QTextEdit {
                padding: 8px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                font-size: 11px;
                min-height: 20px;
            }
            
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QTextEdit:focus {
                border-color: #e74c3c;
                background-color: #fff8f8;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ec7063, stop:1 #e74c3c);
                transform: translateY(-2px);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c0392b, stop:1 #a93226);
            }
            
            QPushButton#calculate_btn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f39c12, stop:1 #e67e22);
                min-width: 80px;
            }
            
            QPushButton#calculate_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5b041, stop:1 #f39c12);
            }
            
            QPushButton#cancel_btn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #95a5a6, stop:1 #7f8c8d);
            }
            
            QPushButton#cancel_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #b2bec3, stop:1 #95a5a6);
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin: 10px 0px;
                padding-top: 15px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            
            QFrame {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # عنوان النافذة
        title_label = QLabel("إضافة قسط جديد")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(title_label)
        
        # مجموعة معلومات الطالب
        student_info_group = QGroupBox("معلومات الطالب")
        student_layout = QFormLayout(student_info_group)
        student_layout.setSpacing(12)
        
        # اختيار المدرسة
        self.school_combo = QComboBox()
        self.school_combo.setPlaceholderText("اختر المدرسة أولاً")
        student_layout.addRow("المدرسة:", self.school_combo)
        
        # اختيار الطالب
        self.student_combo = QComboBox()
        self.student_combo.setPlaceholderText("اختر الطالب")
        self.student_combo.setEnabled(False)
        student_layout.addRow("الطالب:", self.student_combo)
        
        # معلومات الطالب المحددة
        self.student_info_label = QLabel("لم يتم اختيار طالب")
        self.student_info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 8px;
                color: #6c757d;
                font-size: 10px;
            }
        """)
        student_layout.addRow("معلومات:", self.student_info_label)
        
        main_layout.addWidget(student_info_group)
        
        # مجموعة تفاصيل القسط
        installment_group = QGroupBox("تفاصيل القسط")
        installment_layout = QFormLayout(installment_group)
        installment_layout.setSpacing(12)
        
        # نوع القسط
        self.installment_type_combo = QComboBox()
        self.installment_type_combo.addItems([
            "رسوم دراسية", "رسوم تسجيل", "رسوم كتب", 
            "رسوم نشاطات", "رسوم نقل", "أخرى"
        ])
        installment_layout.addRow("نوع القسط:", self.installment_type_combo)
        
        # الوصف
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("وصف القسط (اختياري)")
        installment_layout.addRow("الوصف:", self.description_edit)
        
        # المبلغ الإجمالي
        self.total_amount_spin = QDoubleSpinBox()
        self.total_amount_spin.setRange(0, 999999)
        self.total_amount_spin.setDecimals(2)
        self.total_amount_spin.setSuffix(" ر.س")
        self.total_amount_spin.setValue(1000.00)
        installment_layout.addRow("المبلغ الإجمالي:", self.total_amount_spin)
        
        # عدد الأقساط
        self.installments_count_spin = QSpinBox()
        self.installments_count_spin.setRange(1, 12)
        self.installments_count_spin.setValue(1)
        installment_layout.addRow("عدد الأقساط:", self.installments_count_spin)
        
        # مبلغ القسط الواحد
        self.installment_amount_spin = QDoubleSpinBox()
        self.installment_amount_spin.setRange(0, 999999)
        self.installment_amount_spin.setDecimals(2)
        self.installment_amount_spin.setSuffix(" ر.س")
        self.installment_amount_spin.setReadOnly(True)
        installment_layout.addRow("مبلغ القسط الواحد:", self.installment_amount_spin)
        
        # زر حساب الأقساط
        self.calculate_btn = QPushButton("حساب الأقساط")
        self.calculate_btn.setObjectName("calculate_btn")
        installment_layout.addRow("", self.calculate_btn)
        
        main_layout.addWidget(installment_group)
        
        # مجموعة التواريخ
        dates_group = QGroupBox("تواريخ الاستحقاق")
        dates_layout = QFormLayout(dates_group)
        dates_layout.setSpacing(12)
        
        # تاريخ أول قسط
        self.first_due_date_edit = QDateEdit()
        self.first_due_date_edit.setDate(QDate.currentDate().addDays(30))
        self.first_due_date_edit.setCalendarPopup(True)
        self.first_due_date_edit.setDisplayFormat("yyyy-MM-dd")
        dates_layout.addRow("تاريخ أول قسط:", self.first_due_date_edit)
        
        # الفترة بين الأقساط (بالأيام)
        self.interval_days_spin = QSpinBox()
        self.interval_days_spin.setRange(1, 365)
        self.interval_days_spin.setValue(30)
        self.interval_days_spin.setSuffix(" يوم")
        dates_layout.addRow("الفترة بين الأقساط:", self.interval_days_spin)
        
        main_layout.addWidget(dates_group)
        
        # مجموعة معاينة الأقساط
        preview_group = QGroupBox("معاينة الأقساط")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setPlaceholderText("سيتم عرض تفاصيل الأقساط هنا")
        preview_layout.addWidget(self.preview_text)
        
        main_layout.addWidget(preview_group)
        
        # أزرار العمل
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.save_btn = QPushButton("حفظ الأقساط")
        self.save_btn.setIcon(QIcon("💾"))
        self.save_btn.setEnabled(False)
        buttons_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setIcon(QIcon("❌"))
        buttons_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(buttons_layout)
        
    def setup_connections(self):
        """ربط الإشارات"""
        self.save_btn.clicked.connect(self.save_installments)
        self.cancel_btn.clicked.connect(self.reject)
        self.calculate_btn.clicked.connect(self.calculate_installments)
        
        # ربط تغييرات الحقول
        self.school_combo.currentIndexChanged.connect(self.load_students)
        self.student_combo.currentIndexChanged.connect(self.update_student_info)
        self.total_amount_spin.valueChanged.connect(self.update_installment_amount)
        self.installments_count_spin.valueChanged.connect(self.update_installment_amount)
        
    def load_data(self):
        """تحميل البيانات الأساسية"""
        self.load_schools()
        
    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, arabic_name FROM schools ORDER BY arabic_name")
            schools = cursor.fetchall()
            
            self.school_combo.clear()
            self.school_combo.addItem("اختر المدرسة", None)
            for school_id, school_name in schools:
                self.school_combo.addItem(school_name, school_id)
                
            conn.close()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل المدارس:\n{str(e)}")
    
    def load_students(self):
        """تحميل قائمة الطلاب حسب المدرسة المختارة"""
        school_id = self.school_combo.currentData()
        
        self.student_combo.clear()
        self.student_combo.setEnabled(False)
        
        if not school_id:
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, first_name, last_name, grade, section, status
                FROM students 
                WHERE school_id = ? AND status = 'نشط'
                ORDER BY grade, section, first_name
            """, (school_id,))
            
            students = cursor.fetchall()
            conn.close()
            
            self.student_combo.addItem("اختر الطالب", None)
            for student_id, first_name, last_name, grade, section, status in students:
                display_text = f"{first_name} {last_name} - {grade}"
                if section:
                    display_text += f" ({section})"
                self.student_combo.addItem(display_text, student_id)
            
            self.student_combo.setEnabled(True)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الطلاب: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل الطلاب:\n{str(e)}")
    
    def update_student_info(self):
        """تحديث معلومات الطالب المحدد"""
        student_id = self.student_combo.currentData()
        
        if not student_id:
            self.student_info_label.setText("لم يتم اختيار طالب")
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.first_name, s.last_name, s.grade, s.section, 
                       s.student_number, sc.arabic_name
                FROM students s
                LEFT JOIN schools sc ON s.school_id = sc.id
                WHERE s.id = ?
            """, (student_id,))
            
            student = cursor.fetchone()
            conn.close()
            
            if student:
                info_text = f"""الطالب: {student[0]} {student[1]}
الصف: {student[2]} ({student[3] or 'غير محدد'})
رقم الطالب: {student[4] or 'غير محدد'}
المدرسة: {student[5]}"""
                
                self.student_info_label.setText(info_text)
            
        except Exception as e:
            logging.error(f"خطأ في تحديث معلومات الطالب: {e}")
    
    def update_installment_amount(self):
        """تحديث مبلغ القسط الواحد"""
        total_amount = self.total_amount_spin.value()
        installments_count = self.installments_count_spin.value()
        
        if installments_count > 0:
            installment_amount = total_amount / installments_count
            self.installment_amount_spin.setValue(installment_amount)
    
    def calculate_installments(self):
        """حساب ومعاينة الأقساط"""
        if not self.student_combo.currentData():
            QMessageBox.warning(self, "تحذير", "يجب اختيار الطالب أولاً")
            return
        
        total_amount = self.total_amount_spin.value()
        installments_count = self.installments_count_spin.value()
        first_due_date = self.first_due_date_edit.date().toPyDate()
        interval_days = self.interval_days_spin.value()
        
        if total_amount <= 0:
            QMessageBox.warning(self, "تحذير", "يجب إدخال مبلغ أكبر من صفر")
            return
        
        installment_amount = total_amount / installments_count
        
        # إنشاء معاينة الأقساط
        preview_text = f"إجمالي المبلغ: {total_amount:.2f} ر.س\n"
        preview_text += f"عدد الأقساط: {installments_count}\n"
        preview_text += f"مبلغ القسط الواحد: {installment_amount:.2f} ر.س\n\n"
        preview_text += "تواريخ الاستحقاق:\n"
        preview_text += "-" * 30 + "\n"
        
        current_date = first_due_date
        for i in range(installments_count):
            preview_text += f"القسط {i+1}: {current_date.strftime('%Y-%m-%d')} - {installment_amount:.2f} ر.س\n"
            current_date += timedelta(days=interval_days)
        
        self.preview_text.setPlainText(preview_text)
        self.save_btn.setEnabled(True)
    
    def validate_inputs(self):
        """التحقق من صحة البيانات"""
        errors = []
        
        if not self.student_combo.currentData():
            errors.append("يجب اختيار الطالب")
        
        if self.total_amount_spin.value() <= 0:
            errors.append("يجب إدخال مبلغ أكبر من صفر")
        
        if self.installments_count_spin.value() <= 0:
            errors.append("يجب أن يكون عدد الأقساط أكبر من صفر")
        
        return errors
    
    def save_installments(self):
        """حفظ الأقساط"""
        # التحقق من صحة البيانات
        errors = self.validate_inputs()
        if errors:
            QMessageBox.warning(self, "خطأ في البيانات", "\n".join(errors))
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            student_id = self.student_combo.currentData()
            installment_type = self.installment_type_combo.currentText()
            description = self.description_edit.text().strip()
            total_amount = self.total_amount_spin.value()
            installments_count = self.installments_count_spin.value()
            installment_amount = total_amount / installments_count
            first_due_date = self.first_due_date_edit.date().toPyDate()
            interval_days = self.interval_days_spin.value()
            
            # إدراج الأقساط
            current_date = first_due_date
            for i in range(installments_count):
                installment_description = f"{installment_type}"
                if description:
                    installment_description += f" - {description}"
                installment_description += f" (القسط {i+1} من {installments_count})"
                
                insert_query = """
                    INSERT INTO installments (
                        student_id, amount, payment_date, payment_time, notes
                    ) VALUES (?, ?, ?, ?, ?)
                """
                # Use current date/time for each installment
                from datetime import datetime
                payment_date = datetime.now().strftime("%Y-%m-%d")
                payment_time = datetime.now().strftime("%H:%M:%S")
                cursor.execute(insert_query, (
                    student_id,
                    installment_amount,
                    payment_date,
                    payment_time,
                    installment_description
                ))
                last_installment_id = cursor.lastrowid # Get the ID of the last inserted installment
                
                current_date += timedelta(days=interval_days)
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "نجح", f"تم إضافة {installments_count} قسط بنجاح!")
            self.installment_added.emit()
            if installments_count == 1: # Only emit if a single installment was added
                self.installment_saved.emit(last_installment_id)
            self.accept()
            
        except Exception as e:
            logging.error(f"خطأ في حفظ الأقساط: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ الأقساط:\n{str(e)}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # تطبيق الخط العربي
    font = QFont("Arial", 10)
    app.setFont(font)
    
    dialog = AddInstallmentDialog()
    dialog.show()
    
    sys.exit(app.exec_())
