#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مولد PDF لهويّات الطلاب باستخدام ReportLab
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

import config
from templates.id_template import (
    TEMPLATE_ELEMENTS, ID_WIDTH, ID_HEIGHT, A4_WIDTH, A4_HEIGHT,
    GRID_COLS, GRID_ROWS, PAGE_MARGIN_X, PAGE_MARGIN_Y,
    CARD_SPACING_X, CARD_SPACING_Y, CUT_MARKS,
    get_card_position, get_element_absolute_position, get_element_absolute_size
)


class StudentIDGenerator:
    """مولد هويات الطلاب"""
    
    def __init__(self):
        self.canvas = None
        self.setup_fonts()
    
    def setup_fonts(self):
        """إعداد الخطوط العربية"""
        try:
            # محاولة تحميل خط Cairo العربي
            font_dir = config.RESOURCES_DIR / "fonts"
            cairo_font_path = font_dir / "Cairo-Medium.ttf"
            cairo_bold_path = font_dir / "Cairo-Bold.ttf"
            
            if cairo_font_path.exists():
                pdfmetrics.registerFont(TTFont('Cairo', str(cairo_font_path)))
                logging.info("تم تحميل خط Cairo العربي")
            
            if cairo_bold_path.exists():
                pdfmetrics.registerFont(TTFont('Cairo-Bold', str(cairo_bold_path)))
                logging.info("تم تحميل خط Cairo-Bold العربي")
                
        except Exception as e:
            logging.warning(f"فشل في تحميل الخطوط العربية: {e}")
    
    def generate_student_ids(self, students_data: List[Dict], 
                           output_path: str,
                           school_name: str = "",
                           custom_title: str = "هوية طالب") -> bool:
        """
        إنشاء PDF للهويات الطلابية
        
        Args:
            students_data: قائمة بيانات الطلاب
            output_path: مسار ملف PDF الناتج
            school_name: اسم المدرسة
            custom_title: عنوان مخصص للهوية
        
        Returns:
            True إذا تم الإنشاء بنجاح، False في حالة الخطأ
        """
        try:
            # إنشاء canvas
            self.canvas = canvas.Canvas(output_path, pagesize=A4)
            
            # إعداد معلومات المستند
            self.canvas.setCreator("نظام حسابات المدارس الأهلية")
            self.canvas.setTitle(f"هويات الطلاب - {school_name}")
            self.canvas.setSubject("هويات طلابية")
            self.canvas.setKeywords("هوية، طالب، مدرسة")
            
            # تجهيز البيانات
            total_students = len(students_data)
            cards_per_page = GRID_COLS * GRID_ROWS
            total_pages = (total_students + cards_per_page - 1) // cards_per_page
            
            logging.info(f"بدء إنشاء {total_students} هوية في {total_pages} صفحة")
            
            # إنشاء الصفحات
            for page_num in range(total_pages):
                if page_num > 0:
                    self.canvas.showPage()  # صفحة جديدة
                
                # حساب عدد البطاقات في هذه الصفحة
                start_idx = page_num * cards_per_page
                end_idx = min(start_idx + cards_per_page, total_students)
                page_students = students_data[start_idx:end_idx]
                
                # رسم البطاقات في الصفحة
                self.draw_page(page_students, school_name, custom_title)
                
                # إضافة معلومات الصفحة
                self.add_page_info(page_num + 1, total_pages)
            
            # حفظ PDF
            self.canvas.save()
            logging.info(f"تم حفظ ملف الهويات: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء هويات الطلاب: {e}")
            return False
    
    def draw_page(self, students_data: List[Dict], 
                  school_name: str, custom_title: str):
        """رسم صفحة كاملة من الهويات"""
        
        # رسم علامات القطع إذا كانت مفعلة
        if CUT_MARKS.get("enabled", True):
            self.draw_cut_marks()
        
        # رسم البطاقات
        for idx, student in enumerate(students_data):
            row = idx // GRID_COLS
            col = idx % GRID_COLS
            
            if row < GRID_ROWS:  # التأكد من عدم تجاوز الصفوف
                card_x, card_y = get_card_position(row, col)
                self.draw_student_card(student, card_x, card_y, school_name, custom_title)
    
    def draw_student_card(self, student_data: Dict, 
                         card_x: float, card_y: float,
                         school_name: str, custom_title: str):
        """رسم هوية طالب واحد"""
        
        # رسم حدود البطاقة (خفيفة للمرجع)
        self.canvas.setStrokeColor(Color(0.8, 0.8, 0.8))
        self.canvas.setLineWidth(0.5)
        self.canvas.rect(card_x, card_y, ID_WIDTH, ID_HEIGHT, fill=0)
        
        # رسم عناصر البطاقة
        for element_name, element_config in TEMPLATE_ELEMENTS.items():
            if element_name == "school_name":
                self.draw_school_name(card_x, card_y, element_config, school_name)
            elif element_name == "id_title":
                self.draw_text_element(card_x, card_y, element_config, custom_title)
            elif element_name == "student_name":
                student_name = student_data.get('name', 'اسم الطالب')
                self.draw_text_element(card_x, card_y, element_config, student_name)
            elif element_name == "student_grade":
                grade = student_data.get('grade', '')
                grade_text = f"{element_config.get('label', 'الصف: ')}{grade}"
                self.draw_text_element(card_x, card_y, element_config, grade_text)
            elif element_name == "academic_year":
                year_text = element_config.get('text', 'العام الدراسي: 2025 - 2026')
                self.draw_text_element(card_x, card_y, element_config, year_text)
            elif element_name == "photo_box":
                self.draw_photo_box(card_x, card_y, element_config)
            elif element_name == "qr_box":
                self.draw_qr_box(card_x, card_y, element_config)
            elif element_name == "birth_date_box":
                self.draw_birth_date_box(card_x, card_y, element_config)
    
    def draw_text_element(self, card_x: float, card_y: float, 
                         element_config: Dict, text: str):
        """رسم عنصر نصي"""
        
        abs_x, abs_y = get_element_absolute_position(element_config, card_x, card_y)
        
        # إعداد الخط
        font_name = element_config.get('font_name', 'Helvetica')
        if 'Cairo' in pdfmetrics.getRegisteredFontNames():
            if 'Bold' in font_name:
                font_name = 'Cairo-Bold'
            else:
                font_name = 'Cairo'
        
        font_size = element_config.get('font_size', 8)
        color = element_config.get('color', black)
        
        self.canvas.setFont(font_name, font_size)
        self.canvas.setFillColor(color)
        
        # تحديد المحاذاة
        alignment = element_config.get('alignment', 'right')
        max_width = element_config.get('max_width', 1.0) * ID_WIDTH
        
        # كتابة النص مع دعم النص الطويل
        text = self.fit_text_to_width(text, font_name, font_size, max_width)
        
        if alignment == 'center':
            self.canvas.drawCentredText(abs_x, abs_y, text)
        elif alignment == 'left':
            self.canvas.drawString(abs_x, abs_y, text)
        else:  # right alignment (default)
            self.canvas.drawRightString(abs_x, abs_y, text)
    
    def draw_school_name(self, card_x: float, card_y: float, 
                        element_config: Dict, school_name: str):
        """رسم اسم المدرسة مع معالجة خاصة"""
        if school_name:
            self.draw_text_element(card_x, card_y, element_config, school_name)
    
    def draw_photo_box(self, card_x: float, card_y: float, element_config: Dict):
        """رسم مربع الصورة"""
        
        abs_x, abs_y = get_element_absolute_position(element_config, card_x, card_y)
        width, height = get_element_absolute_size(element_config)
        
        # رسم المربع
        border_color = element_config.get('border_color', black)
        fill_color = element_config.get('fill_color', white)
        border_width = element_config.get('border_width', 1)
        
        self.canvas.setStrokeColor(border_color)
        self.canvas.setFillColor(fill_color)
        self.canvas.setLineWidth(border_width)
        self.canvas.rect(abs_x, abs_y, width, height, fill=1)
        
        # إضافة نص "صورة" في الوسط
        label = element_config.get('label', 'صورة')
        label_font_size = element_config.get('label_font_size', 6)
        
        font_name = 'Cairo' if 'Cairo' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        self.canvas.setFont(font_name, label_font_size)
        self.canvas.setFillColor(Color(0.6, 0.6, 0.6))
        
        # وسط المربع
        center_x = abs_x + width / 2
        center_y = abs_y + height / 2
        self.canvas.drawCentredText(center_x, center_y, label)
    
    def draw_qr_box(self, card_x: float, card_y: float, element_config: Dict):
        """رسم مربع QR مؤقت"""
        
        abs_x, abs_y = get_element_absolute_position(element_config, card_x, card_y)
        width, height = get_element_absolute_size(element_config)
        
        # رسم المربع
        border_color = element_config.get('border_color', black)
        fill_color = element_config.get('fill_color', white)
        border_width = element_config.get('border_width', 1)
        
        self.canvas.setStrokeColor(border_color)
        self.canvas.setFillColor(fill_color)
        self.canvas.setLineWidth(border_width)
        self.canvas.rect(abs_x, abs_y, width, height, fill=1)
        
        # إضافة نص "QR"
        label = element_config.get('label', 'QR')
        label_font_size = element_config.get('label_font_size', 5)
        
        self.canvas.setFont('Helvetica', label_font_size)
        self.canvas.setFillColor(Color(0.6, 0.6, 0.6))
        
        center_x = abs_x + width / 2
        center_y = abs_y + height / 2
        self.canvas.drawCentredText(center_x, center_y, label)
    
    def draw_birth_date_box(self, card_x: float, card_y: float, element_config: Dict):
        """رسم خانة تاريخ الميلاد"""
        
        abs_x, abs_y = get_element_absolute_position(element_config, card_x, card_y)
        width, height = get_element_absolute_size(element_config)
        
        # رسم المربع
        border_color = element_config.get('border_color', black)
        fill_color = element_config.get('fill_color', white)
        border_width = element_config.get('border_width', 0.5)
        
        self.canvas.setStrokeColor(border_color)
        self.canvas.setFillColor(fill_color)
        self.canvas.setLineWidth(border_width)
        self.canvas.rect(abs_x, abs_y, width, height, fill=1)
        
        # إضافة النص
        label = element_config.get('label', 'تاريخ الميلاد: _______________')
        label_font_size = element_config.get('label_font_size', 6)
        label_x = element_config.get('label_x', 0.1)
        label_y = element_config.get('label_y', 0.18)
        
        font_name = 'Cairo' if 'Cairo' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        self.canvas.setFont(font_name, label_font_size)
        self.canvas.setFillColor(black)
        
        text_x = card_x + label_x * ID_WIDTH
        text_y = card_y + label_y * ID_HEIGHT
        self.canvas.drawString(text_x, text_y, label)
    
    def draw_cut_marks(self):
        """رسم علامات القطع"""
        
        if not CUT_MARKS.get("enabled", True):
            return
        
        mark_length = CUT_MARKS.get("length", 3 * mm / 10)
        mark_color = CUT_MARKS.get("color", Color(0.7, 0.7, 0.7))
        mark_width = CUT_MARKS.get("width", 0.5)
        
        self.canvas.setStrokeColor(mark_color)
        self.canvas.setLineWidth(mark_width)
        
        # رسم علامات القطع في نقاط التقاطع
        for row in range(GRID_ROWS + 1):
            for col in range(GRID_COLS + 1):
                x = PAGE_MARGIN_X + col * (ID_WIDTH + CARD_SPACING_X) - CARD_SPACING_X / 2
                y = A4_HEIGHT - PAGE_MARGIN_Y - row * (ID_HEIGHT + CARD_SPACING_Y) + CARD_SPACING_Y / 2
                
                # تجنب الرسم خارج حدود الصفحة
                if 0 <= x <= A4_WIDTH and 0 <= y <= A4_HEIGHT:
                    # علامة أفقية
                    self.canvas.line(x - mark_length/2, y, x + mark_length/2, y)
                    # علامة عمودية
                    self.canvas.line(x, y - mark_length/2, x, y + mark_length/2)
    
    def add_page_info(self, page_num: int, total_pages: int):
        """إضافة معلومات الصفحة"""
        
        # معلومات في أسفل الصفحة
        info_text = f"صفحة {page_num} من {total_pages} - تم الإنشاء في {datetime.now().strftime('%Y/%m/%d %H:%M')}"
        
        self.canvas.setFont('Helvetica', 6)
        self.canvas.setFillColor(Color(0.5, 0.5, 0.5))
        self.canvas.drawCentredText(A4_WIDTH / 2, 10, info_text)
    
    def fit_text_to_width(self, text: str, font_name: str, 
                         font_size: float, max_width: float) -> str:
        """تقليص النص ليناسب العرض المحدد"""
        
        try:
            text_width = self.canvas.stringWidth(text, font_name, font_size)
            
            if text_width <= max_width:
                return text
            
            # تقليص النص تدريجياً
            for i in range(len(text) - 1, 0, -1):
                short_text = text[:i] + "..."
                if self.canvas.stringWidth(short_text, font_name, font_size) <= max_width:
                    return short_text
            
            return text[:3] + "..." if len(text) > 3 else text
            
        except:
            return text


