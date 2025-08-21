#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
قالب هوية الطالب القابل للتعديل
إحداثيات العناصر وأحجام الخطوط للهوية الطلابية
"""

from reportlab.lib.units import mm
from reportlab.lib.colors import Color, black, white

# أبعاد الهوية (ISO ID-1 - حجم بطاقة ماستر كارد)
# 85.60 × 53.98 مم = 242.646 × 153.014 نقطة
ID_WIDTH = 85.60 * mm  # تحويل إلى نقاط ReportLab
ID_HEIGHT = 53.98 * mm  # تحويل إلى نقاط ReportLab

# أبعاد صفحة A4
A4_WIDTH = 210 * mm
A4_HEIGHT = 297 * mm

# تخطيط الشبكة على صفحة A4 (2 عمود × 5 صفوف = 10 هويات)
GRID_COLS = 2
GRID_ROWS = 5

# هوامش الصفحة
PAGE_MARGIN_X = 15 * mm
PAGE_MARGIN_Y = 20 * mm

# مسافات بين البطاقات
CARD_SPACING_X = 10 * mm
CARD_SPACING_Y = 8 * mm

# قالب العناصر داخل الهوية (إحداثيات نسبية من 0 إلى 1)
TEMPLATE_ELEMENTS = {
    # اسم المدرسة ونص "هوية طالب" في الأعلى (محاذاة إلى اليمين)
    "school_name": {
        "x": 0.96,         # يمين البطاقة
        "y": 0.90,         # في الأعلى
        "font_size": 9,
        "font_name": "Helvetica-Bold",
        "alignment": "right",
        "color": black,
        "max_width": 0.95   # 95% من عرض البطاقة
    },
    
    "id_title": {
        "x": 0.96,         # يمين البطاقة
        "y": 0.82,
        "font_size": 7,
        "font_name": "Helvetica",
        "alignment": "right",
        "color": black,
        "text": "هوية طالب"
    },
    
    # اسم الطالب
    "student_name": {
        "x": 0.96,         # بجانب مربع الصورة من اليمين
        "y": 0.68,
        "font_size": 10,
        "font_name": "Helvetica-Bold",
        "alignment": "right",
        "color": black,
        "max_width": 0.52  # المساحة المتبقية بعد مربع الصورة
    },
    
    # صف الطالب
    "student_grade": {
        "x": 0.96,
        "y": 0.58,
        "font_size": 8,
        "font_name": "Helvetica",
        "alignment": "right",
        "color": black,
        "label": "الصف: "
    },
    
    # العام الدراسي
    "academic_year": {
        "x": 0.96,
        "y": 0.48,
        "font_size": 7,
        "font_name": "Helvetica",
        "alignment": "right",
        "color": black,
        "text": "العام الدراسي: 2025 - 2026"
    },
    
    # مربع الصورة (فارغ للتركيب اليدوي)
    "photo_box": {
        "x": 0.04,
        "y": 0.40,
        "width": 0.30,
        "height": 0.54,
        "border_color": black,
        "border_width": 1.5,
        "fill_color": white,
        "label": "صورة",
        "label_font_size": 7
    },
    
    # مربع QR (مؤقت)
    "qr_box": {
        "x": 0.76,
        "y": 0.10,
        "width": 0.20,
        "height": 0.25,
        "border_color": black,
        "border_width": 1,
        "fill_color": white,
        "label": "QR",
        "label_font_size": 5
    },
    
    # خانة المواليد (فارغة للكتابة اليدوية)
    "birth_date_box": {
        "x": 0.04,
        "y": 0.10,
        "width": 0.65,
        "height": 0.25,
        "border_color": black,
        "border_width": 0.5,
        "fill_color": white,
        "label": "تاريخ الميلاد: _______________",
        "label_font_size": 7,
        "label_x": 0.06,
        "label_y": 0.20
    },
    # إضافة نص 'تاريخ الميلاد' يمين المربع
    "birth_date_label": {
        "x": 0.71,             # بعد طرف المربع
        "y": 0.15,             # على مستوى نص التاريخ
        "font_size": 7,
        "font_name": "Helvetica",
        "alignment": "left",
        "color": black,
        "text": "تاريخ الميلاد"
    }
}

# إعدادات علامات القطع
CUT_MARKS = {
    "enabled": True,
    "length": 3 * mm,
    "color": Color(0.7, 0.7, 0.7),  # رمادي فاتح
    "width": 0.5
}

# إعدادات الخطوط
FONTS = {
    "arabic": "Helvetica",  # سيتم استبدالها بخط عربي إذا توفر
    "default": "Helvetica"
}

# ألوان افتراضية
COLORS = {
    "primary": Color(0.2, 0.3, 0.7),      # أزرق داكن
    "secondary": Color(0.5, 0.5, 0.5),    # رمادي
    "accent": Color(0.9, 0.1, 0.1),       # أحمر
    "text": black,
    "background": white,
    "border": black
}

def get_card_position(row, col):
    """حساب موقع البطاقة في الشبكة"""
    x = PAGE_MARGIN_X + col * (ID_WIDTH + CARD_SPACING_X)
    y = A4_HEIGHT - PAGE_MARGIN_Y - (row + 1) * (ID_HEIGHT + CARD_SPACING_Y)
    return x, y

def get_element_absolute_position(element_config, card_x, card_y):
    """تحويل الإحداثيات النسبية إلى مطلقة"""
    abs_x = card_x + element_config["x"] * ID_WIDTH
    abs_y = card_y + element_config["y"] * ID_HEIGHT
    return abs_x, abs_y

def get_element_absolute_size(element_config):
    """تحويل الأحجام النسبية إلى مطلقة"""
    if "width" in element_config and "height" in element_config:
        abs_width = element_config["width"] * ID_WIDTH
        abs_height = element_config["height"] * ID_HEIGHT
        return abs_width, abs_height
    return None, None

# دالة لحفظ القالب كملف JSON (للتخصيص المستقبلي)
def save_template_as_json(filepath):
    """حفظ القالب كملف JSON للتعديل"""
    import json
    
    # تحويل الألوان إلى قوائم للتسلسل
    def color_to_list(color):
        if hasattr(color, 'rgb'):
            return [color.red, color.green, color.blue]
        elif color == black:
            return [0, 0, 0]
        elif color == white:
            return [1, 1, 1]
        else:
            return [0, 0, 0]  # افتراضي
    
    # نسخ TEMPLATE_ELEMENTS وتحويل الألوان
    elements_json = {}
    for key, element in TEMPLATE_ELEMENTS.items():
        element_copy = element.copy()
        if 'color' in element_copy:
            element_copy['color'] = color_to_list(element_copy['color'])
        if 'border_color' in element_copy:
            element_copy['border_color'] = color_to_list(element_copy['border_color'])
        if 'fill_color' in element_copy:
            element_copy['fill_color'] = color_to_list(element_copy['fill_color'])
        elements_json[key] = element_copy
    
    # نسخ CUT_MARKS وتحويل الألوان
    cut_marks_json = CUT_MARKS.copy()
    if 'color' in cut_marks_json:
        cut_marks_json['color'] = color_to_list(cut_marks_json['color'])
    
    template_data = {
        "id_dimensions": {
            "width_mm": 85.60,
            "height_mm": 53.98
        },
        "grid_layout": {
            "cols": GRID_COLS,
            "rows": GRID_ROWS
        },
        "margins": {
            "page_margin_x_mm": 15,
            "page_margin_y_mm": 20,
            "card_spacing_x_mm": 10,
            "card_spacing_y_mm": 8
        },
        "elements": elements_json,
        "cut_marks": cut_marks_json,
        "colors": {
            "primary": [0.2, 0.3, 0.7],
            "secondary": [0.5, 0.5, 0.5],
            "accent": [0.9, 0.1, 0.1],
            "text": [0, 0, 0],
            "background": [1, 1, 1],
            "border": [0, 0, 0]
        }
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(template_data, f, ensure_ascii=False, indent=2)

def load_template_from_json(filepath):
    """تحميل القالب من ملف JSON"""
    import json
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        # تحديث المتغيرات العامة
        global TEMPLATE_ELEMENTS, CUT_MARKS, GRID_COLS, GRID_ROWS
        global ID_WIDTH, ID_HEIGHT, A4_WIDTH, A4_HEIGHT
        global PAGE_MARGIN_X, PAGE_MARGIN_Y, CARD_SPACING_X, CARD_SPACING_Y
        
        TEMPLATE_ELEMENTS = template_data.get("elements", TEMPLATE_ELEMENTS)
        CUT_MARKS = template_data.get("cut_marks", CUT_MARKS)
        
        grid_layout = template_data.get("grid_layout", {})
        GRID_COLS = grid_layout.get("cols", GRID_COLS)
        GRID_ROWS = grid_layout.get("rows", GRID_ROWS)
        
        # تحديث الأبعاد إذا كانت متوفرة
        dimensions = template_data.get("id_dimensions", {})
        if "width_mm" in dimensions:
            ID_WIDTH = dimensions["width_mm"] * mm
        if "height_mm" in dimensions:
            ID_HEIGHT = dimensions["height_mm"] * mm
        
        margins = template_data.get("margins", {})
        if "page_margin_x_mm" in margins:
            PAGE_MARGIN_X = margins["page_margin_x_mm"] * mm
        if "page_margin_y_mm" in margins:
            PAGE_MARGIN_Y = margins["page_margin_y_mm"] * mm
        if "card_spacing_x_mm" in margins:
            CARD_SPACING_X = margins["card_spacing_x_mm"] * mm
        if "card_spacing_y_mm" in margins:
            CARD_SPACING_Y = margins["card_spacing_y_mm"] * mm
        
        return True
    except Exception as e:
        print(f"خطأ في تحميل القالب: {e}")
        return False

# حفظ القالب الافتراضي عند أول تشغيل
def ensure_default_template():
    """التأكد من وجود ملف القالب الافتراضي"""
    from pathlib import Path
    
    template_dir = Path(__file__).parent
    template_file = template_dir / "id_template.json"
    
    if not template_file.exists():
        save_template_as_json(template_file)
        print(f"تم إنشاء ملف القالب الافتراضي: {template_file}")
