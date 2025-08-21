# تحديث عرض اسم المدرسة بالعربية والإنجليزية في الإيصالات

## 📋 ملخص التحديثات المنجزة

تم تحديث النظام لإظهار اسم المدرسة بالإنجليزية تحت الاسم العربي في جميع إيصالات الدفع (أقساط ورسوم إضافية).

## 🔧 الملفات المحدثة

### 1. تحديث استعلامات قاعدة البيانات

#### أ. صفحات تفاصيل الطلاب
- **`ui/pages/students/student_details_page.py`** ✅
- **`ui/pages/students/student_details_page_new.py`** ✅
  ```sql
  -- تم إضافة sc.name_en as school_name_en للاستعلام
  SELECT s.*, sc.name_ar as school_name, sc.name_en as school_name_en, 
         sc.address as school_address, sc.phone as school_phone, 
         sc.logo_path as school_logo_path
  FROM students s
  LEFT JOIN schools sc ON s.school_id = sc.id
  WHERE s.id = ?
  ```

#### ب. مكون جدول الأقساط
- **`ui/pages/students/components/installments_table_widget.py`** ✅
  - تحديث دالة `get_school_info()` لإرجاع `name_en`
  - تحديث `print_installment()` لتمرير `school_name_en`

#### ج. نافذة طباعة الرسوم الإضافية
- **`ui/pages/students/additional_fees_print_dialog.py`** ✅
  ```sql
  -- تم إضافة الاسم الإنجليزي للاستعلام
  SELECT s.name, s.grade, s.section, sc.name_ar as school_name, 
         sc.name_en as school_name_en, sc.logo_path as school_logo_path
  FROM students s
  LEFT JOIN schools sc ON s.school_id = sc.id
  WHERE s.id = ?
  ```

### 2. تحديث مدراء الطباعة

#### أ. مدير طباعة إيصالات الأقساط
- **`core/printing/reportlab_print_manager.py`** ✅
  ```python
  # استلام الاسم الإنجليزي
  school_name_en = receipt_data.get('school_name_en', '')
  
  # رسم الاسم العربي
  c.setFont(self.arabic_bold_font, 13)
  school_text = self.reshape_arabic_text(school_name)
  c.drawRightString(self.page_width - self.margin - header_padding, header_y, school_text)
  
  # إضافة الاسم الإنجليزي تحت العربي (إذا وجد)
  if school_name_en and school_name_en.strip():
      c.setFont('Helvetica', 10)
      c.drawRightString(self.page_width - self.margin - header_padding, header_y - 15, school_name_en.strip())
  ```

#### ب. مدير طباعة الرسوم الإضافية
- **`core/printing/additional_fees_print_manager.py`** ✅
  - نفس منطق الرسم المطبق في مدير إيصالات الأقساط

## 🎯 آلية العمل الجديدة

### منطق عرض أسماء المدارس:
1. **الاسم العربي**: يُعرض دائماً في الأعلى بخط عربي كبير (13pt)
2. **الاسم الإنجليزي**: 
   - يُعرض تحت الاسم العربي بخط إنجليزي أصغر (10pt)
   - **فقط إذا كان موجوداً وغير فارغ**
   - إذا لم يوجد اسم إنجليزي → لا يُعرض شيء إضافي

### التموضع:
```
┌─────────────────────────────────────┐
│  🏫 شعار المدرسة         مدرسة الأمل الثانوية  │
│                      Al-Amal Secondary School │
│                               2025-2026       │
└─────────────────────────────────────┘
```

## ✅ نتائج الاختبار

تم إنشاء 4 ملفات PDF للاختبار:

### 1. إيصالات الأقساط:
- ✅ **مع اسم إنجليزي**: `installment_receipt_20250821_084403.pdf`
  - الاسم العربي: "مدرسة الأمل الثانوية"
  - الاسم الإنجليزي: "Al-Amal Secondary School"
  
- ✅ **بدون اسم إنجليزي**: `installment_receipt_20250821_084403.pdf`
  - الاسم العربي فقط: "مدرسة النور الابتدائية"

### 2. إيصالات الرسوم الإضافية:
- ✅ **مع اسم إنجليزي**: `additional_fees_receipt_20250821_084403.pdf`
  - الاسم العربي: "مدرسة الزهراء المتوسطة"
  - الاسم الإنجليزي: "Al-Zahra Middle School"
  
- ✅ **بدون اسم إنجليزي**: `additional_fees_receipt_20250821_084404.pdf`
  - الاسم العربي فقط: "مدرسة الفرات الابتدائية"

## 🎨 مزايا التحديث

1. **مرونة في العرض**: يمكن إضافة أو عدم إضافة اسم إنجليزي حسب المدرسة
2. **عرض تلقائي**: إذا وُجد اسم إنجليزي → يُعرض، وإلا فلا
3. **تناسق في التصميم**: الاسم الإنجليزي مُنسق بخط مناسب وحجم أصغر
4. **سهولة الإدارة**: يتم إدخال الاسم الإنجليزي من صفحة تعديل المدرسة

## 🔄 طريقة إضافة/تعديل الاسم الإنجليزي

1. اذهب إلى صفحة **"المدارس"**
2. اختر المدرسة المطلوبة → **"تعديل"**
3. في حقل **"الاسم بالإنجليزية"**، أدخل الاسم المطلوب
4. اضغط **"حفظ"**

الآن جميع إيصالات هذه المدرسة ستظهر بالاسم العربي والإنجليزي معاً!

## 📝 ملاحظات فنية

- **حجم الخط العربي**: 13pt بخط `Amiri-Bold`
- **حجم الخط الإنجليزي**: 10pt بخط `Helvetica`
- **المسافة بين الأسماء**: 15 نقطة عمودياً
- **موضع النص**: محاذي لليمين (كلا الاسمين)
- **شرط العرض**: `if school_name_en and school_name_en.strip()`

## 🎯 نتيجة التحديث

الآن كل إيصال سيعرض:
- ✅ اسم المدرسة بالعربية (دائماً)
- ✅ اسم المدرسة بالإنجليزية (إذا وُجد فقط)
- ✅ شعار المدرسة (المخصص أو الافتراضي)

مما يجعل الإيصالات أكثر احترافية ووضوحاً للمدارس ثنائية اللغة! 🎉
