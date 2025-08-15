#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة كشف دقيقة لـ Windows Scale
"""

import sys
import os
from pathlib import Path
import platform

def detect_windows_scale():
    """كشف دقيق لمقياس Windows"""
    
    print("🔍 فحص مقياس Windows...")
    
    if platform.system() != "Windows":
        print("❌ هذا النظام ليس Windows")
        return 1.0
    
    try:
        # طريقة 1: استخدام PyQt5
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QCoreApplication
        
        # تطبيق إعدادات High DPI
        QCoreApplication.setAttribute(QCoreApplication.AA_EnableHighDpiScaling, True)
        QCoreApplication.setAttribute(QCoreApplication.AA_UseHighDpiPixmaps, True)
        
        app = QApplication([])
        
        screen = app.primaryScreen()
        if screen:
            # الحصول على DPI المنطقي والفعلي
            logical_dpi = screen.logicalDotsPerInch()
            physical_dpi = screen.physicalDotsPerInch()
            device_pixel_ratio = screen.devicePixelRatio()
            
            print(f"📊 DPI المنطقي: {logical_dpi}")
            print(f"📊 DPI الفعلي: {physical_dpi}")
            print(f"📊 نسبة البكسل: {device_pixel_ratio}")
            
            # حساب المقياس
            scale_from_dpi = logical_dpi / 96.0
            scale_from_ratio = device_pixel_ratio
            
            print(f"📏 مقياس من DPI: {scale_from_dpi:.2f} ({scale_from_dpi * 100:.0f}%)")
            print(f"📏 مقياس من نسبة البكسل: {scale_from_ratio:.2f} ({scale_from_ratio * 100:.0f}%)")
        
        app.quit()
        
        # طريقة 2: استخدام Windows API
        try:
            import ctypes
            from ctypes import wintypes
            
            # الحصول على handle للنافذة الحالية
            user32 = ctypes.windll.user32
            shcore = ctypes.windll.shcore
            
            # إعداد DPI awareness
            shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
            
            # الحصول على DPI للشاشة الرئيسية
            hdc = user32.GetDC(0)
            dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
            dpi_y = ctypes.windll.gdi32.GetDeviceCaps(hdc, 90)  # LOGPIXELSY
            user32.ReleaseDC(0, hdc)
            
            windows_scale = dpi_x / 96.0
            
            print(f"🪟 Windows API - DPI X: {dpi_x}")
            print(f"🪟 Windows API - DPI Y: {dpi_y}")
            print(f"🪟 Windows API - Scale: {windows_scale:.2f} ({windows_scale * 100:.0f}%)")
            
            return windows_scale
            
        except Exception as e:
            print(f"⚠️  خطأ في Windows API: {e}")
            return scale_from_dpi
    
    except Exception as e:
        print(f"❌ خطأ في كشف المقياس: {e}")
        return 1.0

def force_scale_150_settings():
    """فرض إعدادات Scale 150% بغض النظر عن الكشف"""
    
    print("🔧 فرض إعدادات Scale 150%...")
    
    base_dir = Path(__file__).parent
    
    # إنشاء ملف إعدادات مفروضة لـ Scale 150%
    forced_config = base_dir / "forced_scale_150.py"
    
    config_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعدادات مفروضة لـ Windows Scale 150%
"""

# إجبار التطبيق على استخدام إعدادات Scale 150%
FORCE_SCALE_150 = True

