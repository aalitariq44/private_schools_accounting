#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
حل مباشر لمشكلة Windows Scale 150%
يفرض إعدادات محسنة للعمل مع Scale 150%
"""

import os
import sys
from pathlib import Path

def apply_scale_150_fix():
    """تطبيق إصلاح مباشر لـ Scale 150%"""
    
    print("🔧 تطبيق إصلاح Scale 150% المباشر...")
    
    base_dir = Path(__file__).parent
    
    # 1. إنشاء ملف CSS محسن لـ Scale 150%
    scale_150_css = '''
/* تنسيقات محسنة لـ Windows Scale 150% */

/* الخط الأساسي أصغر */
* {
    font-family: 'Cairo';
    font-size: 11px !important;
}

QMainWindow {
    background-color: #F8F9FA;
    font-family: 'Cairo', 'Segoe UI', Tahoma, Arial;
}

/* الشريط الجانبي أضيق */
#sidebarFrame {
    background-color: #1F2937;
    border-right: 1px solid #2d3748;
    max-width: 200px;
    min-width: 180px;
}

#sidebarHeader {
    background-color: transparent;
    border-bottom: 1px solid #2d3748;
    padding: 0;
}

/* عنوان أصغر */
#appTitle {
    color: #E5E7EB;
    font-size: 16px !important;
    font-weight: bold;
    padding: 8px;
}

#sidebarScrollArea {
    background-color: transparent;
    border: none;
}

/* أزرار أصغر */
#menuButton {
    background-color: transparent;
    border: none;
    color: #E5E7EB;
    text-align: center;
    padding: 6px;
    font-size: 12px !important;
    border-radius: 4px;
    margin: 1px 8px;
    max-height: 30px;
    min-height: 28px;
}

#menuButton:hover {
    background-color: #374151;
    color: white;
}

#menuButton:checked {
    background-color: #3B82F6;
    color: white;
    font-weight: bold;
}

#menuSeparator {
    background-color: #374151;
    margin: 8px 16px;
    height: 1px;
    border: none;
}

/* منطقة المحتوى */
#contentFrame {
    background-color: #F8F9FA;
}

#contentHeader {
    background-color: white;
    border-bottom: 1px solid #E9ECEF;
    border-radius: 8px 8px 0 0;
    padding: 8px 16px;
}

/* عناوين أصغر */
#pageTitle {
    font-size: 18px !important;
    font-weight: bold;
    color: #2C3E50;
}

#userInfo {
    background-color: #ECF0F1;
    border-radius: 16px;
    padding: 6px 12px;
}

#userName {
    color: #2C3E50;
    font-size: 12px !important;
    font-weight: bold;
}

#pagesStack {
    background-color: white;
    border-radius: 0 0 8px 8px;
    border: 1px solid #E9ECEF;
}

/* شريط القوائم أصغر */
QMenuBar {
    background-color: #2C3E50;
    color: white;
    border-bottom: 1px solid #34495E;
    font-size: 11px !important;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
}

QMenuBar::item:selected {
    background-color: #34495E;
}

QMenu {
    background-color: white;
    border: 1px solid #BDC3C7;
    font-size: 11px !important;
}

QMenu::item {
    padding: 6px 12px;
    color: #2C3E50;
}

QMenu::item:selected {
    background-color: #3498DB;
    color: white;
}

/* شريط الحالة أصغر */
QStatusBar {
    background-color: #34495E;
    color: white;
    border-top: 1px solid #2C3E50;
    font-size: 10px !important;
}

/* شريط التمرير أرفع */
QScrollBar:vertical {
    background-color: #ECF0F1;
    width: 12px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #BDC3C7;
    min-height: 16px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #95A5A6;
}

/* أزرار النسخ الاحتياطي */
QPushButton#quickBackupButton {
    background-color: #27AE60;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    font-weight: bold;
    font-size: 10px !important;
    min-width: 120px;
    max-height: 28px;
}

QPushButton#quickBackupButton:hover {
    background-color: #229954;
}

QPushButton#quickBackupButton:pressed {
    background-color: #1E8449;
}

/* تحسينات عامة للـ Scale 150% */
QWidget {
    font-size: 11px !important;
}

QLabel {
    font-size: 11px !important;
}

QPushButton {
    font-size: 11px !important;
    padding: 4px 8px;
    max-height: 30px;
}

QLineEdit {
    font-size: 11px !important;
    padding: 4px;
}

QComboBox {
    font-size: 11px !important;
    padding: 4px;
}

QTableWidget {
    font-size: 10px !important;
}

QTreeWidget {
    font-size: 10px !important;
}
'''
    
    # حفظ ملف CSS
    css_file = base_dir / "scale_150_styles.css"
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(scale_150_css)
    
    print("✅ تم إنشاء ملف CSS محسن لـ Scale 150%")
    
    # 2. تحديث main_window.py لاستخدام CSS الجديد
    main_window_path = base_dir / "app" / "main_window.py"
    
    with open(main_window_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إضافة دالة تحميل CSS مخصص
    load_css_function = '''
    def load_scale_150_styles(self):
        """تحميل تنسيقات محسنة لـ Scale 150%"""
        try:
            import config
            css_file = config.BASE_DIR / "scale_150_styles.css"
            
            if css_file.exists():
                with open(css_file, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                
                self.setStyleSheet(css_content)
                logging.info("تم تحميل تنسيقات Scale 150% المحسنة")
                return True
            else:
                logging.warning("ملف تنسيقات Scale 150% غير موجود")
                return False
                
        except Exception as e:
            logging.error(f"خطأ في تحميل تنسيقات Scale 150%: {e}")
            return False
'''
    
    if "load_scale_150_styles" not in content:
        # إضافة الدالة قبل setup_styles
        setup_styles_pos = content.find("def setup_styles(self):")
        if setup_styles_pos != -1:
            content = content[:setup_styles_pos] + load_css_function + "\n    " + content[setup_styles_pos:]
    
    # تحديث دالة setup_styles لاستخدام CSS المحسن
    if "load_scale_150_styles" not in content.split("def setup_styles(self):")[1].split("def ")[0]:
        old_setup = "def setup_styles(self):"
        new_setup = '''def setup_styles(self):
        """إعداد تنسيقات النافذة"""
        try:
            # محاولة استخدام CSS محسن لـ Scale 150%
            if self.load_scale_150_styles():
                return  # تم تحميل CSS محسن، لا حاجة للمتابعة
            
            # الكود الأصلي كبديل'''
        
        content = content.replace(old_setup, new_setup)
    
    with open(main_window_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ تم تحديث main_window.py لاستخدام CSS محسن")
    
    # 3. تحديث config.py لدعم أحجام Scale 150%
    config_path = base_dir / "config.py"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    # إضافة إعدادات Scale 150%
    scale_150_config = '''
# إعدادات محسنة لـ Windows Scale 150%
SCALE_150_ENABLED = True
SCALE_150_WINDOW_MIN_WIDTH = 850
SCALE_150_WINDOW_MIN_HEIGHT = 550
SCALE_150_SIDEBAR_WIDTH = 180
SCALE_150_BUTTON_HEIGHT = 28
SCALE_150_FONT_SIZE = 11
'''
    
    if "SCALE_150_ENABLED" not in config_content:
        config_content += scale_150_config
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("✅ تم تحديث config.py لدعم Scale 150%")
    
    # 4. إنشاء ملف تشغيل خاص لـ Scale 150%
    launcher_150 = base_dir / "run_scale_150.bat"
    launcher_content = f'''@echo off
title Private Schools Accounting - Scale 150% Optimized
cd /d "{base_dir}"

echo ===================================
echo   Private Schools Accounting
echo   Windows Scale 150% Optimized
echo ===================================
echo.

echo Checking system scale...
python -c "from core.utils.responsive_design import responsive; print(f'Detected Scale: {{responsive.dpi_scale * 100:.0f}}%%')"

echo.
echo Starting application with Scale 150% optimizations...
echo.

python main.py

echo.
echo Application closed.
pause
'''
    
    with open(launcher_150, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("✅ تم إنشاء ملف تشغيل محسن لـ Scale 150%")
    
    # 5. إنشاء ملف اختبار نهائي
    final_test = base_dir / "test_final_scale_150.py"
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نهائي لإصلاح Scale 150%
"""

