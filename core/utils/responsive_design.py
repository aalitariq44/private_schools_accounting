#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أدوات التصميم المتجاوب لدعم أحجام الشاشات المختلفة
"""

import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSize


class ResponsiveDesign:
    """فئة إدارة التصميم المتجاوب"""
    
    def __init__(self):
        try:
            # تأكد من وجود QApplication
            app = QApplication.instance()
            if app is None:
                # إنشاء تطبيق مؤقت إذا لم يكن موجوداً
                app = QApplication([])
                self._temp_app = app
            else:
                self._temp_app = None
                
            self.screen = app.primaryScreen()
            if self.screen is None:
                # في حالة عدم وجود شاشة، استخدم قيم افتراضية
                self.screen_geometry = type('Geometry', (), {
                    'width': lambda: 1920,
                    'height': lambda: 1080
                })()
                self.dpi = 96.0
            else:
                self.screen_geometry = self.screen.geometry()
                self.dpi = self.screen.logicalDotsPerInch()
                
        except Exception:
            # قيم افتراضية في حالة فشل الكشف
            self.screen_geometry = type('Geometry', (), {
                'width': lambda: 1920,
                'height': lambda: 1080
            })()
            self.dpi = 96.0
            self._temp_app = None
        
        self.dpi_scale = self.dpi / 96.0
        
        # تحديد نوع الشاشة
        self.is_small_screen = self.screen_geometry.width() < 1366 or self.dpi_scale > 1.25
        self.is_high_dpi = self.dpi_scale > 1.0
        
        logging.info(f"معلومات الشاشة: {self.screen_geometry.width()}x{self.screen_geometry.height()}, DPI: {self.dpi:.1f}, Scale: {self.dpi_scale:.2f}")
    
    def get_scaled_size(self, base_size: int) -> int:
        """حساب الحجم المقيس بناءً على DPI"""
        return max(base_size, int(base_size * self.dpi_scale))
    
    def get_font_size(self, base_size: int) -> int:
        """حساب حجم الخط المناسب"""
        if self.is_small_screen:
            # تقليل حجم الخط قليلاً للشاشات الصغيرة
            return max(base_size - 1, int(base_size * min(self.dpi_scale, 1.2)))
        else:
            return max(base_size, int(base_size * self.dpi_scale))
    
    def get_window_size(self, min_width: int, min_height: int) -> tuple:
        """حساب حجم النافذة المناسب"""
        # حساب الحد الأدنى بناءً على حجم الشاشة
        screen_width = self.screen_geometry.width()
        screen_height = self.screen_geometry.height()
        
        # للشاشات الصغيرة، استخدم نسبة أكبر من الشاشة
        if self.is_small_screen:
            width_ratio = 0.9
            height_ratio = 0.85
        else:
            width_ratio = 0.8
            height_ratio = 0.8
        
        preferred_width = int(screen_width * width_ratio)
        preferred_height = int(screen_height * height_ratio)
        
        # التأكد من عدم النزول تحت الحد الأدنى
        final_width = max(min_width, preferred_width)
        final_height = max(min_height, preferred_height)
        
        return final_width, final_height
    
    def get_sidebar_width(self, base_width: int) -> int:
        """حساب عرض الشريط الجانبي"""
        if self.is_small_screen:
            # تقليل عرض الشريط الجانبي للشاشات الصغيرة
            return max(200, min(base_width, int(base_width * 0.85)))
        else:
            return max(base_width, int(base_width * self.dpi_scale))
    
    def get_button_height(self, base_height: int) -> int:
        """حساب ارتفاع الأزرار"""
        scaled_height = int(base_height * self.dpi_scale)
        return max(30, min(scaled_height, 65))  # حد أدنى وأقصى للارتفاع
    
    def get_padding(self, base_padding: int) -> int:
        """حساب المساحات والهوامش"""
        return max(base_padding, int(base_padding * self.dpi_scale))
    
    def get_margin(self, base_margin: int) -> int:
        """حساب الهوامش الخارجية"""
        if self.is_small_screen:
            return max(base_margin - 2, int(base_margin * 0.8))
        else:
            return max(base_margin, int(base_margin * self.dpi_scale))
    
    def should_use_compact_mode(self) -> bool:
        """تحديد ما إذا كان يجب استخدام الوضع المضغوط"""
        return (self.screen_geometry.width() < 1200 or 
                self.screen_geometry.height() < 700 or 
                self.dpi_scale > 1.5)
    
    
    def is_windows_scale_150(self):
        """التحقق من أن Windows Scale هو 150%"""
        return abs(self.dpi_scale - 1.5) < 0.1
    
    def get_scale_150_font_size(self, base_size: int) -> int:
        """حساب حجم الخط المناسب لـ Scale 150%"""
        if self.is_windows_scale_150():
            # تقليل حجم الخط بنسبة 25% لـ Scale 150%
            return max(8, int(base_size * 0.75))
        return self.get_font_size(base_size)
    
    def get_scale_150_size(self, base_size: int) -> int:
        """حساب الحجم المناسب لـ Scale 150%"""
        if self.is_windows_scale_150():
            # تقليل الأحجام بنسبة 30% لـ Scale 150%
            return max(base_size // 2, int(base_size * 0.7))
        return self.get_scaled_size(base_size)
    
    def get_scale_150_window_size(self, min_width: int, min_height: int) -> tuple:
        """حساب حجم النافذة المناسب لـ Scale 150%"""
        if self.is_windows_scale_150():
            # أحجام خاصة لـ Scale 150%
            screen_width = self.screen_geometry.width()
            screen_height = self.screen_geometry.height()
            
            # استخدام نسبة أكبر من الشاشة لـ Scale 150%
            width = min(int(screen_width * 0.85), 1200)
            height = min(int(screen_height * 0.85), 800)
            
            return max(min_width, width), max(min_height, height)
        
        return self.get_window_size(min_width, min_height)
    def get_icon_size(self, base_size: int) -> QSize:
        """حساب حجم الأيقونات"""
        scaled_size = self.get_scaled_size(base_size)
        return QSize(scaled_size, scaled_size)
    
    def get_responsive_stylesheet_vars(self) -> dict:
        """إرجاع متغيرات CSS للتصميم المتجاوب"""
        return {
            'base_font_size': self.get_font_size(14),
            'title_font_size': self.get_font_size(24),
            'button_font_size': self.get_font_size(16),
            'header_font_size': self.get_font_size(22),
            'small_font_size': self.get_font_size(12),
            'base_padding': self.get_padding(10),
            'button_padding': self.get_padding(8),
            'margin': self.get_margin(15),
            'border_radius': self.get_padding(6),
            'button_height': self.get_button_height(45),
            'sidebar_width': self.get_sidebar_width(280),
            'scrollbar_width': max(12, int(15 * self.dpi_scale)),
            'is_compact': self.should_use_compact_mode()
        }


# إنشاء مثيل عام للاستخدام في التطبيق - استخدام lazy loading
_responsive_instance = None

def get_responsive():
    """الحصول على مثيل نظام التصميم المتجاوب"""
    global _responsive_instance
    if _responsive_instance is None:
        _responsive_instance = ResponsiveDesign()
    return _responsive_instance

# الخاصية للوصول السريع
class ResponsiveProxy:
    """وكيل للوصول السريع لنظام التصميم المتجاوب"""
    
    def __getattr__(self, name):
        return getattr(get_responsive(), name)

responsive = ResponsiveProxy()