def generate_student_ids_pdf(students_data: List[Dict], 
                           output_path: str,
                           school_name: str = "",
                           custom_title: str = "هوية طالب") -> bool:
    """
    دالة مساعدة لإنشاء PDF الهويات
    
    Args:
        students_data: قائمة بيانات الطلاب (يجب أن تحتوي على 'name' و 'grade' على الأقل)
        output_path: مسار ملف PDF الناتج
        school_name: اسم المدرسة
        custom_title: عنوان مخصص للهوية
    
    Returns:
        True إذا تم الإنشاء بنجاح، False في حالة الخطأ
    """
    
    generator = StudentIDGenerator()
    return generator.generate_student_ids(
        students_data, 
        output_path, 
        school_name, 
        custom_title
    )


# مثال للاستخدام
if __name__ == "__main__":
    # بيانات تجريبية
    test_students = [
        {"name": "أحمد محمد علي", "grade": "الأول الابتدائي"},
        {"name": "فاطمة حسن محمود", "grade": "الثاني الابتدائي"},
        {"name": "محمد عبدالله أحمد", "grade": "الثالث الابتدائي"},
        {"name": "نور الهدى صالح", "grade": "الرابع الابتدائي"},
        {"name": "عمار طارق حسين", "grade": "الخامس الابتدائي"},
    ]
    
    output_file = "test_student_ids.pdf"
    result = generate_student_ids_pdf(
        test_students, 
        output_file, 
        "مدرسة النور الأهلية",
        "هوية طالب"
    )
    
    if result:
        print(f"تم إنشاء ملف الهويات: {output_file}")
    else:
        print("فشل في إنشاء ملف الهويات")
