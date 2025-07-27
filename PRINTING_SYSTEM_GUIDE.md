# نظام الطباعة الموحد للتطبيق

## نظرة عامة

هذا نظام طباعة شامل ومتطور تم تصميمه ليكون قابلاً للاستخدام في جميع أجزاء التطبيق. يوفر النظام:

- **معاينة قبل الطباعة** لجميع التقارير
- **قوالب HTML متقدمة** قابلة للتخصيص
- **طباعة سريعة** بدون معاينة
- **تصدير إلى PDF**
- **إعدادات طباعة متقدمة**
- **واجهة سهلة الاستخدام**

## هيكل النظام

```
core/printing/
├── __init__.py                 # الواردات الرئيسية
├── print_config.py            # إعدادات وتكوين الطباعة
├── template_manager.py        # مدير القوالب
├── print_preview.py          # نافذة معاينة الطباعة
├── print_manager.py          # مدير الطباعة الرئيسي
├── print_utils.py            # أدوات مساعدة
└── templates/                # مجلد القوالب (يتم إنشاؤه تلقائياً)
    ├── student_report.html
    ├── student_list.html
    ├── financial_report.html
    ├── payment_receipt.html
    ├── salary_slip.html
    ├── staff_report.html
    └── school_report.html

resources/print_templates/     # القوالب المخصصة
```

## الميزات الرئيسية

### 1. أنواع التقارير المدعومة

- **تقرير الطالب الفردي**: تفاصيل طالب واحد
- **قائمة الطلاب**: جدول بجميع الطلاب
- **التقرير المالي**: ملخص الإيرادات والمصروفات
- **إيصال الدفع**: إيصال للمدفوعات
- **قسيمة الراتب**: رواتب الموظفين
- **تقرير الموظفين**: قائمة الموظفين
- **تقرير المدرسة**: إحصائيات شاملة

### 2. خيارات الطباعة

- **طباعة مع معاينة**: عرض التقرير قبل الطباعة مع إمكانية التعديل
- **طباعة سريعة**: طباعة مباشرة بالإعدادات الافتراضية
- **تصدير PDF**: حفظ التقرير كملف PDF

### 3. إعدادات متقدمة

- أحجام الورق: A4, A3, Letter, Legal
- اتجاه الطباعة: عمودي/أفقي
- جودة الطباعة: مسودة/عادي/عالي
- هوامش قابلة للتخصيص
- إعدادات الخط والتنسيق

## كيفية الاستخدام

### 1. الاستيراد الأساسي

```python
from core.printing import print_manager, PrintHelper, QuickPrintMixin
```

### 2. طباعة تقرير طالب

```python
# بيانات الطالب
student_data = {
    'id': 1,
    'name': 'أحمد محمد',
    'school_name': 'مدرسة النور',
    'grade': 'الرابع الابتدائي',
    'section': 'أ',
    'gender': 'ذكر',
    'phone': '07901234567',
    'status': 'نشط',
    'total_fee': 500000
}

# طباعة مع معاينة
print_manager.print_student_report(student_data, parent_widget)
```

### 3. طباعة قائمة الطلاب

```python
# قائمة الطلاب
students_list = [student1, student2, student3]

# معلومات الفلاتر المطبقة
filter_info = "المدرسة: مدرسة النور | الصف: الرابع الابتدائي"

# طباعة القائمة
print_manager.print_students_list(students_list, filter_info, parent_widget)
```

### 4. الطباعة السريعة

```python
# طباعة سريعة بدون معاينة
print_manager.quick_print_student_list(students_list, parent_widget)
```

### 5. تصدير PDF

```python
from core.printing import TemplateType

# تصدير قائمة الطلاب إلى PDF
data = {'students': students_list, 'filter_info': filter_info}
print_manager.export_to_pdf(
    TemplateType.STUDENT_LIST, 
    data, 
    "path/to/output.pdf", 
    parent_widget
)
```

## إضافة الطباعة للصفحات

### 1. استخدام QuickPrintMixin

```python
class YourPage(QWidget, QuickPrintMixin):
    def __init__(self):
        super().__init__()
        self.setup_quick_print()  # إعداد الطباعة
    
    def get_current_data_for_print(self):
        """إرجاع البيانات الحالية للطباعة"""
        return self.current_data
```

