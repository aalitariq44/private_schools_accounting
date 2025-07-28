# تحديث نظام الطباعة إلى محرك حديث

## المشكلة
كان نظام الطباعة القديم يستخدم `QTextDocument` الذي لا يدعم جميع ميزات CSS الحديثة، مما يؤدي إلى:
- عدم دعم كامل لقواعد `@page` و `@media print`
- تشويه في التخطيط والجداول
- عدم دعم كامل للطباعة متعددة الصفحات
- ضعف في دعم الخطوط العربية المتقدمة

## الحل الجديد
تم إضافة نظام طباعة محدث يستخدم `QWebEngineView` الذي يعتمد على محرك Chromium ويوفر:
- دعماً كاملاً لجميع ميزات CSS الحديثة
- تخطيط مثالي للجداول والعناصر
- دعم ممتاز للخطوط العربية
- إمكانية حفظ كـ PDF مباشرة
- طباعة عالية الجودة

## التثبيت

### 1. تحديث المتطلبات
```bash
pip install PyQtWebEngine==5.15.6
```

### 2. إعادة تشغيل التطبيق
بعد تثبيت المكتبة الجديدة، أعد تشغيل التطبيق.

## الاستخدام

### الطريقة الجديدة (محرك حديث)
```python
from core.printing import web_print_payment_receipt

# طباعة إيصال دفع بالمحرك الحديث
web_print_payment_receipt(receipt_data, parent=self)
```

### الطريقة التقليدية (للتوافق مع الأنظمة القديمة)
```python  
from core.printing import print_payment_receipt

# طباعة بالمحرك التقليدي
print_payment_receipt(receipt_data, parent=self, use_web_engine=False)

# طباعة بالمحرك الحديث (افتراضي)
print_payment_receipt(receipt_data, parent=self, use_web_engine=True)
```

### التبديل بين المحركين
```python
from core.printing import PrintManager

pm = PrintManager()
# التحقق من توفر المحرك الحديث
if pm.toggle_engine():
    print("تم تغيير المحرك بنجاح")
```

## الميزات الجديدة

### 1. معاينة محسنة
- عرض دقيق كما سيظهر في الطباعة
- دعم كامل للألوان والحدود
- تخطيط مثالي للجداول

### 2. حفظ PDF
- إمكانية حفظ الإيصالات كملفات PDF عالية الجودة
- احتفاظ كامل بالتنسيق والألوان

### 3. طباعة متقدمة
- دعم كامل لـ `page-break`
- هوامش دقيقة
- جودة طباعة عالية

## ملاحظات مهمة

### التوافق
- النظام يدعم كلا المحركين للتوافق مع الأنظمة المختلفة
- إذا لم يكن المحرك الحديث متوفراً، سيعمل المحرك التقليدي تلقائياً

### الأداء
- المحرك الحديث قد يستغرق وقتاً أطول قليلاً في التحميل الأولي
- لكنه يوفر جودة أفضل بكثير في النتيجة النهائية

### استكشاف الأخطاء
إذا واجهت مشاكل:

1. **خطأ في الاستيراد**: تأكد من تثبيت PyQtWebEngine
2. **بطء في التحميل**: هذا طبيعي للمرة الأولى
3. **مشاكل في العرض**: تحقق من إعدادات CSS في القالب

## مثال كامل للاستخدام

```python
# في ملف الطلاب مثلاً
from core.printing import WEB_ENGINE_AVAILABLE, web_print_payment_receipt, print_payment_receipt

def print_receipt(self, receipt_data):
    if WEB_ENGINE_AVAILABLE:
        # استخدام المحرك الحديث
        web_print_payment_receipt(receipt_data, parent=self)
    else:
        # العودة للمحرك التقليدي
        print_payment_receipt(receipt_data, parent=self, use_web_engine=False)
```

## تحديثات CSS للقوالب

تم تحسين قوالب HTML لتعمل بشكل أفضل مع المحرك الجديد:
- إضافة `-webkit-print-color-adjust: exact` للاحتفاظ بالألوان
- تحسين قواعد `@media print` و `@media screen`
- دعم أفضل للجداول والحدود

سيعمل النظام تلقائياً على تطبيق هذه التحسينات عند استخدام المحرك الحديث.
