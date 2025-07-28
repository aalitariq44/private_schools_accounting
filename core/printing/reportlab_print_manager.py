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
                
            # تسجيل خط Amiri إن وجد
            amiri_path = fonts_dir / 'Amiri.ttf'
            amiri_bold_path = fonts_dir / 'Amiri-Bold.ttf'
            if amiri_path.exists():
                pdfmetrics.registerFont(TTFont('Amiri', str(amiri_path)))
                logging.info("تم تسجيل خط Amiri بنجاح")
            if amiri_bold_path.exists():
                pdfmetrics.registerFont(TTFont('Amiri-Bold', str(amiri_bold_path)))
                logging.info("تم تسجيل خط Amiri-Bold بنجاح")

            # تعيين الخطوط الافتراضية
            if amiri_path.exists() and amiri_bold_path.exists():
                self.arabic_font = 'Amiri'
                self.arabic_bold_font = 'Amiri-Bold'
            else:
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

        c = canvas.Canvas(output_path, pagesize=A4)

        # Draw the first receipt
        self._draw_receipt(c, data, self.page_height)

        # Draw the second receipt just below the first with a smaller gap
        receipt_height = self.page_height * 0.35
        gap_between = 10 * mm  # 10mm gap between receipts
        second_receipt_y = self.page_height - receipt_height - gap_between
        self._draw_receipt(c, data, second_receipt_y)
        
        c.save()
        logging.info(f"تم إنشاء إيصال الدفع: {output_path}")
        return output_path

    def _draw_receipt(self, c, data, top_y):
        """Helper function to draw a single receipt."""
        # تحديد منطقة الإيصال (أعلى 40% من الصفحة)
        receipt_height = self.page_height * 0.40
        bottom_y = top_y - receipt_height

        # رسم إطار الإيصال باللون الأزرق
        c.setStrokeColor(blue)
        c.setLineWidth(1.5)
        c.rect(self.margin, bottom_y, self.content_width, receipt_height - self.margin)

        # استعادة لون الخط الافتراضي
        c.setStrokeColor(black)

        # معلومات الإيصال
        receipt_data = data.get('receipt', data)
        student_name = receipt_data.get('student_name', 'غير محدد')
        amount = receipt_data.get('amount', 0)
        payment_date = receipt_data.get('payment_date', datetime.now().strftime('%Y-%m-%d'))
        installment_number = receipt_data.get('installment_number', 1)
        school_name = receipt_data.get('school_name', 'المدرسة')
        receipt_number = receipt_data.get('receipt_number', f'R{datetime.now().strftime("%Y%m%d%H%M%S")}')

        self.arabic_font = 'Amiri'
        self.arabic_bold_font = 'Amiri-Bold'

        # --- بدء الرسم داخل الإطار ---
        y_pos = top_y - self.margin - 20
        
        # 1. رأس الإيصال
        title = self.reshape_arabic_text("إيصال دفع قسط")
        self.draw_centered_text(c, title, self.page_width / 2, y_pos, self.arabic_bold_font, 16)
        y_pos -= 25
        
        school_text = self.reshape_arabic_text(school_name)
        self.draw_centered_text(c, school_text, self.page_width / 2, y_pos, self.arabic_bold_font, 13)
        y_pos -= 30
        
        c.setFont(self.arabic_font, 11)
        receipt_text = self.reshape_arabic_text(f"رقم الإيصال: {receipt_number}")
        c.drawRightString(self.page_width - self.margin - 10, y_pos, receipt_text)
        
        # خط فاصل
        y_pos -= 15
        c.setLineWidth(0.5)
        c.line(self.margin + 10, y_pos, self.page_width - self.margin - 10, y_pos)
        
        # 2. محتوى الإيصال
        y_pos -= 25
        line_height = 22
        
        student_label = self.reshape_arabic_text("اسم الطالب:")
        student_value = self.reshape_arabic_text(student_name)
        c.drawRightString(self.page_width - self.margin - 10, y_pos, student_label)
        c.drawRightString(self.page_width - self.margin - 120, y_pos, student_value)
        y_pos -= line_height
        
        installment_label = self.reshape_arabic_text("رقم القسط:")
        installment_value = str(installment_number)
        c.drawRightString(self.page_width - self.margin - 10, y_pos, installment_label)
        c.drawRightString(self.page_width - self.margin - 120, y_pos, installment_value)
        y_pos -= line_height
        
        amount_label = self.reshape_arabic_text("المبلغ المدفوع:")
        amount_value = f"{amount:,.0f} دينار"
        c.drawRightString(self.page_width - self.margin - 10, y_pos, amount_label)
        c.drawRightString(self.page_width - self.margin - 120, y_pos, amount_value)
        y_pos -= line_height

        date_label = self.reshape_arabic_text("تاريخ الدفع:")
        c.drawRightString(self.page_width - self.margin - 10, y_pos, date_label)
        c.drawRightString(self.page_width - self.margin - 120, y_pos, payment_date)

        # صندوق المبلغ
        y_pos -= 30
        box_height = 65
        c.setLineWidth(1)
        c.rect(self.margin + 20, y_pos - box_height, self.content_width - 40, box_height)
        
        y_pos -= 20
        amount_digits = f"{amount:,.0f}"
        self.draw_centered_text(c, amount_digits, self.page_width / 2, y_pos, self.arabic_bold_font, 14)
        
        y_pos -= 22
        amount_words = self.reshape_arabic_text(self._number_to_arabic_words(amount))
        self.draw_centered_text(c, amount_words, self.page_width / 2, y_pos, self.arabic_font, 11)
        
        y_pos -= 18
        currency_text = self.reshape_arabic_text("دينار عراقي لا غير")
        self.draw_centered_text(c, currency_text, self.page_width / 2, y_pos, self.arabic_font, 10)
        
        # 3. الملاحظة السفلية
        note_y_pos = bottom_y + 15
        note_text = self.reshape_arabic_text("هذا الإيصال محاسبي")
        self.draw_centered_text(c, note_text, self.page_width / 2, note_y_pos, self.arabic_font, 9)

    
    
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
