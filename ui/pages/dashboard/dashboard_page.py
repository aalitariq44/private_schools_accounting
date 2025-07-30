#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة لوحة التحكم الرئيسية
"""

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QLabel, QPushButton, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap

from core.database.connection import db_manager
from core.utils.logger import log_user_action


class DashboardPage(QWidget):
    """صفحة لوحة التحكم"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styles()
        self.load_statistics()
        
        # تحديث الإحصائيات كل 5 دقائق
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_statistics)
        self.refresh_timer.start(300000)  # 5 دقائق
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(10)
            
            # العنوان والعام الدراسي
            self.create_header_section(main_layout)
            
            # إحصائيات سريعة
            self.create_statistics_section(main_layout)
            
            # الإجراءات السريعة
            self.create_quick_actions_section(main_layout)
            
            # معلومات النظام
            self.create_system_info_section(main_layout)
            
            # مساحة مرنة
            main_layout.addStretch()
            
            self.setLayout(main_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة لوحة التحكم: {e}")
            raise
    
    
    def create_header_section(self, layout):
        """إنشاء قسم الرأس مع العام الدراسي"""
        try:
            header_frame = QFrame()
            header_frame.setObjectName("dashboardHeader")
            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(10, 10, 10, 10)
            
            # عنوان لوحة التحكم
            title_label = QLabel("لوحة التحكم")
            title_label.setObjectName("dashboardTitle")
            title_font = QFont()
            title_font.setPointSize(20)
            title_font.setBold(True)
            title_label.setFont(title_font)
            
            header_layout.addWidget(title_label)
            header_layout.addStretch()
            
            # ويدجت العام الدراسي
            try:
                from ui.widgets.academic_year_widget import AcademicYearWidget
                self.academic_year_widget = AcademicYearWidget(show_label=True)
                header_layout.addWidget(self.academic_year_widget)
            except ImportError as e:
                logging.warning(f"لم يتم تحميل ويدجت العام الدراسي: {e}")
            
            header_frame.setLayout(header_layout)
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الرأس: {e}")
    
    def create_statistics_section(self, layout):
        """إنشاء قسم الإحصائيات السريعة"""
        try:
            stats_frame = QFrame()
            stats_frame.setObjectName("statsFrame")
            
            stats_layout = QVBoxLayout(stats_frame)
            stats_layout.setContentsMargins(2, 2, 2, 2)
            
            # عنوان القسم
            stats_title = QLabel("الإحصائيات السريعة")
            stats_title.setObjectName("sectionTitle")
            stats_layout.addWidget(stats_title)
            
            # شبكة الإحصائيات
            stats_grid = QGridLayout()
            stats_grid.setSpacing(1)
            

            # إنشاء بطاقات الإحصائيات الجديدة
            self.schools_card = self.create_stat_card("المدارس", "0", "#3498DB")
            self.students_card = self.create_stat_card("الطلاب", "0", "#27AE60")
            self.teachers_card = self.create_stat_card("المعلمين", "0", "#8E44AD")

            self.total_fees_card = self.create_stat_card("مجموع الرسوم الدراسية", "0 د.ع", "#F39C12")
            self.paid_fees_card = self.create_stat_card("مجموع الأقساط المدفوعة", "0 د.ع", "#2ECC71")
            self.remaining_fees_card = self.create_stat_card("المتبقي", "0 د.ع", "#E74C3C")

            self.additional_fees_card = self.create_stat_card("مجموع الرسوم الإضافية", "0 د.ع", "#9B59B6")
            self.additional_fees_paid_card = self.create_stat_card("الرسوم الإضافية المدفوعة فقط", "0 د.ع", "#16A085")
            self.additional_fees_unpaid_card = self.create_stat_card("الرسوم الإضافية غير المدفوعة فقط", "0 د.ع", "#D35400")

            # ترتيب البطاقات في الشبكة حسب الطلب
            # الصف الأول
            stats_grid.addWidget(self.schools_card, 0, 0)
            stats_grid.addWidget(self.students_card, 0, 1)
            stats_grid.addWidget(self.teachers_card, 0, 2)
            # الصف الثاني
            stats_grid.addWidget(self.total_fees_card, 1, 0)
            stats_grid.addWidget(self.paid_fees_card, 1, 1)
            stats_grid.addWidget(self.remaining_fees_card, 1, 2)
            # الصف الثالث
            stats_grid.addWidget(self.additional_fees_card, 2, 0)
            stats_grid.addWidget(self.additional_fees_paid_card, 2, 1)
            stats_grid.addWidget(self.additional_fees_unpaid_card, 2, 2)
            
            stats_layout.addLayout(stats_grid)
            layout.addWidget(stats_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الإحصائيات: {e}")
            raise
    
    def create_stat_card(self, title: str, value: str, color: str):
        """إنشاء بطاقة إحصائية"""
        try:
            card = QFrame()
            card.setObjectName("statCard")
            # Removed card.setFixedHeight(40)
            
            layout = QHBoxLayout(card)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(10, 10, 10, 10)
            
            # القيمة
            value_label = QLabel(value)
            value_label.setObjectName("statValue")
            value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            layout.addWidget(value_label)
            
            layout.addSpacing(10)
            
            # العنوان
            title_label = QLabel(title)
            title_label.setObjectName("statTitle")
            title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            layout.addWidget(title_label)
            
            # تطبيق اللون
            card.setStyleSheet(f"""
                #statCard {{
                    background-color: {color};
                    border-radius: 3px;
                    border: none;
                    box-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
                }}
                #statValue {{
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                }}
                #statTitle {{
                    color: rgba(255, 255, 255, 0.9);
                    font-size: 18px;
                    font-weight: bold;
                }}
            """)
            
            return card
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء بطاقة الإحصائية: {e}")
            return QFrame()
    
    def create_quick_actions_section(self, layout):
        """إنشاء قسم الإجراءات السريعة"""
        try:
            actions_frame = QFrame()
            actions_frame.setObjectName("actionsFrame")
            
            actions_layout = QVBoxLayout(actions_frame)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            # عنوان القسم
            actions_title = QLabel("الإجراءات السريعة")
            actions_title.setObjectName("sectionTitle")
            actions_layout.addWidget(actions_title)
            
            # أزرار الإجراءات
            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(5)
            
            # زر إضافة مدرسة
            add_school_btn = QPushButton("إضافة مدرسة جديدة")
            add_school_btn.setObjectName("actionButton")
            add_school_btn.clicked.connect(self.add_school_action)
            buttons_layout.addWidget(add_school_btn)
            
            # زر إضافة طالب
            add_student_btn = QPushButton("إضافة طالب جديد")
            add_student_btn.setObjectName("actionButton")
            add_student_btn.clicked.connect(self.add_student_action)
            buttons_layout.addWidget(add_student_btn)
            
            # زر إضافة قسط
            add_payment_btn = QPushButton("إدارة الاقساط")
            add_payment_btn.setObjectName("actionButton")
            add_payment_btn.clicked.connect(self.add_payment_action)
            buttons_layout.addWidget(add_payment_btn)
            
            # زر التقارير
            reports_btn = QPushButton("عرض التقارير")
            reports_btn.setObjectName("actionButton")
            reports_btn.clicked.connect(self.view_reports_action)
            buttons_layout.addWidget(reports_btn)
            
            actions_layout.addLayout(buttons_layout)
            layout.addWidget(actions_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الإجراءات السريعة: {e}")
            raise
    
    def create_system_info_section(self, layout):
        """إنشاء قسم معلومات النظام"""
        try:
            info_frame = QFrame()
            info_frame.setObjectName("infoFrame")
            
            info_layout = QVBoxLayout(info_frame)
            info_layout.setContentsMargins(5, 5, 5, 5)
            
            # عنوان القسم
            info_title = QLabel("معلومات النظام")
            info_title.setObjectName("sectionTitle")
            info_layout.addWidget(info_title)
            
            # معلومات النظام
            info_grid = QGridLayout()
            info_grid.setSpacing(3)
            
            # تاريخ آخر تحديث
            self.last_update_label = QLabel("آخر تحديث: جاري التحميل...")
            self.last_update_label.setObjectName("infoLabel")
            info_grid.addWidget(QLabel("آخر تحديث:"), 0, 0)
            info_grid.addWidget(self.last_update_label, 0, 1)
            
            # حالة قاعدة البيانات
            self.db_status_label = QLabel("متصل")
            self.db_status_label.setObjectName("infoLabel")
            info_grid.addWidget(QLabel("حالة قاعدة البيانات:"), 1, 0)
            info_grid.addWidget(self.db_status_label, 1, 1)
            
            # حالة النسخ الاحتياطي
            self.backup_status_label = QLabel("غير مفعل")
            self.backup_status_label.setObjectName("infoLabel")
            info_grid.addWidget(QLabel("النسخ الاحتياطي:"), 2, 0)
            info_grid.addWidget(self.backup_status_label, 2, 1)
            
            info_layout.addLayout(info_grid)
            layout.addWidget(info_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم معلومات النظام: {e}")
            raise
    
    def load_statistics(self):
        """تحميل الإحصائيات من قاعدة البيانات"""
        try:

            # الصف الأول
            schools_count = self.get_schools_count()
            self.update_stat_card(self.schools_card, str(schools_count))

            students_count = self.get_students_count()
            self.update_stat_card(self.students_card, str(students_count))

            teachers_count = self.get_teachers_count()
            self.update_stat_card(self.teachers_card, str(teachers_count))

            # الصف الثاني
            total_fees, paid_fees, remaining_fees = self.get_fees_statistics()
            self.update_stat_card(self.total_fees_card, f"{total_fees:,.0f} د.ع")
            self.update_stat_card(self.paid_fees_card, f"{paid_fees:,.0f} د.ع")
            self.update_stat_card(self.remaining_fees_card, f"{remaining_fees:,.0f} د.ع")

            # الصف الثالث
            additional_fees_total = self.get_additional_fees_total()
            additional_fees_paid = self.get_additional_fees_paid()
            additional_fees_unpaid = self.get_additional_fees_unpaid()
            self.update_stat_card(self.additional_fees_card, f"{additional_fees_total:,.0f} د.ع")
            self.update_stat_card(self.additional_fees_paid_card, f"{additional_fees_paid:,.0f} د.ع")
            self.update_stat_card(self.additional_fees_unpaid_card, f"{additional_fees_unpaid:,.0f} د.ع")
            
            # تحديث معلومات النظام
            self.update_system_info()
            
            log_user_action("تم تحديث إحصائيات لوحة التحكم")
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الإحصائيات: {e}")
    
    def get_teachers_count(self) -> int:
        """الحصول على عدد المعلمين"""
        try:
            query = "SELECT COUNT(*) as count FROM teachers"
            result = db_manager.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            logging.error(f"خطأ في الحصول على عدد المعلمين: {e}")
            return 0

    def get_additional_fees_paid(self) -> float:
        """الحصول على مجموع الرسوم الإضافية المدفوعة فقط"""
        try:
            query = "SELECT SUM(amount) as total FROM additional_fees WHERE paid = 1"
            result = db_manager.execute_query(query)
            return float(result[0]['total']) if result and result[0]['total'] else 0.0
        except Exception as e:
            logging.error(f"خطأ في الحصول على مجموع الرسوم الإضافية المدفوعة: {e}")
            return 0.0

    def get_additional_fees_unpaid(self) -> float:
        """الحصول على مجموع الرسوم الإضافية غير المدفوعة فقط"""
        try:
            query = "SELECT SUM(amount) as total FROM additional_fees WHERE paid = 0"
            result = db_manager.execute_query(query)
            return float(result[0]['total']) if result and result[0]['total'] else 0.0
        except Exception as e:
            logging.error(f"خطأ في الحصول على مجموع الرسوم الإضافية غير المدفوعة: {e}")
            return 0.0
            
            # تحديث معلومات النظام
            self.update_system_info()
            
            log_user_action("تم تحديث إحصائيات لوحة التحكم")
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الإحصائيات: {e}")
    
    def get_schools_count(self) -> int:
        """الحصول على عدد المدارس"""
        try:
            query = "SELECT COUNT(*) as count FROM schools"
            result = db_manager.execute_query(query)
            return result[0]['count'] if result else 0
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على عدد المدارس: {e}")
            return 0
    
    def get_students_count(self) -> int:
        """الحصول على عدد الطلاب"""
        try:
            query = "SELECT COUNT(*) as count FROM students"
            result = db_manager.execute_query(query)
            return result[0]['count'] if result else 0
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على عدد الطلاب: {e}")
            return 0
    
    def get_fees_statistics(self) -> tuple:
        """الحصول على إحصائيات الأقساط"""
        try:
            # إجمالي الأقساط
            total_query = "SELECT SUM(total_fee) as total FROM students"
            total_result = db_manager.execute_query(total_query)
            total_fees = total_result[0]['total'] if total_result and total_result[0]['total'] else 0
            
            # المبالغ المدفوعة
            paid_query = "SELECT SUM(amount) as paid FROM installments"
            paid_result = db_manager.execute_query(paid_query)
            paid_fees = paid_result[0]['paid'] if paid_result and paid_result[0]['paid'] else 0
            
            # المبالغ المتبقية
            remaining_fees = total_fees - paid_fees
            
            return float(total_fees), float(paid_fees), float(remaining_fees)
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على إحصائيات الأقساط: {e}")
            return 0.0, 0.0, 0.0
    
    def get_additional_fees_total(self) -> float:
        """الحصول على إجمالي جميع الرسوم الإضافية"""
        try:
            query = "SELECT SUM(amount) as total FROM additional_fees"
            result = db_manager.execute_query(query)
            return float(result[0]['total']) if result and result[0]['total'] else 0.0
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على إجمالي الرسوم الإضافية: {e}")
            return 0.0
    
    def update_stat_card(self, card: QFrame, value: str):
        """تحديث قيمة بطاقة الإحصائية"""
        try:
            # العثور على label القيمة وتحديثه
            value_label = card.findChild(QLabel, "statValue")
            if value_label:
                value_label.setText(value)
                
        except Exception as e:
            logging.error(f"خطأ في تحديث بطاقة الإحصائية: {e}")
    
    def update_system_info(self):
        """تحديث معلومات النظام"""
        try:
            from datetime import datetime
            
            # تحديث وقت آخر تحديث
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_update_label.setText(current_time)
            
            # التحقق من حالة قاعدة البيانات
            try:
                db_manager.execute_query("SELECT 1")
                self.db_status_label.setText("متصل")
                self.db_status_label.setStyleSheet("color: #27AE60;")
            except:
                self.db_status_label.setText("غير متصل")
                self.db_status_label.setStyleSheet("color: #E74C3C;")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث معلومات النظام: {e}")
    
    def add_school_action(self):
        """إجراء إضافة مدرسة"""
        try:
            # إرسال إشارة للنافذة الرئيسية للانتقال إلى صفحة المدارس
            from PyQt5.QtWidgets import QApplication
            main_window = QApplication.activeWindow()
            if main_window and hasattr(main_window, 'navigate_to_page'):
                main_window.navigate_to_page('schools')
            
            log_user_action("طلب إضافة مدرسة من لوحة التحكم")
            
        except Exception as e:
            logging.error(f"خطأ في إجراء إضافة مدرسة: {e}")
    
    def add_student_action(self):
        """إجراء إضافة طالب"""
        try:
            from PyQt5.QtWidgets import QApplication
            main_window = QApplication.activeWindow()
            if main_window and hasattr(main_window, 'navigate_to_page'):
                main_window.navigate_to_page('students')
            
            log_user_action("طلب إضافة طالب من لوحة التحكم")
            
        except Exception as e:
            logging.error(f"خطأ في إجراء إضافة طالب: {e}")
    
    def add_payment_action(self):
        """إجراء إضافة دفعة"""
        try:
            from PyQt5.QtWidgets import QApplication
            main_window = QApplication.activeWindow()
            if main_window and hasattr(main_window, 'navigate_to_page'):
                main_window.navigate_to_page('installments')
            
            log_user_action("طلب تسجيل دفعة من لوحة التحكم")
            
        except Exception as e:
            logging.error(f"خطأ في إجراء إضافة دفعة: {e}")
    
    def view_reports_action(self):
        """إجراء عرض التقارير"""
        try:
            from PyQt5.QtWidgets import QApplication
            main_window = QApplication.activeWindow()
            if main_window and hasattr(main_window, 'navigate_to_page'):
                main_window.navigate_to_page('reports')
            
            log_user_action("طلب عرض التقارير من لوحة التحكم")
            
        except Exception as e:
            logging.error(f"خطأ في إجراء عرض التقارير: {e}")
    
    def refresh(self):
        """تحديث الصفحة"""
        try:
            self.load_statistics()
            log_user_action("تم تحديث لوحة التحكم")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث لوحة التحكم: {e}")
    
    def setup_styles(self):
        """إعداد تنسيقات الصفحة"""
        try:
            style = """
                #dashboardHeader {
                    background-color: white;
                    border: 1px solid #E9ECEF;
                    border-radius: 12px;
                    margin-bottom: 20px;
                    padding: 5px;
                }
                
                #dashboardTitle {
                    color: #2C3E50;
                    font-size: 20px;
                    font-weight: bold;
                }
                
                #statsFrame, #actionsFrame, #infoFrame {
                    background-color: white;
                    border: 1px solid #E9ECEF;
                    border-radius: 12px;
                    margin-bottom: 20px;
                }
                
                #sectionTitle {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin-bottom: 10px;
                    padding-bottom: 8px;
                    border-bottom: 1px solid #ECF0F1;
                }
                
                #actionButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #3498DB, stop: 1 #2980B9);
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-size: 18px;
                    font-weight: bold;
                    min-width: 120px;
                }
                
                #actionButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2980B9, stop: 1 #2573A7);
                }
                
                #actionButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #21618C, stop: 1 #1E5A80);
                }
                
                #infoLabel {
                    color: #7F8C8D;
                    font-size: 18px;
                }
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد تنسيقات الصفحة: {e}")
