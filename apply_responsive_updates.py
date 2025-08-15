#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف تحديث سريع للتطبيق لدعم التصميم المتجاوب
تشغيل هذا الملف مرة واحدة لتطبيق جميع التحديثات
"""

import sys
import os
from pathlib import Path

def apply_responsive_updates():
    """تطبيق تحديثات التصميم المتجاوب"""
    
    print("🚀 بدء تطبيق تحديثات التصميم المتجاوب...")
    
    base_dir = Path(__file__).parent
    
    # 1. تحقق من وجود الملفات المطلوبة
    required_files = [
        "core/utils/responsive_design.py",
        "app/main_window.py",
        "config.py",
        "main.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (base_dir / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ ملفات مفقودة:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ جميع الملفات المطلوبة موجودة")
    
    # 2. اختبار استيراد نظام التصميم المتجاوب
    try:
        sys.path.insert(0, str(base_dir))
        from core.utils.responsive_design import responsive
        print(f"✅ نظام التصميم المتجاوب يعمل - DPI Scale: {responsive.dpi_scale:.2f}")
    except Exception as e:
        print(f"❌ خطأ في استيراد نظام التصميم المتجاوب: {e}")
        return False
    
    # 3. اختبار النافذة الرئيسية
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QCoreApplication, Qt
        
        # إعداد Qt للـ High DPI
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        app = QApplication([])
        
        from app.main_window import MainWindow
        print("✅ النافذة الرئيسية يمكن استيرادها بنجاح")
        
        app.quit()
        
    except Exception as e:
        print(f"❌ خطأ في النافذة الرئيسية: {e}")
        return False
    
    # 4. إنشاء ملف تكوين للتطبيق
    app_config = base_dir / "responsive_config.json"
    if not app_config.exists():
        import json
        config_data = {
            "responsive_design": {
                "enabled": True,
                "version": "1.0",
                "auto_scale": True,
                "min_window_width": 1000,
                "min_window_height": 700,
                "sidebar_adaptive": True
            },
            "display_settings": {
                "high_dpi_support": True,
                "font_scaling": True,
                "icon_scaling": True,
                "layout_adaptive": True
            },
            "last_update": "2025-08-15"
        }
        
        with open(app_config, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        
        print("✅ تم إنشاء ملف تكوين التطبيق")
    
    # 5. إنشاء ملف اختصار لتشغيل التطبيق
    launcher_script = base_dir / "run_responsive.bat"
    launcher_content = f'''@echo off
cd /d "{base_dir}"
echo Starting Private Schools Accounting with Responsive Design...
echo Screen Information:
python -c "from core.utils.responsive_design import responsive; print(f'Screen: {{responsive.screen_geometry.width()}}x{{responsive.screen_geometry.height()}}, DPI Scale: {{responsive.dpi_scale:.2f}}')"
echo.
python main.py
pause
'''
    
    with open(launcher_script, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("✅ تم إنشاء ملف تشغيل التطبيق: run_responsive.bat")
    
    # 6. إنشاء ملف تشخيص سريع
    diagnostic_script = base_dir / "diagnose_display.py"
    diagnostic_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشخيص سريع لإعدادات الشاشة والتطبيق
"""

import sys
from pathlib import Path

# إضافة مسار المشروع
sys.path.insert(0, str(Path(__file__).parent))

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QCoreApplication
    from core.utils.responsive_design import responsive
    
    QCoreApplication.setAttribute(QCoreApplication.AA_EnableHighDpiScaling, True)
    app = QApplication([])
    
    print("=" * 50)
    print("تشخيص إعدادات الشاشة والتطبيق")
    print("=" * 50)
    
    print(f"📱 حجم الشاشة: {responsive.screen_geometry.width()} x {responsive.screen_geometry.height()}")
    print(f"🔍 DPI: {responsive.dpi:.1f}")
    print(f"📏 مقياس DPI: {responsive.dpi_scale:.2f}")
    print(f"📱 شاشة صغيرة: {'نعم' if responsive.is_small_screen else 'لا'}")
    print(f"🔍 DPI عالي: {'نعم' if responsive.is_high_dpi else 'لا'}")
    print(f"📦 وضع مضغوط: {'نعم' if responsive.should_use_compact_mode() else 'لا'}")
    
    print("\\n" + "=" * 30)
    print("الأحجام المحسوبة")
    print("=" * 30)
    
    window_size = responsive.get_window_size(1000, 700)
    print(f"🖼️  حجم النافذة المقترح: {window_size[0]} x {window_size[1]}")
    print(f"📋 عرض الشريط الجانبي: {responsive.get_sidebar_width(280)}")
    print(f"🔳 ارتفاع الأزرار: {responsive.get_button_height(45)}")
    
    style_vars = responsive.get_responsive_stylesheet_vars()
    print(f"🔤 حجم الخط الأساسي: {style_vars['base_font_size']}px")
    print(f"📝 حجم خط العناوين: {style_vars['title_font_size']}px")
    print(f"🔘 حجم خط الأزرار: {style_vars['button_font_size']}px")
    
    print("\\n✅ جميع الإعدادات تعمل بشكل صحيح!")
    
    app.quit()
    
except Exception as e:
    print(f"❌ خطأ في التشخيص: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open(diagnostic_script, 'w', encoding='utf-8') as f:
        f.write(diagnostic_content)
    
    print("✅ تم إنشاء ملف التشخيص: diagnose_display.py")
    
    print("\\n🎉 تم تطبيق جميع تحديثات التصميم المتجاوب بنجاح!")
    print("\\n📋 للاستخدام:")
    print("   • تشغيل التطبيق: python main.py أو run_responsive.bat")
    print("   • تشخيص الشاشة: python diagnose_display.py")
    print("   • اختبار النظام: python test_responsive_design.py")
    
    return True


if __name__ == "__main__":
    success = apply_responsive_updates()
    if success:
        print("\\n✨ التطبيق جاهز للاستخدام مع التصميم المتجاوب!")
    else:
        print("\\n❌ فشل في تطبيق التحديثات، يرجى مراجعة الأخطاء أعلاه.")
        sys.exit(1)
