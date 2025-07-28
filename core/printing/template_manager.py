#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير قوالب الطباعة
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from jinja2 import Template, Environment, FileSystemLoader, TemplateNotFound
from datetime import datetime

from .print_config import TemplateType, PrintConfig


class TemplateManager:
    """مدير قوالب الطباعة"""
    
    def __init__(self):
        self.config = PrintConfig()
        self.templates_path = self.config.templates_path
        
        # إعداد Jinja2 environment
        # The loader now points to the single, centralized templates directory
        self.env = Environment(
            loader=FileSystemLoader(self.templates_path),
            autoescape=True
        )
        
        # إضافة فلاتر مخصصة
        self.env.filters['currency'] = self.format_currency
        self.env.filters['date_ar'] = self.format_date_arabic
        self.env.filters['arabic_date'] = self.arabic_date
        
        # إنشاء القوالب الأساسية إذا لم تكن موجودة (تعطيل لمنع الكتابة فوق القوالب اليدوية)
        # إنشاء القوالب الأساسية إذا لم تكن موجودة
        self.create_default_templates()
    
    def format_currency(self, value: float) -> str:
        """تنسيق العملة بدون أصفار زائدة"""
        # إذا كانت القيمة None، عرض صفر بدون كسور
        if value is None:
            return "0 دينار"
        # تنسيق الرقم بدقة منزلتين عشريتين ثم إزالة الأصفار الزائدة
        s = f"{value:,.2f}"
        if '.' in s:
            s = s.rstrip('0').rstrip('.')
        return f"{s} دينار"
    
    def format_date_arabic(self, date_obj) -> str:
        """تنسيق التاريخ باللغة العربية"""
        if date_obj is None:
            return ""
        
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
            except:
                return date_obj
        
        months = [
            "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
            "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
        ]
        
        return f"{date_obj.day} {months[date_obj.month - 1]} {date_obj.year}"
    
    def arabic_date(self, date_str: str) -> str:
        """تحويل التاريخ إلى العربية - دالة مساعدة للاختبارات"""
        return self.format_date_arabic(date_str)
    
    def get_template(self, template_type: TemplateType) -> Optional[Template]:
        """الحصول على قالب"""
        # support both singular and plural alias for student list
        name = template_type.value
        if template_type.name == 'STUDENTS_LIST':
            name = TemplateType.STUDENT_LIST.value
        template_file = f"{name}.html"
        try:
            return self.env.get_template(template_file)
        except TemplateNotFound:
            # Generate default templates and retry
            logging.warning(f"القالب {template_file} غير موجود، سيتم إنشاؤه افتراضياً")
            self.create_default_templates()
            try:
                return self.env.get_template(template_file)
            except Exception as e:
                logging.error(f"فشل تحميل القالب بعد الإنشاء {template_type.value}: {e}")
                return None
        except Exception as e:
            logging.error(f"خطأ في تحميل القالب {template_type.value}: {e}")
            return None
    
    def render_template(self, template_type: TemplateType, data: Dict[str, Any]) -> str:
        """تقديم القالب مع البيانات"""
        try:
            template = self.get_template(template_type)
            if not template:
                return self.get_error_template()
            
            # إضافة البيانات العامة
            common_data = self.get_common_template_data()
            data.update(common_data)
            
            return template.render(**data)
            
        except Exception as e:
            logging.error(f"خطأ في تقديم القالب {template_type.value}: {e}")
            return self.get_error_template()
    
    def get_common_template_data(self) -> Dict[str, Any]:
        """البيانات المشتركة لجميع القوالب"""
        from datetime import datetime
        now = datetime.now()
        
        current_date = now.strftime('%Y-%m-%d')
        # Remove hardcoded school and company names to allow dynamic values
        return {
            'system_version': '1.0',  # application version
            'current_date': current_date,
            'current_time': now.strftime('%H:%M'),
            'print_date': current_date,
            'printed_by': 'نظام إدارة المدارس',
            'page_title': 'تقرير مدرسي'
        }
    
    def get_error_template(self) -> str:
        """قالب الخطأ"""
        return """
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>خطأ في الطباعة</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; }
                .error { color: red; font-size: 18px; }
            </style>
        </head>
        <body>
            <div class="error">
                <h2>خطأ في تحميل قالب الطباعة</h2>
                <p>يرجى التحقق من إعدادات النظام</p>
            </div>
        </body>
        </html>
        """
    
    def create_default_templates(self):
        """إنشاء القوالب الافتراضية"""
        templates = {
            TemplateType.STUDENT_REPORT: self.get_student_report_template(),
            TemplateType.STUDENT_LIST: self.get_student_list_template(),
            TemplateType.FINANCIAL_REPORT: self.get_financial_report_template(),
            TemplateType.PAYMENT_RECEIPT: self.get_payment_receipt_template(),
            TemplateType.SALARY_SLIP: self.get_salary_slip_template(),
            TemplateType.STAFF_REPORT: self.get_staff_report_template(),
            TemplateType.SCHOOL_REPORT: self.get_school_report_template()
        }
        
        for template_type, content in templates.items():
            template_path = self.config.get_template_path(template_type)
            if not os.path.exists(template_path):
                try:
                    with open(template_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                except Exception as e:
                    logging.error(f"خطأ في إنشاء القالب {template_type.value}: {e}")
    
    def get_student_report_template(self) -> str:
        """قالب تقرير الطالب"""
        return """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تقرير الطالب</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            direction: rtl;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .student-info {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ company_name }}</h1>
        <h2>تقرير الطالب</h2>
        <p>تاريخ الطباعة: {{ print_date | date_ar }}</p>
    </div>
    
    <div class="student-info">
        <h3>بيانات الطالب</h3>
        <div class="info-row">
            <strong>الاسم:</strong> {{ student.name }}
        </div>
        <div class="info-row">
            <strong>المدرسة:</strong> {{ student.school_name }}
        </div>
        <div class="info-row">
            <strong>الصف:</strong> {{ student.grade }}
        </div>
        <div class="info-row">
            <strong>الشعبة:</strong> {{ student.section }}
        </div>
        <div class="info-row">
            <strong>الجنس:</strong> {{ student.gender }}
        </div>
        <div class="info-row">
            <strong>الهاتف:</strong> {{ student.phone }}
        </div>
        <div class="info-row">
            <strong>الحالة:</strong> {{ student.status }}
        </div>
        <div class="info-row">
            <strong>الرسوم الدراسية:</strong> {{ student.total_fee | currency }}
        </div>
    </div>
    
    <div class="footer">
        <p>{{ company_name }} - {{ system_version }}</p>
    </div>
</body>
</html>
        """
    
    def get_student_list_template(self) -> str:
        """قالب قائمة الطلاب"""
        return """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>قائمة الطلاب</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            direction: rtl;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #666;
        }
        .summary {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ company_name }}</h1>
        <h2>قائمة الطلاب</h2>
        <p>تاريخ الطباعة: {{ print_date | date_ar }}</p>
    </div>
    
    <div class="summary">
        <p><strong>إجمالي الطلاب:</strong> {{ students|length }}</p>
        {% if filter_info %}
        <p><strong>الفلاتر المطبقة:</strong> {{ filter_info }}</p>
        {% endif %}
    </div>
    
    <table>
        <thead>
            <tr>
                <th>المعرف</th>
                <th>الاسم</th>
                <th>المدرسة</th>
                <th>الصف</th>
                <th>الشعبة</th>
                <th>الجنس</th>
                <th>الحالة</th>
                <th>الرسوم</th>
            </tr>
        </thead>
        <tbody>
            {% for student in students %}
            <tr>
                <td>{{ student.id }}</td>
                <td>{{ student.name }}</td>
                <td>{{ student.school_name }}</td>
                <td>{{ student.grade }}</td>
                <td>{{ student.section }}</td>
                <td>{{ student.gender }}</td>
                <td>{{ student.status }}</td>
                <td>{{ student.total_fee | currency }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <div class="footer">
        <p>{{ company_name }} - {{ system_version }}</p>
    </div>
</body>
</html>
        """
    
    def get_financial_report_template(self) -> str:
        """قالب التقرير المالي"""
        return """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>التقرير المالي</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            direction: rtl;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .summary-box {
            background-color: #e8f5e8;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .summary-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 16px;
        }
        .total {
            font-weight: bold;
            font-size: 18px;
            border-top: 2px solid #333;
            padding-top: 10px;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ company_name }}</h1>
        <h2>التقرير المالي</h2>
        <p>تاريخ الطباعة: {{ print_date | date_ar }}</p>
        {% if date_range %}
        <p>الفترة: {{ date_range }}</p>
        {% endif %}
    </div>
    
    <div class="summary-box">
        <h3>ملخص مالي</h3>
        <div class="summary-item">
            <span>إجمالي الإيرادات:</span>
            <span>{{ financial_data.total_income | currency }}</span>
        </div>
        <div class="summary-item">
            <span>إجمالي المصروفات:</span>
            <span>{{ financial_data.total_expenses | currency }}</span>
        </div>
        <div class="summary-item total">
            <span>صافي الربح:</span>
            <span>{{ (financial_data.total_income - financial_data.total_expenses) | currency }}</span>
        </div>
    </div>
    
    <div class="footer">
        <p>{{ company_name }} - {{ system_version }}</p>
    </div>
</body>
</html>
        """
    
    def get_payment_receipt_template(self) -> str:
        """قالب إيصال الدفع"""
        return """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>إيصال دفع</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            direction: rtl;
            font-size: 14px;
        }
        .receipt {
            border: 2px solid #333;
            padding: 20px;
            max-width: 600px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            border-bottom: 1px solid #333;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        .receipt-info {
            margin-bottom: 20px;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 5px 0;
        }
        .amount-box {
            background-color: #f0f0f0;
            padding: 15px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            border: 1px solid #ddd;
            margin: 20px 0;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="receipt">
        <div class="header">
            <h2>{{ company_name }}</h2>
            <h3>إيصال دفع</h3>
            <p>رقم الإيصال: {{ receipt.id }}</p>
        </div>
        
        <div class="receipt-info">
            <div class="info-row">
                <strong>اسم الطالب:</strong>
                <span>{{ receipt.student_name }}</span>
            </div>
            <div class="info-row">
                <strong>المدرسة:</strong>
                <span>{{ receipt.school_name }}</span>
            </div>
            <div class="info-row">
                <strong>تاريخ الدفع:</strong>
                <span>{{ receipt.payment_date | date_ar }}</span>
            </div>
            <div class="info-row">
                <strong>طريقة الدفع:</strong>
                <span>{{ receipt.payment_method }}</span>
            </div>
            <div class="info-row">
                <strong>الوصف:</strong>
                <span>{{ receipt.description }}</span>
            </div>
        </div>
        
        <div class="amount-box">
            المبلغ المدفوع: {{ receipt.amount | currency }}
        </div>
        
        <div class="footer">
            <p>تاريخ الطباعة: {{ print_date | date_ar }}</p>
            <p>{{ company_name }} - نشكركم لثقتكم</p>
        </div>
    </div>
</body>
</html>
        """
    
    def get_salary_slip_template(self) -> str:
        """قالب قسيمة الراتب"""
        return """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>قسيمة راتب</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            direction: rtl;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .employee-info, .salary-details {
            background-color: #f9f9f9;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        .total-row {
            border-top: 2px solid #333;
            padding-top: 10px;
            font-weight: bold;
            font-size: 16px;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ company_name }}</h1>
        <h2>قسيمة راتب</h2>
        <p>الشهر: {{ salary.month_year }}</p>
    </div>
    
    <div class="employee-info">
        <h3>بيانات الموظف</h3>
        <div class="info-row">
            <strong>الاسم:</strong> {{ salary.employee_name }}
        </div>
        <div class="info-row">
            <strong>الوظيفة:</strong> {{ salary.position }}
        </div>
        <div class="info-row">
            <strong>القسم:</strong> {{ salary.department }}
        </div>
    </div>
    
    <div class="salary-details">
        <h3>تفاصيل الراتب</h3>
        <div class="info-row">
            <span>الراتب الأساسي:</span>
            <span>{{ salary.basic_salary | currency }}</span>
        </div>
        <div class="info-row">
            <span>البدلات:</span>
            <span>{{ salary.allowances | currency }}</span>
        </div>
        <div class="info-row">
            <span>الخصومات:</span>
            <span>{{ salary.deductions | currency }}</span>
        </div>
        <div class="info-row total-row">
            <span>صافي الراتب:</span>
            <span>{{ salary.net_salary | currency }}</span>
        </div>
    </div>
    
    <div class="footer">
        <p>تاريخ الطباعة: {{ print_date | date_ar }}</p>
        <p>{{ company_name }}</p>
    </div>
</body>
</html>
        """
    
    def get_staff_report_template(self) -> str:
        """قالب تقرير الموظفين"""
        return """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تقرير الموظفين</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            direction: rtl;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .summary {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ company_name }}</h1>
        <h2>تقرير الموظفين</h2>
        <p>تاريخ الطباعة: {{ print_date | date_ar }}</p>
    </div>
    
    <div class="summary">
        <p><strong>إجمالي الموظفين:</strong> {{ staff|length }}</p>
    </div>
    
    <table>
        <thead>
            <tr>
                <th>المعرف</th>
                <th>الاسم</th>
                <th>الوظيفة</th>
                <th>القسم</th>
                <th>الهاتف</th>
                <th>الراتب</th>
                <th>تاريخ التوظيف</th>
            </tr>
        </thead>
        <tbody>
            {% for employee in staff %}
            <tr>
                <td>{{ employee.id }}</td>
                <td>{{ employee.name }}</td>
                <td>{{ employee.position }}</td>
                <td>{{ employee.department }}</td>
                <td>{{ employee.phone }}</td>
                <td>{{ employee.salary | currency }}</td>
                <td>{{ employee.hire_date | date_ar }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <div class="footer">
        <p>{{ company_name }} - {{ system_version }}</p>
    </div>
</body>
</html>
        """
    
    def get_school_report_template(self) -> str:
        """قالب تقرير المدرسة"""
        return """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تقرير المدرسة</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            direction: rtl;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .school-info {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-box {
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ company_name }}</h1>
        <h2>تقرير المدرسة</h2>
        <p>تاريخ الطباعة: {{ print_date | date_ar }}</p>
    </div>
    
    <div class="school-info">
        <h3>{{ school.name }}</h3>
        <p><strong>العنوان:</strong> {{ school.address }}</p>
        <p><strong>الهاتف:</strong> {{ school.phone }}</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-box">
            <h4>إجمالي الطلاب</h4>
            <h2>{{ stats.total_students }}</h2>
        </div>
        <div class="stat-box">
            <h4>إجمالي الموظفين</h4>
            <h2>{{ stats.total_staff }}</h2>
        </div>
        <div class="stat-box">
            <h4>إجمالي الإيرادات</h4>
            <h2>{{ stats.total_revenue | currency }}</h2>
        </div>
        <div class="stat-box">
            <h4>إجمالي المصروفات</h4>
            <h2>{{ stats.total_expenses | currency }}</h2>
        </div>
    </div>
    
    <div class="footer">
        <p>{{ company_name }} - {{ system_version }}</p>
    </div>
</body>
</html>
        """
