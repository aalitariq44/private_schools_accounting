#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعدادات خاصة لـ Windows Scale 150%
"""

# إعدادات الخطوط لـ Scale 150%
SCALE_150_FONT_SIZES = {
    "base_font": 11,        # بدلاً من 14
    "title_font": 18,       # بدلاً من 24  
    "button_font": 13,      # بدلاً من 16
    "header_font": 16,      # بدلاً من 22
    "small_font": 10        # بدلاً من 12
}

# إعدادات الأحجام لـ Scale 150%
SCALE_150_SIZES = {
    "sidebar_width": 200,   # بدلاً من 280
    "button_height": 35,    # بدلاً من 45
    "padding": 8,           # بدلاً من 10
    "margin": 10,           # بدلاً من 15
    "border_radius": 4      # بدلاً من 6
}

# إعدادات النافذة لـ Scale 150%
SCALE_150_WINDOW = {
    "min_width": 900,       # بدلاً من 1000
    "min_height": 600,      # بدلاً من 700
    "default_width": 1200,  # حجم افتراضي مناسب
    "default_height": 800
}

def get_scale_150_settings():
    """الحصول على إعدادات Scale 150%"""
    return {
        "fonts": SCALE_150_FONT_SIZES,
        "sizes": SCALE_150_SIZES,
        "window": SCALE_150_WINDOW
    }
