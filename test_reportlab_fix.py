# -*- coding: utf-8 -*-
"""
اختبار إصلاح مشكلة usedforsecurity
"""

# Apply the hashlib patch first
import hashlib

def patch_hashlib():
    """تطبيق إصلاح hashlib"""
    if hasattr(hashlib, 'openssl_md5'):
        _orig_openssl_md5 = hashlib.openssl_md5
        def _patched_openssl_md5(data=b'', **kwargs):
            kwargs.pop('usedforsecurity', None)
            return _orig_openssl_md5(data)
        hashlib.openssl_md5 = _patched_openssl_md5
        print("✅ تم إصلاح openssl_md5")

patch_hashlib()

try:
    # اختبار استيراد ReportLab
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    print("✅ تم استيراد ReportLab بنجاح")
    
    # اختبار إنشاء PDF بسيط
    import tempfile
    import os
    
    temp_file = tempfile.mktemp(suffix='.pdf')
    c = canvas.Canvas(temp_file, pagesize=A4)
    c.drawString(100, 750, "Test PDF")
    c.save()
    
    if os.path.exists(temp_file):
        print("✅ تم إنشاء PDF بنجاح")
        os.remove(temp_file)
    else:
        print("❌ فشل في إنشاء PDF")
        
except Exception as e:
    print(f"❌ خطأ: {e}")

print("انتهى الاختبار")
