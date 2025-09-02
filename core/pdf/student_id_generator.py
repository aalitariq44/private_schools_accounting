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

# Arabic text support
try:
    import arabic_reshaper
    import bidi.algorithm
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    logging.warning("مكتبات دعم العربية غير متوفرة. سيتم استخدام النص العادي.")

import config
from templates.id_template import (
    TEMPLATE_ELEMENTS, ID_WIDTH, ID_HEIGHT, A4_WIDTH, A4_HEIGHT,
    GRID_COLS, GRID_ROWS, PAGE_MARGIN_X, PAGE_MARGIN_Y,
    CARD_SPACING_X, CARD_SPACING_Y, CUT_MARKS,
    get_card_position, get_element_absolute_position, get_element_absolute_size,
    verify_layout_fits, get_optimized_layout
)
from core.utils.settings_manager import get_academic_year


class StudentIDGenerator:
    """مولد هويات الطلاب"""
    
    def __init__(self):
        self.canvas = None
        self.setup_fonts()
    
    def reshape_arabic_text(self, text: str) -> str:
        """إعادة تشكيل النص العربي للعرض الصحيح من اليمين لليسار"""
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
    
    def setup_fonts(self):
        """إعداد الخطوط العربية"""
        try:
            # محاولة تحميل خط Cairo العربي
            font_dir = Path(config.BASE_DIR) / "app" / "resources" / "fonts"
            # البحث في مسار بديل أيضاً
            alt_font_dir = Path(config.RESOURCES_DIR) / "fonts"
            
            cairo_font_path = font_dir / "Cairo-Medium.ttf"
            cairo_bold_path = font_dir / "Cairo-Bold.ttf"
            amiri_font_path = font_dir / "Amiri.ttf"
            amiri_bold_path = font_dir / "Amiri-Bold.ttf"
            
            # البحث في المسار البديل إذا لم توجد في المسار الأساسي
            if not cairo_font_path.exists():
                cairo_font_path = alt_font_dir / "Cairo-Medium.ttf"
            if not cairo_bold_path.exists():
                cairo_bold_path = alt_font_dir / "Cairo-Bold.ttf"
            if not amiri_font_path.exists():
                amiri_font_path = alt_font_dir / "Amiri.ttf"
            if not amiri_bold_path.exists():
                amiri_bold_path = alt_font_dir / "Amiri-Bold.ttf"
            
            fonts_loaded = False
            
            # تحميل خط Amiri أولاً لأنه الأفضل للعربية
            if amiri_font_path.exists():
                pdfmetrics.registerFont(TTFont('Amiri', str(amiri_font_path)))
                fonts_loaded = True
                logging.info("تم تحميل خط Amiri العربي")
            
            if amiri_bold_path.exists():
                pdfmetrics.registerFont(TTFont('Amiri-Bold', str(amiri_bold_path)))
                fonts_loaded = True
                logging.info("تم تحميل خط Amiri-Bold العربي")
            
            # تحميل خط Cairo كبديل
            if cairo_font_path.exists():
                pdfmetrics.registerFont(TTFont('Cairo-Medium', str(cairo_font_path)))
                fonts_loaded = True
                logging.info("تم تحميل خط Cairo-Medium العربي")
            
            if cairo_bold_path.exists():
                pdfmetrics.registerFont(TTFont('Cairo-Bold', str(cairo_bold_path)))
                fonts_loaded = True
                logging.info("تم تحميل خط Cairo-Bold العربي")
            
            # تعيين الخطوط المفضلة للاستخدام
            available_fonts = pdfmetrics.getRegisteredFontNames()
            if 'Amiri' in available_fonts and 'Amiri-Bold' in available_fonts:
                self.arabic_font = 'Amiri'
                self.arabic_bold_font = 'Amiri-Bold'
                logging.info("تم تعيين خط Amiri كخط أساسي للعربية")
            elif 'Cairo-Medium' in available_fonts and 'Cairo-Bold' in available_fonts:
                self.arabic_font = 'Cairo-Medium'
                self.arabic_bold_font = 'Cairo-Bold'
                logging.info("تم تعيين خط Cairo كخط أساسي للعربية")
            else:
                self.arabic_font = 'Helvetica'
                self.arabic_bold_font = 'Helvetica-Bold'
                logging.warning("لم يتم تحميل خطوط عربية - سيتم استخدام Helvetica")
            
            if not fonts_loaded:
                logging.warning("لم يتم العثور على خطوط عربية - سيتم استخدام الخط الافتراضي")
                
        except Exception as e:
            logging.warning(f"فشل في تحميل الخطوط العربية: {e}")
            self.arabic_font = 'Helvetica'
            self.arabic_bold_font = 'Helvetica-Bold'
    
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
            # التحقق من التخطيط قبل البدء
            layout_check = verify_layout_fits()
            if not layout_check['width_fits'] or not layout_check['height_fits']:
                logging.warning(f"تحذير: التخطيط قد لا يتسع في الصفحة")
                logging.warning(f"العرض المطلوب: {layout_check['total_width']:.2f}, المتاح: {layout_check['a4_width']:.2f}")
                logging.warning(f"الارتفاع المطلوب: {layout_check['total_height']:.2f}, المتاح: {layout_check['a4_height']:.2f}")
                
                # محاولة استخدام تخطيط محسن
                optimized = get_optimized_layout()
                if optimized:
                    logging.info("سيتم استخدام تخطيط محسن للصفحة")
                    global PAGE_MARGIN_X, PAGE_MARGIN_Y, CARD_SPACING_X, CARD_SPACING_Y
                    PAGE_MARGIN_X = optimized['page_margin_x']
                    PAGE_MARGIN_Y = optimized['page_margin_y']
                    CARD_SPACING_X = optimized['card_spacing_x'] 
                    CARD_SPACING_Y = optimized['card_spacing_y']
            else:
                logging.info("التخطيط يتسع بشكل مناسب في صفحة A4")
            
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
                
                # التحقق من أن البطاقة تقع ضمن حدود الصفحة
                if (card_x >= 0 and card_x + ID_WIDTH <= A4_WIDTH and 
                    card_y >= 0 and card_y + ID_HEIGHT <= A4_HEIGHT):
                    self.draw_student_card(student, card_x, card_y, school_name, custom_title)
                else:
                    logging.warning(f"تحذير: البطاقة في الصف {row}, العمود {col} تتجاوز حدود الصفحة")
                    logging.warning(f"موقع البطاقة: x={card_x:.2f}, y={card_y:.2f}")
                    logging.warning(f"حدود الصفحة: width={A4_WIDTH:.2f}, height={A4_HEIGHT:.2f}")
            else:
                logging.warning(f"تحذير: تجاوز عدد الصفوف المسموح - الصف {row} للطالب رقم {idx + 1}")
    
    
    def draw_student_card(self, student_data: Dict, 
                         card_x: float, card_y: float,
                         school_name: str, custom_title: str):
        """رسم هوية طالب واحد مع التصميم المحسّن"""
        
        # رسم حدود البطاقة (خفيفة للمرجع)
        self.canvas.setStrokeColor(Color(0.8, 0.8, 0.8))
        self.canvas.setLineWidth(0.5)
        self.canvas.rect(card_x, card_y, ID_WIDTH, ID_HEIGHT, fill=0)
        
        # رسم عناصر البطاقة
        for element_name, element_config in TEMPLATE_ELEMENTS.items():
            if element_name == "school_name":
                # استخدام اسم مدرسة الطالب الفردية إذا توفرت، وإلا اسم المدرسة العامة
                student_school = student_data.get('school_name', school_name)
                self.draw_school_name(card_x, card_y, element_config, student_school)
            elif element_name == "id_title":
                # استخدام النص الثابت من التكوين
                title_text = element_config.get('text', 'هوية طالب')
                self.draw_text_element(card_x, card_y, element_config, title_text)
            elif element_name == "student_name":
                student_name = student_data.get('name', 'اسم الطالب')
                self.draw_text_element(card_x, card_y, element_config, student_name)
            elif element_name == "student_grade":
                grade = student_data.get('grade', '')
                grade_text = f"{element_config.get('label', '')}{grade}"
                self.draw_text_element(card_x, card_y, element_config, grade_text)
            elif element_name == "academic_year":
                current_year = get_academic_year()
                year_text = element_config.get('text', f'العام الدراسي: {current_year}')
                self.draw_text_element(card_x, card_y, element_config, year_text)
            elif element_name == "photo_box":
                self.draw_photo_box(card_x, card_y, element_config)
            elif element_name == "qr_box":
                self.draw_qr_box(card_x, card_y, element_config)
            elif element_name == "birth_date_box":
                birthdate = student_data.get('birthdate', '')
                self.draw_birth_date_box(card_x, card_y, element_config, birthdate)
            elif element_name.endswith('_label'):
                # رسم التسميات (العناوين الفرعية)
                label_text = element_config.get('text', '')
                if label_text:
                    self.draw_text_element(card_x, card_y, element_config, label_text)
            elif element_name.endswith('_line') or element_config.get('type') == 'line':
                # رسم الخطوط الفاصلة
                self.draw_line_element(card_x, card_y, element_config)
            elif element_name == "id_number":
                # رسم رقم الطالب (يمكن تخصيصه لاحقاً)
                id_text = f"رقم الطالب: {student_data.get('id', 'AUTO')}"
                self.draw_text_element(card_x, card_y, element_config, id_text)
    
    def draw_text_element(self, card_x: float, card_y: float, 
                         element_config: Dict, text: str):
        """رسم عنصر نصي مع دعم كامل للعربية"""
        
        abs_x, abs_y = get_element_absolute_position(element_config, card_x, card_y)
        
        # إعداد الخط
        font_name = element_config.get('font_name', 'Helvetica')
        
        # استخدام الخطوط العربية المحددة مسبقاً
        if 'Bold' in font_name or 'bold' in font_name.lower():
            if hasattr(self, 'arabic_bold_font'):
                font_name = self.arabic_bold_font
            else:
                available_fonts = pdfmetrics.getRegisteredFontNames()
                if 'Amiri-Bold' in available_fonts:
                    font_name = 'Amiri-Bold'
                elif 'Cairo-Bold' in available_fonts:
                    font_name = 'Cairo-Bold'
                elif 'Amiri' in available_fonts:
                    font_name = 'Amiri'
                elif 'Cairo-Medium' in available_fonts:
                    font_name = 'Cairo-Medium'
        else:
            if hasattr(self, 'arabic_font'):
                font_name = self.arabic_font
            else:
                available_fonts = pdfmetrics.getRegisteredFontNames()
                if 'Amiri' in available_fonts:
                    font_name = 'Amiri'
                elif 'Cairo-Medium' in available_fonts:
                    font_name = 'Cairo-Medium'
        
        font_size = element_config.get('font_size', 8)
        color = element_config.get('color', black)
        
        self.canvas.setFont(font_name, font_size)
        self.canvas.setFillColor(color)
        
        # تحديد المحاذاة
        alignment = element_config.get('alignment', 'right')
        max_width = element_config.get('max_width', 1.0) * ID_WIDTH
        
        # تشكيل النص العربي أولاً
        shaped_text = self.reshape_arabic_text(text)
        
        # ثم ملائمة النص للعرض (بدون إعادة تشكيل)
        final_text = self.fit_text_to_width_simple(shaped_text, font_name, font_size, max_width)
        
        if alignment == 'center':
            self.canvas.drawCentredString(abs_x, abs_y, final_text)
        elif alignment == 'left':
            self.canvas.drawString(abs_x, abs_y, final_text)
        else:  # right alignment (default)
            self.canvas.drawRightString(abs_x, abs_y, final_text)
    
    def draw_school_name(self, card_x: float, card_y: float, 
                        element_config: Dict, school_name: str):
        """رسم اسم المدرسة مع معالجة خاصة"""
        if school_name:
            self.draw_text_element(card_x, card_y, element_config, school_name)
    
    def draw_line_element(self, card_x: float, card_y: float, element_config: Dict):
        """رسم خط فاصل"""
        
        abs_x, abs_y = get_element_absolute_position(element_config, card_x, card_y)
        width = element_config.get('width', 0.9) * ID_WIDTH
        height = element_config.get('height', 0.01) * ID_HEIGHT
        color = element_config.get('color', black)
        
        self.canvas.setFillColor(color)
        self.canvas.rect(abs_x, abs_y, width, height, fill=1, stroke=0)
    
    def draw_photo_box(self, card_x: float, card_y: float, element_config: Dict):
        """رسم مربع الصورة مع التصميم المحسّن"""
        
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
        label_color = element_config.get('label_color', Color(0.6, 0.6, 0.6))
        
        # استخدام الخط العربي إذا كان متوفراً
        font_name = getattr(self, 'arabic_font', 'Helvetica')
        
        self.canvas.setFont(font_name, label_font_size)
        self.canvas.setFillColor(label_color)
        
        # تشكيل النص العربي
        shaped_label = self.reshape_arabic_text(label)
        
        # وسط المربع
        center_x = abs_x + width / 2
        center_y = abs_y + height / 2
        self.canvas.drawCentredString(center_x, center_y, shaped_label)
    
    def draw_qr_box(self, card_x: float, card_y: float, element_config: Dict):
        """رسم مربع QR مع التصميم المحسّن"""
        
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
        label_color = element_config.get('label_color', Color(0.6, 0.6, 0.6))
        
        self.canvas.setFont('Helvetica', label_font_size)
        self.canvas.setFillColor(label_color)
        
        center_x = abs_x + width / 2
        center_y = abs_y + height / 2
        self.canvas.drawCentredString(center_x, center_y, label)
    
    def draw_birth_date_box(self, card_x: float, card_y: float, element_config: Dict, birthdate: str = ''):
        """رسم خانة تاريخ الميلاد مع التصميم المحسّن"""
        
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
        if birthdate:
            # إذا كان تاريخ الميلاد متوفراً، اعرضه
            label = f"تاريخ الميلاد: {birthdate}"
        else:
            # إذا لم يكن متوفراً، اعرض خانة فارغة
            label = element_config.get('label', 'تاريخ الميلاد: _______________')
            
        label_font_size = element_config.get('label_font_size', 6)
        label_x = element_config.get('label_x', 0.1)
        label_y = element_config.get('label_y', 0.18)
        label_color = element_config.get('label_color', black)
        
        # استخدام الخط العربي إذا كان متوفراً
        font_name = getattr(self, 'arabic_font', 'Helvetica')
        
        self.canvas.setFont(font_name, label_font_size)
        self.canvas.setFillColor(label_color)
        
        # تشكيل النص العربي
        shaped_label = self.reshape_arabic_text(label)
        
        text_x = card_x + label_x * ID_WIDTH
        text_y = card_y + label_y * ID_HEIGHT
        self.canvas.drawString(text_x, text_y, shaped_label)
    
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
        self.canvas.drawCentredString(A4_WIDTH / 2, 10, info_text)
    
    def fit_text_to_width_simple(self, shaped_text: str, font_name: str, 
                                font_size: float, max_width: float) -> str:
        """تقليص النص المُشكل ليناسب العرض المحدد بدون إعادة تشكيل"""
        
        try:
            text_width = self.canvas.stringWidth(shaped_text, font_name, font_size)
            
            if text_width <= max_width:
                return shaped_text
            
            # إذا كان النص طويلاً جداً، نحاول تقليصه بحذف أحرف من النهاية
            # نحتاج لحساب طول النص الأصلي قبل التشكيل للقطع الصحيح
            original_length = len(shaped_text)
            
            # محاولة تقليص تدريجي
            for i in range(original_length - 1, max(0, original_length // 2), -1):
                if i <= 0:
                    break
                    
                # قطع النص وإضافة نقاط
                truncated = shaped_text[:i] + "..."
                test_width = self.canvas.stringWidth(truncated, font_name, font_size)
                
                if test_width <= max_width:
                    return truncated
            
            # إذا لم ننجح، إرجاع جزء صغير مع نقاط
            return shaped_text[:max(1, len(shaped_text)//3)] + "..."
            
        except Exception as e:
            logging.error(f"خطأ في ملائمة النص للعرض: {e}")
            return shaped_text

    def fit_text_to_width(self, text: str, font_name: str, 
                         font_size: float, max_width: float) -> str:
        """تقليص النص ليناسب العرض المحدد مع دعم العربية (للاستخدام الخارجي)"""
        
        try:
            # قياس النص بعد إعادة تشكيله
            shaped_text = self.reshape_arabic_text(text)
            return self.fit_text_to_width_simple(shaped_text, font_name, font_size, max_width)
            
        except:
            # في حالة الخطأ، إرجاع النص مُشكل بالعربية على الأقل
            return self.reshape_arabic_text(text)


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


def generate_single_student_id_preview(student_data: Dict,
                                     output_path: str,
                                     school_name: str = "",
                                     custom_title: str = "هوية طالب") -> bool:
    """
    إنشاء معاينة لهوية طالب واحد لأغراض التصميم والاختبار
    
    Args:
        student_data: بيانات طالب واحد
        output_path: مسار ملف PDF للمعاينة
        school_name: اسم المدرسة
        custom_title: عنوان مخصص للهوية
    
    Returns:
        True إذا تم الإنشاء بنجاح، False في حالة الخطأ
    """
    
    try:
        generator = StudentIDGenerator()
        
        # إنشاء canvas
        generator.canvas = canvas.Canvas(output_path, pagesize=A4)
        
        # إعداد معلومات المستند
        generator.canvas.setCreator("نظام حسابات المدارس الأهلية")
        generator.canvas.setTitle(f"معاينة هوية - {student_data.get('name', 'طالب')}")
        generator.canvas.setSubject("معاينة هوية طالب")
        
        # رسم هوية واحدة في وسط الصفحة
        card_x = (A4_WIDTH - ID_WIDTH) / 2
        card_y = (A4_HEIGHT - ID_HEIGHT) / 2
        
        generator.draw_student_card(student_data, card_x, card_y, school_name, custom_title)
        
        # إضافة معلومات المعاينة
        generator.canvas.setFont('Helvetica', 8)
        generator.canvas.setFillColor(Color(0.5, 0.5, 0.5))
        preview_info = f"معاينة هوية الطالب - {datetime.now().strftime('%Y/%m/%d %H:%M')}"
        generator.canvas.drawCentredString(A4_WIDTH / 2, 50, preview_info)
        
        # حفظ PDF
        generator.canvas.save()
        logging.info(f"تم حفظ معاينة الهوية: {output_path}")
        return True
        
    except Exception as e:
        logging.error(f"خطأ في إنشاء معاينة الهوية: {e}")
        return False


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
