#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة اختيار الرسوم الإضافية للطباعة
"""

from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QCheckBox, QPushButton, QGroupBox,
    QButtonGroup, QRadioButton, QHeaderView, QAbstractItemView,
    QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from core.database.connection import db_manager
from core.utils.logger import log_user_action
import logging


class AdditionalFeesPrintDialog(QDialog):
    """نافذة اختيار الرسوم الإضافية للطباعة"""
    
    # إشارة لإرسال البيانات المحددة للطباعة
    print_requested = pyqtSignal(dict)
    
    def __init__(self, student_id, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.fees_data = []
        self.selected_fees = []
        
        self.setWindowTitle("طباعة إيصال الرسوم الإضافية")
        self.setFixedSize(800, 600)
        self.setModal(True)
        
        self.setup_ui()
        self.load_fees_data()
        self.setup_connections()
        
        log_user_action(f"فتح نافذة طباعة الرسوم الإضافية للطالب: {student_id}")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # العنوان
        title_label = QLabel("اختيار الرسوم الإضافية للطباعة")
        title_label.setObjectName("dialogTitle")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # مجموعة خيارات التصفية
        self.create_filter_group(layout)
        
        # مجموعة اختيار الرسوم
        self.create_selection_group(layout)
        
        # جدول الرسوم
        self.create_fees_table(layout)
        
        # أزرار العمليات
        self.create_action_buttons(layout)
        
        self.setLayout(layout)
        self.apply_styles()
    
    def create_filter_group(self, layout):
        """إنشاء مجموعة خيارات التصفية"""
        filter_group = QGroupBox("تصفية الرسوم")
        filter_layout = QHBoxLayout()
        
        # مجموعة أزرار الراديو للتصفية
        self.filter_group = QButtonGroup()
        
        self.all_fees_radio = QRadioButton("جميع الرسوم")
        self.filter_group.addButton(self.all_fees_radio, 0)
        filter_layout.addWidget(self.all_fees_radio)
        
        self.paid_only_radio = QRadioButton("المدفوع فقط")
        self.paid_only_radio.setChecked(True)
        self.filter_group.addButton(self.paid_only_radio, 1)
        filter_layout.addWidget(self.paid_only_radio)
        
        self.unpaid_only_radio = QRadioButton("غير المدفوع فقط")
        self.filter_group.addButton(self.unpaid_only_radio, 2)
        filter_layout.addWidget(self.unpaid_only_radio)
        
        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
    
    def create_selection_group(self, layout):
        """إنشاء مجموعة خيارات الاختيار"""
        selection_group = QGroupBox("اختيار الرسوم")
        selection_layout = QHBoxLayout()
        
        self.select_all_checkbox = QCheckBox("تحديد آخر 3 رسوم")
        self.select_all_checkbox.setChecked(True)
        selection_layout.addWidget(self.select_all_checkbox)
        
        selection_layout.addStretch()
        
        # معلومات الاختيار
        self.selection_info_label = QLabel("المحدد: 0 رسوم - المجموع: 0 د.ع")
        self.selection_info_label.setObjectName("selectionInfo")
        selection_layout.addWidget(self.selection_info_label)
        
        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)
    
    def create_fees_table(self, layout):
        """إنشاء جدول الرسوم"""
        self.fees_table = QTableWidget()
        self.fees_table.setObjectName("feesTable")
        
        # إعداد الأعمدة
        columns = ["اختيار", "النوع", "المبلغ", "الحالة", "تاريخ الإضافة", "تاريخ الدفع", "الملاحظات"]
        self.fees_table.setColumnCount(len(columns))
        self.fees_table.setHorizontalHeaderLabels(columns)
        
        # إعداد خصائص الجدول
        self.fees_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fees_table.setAlternatingRowColors(True)
        self.fees_table.verticalHeader().setVisible(False)
        
        # إعداد حجم الأعمدة
        header = self.fees_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # اختيار
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # النوع
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # المبلغ
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # الحالة
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # تاريخ الإضافة
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # تاريخ الدفع
        header.setSectionResizeMode(6, QHeaderView.Stretch)          # الملاحظات
        
        layout.addWidget(self.fees_table)
    
    def create_action_buttons(self, layout):
        """إنشاء أزرار العمليات"""
        buttons_layout = QHBoxLayout()
        
        # زر الإلغاء
        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setObjectName("cancelButton")
        buttons_layout.addWidget(self.cancel_button)
        
        # زر تشخيص (مؤقت للتصحيح)
        self.debug_button = QPushButton("تشخيص البيانات")
        self.debug_button.setObjectName("debugButton")
        buttons_layout.addWidget(self.debug_button)
        
        buttons_layout.addStretch()
        
        # زر المعاينة
        self.preview_button = QPushButton("معاينة")
        self.preview_button.setObjectName("previewButton")
        buttons_layout.addWidget(self.preview_button)
        
        # زر الطباعة
        self.print_button = QPushButton("طباعة")
        self.print_button.setObjectName("primaryButton")
        buttons_layout.addWidget(self.print_button)
        
        layout.addLayout(buttons_layout)
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        # أزرار التصفية
        self.filter_group.buttonClicked.connect(self.filter_fees)
        
        # خانة اختيار الجميع
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        
        # أزرار العمليات
        self.cancel_button.clicked.connect(self.reject)
        self.debug_button.clicked.connect(self.debug_data)
        self.preview_button.clicked.connect(self.preview_receipt)
        self.print_button.clicked.connect(self.print_receipt)
        
        # تحديث معلومات الاختيار عند تغيير التحديد
        self.fees_table.itemChanged.connect(self.update_selection_info)
    
    def load_fees_data(self):
        """تحميل بيانات الرسوم الإضافية"""
        try:
            query = """
                SELECT id, fee_type, amount, paid, payment_date, created_at, notes
                FROM additional_fees
                WHERE student_id = ?
                ORDER BY created_at DESC
            """
            self.fees_data = db_manager.execute_query(query, (self.student_id,))
            
            # تسجيل معلومات التشخيص
            logging.info(f"تحميل الرسوم الإضافية للطالب {self.student_id}: {len(self.fees_data) if self.fees_data else 0} رسم")
            
            # التحقق من وجود بيانات
            if not self.fees_data:
                self.fees_data = []
                logging.info("لا توجد رسوم إضافية للطالب")
            
            self.populate_table()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الرسوم الإضافية: {e}")
            import traceback
            logging.error(f"تفاصيل الخطأ: {traceback.format_exc()}")
            
            # في حالة الخطأ، تعيين قائمة فارغة
            self.fees_data = []
            self.populate_table()
            
            QMessageBox.warning(self, "تحذير", f"تعذر تحميل بيانات الرسوم الإضافية: {str(e)}")
            # لا نغلق النافذة، بل نعرض رسالة تحذير فقط
    
    def populate_table(self):
        """ملء الجدول بالبيانات"""
        try:
            filtered_fees = self.get_filtered_fees()
            self.fees_table.setRowCount(len(filtered_fees))
            
            logging.info(f"ملء الجدول بـ {len(filtered_fees)} رسم مفلتر")
            
            if not filtered_fees:
                # إذا لم توجد رسوم، عرض رسالة في الجدول
                self.fees_table.setRowCount(1)
                no_data_item = QTableWidgetItem("لا توجد رسوم إضافية لعرضها")
                no_data_item.setTextAlignment(Qt.AlignCenter)
                # دمج جميع الأعمدة لعرض الرسالة
                self.fees_table.setItem(0, 0, no_data_item)
                self.fees_table.setSpan(0, 0, 1, 7)  # دمج جميع الأعمدة السبعة
                
                # تحديث معلومات الاختيار
                self.update_selection_info()
                return
            
            for row, fee in enumerate(filtered_fees):
                try:
                    # التحقق من صحة البيانات
                    if not fee or len(fee) < 7:
                        logging.warning(f"بيانات رسم غير كاملة في الصف {row}: {fee}")
                        continue
                    
                    # خانة الاختيار
                    checkbox = QCheckBox()
                    # تحديد آخر 3 رسوم مضافة بشكل افتراضي
                    checkbox.setChecked(row < 3)
                    # ربط الحدث بالدالة التي تفرض قيد التحديد
                    checkbox.stateChanged.connect(
                        lambda state, cb=checkbox: self.on_checkbox_state_changed(cb, state)
                    )
                    self.fees_table.setCellWidget(row, 0, checkbox)
                    
                    # النوع
                    fee_type = str(fee[1]) if fee[1] else "غير محدد"
                    self.fees_table.setItem(row, 1, QTableWidgetItem(fee_type))
                    
                    # المبلغ
                    try:
                        amount = float(fee[2]) if fee[2] else 0
                        amount_item = QTableWidgetItem(f"{amount:,.0f} د.ع")
                    except (ValueError, TypeError):
                        amount_item = QTableWidgetItem("0 د.ع")
                    amount_item.setTextAlignment(Qt.AlignCenter)
                    self.fees_table.setItem(row, 2, amount_item)
                    
                    # الحالة
                    paid = bool(fee[3]) if fee[3] is not None else False
                    status = "مدفوع" if paid else "غير مدفوع"
                    status_item = QTableWidgetItem(status)
                    status_item.setTextAlignment(Qt.AlignCenter)
                    if paid:
                        status_item.setBackground(QColor(144, 238, 144))  # لون أخضر فاتح
                    else:
                        status_item.setBackground(QColor(255, 255, 0))    # لون أصفر
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
                    
                    logging.debug(f"تم إضافة الصف {row}: {fee_type}, {amount}, {status}")
                    
                except Exception as row_error:
                    logging.error(f"خطأ في معالجة الصف {row}: {row_error}")
                    continue
            
            self.update_selection_info()
            logging.info("تم ملء الجدول بنجاح")
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول الرسوم: {e}")
            import traceback
            logging.error(f"تفاصيل الخطأ: {traceback.format_exc()}")
            
            # في حالة الخطأ، عرض رسالة خطأ
            self.fees_table.setRowCount(1)
            error_item = QTableWidgetItem(f"خطأ في تحميل البيانات: {str(e)}")
            error_item.setTextAlignment(Qt.AlignCenter)
            self.fees_table.setItem(0, 0, error_item)
            self.fees_table.setSpan(0, 0, 1, 7)
    
    def get_filtered_fees(self):
        """الحصول على الرسوم المفلترة حسب الاختيار"""
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
        """تصفية الرسوم حسب الاختيار"""
        self.populate_table()
    
    def toggle_select_all(self, state):
        """تحديد أو إلغاء تحديد الرسوم (بحد أقصى 3)"""
        # إيقاف الإشارات مؤقتاً لتجنب استدعاء on_checkbox_state_changed بشكل متكرر
        for row in range(self.fees_table.rowCount()):
            checkbox = self.fees_table.cellWidget(row, 0)
            if checkbox:
                checkbox.blockSignals(True)

        if state == Qt.Checked:
            # تحديد أول 3 رسوم فقط
            for row in range(self.fees_table.rowCount()):
                checkbox = self.fees_table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(row < 3)
        else:
            # إلغاء تحديد الجميع
            for row in range(self.fees_table.rowCount()):
                checkbox = self.fees_table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(False)

        # إعادة تفعيل الإشارات
        for row in range(self.fees_table.rowCount()):
            checkbox = self.fees_table.cellWidget(row, 0)
            if checkbox:
                checkbox.blockSignals(False)
        
        # تحديث معلومات التحديد يدوياً لأن الإشارات كانت معطلة
        self.update_selection_info()

    def on_checkbox_state_changed(self, checkbox, state):
        """
        يتم استدعاؤه عند تغيير حالة أي خانة اختيار.
        يفرض قيد عدم تحديد أكثر من 3 رسوم.
        """
        if state == Qt.Checked:
            selected_count = 0
            for row in range(self.fees_table.rowCount()):
                cb = self.fees_table.cellWidget(row, 0)
                if cb and cb.isChecked():
                    selected_count += 1
            
            if selected_count > 3:
                QMessageBox.warning(self, "تنبيه", "لا يمكن تحديد أكثر من 3 رسوم للطباعة في الوصل الواحد.")
                # منع التحديد بإلغاء تحديد الخانة مع حظر الإشارات لتجنب التكرار
                checkbox.blockSignals(True)
                checkbox.setChecked(False)
                checkbox.blockSignals(False)

        # تحديث معلومات الملخص بعد أي تغيير
        self.update_selection_info()
    
    def update_selection_info(self):
        """تحديث معلومات الاختيار"""
        try:
            selected_count = 0
            selected_total = 0.0
            
            filtered_fees = self.get_filtered_fees()
            
            # إذا لم توجد رسوم، عرض رسالة مناسبة
            if not filtered_fees:
                self.selection_info_label.setText("لا توجد رسوم لعرضها")
                self.select_all_checkbox.setCheckState(Qt.Unchecked)
                return
            
            # حساب الرسوم المحددة
            for row in range(self.fees_table.rowCount()):
                checkbox = self.fees_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked() and row < len(filtered_fees):
                    selected_count += 1
                    try:
                        # التأكد من صحة البيانات قبل الإضافة
                        amount = float(filtered_fees[row][2]) if filtered_fees[row][2] else 0
                        selected_total += amount
                    except (ValueError, TypeError, IndexError):
                        logging.warning(f"مبلغ غير صحيح في الصف {row}")
                        continue
            
            # عرض المعلومات
            self.selection_info_label.setText(
                f"المحدد: {selected_count} رسوم - المجموع: {selected_total:,.0f} د.ع"
            )
            
            # تحديث حالة خانة تحديد الجميع
            total_rows_with_checkboxes = sum(1 for row in range(self.fees_table.rowCount()) 
                                           if self.fees_table.cellWidget(row, 0) is not None)
            
            if selected_count == 0:
                self.select_all_checkbox.setCheckState(Qt.Unchecked)
            elif selected_count == total_rows_with_checkboxes:
                self.select_all_checkbox.setCheckState(Qt.Checked)
            else:
                self.select_all_checkbox.setCheckState(Qt.PartiallyChecked)
                
        except Exception as e:
            logging.error(f"خطأ في تحديث معلومات الاختيار: {e}")
            self.selection_info_label.setText("خطأ في حساب الاختيار")
    
    def get_selected_fees_data(self):
        """الحصول على بيانات الرسوم المحددة"""
        try:
            selected_fees = []
            filtered_fees = self.get_filtered_fees()
            
            for row in range(self.fees_table.rowCount()):
                checkbox = self.fees_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked() and row < len(filtered_fees):
                    selected_fees.append(filtered_fees[row])
            
            return selected_fees
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على الرسوم المحددة: {e}")
            return []
    
    def preview_receipt(self):
        """معاينة الإيصال"""
        selected_fees = self.get_selected_fees_data()
        
        if not selected_fees:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار رسم واحد على الأقل للطباعة")
            return
        
        try:
            # إعداد بيانات الطباعة
            print_data = self.prepare_print_data(selected_fees)
            
            # إرسال إشارة المعاينة
            print_data['preview_only'] = True
            self.print_requested.emit(print_data)
            
        except Exception as e:
            logging.error(f"خطأ في معاينة الإيصال: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في معاينة الإيصال: {str(e)}")
    
    def print_receipt(self):
        """طباعة الإيصال"""
        selected_fees = self.get_selected_fees_data()
        
        if not selected_fees:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار رسم واحد على الأقل للطباعة")
            return
        
        try:
            # إعداد بيانات الطباعة
            print_data = self.prepare_print_data(selected_fees)
            
            # إرسال إشارة الطباعة
            print_data['preview_only'] = False
            self.print_requested.emit(print_data)
            
            # إغلاق النافذة
            self.accept()
            
        except Exception as e:
            logging.error(f"خطأ في طباعة الإيصال: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في طباعة الإيصال: {str(e)}")
    
    def prepare_print_data(self, selected_fees):
        """إعداد بيانات الطباعة"""
        try:
            # الحصول على معلومات الطالب
            student_query = """
                SELECT s.name, s.grade, s.section, sc.name_ar as school_name, sc.name_en as school_name_en, sc.logo_path as school_logo_path
                FROM students s
                LEFT JOIN schools sc ON s.school_id = sc.id
                WHERE s.id = ?
            """
            student_data = db_manager.execute_query(student_query, (self.student_id,))
            
            if not student_data:
                raise Exception("لم يتم العثور على بيانات الطالب")
            
            student = student_data[0]
            
            # حساب الإحصائيات
            total_amount = sum(fee[2] for fee in selected_fees)
            paid_amount = sum(fee[2] for fee in selected_fees if fee[3])
            unpaid_amount = total_amount - paid_amount
            fees_count = len(selected_fees)
            
            # تحضير بيانات الرسوم للطباعة
            fees_for_print = []
            for fee in selected_fees:
                fees_for_print.append({
                    'id': fee[0],
                    'fee_type': fee[1],
                    'amount': fee[2],
                    'paid': fee[3],
                    'payment_date': fee[4],
                    'created_at': fee[5],
                    'notes': fee[6]
                })
            
            # إعداد البيانات النهائية
            print_data = {
                'student': {
                    'id': self.student_id,
                    'name': student[0],
                    'grade': student[1],
                    'section': student[2],
                    'school_name': student[3],
                    'school_name_en': student[4] if len(student) > 4 else '',
                    'school_logo_path': student[5] if len(student) > 5 else ''
                },
                'fees': fees_for_print,
                'summary': {
                    'fees_count': fees_count,
                    'total_amount': total_amount,
                    'paid_amount': paid_amount,
                    'unpaid_amount': unpaid_amount
                },
                'print_date': datetime.now().strftime('%Y-%m-%d'),
                'print_time': datetime.now().strftime('%H:%M:%S'),
                'receipt_number': f'AF{datetime.now().strftime("%Y%m%d%H%M%S")}'
            }
            
            return print_data
            
        except Exception as e:
            logging.error(f"خطأ في إعداد بيانات الطباعة: {e}")
            raise
    
    def debug_data(self):
        """دالة تشخيص البيانات (مؤقتة للتصحيح)"""
        try:
            debug_info = []
            debug_info.append(f"معرف الطالب: {self.student_id}")
            debug_info.append(f"عدد الرسوم الأصلية: {len(self.fees_data) if self.fees_data else 0}")
            
            if self.fees_data:
                debug_info.append("الرسوم الأصلية:")
                for i, fee in enumerate(self.fees_data):
                    debug_info.append(f"  {i+1}. {fee}")
            
            filtered_fees = self.get_filtered_fees()
            debug_info.append(f"عدد الرسوم المفلترة: {len(filtered_fees)}")
            
            if filtered_fees:
                debug_info.append("الرسوم المفلترة:")
                for i, fee in enumerate(filtered_fees):
                    debug_info.append(f"  {i+1}. {fee}")
            
            debug_info.append(f"عدد صفوف الجدول: {self.fees_table.rowCount()}")
            debug_info.append(f"فلتر مختار: {self.filter_group.checkedId()}")
            
            # اختبار الاتصال بقاعدة البيانات
            try:
                test_query = "SELECT COUNT(*) FROM additional_fees WHERE student_id = ?"
                result = db_manager.execute_query(test_query, (self.student_id,))
                debug_info.append(f"عدد الرسوم في قاعدة البيانات: {result[0][0] if result else 'خطأ'}")
            except Exception as db_error:
                debug_info.append(f"خطأ في قاعدة البيانات: {db_error}")
            
            # عرض المعلومات في نافذة رسالة
            debug_text = "\n".join(debug_info)
            QMessageBox.information(self, "معلومات التشخيص", debug_text)
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ في التشخيص", f"فشل في تشخيص البيانات: {str(e)}")
    
    def apply_styles(self):
        """تطبيق التنسيقات"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLabel#dialogTitle {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                border: 2px solid #3498db;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QTableWidget#feesTable {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                gridline-color: #dee2e6;
            }
            
            QTableWidget#feesTable::item {
                padding: 8px;
                border-bottom: 1px solid #dee2e6;
            }
            
            QTableWidget#feesTable::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
            
            QLabel#selectionInfo {
                font-weight: bold;
                color: #2c3e50;
                background-color: #e8f4fd;
                padding: 5px 10px;
                border-radius: 3px;
                border: 1px solid #3498db;
            }
            
            QPushButton#primaryButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #229954;
            }
            
            QPushButton#previewButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton#previewButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton#cancelButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton#cancelButton:hover {
                background-color: #7f8c8d;
            }
            
            QRadioButton {
                font-weight: bold;
                spacing: 5px;
            }
            
            QRadioButton::indicator {
                width: 15px;
                height: 15px;
            }
            
            QRadioButton::indicator:checked {
                background-color: #3498db;
                border: 2px solid #2980b9;
                border-radius: 8px;
            }
            
            QCheckBox {
                font-weight: bold;
                spacing: 5px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            
            QCheckBox::indicator:checked {
                background-color: #27ae60;
                border: 2px solid #229954;
                border-radius: 3px;
            }
        """)
