#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
قالب هوية الطالب القابل للتعديل
إحداثيات العناصر وأحجام الخطوط للهوية الطلابية
"""

from reportlab.lib.units import mm
from reportlab.lib.colors import Color, black, white
from core.utils.settings_manager import get_academic_year

# أبعاد الهوية (ISO ID-1 - حجم بطاقة ماستر كارد)
# 85.60 × 53.98 مم = 242.646 × 153.014 نقطة
ID_WIDTH = 85.60 * mm  # تحويل إلى نقاط ReportLab
ID_HEIGHT = 53.98 * mm  # تحويل إلى نقاط ReportLab

# أبعاد صفحة A4
A4_WIDTH = 210 * mm
A4_HEIGHT = 297 * mm

# تخطيط الشبكة على صفحة A4 (2 عمود × 4 صفوف = 8 هويات)
# تم تقليل الصفوف من 5 إلى 4 لضمان دخول جميع البطاقات في الصفحة
GRID_COLS = 2
GRID_ROWS = 4

# هوامش الصفحة
PAGE_MARGIN_X = 15 * mm  # هامش جانبي معقول
PAGE_MARGIN_Y = 20 * mm  # هامش علوي وسفلي معقول

# مسافات بين البطاقات  
CARD_SPACING_X = 8 * mm   # مسافة أفقية كافية للقطع
CARD_SPACING_Y = 10 * mm  # مسافة عمودية كافية للقطع

# قالب العناصر داخل الهوية (إحداثيات نسبية من 0 إلى 1)
# تصميم مبسط وعصري أكثر أناقة
TEMPLATE_ELEMENTS = {
    # عنوان "هوية طالب" في الأعلى - بسيط وأنيق
    "id_title": {
        "x": 0.5,          # في الوسط
        "y": 0.92,         # في أعلى البطاقة
        "font_size": 16,   # خط أكبر قليلاً
        "font_name": "Helvetica-Bold",
        "alignment": "center",
        "color": Color(0.2, 0.4, 0.7),  # أزرق هادئ
        "text": "هوية طالب"
    },
    
    # اسم المدرسة تحت العنوان - مبسط
    "school_name": {
        "x": 0.5,          # في الوسط
        "y": 0.84,         # تحت العنوان
        "font_size": 11,   # خط متوسط
        "font_name": "Helvetica",
        "alignment": "center",
        "color": Color(0.3, 0.3, 0.3),  # رمادي هادئ
        "max_width": 0.95
    },
    
    # خط فاصل بسيط وأنيق
    "header_line": {
        "x": 0.1,
        "y": 0.78,
        "width": 0.8,
        "height": 0.008,
        "color": Color(0.2, 0.4, 0.7),
        "type": "line"
    },
    
    # مربع الصورة - تصميم نظيف
    "photo_box": {
        "x": 0.05,
        "y": 0.45,
        "width": 0.25,
        "height": 0.45,
        "border_color": Color(0.6, 0.6, 0.6),  # رمادي فاتح
        "border_width": 1.5,
        "fill_color": Color(0.97, 0.97, 0.97),  # خلفية بيضاء تقريباً
        "label": "الصورة",
        "label_font_size": 8,
        "label_color": Color(0.5, 0.5, 0.5)
    },
    
    # اسم الطالب - بدون تسمية منفصلة لتبسيط التصميم
    "student_name": {
        "x": 0.95,         # من اليمين
        "y": 0.68,         # في النصف العلوي
        "font_size": 14,   # خط بارز
        "font_name": "Helvetica-Bold",
        "alignment": "right",
        "color": Color(0.1, 0.1, 0.1),  # أسود تقريباً
        "max_width": 0.65  # المساحة المتبقية بعد الصورة
    },
    
    # الصف الدراسي - مع أيقونة بسيطة
    "student_grade": {
        "x": 0.95,
        "y": 0.58,
        "font_size": 11,
        "font_name": "Helvetica",
        "alignment": "right",
        "color": Color(0.2, 0.4, 0.7),
        "label": "الصف: "
    },
    
    # العام الدراسي - مبسط
    "academic_year": {
        "x": 0.95,
        "y": 0.48,
        "font_size": 10,
        "font_name": "Helvetica",
        "alignment": "right",
        "color": Color(0.4, 0.4, 0.4),
        "text": get_academic_year()
    },
    
    # تاريخ الميلاد - تصميم مبسط
    "birth_date_box": {
        "x": 0.35,
        "y": 0.15,
        "width": 0.6,
        "height": 0.2,
        "border_color": Color(0.8, 0.8, 0.8),
        "border_width": 1,
        "fill_color": Color(0.99, 0.99, 0.99),
        "label": "التاريخ: __ / __ / ____",
        "label_font_size": 9,
        "label_x": 0.37,
        "label_y": 0.2,
        "label_color": Color(0.5, 0.5, 0.5)
    },
    
    # مربع QR - أصغر وأنيق
    "qr_box": {
        "x": 0.05,
        "y": 0.05,
        "width": 0.25,
        "height": 0.3,
        "border_color": Color(0.7, 0.7, 0.7),
        "border_width": 1,
        "fill_color": white,
        "label": "QR",
        "label_font_size": 8,
        "label_color": Color(0.6, 0.6, 0.6)
    },
    
    # رقم الطالب - بسيط في الزاوية
    "id_number": {
        "x": 0.95,
        "y": 0.1,
        "font_size": 8,
        "font_name": "Helvetica",
        "alignment": "right",
        "color": Color(0.6, 0.6, 0.6),
        "text": "ID: AUTO"
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

# ألوان حديثة وأنيقة
COLORS = {
    "primary": Color(0.2, 0.4, 0.7),        # أزرق هادئ
    "secondary": Color(0.4, 0.4, 0.4),      # رمادي متوسط
    "accent": Color(0.0, 0.6, 0.5),         # تركوازي أنيق
    "text": Color(0.1, 0.1, 0.1),           # أسود ناعم
    "background": white,
    "border": Color(0.6, 0.6, 0.6),        # رمادي فاتح للحدود
    "light_gray": Color(0.95, 0.95, 0.95), # رمادي فاتح جداً
    "medium_gray": Color(0.5, 0.5, 0.5)    # رمادي متوسط
}

def get_card_position(row, col):
    """حساب موقع البطاقة في الشبكة"""
    x = PAGE_MARGIN_X + col * (ID_WIDTH + CARD_SPACING_X)
    # تصحيح حساب الموقع Y لتجنب خروج البطاقات من الصفحة
    y = A4_HEIGHT - PAGE_MARGIN_Y - row * (ID_HEIGHT + CARD_SPACING_Y) - ID_HEIGHT
    return x, y

def verify_layout_fits():
    """التحقق من أن التخطيط يتسع في صفحة A4"""
    # حساب المساحة المطلوبة
    total_width = PAGE_MARGIN_X * 2 + GRID_COLS * ID_WIDTH + (GRID_COLS - 1) * CARD_SPACING_X
    total_height = PAGE_MARGIN_Y * 2 + GRID_ROWS * ID_HEIGHT + (GRID_ROWS - 1) * CARD_SPACING_Y
    
    width_fits = total_width <= A4_WIDTH
    height_fits = total_height <= A4_HEIGHT
    
    return {
        'width_fits': width_fits,
        'height_fits': height_fits,
        'total_width': total_width,
        'total_height': total_height,
        'a4_width': A4_WIDTH,
        'a4_height': A4_HEIGHT,
        'width_margin': A4_WIDTH - total_width,
        'height_margin': A4_HEIGHT - total_height
    }

def get_optimized_layout():
    """حساب تخطيط محسّن يضمن وضع جميع البطاقات ضمن الصفحة"""
    verification = verify_layout_fits()
    
    if not verification['width_fits'] or not verification['height_fits']:
        # إذا كان التخطيط لا يتسع، نحسب هوامش ومسافات جديدة
        available_width = A4_WIDTH
        available_height = A4_HEIGHT
        
        # حساب الهوامش والمسافات المثلى
        min_margin = 10 * mm  # حد أدنى للهامش
        
        # للعرض
        remaining_width = available_width - 2 * min_margin - GRID_COLS * ID_WIDTH
        optimal_spacing_x = remaining_width / (GRID_COLS - 1) if GRID_COLS > 1 else 0
        
        # للارتفاع
        remaining_height = available_height - 2 * min_margin - GRID_ROWS * ID_HEIGHT
        optimal_spacing_y = remaining_height / (GRID_ROWS - 1) if GRID_ROWS > 1 else 0
        
        return {
            'page_margin_x': min_margin,
            'page_margin_y': min_margin,
            'card_spacing_x': max(optimal_spacing_x, 3 * mm),  # حد أدنى 3mm
            'card_spacing_y': max(optimal_spacing_y, 3 * mm)   # حد أدنى 3mm
        }
    
    return None  # التخطيط الحالي مناسب

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
