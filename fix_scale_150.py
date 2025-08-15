#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح خاص لمشكلة Windows Scale 150%
هذا الملف يحل مشكلة عدم ظهور التطبيق بشكل صحيح عند scale 150%
"""

import os
import sys
from pathlib import Path

def fix_windows_scale_150():
    """إصلاح خاص لمشكلة Windows Scale 150%"""
    
    print("🔧 بدء إصلاح مشكلة Windows Scale 150%...")
    
    base_dir = Path(__file__).parent
    
    # 1. تحديث main.py لدعم أفضل لـ Scale 150%
    main_py_path = base_dir / "main.py"
    
    # قراءة الملف الحالي
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إضافة إعدادات خاصة لـ Scale 150%
    scale_fix = '''# إعدادات خاصة لحل مشكلة Windows Scale 150%
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
QCoreApplication.setAttribute(Qt.AA_DisableWindowContextHelpButton, True)

# تحسينات خاصة لـ Scale 150%
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1" 
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_FONT_DPI"] = "96"  # إجبار DPI للخطوط
os.environ["QT_DEVICE_PIXEL_RATIO"] = "1"  # تحكم في نسبة البكسل'''
    
    if "QT_DEVICE_PIXEL_RATIO" not in content:
        # البحث عن موقع الإعدادات الحالية
        if "QT_ENABLE_HIGHDPI_SCALING" in content:
            content = content.replace(
                'os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"',
                scale_fix
            )
        else:
            # إضافة الإعدادات بعد الاستيرادات
            import_line = "from PyQt5.QtCore import Qt, QDir, QTranslator, QLocale, QCoreApplication"
            if import_line in content:
                content = content.replace(
                    import_line,
                    import_line + "\n\n" + scale_fix
                )
        
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ تم تحديث main.py لدعم Scale 150%")
    
    # 2. إنشاء ملف إعدادات خاص لـ Scale 150%
    scale_config_path = base_dir / "scale_150_config.py"
    scale_config_content = '''#!/usr/bin/env python3
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
'''
    
    with open(scale_config_path, 'w', encoding='utf-8') as f:
        f.write(scale_config_content)
    
    print("✅ تم إنشاء ملف إعدادات Scale 150%")
    
    # 3. تحديث responsive_design.py لدعم خاص لـ Scale 150%
    responsive_path = base_dir / "core" / "utils" / "responsive_design.py"
    
    with open(responsive_path, 'r', encoding='utf-8') as f:
        responsive_content = f.read()
    
    # إضافة دالة خاصة لـ Scale 150%
    scale_150_method = '''
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
        
        return self.get_window_size(min_width, min_height)'''
    
    if "is_windows_scale_150" not in responsive_content:
        # إضافة الدوال بعد دالة should_use_compact_mode
        insertion_point = "def get_icon_size(self, base_size: int) -> QSize:"
        if insertion_point in responsive_content:
            responsive_content = responsive_content.replace(
                insertion_point,
                scale_150_method + "\n    " + insertion_point
            )
            
            with open(responsive_path, 'w', encoding='utf-8') as f:
                f.write(responsive_content)
            
            print("✅ تم تحديث responsive_design.py لدعم Scale 150%")
    
    # 4. تحديث main_window.py لاستخدام إعدادات Scale 150%
    main_window_path = base_dir / "app" / "main_window.py"
    
    with open(main_window_path, 'r', encoding='utf-8') as f:
        window_content = f.read()
    
    # تحديث دالة setup_responsive_sizing
    new_sizing_method = '''    def setup_responsive_sizing(self):
        """إعداد الأحجام المتجاوبة مع DPI الحالي"""
        try:
            from PyQt5.QtWidgets import QApplication
            
            # الحصول على معلومات الشاشة
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            
            # التحقق من Scale 150% والتعامل معه خصيصاً
            if responsive.is_windows_scale_150():
                print("🔧 تم اكتشاف Windows Scale 150% - تطبيق إعدادات خاصة")
                window_width, window_height = responsive.get_scale_150_window_size(
                    config.WINDOW_MIN_WIDTH, 
                    config.WINDOW_MIN_HEIGHT
                )
                # تعيين أحجام خاصة لـ Scale 150%
                self.setMinimumSize(900, 600)
            else:
                # حساب الأحجام المناسبة للمقاييس الأخرى
                window_width, window_height = responsive.get_window_size(
                    config.WINDOW_MIN_WIDTH, 
                    config.WINDOW_MIN_HEIGHT
                )
                self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
            
            # تعيين الحجم المفضل
            self.resize(window_width, window_height)
            
            # حفظ معلومات DPI للاستخدام في باقي المكونات
            self.dpi_scale = responsive.dpi_scale
            
            logging.info(f"DPI Scale: {responsive.dpi_scale:.2f}, Window: {window_width}x{window_height}")
            if responsive.is_windows_scale_150():
                logging.info("تم تطبيق إعدادات خاصة لـ Windows Scale 150%")
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الأحجام المتجاوبة: {e}")
            # في حالة الخطأ، استخدم الأحجام الافتراضية
            self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
            self.resize(1200, 800)
            self.dpi_scale = 1.0'''
    
    # البحث عن دالة setup_responsive_sizing واستبدالها
    import re
    pattern = r'def setup_responsive_sizing\(self\):.*?self\.dpi_scale = 1\.0'
    
    if re.search(pattern, window_content, re.DOTALL):
        window_content = re.sub(pattern, new_sizing_method.strip(), window_content, flags=re.DOTALL)
        
        with open(main_window_path, 'w', encoding='utf-8') as f:
            f.write(window_content)
        
        print("✅ تم تحديث main_window.py لدعم Scale 150%")
    
    # 5. إنشاء ملف اختبار خاص لـ Scale 150%
    test_scale_path = base_dir / "test_scale_150.py"
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار خاص لـ Windows Scale 150%
"""

