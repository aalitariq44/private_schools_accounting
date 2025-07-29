#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصدار محسن من نافذة طباعة الرسوم الإضافية مع حل المشاكل
"""

from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QCheckBox, QPushButton, QGroupBox,
    QButtonGroup, QRadioButton, QHeaderView, QAbstractItemView,
    QFrame, QMessageBox, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from core.database.connection import db_manager
from core.utils.logger import log_user_action
import logging


class AdditionalFeesPrintDialogFixed(QDialog):
    """إصدار محسن من نافذة اختيار الرسوم الإضافية للطباعة"""
    
    # إشارة لإرسال البيانات المحددة للطباعة
    print_requested = pyqtSignal(dict)
    
    def __init__(self, student_id, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.fees_data = []
        self.selected_fees = []
        
        self.setWindowTitle("طباعة إيصال الرسوم الإضافية - محسن")
        self.setFixedSize(900, 700)
        self.setModal(True)
        
        # إعداد واجهة المستخدم
        self.setup_ui()
        
        # تحميل البيانات مع معالجة محسنة
        self.load_fees_data_enhanced()
        
        # ربط الإشارات
        self.setup_connections()
        
        log_user_action(f"فتح نافذة طباعة الرسوم الإضافية المحسنة للطالب: {student_id}")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم المحسنة"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # العنوان
        title_label = QLabel("اختيار الرسوم الإضافية للطباعة (محسن)")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
            border: 2px solid #3498db;
        """)
        layout.addWidget(title_label)
        
        # معلومات التشخيص
        self.debug_text = QTextEdit()
        self.debug_text.setMaximumHeight(100)
        self.debug_text.setReadOnly(True)
        layout.addWidget(self.debug_text)
        
        # مجموعة خيارات التصفية
        filter_group = QGroupBox("تصفية الرسوم")
        filter_layout = QHBoxLayout()
        
        self.filter_group = QButtonGroup()
        
        self.all_fees_radio = QRadioButton("جميع الرسوم")
        self.all_fees_radio.setChecked(True)
        self.filter_group.addButton(self.all_fees_radio, 0)
        filter_layout.addWidget(self.all_fees_radio)
        
        self.paid_only_radio = QRadioButton("المدفوع فقط")
        self.filter_group.addButton(self.paid_only_radio, 1)
        filter_layout.addWidget(self.paid_only_radio)
        
        self.unpaid_only_radio = QRadioButton("غير المدفوع فقط")
        self.filter_group.addButton(self.unpaid_only_radio, 2)
        filter_layout.addWidget(self.unpaid_only_radio)
        
        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # مجموعة اختيار الرسوم
        selection_group = QGroupBox("اختيار الرسوم")
        selection_layout = QHBoxLayout()
        
        self.select_all_checkbox = QCheckBox("تحديد الجميع")
        self.select_all_checkbox.setChecked(True)
        selection_layout.addWidget(self.select_all_checkbox)
        
        selection_layout.addStretch()
        
        self.selection_info_label = QLabel("المحدد: 0 رسوم - المجموع: 0 د.ع")
        selection_layout.addWidget(self.selection_info_label)
        
        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)
        
        # جدول الرسوم
        self.fees_table = QTableWidget()
        columns = ["اختيار", "النوع", "المبلغ", "الحالة", "تاريخ الإضافة", "تاريخ الدفع", "الملاحظات"]
        self.fees_table.setColumnCount(len(columns))
        self.fees_table.setHorizontalHeaderLabels(columns)
        self.fees_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fees_table.setAlternatingRowColors(True)
        self.fees_table.verticalHeader().setVisible(False)
        
        # إعداد حجم الأعمدة
        header = self.fees_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        
        layout.addWidget(self.fees_table)
        
        # أزرار العمليات
        buttons_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("إلغاء")
        buttons_layout.addWidget(self.cancel_button)
        
        self.reload_button = QPushButton("إعادة تحميل")
        buttons_layout.addWidget(self.reload_button)
        
        buttons_layout.addStretch()
        
        self.preview_button = QPushButton("معاينة")
        buttons_layout.addWidget(self.preview_button)
        
        self.print_button = QPushButton("طباعة")
        buttons_layout.addWidget(self.print_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        # أزرار التصفية
        self.filter_group.buttonClicked.connect(self.filter_fees)
        
        # خانة اختيار الجميع
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        
        # أزرار العمليات
        self.cancel_button.clicked.connect(self.reject)
        self.reload_button.clicked.connect(self.load_fees_data_enhanced)
        self.preview_button.clicked.connect(self.preview_receipt)
        self.print_button.clicked.connect(self.print_receipt)
    
    def add_debug_info(self, message):
        """إضافة معلومات تشخيص"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.debug_text.append(f"[{current_time}] {message}")
    
    def load_fees_data_enhanced(self):
        """تحميل بيانات الرسوم الإضافية مع معالجة محسنة"""
        try:
            self.add_debug_info(f"بدء تحميل الرسوم للطالب ID: {self.student_id}")
            
            # اختبار الاتصال بقاعدة البيانات أولاً
            try:
                test_query = "SELECT 1"
                db_manager.execute_query(test_query)
                self.add_debug_info("✅ اتصال قاعدة البيانات سليم")
            except Exception as db_test_error:
                self.add_debug_info(f"❌ مشكلة في اتصال قاعدة البيانات: {db_test_error}")
                raise db_test_error
            
            # التحقق من وجود جدول الرسوم الإضافية
            try:
                table_check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='additional_fees'"
                table_exists = db_manager.execute_query(table_check_query)
                if not table_exists:
                    self.add_debug_info("❌ جدول additional_fees غير موجود")
                    raise Exception("جدول الرسوم الإضافية غير موجود في قاعدة البيانات")
                else:
                    self.add_debug_info("✅ جدول additional_fees موجود")
            except Exception as table_error:
                self.add_debug_info(f"❌ خطأ في فحص الجدول: {table_error}")
                raise table_error
            
            # التحقق من وجود الطالب
            try:
                student_check_query = "SELECT name FROM students WHERE id = ?"
                student_data = db_manager.execute_query(student_check_query, (self.student_id,))
                if student_data:
                    student_name = student_data[0][0]
                    self.add_debug_info(f"✅ الطالب موجود: {student_name}")
                else:
                    self.add_debug_info(f"❌ الطالب ID {self.student_id} غير موجود")
                    raise Exception(f"الطالب رقم {self.student_id} غير موجود")
            except Exception as student_error:
                self.add_debug_info(f"❌ خطأ في فحص الطالب: {student_error}")
                raise student_error
            
            # تحميل الرسوم الإضافية
            query = """
                SELECT id, fee_type, amount, paid, payment_date, created_at, notes
                FROM additional_fees
                WHERE student_id = ?
                ORDER BY created_at DESC
            """
            
            self.add_debug_info("🔍 تنفيذ استعلام الرسوم...")
            self.fees_data = db_manager.execute_query(query, (self.student_id,))
            
            if self.fees_data is None:
                self.fees_data = []
                self.add_debug_info("⚠️ استعلام الرسوم أرجع None")
            else:
                self.add_debug_info(f"✅ تم تحميل {len(self.fees_data)} رسم")
            
            # عرض تفاصيل الرسوم المحملة
            if self.fees_data:
                self.add_debug_info("📋 تفاصيل الرسوم:")
                for i, fee in enumerate(self.fees_data):
                    fee_info = f"  {i+1}. {fee[1]} - {fee[2]:,} د.ع - {'مدفوع' if fee[3] else 'غير مدفوع'}"
                    self.add_debug_info(fee_info)
            else:
                self.add_debug_info("📭 لا توجد رسوم إضافية للطالب")
            
            # ملء الجدول
            self.populate_table_enhanced()
            
        except Exception as e:
            error_msg = f"خطأ في تحميل الرسوم: {str(e)}"
            self.add_debug_info(f"❌ {error_msg}")
            logging.error(error_msg)
            
            # في حالة الخطأ، تعيين قائمة فارغة
            self.fees_data = []
            self.populate_table_enhanced()
            
            QMessageBox.warning(self, "تحذير", error_msg)
    
    def populate_table_enhanced(self):
        """ملء الجدول بطريقة محسنة"""
        try:
            self.add_debug_info("🔄 بدء ملء الجدول...")
            
            filtered_fees = self.get_filtered_fees()
            self.fees_table.setRowCount(len(filtered_fees))
            
            if not filtered_fees:
                self.add_debug_info("📭 لا توجد رسوم لعرضها")
                # عرض رسالة في الجدول
                self.fees_table.setRowCount(1)
                no_data_item = QTableWidgetItem("لا توجد رسوم إضافية لعرضها")
                no_data_item.setTextAlignment(Qt.AlignCenter)
                self.fees_table.setItem(0, 0, no_data_item)
                self.fees_table.setSpan(0, 0, 1, 7)
                self.update_selection_info_enhanced()
                return
            
            # ملء البيانات
            for row, fee in enumerate(filtered_fees):
                try:
                    # خانة الاختيار
                    checkbox = QCheckBox()
                    checkbox.setChecked(True)
                    checkbox.stateChanged.connect(self.update_selection_info_enhanced)
                    self.fees_table.setCellWidget(row, 0, checkbox)
                    
                    # النوع
                    fee_type = str(fee[1]) if fee[1] else "غير محدد"
                    self.fees_table.setItem(row, 1, QTableWidgetItem(fee_type))
                    
                    # المبلغ
                    amount = float(fee[2]) if fee[2] else 0
                    amount_item = QTableWidgetItem(f"{amount:,.0f} د.ع")
                    amount_item.setTextAlignment(Qt.AlignCenter)
                    self.fees_table.setItem(row, 2, amount_item)
                    
                    # الحالة
                    paid = bool(fee[3])
                    status = "مدفوع" if paid else "غير مدفوع"
                    status_item = QTableWidgetItem(status)
                    status_item.setTextAlignment(Qt.AlignCenter)
                    if paid:
                        status_item.setBackground(Qt.lightGreen)
                    else:
                        status_item.setBackground(Qt.yellow)
                    self.fees_table.setItem(row, 3, status_item)
                    
                    # تاريخ الإضافة
                    created_date = str(fee[5]) if fee[5] else "--"
                    self.fees_table.setItem(row, 4, QTableWidgetItem(created_date))
                    
                    # تاريخ الدفع
                    payment_date = str(fee[4]) if fee[4] and paid else "--"
                    self.fees_table.setItem(row, 5, QTableWidgetItem(payment_date))
                    
                    # الملاحظات
                    notes = str(fee[6]) if fee[6] else ""
                    self.fees_table.setItem(row, 6, QTableWidgetItem(notes))
                    
                except Exception as row_error:
                    self.add_debug_info(f"❌ خطأ في الصف {row}: {row_error}")
                    continue
            
            self.add_debug_info(f"✅ تم ملء {len(filtered_fees)} صف في الجدول")
            self.update_selection_info_enhanced()
            
        except Exception as e:
            error_msg = f"خطأ في ملء الجدول: {str(e)}"
            self.add_debug_info(f"❌ {error_msg}")
            logging.error(error_msg)
    
    def get_filtered_fees(self):
        """الحصول على الرسوم المفلترة"""
        if not self.fees_data:
            return []
        
        filter_type = self.filter_group.checkedId()
        
        if filter_type == 1:  # المدفوع فقط
            return [fee for fee in self.fees_data if fee[3]]
        elif filter_type == 2:  # غير المدفوع فقط
            return [fee for fee in self.fees_data if not fee[3]]
        else:  # جميع الرسوم
            return self.fees_data
    
    def filter_fees(self):
        """تصفية الرسوم"""
        self.add_debug_info(f"🔍 تطبيق تصفية: {self.filter_group.checkedId()}")
        self.populate_table_enhanced()
    
    def toggle_select_all(self, state):
        """تبديل تحديد جميع الرسوم"""
        checked = state == Qt.Checked
        self.add_debug_info(f"🔄 تحديد الجميع: {checked}")
        
        for row in range(self.fees_table.rowCount()):
            checkbox = self.fees_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(checked)
    
    def update_selection_info_enhanced(self):
        """تحديث معلومات الاختيار"""
        try:
            selected_count = 0
            selected_total = 0.0
            
            filtered_fees = self.get_filtered_fees()
            
            if not filtered_fees:
                self.selection_info_label.setText("لا توجد رسوم لعرضها")
                return
            
            for row in range(self.fees_table.rowCount()):
                checkbox = self.fees_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked() and row < len(filtered_fees):
                    selected_count += 1
                    try:
                        amount = float(filtered_fees[row][2])
                        selected_total += amount
                    except (ValueError, TypeError, IndexError):
                        continue
            
            self.selection_info_label.setText(
                f"المحدد: {selected_count} رسوم - المجموع: {selected_total:,.0f} د.ع"
            )
            
        except Exception as e:
            self.add_debug_info(f"❌ خطأ في تحديث الاختيار: {e}")
    
    def preview_receipt(self):
        """معاينة الإيصال"""
        QMessageBox.information(self, "معاينة", "ميزة المعاينة قيد التطوير")
    
    def print_receipt(self):
        """طباعة الإيصال"""
        QMessageBox.information(self, "طباعة", "ميزة الطباعة قيد التطوير")
