# نظام الطباعة المزدوج

يدعم التطبيق الآن نظام طباعة مزدوج متطور يختار أفضل طريقة طباعة تلقائياً حسب نوع المستند:

## 🎯 المسارات المتاحة

### 1. مسار HTML (QWebEngineView)
**الاستخدام**: التقارير البسيطة والقوائم العامة
- ✅ تقارير الطلاب
- ✅ قوائم الطلاب  
- ✅ التقارير المالية
- ✅ تقارير الموظفين
- ✅ تقارير المدارس

**المميزات**:
- سهولة التصميم باستخدام HTML + CSS
- قوالب Jinja2 مرنة
- معاينة فورية عبر محرك الويب
- طباعة مباشرة عبر `view.page().print()`

### 2. مسار ReportLab 
**الاستخدام**: الوصولات والفواتير الرسمية
- ✅ إيصالات دفع الأقساط
- ✅ إيصالات الدفع العامة
- ✅ الفواتير الرسمية (قابل للتوسع)

**المميزات**:
- دقة مواضع عالية للنصوص والعناصر
- دعم مثالي للعربية (RTL + تشكيل الأحرف)
- إخراج PDF احترافي
- تحكم كامل في التصميم برمجياً
- لا يحتاج HTML

## 🔧 كيفية الاستخدام

### الطريقة التلقائية (مستحسنة)
```python
from core.printing.print_manager import PrintManager

# إنشاء مدير الطباعة
pm = PrintManager()

# طباعة إيصال قسط (سيستخدم ReportLab تلقائياً)
installment_data = {
    'student_name': 'أحمد محمد',
    'amount': 250000,
    'installment_number': 3,
    'school_name': 'مدرسة النور'
}
pm.preview_document(TemplateType.INSTALLMENT_RECEIPT, installment_data)

# طباعة تقرير طالب (سيستخدم HTML تلقائياً)
student_data = {
    'student': {'name': 'فاطمة علي', 'class': 'السادس'}
}
pm.preview_document(TemplateType.STUDENT_REPORT, student_data)
```

### الدوال السريعة
```python
from core.printing.print_manager import print_installment_receipt, print_student_report

# طباعة إيصال قسط
print_installment_receipt(installment_data)

# طباعة تقرير طالب
print_student_report(student_data)
```

### استخدام ReportLab مباشرة
```python
from core.printing.reportlab_print_manager import ReportLabPrintManager

manager = ReportLabPrintManager()
pdf_path = manager.create_installment_receipt(data)
```

## ⚙️ التكوين

تحديد طريقة الطباعة لكل نوع مستند في `print_config.py`:

```python
TEMPLATE_PRINT_METHODS = {
    # HTML للتقارير
    TemplateType.STUDENT_REPORT: PrintMethod.HTML_WEB_ENGINE,
    TemplateType.STUDENT_LIST: PrintMethod.HTML_WEB_ENGINE,
    
    # ReportLab للوصولات
    TemplateType.INSTALLMENT_RECEIPT: PrintMethod.REPORTLAB_CANVAS,
    TemplateType.PAYMENT_RECEIPT: PrintMethod.REPORTLAB_CANVAS,
}
```

## 📦 المتطلبات الإضافية

```bash
pip install arabic-reshaper python-bidi
```

## 🧪 الاختبار

```bash
python test_dual_print_system.py
```

## 📁 هيكل الملفات

```
core/printing/
├── print_manager.py           # المدير الرئيسي (مزدوج)
├── web_print_manager.py       # مدير HTML/WebEngine  
├── reportlab_print_manager.py # مدير ReportLab
├── print_config.py           # التكوين والمصفوفات
└── template_manager.py       # مدير قوالب HTML
```

## 🎨 تخصيص إيصالات ReportLab

لتخصيص تصميم الإيصالات، عدل في `reportlab_print_manager.py`:

- `_draw_receipt_header()` - الرأس
- `_draw_receipt_body()` - المحتوى  
- `_draw_receipt_footer()` - الذيل
- `_number_to_arabic_words()` - تحويل الأرقام لكلمات

## 🔍 استكشاف الأخطاء

### خطأ في الخطوط العربية
- تأكد من وجود خطوط Cairo في `app/resources/fonts/`
- تحقق من مسار `config.RESOURCES_DIR`

### خطأ في دعم العربية
```bash
pip install arabic-reshaper python-bidi
```

### التبديل للمسار البديل
النظام يتبدل تلقائياً لمسار HTML في حالة فشل ReportLab.

## 🚀 التطوير المستقبلي

- [ ] دعم أنواع فواتير إضافية في ReportLab
- [ ] قوالب ReportLab قابلة للتخصيص
- [ ] واجهة مرئية لاختيار مسار الطباعة
- [ ] تصدير للصور بدلاً من PDF
- [ ] دمج التوقيع الرقمي
