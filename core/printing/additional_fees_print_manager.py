# -*- coding: utf-8 -*-
"""
مدير طباعة إيصالات الرسوم الإضافية
يوفر طباعة دقيقة مع دعم كامل للعربية (RTL + تشكيل الأحرف)
"""

# Apply hashlib patch FIRST
import hashlib_patch

import logging
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# ReportLab imports
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle
from reportlab.lib.colors import Color, black, blue, red, green
from reportlab.pdfgen import canvas

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
from core.utils.settings_manager import get_academic_year


class AdditionalFeesPrintManager:
    """مدير طباعة إيصالات الرسوم الإضافية"""
    
    def __init__(self):
        self.setup_fonts()
        self.page_width, self.page_height = A4
        self.margin = 10 * mm  # هوامش مقلصة لتخطيط أكثر إحكاماً
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
            # تطبيق خوارزمية BiDi مع تحديد اتجاه RTL
            bidi_text = bidi.algorithm.get_display(reshaped_text, base_dir='R')
            return bidi_text
        except Exception as e:
            logging.error(f"خطأ في إعادة تشكيل النص العربي: {e}")
            return text
    
    def create_additional_fees_receipt(self, data: Dict[str, Any], output_path: str = None) -> str:
        """إنشاء إيصال الرسوم الإضافية"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                config.DATA_DIR, 'exports', 'prints',
                f'additional_fees_receipt_{timestamp}.pdf'
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        c = canvas.Canvas(output_path, pagesize=A4)

        # رسم الإيصال الأول
        self._draw_fees_receipt(c, data, self.page_height)

        # رسم الإيصال الثاني أسفل الأول مع فجوة صغيرة
        receipt_height = self.page_height * 0.48
        gap_between = 0 * mm  # 0mm فجوة بين الإيصالات
        second_receipt_y = self.page_height - receipt_height - gap_between
        self._draw_fees_receipt(c, data, second_receipt_y)
        
        c.save()
        logging.info(f"تم إنشاء إيصال الرسوم الإضافية: {output_path}")
        return output_path

    def _draw_fees_receipt(self, c, data, top_y):
        """دالة مساعدة لرسم إيصال واحد للرسوم الإضافية"""
        receipt_height = self.page_height * 0.48
        bottom_y = top_y - receipt_height

        # رسم إطار الإيصال
        c.setStrokeColor(blue)
        c.setLineWidth(1.5)
        c.rect(self.margin, bottom_y, self.content_width, receipt_height - self.margin)
        c.setStrokeColor(black)

        # استخراج البيانات
        student = data.get('student', {})
        fees = data.get('fees', [])
        summary = data.get('summary', {})
        
        student_name = student.get('name', 'غير محدد')
        school_name = student.get('school_name', 'المدرسة')
        school_name_en = student.get('school_name_en', '')
        school_logo_path = student.get('school_logo_path', '')
        grade = student.get('grade', '')
        section = student.get('section', '')
        receipt_number = data.get('receipt_number', f'AF{datetime.now().strftime("%Y%m%d%H%M%S")}')
        print_date = data.get('print_date', datetime.now().strftime('%Y-%m-%d'))
        print_time = data.get('print_time', datetime.now().strftime('%H:%M:%S'))

        y_pos = top_y - self.margin - 15
        
        # Header similar to installment receipt
        from reportlab.lib.units import mm  # ensure mm available
        # Calculate header positions
        top_padding = 10 * mm
        header_y = top_y - self.margin - top_padding
        header_height = 45  # enough for two lines on left
        header_padding = 10 * mm

        # Right: School Name
        c.setFont(self.arabic_bold_font, 13)
        school_text = self.reshape_arabic_text(school_name)
        c.drawRightString(self.page_width - self.margin - header_padding, header_y, school_text)
        
        # إضافة الاسم الإنجليزي تحت الاسم العربي (إذا وجد)
        if school_name_en and school_name_en.strip():
            c.setFont('Helvetica', 10)  # خط إنجليزي
            c.drawRightString(self.page_width - self.margin - header_padding, header_y - 15, school_name_en.strip())

        # Center: School Logo
        circle_x = self.page_width / 2
        circle_y = header_y - 10
        
        # تحديد مسار الشعار - أولوية لشعار المدرسة ثم الافتراضي
        logo_path = None
        if school_logo_path and Path(school_logo_path).exists():
            logo_path = Path(school_logo_path)
        else:
            default_logo_path = Path(config.RESOURCES_DIR) / 'images' / 'logo.png'
            if default_logo_path.exists():
                logo_path = default_logo_path
        
        if logo_path and logo_path.exists():
            img_size = 49
            c.drawImage(str(logo_path), circle_x - img_size / 2, circle_y - img_size / 2, width=img_size, height=img_size, preserveAspectRatio=True, mask='auto')
        else:
            c.setLineWidth(1)
            c.circle(circle_x, circle_y, 18, stroke=1, fill=0)

        # Left: Receipt Title and Academic Year
        left_x = self.margin + header_padding
        c.setFont(self.arabic_bold_font, 14)
        receipt_title = self.reshape_arabic_text("إيصال الرسوم الإضافية")
        c.drawString(left_x, header_y, receipt_title)
        c.setFont(self.arabic_font, 11)
        current_academic_year = get_academic_year()
        academic_year = self.reshape_arabic_text(f"للعام الدراسي {current_academic_year}")
        c.drawString(left_x, header_y - 18, academic_year)

        # End Header
        y_pos = header_y - header_height

        # Add receipt number and print date
        c.setFont(self.arabic_font, 10)
        receipt_text = self.reshape_arabic_text(f"رمز الإيصال: {receipt_number}")
        c.drawRightString(self.page_width - self.margin - 10, y_pos, receipt_text)
        date_text = self.reshape_arabic_text(f"تاريخ الطباعة: {print_date} - {print_time}")
        c.drawString(self.margin + 10, y_pos, date_text)
        y_pos -= 12
        c.setLineWidth(0.5)
        c.line(self.margin + 10, y_pos, self.page_width - self.margin - 10, y_pos)
        y_pos -= 15

        # معلومات الطالب
        student_info_data = [
            [self.reshape_arabic_text(student_name), self.reshape_arabic_text("اسم الطالب")],
            [self.reshape_arabic_text(f"{grade} - {section}"), self.reshape_arabic_text("الصف والشعبة")],
        ]

        col_widths = [self.content_width * 0.6, self.content_width * 0.4]
        student_table = Table(student_info_data, colWidths=col_widths, hAlign='CENTER')
        
        student_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (1, 0), (1, -1), self.arabic_bold_font),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        student_table_height = student_table.wrapOn(c, self.content_width, receipt_height)[1]
        y_pos -= student_table_height
        student_table.drawOn(c, self.margin, y_pos)
        y_pos -= 10

        # جدول الرسوم الإضافية
        fees_header = [
            self.reshape_arabic_text("المبلغ"),
            self.reshape_arabic_text("الحالة"), 
            self.reshape_arabic_text("تاريخ الدفع"),
            self.reshape_arabic_text("تاريخ الإضافة"),
            self.reshape_arabic_text("الملاحظات"),
            self.reshape_arabic_text("نوع الرسم")
        ]
        
        fees_data = [fees_header]
        
        for fee in fees:
            status = "مدفوع" if fee.get('paid', False) else "غير مدفوع"
            
            # معالجة تاريخ الدفع بشكل صحيح
            if fee.get('paid', False):
                payment_date = fee.get('payment_date')
                if payment_date and payment_date != 'None' and str(payment_date).strip():
                    # إذا كان هناك تاريخ دفع صحيح
                    if isinstance(payment_date, str) and payment_date != 'None':
                        display_payment_date = payment_date
                    else:
                        display_payment_date = str(payment_date) if payment_date else '--'
                else:
                    # إذا لم يكن هناك تاريخ دفع، استخدم تاريخ الإنشاء
                    created_date = fee.get('created_at')
                    if created_date and created_date != 'None' and str(created_date).strip():
                        display_payment_date = str(created_date)
                    else:
                        display_payment_date = '--'
            else:
                display_payment_date = '--'
            
            # معالجة تاريخ الإضافة
            created_date = fee.get('created_at')
            if created_date and created_date != 'None' and str(created_date).strip():
                display_created_date = str(created_date)
            else:
                display_created_date = '--'
            
            # معالجة الملاحظات
            notes = fee.get('notes')
            if notes and notes != 'None' and str(notes).strip():
                display_notes = str(notes)
            else:
                display_notes = ''
            
            row = [
                f"{fee.get('amount', 0):,.0f} د.ع",
                self.reshape_arabic_text(status),
                self.reshape_arabic_text(display_payment_date),
                self.reshape_arabic_text(display_created_date),
                self.reshape_arabic_text(display_notes),
                self.reshape_arabic_text(str(fee.get('fee_type', '') or ''))
            ]
            fees_data.append(row)

        # حساب عرض أعمدة جدول الرسوم (6 أعمدة)
        fees_col_widths = [
            self.content_width * 0.15,  # المبلغ
            self.content_width * 0.15,  # الحالة
            self.content_width * 0.18,  # تاريخ الدفع
            self.content_width * 0.18,  # تاريخ الإضافة
            self.content_width * 0.14,  # الملاحظات
            self.content_width * 0.20   # نوع الرسم
        ]
        
        fees_table = Table(fees_data, colWidths=fees_col_widths, hAlign='CENTER')
        
        fees_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), self.arabic_bold_font),  # رأس الجدول
            ('BACKGROUND', (0, 0), (-1, 0), Color(0.85, 0.85, 0.85)),  # خلفية رأس الجدول
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        # تلوين الصفوف حسب حالة الدفع
        for i, fee in enumerate(fees, 1):
            if fee.get('paid', False):
                fees_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (-1, i), Color(0.9, 1.0, 0.9))  # أخضر فاتح للمدفوع
                ]))
            else:
                fees_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (-1, i), Color(1.0, 0.95, 0.8))  # أصفر فاتح لغير المدفوع
                ]))
        
        fees_table_height = fees_table.wrapOn(c, self.content_width, receipt_height)[1]
        y_pos -= fees_table_height
        fees_table.drawOn(c, self.margin, y_pos)
        y_pos -= 15

        # ملخص الرسوم
        summary_data = [
            [f"{summary.get('fees_count', 0)}", self.reshape_arabic_text("عدد الرسوم")],
            [f"{summary.get('total_amount', 0):,.0f} د.ع", self.reshape_arabic_text("المجموع الكلي")],
            [f"{summary.get('paid_amount', 0):,.0f} د.ع", self.reshape_arabic_text("المدفوع")],
            [f"{summary.get('unpaid_amount', 0):,.0f} د.ع", self.reshape_arabic_text("غير المدفوع")],
        ]

        summary_table = Table(summary_data, colWidths=col_widths, hAlign='CENTER')
        
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (1, 0), (1, -1), self.arabic_bold_font),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('BACKGROUND', (0, -1), (-1, -1), Color(0.92, 0.92, 0.92)),  # خلفية للصف الأخير
            ('TEXTCOLOR', (0, -1), (-1, -1), red),  # لون أحمر للمبلغ غير المدفوع
            ('FONTNAME', (0, -1), (-1, -1), self.arabic_bold_font),
        ]))
        
        summary_table_height = summary_table.wrapOn(c, self.content_width, receipt_height)[1]
        y_pos -= summary_table_height
        summary_table.drawOn(c, self.margin, y_pos)

        # Footer section with image and company info
        footer_height = 12 * mm  # reduced footer height
        footer_padding = 5 * mm
        footer_y = bottom_y + footer_padding
        footer_x = self.margin
        # Divider line above footer
        divider_y = footer_y + footer_height + 2 * mm  # reduced space above footer
        c.setLineWidth(0.5)
        c.line(self.margin, divider_y, self.page_width - self.margin, divider_y)


        # Image and text columns
        left_width = self.content_width * 0.8
        right_width = self.content_width * 0.15  # smaller logo column width
        # Draw logo in right column
        logo_path = Path(config.RESOURCES_DIR) / 'images' / 'new_tech.jpg'
        if logo_path.exists():
            c.drawImage(
                str(logo_path),
                footer_x + left_width,
                footer_y,
                width=right_width,
                height=footer_height,
                preserveAspectRatio=True,
                mask='auto'
            )
        # Company info text in left column
        text0 = self.reshape_arabic_text("يرجى الاحتفاظ بالوصل لإبرازه عند الحاجة")
        text1 = self.reshape_arabic_text("شركة الحلول التقنية الجديدة   واتساب: 07859371340 تليجرام: @tech_solu")
        text2 = self.reshape_arabic_text("لإنشاء كافة تطبيقات الجوال وسطح المكتب والويب")
        center_x_left = footer_x + (left_width / 2)
        center_y = footer_y + (footer_height / 2)
        self.draw_centered_text(c, text0, center_x_left, center_y + 14, self.arabic_font, 9)
        self.draw_centered_text(c, text1, center_x_left, center_y + 2, self.arabic_bold_font, 9)
        self.draw_centered_text(c, text2, center_x_left, center_y - 8, self.arabic_font, 9)

    def preview_additional_fees_receipt(self, data: Dict[str, Any]) -> str:
        """معاينة إيصال الرسوم الإضافية"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_path = os.path.join(
            config.DATA_DIR, 'uploads', 'temp', 
            f'preview_additional_fees_receipt_{timestamp}.pdf'
        )
        return self.create_additional_fees_receipt(data, temp_path)


# دالة مساعدة للطباعة
def print_additional_fees_receipt(data: Dict[str, Any], preview_only: bool = True) -> str:
    """طباعة إيصال الرسوم الإضافية"""
    manager = AdditionalFeesPrintManager()
    if preview_only:
        return manager.preview_additional_fees_receipt(data)
    else:
        return manager.create_additional_fees_receipt(data)
