# نظام حسابات المدارس الأهلية

نظام شامل لإدارة الحسابات المالية للمدارس الأهلية مطور باستخدام Python و PyQt5.

## بنية المشروع

```
private_schools_accounting/
├── 📁 app/                    # التطبيق الرئيسي
├── 📁 core/                   # الوحدات الأساسية
├── 📁 ui/                     # واجهات المستخدم
├── 📁 data/                   # ملفات البيانات
├── 📁 docs/                   # التوثيق
├── 📁 logs/                   # ملفات السجلات
├── 📁 test data/              # بيانات الاختبار
├── 📄 main.py                 # نقطة بداية التطبيق
├── 📄 config.py               # إعدادات التطبيق
├── 📄 requirements.txt        # متطلبات Python
├── 📄 setup.py                # إعداد التطبيق
├── 📄 create_db.py            # إنشاء قاعدة البيانات
└── 📄 hashlib_patch.py        # إصلاحات hashlib
```

## الملفات الرئيسية

### ملفات التشغيل
- `main.py` - نقطة البداية الرئيسية للتطبيق
- `run.bat` - ملف تشغيل التطبيق على Windows
- `install.bat` - تثبيت المتطلبات

### ملفات الإعداد
- `config.py` - إعدادات التطبيق العامة
- `setup.py` - إعداد وتثبيت التطبيق
- `requirements.txt` - قائمة المكتبات المطلوبة

### ملفات قاعدة البيانات
- `create_db.py` - إنشاء قاعدة البيانات الأولية
- `supabase_permissions.sql` - صلاحيات قاعدة البيانات

### ملفات الطباعة والتكوين
- `printing_config.json` - إعدادات الطباعة
- `build_config.json` - إعدادات البناء
- `build_distribution.spec` - ملف PyInstaller للتوزيع
- `build_pro.spec` - ملف PyInstaller الاحترافي

### ملفات التوثيق
- `BUILD_GUIDE.md` - دليل بناء التطبيق
- `PRINT_FIX_README.md` - دليل إصلاحات الطباعة
- `RESPONSIVE_DESIGN_GUIDE.md` - دليل التصميم المتجاوب
- `SECURITY_UPDATES.md` - تحديثات الأمان
- `QUICK_USER_GUIDE_AUTO_BACKUP.md` - دليل النسخ الاحتياطي
- `ADVANCED_EDIT_FEATURE.md` - ميزات التحرير المتقدمة
- `AUTO_BACKUP_ON_EXIT_FEATURE.md` - ميزة النسخ الاحتياطي عند الخروج
- `DESIGN_IMPROVEMENTS.md` - تحسينات التصميم

## متطلبات التشغيل

```
Python 3.8+
PyQt5 >= 5.15.0
PyQt5-tools
PyQtWebEngine >= 5.15.0
python-dotenv >= 1.0.0
bcrypt >= 4.0.0
Pillow >= 10.0.0
reportlab >= 4.0.0
jinja2 >= 3.1.0
supabase >= 2.3.0
storage3 >= 0.7.0
arabic-reshaper >= 3.0.0
python-bidi >= 0.4.0
```

## التثبيت والتشغيل

### 1. تثبيت المتطلبات
```bash
# Windows
install.bat

# أو يدوياً
pip install -r requirements.txt
```

### 2. إعداد قاعدة البيانات
```bash
python create_db.py
```

### 3. تشغيل التطبيق
```bash
# Windows
run.bat

# أو يدوياً
python main.py
```

## المميزات الرئيسية

- ✅ إدارة بيانات الطلاب والموظفين
- ✅ نظام الرسوم والمدفوعات
- ✅ إدارة الرواتب والمصروفات
- ✅ تقارير مالية شاملة
- ✅ طباعة وثائق PDF
- ✅ نسخ احتياطي تلقائي
- ✅ واجهة عربية متجاوبة
- ✅ أمان البيانات

## إصدار التطبيق

الإصدار الحالي محفوظ في `version_info.txt`

## الدعم والمساعدة

راجع ملفات التوثيق في مجلد `docs/` للحصول على معلومات مفصلة حول استخدام النظام.

---

تم تطوير هذا النظام خصيصاً لإدارة حسابات المدارس الأهلية بطريقة احترافية وآمنة.
