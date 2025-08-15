#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة منبثقة للرسوم الإضافية - عرض شامل ومنظم
"""
import os
import logging
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase, QColor

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation
from ..add_additional_fee_dialog import AddAdditionalFeeDialog
from ..additional_fees_print_dialog import AdditionalFeesPrintDialog
from core.printing.additional_fees_print_manager import print_additional_fees_receipt


class AdditionalFeesPopup(QDialog):
    """نافذة منبثقة للرسوم الإضافية"""
    
    fees_updated = pyqtSignal()
    
    def __init__(self, student_id, student_data, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.student_data = student_data
        self.additional_fees_data = []
        
        self.setup_cairo_font()
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_additional_fees()
        
        log_user_action(f"فتح نافذة الرسوم الإضافية للطالب: {student_id}")
    
    def setup_cairo_font(self):
        """تحميل وتطبيق خط Cairo"""
        try:
            font_db = QFontDatabase()
            # استخدام خط من المجلد المحدد في config
            self.cairo_family = "Arial"  # خط افتراضي
        except Exception as e:
            logging.warning(f"فشل في تحميل خط Cairo: {e}")
            self.cairo_family = "Arial"
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            self.setWindowTitle("الرسوم الإضافية")
            self.setModal(True)
            self.resize(900, 600)
            
            # التخطيط الرئيسي
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(15, 15, 15, 15)
            main_layout.setSpacing(15)
            
            # رأس النافذة
            self.create_header(main_layout)
            
            # ملخص الرسوم الإضافية
            self.create_fees_summary(main_layout)
            
            # قسم الرسوم الإضافية
            self.create_fees_section(main_layout)
            
            # أزرار التحكم
            self.create_control_buttons(main_layout)
            
            self.setLayout(main_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة نافذة الرسوم الإضافية: {e}")
            raise
    
    def create_header(self, layout):
        """إنشاء رأس النافذة"""
        try:
            header_frame = QFrame()
            header_frame.setObjectName("headerFrame")
            
            header_layout = QVBoxLayout(header_frame)
            header_layout.setContentsMargins(20, 15, 20, 15)
            
            # عنوان النافذة
            title_label = QLabel("الرسوم الإضافية")
            title_label.setObjectName("popupTitle")
            title_label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(title_label)
            
            # معلومات الطالب
            if self.student_data:
                student_info = f"الطالب: {self.student_data[1]} - الصف: {self.student_data[4]}"
                info_label = QLabel(student_info)
                info_label.setObjectName("studentInfo")
                info_label.setAlignment(Qt.AlignCenter)
                header_layout.addWidget(info_label)
            
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء رأس النافذة: {e}")
            raise
    
    def create_fees_summary(self, layout):
        """إنشاء ملخص الرسوم الإضافية"""
        try:
            summary_frame = QFrame()
            summary_frame.setObjectName("feesSummaryFrame")
            
            summary_layout = QHBoxLayout(summary_frame)
            summary_layout.setContentsMargins(20, 15, 20, 15)
            
            # عدد الرسوم الإضافية
            self.fees_count_label = QLabel("عدد الرسوم: 0")
            self.fees_count_label.setObjectName("feesCount")
            summary_layout.addWidget(self.fees_count_label)
            
            # مجموع الرسوم الإضافية
            self.fees_total_label = QLabel("المجموع: 0 د.ع")
            self.fees_total_label.setObjectName("feesTotal")
            summary_layout.addWidget(self.fees_total_label)
            
            # المدفوع من الرسوم
            self.fees_paid_label = QLabel("المدفوع: 0 د.ع")
            self.fees_paid_label.setObjectName("feesPaid")
            summary_layout.addWidget(self.fees_paid_label)
            
            # غير المدفوع من الرسوم
            self.fees_unpaid_label = QLabel("غير المدفوع: 0 د.ع")
            self.fees_unpaid_label.setObjectName("feesUnpaid")
            summary_layout.addWidget(self.fees_unpaid_label)
            
            layout.addWidget(summary_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء ملخص الرسوم الإضافية: {e}")
            raise
    
    def create_fees_section(self, layout):
        """إنشاء قسم الرسوم الإضافية"""
        try:
            fees_frame = QFrame()
            fees_frame.setObjectName("feesFrame")
            
            fees_layout = QVBoxLayout(fees_frame)
            fees_layout.setContentsMargins(15, 15, 15, 15)
            
            # رأس القسم
            header_layout = QHBoxLayout()
            
            title_label = QLabel("قائمة الرسوم الإضافية")
            title_label.setObjectName("sectionTitle")
            header_layout.addWidget(title_label)
            
            header_layout.addStretch()
            
            # زر إضافة رسم
            self.add_fee_button = QPushButton("+ إضافة رسم")
            self.add_fee_button.setObjectName("addButton")
            header_layout.addWidget(self.add_fee_button)
            
            fees_layout.addLayout(header_layout)
            
            # جدول الرسوم الإضافية
            self.fees_table = QTableWidget()
            # إزالة padding في صفوف الجدول لإظهار الأزرار بشكل كامل
            self.fees_table.setStyleSheet("QTableWidget::item { padding: 0px; }")
            self.fees_table.setObjectName("feesTable")
            
            # إعداد أعمدة الجدول
            columns = ["النوع", "المبلغ", "تاريخ الإضافة", "تاريخ الدفع", "الحالة", "الملاحظات", "إجراءات"]
            self.fees_table.setColumnCount(len(columns))
            self.fees_table.setHorizontalHeaderLabels(columns)
            
            # إعداد خصائص الجدول
            self.fees_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.fees_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.fees_table.setAlternatingRowColors(True)
            
            # إعداد حجم الأعمدة
            header = self.fees_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # النوع
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # المبلغ
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # تاريخ الإضافة
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # تاريخ الدفع
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # الحالة
            header.setSectionResizeMode(5, QHeaderView.Stretch)          # الملاحظات
            header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # الإجراءات
            
            # ضبط ارتفاع الجدول
            self.fees_table.setMinimumHeight(300)
            
            fees_layout.addWidget(self.fees_table)
            layout.addWidget(fees_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الرسوم الإضافية: {e}")
            raise
    
    def create_control_buttons(self, layout):
        """إنشاء أزرار التحكم"""
        try:
            buttons_layout = QHBoxLayout()
            
            # زر طباعة إيصال الرسوم الإضافية
            self.print_fees_button = QPushButton("طباعة إيصال الرسوم")
            self.print_fees_button.setObjectName("printButton")
            buttons_layout.addWidget(self.print_fees_button)
            
            buttons_layout.addStretch()
            
            # زر إغلاق
            self.close_button = QPushButton("إغلاق")
            self.close_button.setObjectName("closeButton")
            buttons_layout.addWidget(self.close_button)
            
            layout.addLayout(buttons_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء أزرار التحكم: {e}")
            raise
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            self.add_fee_button.clicked.connect(self.add_additional_fee)
            self.print_fees_button.clicked.connect(self.print_additional_fees_receipt)
            self.close_button.clicked.connect(self.close)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def load_additional_fees(self):
        """تحميل الرسوم الإضافية"""
        try:
            query = """
                SELECT id, fee_type, amount, paid, payment_date, created_at, notes
                FROM additional_fees
                WHERE student_id = ?
                ORDER BY created_at DESC
            """
            self.additional_fees_data = db_manager.execute_query(query, (self.student_id,))
            self.update_fees_table()
            self.update_fees_summary()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الرسوم الإضافية: {e}")
    
    def update_fees_summary(self):
        """تحديث ملخص الرسوم الإضافية"""
        try:
            total_fees = 0
            paid_fees = 0
            fees_count = len(self.additional_fees_data)
            
            for fee in self.additional_fees_data:
                try:
                    amount = float(fee[2]) if fee[2] else 0
                    total_fees += amount
                    
                    is_paid = fee[3] if isinstance(fee[3], bool) else (fee[3] == 1 if fee[3] is not None else False)
                    if is_paid:
                        paid_fees += amount
                except (ValueError, TypeError, IndexError):
                    continue
            
            unpaid_fees = total_fees - paid_fees
            
            # تحديث التسميات
            self.fees_count_label.setText(f"عدد الرسوم: {fees_count}")
            self.fees_total_label.setText(f"المجموع: {total_fees:,.0f} د.ع")
            self.fees_paid_label.setText(f"المدفوع: {paid_fees:,.0f} د.ع")
            self.fees_unpaid_label.setText(f"غير المدفوع: {unpaid_fees:,.0f} د.ع")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث ملخص الرسوم الإضافية: {e}")
    
    def update_fees_table(self):
        """تحديث جدول الرسوم الإضافية"""
        try:
            self.fees_table.setRowCount(len(self.additional_fees_data))
            
            for row, fee in enumerate(self.additional_fees_data):
                # النوع
                type_item = QTableWidgetItem(str(fee[1]))
                self.fees_table.setItem(row, 0, type_item)
                
                # المبلغ
                amount_item = QTableWidgetItem(f"{float(fee[2]):,.0f} د.ع")
                self.fees_table.setItem(row, 1, amount_item)
                
                # تاريخ الإضافة
                date_item = QTableWidgetItem(str(fee[5] or "--"))
                self.fees_table.setItem(row, 2, date_item)
                
                # تاريخ الدفع
                payment_date_item = QTableWidgetItem(str(fee[4] or "--"))
                self.fees_table.setItem(row, 3, payment_date_item)
                
                # الحالة
                is_paid = fee[3] if isinstance(fee[3], bool) else (fee[3] == 1 if fee[3] is not None else False)
                status_text = "مدفوع" if is_paid else "غير مدفوع"
                status_item = QTableWidgetItem(status_text)
                if is_paid:
                    status_item.setBackground(QColor(144, 238, 144))  # أخضر فاتح
                else:
                    status_item.setBackground(QColor(255, 182, 193))  # أحمر فاتح
                self.fees_table.setItem(row, 4, status_item)
                
                # الملاحظات
                notes_item = QTableWidgetItem(str(fee[6] or ""))
                self.fees_table.setItem(row, 5, notes_item)
                
                # أزرار الإجراءات
                actions_layout = QHBoxLayout()
                # ضبط margins و spacing للعرض بدون مساحات زائدة
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_layout.setSpacing(0)
                actions_widget = QWidget()
                
                # إذا كان غير مدفوع، أضف زر الدفع
                if not is_paid:
                    pay_btn = QPushButton("دفع")
                    # إضافة مارجن يمين ويسار للزر
                    pay_btn.setStyleSheet("margin-left:5px; margin-right:5px;")
                    pay_btn.setObjectName("payButton")
                    pay_btn.setFixedSize(80, 25)
                    pay_btn.clicked.connect(lambda checked, id=fee[0]: self.pay_additional_fee(id))
                    actions_layout.addWidget(pay_btn)
            
                delete_btn = QPushButton("حذف")
                # إضافة مارجن يمين ويسار للزر
                delete_btn.setStyleSheet("margin-left:5px; margin-right:5px;")
                delete_btn.setObjectName("deleteButton")
                delete_btn.setFixedSize(80, 25)
                delete_btn.clicked.connect(lambda checked, id=fee[0]: self.delete_additional_fee(id))
                actions_layout.addWidget(delete_btn)
                
                actions_widget.setLayout(actions_layout)
                self.fees_table.setCellWidget(row, 6, actions_widget)
        
            # ضبط ارتفاع الصفوف
            for r in range(self.fees_table.rowCount()):
                self.fees_table.setRowHeight(r, 40)
        except Exception as e:
            logging.error(f"خطأ في تحديث جدول الرسوم الإضافية: {e}")
    
    def add_additional_fee(self):
        """إضافة رسم إضافي"""
        try:
            dialog = AddAdditionalFeeDialog(self.student_id, self)
            if dialog.exec_() == QDialog.Accepted:
                self.load_additional_fees()
                self.fees_updated.emit()
                
        except Exception as e:
            logging.error(f"خطأ في إضافة رسم إضافي: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في إضافة الرسم: {str(e)}")
    
    def delete_additional_fee(self, fee_id):
        """حذف رسم إضافي"""
        try:
            reply = QMessageBox.question(
                self, "تأكيد الحذف", 
                "هل أنت متأكد من حذف هذا الرسم؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                query = "DELETE FROM additional_fees WHERE id = ?"
                db_manager.execute_query(query, (fee_id,))
                
                log_database_operation(f"حذف رسم إضافي - معرف الرسم: {fee_id}", "additional_fees")
                log_user_action(f"حذف رسم إضافي للطالب: {self.student_id}")
                
                self.load_additional_fees()
                self.fees_updated.emit()
                
                QMessageBox.information(self, "نجح", "تم حذف الرسم بنجاح")
                
        except Exception as e:
            logging.error(f"خطأ في حذف الرسم الإضافي: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في حذف الرسم: {str(e)}")
    
    def pay_additional_fee(self, fee_id):
        """دفع رسم إضافي"""
        try:
            reply = QMessageBox.question(
                self, "تأكيد الدفع", 
                "هل تريد تسجيل هذا الرسم كمدفوع؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                current_date = date.today().strftime('%Y-%m-%d')
                
                query = """
                    UPDATE additional_fees 
                    SET paid = 1, payment_date = ?
                    WHERE id = ?
                """
                db_manager.execute_query(query, (current_date, fee_id))
                
                log_database_operation(f"دفع رسم إضافي - معرف الرسم: {fee_id}", "additional_fees")
                log_user_action(f"دفع رسم إضافي للطالب: {self.student_id}")
                
                self.load_additional_fees()
                self.fees_updated.emit()
                
                QMessageBox.information(self, "نجح", "تم تسجيل الدفع بنجاح")
                
        except Exception as e:
            logging.error(f"خطأ في دفع الرسم الإضافي: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في تسجيل الدفع: {str(e)}")
    
    def print_additional_fees_receipt(self):
        """فتح نافذة طباعة إيصال الرسوم الإضافية"""
        try:
            if not self.additional_fees_data:
                QMessageBox.information(
                    self, 
                    "معلومات", 
                    "لا توجد رسوم إضافية للطالب لطباعتها"
                )
                return
            
            # استخدام النظام الآمن للطباعة مباشرة
            from core.printing.additional_fees_safe_print import print_additional_fees_safe
            
            # تحضير بيانات الإيصال
            receipt_data = self.prepare_receipt_data()
            
            if receipt_data:
                print_additional_fees_safe(receipt_data, self)
            else:
                QMessageBox.warning(self, "تحذير", "لا توجد بيانات كافية للطباعة")
            
        except Exception as e:
            logging.error(f"خطأ في طباعة الرسوم الإضافية: {e}")
            QMessageBox.critical(
                self, 
                "خطأ", 
                f"فشل في طباعة الرسوم الإضافية: {str(e)}"
            )
    
    def prepare_receipt_data(self):
        """تحضير بيانات الإيصال للطباعة"""
        try:
            # معلومات الطالب
            student_name = self.student_data.get('name', '') if self.student_data else ''
            grade = self.student_data.get('grade', '') if self.student_data else ''
            section = self.student_data.get('section', '') if self.student_data else ''
            school_name = self.student_data.get('school_name', '') if self.student_data else ''
            
            # تحضير قائمة الرسوم
            fees_list = []
            total_amount = 0
            
            for fee in self.additional_fees_data:
                fee_data = {
                    'fee_type': fee.get('fee_type', ''),
                    'due_date': fee.get('due_date', ''),
                    'amount': float(fee.get('amount', 0)),
                    'is_paid': fee.get('payment_date') is not None
                }
                fees_list.append(fee_data)
                
                if fee_data['is_paid']:
                    total_amount += fee_data['amount']
            
            receipt_data = {
                'school_name': school_name,
                'school_address': '',  # يمكن إضافة معلومات المدرسة لاحقاً
                'school_phone': '',
                'student_name': student_name,
                'grade': grade,
                'section': section,
                'fees_list': fees_list,
                'total_amount': total_amount,
                'payment_date': datetime.now().strftime('%Y-%m-%d'),
                'receipt_number': f"FEES-{self.student_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            return receipt_data
            
        except Exception as e:
            logging.error(f"خطأ في تحضير بيانات الإيصال: {e}")
            return None
    
    def handle_fees_print_request(self, print_data):
        """معالجة طلب طباعة الرسوم الإضافية"""
        try:
            preview_only = print_data.get('preview_only', True)
            
            receipt_path = print_additional_fees_receipt(print_data, preview_only)
            
            if receipt_path and os.path.exists(receipt_path):
                if preview_only:
                    os.startfile(receipt_path)
                else:
                    import subprocess
                    subprocess.run(["print", receipt_path], shell=True)
            else:
                QMessageBox.warning(
                    self, 
                    "تحذير", 
                    "فشل في إنشاء ملف الإيصال"
                )
                
        except Exception as e:
            logging.error(f"خطأ في معالجة طلب طباعة الرسوم الإضافية: {e}")
            QMessageBox.critical(
                self, 
                "خطأ", 
                f"فشل في طباعة إيصال الرسوم الإضافية: {str(e)}"
            )
    
    def setup_styles(self):
        """إعداد التنسيقات"""
        try:
            cairo_font = f"'{self.cairo_family}', 'Cairo', 'Segoe UI', Tahoma, Arial"
            
            style = f"""
                QDialog {{
                    background-color: #F8F9FA;
                    font-family: {cairo_font};
                    font-size: 16px;
                }}
                
                #headerFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #3498DB, stop:1 #2980B9);
                    border-radius: 12px;
                    color: white;
                    margin-bottom: 15px;
                }}
                
                #popupTitle {{
                    font-size: 24px;
                    font-weight: bold;
                    color: black;
                    font-family: {cairo_font};
                }}
                
                #studentInfo {{
                    font-size: 16px;
                    color: black;
                    font-family: {cairo_font};
                }}
                
                #feesSummaryFrame {{
                    background-color: #F8F9FA;
                    border: 2px solid #BDC3C7;
                    border-radius: 10px;
                    margin: 15px 0px;
                }}
                
                #feesFrame {{
                    background-color: white;
                    border: 2px solid #E0E0E0;
                    border-radius: 15px;
                    margin: 8px 0px;
                }}
                
                #sectionTitle {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin-bottom: 15px;
                    font-family: {cairo_font};
                }}
                
                #feesTable {{
                    background-color: white;
                    border: 2px solid #E0E0E0;
                    border-radius: 12px;
                    gridline-color: #F0F0F0;
                    font-size: 16px;
                    font-family: {cairo_font};
                }}
                
                #feesTable::item {{
                    padding: 8px;
                    border-bottom: 1px solid #F0F0F0;
                }}
                
                #feesTable QHeaderView::section {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #34495E, stop:1 #2C3E50);
                    border: 1px solid #2C3E50;
                    padding: 10px;
                    font-weight: bold;
                    color: white;
                    font-size: 14px;
                    font-family: {cairo_font};
                }}
                
                #feesCount, #feesTotal, #feesPaid, #feesUnpaid {{
                    font-size: 16px;
                    font-weight: bold;
                    padding: 8px 15px;
                    border-radius: 8px;
                    font-family: {cairo_font};
                }}
                
                #feesCount {{
                    color: #2C3E50;
                    background-color: rgba(44, 62, 80, 0.1);
                    border: 2px solid #E0E0E0;
                }}
                
                #feesTotal {{
                    color: #2C3E50;
                    background-color: rgba(44, 62, 80, 0.1);
                    border: 2px solid #E0E0E0;
                }}
                
                #feesPaid {{
                    color: #27AE60;
                    background-color: rgba(39, 174, 96, 0.1);
                    border: 2px solid rgba(39, 174, 96, 0.3);
                }}
                
                #feesUnpaid {{
                    color: #E74C3C;
                    background-color: rgba(231, 76, 60, 0.1);
                    border: 2px solid rgba(231, 76, 60, 0.3);
                }}
                
                #addButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #27AE60, stop:1 #229954);
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 16px;
                    font-family: {cairo_font};
                }}
                
                #addButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #229954, stop:1 #1E8449);
                }}
                
                #deleteButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #E74C3C, stop:1 #C0392B);
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                    font-family: {cairo_font};
                }}
                
                #payButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #F39C12, stop:1 #E67E22);
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                    font-family: {cairo_font};
                }}
                
                #printButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #9B59B6, stop:1 #8E44AD);
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 16px;
                    font-family: {cairo_font};
                }}
                
                #closeButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #95A5A6, stop:1 #7F8C8D);
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 16px;
                    font-family: {cairo_font};
                }}
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد التنسيقات: {e}")
