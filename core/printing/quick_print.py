# -*- coding: utf-8 -*-
"""
واجهة سريعة لاستخدام نظام الطباعة المزدوج
"""

from core.printing.print_manager import PrintManager, print_installment_receipt
from core.printing.print_config import TemplateType


class QuickPrintInterface:
    """واجهة سريعة للطباعة"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.print_manager = PrintManager(parent)
    
    def print_installment_receipt_simple(self, student_name: str, amount: float, 
                                       installment_number: int, school_name: str = "المدرسة"):
        """طباعة إيصال قسط بطريقة مبسطة"""
        from datetime import datetime
        
        data = {
            'student_name': student_name,
            'amount': amount,
            'payment_date': datetime.now().strftime('%Y-%m-%d'),
            'installment_number': installment_number,
            'school_name': school_name,
            'receipt_number': f'R{datetime.now().strftime("%Y%m%d%H%M%S")}'
        }
        
        return print_installment_receipt(data, self.parent)
    
    def print_student_details(self, student_data: dict):
        """طباعة تفاصيل طالب (HTML)"""
        self.print_manager.preview_document(TemplateType.STUDENT_REPORT, student_data)
    
    def print_students_list(self, students_list: list, title: str = "قائمة الطلاب"):
        """طباعة قائمة طلاب (HTML)"""
        data = {
            'students': students_list,
            'title': title
        }
        self.print_manager.preview_document(TemplateType.STUDENT_LIST, data)
    
    def print_financial_report(self, report_data: dict):
        """طباعة تقرير مالي (HTML)"""
        self.print_manager.preview_document(TemplateType.FINANCIAL_REPORT, report_data)


# دوال سريعة للاستخدام المباشر
def quick_print_installment(student_name: str, amount: float, installment_number: int, 
                           school_name: str = "المدرسة", parent=None):
    """طباعة سريعة لإيصال قسط"""
    interface = QuickPrintInterface(parent)
    return interface.print_installment_receipt_simple(
        student_name, amount, installment_number, school_name
    )


def quick_print_student_report(student_data: dict, parent=None):
    """طباعة سريعة لتقرير طالب"""
    interface = QuickPrintInterface(parent)
    return interface.print_student_details(student_data)


# مثال للاستخدام
if __name__ == "__main__":
    # مثال طباعة إيصال قسط
    quick_print_installment(
        student_name="محمد أحمد علي",
        amount=200000,
        installment_number=4,
        school_name="مدرسة النجاح الأهلية"
    )
    
    # مثال طباعة تقرير طالب
    student_example = {
        'student': {
            'name': 'سارة محمود',
            'class': 'الصف الخامس',
            'grades': [
                {'subject': 'الرياضيات', 'grade': 90},
                {'subject': 'العلوم', 'grade': 85}
            ]
        }
    }
    quick_print_student_report(student_example)
