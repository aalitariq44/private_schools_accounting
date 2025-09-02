#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعدادات محسّنة للطباعة والجودة
"""

from reportlab.lib.units import mm
from reportlab.lib.colors import Color, black, white, blue, red, green
from core.utils.settings_manager import get_academic_year

# إعدادات الجودة والطباعة
PRINT_SETTINGS = {
    # دقة الطباعة
    "dpi": 300,  # نقطة لكل بوصة
    "quality": "high",  # high, medium, low
    
    # إعدادات الألوان
    "color_mode": "rgb",  # rgb, cmyk
    "color_profile": "sRGB",
    
    # إعدادات الخط
    "font_smoothing": True,
    "font_hinting": True,
    
    # إعدادات الصفحة
    "page_orientation": "portrait",
    "page_size": "A4",
    "margins_bleed": 2 * mm / 10,  # هامش إضافي للقطع
}

# إعدادات محسّنة للعناصر
ENHANCED_ELEMENTS = {
    # تحسينات اسم المدرسة
    "school_name_enhanced": {
        "shadow": True,
        "shadow_color": Color(0.8, 0.8, 0.8),
        "shadow_offset": (1, -1),
        "gradient": False,
        "gradient_colors": [Color(0.2, 0.3, 0.7), Color(0.1, 0.2, 0.5)]
    },
    
    # تحسينات مربع الصورة
    "photo_box_enhanced": {
        "corner_radius": 2,  # زوايا مدورة
        "inner_border": True,
        "inner_border_color": Color(0.9, 0.9, 0.9),
        "inner_border_width": 0.5,
        "placeholder_pattern": "dots"  # dots, lines, grid
    },
    
    # تحسينات QR
    "qr_enhanced": {
        "actual_qr": False,  # سيتم تفعيلها لاحقاً
        "qr_data_template": "student_{id}_{year}",
        "qr_error_correction": "M",  # L, M, Q, H
        "qr_border": 2
    },
    
    # تحسينات خانة الميلاد
    "birth_date_enhanced": {
        "date_format": "DD/MM/YYYY",
        "separator_style": "line",  # line, dots, boxes
        "guide_text": True
    }
}

# أنماط مختلفة للهويات
ID_STYLES = {
    "default": {
        "name": "النمط الافتراضي",
        "description": "نمط بسيط ووضح للاستخدام العام",
        "primary_color": Color(0.2, 0.3, 0.7),
        "secondary_color": Color(0.5, 0.5, 0.5),
        "accent_color": Color(0.9, 0.1, 0.1)
    },
    
    "elegant": {
        "name": "النمط الأنيق",
        "description": "نمط راقي للمدارس المتميزة",
        "primary_color": Color(0.1, 0.2, 0.4),
        "secondary_color": Color(0.6, 0.6, 0.6),
        "accent_color": Color(0.8, 0.6, 0.1)
    },
    
    "modern": {
        "name": "النمط العصري",
        "description": "نمط حديث وجريء",
        "primary_color": Color(0.2, 0.7, 0.4),
        "secondary_color": Color(0.4, 0.4, 0.4),
        "accent_color": Color(0.2, 0.8, 0.9)
    },
    
    "classic": {
        "name": "النمط الكلاسيكي",
        "description": "نمط تقليدي ومحافظ",
        "primary_color": Color(0.3, 0.2, 0.1),
        "secondary_color": Color(0.7, 0.7, 0.7),
        "accent_color": Color(0.6, 0.2, 0.2)
    }
}

# إعدادات التحقق من الجودة
QUALITY_CHECKS = {
    "text_readability": {
        "min_font_size": 6,
        "min_contrast_ratio": 3.0,
        "max_text_width_ratio": 0.9
    },
    
    "layout_validation": {
        "min_element_spacing": 2,  # بكسل
        "max_overlap_tolerance": 1,  # بكسل
        "boundary_check": True
    },
    
    "print_validation": {
        "check_bleed_area": True,
        "validate_colors": True,
        "check_resolution": True
    }
}

# إعدادات النصوص القابلة للتخصيص
CUSTOMIZABLE_TEXTS = {
    "school_name": {
        "default": "اسم المدرسة",
        "placeholder": "أدخل اسم المدرسة",
        "max_length": 50,
        "required": True
    },
    
    "id_title": {
        "default": "هوية طالب",
        "alternatives": [
            "هوية طالب",
            "بطاقة طالب",
            "هوية تعريف",
            "Student ID"
        ],
        "custom_allowed": True
    },
    
    "academic_year": {
        "default": get_academic_year(),
        "format": "YYYY - YYYY",
        "auto_generate": True
    },
    
    "birth_date_label": {
        "default": "تاريخ الميلاد:",
        "alternatives": [
            "تاريخ الميلاد:",
            "المواليد:",
            "تاريخ الولادة:",
            "Date of Birth:"
        ]
    }
}

# مقاسات بديلة للهويات
ALTERNATIVE_SIZES = {
    "iso_id1": {
        "name": "ISO ID-1 (ماستر كارد)",
        "width_mm": 85.60,
        "height_mm": 53.98,
        "description": "الحجم القياسي العالمي للبطاقات"
    },
    
    "business_card": {
        "name": "بطاقة أعمال",
        "width_mm": 90.0,
        "height_mm": 55.0,
        "description": "حجم بطاقة الأعمال الشائع"
    },
    
    "custom_small": {
        "name": "مخصص صغير",
        "width_mm": 80.0,
        "height_mm": 50.0,
        "description": "حجم مخصص أصغر لتوفير الورق"
    },
    
    "custom_large": {
        "name": "مخصص كبير",
        "width_mm": 95.0,
        "height_mm": 60.0,
        "description": "حجم مخصص أكبر للمزيد من المعلومات"
    }
}

# تخطيطات بديلة للصفحة
PAGE_LAYOUTS = {
    "2x5": {
        "name": "2×5 (10 هويات)",
        "cols": 2,
        "rows": 5,
        "total": 10,
        "description": "التخطيط الافتراضي المحسّن"
    },
    
    "3x3": {
        "name": "3×3 (9 هويات)",
        "cols": 3,
        "rows": 3,
        "total": 9,
        "description": "تخطيط مربع متوازن"
    },
    
    "1x8": {
        "name": "1×8 (8 هويات)",
        "cols": 1,
        "rows": 8,
        "total": 8,
        "description": "تخطيط عمودي للهويات الكبيرة"
    },
    
    "4x2": {
        "name": "4×2 (8 هويات)",
        "cols": 4,
        "rows": 2,
        "total": 8,
        "description": "تخطيط أفقي للهويات الصغيرة"
    }
}

def get_enhanced_template(style_name="default", size_name="iso_id1", layout_name="2x5"):
    """
    إنشاء قالب محسّن بناء على الإعدادات المختارة
    
    Args:
        style_name: اسم النمط من ID_STYLES
        size_name: اسم المقاس من ALTERNATIVE_SIZES  
        layout_name: اسم التخطيط من PAGE_LAYOUTS
    
    Returns:
        dict: قالب محسّن جاهز للاستخدام
    """
    
    style = ID_STYLES.get(style_name, ID_STYLES["default"])
    size = ALTERNATIVE_SIZES.get(size_name, ALTERNATIVE_SIZES["iso_id1"])
    layout = PAGE_LAYOUTS.get(layout_name, PAGE_LAYOUTS["2x5"])
    
    enhanced_template = {
        "metadata": {
            "style": style_name,
            "size": size_name,
            "layout": layout_name,
            "created_with": "Enhanced Template Generator v1.0"
        },
        
        "dimensions": {
            "width_mm": size["width_mm"],
            "height_mm": size["height_mm"],
            "width_pt": size["width_mm"] * mm / 10,
            "height_pt": size["height_mm"] * mm / 10
        },
        
        "grid": {
            "cols": layout["cols"],
            "rows": layout["rows"],
            "total_per_page": layout["total"]
        },
        
        "colors": {
            "primary": style["primary_color"],
            "secondary": style["secondary_color"],
            "accent": style["accent_color"]
        },
        
        "print_settings": PRINT_SETTINGS.copy(),
        "quality_checks": QUALITY_CHECKS.copy(),
        "enhanced_features": ENHANCED_ELEMENTS.copy()
    }
    
    return enhanced_template

def validate_template_quality(template_elements):
    """
    التحقق من جودة القالب وإرجاع تقرير
    
    Args:
        template_elements: عناصر القالب للفحص
    
    Returns:
        dict: تقرير الجودة مع المشاكل والاقتراحات
    """
    
    issues = []
    suggestions = []
    warnings = []
    
    # فحص أحجام الخطوط
    for element_name, element in template_elements.items():
        if 'font_size' in element:
            font_size = element['font_size']
            min_size = QUALITY_CHECKS["text_readability"]["min_font_size"]
            
            if font_size < min_size:
                issues.append(f"حجم خط {element_name} صغير جداً ({font_size})")
                suggestions.append(f"زيادة حجم خط {element_name} إلى {min_size} على الأقل")
    
    # فحص التداخلات
    positions = []
    for element_name, element in template_elements.items():
        if 'x' in element and 'y' in element:
            positions.append({
                'name': element_name,
                'x': element['x'],
                'y': element['y'],
                'width': element.get('width', 0.1),
                'height': element.get('height', 0.1)
            })
    
    # فحص التداخل البسيط
    for i, pos1 in enumerate(positions):
        for j, pos2 in enumerate(positions[i+1:], i+1):
            if (abs(pos1['x'] - pos2['x']) < 0.1 and 
                abs(pos1['y'] - pos2['y']) < 0.1):
                warnings.append(f"تداخل محتمل بين {pos1['name']} و {pos2['name']}")
    
    # فحص الحدود
    for element_name, element in template_elements.items():
        if 'x' in element and 'y' in element:
            x, y = element['x'], element['y']
            width = element.get('width', 0)
            height = element.get('height', 0)
            
            if x + width > 1.0 or y + height > 1.0:
                issues.append(f"العنصر {element_name} يتجاوز حدود البطاقة")
            
            if x < 0 or y < 0:
                issues.append(f"العنصر {element_name} خارج حدود البطاقة")
    
    return {
        "status": "error" if issues else "warning" if warnings else "good",
        "issues": issues,
        "warnings": warnings,
        "suggestions": suggestions,
        "score": max(0, 100 - len(issues) * 20 - len(warnings) * 5)
    }

# دالة مساعدة لحساب المواقع التلقائية
def auto_layout_elements(elements_list, card_width=1.0, card_height=1.0):
    """
    حساب مواقع تلقائية متوازنة للعناصر
    
    Args:
        elements_list: قائمة أسماء العناصر
        card_width: عرض البطاقة (نسبي)
        card_height: ارتفاع البطاقة (نسبي)
    
    Returns:
        dict: مواقع محسوبة للعناصر
    """
    
    auto_positions = {}
    y_positions = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    
    for i, element_name in enumerate(elements_list):
        if i < len(y_positions):
            auto_positions[element_name] = {
                "x": 0.5,  # وسط البطاقة
                "y": y_positions[i],
                "alignment": "center"
            }
    
    return auto_positions
