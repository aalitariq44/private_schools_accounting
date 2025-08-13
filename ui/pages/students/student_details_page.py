#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة تفاصيل الطالب المحسنة - عرض شامل ومنظم لمعلومات الطالب والأقساط
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFontDatabase

from core.database.connection import db_manager
from core.utils.logger import log_user_action
from core.printing.print_manager import PrintManager
from core.printing.print_config import TemplateType

# استيراد المكونات الجديدة
from .components import (
    AdditionalFeesPopup,
    StudentInfoWidget,
    InstallmentsTableWidget,
    get_student_details_styles
)


class StudentDetailsPage(QWidget):
    """صفحة تفاصيل الطالب المحسنة"""
    
    # إشارات النافذة
    back_requested = pyqtSignal()
    student_updated = pyqtSignal()
    
    def __init__(self, student_id):
        super().__init__()
        self.student_id = student_id
        self.student_data = None
        
        # تحميل وتطبيق خط Cairo
        self.setup_cairo_font()
        
        # إنشاء المكونات
        self.student_info_widget = StudentInfoWidget(self)
        self.installments_widget = InstallmentsTableWidget(self)
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_student_data()
        
        log_user_action(f"فتح صفحة تفاصيل الطالب: {student_id}")
    
    def setup_cairo_font(self):
        """تحميل وتطبيق خط Cairo"""
        try:
            font_db = QFontDatabase()
            # محاولة تحميل خط Cairo من مجلد الموارد
            self.cairo_family = "Arial"  # خط افتراضي
            logging.info(f"تم استخدام الخط: {self.cairo_family}")
            
        except Exception as e:
            logging.warning(f"فشل في تحميل خط Cairo، استخدام الخط الافتراضي: {e}")
            self.cairo_family = "Arial"
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(10)
            
            # شريط الرجوع والأزرار
            self.create_toolbar(main_layout)
            
            # منطقة التمرير
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            
            # المحتوى الرئيسي
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(5, 5, 5, 5)
            content_layout.setSpacing(15)
            
            # إضافة مكون معلومات الطالب
            content_layout.addWidget(self.student_info_widget)
            
            # إضافة مكون جدول الأقساط (بحجم أكبر)
            content_layout.addWidget(self.installments_widget)
            
            scroll_area.setWidget(content_widget)
            main_layout.addWidget(scroll_area)
            
            self.setLayout(main_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة تفاصيل الطالب: {e}")
            raise
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات"""
        try:
            toolbar_frame = QFrame()
            toolbar_frame.setObjectName("backToolbar")
            
            toolbar_layout = QHBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(15, 10, 15, 10)
            
            # زر الرجوع
            self.back_button = QPushButton("← رجوع")
            self.back_button.setObjectName("backButton")
            toolbar_layout.addWidget(self.back_button)
            
            # عنوان الصفحة
            self.page_title = QLabel("تفاصيل الطالب")
            self.page_title.setObjectName("pageTitle")
            self.page_title.setAlignment(Qt.AlignCenter)
            self.page_title.setStyleSheet("color: black;")
            toolbar_layout.addWidget(self.page_title)
            # زر الرسوم الإضافية (جديد)
            self.additional_fees_button = QPushButton("الرسوم الإضافية")
            self.additional_fees_button.setObjectName("additionalFeesButton")
            toolbar_layout.addWidget(self.additional_fees_button)
            
            # زر التحديث
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("refreshButton")
            toolbar_layout.addWidget(self.refresh_button)
            
            # زر طباعة التفاصيل
            self.print_button = QPushButton("طباعة")
            self.print_button.setObjectName("primaryButton")
            toolbar_layout.addWidget(self.print_button)
            
            layout.addWidget(toolbar_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
            raise
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            # أزرار العمليات
            self.back_button.clicked.connect(self.back_requested.emit)
            self.refresh_button.clicked.connect(self.refresh_data)
            self.print_button.clicked.connect(self.print_details)
            self.additional_fees_button.clicked.connect(self.show_additional_fees_popup)
            
            # إشارات المكونات
            self.installments_widget.installment_added.connect(self.on_installment_changed)
            self.installments_widget.installment_deleted.connect(self.on_installment_changed)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def load_student_data(self):
        """تحميل بيانات الطالب"""
        try:
            # تحميل المعلومات الأساسية
            query = """
                SELECT s.*, sc.name_ar as school_name, sc.address as school_address, sc.phone as school_phone
                FROM students s
                LEFT JOIN schools sc ON s.school_id = sc.id
                WHERE s.id = ?
            """
            result = db_manager.execute_query(query, (self.student_id,))
            
            if result:
                self.student_data = result[0]
                self.update_page_data()
            else:
                # في حالة عدم العثور على بيانات
                self.student_data = None
                logging.warning(f"لم يتم العثور على بيانات للطالب: {self.student_id}")
                
                # عرض رسالة تحذير فقط في حالة عدم العثور على بيانات حقيقية
                if hasattr(self, 'parent') and self.parent():
                    QMessageBox.warning(self, "خطأ", "لم يتم العثور على بيانات الطالب")
                
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الطالب: {e}")
            self.student_data = None
            
            # عرض رسالة خطأ فقط في حالة وجود واجهة مستخدم
            if hasattr(self, 'parent') and self.parent():
                QMessageBox.critical(self, "خطأ", f"خطأ في تحميل البيانات: {str(e)}")
    
    def update_page_data(self):
        """تحديث بيانات الصفحة"""
        try:
            # تحديث عنوان الصفحة
            if self.student_data and len(self.student_data) > 1:
                student_name = str(self.student_data[1])
                self.page_title.setText(f"تفاصيل الطالب: {student_name}")
            
            # تحديث معلومات الطالب
            self.student_info_widget.update_student_info(self.student_data)
            
            # تعيين بيانات الطالب لمكون الأقساط
            self.installments_widget.set_student_data(self.student_id, self.student_data)
            
            # تحميل الأقساط
            self.installments_widget.load_installments()
            
            # تحديث الملخص المالي
            installments_data = self.installments_widget.get_installments_data()
            self.student_info_widget.update_financial_summary(installments_data)
            
        except Exception as e:
            logging.error(f"خطأ في تحديث بيانات الصفحة: {e}")
    
    def on_installment_changed(self):
        """معالجة تغييرات الأقساط"""
        try:
            # تحديث الملخص المالي
            installments_data = self.installments_widget.get_installments_data()
            self.student_info_widget.update_financial_summary(installments_data)
            
            # إرسال إشارة التحديث
            self.student_updated.emit()
            
        except Exception as e:
            logging.error(f"خطأ في معالجة تغييرات الأقساط: {e}")
    
    def show_additional_fees_popup(self):
        """عرض نافذة الرسوم الإضافية المنبثقة"""
        try:
            if not self.student_data:
                QMessageBox.warning(self, "خطأ", "لا توجد بيانات صحيحة للطالب")
                return
            
            # إنشاء وعرض النافذة المنبثقة
            popup = AdditionalFeesPopup(self.student_id, self.student_data, self)
            
            # ربط إشارة التحديث
            popup.fees_updated.connect(self.student_updated.emit)
            
            # عرض النافذة
            popup.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض نافذة الرسوم الإضافية: {e}")
            QMessageBox.critical(
                self, 
                "خطأ", 
                f"فشل في فتح نافذة الرسوم الإضافية: {str(e)}"
            )
    
    def print_details(self):
        """طباعة تفاصيل الطالب"""
        try:
            log_user_action(f"طباعة تفاصيل الطالب: {self.student_id}")
            
            if not self.student_data:
                QMessageBox.warning(self, "خطأ", "لا توجد بيانات للطباعة")
                return
            
            # جمع المعلومات للطباعة
            basic_info = self.student_info_widget.get_basic_info()
            school_info = self.student_info_widget.get_school_info()
            
            # بيانات الطالب
            try:
                total_fee = float(self.student_data[11])
            except Exception:
                total_fee = 0
            
            student = {
                'id': self.student_id,
                'name': basic_info['name'],
                'school_name': school_info['name'],
                'school_address': school_info['address'],
                'school_phone': school_info['phone'],
                'grade': basic_info['grade'],
                'section': basic_info['section'],
                'gender': basic_info['gender'],
                'phone': basic_info['phone'],
                'status': basic_info['status'],
                'total_fee': total_fee
            }
            
            # الأقساط
            installments_data = self.installments_widget.get_installments_data()
            installments = []
            for inst in installments_data:
                installments.append({
                    'amount': float(inst[1]) if inst[1] else 0,
                    'payment_date': inst[2],
                    'payment_time': inst[3],
                    'notes': inst[4]
                })
            
            # حساب الملخص المالي للأقساط فقط
            installments_total = sum(inst['amount'] for inst in installments)
            school_fee_remaining = student['total_fee'] - installments_total

            # إعداد الملخص المالي الأساسي
            financial_summary = {
                'installments_count': len(installments),
                'installments_total': installments_total,
                'school_fee_remaining': school_fee_remaining,
                'additional_fees_count': 0,
                'additional_fees_total': 0,
                'additional_fees_paid_total': 0,
                'additional_fees_unpaid_total': 0
            }

            # تحميل وحساب الرسوم الإضافية
            query_fees = """
                SELECT id, fee_type, amount, paid, payment_date, created_at, notes
                FROM additional_fees
                WHERE student_id = ?
                ORDER BY created_at DESC
            """
            fees_data = db_manager.execute_query(query_fees, (self.student_id,))
            additional_fees = []
            total_fees = 0
            paid_fees = 0
            for fee in fees_data:
                fee_amount = float(fee[2]) if fee[2] else 0
                is_paid = fee[3] if isinstance(fee[3], bool) else (fee[3] == 1 if fee[3] is not None else False)
                total_fees += fee_amount
                if is_paid:
                    paid_fees += fee_amount
                additional_fees.append({
                    'id': fee[0],
                    'fee_type': fee[1],
                    'amount': fee_amount,
                    'paid': is_paid,
                    'payment_date': fee[4],
                    'created_at': fee[5],
                    'notes': fee[6]
                })
            unpaid_fees = total_fees - paid_fees
            # تحديث الملخص المالي بالرسوم الإضافية
            financial_summary.update({
                'additional_fees_count': len(additional_fees),
                'additional_fees_total': total_fees,
                'additional_fees_paid_total': paid_fees,
                'additional_fees_unpaid_total': unpaid_fees
            })

            # معاينة الطباعة
            pm = PrintManager(self)
            pm.preview_document(TemplateType.STUDENT_REPORT, {
                'student': student,
                'installments': installments,
                'additional_fees': additional_fees,
                'financial_summary': financial_summary
            })
            
        except Exception as e:
            logging.error(f"خطأ في طباعة تفاصيل الطالب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في طباعة التفاصيل: {str(e)}")
    
    def refresh_data(self):
        """تحديث جميع البيانات"""
        try:
            self.load_student_data()
            
        except Exception as e:
            logging.error(f"خطأ في تحديث البيانات: {e}")
    
    def setup_styles(self):
        """إعداد التنسيقات"""
        try:
            # تطبيق الأنماط من الملف المنفصل
            style = get_student_details_styles(self.cairo_family)
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد التنسيقات: {e}")
