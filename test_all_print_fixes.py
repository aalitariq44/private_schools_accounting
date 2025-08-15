# -*- coding: utf-8 -*-
"""
اختبار شامل لإصلاحات الطباعة
"""

import sys
import os
import logging
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox, QTextEdit
from PyQt5.QtCore import Qt

def test_installment_print():
    """اختبار طباعة إيصال القسط"""
    try:
        from core.printing.print_manager import print_payment_receipt
        
        sample_data = {
            'id': 1,
            'student_name': 'أحمد محمد علي',
            'school_name': 'مدرسة الأمل الأهلية',
            'school_address': 'بغداد - الكرادة',
            'school_phone': '07801234567',
            'grade': 'الصف الأول',
            'section': 'أ',
            'payment_date': '2025-08-15',
            'payment_method': 'نقداً',
            'amount': 250000,
            'total_paid': 500000,
            'total_fee': 1000000,
            'remaining': 500000
        }
        
        print_payment_receipt(sample_data)
        return True
        
    except Exception as e:
        logging.error(f"خطأ في اختبار طباعة إيصال القسط: {e}")
        return False

def test_additional_fees_print():
    """اختبار طباعة الرسوم الإضافية"""
    try:
        from core.printing.additional_fees_safe_print import print_additional_fees_safe
        
        sample_data = {
            'school_name': 'مدرسة الأمل الأهلية',
            'school_address': 'بغداد - الكرادة',
            'school_phone': '07801234567',
            'student_name': 'أحمد محمد علي',
            'grade': 'الصف الأول',
            'section': 'أ',
            'fees_list': [
                {
                    'fee_type': 'رسوم النشاطات',
                    'due_date': '2025-08-15',
                    'amount': 50000,
                    'is_paid': True
                },
                {
                    'fee_type': 'رسوم الكتب',
                    'due_date': '2025-08-20',
                    'amount': 75000,
                    'is_paid': True
                }
            ],
            'total_amount': 125000,
            'payment_date': '2025-08-15',
            'receipt_number': 'FEES-TEST-20250815'
        }
        
        print_additional_fees_safe(sample_data)
        return True
        
    except Exception as e:
        logging.error(f"خطأ في اختبار طباعة الرسوم الإضافية: {e}")
        return False

def test_students_list_print():
    """اختبار طباعة قائمة الطلاب"""
    try:
        from core.printing.print_manager import print_students_list
        
        sample_students = [
            {
                'id': 1,
                'name': 'أحمد محمد علي',
                'school_name': 'مدرسة الأمل',
                'grade': 'الأول',
                'section': 'أ',
                'gender': 'ذكر',
                'status': 'نشط',
                'total_fee': '1,000,000 د.ع',
                'total_paid': '500,000 د.ع',
                'remaining': '500,000 د.ع'
            },
            {
                'id': 2,
                'name': 'فاطمة أحمد محمد',
                'school_name': 'مدرسة الأمل',
                'grade': 'الثاني',
                'section': 'ب',
                'gender': 'أنثى',
                'status': 'نشط',
                'total_fee': '1,200,000 د.ع',
                'total_paid': '800,000 د.ع',
                'remaining': '400,000 د.ع'
            }
        ]
        
        print_students_list(sample_students, "اختبار الطباعة")
        return True
        
    except Exception as e:
        logging.error(f"خطأ في اختبار طباعة قائمة الطلاب: {e}")
        return False

class PrintTestWindow(QMainWindow):
    """نافذة اختبار الطباعة"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار إصلاحات الطباعة")
        self.setGeometry(200, 200, 500, 400)
        
        # إعداد واجهة المستخدم
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # معلومات الاختبار
        info_text = QTextEdit()
        info_text.setMaximumHeight(100)
        info_text.setPlainText("""
اختبار إصلاحات الطباعة:
✅ طباعة إيصال القسط - تم الإصلاح
✅ طباعة قائمة الطلاب - تم الإصلاح
✅ طباعة الرسوم الإضافية - تم الإصلاح والتحديث
        """)
        layout.addWidget(info_text)
        
        # أزرار الاختبار
        test_installment_btn = QPushButton("اختبار طباعة إيصال القسط")
        test_installment_btn.clicked.connect(self.test_installment)
        layout.addWidget(test_installment_btn)
        
        test_fees_btn = QPushButton("اختبار طباعة الرسوم الإضافية")
        test_fees_btn.clicked.connect(self.test_additional_fees)
        layout.addWidget(test_fees_btn)
        
        test_students_btn = QPushButton("اختبار طباعة قائمة الطلاب")
        test_students_btn.clicked.connect(self.test_students_list)
        layout.addWidget(test_students_btn)
        
        # زر اختبار شامل
        test_all_btn = QPushButton("اختبار شامل لجميع أنواع الطباعة")
        test_all_btn.setStyleSheet("background-color: #007BFF; color: white; padding: 10px; font-weight: bold;")
        test_all_btn.clicked.connect(self.test_all)
        layout.addWidget(test_all_btn)
        
    def test_installment(self):
        """اختبار طباعة إيصال القسط"""
        try:
            if test_installment_print():
                QMessageBox.information(self, "نجح", "اختبار طباعة إيصال القسط نجح!")
            else:
                QMessageBox.warning(self, "فشل", "فشل في اختبار طباعة إيصال القسط")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في الاختبار: {str(e)}")
    
    def test_additional_fees(self):
        """اختبار طباعة الرسوم الإضافية"""
        try:
            if test_additional_fees_print():
                QMessageBox.information(self, "نجح", "اختبار طباعة الرسوم الإضافية نجح!")
            else:
                QMessageBox.warning(self, "فشل", "فشل في اختبار طباعة الرسوم الإضافية")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في الاختبار: {str(e)}")
    
    def test_students_list(self):
        """اختبار طباعة قائمة الطلاب"""
        try:
            if test_students_list_print():
                QMessageBox.information(self, "نجح", "اختبار طباعة قائمة الطلاب نجح!")
            else:
                QMessageBox.warning(self, "فشل", "فشل في اختبار طباعة قائمة الطلاب")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في الاختبار: {str(e)}")
    
    def test_all(self):
        """اختبار شامل"""
        results = []
        
        # اختبار طباعة إيصال القسط
        try:
            if test_installment_print():
                results.append("✅ طباعة إيصال القسط: نجح")
            else:
                results.append("❌ طباعة إيصال القسط: فشل")
        except Exception as e:
            results.append(f"❌ طباعة إيصال القسط: خطأ - {str(e)}")
        
        # اختبار طباعة الرسوم الإضافية
        try:
            if test_additional_fees_print():
                results.append("✅ طباعة الرسوم الإضافية: نجح")
            else:
                results.append("❌ طباعة الرسوم الإضافية: فشل")
        except Exception as e:
            results.append(f"❌ طباعة الرسوم الإضافية: خطأ - {str(e)}")
        
        # اختبار طباعة قائمة الطلاب
        try:
            if test_students_list_print():
                results.append("✅ طباعة قائمة الطلاب: نجح")
            else:
                results.append("❌ طباعة قائمة الطلاب: فشل")
        except Exception as e:
            results.append(f"❌ طباعة قائمة الطلاب: خطأ - {str(e)}")
        
        # عرض النتائج
        results_text = "\n".join(results)
        QMessageBox.information(self, "نتائج الاختبار الشامل", results_text)

def main():
    """دالة الاختبار الرئيسية"""
    app = QApplication(sys.argv)
    
    # إعداد خصائص التطبيق للطباعة الآمنة
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings, True)
    
    window = PrintTestWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
