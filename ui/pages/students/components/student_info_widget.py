#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مكونات معلومات الطالب - عرض المعلومات الأساسية والملخص المالي
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase


class StudentInfoWidget(QWidget):
    """مكون عرض معلومات الطالب"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.student_data = None
        self.installments_data = []
        
        self.setup_cairo_font()
        self.setup_ui()
    
    def setup_cairo_font(self):
        """تحميل وتطبيق خط Cairo"""
        try:
            self.cairo_family = "Arial"  # خط افتراضي
        except Exception as e:
            logging.warning(f"فشل في تحميل خط Cairo: {e}")
            self.cairo_family = "Arial"
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            layout = QVBoxLayout()
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(15)
            
            # معلومات الطالب الأساسية
            self.create_basic_info_section(layout)
            
            # الملخص المالي
            self.create_financial_summary(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة معلومات الطالب: {e}")
            raise
    
    def create_basic_info_section(self, layout):
        """إنشاء قسم المعلومات الأساسية"""
        try:
            info_frame = QFrame()
            info_frame.setObjectName("studentInfoFrame")
            
            info_layout = QVBoxLayout(info_frame)
            info_layout.setContentsMargins(20, 15, 20, 15)
            
            # عنوان القسم
            title_label = QLabel("معلومات الطالب")
            title_label.setObjectName("sectionTitle")
            info_layout.addWidget(title_label)
            
            # شبكة المعلومات
            grid_layout = QGridLayout()
            grid_layout.setSpacing(15)
            
            # إنشاء التسميات
            self.name_label = QLabel("--")
            self.name_label.setObjectName("studentName")
            
            self.school_label = QLabel("--")
            self.school_label.setObjectName("infoValue")
            
            self.grade_label = QLabel("--")
            self.grade_label.setObjectName("infoValue")
            
            self.section_label = QLabel("--")
            self.section_label.setObjectName("infoValue")
            
            self.gender_label = QLabel("--")
            self.gender_label.setObjectName("infoValue")
            
            self.phone_label = QLabel("--")
            self.phone_label.setObjectName("infoValue")
            
            self.status_label = QLabel("--")
            self.status_label.setObjectName("infoValue")
            
            self.start_date_label = QLabel("--")
            self.start_date_label.setObjectName("infoValue")
            
            # إضافة المعلومات للشبكة
            # الصف الأول
            grid_layout.addWidget(QLabel("الاسم:"), 0, 0)
            grid_layout.addWidget(self.name_label, 0, 1)
            grid_layout.addWidget(QLabel("المدرسة:"), 0, 2)
            grid_layout.addWidget(self.school_label, 0, 3)
            grid_layout.addWidget(QLabel("الجنس:"), 0, 4)
            grid_layout.addWidget(self.gender_label, 0, 5)
            
            # الصف الثاني
            grid_layout.addWidget(QLabel("الصف:"), 1, 0)
            grid_layout.addWidget(self.grade_label, 1, 1)
            grid_layout.addWidget(QLabel("الشعبة:"), 1, 2)
            grid_layout.addWidget(self.section_label, 1, 3)
            grid_layout.addWidget(QLabel("الهاتف:"), 1, 4)
            grid_layout.addWidget(self.phone_label, 1, 5)
            
            # الصف الثالث
            grid_layout.addWidget(QLabel("الحالة:"), 2, 0)
            grid_layout.addWidget(self.status_label, 2, 1)
            grid_layout.addWidget(QLabel("تاريخ المباشرة:"), 2, 2)
            grid_layout.addWidget(self.start_date_label, 2, 3)
            
            info_layout.addLayout(grid_layout)
            layout.addWidget(info_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم المعلومات الأساسية: {e}")
            raise
    
    def create_financial_summary(self, layout):
        """إنشاء الملخص المالي"""
        try:
            summary_frame = QFrame()
            summary_frame.setObjectName("financialSummary")
            
            summary_layout = QHBoxLayout(summary_frame)
            summary_layout.setContentsMargins(15, 10, 15, 10)
            
            # القسط الكلي
            self.total_fee_label = QLabel("القسط الكلي: 0 د.ع")
            self.total_fee_label.setObjectName("totalFee")
            summary_layout.addWidget(self.total_fee_label)
            
            # المدفوع
            self.paid_amount_label = QLabel("المدفوع: 0 د.ع")
            self.paid_amount_label.setObjectName("paidAmount")
            summary_layout.addWidget(self.paid_amount_label)
            
            # المتبقي
            self.remaining_amount_label = QLabel("المتبقي: 0 د.ع")
            self.remaining_amount_label.setObjectName("remainingAmount")
            summary_layout.addWidget(self.remaining_amount_label)
            
            # عدد الدفعات
            self.installments_count_label = QLabel("عدد الدفعات: 0")
            self.installments_count_label.setObjectName("installmentsCount")
            summary_layout.addWidget(self.installments_count_label)
            
            layout.addWidget(summary_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الملخص المالي: {e}")
            raise
    
    def update_student_info(self, student_data):
        """تحديث معلومات الطالب"""
        try:
            self.student_data = student_data
            
            if not student_data:
                # قيم افتراضية في حالة عدم وجود بيانات
                self.name_label.setText("--")
                self.school_label.setText("--")
                self.grade_label.setText("--")
                self.section_label.setText("--")
                self.gender_label.setText("--")
                self.phone_label.setText("--")
                self.status_label.setText("--")
                self.start_date_label.setText("--")
                self.total_fee_label.setText("القسط الكلي: 0 د.ع")
                return
            
            # التحقق من طول البيانات
            if len(student_data) < 16:
                logging.warning(f"بيانات الطالب غير مكتملة: {len(student_data)} حقل")
                return
            
            # تحديث المعلومات
            self.name_label.setText(str(student_data[1]))  # name
            self.school_label.setText(str(student_data[-3] or "--"))  # school_name
            self.grade_label.setText(str(student_data[4]))  # grade
            self.section_label.setText(str(student_data[5]))  # section
            self.gender_label.setText(str(student_data[7]))  # gender
            self.phone_label.setText(str(student_data[8] or "--"))  # phone
            self.status_label.setText(str(student_data[13]))  # status
            self.start_date_label.setText(str(student_data[12]))  # start_date
            
            # تحديث القسط الكلي
            try:
                total_fee = float(student_data[11])
                self.total_fee_label.setText(f"القسط الكلي: {total_fee:,.0f} د.ع")
            except (ValueError, TypeError):
                logging.error(f"خطأ في تحويل القسط الكلي: {student_data[11]}")
                self.total_fee_label.setText("القسط الكلي: 0 د.ع")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث معلومات الطالب: {e}")
    
    def update_financial_summary(self, installments_data):
        """تحديث الملخص المالي"""
        try:
            self.installments_data = installments_data
            
            if not self.student_data or len(self.student_data) < 12:
                # قيم افتراضية في حالة عدم وجود بيانات
                self.total_fee_label.setText("القسط الكلي: 0 د.ع")
                self.paid_amount_label.setText("المدفوع: 0 د.ع")
                self.remaining_amount_label.setText("المتبقي: 0 د.ع")
                self.installments_count_label.setText("عدد الدفعات: 0")
                return
            
            # حساب المبلغ المدفوع من الأقساط
            total_paid = 0
            for installment in installments_data:
                try:
                    paid_amount = installment[6] if len(installment) > 6 and installment[6] else installment[1]
                    total_paid += float(paid_amount)
                except (ValueError, TypeError, IndexError):
                    continue
            
            # القسط الكلي
            try:
                total_fee = float(self.student_data[11])
            except (ValueError, TypeError):
                logging.error(f"خطأ في تحويل القسط الكلي: {self.student_data[11]}")
                total_fee = 0
            
            # المتبقي
            remaining = total_fee - total_paid
            
            # عدد الدفعات
            installments_count = len(installments_data)
            
            # تحديث التسميات
            self.total_fee_label.setText(f"القسط الكلي: {total_fee:,.0f} د.ع")
            self.paid_amount_label.setText(f"المدفوع: {total_paid:,.0f} د.ع")
            self.remaining_amount_label.setText(f"المتبقي: {remaining:,.0f} د.ع")
            self.installments_count_label.setText(f"عدد الدفعات: {installments_count}")
            
            # تلوين المتبقي
            if remaining > 0:
                self.remaining_amount_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
            else:
                self.remaining_amount_label.setStyleSheet("color: #27AE60; font-weight: bold;")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث الملخص المالي: {e}")
    
    def get_student_name(self):
        """الحصول على اسم الطالب"""
        return self.name_label.text() if self.name_label.text() != "--" else ""
    
    def get_school_info(self):
        """الحصول على معلومات المدرسة"""
        if not self.student_data or len(self.student_data) < 3:
            return {"name": "", "address": "", "phone": ""}
        
        return {
            "name": self.school_label.text(),
            "address": self.student_data[-2] if len(self.student_data) > 2 else "",
            "phone": self.student_data[-1] if len(self.student_data) > 1 else ""
        }
    
    def get_basic_info(self):
        """الحصول على المعلومات الأساسية"""
        return {
            "name": self.name_label.text(),
            "school": self.school_label.text(),
            "grade": self.grade_label.text(),
            "section": self.section_label.text(),
            "gender": self.gender_label.text(),
            "phone": self.phone_label.text(),
            "status": self.status_label.text(),
            "start_date": self.start_date_label.text()
        }
