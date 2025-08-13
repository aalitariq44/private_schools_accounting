# تحديث طباعة الوصولات لعرض بيانات المدرسة الحقيقية

## المشكلة
كانت الوصولات تعرض نصوص ثابتة:
- "عنوان المدرسة:" بدلاً من العنوان الحقيقي
- "للتواصل" بدلاً من أرقام الهاتف الحقيقية

## الحل المطبق

### 1. تحديث استعلام قاعدة البيانات
**الملف:** `ui/pages/students/student_details_page.py`

**التغيير:**
```sql
-- قبل التحديث
SELECT s.*, sc.name_ar as school_name
FROM students s
LEFT JOIN schools sc ON s.school_id = sc.id
WHERE s.id = ?

-- بعد التحديث
SELECT s.*, sc.name_ar as school_name, sc.address as school_address, sc.phone as school_phone
FROM students s
LEFT JOIN schools sc ON s.school_id = sc.id
WHERE s.id = ?
```

### 2. تحديث بيانات الوصل
**الملف:** `ui/pages/students/student_details_page.py`

**في دالة `print_installment`:**
```python
receipt = {
    'id': inst[0],
    'installment_id': inst[0],
    'student_name': self.name_label.text(),
    'school_name': self.school_label.text(),
    'school_address': self.student_data[-2] if self.student_data and len(self.student_data) > 2 else '',
    'school_phone': self.student_data[-1] if self.student_data and len(self.student_data) > 1 else '',
    # ... باقي البيانات
}
```

**في دالة `print_details`:**
```python
student = {
    'id': self.student_id,
    'name': self.name_label.text(),
    'school_name': self.school_label.text(),
    'school_address': self.student_data[-2] if self.student_data and len(self.student_data) > 2 else '',
    'school_phone': self.student_data[-1] if self.student_data and len(self.student_data) > 1 else '',
    # ... باقي البيانات
}
```

### 3. تحديث مدير طباعة ReportLab
**الملف:** `core/printing/reportlab_print_manager.py`

**استخراج البيانات:**
```python
def _draw_receipt(self, c, data, top_y):
    receipt_data = data.get('receipt', data)
    student_name = receipt_data.get('student_name', 'غير محدد')
    amount = receipt_data.get('amount', 0)
    payment_date = receipt_data.get('payment_date', datetime.now().strftime('%Y-%m-%d'))
    installment_number = receipt_data.get('installment_number', 1)
    school_name = receipt_data.get('school_name', 'المدرسة')
    school_address = receipt_data.get('school_address', '')  # إضافة جديدة
    school_phone = receipt_data.get('school_phone', '')     # إضافة جديدة
    # ... باقي البيانات
```

**عرض البيانات في الوصل:**
```python
# استخدام عنوان المدرسة الحقيقي أو نص افتراضي
school_address_text = school_address if school_address else "عنوان المدرسة:"
school_phone_text = school_phone if school_phone else "للتواصل"

text1 = self.reshape_arabic_text(school_address_text)
text2 = self.reshape_arabic_text(school_phone_text)
c.setFont(self.arabic_bold_font, 10)
c.drawCentredString(self.page_width / 2, divider_y + 6 * mm, text1)
c.setFont(self.arabic_font, 9)
c.drawCentredString(self.page_width / 2, divider_y + 3 * mm, text2)
```

## النتائج

### 🎯 المدارس التي لديها عنوان وهاتف:
- **المدرسة:** ثانوية مريم الاهلية
- **العنوان:** البصرة - الهارثة حي الانتصار - شارع المدرسة
- **الهاتف:** 07710995922 - 07710995944
- **النتيجة:** ستظهر البيانات الحقيقية في الوصل

### 📋 المدارس التي ليس لديها عنوان أو هاتف:
- **المدرسة:** مدرسة مريم الابتدائية
- **العنوان:** NULL/فارغ
- **الهاتف:** NULL/فارغ
- **النتيجة:** ستظهر النصوص الافتراضية:
  - "عنوان المدرسة:"
  - "للتواصل"

## الميزات الجديدة

✅ **عرض بيانات المدرسة الحقيقية** عند توفرها
✅ **النصوص الافتراضية** عند عدم توفر البيانات
✅ **دعم كامل للتوافق العكسي** مع المدارس التي لا تحتوي بيانات
✅ **تحديث تلقائي** للوصولات القديمة والجديدة
✅ **عدم كسر** أي وظائف موجودة

## طريقة الاختبار

1. **طباعة وصل لطالب من ثانوية مريم الاهلية** → ستظهر البيانات الحقيقية
2. **طباعة وصل لطالب من مدرسة مريم الابتدائية** → ستظهر النصوص الافتراضية
3. **التأكد من عمل** الطباعة بشكل طبيعي لجميع الحالات

## ملاحظات مهمة

- ⚠️ **لا يلزم تحديث** أي بيانات موجودة في قاعدة البيانات
- 🔄 **التحديث تلقائي** عند إضافة عنوان وهاتف لأي مدرسة
- 📱 **يعمل مع** جميع أنواع الطباعة (وصولات أقساط، تقارير طلاب)
- 🛡️ **آمن تماماً** ولا يؤثر على البيانات الموجودة

## تاريخ التحديث
**التاريخ:** 13 أغسطس 2025  
**الإصدار:** 1.0  
**المطور:** GitHub Copilot
