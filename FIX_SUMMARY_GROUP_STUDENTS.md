# إصلاح مشكلة إضافة الطلاب في نافذة إضافة مجموعة الطلاب

## المشاكل التي تم اكتشافها وإصلاحها:

### 1. مشكلة اسم العمود في قاعدة البيانات
**المشكلة**: الكود يحاول إدراج البيانات في عمود `full_name` لكن الجدول يحتوي على عمود `name`
```sql
-- خطأ قبل الإصلاح
INSERT INTO students (full_name, school_id, grade, section, phone, total_fee, start_date, status, gender)

-- صحيح بعد الإصلاح  
INSERT INTO students (name, school_id, grade, section, phone, total_fee, start_date, status, gender)
```

### 2. مشكلة في الإشارة إلى عنصر واجهة غير موجود
**المشكلة**: الكود يشير إلى `self.section_input` لكن العنصر الصحيح هو `self.section_combo`
```python
# خطأ قبل الإصلاح
section = self.section_input.text().strip()

# صحيح بعد الإصلاح
section = self.section_combo.currentData()
```

## الملفات التي تم تعديلها:
- `ui/pages/students/add_group_students_dialog.py` (سطرين من التعديل)

## النتيجة:
الآن يجب أن تعمل نافذة إضافة مجموعة الطلاب بشكل صحيح ويتم حفظ الطلاب في قاعدة البيانات بنجاح.

## كيفية الاختبار:
1. شغل التطبيق الرئيسي: `python main.py`
2. انتقل إلى صفحة الطلاب
3. انقر على زر "إضافة مجموعة طلاب"
4. املأ البيانات المطلوبة
5. أضف أسماء الطلاب
6. انقر على "حفظ المجموعة"

المتوقع: حفظ الطلاب بنجاح وظهور رسالة تأكيد.