class ForcedScale150Settings:
    """إعدادات مفروضة لـ Scale 150%"""
    
    def __init__(self):
        self.dpi_scale = 1.5
        self.is_forced = True
    
    def get_font_size(self, base_size: int) -> int:
        """أحجام خطوط محسنة لـ Scale 150%"""
        scale_map = {
            24: 16,  # العناوين
            22: 15,  # العناوين الفرعية
            16: 12,  # الأزرار
            14: 11,  # النص الأساسي
            12: 10,  # النص الصغير
            10: 9    # النص الأصغر
        }
        return scale_map.get(base_size, max(8, int(base_size * 0.7)))
    
    def get_size(self, base_size: int) -> int:
        """أحجام عناصر محسنة لـ Scale 150%"""
        scale_map = {
            280: 190,  # عرض الشريط الجانبي
            45: 32,    # ارتفاع الأزرار
            20: 14,    # البادينغ
            15: 10,    # الهوامش
            10: 7,     # المساحات الصغيرة
            6: 4       # border radius
        }
        return scale_map.get(base_size, max(base_size // 2, int(base_size * 0.68)))
    
    def get_window_size(self, min_width: int, min_height: int) -> tuple:
        """أحجام نافذة محسنة لـ Scale 150%"""
        # أحجام مثلى لـ Scale 150%
        optimal_width = 1100
        optimal_height = 750
        
        return (
            max(min_width, optimal_width),
            max(min_height, optimal_height)
        )

# إنشاء مثيل للاستخدام العام
forced_scale_150 = ForcedScale150Settings()
'''
    
    with open(forced_config, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ تم إنشاء إعدادات Scale 150% المفروضة")
    
    # تحديث responsive_design.py لاستخدام الإعدادات المفروضة
    responsive_path = base_dir / "core" / "utils" / "responsive_design.py"
    
    with open(responsive_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إضافة استيراد الإعدادات المفروضة
    import_line = "import logging"
    if import_line in content and "forced_scale_150" not in content:
        content = content.replace(
            import_line,
            import_line + "\n\ntry:\n    from forced_scale_150 import forced_scale_150, FORCE_SCALE_150\nexcept ImportError:\n    FORCE_SCALE_150 = False\n    forced_scale_150 = None"
        )
    
    # إضافة دالة للتحقق من الإعدادات المفروضة
    check_forced = '''
    def is_scale_150_forced(self):
        """التحقق من فرض إعدادات Scale 150%"""
        try:
            from forced_scale_150 import FORCE_SCALE_150
            return FORCE_SCALE_150
        except ImportError:
            return False
    
    def use_forced_scale_150(self):
        """استخدام الإعدادات المفروضة لـ Scale 150%"""
        if self.is_scale_150_forced():
            from forced_scale_150 import forced_scale_150
            return forced_scale_150
        return None'''
    
    if "is_scale_150_forced" not in content:
        # إضافة الدالة بعد __init__
        init_end = "logging.info(f\"معلومات الشاشة:"
        if init_end in content:
            insertion_point = content.find(init_end)
            next_def = content.find("def ", insertion_point)
            if next_def != -1:
                content = content[:next_def] + check_forced + "\n    " + content[next_def:]
    
    with open(responsive_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ تم تحديث responsive_design.py للدعم المفروض")
    
    # تحديث main_window.py
    main_window_path = base_dir / "app" / "main_window.py"
    
    with open(main_window_path, 'r', encoding='utf-8') as f:
        window_content = f.read()
    
    # إضافة فحص الإعدادات المفروضة
    forced_check = '''            # فحص الإعدادات المفروضة لـ Scale 150%
            forced_settings = responsive.use_forced_scale_150()
            if forced_settings:
                print("🔧 استخدام إعدادات Scale 150% المفروضة")
                window_width, window_height = forced_settings.get_window_size(
                    config.WINDOW_MIN_WIDTH, 
                    config.WINDOW_MIN_HEIGHT
                )
                self.setMinimumSize(850, 550)
                self.dpi_scale = 1.5
                self.forced_scale_150 = True
            elif responsive.is_windows_scale_150():'''
    
    if "استخدام إعدادات Scale 150% المفروضة" not in window_content:
        # البحث عن موقع التحقق من Scale 150%
        scale_check = "# التحقق من Scale 150% والتعامل معه خصيصاً"
        if scale_check in window_content:
            window_content = window_content.replace(
                scale_check,
                scale_check + "\n" + forced_check
            )
        
        with open(main_window_path, 'w', encoding='utf-8') as f:
            f.write(window_content)
        
        print("✅ تم تحديث main_window.py للدعم المفروض")
    
    return True

if __name__ == "__main__":
    scale = detect_windows_scale()
    print(f"\\n🎯 المقياس المكتشف: {scale:.2f} ({scale * 100:.0f}%)")
    
    if scale >= 1.4:  # إذا كان المقياس 140% أو أعلى
        print("✅ تم اكتشاف مقياس عالي - سيتم تطبيق إعدادات Scale 150%")
    else:
        print("⚠️  لم يتم اكتشاف Scale 150% - سيتم فرض الإعدادات")
        force_scale_150_settings()
        print("✅ تم فرض إعدادات Scale 150%")
