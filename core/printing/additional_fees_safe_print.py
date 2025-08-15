# -*- coding: utf-8 -*-
"""
مدير طباعة آمن للرسوم الإضافية
"""

import logging
import os
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox
from core.printing.safe_print_manager import SafePrintManager
from core.printing.template_manager import TemplateManager
from core.utils.logger import log_user_action

def print_additional_fees_safe(receipt_data, parent=None):
    """طباعة آمنة لإيصال الرسوم الإضافية"""
    try:
        log_user_action("طباعة إيصال الرسوم الإضافية")
        
        # إنشاء HTML للإيصال
        html_content = generate_additional_fees_html(receipt_data)
        
        if not html_content:
            QMessageBox.warning(parent, "خطأ", "فشل في إنشاء محتوى الإيصال")
            return False
        
        # استخدام النظام الآمن للطباعة
        from core.printing.simple_print_preview import SimplePrintPreviewDialog
        
        preview_dialog = SimplePrintPreviewDialog(html_content, parent)
        preview_dialog.setWindowTitle("طباعة إيصال الرسوم الإضافية")
        preview_dialog.exec_()
        
        return True
        
    except Exception as e:
        logging.error(f"خطأ في طباعة الرسوم الإضافية الآمنة: {e}")
        if parent:
            QMessageBox.critical(parent, "خطأ", f"فشل في الطباعة: {str(e)}")
        return False

def generate_additional_fees_html(receipt_data):
    """إنشاء HTML لإيصال الرسوم الإضافية"""
    try:
        # استخراج البيانات
        school_name = receipt_data.get('school_name', 'المدرسة')
        school_address = receipt_data.get('school_address', '')
        school_phone = receipt_data.get('school_phone', '')
        student_name = receipt_data.get('student_name', '')
        grade = receipt_data.get('grade', '')
        section = receipt_data.get('section', '')
        total_amount = receipt_data.get('total_amount', 0)
        fees_list = receipt_data.get('fees_list', [])
        payment_date = receipt_data.get('payment_date', datetime.now().strftime('%Y-%m-%d'))
        receipt_number = receipt_data.get('receipt_number', f"FEES-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # بناء HTML
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>إيصال رسوم إضافية</title>
            <style>
                body {{
                    font-family: 'Cairo', 'Arial', sans-serif;
                    margin: 20px;
                    direction: rtl;
                    font-size: 14px;
                    line-height: 1.6;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #007BFF;
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                .school-name {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #007BFF;
                    margin-bottom: 5px;
                }}
                .school-info {{
                    font-size: 12px;
                    color: #666;
                }}
                .receipt-title {{
                    font-size: 20px;
                    font-weight: bold;
                    text-align: center;
                    background-color: #f8f9fa;
                    padding: 10px;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .info-section {{
                    display: flex;
                    justify-content: space-between;
                    margin: 20px 0;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                }}
                .info-group {{
                    flex: 1;
                }}
                .info-label {{
                    font-weight: bold;
                    color: #495057;
                }}
                .info-value {{
                    color: #212529;
                    margin-bottom: 10px;
                }}
                .fees-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    border: 1px solid #dee2e6;
                }}
                .fees-table th,
                .fees-table td {{
                    border: 1px solid #dee2e6;
                    padding: 12px;
                    text-align: center;
                }}
                .fees-table th {{
                    background-color: #007BFF;
                    color: white;
                    font-weight: bold;
                }}
                .fees-table tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                .total-section {{
                    text-align: left;
                    margin: 20px 0;
                    padding: 15px;
                    background-color: #e8f5e8;
                    border: 2px solid #28a745;
                    border-radius: 5px;
                }}
                .total-amount {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #28a745;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    border-top: 1px solid #dee2e6;
                    padding-top: 15px;
                }}
                .receipt-number {{
                    font-size: 12px;
                    color: #666;
                    text-align: left;
                }}
                @media print {{
                    body {{
                        margin: 0;
                        font-size: 12px;
                    }}
                    .info-section {{
                        display: block;
                    }}
                    .info-group {{
                        margin-bottom: 10px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="school-name">{school_name}</div>
                <div class="school-info">
                    {school_address}<br>
                    {school_phone}
                </div>
            </div>
            
            <div class="receipt-number">رقم الإيصال: {receipt_number}</div>
            
            <div class="receipt-title">إيصال رسوم إضافية</div>
            
            <div class="info-section">
                <div class="info-group">
                    <div class="info-label">اسم الطالب:</div>
                    <div class="info-value">{student_name}</div>
                    <div class="info-label">الصف:</div>
                    <div class="info-value">{grade}</div>
                </div>
                <div class="info-group">
                    <div class="info-label">الشعبة:</div>
                    <div class="info-value">{section}</div>
                    <div class="info-label">تاريخ الدفع:</div>
                    <div class="info-value">{payment_date}</div>
                </div>
            </div>
            
            <table class="fees-table">
                <thead>
                    <tr>
                        <th>نوع الرسوم</th>
                        <th>تاريخ الاستحقاق</th>
                        <th>المبلغ</th>
                        <th>الحالة</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # إضافة صفوف الرسوم
        for fee in fees_list:
            fee_type = fee.get('fee_type', '')
            due_date = fee.get('due_date', '')
            amount = fee.get('amount', 0)
            status = 'مدفوع' if fee.get('is_paid', False) else 'غير مدفوع'
            status_color = '#28a745' if fee.get('is_paid', False) else '#dc3545'
            
            html_content += f"""
                    <tr>
                        <td>{fee_type}</td>
                        <td>{due_date}</td>
                        <td>{amount:,.0f} د.ع</td>
                        <td style="color: {status_color}; font-weight: bold;">{status}</td>
                    </tr>
            """
        
        # إنهاء HTML
        html_content += f"""
                </tbody>
            </table>
            
            <div class="total-section">
                <div class="total-amount">المجموع الكلي: {total_amount:,.0f} دينار عراقي</div>
            </div>
            
            <div class="footer">
                <p>تم إصدار هذا الإيصال في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>نظام حسابات المدارس الأهلية</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        logging.error(f"خطأ في إنشاء HTML للرسوم الإضافية: {e}")
        return None
