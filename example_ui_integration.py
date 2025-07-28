# -*- coding: utf-8 -*-
"""
مثال على كيفية استخدام نظام الطباعة المزدوج في واجهات المستخدم
"""

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QWidget, QPushButton, QLabel, QLineEdit, QSpinBox, 
                           QTextEdit, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt
import sys

# استيراد نظام الطباعة
from core.printing import (
    quick_print_installment,
    quick_print_student_report,
    print_students_list,
    TemplateType,
    QuickPrintInterface
)


class PrintingTestWindow(QMainWindow):
    """نافذة تجريبية لاختبار نظام الطباعة"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.print_interface = QuickPrintInterface(self)
    
    def init_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("اختبار نظام الطباعة المزدوج")
        self.setGeometry(100, 100, 600, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # مجموعة إيصالات الأقساط (ReportLab)
        installment_group = QGroupBox("طباعة إيصال قسط (ReportLab)")
        installment_layout = QVBoxLayout(installment_group)
        
        # حقول الإدخال للإيصال
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("اسم الطالب:"))
        self.student_name_edit = QLineEdit("أحمد محمد علي")
        name_layout.addWidget(self.student_name_edit)
        installment_layout.addLayout(name_layout)
        
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("المبلغ:"))
        self.amount_spin = QSpinBox()
        self.amount_spin.setRange(1000, 10000000)
        self.amount_spin.setValue(250000)
        amount_layout.addWidget(self.amount_spin)
        installment_layout.addLayout(amount_layout)
        
        installment_layout.addWidget(QLabel("رقم القسط:"))
        self.installment_number_spin = QSpinBox()
        self.installment_number_spin.setRange(1, 12)
        self.installment_number_spin.setValue(3)
        installment_layout.addWidget(self.installment_number_spin)
        
        school_layout = QHBoxLayout()
        school_layout.addWidget(QLabel("اسم المدرسة:"))
        self.school_name_edit = QLineEdit("مدرسة النور الأهلية")
        school_layout.addWidget(self.school_name_edit)
        installment_layout.addLayout(school_layout)
        
        print_installment_btn = QPushButton("طباعة إيصال القسط")
        print_installment_btn.clicked.connect(self.print_installment)
        installment_layout.addWidget(print_installment_btn)
        
        layout.addWidget(installment_group)
        
        # مجموعة التقارير (HTML)
        reports_group = QGroupBox("طباعة التقارير (HTML)")
        reports_layout = QVBoxLayout(reports_group)
        
        student_report_btn = QPushButton("طباعة تقرير طالب")
        student_report_btn.clicked.connect(self.print_student_report)
        reports_layout.addWidget(student_report_btn)
        
        students_list_btn = QPushButton("طباعة قائمة طلاب")
        students_list_btn.clicked.connect(self.print_students_list)
        reports_layout.addWidget(students_list_btn)
        
        layout.addWidget(reports_group)
        
        # منطقة معلومات
        info_label = QLabel(
            "📋 هذا المثال يوضح استخدام نظام الطباعة المزدوج:\n"
            "• إيصالات الأقساط تستخدم ReportLab (دقيقة ومضبوطة)\n"
            "• التقارير تستخدم HTML (مرنة وسهلة)"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("background-color: #f0f8ff; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(info_label)
    
    def print_installment(self):
        """طباعة إيصال قسط"""
        try:
            student_name = self.student_name_edit.text()
            amount = self.amount_spin.value()
            installment_number = self.installment_number_spin.value()
            school_name = self.school_name_edit.text()
            
            if not student_name.strip():
                QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم الطالب")
                return
            
            # استخدام الدالة السريعة
            quick_print_installment(
                student_name=student_name,
                amount=amount,
                installment_number=installment_number,
                school_name=school_name,
                parent=self
            )
            
            QMessageBox.information(self, "نجح", "تم إنشاء إيصال القسط بنجاح!")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في طباعة الإيصال:\n{e}")
    
    def print_student_report(self):
        """طباعة تقرير طالب"""
        try:
            sample_student_data = {
                'student': {
                    'name': 'فاطمة عبد الله',
                    'class': 'الصف السادس الابتدائي',
                    'student_id': '2023001',
                    'grades': [
                        {'subject': 'الرياضيات', 'grade': 85, 'max_grade': 100},
                        {'subject': 'العلوم', 'grade': 92, 'max_grade': 100},
                        {'subject': 'اللغة العربية', 'grade': 88, 'max_grade': 100},
                        {'subject': 'التاريخ', 'grade': 90, 'max_grade': 100}
                    ],
                    'total_average': 88.75,
                    'rank': 5,
                    'attendance': '95%'
                },
                'school': {
                    'name': 'مدرسة النور الأهلية',
                    'academic_year': '2024-2025'
                }
            }
            
            quick_print_student_report(sample_student_data, self)
            QMessageBox.information(self, "نجح", "تم فتح معاينة تقرير الطالب!")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في طباعة التقرير:\n{e}")
    
    def print_students_list(self):
        """طباعة قائمة طلاب"""
        try:
            sample_students = [
                {'name': 'أحمد محمد علي', 'class': 'السادس الابتدائي', 'student_id': '2023001'},
                {'name': 'فاطمة عبد الله', 'class': 'السادس الابتدائي', 'student_id': '2023002'},
                {'name': 'محمد حسن', 'class': 'السادس الابتدائي', 'student_id': '2023003'},
                {'name': 'زينب أحمد', 'class': 'السادس الابتدائي', 'student_id': '2023004'},
                {'name': 'عبد الرحمن سالم', 'class': 'السادس الابتدائي', 'student_id': '2023005'}
            ]
            
            self.print_interface.print_students_list(sample_students, "قائمة طلاب الصف السادس")
            QMessageBox.information(self, "نجح", "تم فتح معاينة قائمة الطلاب!")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في طباعة القائمة:\n{e}")


def main():
    """تشغيل التطبيق التجريبي"""
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)  # دعم العربية
    
    window = PrintingTestWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
