# دليل اختبار وإصلاح النسخ الاحتياطي

## المشكلة الحالية
النسخ الاحتياطي يتم رفعها بنجاح على Supabase لكن لا يتم عرضها في قائمة النسخ الاحتياطية. هذا يحدث عادة بسبب:

1. **مشاكل في صلاحيات البكت** - لا يمكن قراءة الملفات المرفوعة
2. **خطأ في مسار البحث** - البحث في مسار مختلف عن مسار الرفع
3. **مشاكل في استراتيجية التخزين** - تضارب بين طريقة الحفظ وطريقة القراءة

## خطوات الاختبار والإصلاح

### 1. تشغيل صفحة الاختبار
```bash
python test_file_upload.py
```

هذه الصفحة ستساعدك في:
- اختبار رفع ملفات بسيطة (txt)
- قراءة الملفات المرفوعة
- التحقق من أن الاتصال يعمل بشكل صحيح

### 2. تنفيذ أوامر SQL في Supabase

1. اذهب إلى لوحة تحكم Supabase
2. اختر مشروعك
3. اذهب إلى **SQL Editor**
4. انسخ والصق الأوامر من ملف `supabase_permissions.sql`
5. نفذ الأوامر واحداً تلو الآخر

**الأوامر المهمة:**
```sql
-- فحص البكت
SELECT * FROM storage.buckets WHERE name = 'schools-backup';

-- فحص الصلاحيات
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename = 'objects' AND schemaname = 'storage';

-- فحص الملفات الموجودة
SELECT name, id, bucket_id, owner, created_at, updated_at, metadata
FROM storage.objects 
WHERE bucket_id = 'schools-backup'
ORDER BY created_at DESC;
```

### 3. إصلاح مدير النسخ الاحتياطي

بعد تشغيل الاختبار، إذا نجح في الرفع والقراءة، المشكلة في `backup_manager.py`:

#### مشاكل محتملة:

1. **البحث في مسار خاطئ:**
   - الرفع يتم في: `backups/{organization_name}/`
   - البحث يتم في مسار مختلف

2. **استراتيجية البحث معقدة:**
   - البحث يحاول عدة طرق مختلفة
   - قد يفشل في العثور على الملفات

3. **مشاكل في parsing البيانات:**
   - استخراج معلومات الملف قد يفشل

### 4. الحل المقترح

إذا نجح الاختبار، سنطبق نفس الاستراتيجية البسيطة على النسخ الاحتياطي:

```python
def list_backups_simple(self):
    """طريقة مبسطة لجلب النسخ الاحتياطية"""
    try:
        # جلب جميع الملفات من البكت
        all_files = self.supabase.storage.from_(self.bucket_name).list("")
        
        backups = []
        for file_item in all_files:
            file_path = file_item.get('name', '')
            
            # البحث عن ملفات النسخ الاحتياطية
            if 'backup_' in file_path and file_path.endswith('.zip'):
                backup_info = {
                    'filename': os.path.basename(file_path),
                    'path': file_path,
                    'created_at': file_item.get('created_at', ''),
                    'size': file_item.get('metadata', {}).get('size', 0)
                }
                backups.append(backup_info)
        
        return backups
        
    except Exception as e:
        self.logger.error(f"خطأ في جلب النسخ: {e}")
        return []
```

## التشخيص خطوة بخطوة

### 1. اختبر صفحة الملفات البسيطة
- شغل `test_file_upload.py`
- ارفع ملف txt
- تأكد من ظهوره في القائمة
- اقرأ محتواه

### 2. إذا فشل الاختبار:
- المشكلة في إعدادات Supabase
- نفذ أوامر SQL لإصلاح الصلاحيات
- تأكد من صحة `SUPABASE_URL` و `SUPABASE_KEY`

### 3. إذا نجح الاختبار:
- المشكلة في `backup_manager.py`
- طبق الحل المبسط
- اختبر النسخ الاحتياطي مرة أخرى

## ملاحظات مهمة

1. **أسماء الملفات:** تأكد من أن أسماء ملفات النسخ الاحتياطية تتبع نمط ثابت
2. **المسارات:** استخدم مسارات بسيطة بدون تعقيد
3. **المعالجة:** تعامل مع الأخطاء بشكل واضح
4. **السجلات:** فعل التسجيل لمتابعة العمليات

## اختبار سريع

للتأكد من أن كل شيء يعمل:

```python
# اختبار سريع للاتصال
from supabase import create_client
import config

supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
files = supabase.storage.from_(config.SUPABASE_BUCKET).list("")
print(f"عدد الملفات: {len(files)}")
for f in files[:5]:  # أول 5 ملفات
    print(f"الملف: {f.get('name', 'بدون اسم')}")
```
