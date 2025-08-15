#!/usr/bin/env python3
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
            print("\n🔧 إعدادات Scale 150%:")
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
        
        QMessageBox.critical(None, "خطأ", f"حدث خطأ أثناء اختبار Scale 150%:\n{e}")
        return 1

if __name__ == "__main__":
    test_scale_150()
