import sys
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox,
                            QPushButton, QFrame, QMessageBox, QGroupBox, QTextEdit,
                            QCheckBox, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import sqlite3
from datetime import datetime
import logging

class AddAdditionalFeeDialog(QDialog):
    fee_added = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'database', 'private_schools.db')
        self.selected_students = []
        self.setup_ui()
        self.load_data()
        self.setup_connections()
        
    def setup_ui(self):
        self.setWindowTitle("إضافة رسم إضافي")
        self.setModal(True)
        self.resize(700, 750)
        
        # تطبيق الستايل
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #faf5ff, stop:1 #f0e8ff);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 24px;
            }
            
            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QTextEdit {
                padding: 8px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                font-size: 24px;
                min-height: 20px;
            }
            
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus, QTextEdit:focus {
                border-color: #8e44ad;
                background-color: #fdf2e9;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8e44ad, stop:1 #7d3c98);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 24px;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a569bd, stop:1 #8e44ad);
                transform: translateY(-2px);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7d3c98, stop:1 #6c3483);
            }
            
            QPushButton#select_btn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #2ecc71);
                min-width: 80px;
            }
            
            QPushButton#select_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2ecc71, stop:1 #58d68d);
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
                font-size: 24px;
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
                background-color: #8e44ad;
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
            
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                padding: 5px;
            }
            
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ecf0f1;
            }
            
            QListWidget::item:selected {
                background-color: #d5b7e8;
                color: #2c3e50;
            }
            
            QCheckBox {
                font-size: 24px;
                color: #2c3e50;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            
            QCheckBox::indicator:unchecked {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            
            QCheckBox::indicator:checked {
                border: 2px solid #8e44ad;
                border-radius: 4px;
                background-color: #8e44ad;
                image: url(checkmark.png);
            }
        """)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # عنوان النافذة
        title_label = QLabel("إضافة رسم إضافي")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8e44ad, stop:1 #7d3c98);
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(title_label)
        
        # مجموعة تفاصيل الرسم
        fee_details_group = QGroupBox("تفاصيل الرسم")
        fee_layout = QFormLayout(fee_details_group)
        fee_layout.setSpacing(12)
        
        # نوع الرسم
        self.fee_type_combo = QComboBox()
        self.fee_type_combo.addItems([
            "كتب ومواد دراسية", "نشاطات ورحلات", "نقل وباصات",
            "امتحانات وشهادات", "رسوم إدارية", "خدمات إضافية", "أخرى"
        ])
        fee_layout.addRow("نوع الرسم:", self.fee_type_combo)
        
        # اسم الرسم
        self.fee_name_edit = QLineEdit()
        self.fee_name_edit.setPlaceholderText("مثال: كتب الفصل الأول")
        fee_layout.addRow("اسم الرسم:", self.fee_name_edit)
        
        # الوصف
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("وصف تفصيلي للرسم (اختياري)")
        self.description_edit.setMaximumHeight(80)
        fee_layout.addRow("الوصف:", self.description_edit)
        
        # المبلغ
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setSuffix(" ر.س")
        self.amount_spin.setValue(100.00)
        fee_layout.addRow("المبلغ:", self.amount_spin)
        
        # تاريخ الاستحقاق
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setDate(QDate.currentDate().addDays(30))
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDisplayFormat("yyyy-MM-dd")
        fee_layout.addRow("تاريخ الاستحقاق:", self.due_date_edit)
        
        main_layout.addWidget(fee_details_group)
        
        # مجموعة اختيار الطلاب
        students_group = QGroupBox("اختيار الطلاب")
        students_layout = QVBoxLayout(students_group)
        
        # شريط الفلترة
        filter_layout = QHBoxLayout()
        
        # اختيار المدرسة
        self.school_combo = QComboBox()
        self.school_combo.setPlaceholderText("اختر المدرسة")
        filter_layout.addWidget(QLabel("المدرسة:"))
        filter_layout.addWidget(self.school_combo)
        
        # اختيار الصف
        self.grade_combo = QComboBox()
        self.grade_combo.addItems([
            "الكل", "KG1", "KG2", "الأول الابتدائي", "الثاني الابتدائي", 
            "الثالث الابتدائي", "الرابع الابتدائي", "الخامس الابتدائي", 
            "السادس الابتدائي", "الأول المتوسط", "الثاني المتوسط", 
            "الثالث المتوسط", "الأول الثانوي", "الثاني الثانوي", "الثالث الثانوي"
        ])
        filter_layout.addWidget(QLabel("الصف:"))
        filter_layout.addWidget(self.grade_combo)
        
        students_layout.addLayout(filter_layout)
        
        # أزرار التحديد
        selection_layout = QHBoxLayout()
        
        self.select_all_checkbox = QCheckBox("تحديد الكل")
        selection_layout.addWidget(self.select_all_checkbox)
        
        selection_layout.addStretch()
        
        self.filter_btn = QPushButton("تطبيق الفلتر")
        self.filter_btn.setObjectName("select_btn")
        selection_layout.addWidget(self.filter_btn)
        
        students_layout.addLayout(selection_layout)
        
        # قائمة الطلاب
        self.students_list = QListWidget()
        self.students_list.setMaximumHeight(200)
        students_layout.addWidget(self.students_list)
        
        # معلومات الطلاب المحددين
        self.selected_info_label = QLabel("لم يتم تحديد أي طلاب")
        self.selected_info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 8px;
                color: #6c757d;
                font-size: 24px;
            }
        """)
        students_layout.addWidget(self.selected_info_label)
        
        main_layout.addWidget(students_group)
        
        # أزرار العمل
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.save_btn = QPushButton("حفظ الرسوم")
        self.save_btn.setIcon(QIcon("💾"))
        buttons_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setIcon(QIcon("❌"))
        buttons_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(buttons_layout)
        
    def setup_connections(self):
        """ربط الإشارات"""
        self.save_btn.clicked.connect(self.save_fees)
        self.cancel_btn.clicked.connect(self.reject)
        self.filter_btn.clicked.connect(self.load_students)
        
        # ربط التحديد
        self.select_all_checkbox.toggled.connect(self.toggle_select_all)
        self.students_list.itemChanged.connect(self.update_selected_count)
        
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
            self.school_combo.addItem("الكل", None)
            for school_id, school_name in schools:
                self.school_combo.addItem(school_name, school_id)
                
            conn.close()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل المدارس:\n{str(e)}")
    
    def load_students(self):
        """تحميل قائمة الطلاب حسب الفلتر"""
        school_id = self.school_combo.currentData()
        grade = self.grade_combo.currentText()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # بناء الاستعلام
            query = """
                SELECT s.id, s.first_name, s.last_name, s.grade, s.section, sc.arabic_name
                FROM students s
                LEFT JOIN schools sc ON s.school_id = sc.id
                WHERE s.status = 'نشط'
            """
            params = []
            
            if school_id:
                query += " AND s.school_id = ?"
                params.append(school_id)
            
            if grade != "الكل":
                query += " AND s.grade = ?"
                params.append(grade)
            
            query += " ORDER BY sc.arabic_name, s.grade, s.section, s.first_name"
            
            cursor.execute(query, params)
            students = cursor.fetchall()
            conn.close()
            
            # تحديث قائمة الطلاب
            self.students_list.clear()
            for student_id, first_name, last_name, grade, section, school_name in students:
                display_text = f"{first_name} {last_name} - {grade}"
                if section:
                    display_text += f" ({section})"
                display_text += f" - {school_name}"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, student_id)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.students_list.addItem(item)
            
            self.update_selected_count()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الطلاب: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل الطلاب:\n{str(e)}")
    
    def toggle_select_all(self, checked):
        """تحديد/إلغاء تحديد جميع الطلاب"""
        for i in range(self.students_list.count()):
            item = self.students_list.item(i)
            item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
    
    def update_selected_count(self):
        """تحديث عدد الطلاب المحددين"""
        selected_count = 0
        total_amount = 0
        
        for i in range(self.students_list.count()):
            item = self.students_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_count += 1
                total_amount += self.amount_spin.value()
        
        if selected_count == 0:
            self.selected_info_label.setText("لم يتم تحديد أي طلاب")
        else:
            info_text = f"الطلاب المحددون: {selected_count}\n"
            info_text += f"إجمالي المبلغ: {total_amount:.2f} ر.س"
            self.selected_info_label.setText(info_text)
    
    def get_selected_students(self):
        """الحصول على قائمة الطلاب المحددين"""
        selected_students = []
        for i in range(self.students_list.count()):
            item = self.students_list.item(i)
            if item.checkState() == Qt.Checked:
                student_id = item.data(Qt.UserRole)
                selected_students.append(student_id)
        return selected_students
    
    def validate_inputs(self):
        """التحقق من صحة البيانات"""
        errors = []
        
        if not self.fee_name_edit.text().strip():
            errors.append("يجب إدخال اسم الرسم")
        
        if self.amount_spin.value() <= 0:
            errors.append("يجب إدخال مبلغ أكبر من صفر")
        
        selected_students = self.get_selected_students()
        if not selected_students:
            errors.append("يجب تحديد طالب واحد على الأقل")
        
        return errors
    
    def save_fees(self):
        """حفظ الرسوم الإضافية"""
        # التحقق من صحة البيانات
        errors = self.validate_inputs()
        if errors:
            QMessageBox.warning(self, "خطأ في البيانات", "\n".join(errors))
            return
        
        selected_students = self.get_selected_students()
        
        # تأكيد الحفظ
        reply = QMessageBox.question(
            self, 
            "تأكيد الحفظ",
            f"هل أنت متأكد من إضافة الرسم لـ {len(selected_students)} طالب؟\n"
            f"إجمالي المبلغ: {len(selected_students) * self.amount_spin.value():.2f} ر.س",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            fee_type = self.fee_type_combo.currentText()
            fee_name = self.fee_name_edit.text().strip()
            description = self.description_edit.toPlainText().strip()
            amount = self.amount_spin.value()
            due_date = self.due_date_edit.date().toString("yyyy-MM-dd")
            
            # إنشاء الوصف الكامل
            full_description = f"{fee_type} - {fee_name}"
            if description:
                full_description += f"\n{description}"
            
            # إدراج الرسوم لكل طالب محدد
            insert_query = """
                INSERT INTO additional_fees (
                    student_id, type, description, amount, due_date, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            for student_id in selected_students:
                cursor.execute(insert_query, (
                    student_id,
                    fee_type,
                    full_description,
                    amount,
                    due_date,
                    "مستحق",
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(
                self, 
                "نجح", 
                f"تم إضافة الرسم بنجاح لـ {len(selected_students)} طالب!\n"
                f"إجمالي المبلغ: {len(selected_students) * amount:.2f} ر.س"
            )
            
            self.fee_added.emit()
            self.accept()
            
        except Exception as e:
            logging.error(f"خطأ في حفظ الرسوم: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ الرسوم:\n{str(e)}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # تطبيق الخط العربي
    font = QFont("Arial", 10)
    app.setFont(font)
    
    dialog = AddAdditionalFeeDialog()
    dialog.show()
    
    sys.exit(app.exec_())