import sys
import os
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QCoreApplication

# إعدادات خاصة لـ Scale 150%
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
QCoreApplication.setAttribute(Qt.AA_DisableWindowContextHelpButton, True)

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_FONT_DPI"] = "96"
os.environ["QT_DEVICE_PIXEL_RATIO"] = "1"

def test_scale_150():
    """اختبار Windows Scale 150%"""
    app = QApplication(sys.argv)
    
    try:
        from core.utils.responsive_design import responsive
        
        print("=" * 50)
        print("اختبار Windows Scale 150%")
        print("=" * 50)
        
        print(f"🖥️  حجم الشاشة: {responsive.screen_geometry.width()}x{responsive.screen_geometry.height()}")
        print(f"📏 DPI: {responsive.dpi:.1f}")
        print(f"📊 مقياس DPI: {responsive.dpi_scale:.2f}")
        print(f"🔍 Windows Scale المكتشف: {responsive.dpi_scale * 100:.0f}%")
        
        is_150 = responsive.is_windows_scale_150()
        print(f"✅ Scale 150% مكتشف: {'نعم' if is_150 else 'لا'}")
        
        if is_150:
            print("\\n🔧 إعدادات Scale 150%:")
            window_size = responsive.get_scale_150_window_size(900, 600)
            print(f"📐 حجم النافذة المقترح: {window_size[0]}x{window_size[1]}")
            print(f"📝 حجم خط العنوان: {responsive.get_scale_150_font_size(24)}px")
            print(f"🔘 حجم خط الأزرار: {responsive.get_scale_150_font_size(16)}px")
            print(f"📋 عرض الشريط الجانبي: {responsive.get_scale_150_size(280)}px")
            print(f"🔳 ارتفاع الأزرار: {responsive.get_scale_150_size(45)}px")
        
        # اختبار النافذة الرئيسية
        from app.main_window import MainWindow
        
        main_window = MainWindow()
        main_window.show()
        
        # رسالة نجاح
        message = f"""تم تحميل التطبيق بنجاح!

الشاشة: {responsive.screen_geometry.width()}x{responsive.screen_geometry.height()}
Windows Scale: {responsive.dpi_scale * 100:.0f}%
Scale 150%: {'مكتشف' if is_150 else 'غير مكتشف'}
حجم النافذة: {main_window.width()}x{main_window.height()}

{"✅ تم تطبيق إعدادات خاصة لـ Scale 150%" if is_150 else "ℹ️ تم استخدام الإعدادات العادية"}"""
        
        QMessageBox.information(main_window, "اختبار Scale 150%", message)
        
        return app.exec_()
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        
        QMessageBox.critical(None, "خطأ", f"حدث خطأ أثناء اختبار Scale 150%:\\n{e}")
        return 1

if __name__ == "__main__":
    test_scale_150()
'''
    
    with open(test_scale_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ تم إنشاء ملف اختبار Scale 150%")
    
    print("\\n🎉 تم إكمال إصلاح مشكلة Windows Scale 150%!")
    print("\\n📋 للاختبار:")
    print("   • تشغيل الاختبار: python test_scale_150.py")
    print("   • تشغيل التطبيق: python main.py")
    
    return True

if __name__ == "__main__":
    fix_windows_scale_150()
