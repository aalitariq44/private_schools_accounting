# مخطط قاعدة البيانات - نظام حسابات المدارس الأهلية

## نظرة عامة

قاعدة البيانات مصممة باستخدام SQLite وتحتوي على 6 جداول رئيسية لإدارة المدارس والطلاب والأقساط والرسوم الإضافية.

## الجداول والحقول

### 1. جدول المستخدمين (users)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,    -- المعرف الفريد
    username TEXT UNIQUE NOT NULL DEFAULT 'admin',  -- اسم المستخدم
    password_hash TEXT NOT NULL,             -- كلمة المرور المشفرة
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- تاريخ الإنشاء
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- تاريخ آخر تحديث
);
```

**الغرض**: تخزين بيانات المستخدمين المخولين لاستخدام النظام
**ملاحظات**: 
- يحتوي على مستخدم واحد افتراضي (admin)
- كلمات المرور مشفرة باستخدام bcrypt
- يمكن توسيعه لاحقاً لدعم عدة مستخدمين

### 2. جدول المدارس (schools)

```sql
CREATE TABLE schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,    -- المعرف الفريد
    name_ar TEXT NOT NULL,                   -- الاسم بالعربية
    name_en TEXT,                           -- الاسم بالإنجليزية
    logo_path TEXT,                         -- مسار شعار المدرسة
    address TEXT,                           -- عنوان المدرسة
    phone TEXT,                             -- رقم الهاتف
    principal_name TEXT,                    -- اسم المدير
    school_types TEXT NOT NULL,             -- أنواع المدرسة (JSON)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**الغرض**: تخزين معلومات المدارس الأهلية
**ملاحظات**:
- `school_types` يحتوي على مصفوفة JSON للأنواع: ["ابتدائية", "متوسطة", "إعدادية"]
- `logo_path` يحتوي على مسار الشعار في مجلد uploads/school_logos/

**أمثلة على school_types**:
```json
["ابتدائية"]
["متوسطة", "إعدادية"] 
["ابتدائية", "متوسطة", "إعدادية"]
```

### 3. جدول الطلاب (students)

```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,    -- المعرف الفريد
    full_name TEXT NOT NULL,                 -- الاسم الكامل للطالب
    school_id INTEGER NOT NULL,              -- معرف المدرسة
    grade TEXT NOT NULL,                     -- الصف الدراسي
    section TEXT NOT NULL,                   -- الشعبة
    gender TEXT NOT NULL,                    -- الجنس (ذكر/أنثى)
    phone TEXT,                              -- رقم الهاتف
    total_fee DECIMAL(10,2) NOT NULL,        -- القسط الكلي
    start_date DATE NOT NULL,                -- تاريخ المباشرة
    status TEXT DEFAULT 'نشط',               -- الحالة
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
);
```

**الغرض**: تخزين معلومات الطلاب
**ملاحظات**:
- مرتبط بجدول المدارس عبر `school_id`
- حذف المدرسة يؤدي لحذف جميع طلابها تلقائياً
- `grade` يعتمد على نوع المدرسة:

**الصفوف المتاحة حسب النوع**:
- **ابتدائية**: الأول الابتدائي، الثاني الابتدائي، ... السادس الابتدائي
- **متوسطة**: الأول المتوسط، الثاني المتوسط، الثالث المتوسط  
- **إعدادية**: الرابع العلمي، الرابع الأدبي، الخامس العلمي، الخامس الأدبي، السادس العلمي، السادس الأدبي

**الشعب المتاحة**: أ، ب، ج، د، هـ، و، ز، ح، ط، ي

### 4. جدول الأقساط (installments)

```sql
CREATE TABLE installments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,    -- المعرف الفريد
    student_id INTEGER NOT NULL,            -- معرف الطالب
    amount DECIMAL(10,2) NOT NULL,          -- مبلغ الدفعة
    payment_date DATE NOT NULL,             -- تاريخ الدفعة
    payment_time TIME NOT NULL,             -- وقت الدفعة
    notes TEXT,                             -- ملاحظات اختيارية
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
```

**الغرض**: تسجيل دفعات الأقساط
**ملاحظات**:
- مرتبط بجدول الطلاب عبر `student_id`
- حذف الطالب يؤدي لحذف جميع أقساطه
- يتم تسجيل التاريخ والوقت الدقيق لكل دفعة
- يمكن حساب المتبقي من خلال: (إجمالي قسط الطالب - مجموع دفعاته)

### 5. جدول الرسوم الإضافية (additional_fees)

```sql
CREATE TABLE additional_fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,    -- المعرف الفريد
    student_id INTEGER NOT NULL,            -- معرف الطالب
    fee_type TEXT NOT NULL,                 -- نوع الرسم
    amount DECIMAL(10,2) NOT NULL,          -- مبلغ الرسم
    due_date DATE,                          -- تاريخ الاستحقاق
    paid BOOLEAN DEFAULT FALSE,             -- حالة الدفع
    payment_date DATE,                      -- تاريخ الدفع
    notes TEXT,                             -- ملاحظات
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
```

**الغرض**: إدارة الرسوم الإضافية (غير الأكاديمية)
**أنواع الرسوم المتاحة**:
- رسوم التسجيل
- الزي المدرسي  
- الكتب
- القرطاسية
- رسم مخصص (أي نوع آخر)

**ملاحظات**:
- `paid`: FALSE = غير مدفوع، TRUE = مدفوع
- `payment_date` يتم ملؤه عند تسجيل الدفع

