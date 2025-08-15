#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام التصميم المتجاوب للتطبيق
"""

import sys
import os
from pathlib import Path

# إضافة مسار المشروع إلى Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QCoreApplication

# إعداد خصائص التطبيق قبل إنشاء QApplication
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
QCoreApplication.setAttribute(Qt.AA_DisableWindowContextHelpButton, True)

# تحسينات إضافية لدعم high DPI
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"


def test_responsive_design():
    """اختبار نظام التصميم المتجاوب"""
    app = QApplication(sys.argv)
    
    try:
        from core.utils.responsive_design import responsive
        
        print("=== معلومات الشاشة ===")
        print(f"حجم الشاشة: {responsive.screen_geometry.width()}x{responsive.screen_geometry.height()}")
        print(f"DPI: {responsive.dpi:.1f}")
        print(f"مقياس DPI: {responsive.dpi_scale:.2f}")
        print(f"شاشة صغيرة: {'نعم' if responsive.is_small_screen else 'لا'}")
        print(f"DPI عالي: {'نعم' if responsive.is_high_dpi else 'لا'}")
        print(f"وضع مضغوط: {'نعم' if responsive.should_use_compact_mode() else 'لا'}")
        
        print("\n=== الأحجام المحسوبة ===")
        window_width, window_height = responsive.get_window_size(1000, 700)
        print(f"حجم النافذة المقترح: {window_width}x{window_height}")
        print(f"عرض الشريط الجانبي: {responsive.get_sidebar_width(280)}")
        print(f"ارتفاع الأزرار: {responsive.get_button_height(45)}")
        
        print("\n=== أحجام الخطوط ===")
        style_vars = responsive.get_responsive_stylesheet_vars()
        for key, value in style_vars.items():
            if 'font' in key:
                print(f"{key}: {value}px")
        
        # اختبار النافذة الرئيسية
        from app.main_window import MainWindow
        
        # محاولة إنشاء النافذة الرئيسية
        main_window = MainWindow()
        main_window.show()
        
        # عرض رسالة نجاح
        QMessageBox.information(
            main_window,
            "اختبار التصميم المتجاوب",
            f"تم تحميل التطبيق بنجاح!\n\n"
            f"حجم الشاشة: {responsive.screen_geometry.width()}x{responsive.screen_geometry.height()}\n"
            f"مقياس DPI: {responsive.dpi_scale:.2f}\n"
            f"حجم النافذة: {main_window.width()}x{main_window.height()}"
        )
        
        return app.exec_()
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        
        QMessageBox.critical(
            None,
            "خطأ",
            f"حدث خطأ أثناء اختبار التصميم المتجاوب:\n{e}"
        )
        return 1


if __name__ == "__main__":
    test_responsive_design()
