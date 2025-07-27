# -*- coding: utf-8 -*-
"""
أدوات مساعدة للطباعة
"""

from PyQt5.QtWidgets import QAction, QMessageBox
from .print_manager import PrintManager
from .print_config import TemplateType

def apply_print_styles(widget):
    """تطبيق أنماط الطباعة على الويدجت"""
    widget.setStyleSheet("""
        QPushButton#printButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 14px;
            border-radius: 5px;
        }
        QPushButton#printButton:hover {
            background-color: #45a049;
        }
    """)

class PrintHelper:
    """مساعد الطباعة"""
    def __init__(self, parent, template_type: TemplateType, data_provider_func):
        self.parent = parent
        self.template_type = template_type
        self.data_provider_func = data_provider_func
        self.print_manager = PrintManager(parent)


    @staticmethod
    def format_students_list_for_print(students):
        """تنسيق قائمة الطلاب للطباعة"""
        return [
            {
                'id': s['id'],
                'name': s['name'],
                'school_name': s['school_name'],
                'grade': s['grade'],
                'section': s['section'],
                'gender': s['gender'],
                'status': s['status'],
                'total_fee': s['total_fee']
            } for s in students
        ]

    @staticmethod
    def format_student_data_for_print(student):
        """تنسيق بيانات طالب واحد للطباعة"""
        return {'student': student}

    @staticmethod
    def create_filter_info_string(filters):
        """إنشاء سلسلة معلومات الفلاتر"""
        filter_parts = []
        for key, value in filters.items():
            if value and value not in ["جميع المدارس", "جميع الصفوف", "جميع الحالات", "جميع الطلاب"]:
                filter_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        return " | ".join(filter_parts) if filter_parts else "لا توجد فلاتر"

    def print_action(self):
        """إجراء الطباعة"""
        data = self.data_provider_func()
        if not data:
            QMessageBox.warning(self.parent, "خطأ", "لا توجد بيانات للطباعة")
            return
        self.print_manager.print_document(self.template_type, data)

    def preview_action(self):
        """إجراء المعاينة"""
        data = self.data_provider_func()
        if not data:
            QMessageBox.warning(self.parent, "خطأ", "لا توجد بيانات للمعاينة")
            return
        self.print_manager.preview_document(self.template_type, data)

class QuickPrintMixin:
    """Mixin لإضافة وظائف الطباعة السريعة إلى الصفحات"""
    def setup_printing(self, template_type: TemplateType, data_provider_func):
        self.print_helper = PrintHelper(self, template_type, data_provider_func)
        
        print_action = QAction("طباعة", self)
        print_action.triggered.connect(self.print_helper.print_action)
        
        preview_action = QAction("معاينة", self)
        preview_action.triggered.connect(self.print_helper.preview_action)
        
        # يجب إضافة هذه الإجراءات إلى قائمة أو شريط أدوات في الواجهة
        self.addAction(print_action)
        self.addAction(preview_action)