### 6. جدول إعدادات التطبيق (app_settings)

```sql
CREATE TABLE app_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,    -- المعرف الفريد
    setting_key TEXT UNIQUE NOT NULL,       -- مفتاح الإعداد
    setting_value TEXT,                     -- قيمة الإعداد
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**الغرض**: تخزين إعدادات التطبيق العامة
**أمثلة على الإعدادات**:
- backup_enabled: تفعيل النسخ الاحتياطي
- backup_interval: فترة النسخ الاحتياطي
- last_backup_date: تاريخ آخر نسخة احتياطية
- app_theme: قالب التطبيق

## الفهارس (Indexes)

```sql
-- فهارس الطلاب
CREATE INDEX idx_students_school_id ON students(school_id);
CREATE INDEX idx_students_name ON students(full_name);
CREATE INDEX idx_students_grade ON students(grade);

-- فهارس الأقساط  
CREATE INDEX idx_installments_student_id ON installments(student_id);
CREATE INDEX idx_installments_payment_date ON installments(payment_date);

-- فهارس الرسوم الإضافية
CREATE INDEX idx_additional_fees_student_id ON additional_fees(student_id);
CREATE INDEX idx_additional_fees_paid ON additional_fees(paid);
CREATE INDEX idx_additional_fees_due_date ON additional_fees(due_date);
```

**الغرض**: تحسين أداء الاستعلامات وتسريع البحث

## العلاقات بين الجداول

```
users (مستقل)

schools (1) ←→ (∞) students
    ↓
students (1) ←→ (∞) installments
    ↓  
students (1) ←→ (∞) additional_fees

app_settings (مستقل)
```

### شرح العلاقات:
1. **schools → students**: كل مدرسة يمكن أن تحتوي على عدة طلاب
2. **students → installments**: كل طالب يمكن أن يكون له عدة دفعات
3. **students → additional_fees**: كل طالب يمكن أن يكون له عدة رسوم إضافية

### سياسة الحذف المتسلسل:
- حذف مدرسة → حذف جميع طلابها → حذف جميع أقساطهم ورسومهم
- حذف طالب → حذف جميع أقساطه ورسومه الإضافية

## استعلامات شائعة

### 1. الحصول على إحصائيات سريعة
```sql
-- عدد المدارس
SELECT COUNT(*) FROM schools;

-- عدد الطلاب
SELECT COUNT(*) FROM students;

-- إجمالي الأقساط
SELECT SUM(total_fee) FROM students;

-- المبالغ المدفوعة
SELECT SUM(amount) FROM installments;

-- المبالغ المتبقية
SELECT 
    SUM(s.total_fee) - COALESCE(SUM(i.amount), 0) as remaining
FROM students s
LEFT JOIN installments i ON s.id = i.student_id;
```

### 2. تفاصيل طالب مع أقساطه
```sql
SELECT 
    s.name,
    s.total_fee,
    COALESCE(SUM(i.amount), 0) as paid_amount,
    s.total_fee - COALESCE(SUM(i.amount), 0) as remaining_amount,
    COUNT(i.id) as installments_count
FROM students s
LEFT JOIN installments i ON s.id = i.student_id
WHERE s.id = ?
GROUP BY s.id;
```

### 3. طلاب مدرسة معينة
```sql
SELECT 
    s.full_name,
    s.grade,
    s.section,
    s.total_fee,
    sc.name_ar as school_name
FROM students s
JOIN schools sc ON s.school_id = sc.id
WHERE sc.id = ?
ORDER BY s.grade, s.section, s.full_name;
```

### 4. الأقساط في فترة معينة
```sql
SELECT 
    i.payment_date,
    i.amount,
    s.full_name as student_name,
    sc.name_ar as school_name
FROM installments i
JOIN students s ON i.student_id = s.id
JOIN schools sc ON s.school_id = sc.id
WHERE i.payment_date BETWEEN ? AND ?
ORDER BY i.payment_date DESC;
```

## نصائح للصيانة

### 1. تنظيف البيانات:
```sql
-- حذف الإعدادات غير المستخدمة
DELETE FROM app_settings WHERE setting_value IS NULL OR setting_value = '';

-- تحديث التواريخ المتأخرة
UPDATE additional_fees SET updated_at = CURRENT_TIMESTAMP WHERE updated_at < created_at;
```

### 2. إعادة بناء الفهارس:
```sql
REINDEX;
```

### 3. تحسين قاعدة البيانات:
```sql
VACUUM;
ANALYZE;
```

### 4. النسخ الاحتياطي:
- يُنصح بإنشاء نسخة احتياطية يومية من ملف `schools.db`
- احتفظ بعدة نسخ في أماكن مختلفة
- اختبر استعادة النسخة الاحتياطية دورياً

## أمان البيانات

### 1. تشفير كلمات المرور:
- استخدام bcrypt مع salt عشوائي
- 100,000 تكرار للتشفير
- عدم تخزين كلمات المرور بصيغة واضحة أبداً

### 2. حماية قاعدة البيانات:
- تفعيل المفاتيح الأجنبية (PRAGMA foreign_keys = ON)
- استخدام المعاملات للعمليات المتعددة
- التحقق من صحة البيانات قبل الإدخال

### 3. سجلات العمليات:
- تسجيل جميع العمليات المهمة في ملفات السجلات
- تتبع محاولات تسجيل الدخول
- رصد العمليات المشبوهة
