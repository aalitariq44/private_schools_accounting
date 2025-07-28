# -*- coding: utf-8 -*-
"""
مدير طباعة ReportLab للوصولات والفواتير
يوفر طباعة دقيقة مع دعم كامل للعربية (RTL + تشكيل الأحرف)
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# ReportLab imports
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import Color, black, blue, red, green
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import KeepTogether

# Arabic text support
try:
    import arabic_reshaper
    import bidi.algorithm
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    logging.warning("مكتبات دعم العربية غير متوفرة. سيتم استخدام النص العادي.")

# Font support
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import config


class ReportLabPrintManager:
    """مدير طباعة ReportLab للوصولات والفواتير"""
    
    def __init__(self):
        self.setup_fonts()
        self.page_width, self.page_height = A4
        self.margin = 10 * mm  # reduced margins to 10mm for tighter layout
        self.content_width = self.page_width - (2 * self.margin)
        
    def setup_fonts(self):
        """إعداد الخطوط العربية"""
        try:
            # مسار خط القاهرة
            fonts_dir = Path(config.RESOURCES_DIR) / 'fonts'
            cairo_bold_path = fonts_dir / 'Cairo-Bold.ttf'
            cairo_medium_path = fonts_dir / 'Cairo-Medium.ttf'
            
            if cairo_bold_path.exists():
                pdfmetrics.registerFont(TTFont('Cairo-Bold', str(cairo_bold_path)))
                logging.info("تم تسجيل خط Cairo-Bold بنجاح")
                
            if cairo_medium_path.exists():
                pdfmetrics.registerFont(TTFont('Cairo-Medium', str(cairo_medium_path)))
                logging.info("تم تسجيل خط Cairo-Medium بنجاح")
                
            self.arabic_font = 'Cairo-Medium'
            self.arabic_bold_font = 'Cairo-Bold'
            
        except Exception as e:
            logging.error(f"خطأ في تسجيل الخطوط العربية: {e}")
            self.arabic_font = 'Helvetica'
            self.arabic_bold_font = 'Helvetica-Bold'
    
    def draw_centered_text(self, canvas, text: str, x: float, y: float, font_name: str = None, font_size: int = 12):
        """رسم نص في المركز بدقة"""
        if font_name:
            canvas.setFont(font_name, font_size)
        
        # حساب عرض النص
        text_width = canvas.stringWidth(text, font_name or canvas._fontname, font_size)
        # رسم النص في المركز
        canvas.drawString(x - (text_width / 2), y, text)
    
    def reshape_arabic_text(self, text: str) -> str:
        """إعادة تشكيل النص العربي للعرض الصحيح"""
        if not ARABIC_SUPPORT or not text:
            return text
            
        try:
            # إعادة تشكيل النص العربي
            reshaped_text = arabic_reshaper.reshape(text)
            # تطبيق خوارزمية BiDi
            bidi_text = bidi.algorithm.get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            logging.error(f"خطأ في إعادة تشكيل النص العربي: {e}")
            return text
    
    def create_installment_receipt(self, data: Dict[str, Any], output_path: str = None) -> str:
        """إنشاء إيصال دفع قسط"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                config.DATA_DIR, 'exports', 'prints', 
                f'installment_receipt_{timestamp}.pdf'
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # إنشاء canvas للرسم المباشر
        c = canvas.Canvas(output_path, pagesize=A4)
        
        # معلومات الإيصال
        receipt_data = data.get('receipt', data)
        student_name = receipt_data.get('student_name', 'غير محدد')
        amount = receipt_data.get('amount', 0)
        payment_date = receipt_data.get('payment_date', datetime.now().strftime('%Y-%m-%d'))
        installment_number = receipt_data.get('installment_number', 1)
        school_name = receipt_data.get('school_name', 'المدرسة')
        receipt_number = receipt_data.get('receipt_number', f'R{datetime.now().strftime("%Y%m%d%H%M%S")}')
        
        # رسم الإيصال
        self._draw_receipt_header(c, school_name, receipt_number)
        self._draw_receipt_body(c, student_name, amount, payment_date, installment_number)
        self._draw_receipt_footer(c)
        
        c.save()
        logging.info(f"تم إنشاء إيصال الدفع: {output_path}")
        return output_path
    
    def _draw_receipt_header(self, canvas, school_name: str, receipt_number: str):
        """رسم رأس الإيصال"""
        y_position = self.page_height - self.margin - 30
        
        # إطار الإيصال
        canvas.setStrokeColor(black)
        canvas.setLineWidth(2)
        canvas.rect(self.margin, self.margin, self.content_width, self.page_height - (2 * self.margin))
        
        # عنوان الإيصال
        title = self.reshape_arabic_text("إيصال دفع قسط")
        self.draw_centered_text(canvas, title, self.page_width / 2, y_position, self.arabic_bold_font, 18)
        
        y_position -= 30
        
        # اسم المدرسة
        school_text = self.reshape_arabic_text(school_name)
        self.draw_centered_text(canvas, school_text, self.page_width / 2, y_position, self.arabic_bold_font, 14)
        
        y_position -= 40
        
        # رقم الإيصال
        canvas.setFont(self.arabic_font, 12)
        receipt_text = self.reshape_arabic_text(f"رقم الإيصال: {receipt_number}")
        canvas.drawRightString(self.page_width - self.margin - 10, y_position, receipt_text)
        
        # خط فاصل
        y_position -= 20
        canvas.setLineWidth(1)
        canvas.line(self.margin + 10, y_position, self.page_width - self.margin - 10, y_position)
    
    def _draw_receipt_body(self, canvas, student_name: str, amount: float, payment_date: str, installment_number: int):
        """رسم محتوى الإيصال"""
        y_position = self.page_height - self.margin - 160
        
        canvas.setFont(self.arabic_font, 12)
        line_height = 25
        
        # بيانات الطالب
        student_label = self.reshape_arabic_text("اسم الطالب:")
        student_value = self.reshape_arabic_text(student_name)
        canvas.drawRightString(self.page_width - self.margin - 10, y_position, student_label)
        canvas.drawRightString(self.page_width - self.margin - 100, y_position, student_value)
        
        y_position -= line_height
        
        # رقم القسط
        installment_label = self.reshape_arabic_text("رقم القسط:")
        installment_value = str(installment_number)
        canvas.drawRightString(self.page_width - self.margin - 10, y_position, installment_label)
        canvas.drawRightString(self.page_width - self.margin - 100, y_position, installment_value)
        
        y_position -= line_height
        
        # المبلغ
        amount_label = self.reshape_arabic_text("المبلغ المدفوع:")
        amount_value = f"{amount:,.0f} دينار"
        canvas.drawRightString(self.page_width - self.margin - 10, y_position, amount_label)
        canvas.drawRightString(self.page_width - self.margin - 100, y_position, amount_value)
        
        y_position -= line_height
        
        # تاريخ الدفع
        date_label = self.reshape_arabic_text("تاريخ الدفع:")
        canvas.drawRightString(self.page_width - self.margin - 10, y_position, date_label)
        canvas.drawRightString(self.page_width - self.margin - 100, y_position, payment_date)
        
        # صندوق بيانات القسط
        y_position -= 50
        box_height = 80
        canvas.setStrokeColor(black)
        canvas.setLineWidth(1)
        canvas.rect(self.margin + 20, y_position - box_height, self.content_width - 40, box_height)
        
        # المبلغ بالأرقام والحروف
        y_position -= 20
        amount_digits = f"{amount:,.0f}"
        self.draw_centered_text(canvas, amount_digits, self.page_width / 2, y_position, self.arabic_bold_font, 14)
        
        y_position -= 25
        amount_words = self.reshape_arabic_text(self._number_to_arabic_words(amount))
        self.draw_centered_text(canvas, amount_words, self.page_width / 2, y_position, self.arabic_font, 11)
        
        y_position -= 20
        currency_text = self.reshape_arabic_text("دينار عراقي لا غير")
        self.draw_centered_text(canvas, currency_text, self.page_width / 2, y_position, self.arabic_font, 10)
    
    def _draw_receipt_footer(self, canvas):
        """رسم ذيل الإيصال"""
        y_position = self.margin + 80
        
        # توقيع المحاسب
        canvas.setFont(self.arabic_font, 11)
        signature_label = self.reshape_arabic_text("توقيع المحاسب:")
        canvas.drawRightString(self.page_width - self.margin - 10, y_position, signature_label)
        
        # خط التوقيع
        signature_line_start = self.page_width - self.margin - 150
        signature_line_end = self.page_width - self.margin - 250
        canvas.line(signature_line_end, y_position - 5, signature_line_start, y_position - 5)
        
        # التاريخ والوقت
        y_position -= 30
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        timestamp_text = self.reshape_arabic_text(f"تاريخ الطباعة: {timestamp}")
        canvas.drawRightString(self.page_width - self.margin - 10, y_position, timestamp_text)
        
        # ملاحظة
        y_position -= 30
        note_text = self.reshape_arabic_text("هذا الإيصال محاسبي معتمد ولا يقبل التراجع عنه")
        self.draw_centered_text(canvas, note_text, self.page_width / 2, y_position, self.arabic_font, 9)
    
    def _number_to_arabic_words(self, number: float) -> str:
        """تحويل الرقم إلى كلمات عربية"""
        # تنفيذ بسيط لتحويل الأرقام إلى كلمات
        # يمكن توسيعه لاحقاً لدعم أكثر شمولية
        
        units = ['', 'واحد', 'اثنان', 'ثلاثة', 'أربعة', 'خمسة', 'ستة', 'سبعة', 'ثمانية', 'تسعة']
        tens = ['', '', 'عشرون', 'ثلاثون', 'أربعون', 'خمسون', 'ستون', 'سبعون', 'ثمانون', 'تسعون']
        hundreds = ['', 'مائة', 'مائتان', 'ثلاثمائة', 'أربعمائة', 'خمسمائة', 'ستمائة', 'سبعمائة', 'ثمانمائة', 'تسعمائة']
        
        if number == 0:
            return 'صفر'
        
        # تنفيذ بسيط للأرقام حتى 999
        num = int(number)
        if num > 999:
            return f'{num:,} دينار'
        
        result = ''
        
        # المئات
        h = num // 100
        if h > 0:
            result += hundreds[h] + ' '
        
        # العشرات والوحدات
        remainder = num % 100
        if remainder >= 20:
            t = remainder // 10
            u = remainder % 10
            result += tens[t]
            if u > 0:
                result += ' ' + units[u]
        elif remainder >= 11:
            teens = ['أحد عشر', 'اثنا عشر', 'ثلاثة عشر', 'أربعة عشر', 'خمسة عشر', 
                    'ستة عشر', 'سبعة عشر', 'ثمانية عشر', 'تسعة عشر']
            result += teens[remainder - 11]
        elif remainder == 10:
            result += 'عشرة'
        elif remainder > 0:
            result += units[remainder]
        
        return result.strip()
    
    def preview_installment_receipt(self, data: Dict[str, Any]) -> str:
        """معاينة إيصال دفع قسط"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_path = os.path.join(
            config.DATA_DIR, 'uploads', 'temp', 
            f'preview_installment_receipt_{timestamp}.pdf'
        )
        return self.create_installment_receipt(data, temp_path)


# Convenience function for installment receipts
def print_installment_receipt(data: Dict[str, Any], preview_only: bool = True) -> str:
    """طباعة إيصال دفع قسط"""
    manager = ReportLabPrintManager()
    if preview_only:
        return manager.preview_installment_receipt(data)
    else:
        return manager.create_installment_receipt(data)