### 2. إضافة أزرار الطباعة

```python
# في إعداد واجهة المستخدم
def create_toolbar(self, layout):
    # أزرار الطباعة
    self.print_button = QPushButton("طباعة")
    self.print_button.setObjectName("printButton")
    self.print_button.clicked.connect(self.print_with_preview)
    
    self.quick_print_button = QPushButton("طباعة سريعة")
    self.quick_print_button.setObjectName("quickPrintButton")
    self.quick_print_button.clicked.connect(self.quick_print_current_data)
    
    self.export_button = QPushButton("تصدير PDF")
    self.export_button.setObjectName("exportButton")
    self.export_button.clicked.connect(self.export_to_pdf)
```

### 3. تطبيق التنسيقات

```python
from core.printing import apply_print_styles

def setup_styles(self):
    base_style = """
        /* تنسيقاتك الأساسية */
    """
    
    # إضافة تنسيقات الطباعة
    full_style = base_style + apply_print_styles()
    self.setStyleSheet(full_style)
```

## تخصيص القوالب

### 1. تعديل القوالب الموجودة

القوالب موجودة في `resources/print_templates/` ويمكن تعديلها مباشرة.

### 2. إنشاء قالب جديد

```python
# إضافة نوع جديد في print_config.py
class TemplateType(Enum):
    CUSTOM_REPORT = "custom_report"

# إنشاء القالب في template_manager.py
def get_custom_template(self):
    return """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>تقرير مخصص</title>
        <style>
            /* تنسيقات CSS */
        </style>
    </head>
    <body>
        <!-- محتوى HTML -->
    </body>
    </html>
    """
```

### 3. استخدام متغيرات Jinja2

```html
<!-- في القالب -->
<h1>{{ company_name }}</h1>
<p>التاريخ: {{ print_date | date_ar }}</p>
<p>المبلغ: {{ amount | currency }}</p>

<!-- عرض قائمة -->
{% for student in students %}
    <tr>
        <td>{{ student.name }}</td>
        <td>{{ student.grade }}</td>
    </tr>
{% endfor %}
```

## الفلاتر المخصصة

يوفر النظام فلاتر مخصصة لتنسيق البيانات:

- `currency`: تنسيق العملة (مثال: 1000.50 دينار)
- `date_ar`: تنسيق التاريخ بالعربية (مثال: 15 يناير 2024)

## معالجة الأخطاء

النظام يتعامل مع الأخطاء بشكل تلقائي:

- **خطأ في القالب**: عرض قالب خطأ بدلاً من توقف التطبيق
- **خطأ في البيانات**: رسائل تحذير للمستخدم
- **خطأ في الطباعة**: إعادة المحاولة أو إلغاء العملية

## الأداء والتحسين

- **تحميل القوالب**: يتم تحميل القوالب مرة واحدة عند بدء التطبيق
- **ذاكرة التخزين المؤقت**: القوالب محفوظة في الذاكرة لتسريع الوصول
- **معاينة سريعة**: استخدام WebEngine لمعاينة سريعة

## اختبار النظام

```bash
# تشغيل اختبار النظام
python test_printing_system.py
```

## المتطلبات

- PyQt5 >= 5.15.0
- jinja2 >= 3.0.0
- PyQt5-WebEngine (للمعاينة)

## المساعدة والدعم

للحصول على المساعدة أو الإبلاغ عن مشاكل:

1. تحقق من ملفات السجل في `logs/`
2. راجع الأمثلة في `test_printing_system.py`
3. استخدم الأدوات المساعدة في `print_utils.py`

## أمثلة متقدمة

### إضافة معالج طباعة مخصص

```python
class CustomPrintHandler:
    def __init__(self, page_widget):
        self.page = page_widget
    
    def print_custom_report(self, data):
        # معالجة البيانات
        formatted_data = self.format_data(data)
        
        # طباعة مع معاينة
        print_manager.print_custom_report(
            TemplateType.CUSTOM,
            formatted_data,
            "تقرير مخصص",
            self.page
        )
    
    def format_data(self, data):
        # تنسيق البيانات للطباعة
        return formatted_data
```

هذا النظام يوفر حلاً شاملاً ومرناً لجميع احتياجات الطباعة في التطبيق مع إمكانيات التخصيص والتوسع.
