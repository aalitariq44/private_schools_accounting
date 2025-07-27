# كيفية إضافة نظام الطباعة لأي صفحة في التطبيق

## خطوات سريعة للإضافة

### 1. استيراد النظام

```python
# في أعلى ملف الصفحة
from core.printing import print_manager, PrintHelper, QuickPrintMixin, apply_print_styles
```

### 2. وراثة QuickPrintMixin

```python
class YourPage(QWidget, QuickPrintMixin):
    def __init__(self):
        super().__init__()
        self.setup_quick_print()  # إضافة هذا السطر
        # باقي الكود...
```

### 3. إضافة أزرار الطباعة

```python
def create_toolbar(self, layout):
    # ... باقي الأزرار
    
    # أزرار الطباعة
    self.print_button = QPushButton("طباعة القائمة")
    self.print_button.setObjectName("printButton")
    self.print_button.clicked.connect(self.print_current_list)
    layout.addWidget(self.print_button)
    
    self.quick_print_button = QPushButton("طباعة سريعة")
    self.quick_print_button.setObjectName("quickPrintButton")
    self.quick_print_button.clicked.connect(self.quick_print_current_data)
    layout.addWidget(self.quick_print_button)
    
    self.export_pdf_button = QPushButton("تصدير PDF")
    self.export_pdf_button.setObjectName("exportButton")
    self.export_pdf_button.clicked.connect(self.export_to_pdf)
    layout.addWidget(self.export_pdf_button)
```

### 4. إضافة وظائف الطباعة

```python
def print_current_list(self):
    """طباعة القائمة الحالية مع معاينة"""
    try:
        if not self.current_data:
            QMessageBox.warning(self, "تحذير", "لا توجد بيانات للطباعة")
            return
        
        # تنسيق البيانات للطباعة
        formatted_data = PrintHelper.format_students_list_for_print(self.current_data)
        
        # معلومات الفلاتر
        filter_info = self.get_current_filters_info()
        
        # طباعة مع معاينة
        print_manager.print_students_list(formatted_data, filter_info, self)
        
    except Exception as e:
        QMessageBox.critical(self, "خطأ", f"حدث خطأ في الطباعة: {str(e)}")

def export_to_pdf(self):
    """تصدير إلى PDF"""
    try:
        if not self.current_data:
            QMessageBox.warning(self, "تحذير", "لا توجد بيانات للتصدير")
            return
        
        from PyQt5.QtWidgets import QFileDialog
        from core.printing import TemplateType
        
        # اختيار مكان الحفظ
        file_path, _ = QFileDialog.getSaveFileName(
            self, "حفظ التقرير", 
            f"تقرير_{len(self.current_data)}_عنصر.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            formatted_data = PrintHelper.format_students_list_for_print(self.current_data)
            filter_info = self.get_current_filters_info()
            
            data = {
                'students': formatted_data,
                'filter_info': filter_info
            }
            
            print_manager.export_to_pdf(TemplateType.STUDENT_LIST, data, file_path, self)
            
    except Exception as e:
        QMessageBox.critical(self, "خطأ", f"حدث خطأ في التصدير: {str(e)}")

# وظائف مطلوبة من QuickPrintMixin
def get_current_data_for_print(self):
    """إرجاع البيانات الحالية للطباعة السريعة"""
    return PrintHelper.format_students_list_for_print(self.current_data)

def get_current_filters_info(self):
    """إرجاع معلومات الفلاتر الحالية"""
    filters = {
        'school': getattr(self, 'school_combo', None) and self.school_combo.currentText(),
        'grade': getattr(self, 'grade_combo', None) and self.grade_combo.currentText(),
        'status': getattr(self, 'status_combo', None) and self.status_combo.currentText(),
        'search': getattr(self, 'search_input', None) and self.search_input.text().strip()
    }
    return PrintHelper.create_filter_info_string(filters)
```

### 5. إضافة التنسيقات

```python
def setup_styles(self):
    base_style = """
        /* تنسيقاتك الأساسية */
    """
    
    # إضافة تنسيقات الطباعة
    full_style = base_style + apply_print_styles()
    self.setStyleSheet(full_style)
```

### 6. أمثلة لأنواع مختلفة من الطباعة

#### طباعة تقرير طالب واحد

```python
def print_student_report(self, student_id):
    """طباعة تقرير طالب واحد"""
    try:
        # جلب بيانات الطالب
        student_data = self.get_student_by_id(student_id)
        
        if student_data:
            formatted_data = PrintHelper.format_student_data_for_print(student_data)
            print_manager.print_student_report(formatted_data, self)
        else:
            QMessageBox.warning(self, "خطأ", "لم يتم العثور على بيانات الطالب")
            
    except Exception as e:
        QMessageBox.critical(self, "خطأ", f"خطأ في طباعة التقرير: {str(e)}")
```

#### طباعة إيصال دفع

```python
def print_payment_receipt(self, payment_data):
    """طباعة إيصال دفع"""
    try:
        receipt_data = {
            'id': payment_data.get('id'),
            'student_name': payment_data.get('student_name'),
            'school_name': payment_data.get('school_name'),
            'payment_date': payment_data.get('payment_date'),
            'payment_method': payment_data.get('payment_method'),
            'description': payment_data.get('description'),
            'amount': payment_data.get('amount')
        }
        
        print_manager.print_payment_receipt(receipt_data, self)
        
    except Exception as e:
        QMessageBox.critical(self, "خطأ", f"خطأ في طباعة الإيصال: {str(e)}")
```

### 7. تخصيص القوالب

إذا كنت تريد قالب مخصص:

```python
# في template_manager.py يمكنك إضافة قالب جديد
def get_custom_template(self):
    return """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>قالب مخصص</title>
        <style>
            body { font-family: Arial; direction: rtl; }
            .header { text-align: center; border-bottom: 2px solid #333; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{{ title }}</h1>
            <p>{{ date }}</p>
        </div>
        <div class="content">
            <!-- محتواك هنا -->
        </div>
    </body>
    </html>
    """
```

## مميزات النظام

- ✅ **معاينة قبل الطباعة** مع إعدادات متقدمة
- ✅ **طباعة سريعة** بدون معاينة
- ✅ **تصدير PDF** مباشر
- ✅ **قوالب HTML** قابلة للتخصيص
- ✅ **تنسيقات جاهزة** لجميع الأزرار
- ✅ **معالجة الأخطاء** تلقائياً
- ✅ **دعم العربية** كامل
- ✅ **سهولة الإضافة** لأي صفحة

## نصائح مهمة

1. **تأكد من البيانات**: استخدم `PrintHelper.validate_print_data()` للتحقق من البيانات
2. **معالجة الأخطاء**: ضع دائماً وظائف الطباعة في `try-except`
3. **تنسيق البيانات**: استخدم `PrintHelper.format_*_for_print()` لتنسيق البيانات
4. **الفلاتر**: وضح الفلاتر المطبقة في التقارير
5. **الأداء**: لا تحمّل بيانات كبيرة للطباعة دفعة واحدة

هذا النظام سيعطيك طباعة احترافية في دقائق قليلة!
