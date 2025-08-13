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
            # تطبيق خوارزمية BiDi مع اتجاه RTL
            bidi_text = bidi.algorithm.get_display(reshaped_text, base_dir='R')
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

        # Draw the second receipt just below the first with a larger height and small gap
        receipt_height = self.page_height * 0.48
        gap_between = 0 * mm  # 10mm gap between receipts
        second_receipt_y = self.page_height - receipt_height - gap_between
        self._draw_receipt(c, data, second_receipt_y)
        
        c.save()
        logging.info(f"تم إنشاء إيصال الدفع: {output_path}")
        return output_path

    def _draw_receipt(self, c, data, top_y):
        """Helper function to draw a single receipt with a more organized layout."""
        receipt_height = self.page_height * 0.48
        bottom_y = top_y - receipt_height

        c.setStrokeColor(blue)
        c.setLineWidth(1.5)
        c.rect(self.margin, bottom_y, self.content_width, receipt_height - self.margin)
        c.setStrokeColor(black)

        receipt_data = data.get('receipt', data)
        student_name = receipt_data.get('student_name', 'غير محدد')
        amount = receipt_data.get('amount', 0)
        payment_date = receipt_data.get('payment_date', datetime.now().strftime('%Y-%m-%d'))
        installment_number = receipt_data.get('installment_number', 1)
        school_name = receipt_data.get('school_name', 'المدرسة')
        receipt_number = receipt_data.get('receipt_number', f'R{datetime.now().strftime("%Y%m%d%H%M%S")}')
        installment_id = receipt_data.get('installment_id', '') # Get installment_id from data

        self.arabic_font = 'Amiri'
        self.arabic_bold_font = 'Amiri-Bold'

        # ==== New Header Layout ====
        top_padding = 10 * mm  # Padding from top
        header_y = top_y - self.margin - top_padding
        header_height = 45  # enough for two lines on left

        header_padding = 10 * mm  # Padding from left/right for header content

        # Right: School Name (with padding)
        c.setFont(self.arabic_bold_font, 13)
        school_text = self.reshape_arabic_text(school_name)
        c.drawRightString(self.page_width - self.margin - header_padding, header_y, school_text)

        # Center: School Logo Placeholder (circle)
        circle_x = self.page_width / 2
        circle_y = header_y - 10
        circle_radius = 18
        c.setLineWidth(1)
        c.circle(circle_x, circle_y, circle_radius, stroke=1, fill=0)
        c.setFont(self.arabic_font, 9)
        logo_placeholder = self.reshape_arabic_text("شعار")
        text_width = c.stringWidth(logo_placeholder, self.arabic_font, 9)
        c.drawString(circle_x - text_width / 2, circle_y - 4, logo_placeholder)

        # Left: Receipt Title and Academic Year (with padding)
        left_x = self.margin + header_padding
        c.setFont(self.arabic_bold_font, 14)
        receipt_title = self.reshape_arabic_text("إيصال دفع قسط")
        c.drawString(left_x, header_y, receipt_title)
        c.setFont(self.arabic_font, 11)
        academic_year = self.reshape_arabic_text("للعام الدراسي 2025 - 2026")
        c.drawString(left_x, header_y - 18, academic_year)

        # ==== End Header ====

        y_pos = header_y - header_height
        
        # --- Remove duplicate title under logo ---
        # (احذف السطر التالي:)
        # title = self.reshape_arabic_text("إيصال دفع قسط")
        # self.draw_centered_text(c, title, self.page_width / 2, y_pos, self.arabic_bold_font, 16)
        # y_pos -= 25
        
        c.setFont(self.arabic_font, 11)
        receipt_text = self.reshape_arabic_text(f"رقم الإيصال: {receipt_number}")
        c.drawRightString(self.page_width - self.margin - 10, y_pos, receipt_text)
        
        y_pos -= 15
        c.setLineWidth(0.5)
        c.line(self.margin + 10, y_pos, self.page_width - self.margin - 10, y_pos)
        
        y_pos -= 10
        
        # --- جدول بيانات الوصل بشكل عمودين ---
        # البيانات
        table_fields = [
           
            (self.reshape_arabic_text(f"{amount:,.0f} د.ع"), self.reshape_arabic_text("المبلغ المدفوع")),
            (self.reshape_arabic_text(payment_date), self.reshape_arabic_text("تاريخ الدفع")),
            (self.reshape_arabic_text(f"{receipt_data.get('total_fee', 0):,.0f} د.ع"), self.reshape_arabic_text("إجمالي الرسوم")),
            (self.reshape_arabic_text(f"{receipt_data.get('total_paid', 0):,.0f} د.ع"), self.reshape_arabic_text("المدفوع تراكمياً")),
            (self.reshape_arabic_text(student_name), self.reshape_arabic_text("اسم الطالب")),
            (self.reshape_arabic_text(receipt_data.get('grade', '')), self.reshape_arabic_text("الصف")),
            (self.reshape_arabic_text(receipt_data.get('section', '')), self.reshape_arabic_text("الشعبة")),
            (self.reshape_arabic_text(str(installment_id)), self.reshape_arabic_text("رقم الوصل")),
        ]
        remaining_row = [
            self.reshape_arabic_text(f"{receipt_data.get('remaining', 0):,.0f} د.ع"),
            self.reshape_arabic_text("المبلغ المتبقي")
        ]

        # تقسيم إلى عمودين (يمين ويسار)
        right_col = table_fields[:4]
        left_col = table_fields[4:8]

        # بناء الجدول: كل صف يحوي خليتين من اليمين وخليتين من اليسار
        merged_table_data = []
        for i in range(4):
            merged_table_data.append(
                right_col[i] + left_col[i]
            )
        # صف المبلغ المتبقي بعرض كامل (4 أعمدة)
        merged_table_data.append([
            '', '', remaining_row[0], remaining_row[1]
        ])

        col_widths = [
            self.content_width * 0.25,  # بيانات يمين
            self.content_width * 0.25,  # عنوان يمين
            self.content_width * 0.25,  # بيانات يسار
            self.content_width * 0.25   # عنوان يسار
        ]
        tbl = Table(merged_table_data, colWidths=col_widths, hAlign='CENTER')

        tbl.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -2), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (1, 0), (1, -2), self.arabic_bold_font),
            ('FONTNAME', (3, 0), (3, -2), self.arabic_bold_font),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            # صف المبلغ المتبقي
            ('SPAN', (0, 4), (1, 4)),  # دمج أول خليتين
            ('BACKGROUND', (0, 4), (-1, 4), Color(0.92, 0.92, 0.92)),
            ('TEXTCOLOR', (0, 4), (-1, 4), red),
            ('FONTNAME', (2, 4), (3, 4), self.arabic_bold_font),
            ('ALIGN', (2, 4), (3, 4), 'RIGHT'),
        ]))
        
        table_height = tbl.wrapOn(c, self.content_width, receipt_height)[1]
        y_pos -= table_height
        tbl.drawOn(c, self.margin, y_pos)

        y_pos -= 15
        box_height = 40
        y_pos -= box_height
        c.setLineWidth(1)
        c.rect(self.margin + 20, y_pos, self.content_width - 40, box_height)
        
        amount_digits_text = self.reshape_arabic_text(f"المبلغ: {amount:,.0f} د.ع")
        self.draw_centered_text(c, amount_digits_text, self.page_width / 2, y_pos + 25, self.arabic_bold_font, 13)
        
        amount_words_text = self.reshape_arabic_text(f"فقط ({self._number_to_arabic_words(amount)}) دينار عراقي لا غير")
        self.draw_centered_text(c, amount_words_text, self.page_width / 2, y_pos + 10, self.arabic_font, 10)

    def _number_to_arabic_words(self, number: float) -> str:
        """تحويل الرقم إلى كلمات عربية"""
        # تنفيذ بسيط لتحويل الأرقام إلى كلمات
        # يمكن توسيعه لاحقاً لدعم أكثر شمولية
        
        units = ['', 'واحد', 'اثنان', 'ثلاثة', 'أربعة', 'خمسة', 'ستة', 'سبعة', 'ثمانية', 'تسعة']
        tens = ['', '', 'عشرون', 'ثلاثون', 'أربعون', 'خمسمائة', 'ستمائة', 'سبعمائة', 'ثمانمائة', 'تسعمائة']
        hundreds = ['', 'مائة', 'مائتان', 'ثلاثمائة', 'أربعمائة', 'خمسمائة', 'ستمائة', 'سبعمائة', 'ثمانمائة', 'تسعمائة']
        
        if number == 0:
            return 'صفر'
        
        num = int(number)
        if num > 999999:
            return f'{num:,}'

        if num >= 1000:
            thousands = num // 1000
            remainder = num % 1000
            if thousands == 1:
                k_str = 'ألف'
            elif thousands == 2:
                k_str = 'ألفان'
            elif 3 <= thousands <= 10:
                k_str = self._number_to_arabic_words(thousands) + ' آلاف'
            else:
                k_str = self._number_to_arabic_words(thousands) + ' ألف'

            if remainder > 0:
                return k_str + ' و' + self._number_to_arabic_words(remainder)
            else:
                return k_str

        result = []
        
        h = num // 100
        if h > 0:
            result.append(hundreds[h])
        
        rem = num % 100
        if rem > 0:
            if rem >= 20:
                t = rem // 10
                u = rem % 10
                if u > 0:
                    result.append(units[u])
                result.append(tens[t])
            elif rem >= 11:
                teens = ['أحد عشر', 'اثنا عشر', 'ثلاثة عشر', 'أربعة عشر', 'خمسة عشر', 
                         'ستة عشر', 'سبعة عشر', 'ثمانية عشر', 'تسعة عشر']
                result.append(teens[rem - 11])
            elif rem == 10:
                result.append('عشرة')
            else:
                result.append(units[rem])
        
        return ' و'.join(result)
    
    def preview_installment_receipt(self, data: Dict[str, Any]) -> str:
        """معاينة إيصال دفع قسط"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_path = os.path.join(
            config.DATA_DIR, 'uploads', 'temp', 
            f'preview_installment_receipt_{timestamp}.pdf'
        )
        return self.create_installment_receipt(data, temp_path)
    
    def create_student_report(self, data: Dict[str, Any], output_path: str = None) -> str:
        """إنشاء تقرير طالب مفصل PDF"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                config.DATA_DIR, 'exports', 'prints',
                f'student_report_{timestamp}.pdf'
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        styles = getSampleStyleSheet()
        story = []

        # عنوان التقرير
        title = self.reshape_arabic_text("تقرير الطالب")
        story.append(Paragraph(title, ParagraphStyle(
            'Title', fontName=self.arabic_bold_font,
            fontSize=16, alignment=TA_CENTER, spaceAfter=12)))

        # بيانات الطالب
        student = data.get('student', {})
        info_data = [
            [self.reshape_arabic_text(k), self.reshape_arabic_text(str(v))]
            for k, v in [
                ("الاسم", student.get('name', '')),
                ("المدرسة", student.get('school_name', '')),
                ("الصف", student.get('grade', '')),
                ("الشعبة", student.get('section', '')),
                ("الجنس", student.get('gender', '')),
                ("الهاتف", student.get('phone', '')),
                ("الحالة", student.get('status', '')),
                ("الرسوم الدراسية", f"{student.get('total_fee', 0):,.0f}")
            ]
        ]
        info_table = Table(info_data, hAlign='RIGHT', colWidths=[100, 200])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), None),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 12))

        # الأقساط
        installments = data.get('installments', [])
        if installments:
            story.append(Paragraph(self.reshape_arabic_text("الأقساط المدفوعة"), styles['Heading3']))
            inst_header = [self.reshape_arabic_text(h) for h in ["المبلغ","تاريخ الدفع","وقت الدفع","ملاحظات"]]
            table_data = [inst_header]
            for inst in installments:
                row = [
                    f"{inst.get('amount',0):,.0f}",
                    self.reshape_arabic_text(str(inst.get('payment_date',''))),
                    self.reshape_arabic_text(str(inst.get('payment_time',''))),
                    self.reshape_arabic_text(inst.get('notes',''))
                ]
                table_data.append(row)
            inst_table = Table(table_data, hAlign='RIGHT')
            inst_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, black),
                ('FONTNAME', (0,0), (-1,-1), self.arabic_font),
                ('ALIGN', (0,0), (-1, -1), 'CENTER')
            ]))
            story.append(inst_table)
            story.append(Spacer(1, 12))

        # الرسوم الإضافية
        fees = data.get('additional_fees', [])
        if fees:
            story.append(Paragraph(self.reshape_arabic_text("الرسوم الإضافية"), styles['Heading3']))
            fee_header = [self.reshape_arabic_text(h) for h in ["النوع","المبلغ","تاريخ الإضافة","تاريخ الدفع","ملاحظات"]]
            fee_data = [fee_header]
            for fee in fees:
                row = [
                    self.reshape_arabic_text(str(fee.get('fee_type',''))),
                    f"{fee.get('amount',0):,.0f}",
                    self.reshape_arabic_text(str(fee.get('added_at',''))),
                    self.reshape_arabic_text(str(fee.get('payment_date',''))),
                    self.reshape_arabic_text(fee.get('notes',''))
                ]
                fee_data.append(row)
            fee_table = Table(fee_data, hAlign='RIGHT')
            fee_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, black),
                ('FONTNAME', (0,0), (-1,-1), self.arabic_font),
                ('ALIGN', (0,0), (-1, -1), 'CENTER')
            ]))
            story.append(fee_table)
            story.append(Spacer(1, 12))

        # الملخص المالي
        summary = data.get('financial_summary', {})
        if summary:
            story.append(Paragraph(self.reshape_arabic_text("الملخص المالي"), styles['Heading3']))
            sum_data = [
                [self.reshape_arabic_text(k), f"{v:,.0f}"]
                for k, v in [
                    ("عدد الأقساط", summary.get('installments_count', 0)),
                    ("مجموع الأقساط", summary.get('installments_total', 0)),
                    ("المتبقي من الرسوم", summary.get('school_fee_remaining', 0)),
                    ("عدد الرسوم الإضافية", summary.get('additional_fees_count', 0)),
                    ("مجموع الرسوم الإضافية", summary.get('additional_fees_total', 0)),
                    ("المدفوع من الرسوم الإضافية", summary.get('additional_fees_paid_total', 0)),
                    ("غير المدفوع من الرسوم الإضافية", summary.get('additional_fees_unpaid_total', 0))
                ]
            ]
            sum_table = Table(sum_data, hAlign='RIGHT', colWidths=[150,150])
            sum_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, black),
                ('FONTNAME', (0,0), (-1,-1), self.arabic_font),
                ('ALIGN', (0,0), (-1, -1), 'RIGHT')
            ]))
            story.append(sum_table)

        # بناء المستند
        doc.build(story)
        logging.info(f"تم إنشاء تقرير الطالب: {output_path}")
        return output_path

    def preview_student_report(self, data: Dict[str, Any]) -> str:
        """معاينة تقرير طالب"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_path = os.path.join(
            config.DATA_DIR, 'uploads', 'temp',
            f'preview_student_report_{timestamp}.pdf'
        )
        return self.create_student_report(data, temp_path)


# Convenience function for installment receipts
def print_installment_receipt(data: Dict[str, Any], preview_only: bool = True) -> str:
    """طباعة إيصال دفع قسط"""
    manager = ReportLabPrintManager()
    if preview_only:
        return manager.preview_installment_receipt(data)
    else:
        return manager.create_installment_receipt(data)
