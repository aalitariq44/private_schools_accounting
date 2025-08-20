# إصلاح مشكلة ترتيب المعرف في جدول الطلاب

## المشكلة
عند النقر على عمود "المعرف" للترتيب، كان الترتيب يتم كنص وليس كأرقام، مما يؤدي إلى ظهور:
- 1, 10, 100, 101, 102, 103...
بدلاً من الترتيب الصحيح:
- 1, 2, 3, 4, 5, 6, 7, 8, 9, 10...

## الحل المطبق

### 1. إنشاء فئة مخصصة لعناصر الجدول الرقمية
```python
class NumericTableWidgetItem(QTableWidgetItem):
    """عنصر جدول مخصص للترتيب الرقمي"""
    
    def __init__(self, text, numeric_value=None):
        super().__init__(text)
        if numeric_value is not None:
            self.setData(Qt.UserRole, numeric_value)
        else:
            # محاولة استخراج القيمة الرقمية من النص
            try:
                clean_text = text.replace(',', '').replace('د.ع', '').strip()
                numeric_value = float(clean_text) if clean_text else 0
                self.setData(Qt.UserRole, numeric_value)
            except:
                self.setData(Qt.UserRole, 0)
    
    def __lt__(self, other):
        """مقارنة مخصصة للترتيب الرقمي"""
        try:
            self_data = self.data(Qt.UserRole)
            other_data = other.data(Qt.UserRole)
            
            if self_data is not None and other_data is not None:
                if isinstance(self_data, (int, float)) and isinstance(other_data, (int, float)):
                    return float(self_data) < float(other_data)
            
            return super().__lt__(other)
        except:
            return super().__lt__(other)
```

### 2. تطبيق الفئة المخصصة في دالة ملء الجدول
تم تحديث الكود في `students_page.py` ليستخدم `NumericTableWidgetItem` للأعمدة الرقمية:
- عمود المعرف (col_idx == 0)
- أعمدة المبالغ (col_idx in [8, 9, 10]) للرسوم، المدفوع، والمتبقي

### 3. النتيجة
الآن عند النقر على عمود المعرف، سيتم الترتيب رقمياً بالطريقة الصحيحة:
1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11...

## الملفات المحدثة
- `ui/pages/students/students_page.py`: إضافة الفئة المخصصة وتحديث دالة ملء الجدول

## اختبار الإصلاح
تم إنشاء ملف اختبار `test_sorting_fix.py` للتحقق من عمل الحل بشكل صحيح.

التاريخ: 20 أغسطس 2025
