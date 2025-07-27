#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مثال شامل: إضافة نظام الطباعة لصفحة المالية
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QComboBox, QDateEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

# استيراد نظام الطباعة
from core.printing import print_manager, PrintHelper, QuickPrintMixin, apply_print_styles, TemplateType
from core.database.connection import db_manager
from core.utils.logger import log_user_action


class FinancialPageWithPrint(QWidget, QuickPrintMixin):
    """مثال على صفحة مالية مع نظام طباعة شامل"""
    
    def __init__(self):
        super().__init__()
        self.current_financial_data = []
        self.current_payments = []
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.setup_quick_print()  # تفعيل الطباعة السريعة
        self.load_financial_data()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # شريط الأدوات مع أزرار الطباعة
        self.create_toolbar(layout)
        
        # جدول البيانات المالية
        self.create_financial_table(layout)
        
        # إحصائيات سريعة
        self.create_summary_section(layout)
        
        self.setLayout(layout)
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات مع أزرار الطباعة"""
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("toolbarFrame")
        
        toolbar_layout = QHBoxLayout(toolbar_frame)
        
        # فلاتر التاريخ
        start_date_label = QLabel("من تاريخ:")
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        
        end_date_label = QLabel("إلى تاريخ:")
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        
        # فلتر نوع المعاملة
        type_label = QLabel("نوع المعاملة:")
        self.transaction_type = QComboBox()
        self.transaction_type.addItems(["جميع المعاملات", "إيرادات", "مصروفات", "رسوم دراسية", "رواتب"])
        
        toolbar_layout.addWidget(start_date_label)
        toolbar_layout.addWidget(self.start_date)
        toolbar_layout.addWidget(end_date_label)
        toolbar_layout.addWidget(self.end_date)
        toolbar_layout.addWidget(type_label)
        toolbar_layout.addWidget(self.transaction_type)
        
        toolbar_layout.addStretch()
        
        # أزرار الطباعة
        print_section = self.create_print_section()
        toolbar_layout.addLayout(print_section)
        
        layout.addWidget(toolbar_frame)
    
    def create_print_section(self):
        """إنشاء قسم أزرار الطباعة"""
        print_layout = QHBoxLayout()
        
        # زر طباعة التقرير المالي
        self.print_financial_btn = QPushButton("طباعة التقرير المالي")
        self.print_financial_btn.setObjectName("printButton")
        self.print_financial_btn.clicked.connect(self.print_financial_report)
        print_layout.addWidget(self.print_financial_btn)
        
        # زر طباعة قائمة المعاملات
        self.print_transactions_btn = QPushButton("طباعة المعاملات")
        self.print_transactions_btn.setObjectName("printButton")
        self.print_transactions_btn.clicked.connect(self.print_transactions_list)
        print_layout.addWidget(self.print_transactions_btn)
        
        # زر الطباعة السريعة
        self.quick_print_btn = QPushButton("طباعة سريعة")
        self.quick_print_btn.setObjectName("quickPrintButton")
        self.quick_print_btn.clicked.connect(self.quick_print_current_data)
        print_layout.addWidget(self.quick_print_btn)
        
        # زر تصدير PDF
        self.export_pdf_btn = QPushButton("تصدير PDF")
        self.export_pdf_btn.setObjectName("exportButton")
        self.export_pdf_btn.clicked.connect(self.export_financial_pdf)
        print_layout.addWidget(self.export_pdf_btn)
        
        # زر طباعة الإيصالات
        self.print_receipts_btn = QPushButton("طباعة الإيصالات")
        self.print_receipts_btn.setObjectName("printButton")
        self.print_receipts_btn.clicked.connect(self.print_selected_receipts)
        print_layout.addWidget(self.print_receipts_btn)
        
        return print_layout
    
    def create_financial_table(self, layout):
        """إنشاء جدول البيانات المالية"""
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        
        table_layout = QVBoxLayout(table_frame)
        
        # الجدول
        self.financial_table = QTableWidget()
        self.financial_table.setObjectName("dataTable")
        
        columns = ["التاريخ", "الوصف", "النوع", "المبلغ", "الطالب/الموظف", "ملاحظات"]
        self.financial_table.setColumnCount(len(columns))
        self.financial_table.setHorizontalHeaderLabels(columns)
        
        table_layout.addWidget(self.financial_table)
        layout.addWidget(table_frame)
    
    def create_summary_section(self, layout):
        """إنشاء قسم الملخص المالي"""
        summary_frame = QFrame()
        summary_frame.setObjectName("summaryFrame")
        
        summary_layout = QHBoxLayout(summary_frame)
        
        self.total_income_label = QLabel("إجمالي الإيرادات: 0")
        self.total_income_label.setObjectName("summaryLabel")
        
        self.total_expenses_label = QLabel("إجمالي المصروفات: 0")
        self.total_expenses_label.setObjectName("summaryLabel")
        
        self.net_profit_label = QLabel("صافي الربح: 0")
        self.net_profit_label.setObjectName("summaryLabel")
        
        summary_layout.addWidget(self.total_income_label)
        summary_layout.addWidget(self.total_expenses_label)
        summary_layout.addWidget(self.net_profit_label)
        summary_layout.addStretch()
        
        layout.addWidget(summary_frame)
    
    def setup_connections(self):
        """ربط الإشارات"""
        self.start_date.dateChanged.connect(self.apply_filters)
        self.end_date.dateChanged.connect(self.apply_filters)
        self.transaction_type.currentTextChanged.connect(self.apply_filters)
    
    def load_financial_data(self):
        """تحميل البيانات المالية"""
        try:
            # هنا يتم جلب البيانات من قاعدة البيانات
            # مثال على البيانات التجريبية
            self.current_financial_data = [
                {
                    'date': '2024-01-15',
                    'description': 'رسوم دراسية',
                    'type': 'إيراد',
                    'amount': 500000,
                    'person': 'أحمد محمد',
                    'notes': 'شهر كانون الثاني'
                },
                {
                    'date': '2024-01-20',
                    'description': 'راتب موظف',
                    'type': 'مصروف',
                    'amount': 800000,
                    'person': 'سارة أحمد',
                    'notes': 'راتب شهر كانون الثاني'
                }
            ]
            
            self.fill_financial_table()
            self.update_summary()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في تحميل البيانات: {str(e)}")
    
    def fill_financial_table(self):
        """ملء الجدول بالبيانات"""
        self.financial_table.setRowCount(len(self.current_financial_data))
        
        for row, data in enumerate(self.current_financial_data):
            self.financial_table.setItem(row, 0, QTableWidgetItem(data['date']))
            self.financial_table.setItem(row, 1, QTableWidgetItem(data['description']))
            self.financial_table.setItem(row, 2, QTableWidgetItem(data['type']))
            self.financial_table.setItem(row, 3, QTableWidgetItem(f"{data['amount']:,}"))
            self.financial_table.setItem(row, 4, QTableWidgetItem(data['person']))
            self.financial_table.setItem(row, 5, QTableWidgetItem(data['notes']))
    
    def update_summary(self):
        """تحديث الملخص المالي"""
        total_income = sum(item['amount'] for item in self.current_financial_data if item['type'] == 'إيراد')
        total_expenses = sum(item['amount'] for item in self.current_financial_data if item['type'] == 'مصروف')
        net_profit = total_income - total_expenses
        
        self.total_income_label.setText(f"إجمالي الإيرادات: {total_income:,}")
        self.total_expenses_label.setText(f"إجمالي المصروفات: {total_expenses:,}")
        self.net_profit_label.setText(f"صافي الربح: {net_profit:,}")
    
    def apply_filters(self):
        """تطبيق الفلاتر"""
        # هنا يتم تطبيق الفلاتر وإعادة تحميل البيانات
        self.load_financial_data()
    
    # وظائف الطباعة
    def print_financial_report(self):
        """طباعة التقرير المالي الشامل"""
        try:
            total_income = sum(item['amount'] for item in self.current_financial_data if item['type'] == 'إيراد')
            total_expenses = sum(item['amount'] for item in self.current_financial_data if item['type'] == 'مصروف')
            
            financial_data = {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'transactions': self.current_financial_data
            }
            
            date_range = f"{self.start_date.date().toString('yyyy-MM-dd')} إلى {self.end_date.date().toString('yyyy-MM-dd')}"
            
            print_manager.print_financial_report(financial_data, date_range, self)
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في طباعة التقرير المالي: {str(e)}")
    
    def print_transactions_list(self):
        """طباعة قائمة المعاملات"""
        try:
            if not self.current_financial_data:
                QMessageBox.warning(self, "تحذير", "لا توجد معاملات للطباعة")
                return
            
            # يمكن إنشاء قالب خاص للمعاملات أو استخدام قالب موجود
            print_manager.print_custom_report(
                TemplateType.CUSTOM,  # يحتاج إنشاء قالب للمعاملات
                {'transactions': self.current_financial_data},
                "قائمة المعاملات المالية",
                self
            )
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في طباعة المعاملات: {str(e)}")
    
    def export_financial_pdf(self):
        """تصدير التقرير المالي إلى PDF"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "حفظ التقرير المالي", 
                f"التقرير_المالي_{self.start_date.date().toString('yyyy-MM-dd')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                total_income = sum(item['amount'] for item in self.current_financial_data if item['type'] == 'إيراد')
                total_expenses = sum(item['amount'] for item in self.current_financial_data if item['type'] == 'مصروف')
                
                financial_data = {
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'transactions': self.current_financial_data
                }
                
                date_range = f"{self.start_date.date().toString('yyyy-MM-dd')} إلى {self.end_date.date().toString('yyyy-MM-dd')}"
                data = {
                    'financial_data': financial_data,
                    'date_range': date_range
                }
                
                print_manager.export_to_pdf(TemplateType.FINANCIAL_REPORT, data, file_path, self)
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في تصدير PDF: {str(e)}")
    
    def print_selected_receipts(self):
        """طباعة إيصالات للمعاملات المحددة"""
        try:
            selected_rows = []
            for i in range(self.financial_table.rowCount()):
                if self.financial_table.item(i, 0).isSelected():
                    selected_rows.append(i)
            
            if not selected_rows:
                QMessageBox.warning(self, "تحذير", "يرجى تحديد المعاملات المراد طباعة إيصالاتها")
                return
            
            for row in selected_rows:
                transaction = self.current_financial_data[row]
                
                receipt_data = {
                    'id': f"REC-{row + 1:03d}",
                    'student_name': transaction['person'],
                    'school_name': 'مدرسة النور الأهلية',
                    'payment_date': transaction['date'],
                    'payment_method': 'نقداً',
                    'description': transaction['description'],
                    'amount': transaction['amount']
                }
                
                print_manager.print_payment_receipt(receipt_data, self)
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في طباعة الإيصالات: {str(e)}")
    
    # وظائف مطلوبة من QuickPrintMixin
    def get_current_data_for_print(self):
        """البيانات الحالية للطباعة السريعة"""
        return self.current_financial_data
    
    def get_current_filters_info(self):
        """معلومات الفلاتر المطبقة"""
        filters = {
            'start_date': self.start_date.date().toString('yyyy-MM-dd'),
            'end_date': self.end_date.date().toString('yyyy-MM-dd'),
            'transaction_type': self.transaction_type.currentText()
        }
        
        filter_parts = []
        if filters['start_date']:
            filter_parts.append(f"من: {filters['start_date']}")
        if filters['end_date']:
            filter_parts.append(f"إلى: {filters['end_date']}")
        if filters['transaction_type'] != "جميع المعاملات":
            filter_parts.append(f"النوع: {filters['transaction_type']}")
        
        return " | ".join(filter_parts) if filter_parts else "بدون فلاتر"
    
    def setup_styles(self):
        """تطبيق التنسيقات"""
        base_style = """
            QWidget {
                background-color: #F8F9FA;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            
            #toolbarFrame {
                background-color: white;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
            }
            
            #tableFrame {
                background-color: white;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                padding: 10px;
            }
            
            #dataTable {
                border: none;
                gridline-color: #E9ECEF;
            }
            
            #summaryFrame {
                background-color: #E8F5E8;
                border: 1px solid #C3E6CB;
                border-radius: 8px;
                padding: 15px;
                margin-top: 15px;
            }
            
            #summaryLabel {
                font-size: 16px;
                font-weight: bold;
                color: #155724;
                padding: 5px 15px;
            }
        """
        
        # إضافة تنسيقات الطباعة
        full_style = base_style + apply_print_styles()
        self.setStyleSheet(full_style)


# مثال على الاستخدام
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    app.setLayoutDirection(2)  # Right to Left
    
    window = FinancialPageWithPrint()
    window.show()
    
    sys.exit(app.exec_())
