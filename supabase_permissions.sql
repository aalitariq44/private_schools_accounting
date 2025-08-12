-- أوامر SQL لضبط صلاحيات Supabase Storage
-- يجب تنفيذها في SQL Editor في لوحة تحكم Supabase

-- 1. التحقق من وجود البكت
SELECT * FROM storage.buckets WHERE name = 'schools-backup';

-- 2. إنشاء البكت إذا لم يكن موجود (اختياري)
-- INSERT INTO storage.buckets (id, name, public)
-- VALUES ('schools-backup', 'schools-backup', false);

-- 3. حذف جميع السياسات الموجودة للبكت (للبدء من جديد)
DROP POLICY IF EXISTS "Allow authenticated users to upload" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated users to view" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated users to delete" ON storage.objects;
DROP POLICY IF EXISTS "Public Access" ON storage.objects;
DROP POLICY IF EXISTS "Give users access to own folder" ON storage.objects;

-- 4. إنشاء سياسة للسماح بالرفع (Upload)
CREATE POLICY "Allow authenticated users to upload"
ON storage.objects FOR INSERT 
WITH CHECK (bucket_id = 'schools-backup');

-- 5. إنشاء سياسة للسماح بالقراءة/العرض (Select/View)
CREATE POLICY "Allow authenticated users to view"
ON storage.objects FOR SELECT 
USING (bucket_id = 'schools-backup');

-- 6. إنشاء سياسة للسماح بالحذف (Delete)
CREATE POLICY "Allow authenticated users to delete"
ON storage.objects FOR DELETE 
USING (bucket_id = 'schools-backup');

-- 7. إنشاء سياسة للسماح بالتحديث (Update)
CREATE POLICY "Allow authenticated users to update"
ON storage.objects FOR UPDATE 
USING (bucket_id = 'schools-backup');

-- 8. التحقق من السياسات المُنشأة
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename = 'objects' AND schemaname = 'storage';

-- 9. إعطاء صلاحيات إضافية للمستخدمين المجهولين (إذا لزم الأمر)
-- CREATE POLICY "Public Access" ON storage.objects
-- FOR ALL USING (bucket_id = 'schools-backup');

-- 10. التحقق من حالة RLS (Row Level Security)
SELECT schemaname, tablename, rowsecurity, forcerowsecurity 
FROM pg_tables 
WHERE schemaname = 'storage' AND tablename = 'objects';

-- 11. تفعيل RLS إذا لم يكن مفعل
-- ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- 12. فحص الملفات الموجودة في البكت
SELECT name, id, bucket_id, owner, created_at, updated_at, last_accessed_at, metadata
FROM storage.objects 
WHERE bucket_id = 'schools-backup'
ORDER BY created_at DESC;

-- 13. فحص حجم البكت والملفات
SELECT 
    bucket_id,
    COUNT(*) as file_count,
    SUM((metadata->>'size')::bigint) as total_size_bytes,
    SUM((metadata->>'size')::bigint) / 1024 / 1024 as total_size_mb
FROM storage.objects 
WHERE bucket_id = 'schools-backup'
GROUP BY bucket_id;

-- 14. البحث عن ملفات النسخ الاحتياطية
SELECT name, created_at, (metadata->>'size')::bigint as size_bytes
FROM storage.objects 
WHERE bucket_id = 'schools-backup' 
AND name LIKE '%backup_%'
ORDER BY created_at DESC;

-- 15. سياسة أكثر تخصصاً للنسخ الاحتياطية (اختيارية)
/*
CREATE POLICY "Backup files access" ON storage.objects
FOR ALL 
USING (
    bucket_id = 'schools-backup' 
    AND (
        name LIKE 'backups/%' 
        OR name LIKE 'test_files/%'
    )
);
*/
