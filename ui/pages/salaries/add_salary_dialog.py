#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إضافة راتب جديد
"""

import logging
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit,
    QDateEdit, QSpinBox, QDoubleSpinBox, QMessageBox,
    QFrame, QGroupBox, QCheckBox, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator

from core.database.connection import db_manager
from core.utils.logger import log_user_action


class AddSalaryDialog(QDialog):
    """نافذة إضافة راتب جديد"""
    
    salary_added = pyqtSignal()  # إشارة إضافة راتب جديد
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.staff_list = []
        self.setup_ui()
        self.setup_connections()
        self.load_schools()
        self.load_staff_data()
        self.calculate_default_period()
        self.apply_responsive_design()
        
    def setup_ui(self):
        """إعداد الواجهة (تصميم متجاوب مبسط موحد)."""
        self.setWindowTitle("إضافة راتب جديد")
        self.setModal(True)
        self.resize(640, 620)
        self.setMinimumSize(480, 520)

        # ستايل موحد خفيف (مشابه للحوارات الأخرى)
        self.setStyleSheet("""
            QDialog { background:#f5f7fa; font-family:'Segoe UI', Arial, sans-serif; }
            QLabel { color:#1f2d3d; font-weight:600; margin:4px 0; }
            QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit {
                padding:6px 8px; border:1px solid #c0c6ce; border-radius:6px; background:#ffffff; }
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTextEdit:focus {
                border:1px solid #357abd; background:#f0f7ff; }
            QPushButton { background:#357abd; color:#fff; border:none; padding:8px 18px; border-radius:6px; font-weight:600; }
            QPushButton:hover { background:#4b8fcc; }
            QPushButton:pressed { background:#2d6399; }
            QPushButton#cancel_btn { background:#c0392b; }
            QPushButton#cancel_btn:hover { background:#d35445; }
            QPushButton#delete_btn { background:#dc3545; }
            QPushButton#delete_btn:hover { background:#c82333; }
            QGroupBox { border:1px solid #d3d8de; border-radius:8px; margin-top:12px; font-weight:600; }
            QGroupBox::title { subcontrol-origin: margin; left:8px; padding:2px 8px; background:#357abd; color:#fff; border-radius:4px; }
            QScrollArea { border:none; }
            QLabel#salaryLabel { color:#27ae60; font-weight:600; }
            QLabel#daysLabel { color:#c0392b; font-weight:600; }
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

        title_label = QLabel("إضافة راتب جديد")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("background:#357abd; color:#fff; padding:10px; border-radius:6px; font-weight:700;")
        content_layout.addWidget(title_label)

        content_layout.addWidget(self.create_staff_group())
        content_layout.addWidget(self.create_salary_group())
        content_layout.addWidget(self.create_period_group())
        content_layout.addWidget(self.create_notes_group())
        content_layout.addLayout(self.create_buttons())

        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
    def create_staff_group(self):
        group = QGroupBox("بيانات الموظف/المعلم")
        layout = QFormLayout(); layout.setSpacing(8); layout.setLabelAlignment(Qt.AlignRight)
        self.school_combo = QComboBox(); self.school_combo.addItem("جميع المدارس", "")
        layout.addRow("اختر المدرسة:", self.school_combo)
        self.staff_type_combo = QComboBox(); self.staff_type_combo.addItem("جميع الأنواع", ""); self.staff_type_combo.addItem("معلم", "teacher"); self.staff_type_combo.addItem("موظف", "employee")
        layout.addRow("نوع الموظف:", self.staff_type_combo)
        self.staff_combo = QComboBox(); layout.addRow("اختر الموظف/المعلم:", self.staff_combo)
        self.base_salary_label = QLabel("0.00 دينار"); self.base_salary_label.setObjectName("salaryLabel")
        layout.addRow("الراتب المسجل:", self.base_salary_label)
        group.setLayout(layout); return group
    
    def create_salary_group(self):
        group = QGroupBox("تفاصيل الراتب")
        layout = QFormLayout(); layout.setSpacing(8); layout.setLabelAlignment(Qt.AlignRight)
        self.paid_amount_input = QDoubleSpinBox(); self.paid_amount_input.setRange(0, 999999999); self.paid_amount_input.setDecimals(2); self.paid_amount_input.setSuffix(" دينار")
        layout.addRow("المبلغ المدفوع:", self.paid_amount_input)
        self.payment_date_input = QDateEdit(); self.payment_date_input.setDate(QDate.currentDate()); self.payment_date_input.setCalendarPopup(True)
        layout.addRow("تاريخ الدفع:", self.payment_date_input)
        group.setLayout(layout); return group
    
    def create_period_group(self):
        group = QGroupBox("فترة الراتب")
        layout = QFormLayout(); layout.setSpacing(8); layout.setLabelAlignment(Qt.AlignRight)
        self.from_date_input = QDateEdit(); self.from_date_input.setCalendarPopup(True)
        layout.addRow("من تاريخ:", self.from_date_input)
        self.to_date_input = QDateEdit(); self.to_date_input.setCalendarPopup(True)
        layout.addRow("إلى تاريخ:", self.to_date_input)
        self.days_count_label = QLabel("30 يوم"); self.days_count_label.setObjectName("daysLabel")
        layout.addRow("عدد الأيام:", self.days_count_label)
        group.setLayout(layout); return group
    
    def create_notes_group(self):
        group = QGroupBox("ملاحظات")
        layout = QVBoxLayout(); layout.setSpacing(6)
        self.notes_input = QTextEdit(); self.notes_input.setMaximumHeight(90); self.notes_input.setPlaceholderText("ملاحظات إضافية...")
        layout.addWidget(self.notes_input)
        group.setLayout(layout); return group
    
    def create_buttons(self):
        layout = QHBoxLayout(); layout.addStretch()
        self.save_btn = QPushButton("إضافة الراتب")
        self.cancel_btn = QPushButton("إلغاء"); self.cancel_btn.setObjectName("cancel_btn")
        layout.addWidget(self.save_btn); layout.addWidget(self.cancel_btn)
        return layout
    
    def setup_connections(self):
        """إعداد الاتصالات والأحداث"""
        self.school_combo.currentTextChanged.connect(self.load_staff_data)
        self.staff_type_combo.currentTextChanged.connect(self.load_staff_data)
        self.staff_combo.currentTextChanged.connect(self.update_base_salary)
        self.from_date_input.dateChanged.connect(self.calculate_days)
        self.to_date_input.dateChanged.connect(self.calculate_days)
        self.save_btn.clicked.connect(self.save_salary)
        self.cancel_btn.clicked.connect(self.reject)
    
    # أزلنا دالة setup_styles لصالح ستايل مبسط داخل setup_ui

    def apply_responsive_design(self):
        """ضبط الحجم والخط حسب دقة الشاشة (متوافق مع باقي الحوارات)."""
        try:
            from PyQt5.QtWidgets import QApplication, QGroupBox, QPushButton
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
            f = self.font(); f.setPointSize(point_size); self.setFont(f)

            if sw <= 1366:
                for grp in self.findChildren(QGroupBox):
                    lay = grp.layout()
                    if lay:
                        lay.setHorizontalSpacing(6)
                        lay.setVerticalSpacing(6)
                for btn in self.findChildren(QPushButton):
                    btn.setMinimumHeight(32)
        except Exception as e:
            logging.warning(f"Responsive design adjustment failed (salary add): {e}")
    
    def calculate_default_period(self):
        """حساب الفترة الافتراضية (30 يوم قبل اليوم الحالي)"""
        today = QDate.currentDate()
        thirty_days_ago = today.addDays(-30)
        
        self.from_date_input.setDate(thirty_days_ago)
        self.to_date_input.setDate(today)
        
        self.calculate_days()
    
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
    
    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            self.school_combo.clear()
            self.school_combo.addItem("جميع المدارس", "")
            
            query = "SELECT id, name_ar FROM schools ORDER BY name_ar"
            
            with db_manager.get_cursor() as cursor:
                cursor.execute(query)
                schools = cursor.fetchall()
                
                for school in schools:
                    self.school_combo.addItem(school['name_ar'], school['id'])
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المدارس:\n{e}")
    
    def load_staff_data(self):
        """تحميل بيانات الموظفين/المعلمين مع التصفية"""
        try:
            self.staff_combo.clear()
            self.staff_list = []
            
            school_id = self.school_combo.currentData()
            staff_type = self.staff_type_combo.currentData()
            
            # بناء الاستعلام حسب الفلاتر
            if staff_type == "teacher":
                query = """
                    SELECT t.id, t.name, t.monthly_salary, t.school_id, s.name_ar as school_name
                    FROM teachers t
                    LEFT JOIN schools s ON t.school_id = s.id
                """
                conditions = []
                params = []
                
                if school_id:
                    conditions.append("t.school_id = ?")
                    params.append(school_id)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                query += " ORDER BY t.name"
                
            elif staff_type == "employee":
                query = """
                    SELECT e.id, e.name, e.monthly_salary, e.school_id, s.name_ar as school_name
                    FROM employees e
                    LEFT JOIN schools s ON e.school_id = s.id
                """
                conditions = []
                params = []
                
                if school_id:
                    conditions.append("e.school_id = ?")
                    params.append(school_id)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                query += " ORDER BY e.name"
                
            else:  # جميع الأنواع
                # تحميل المعلمين والموظفين معاً
                conditions = []
                params = []
                
                if school_id:
                    conditions.append("school_id = ?")
                    params.append(school_id)
                
                condition_str = ""
                if conditions:
                    condition_str = " WHERE " + " AND ".join(conditions)
                
                # استعلام المعلمين
                teacher_query = f"""
                    SELECT t.id, t.name, t.monthly_salary, t.school_id, s.name_ar as school_name, 'teacher' as type
                    FROM teachers t
                    LEFT JOIN schools s ON t.school_id = s.id
                    {condition_str.replace("school_id", "t.school_id")}
                """
                
                # استعلام الموظفين
                employee_query = f"""
                    SELECT e.id, e.name, e.monthly_salary, e.school_id, s.name_ar as school_name, 'employee' as type
                    FROM employees e
                    LEFT JOIN schools s ON e.school_id = s.id
                    {condition_str.replace("school_id", "e.school_id")}
                """
                
                query = f"{teacher_query} UNION {employee_query} ORDER BY name"
            
            with db_manager.get_cursor() as cursor:
                if staff_type in ["teacher", "employee"]:
                    cursor.execute(query, params)
                else:
                    # للاستعلام المدمج (UNION) نحتاج parameters مكررة
                    if params:
                        cursor.execute(query, params + params)
                    else:
                        cursor.execute(query)
                    
                staff_data = cursor.fetchall()
                
                for staff in staff_data:
                    # تحديد نوع الموظف
                    if 'type' in staff.keys():
                        staff_type_actual = staff['type']
                    else:
                        staff_type_actual = staff_type
                    
                    staff_type_display = "معلم" if staff_type_actual == "teacher" else "موظف"
                    display_text = f"{staff['name']} - {staff['school_name'] or 'غير محدد'} ({staff_type_display})"
                    self.staff_combo.addItem(display_text)
                    self.staff_list.append({
                        'id': staff['id'],
                        'name': staff['name'],
                        'salary': staff['monthly_salary'] or 0,
                        'school_id': staff['school_id'],
                        'school_name': staff['school_name'],
                        'type': staff_type_actual
                    })
            
            # تحديث الراتب المعروض
            self.update_base_salary()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الموظفين: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات الموظفين:\n{e}")
    
    def update_base_salary(self):
        """تحديث عرض الراتب المسجل"""
        try:
            current_index = self.staff_combo.currentIndex()
            if current_index >= 0 and current_index < len(self.staff_list):
                staff = self.staff_list[current_index]
                salary = staff['salary']
                self.base_salary_label.setText(f"{salary:.2f} دينار")
                
                # تعبئة المبلغ المدفوع بالراتب المسجل كقيمة افتراضية
                self.paid_amount_input.setValue(salary)
            else:
                self.base_salary_label.setText("0.00 دينار")
                self.paid_amount_input.setValue(0)
                
        except Exception as e:
            logging.error(f"خطأ في تحديث الراتب: {e}")
    
    def validate_inputs(self):
        """التحقق من صحة البيانات المدخلة"""
        # التحقق من اختيار موظف
        if self.staff_combo.currentIndex() < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار موظف أو معلم")
            return False
        
        # التحقق من المبلغ المدفوع
        if self.paid_amount_input.value() <= 0:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال مبلغ صحيح")
            return False
        
        # التحقق من صحة التواريخ
        from_date = self.from_date_input.date()
        to_date = self.to_date_input.date()
        
        if from_date > to_date:
            QMessageBox.warning(self, "تحذير", "تاريخ البداية يجب أن يكون قبل تاريخ النهاية")
            return False
        
        return True
    
    def save_salary(self):
        """حفظ الراتب الجديد"""
        try:
            if not self.validate_inputs():
                return
            
            # جمع البيانات
            current_index = self.staff_combo.currentIndex()
            staff = self.staff_list[current_index]
            staff_type = staff['type']
            
            # الحصول على كائنات QDate لحساب عدد الأيام
            from_date_q = self.from_date_input.date()
            to_date_q = self.to_date_input.date()
            from_date = from_date_q.toString(Qt.ISODate)
            to_date = to_date_q.toString(Qt.ISODate)
            payment_date = self.payment_date_input.date().toString(Qt.ISODate)
            payment_time = datetime.now().strftime("%H:%M:%S")

            # حساب عدد الأيام بين التاريخين
            days_count = from_date_q.daysTo(to_date_q) + 1
            
            # إدخال البيانات في قاعدة البيانات
            with db_manager.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO salaries 
                    (staff_type, staff_id, base_salary, paid_amount, 
                     from_date, to_date, days_count, payment_date, payment_time, notes, school_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    staff_type,
                    staff['id'],
                    staff['salary'],
                    self.paid_amount_input.value(),
                    from_date,
                    to_date,
                    days_count,
                    payment_date,
                    payment_time,
                    self.notes_input.toPlainText().strip() or None,
                    staff['school_id']
                ))
            
            # تسجيل العملية
            log_user_action(
                f"إضافة راتب {staff_type}",
                f"الاسم: {staff['name']}, المبلغ: {self.paid_amount_input.value()}, المدرسة: {staff['school_name']}"
            )
            
            # إرسال إشارة التحديث
            self.salary_added.emit()
            
            QMessageBox.information(self, "نجح", "تم إضافة الراتب بنجاح")
            self.accept()
            
        except Exception as e:
            logging.error(f"خطأ في حفظ الراتب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ الراتب:\n{e}")