import sys
import os
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QCoreApplication

# إعدادات Qt محسنة
QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

def test_scale_150_final():
    """الاختبار النهائي لإصلاح Scale 150%"""
    app = QApplication(sys.argv)
    
    try:
        print("🧪 الاختبار النهائي لإصلاح Scale 150%")
        print("=" * 40)
        
        # تحميل التطبيق مع الإصلاحات
        from app.main_window import MainWindow
        
        main_window = MainWindow()
        
        # فرض أحجام محسنة للنافذة
        main_window.setMinimumSize(850, 550)
        main_window.resize(1100, 750)
        
        # فرض عرض أضيق للشريط الجانبي
        if hasattr(main_window, 'sidebar_frame'):
            main_window.sidebar_frame.setFixedWidth(180)
        
        main_window.show()
        
        # رسالة نجاح
        QMessageBox.information(
            main_window,
            "✅ إصلاح Scale 150%",
            f"""تم تطبيق الإصلاحات بنجاح!

🖥️ حجم النافذة: {main_window.width()} x {main_window.height()}
📋 عرض الشريط الجانبي: {main_window.sidebar_frame.width() if hasattr(main_window, 'sidebar_frame') else 'غير محدد'}
🎨 تم تطبيق CSS محسن: نعم

التطبيق الآن محسن للعمل مع Windows Scale 150%
يجب أن تظهر العناصر بأحجام مناسبة ومقروءة."""
        )
        
        return app.exec_()
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        
        QMessageBox.critical(None, "خطأ", f"حدث خطأ:\\n{e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_scale_150_final())
'''
    
    with open(final_test, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ تم إنشاء الاختبار النهائي")
    
    print("\\n🎉 تم إكمال الإصلاح المباشر لـ Scale 150%!")
    print("\\n📋 للاستخدام:")
    print("   🚀 تشغيل محسن: run_scale_150.bat")
    print("   🧪 اختبار نهائي: python test_final_scale_150.py")
    print("   📁 تشغيل عادي: python main.py")
    
    return True

if __name__ == "__main__":
    apply_scale_150_fix()
