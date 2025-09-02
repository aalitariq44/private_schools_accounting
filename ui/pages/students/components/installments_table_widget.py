#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مكون جدول الأقساط - عرض وإدارة الأقساط المدفوعة
"""
import logging
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFontDatabase

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation
from ..add_installment_dialog import AddInstallmentDialog
from core.printing.print_manager import print_payment_receipt


class InstallmentsTableWidget(QWidget):
    """مكون جدول الأقساط"""
    
    installment_added = pyqtSignal()
    installment_deleted = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.student_id = None
        self.student_data = None
        self.installments_data = []
        
        self.setup_cairo_font()
        self.setup_ui()
        self.setup_connections()
    
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
            
            # إنشاء قسم الأقساط
            self.create_installments_section(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة جدول الأقساط: {e}")
            raise
    
    def create_installments_section(self, layout):
        """إنشاء قسم الأقساط"""
        try:
            installments_frame = QFrame()
            installments_frame.setObjectName("installmentsFrame")
            
            installments_layout = QVBoxLayout(installments_frame)
            installments_layout.setContentsMargins(15, 15, 15, 15)
            
            # رأس القسم
            header_layout = QHBoxLayout()
            
            title_label = QLabel("الأقساط المدفوعة")
            title_label.setObjectName("sectionTitle")
            header_layout.addWidget(title_label)
            
            header_layout.addStretch()
            
            # زر إضافة قسط
            self.add_installment_button = QPushButton("+ إضافة قسط")
            self.add_installment_button.setObjectName("addButton")
            header_layout.addWidget(self.add_installment_button)
            
            installments_layout.addLayout(header_layout)
            
            # جدول الأقساط
            self.installments_table = QTableWidget()
            # إزالة padding في الصفوف لتظهر الأزرار بالكامل
            self.installments_table.setStyleSheet("QTableWidget::item { padding: 0px; }")
            self.installments_table.setObjectName("installmentsTable")
            
            # إعداد أعمدة الجدول
            columns = ["رقم الوصل", "المبلغ", "التاريخ", "وقت الدفع", "الملاحظات", "إجراءات"]
            self.installments_table.setColumnCount(len(columns))
            self.installments_table.setHorizontalHeaderLabels(columns)
            
            # إعداد خصائص الجدول
            self.installments_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.installments_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.installments_table.setAlternatingRowColors(True)
            
            # إعداد حجم الأعمدة
            header = self.installments_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # رقم الوصل
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # المبلغ
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # التاريخ
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # وقت الدفع
            header.setSectionResizeMode(4, QHeaderView.Stretch)          # الملاحظات
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # الإجراءات
            
            # ضبط ارتفاع الجدول ليكون أكبر
            self.installments_table.setMinimumHeight(450)  # زيادة الارتفاع
            
            installments_layout.addWidget(self.installments_table)
            layout.addWidget(installments_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الأقساط: {e}")
            raise
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            self.add_installment_button.clicked.connect(self.add_installment)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def set_student_data(self, student_id, student_data):
        """تعيين بيانات الطالب"""
        self.student_id = student_id
        self.student_data = student_data
    
    def load_installments(self):
        """تحميل الأقساط المدفوعة"""
        try:
            if not self.student_id:
                return
            
            query = """
                SELECT id, amount, payment_date, payment_time, notes
                FROM installments 
                WHERE student_id = ?
                ORDER BY created_at ASC
            """
            self.installments_data = db_manager.execute_query(query, (self.student_id,))
            self.update_installments_table()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الأقساط: {e}")
    
    def update_installments_table(self):
        """تحديث جدول الأقساط"""
        try:
            self.installments_table.setRowCount(len(self.installments_data))
            
            for row, installment in enumerate(self.installments_data):
                # رقم الوصل (id القسط)
                receipt_id_item = QTableWidgetItem(str(installment[0]))
                receipt_id_item.setTextAlignment(Qt.AlignCenter)
                self.installments_table.setItem(row, 0, receipt_id_item)
                
                # المبلغ
                amount_value = float(installment[1]) if installment and len(installment) > 1 else 0
                amount_item = QTableWidgetItem(f"{amount_value:,.0f} د.ع")
                amount_item.setTextAlignment(Qt.AlignCenter)
                self.installments_table.setItem(row, 1, amount_item)
                
                # التاريخ
                date_item = QTableWidgetItem(str(installment[2] or ""))
                date_item.setTextAlignment(Qt.AlignCenter)
                self.installments_table.setItem(row, 2, date_item)
                
                # وقت الدفع
                time_item = QTableWidgetItem(str(installment[3] or "--"))
                time_item.setTextAlignment(Qt.AlignCenter)
                self.installments_table.setItem(row, 3, time_item)
                
                # الملاحظات
                notes_item = QTableWidgetItem(str(installment[4] or ""))
                self.installments_table.setItem(row, 4, notes_item)
                
                # أزرار الإجراءات
                actions_layout = QHBoxLayout()
                # ضبط padding و spacing لعرض الأزرار بدون مساحة زائدة
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_layout.setSpacing(0)
                actions_widget = QWidget()
                
                # زر طباعة إيصال القسط
                print_btn = QPushButton("طباعة")
                print_btn.setObjectName("printButton")
                print_btn.setFixedSize(100, 30)
                # إضافة مارجن يمين ويسار للزر
                print_btn.setStyleSheet("margin-left:5px; margin-right:5px;")
                print_btn.clicked.connect(lambda checked, id=installment[0]: self.print_installment(id))
                actions_layout.addWidget(print_btn)
                
                delete_btn = QPushButton("حذف")
                delete_btn.setObjectName("deleteButton")
                delete_btn.setFixedSize(100, 30)
                # إضافة مارجن يمين ويسار للزر
                delete_btn.setStyleSheet("margin-left:5px; margin-right:5px;")
                delete_btn.clicked.connect(lambda checked, id=installment[0]: self.delete_installment(id))
                actions_layout.addWidget(delete_btn)
                
                actions_widget.setLayout(actions_layout)
                self.installments_table.setCellWidget(row, 5, actions_widget)
            
            # ضبط ارتفاع الصفوف
            for row in range(self.installments_table.rowCount()):
                self.installments_table.setRowHeight(row, 40)
            
        except Exception as e:
            logging.error(f"خطأ في تحديث جدول الأقساط: {e}")
    
    def add_installment(self):
        """إضافة قسط جديد"""
        try:
            if not self.student_data or len(self.student_data) < 12:
                QMessageBox.warning(self, "خطأ", "لا توجد بيانات صحيحة للطالب")
                return
            
            # حساب المتبقي
            total_paid = 0
            for installment in self.installments_data:
                try:
                    paid_amount = installment[6] if len(installment) > 6 and installment[6] else installment[1]
                    total_paid += float(paid_amount)
                except (ValueError, TypeError, IndexError):
                    continue
            
            # القسط الكلي
            try:
                total_fee = float(self.student_data[12])  # total_fee في الفهرس 12
            except (ValueError, TypeError):
                QMessageBox.warning(self, "خطأ", "قيمة القسط الكلي غير صحيحة")
                return
            
            remaining = total_fee - total_paid
            
            if remaining <= 0:
                QMessageBox.information(self, "تنبيه", "تم دفع القسط بالكامل")
                return
            
            # فتح نافذة إضافة قسط
            last_installment = {'id': None}
            dialog = AddInstallmentDialog(self.student_id, remaining, self)
            
            # التقاط المعرف عند الإضافة
            dialog.installment_saved.connect(lambda inst_id: last_installment.update({'id': inst_id}))
            
            if dialog.exec_() == QDialog.Accepted:
                # تحديث البيانات
                self.load_installments()
                self.installment_added.emit()
                
                # عرض معاينة وطباعة الإيصال للقسط الجديد
                if last_installment['id']:
                    self.print_installment(last_installment['id'])
                
        except Exception as e:
            logging.error(f"خطأ في إضافة قسط: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في إضافة القسط: {str(e)}")
    
    def print_installment(self, installment_id):
        """طباعة إيصال قسط منفصل"""
        try:
            log_user_action(f"طباعة إيصال القسط: {installment_id}")
            inst = next((i for i in self.installments_data if i[0] == installment_id), None)
            if not inst:
                return
            
            # حساب المجموع المدفوع والرصيد
            total_paid = 0
            for i in self.installments_data:
                paid_amount = i[6] if len(i) > 6 and i[6] else i[1]
                try:
                    total_paid += float(paid_amount)
                except:
                    continue
            
            try:
                total_fee = float(self.student_data[12])  # total_fee في الفهرس 12
            except:
                total_fee = 0
            remaining = total_fee - total_paid
            
            # معلومات المدرسة
            school_info = self.get_school_info()
            
            receipt = {
                'id': inst[0],
                'installment_id': inst[0],
                'student_name': str(self.student_data[1]),  # name في الفهرس 1
                'school_name': school_info["name"],
                'school_name_en': school_info["name_en"],
                'school_address': school_info["address"],
                'school_phone': school_info["phone"],
                'school_logo_path': school_info["logo_path"],
                'grade': str(self.student_data[4]),  # grade في الفهرس 4
                'section': str(self.student_data[5]),  # section في الفهرس 5,
                'payment_date': f"{inst[2]} {inst[3] or ''}",
                'payment_method': inst[4] or '',
                'description': inst[4] or '',
                'amount': float(inst[1]) if inst[1] else 0,
                'total_paid': total_paid,
                'total_fee': total_fee,
                'remaining': remaining
            }
            print_payment_receipt(receipt, parent=self)
            
        except Exception as e:
            logging.error(f"خطأ في طباعة إيصال القسط: {e}")
    
    def delete_installment(self, installment_id):
        """حذف قسط"""
        try:
            reply = QMessageBox.question(
                self, "تأكيد الحذف", 
                "هل أنت متأكد من حذف هذا القسط؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                query = "DELETE FROM installments WHERE id = ?"
                db_manager.execute_query(query, (installment_id,))
                
                log_database_operation(f"حذف قسط - معرف القسط: {installment_id}", "installments")
                log_user_action(f"حذف قسط للطالب: {self.student_id}")
                
                self.load_installments()
                self.installment_deleted.emit()
                
                QMessageBox.information(self, "نجح", "تم حذف القسط بنجاح")
                
        except Exception as e:
            logging.error(f"خطأ في حذف القسط: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في حذف القسط: {str(e)}")
    
    def get_school_info(self):
        """الحصول على معلومات المدرسة"""
        if not self.student_data or len(self.student_data) < 6:
            return {"name": "", "name_en": "", "address": "", "phone": "", "logo_path": ""}
        
        # معلومات المدرسة من JOIN في نهاية البيانات
        # البيانات بعد إضافة عمود notes:
        # 18: school_name, 19: school_name_en, 20: school_address, 21: school_phone, 22: school_logo_path
        return {
            "name": str(self.student_data[-5] or ""),  # school_name
            "name_en": str(self.student_data[-4] or ""),  # school_name_en
            "address": str(self.student_data[-3] or ""),  # school_address
            "phone": str(self.student_data[-2] or ""),  # school_phone
            "logo_path": str(self.student_data[-1] or "")  # school_logo_path
        }
    
    def get_installments_data(self):
        """الحصول على بيانات الأقساط"""
        return self.installments_data
    
    def refresh_data(self):
        """تحديث البيانات"""
        self.load_installments()
