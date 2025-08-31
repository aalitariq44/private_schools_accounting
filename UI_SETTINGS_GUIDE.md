# دليل استخدام نظام إعدادات UI
# =================================

## نظرة عامة
تم إنشاء نظام إعدادات UI ليحفظ إعدادات كل صفحة من التطبيق في ملف JSON موحد.
هذا يضمن أن الإعدادات تُحفظ عند إعادة تشغيل التطبيق.

## الملفات المعنية
- `ui/ui_settings_manager.py`: مدير إعدادات UI الرئيسي
- `data/ui_settings.json`: ملف تخزين الإعدادات
- `ui/font_sizes.py`: مدير أحجام الخطوط

## كيفية استخدام النظام في صفحة جديدة

### 1. استيراد المدير
```python
from ...ui_settings_manager import ui_settings_manager
```

### 2. في دالة __init__ للصفحة
```python
def __init__(self):
    super().__init__()
    
    # الحصول على إعدادات الصفحة
    self.current_font_size = ui_settings_manager.get_font_size("page_name")
    self.statistics_visible = ui_settings_manager.get_statistics_visible("page_name")
    
    # باقي الكود...
```

### 3. حفظ التغييرات
```python
def change_font_size(self):
    selected_size = self.font_size_combo.currentText()
    if selected_size != self.current_font_size:
        self.current_font_size = selected_size
        self.setup_styles()
        
        # حفظ التغيير
        ui_settings_manager.set_font_size("page_name", selected_size)

def toggle_statistics_visibility(self):
    self.statistics_visible = not self.statistics_visible
    self.summary_frame.setVisible(self.statistics_visible)
    
    # حفظ التغيير
    ui_settings_manager.set_statistics_visible("page_name", self.statistics_visible)
```

### 4. إعدادات الصفحة الافتراضية
تأكد من إضافة إعدادات الصفحة الافتراضية في `ui_settings_manager.py` في دالة `get_default_settings()`.

## الإعدادات المتاحة حالياً لكل صفحة
- `font_size`: حجم الخط ("صغير جدا", "صغير", "متوسط", "كبير", "كبير جدا")
- `statistics_window_visible`: رؤية نافذة الإحصائيات (true/false)
- `table_columns_visible`: رؤية أعمدة الجدول (قاموس بأسماء الأعمدة)
- `search_filters_visible`: رؤية فلاتر البحث (true/false)
- `export_options_visible`: رؤية خيارات التصدير (true/false)

## إضافة إعدادات جديدة
1. أضف الإعداد الجديد في `ui_settings.json`
2. أضف دالة getter/setter في `UISettingsManager`
3. استخدم الدالة في الصفحة المعنية

## ملاحظات مهمة
- جميع الصفحات تستخدم نفس ملف الإعدادات
- الإعدادات تُحفظ فوراً عند التغيير
- في حالة عدم وجود إعدادات محفوظة، يتم استخدام الإعدادات الافتراضية
- تأكد من استيراد `ui_settings_manager` في بداية ملف الصفحة
