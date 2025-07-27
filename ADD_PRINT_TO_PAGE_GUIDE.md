# دليل إضافة الطباعة لصفحة جديدة - 5 دقائق ⚡

## الخطوة 1: الاستيرادات الأساسية

```python
# في بداية ملف صفحتك الجديدة
from core.printing import print_manager, QuickPrintMixin, apply_print_styles, TemplateType
```

## الخطوة 2: تحديث كلاس الصفحة

```python
# تغيير هذا:
class MyPage(QWidget):

# إلى هذا:
class MyPage(QWidget, QuickPrintMixin):
```

## الخطوة 3: في دالة __init__

```python
def __init__(self):
    super().__init__()
    # باقي الكود الموجود...
    
    self.setup_quick_print()  # إضافة هذا السطر
```

## الخطوة 4: إضافة أزرار الطباعة

```python
def create_print_buttons(self):
    """إضافة أزرار الطباعة في أي مكان في صفحتك"""
    
    # زر طباعة سريعة (يطبع البيانات الحالية)
    quick_print_btn = QPushButton("طباعة سريعة")
    quick_print_btn.clicked.connect(self.quick_print_current_data)
    
    # زر طباعة قائمة مخصصة
    custom_print_btn = QPushButton("طباعة التقرير")
    custom_print_btn.clicked.connect(self.print_custom_report)
    
    return quick_print_btn, custom_print_btn
```

## الخطوة 5: الوظائف المطلوبة

```python
def get_current_data_for_print(self):
    """البيانات الحالية للطباعة السريعة"""
    return self.your_data_list  # قائمة بياناتك الحالية

def get_current_filters_info(self):
    """معلومات الفلاتر المطبقة"""
    return "الفلاتر المطبقة هنا"  # أو "" إذا لم تكن تستخدم فلاتر
```

## الخطوة 6: وظائف الطباعة المخصصة

```python
def print_custom_report(self):
    """طباعة تقرير مخصص"""
    try:
        # تحضير البيانات
        data = {
            'items': self.your_data_list,
            'title': 'عنوان التقرير',
            'total': len(self.your_data_list)
        }
        
        # طباعة باستخدام قالب موجود
        print_manager.print_students_list(data, self)  # أو أي نوع آخر
        
        # أو إنشاء طباعة مخصصة كلياً
        print_manager.print_custom_report(
            TemplateType.CUSTOM, 
            data, 
            "عنوان التقرير", 
            self
        )
        
    except Exception as e:
        QMessageBox.critical(self, "خطأ", f"خطأ في الطباعة: {str(e)}")
```

## الخطوة 7: إضافة التنسيقات

```python
def setup_styles(self):
    """في نهاية دالة التنسيقات الموجودة"""
    
    base_style = """
        /* تنسيقاتك الموجودة */
    """
    
    # إضافة تنسيقات الطباعة
    full_style = base_style + apply_print_styles()
    self.setStyleSheet(full_style)
```

---

## أمثلة سريعة لأنواع مختلفة من الطباعة:

### 1. طباعة قائمة طلاب:
```python
student_data = {'students': self.students_list, 'total': len(self.students_list)}
print_manager.print_students_list(student_data, self)
```

### 2. طباعة إيصال دفع:
```python
receipt_data = {
    'id': 'REC-001',
    'student_name': 'أحمد محمد',
    'amount': 500000,
    'payment_date': '2024-01-15'
}
print_manager.print_payment_receipt(receipt_data, self)
```

### 3. طباعة تقرير مالي:
```python
financial_data = {
    'total_income': 1000000,
    'total_expenses': 600000,
    'transactions': self.transactions_list
}
print_manager.print_financial_report(financial_data, "كانون الثاني 2024", self)
```

### 4. تصدير PDF:
```python
file_path = "C:/Users/Desktop/report.pdf"
print_manager.export_to_pdf(TemplateType.STUDENTS_LIST, data, file_path, self)
```

---

## نصائح مهمة:

✅ **تأكد من تشغيل setup_printing_system.py أولاً**

✅ **استخدم QuickPrintMixin لطباعة سريعة**

✅ **تحقق من وجود البيانات قبل الطباعة**

✅ **استخدم try/except دائماً مع وظائف الطباعة**

✅ **راجع الأمثلة في financial_page_print_example.py**

---

## إذا واجهت مشاكل:

1. تأكد من تشغيل: `python setup_printing_system.py`
2. راجع ملف: `PRINTING_SYSTEM_GUIDE.md`
3. جرب المثال: `python printing_usage_example.py`
4. شغل اختبار: `python test_printing_system.py`
