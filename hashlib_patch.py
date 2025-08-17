# -*- coding: utf-8 -*-
"""
إصلاح مشكلة usedforsecurity في hashlib
يجب استيراد هذا الملف قبل استيراد أي مكتبة تستخدم hashlib
"""

import hashlib
import logging

def apply_hashlib_patch():
    """تطبيق إصلاح شامل لمشكلة usedforsecurity"""
    try:
        # إصلاح openssl_md5 - السبب الرئيسي للمشكلة
        if hasattr(hashlib, 'openssl_md5'):
            _orig_openssl_md5 = hashlib.openssl_md5
            def _patched_openssl_md5(data=b'', **kwargs):
                kwargs.pop('usedforsecurity', None)
                try:
                    return _orig_openssl_md5(data)
                except TypeError as e:
                    if 'usedforsecurity' in str(e):
                        return _orig_openssl_md5(data)
                    raise
            hashlib.openssl_md5 = _patched_openssl_md5
            logging.info("تم إصلاح openssl_md5 بنجاح")
        
        # إصلاح openssl_sha1
        if hasattr(hashlib, 'openssl_sha1'):
            _orig_openssl_sha1 = hashlib.openssl_sha1
            def _patched_openssl_sha1(data=b'', **kwargs):
                kwargs.pop('usedforsecurity', None)
                try:
                    return _orig_openssl_sha1(data)
                except TypeError as e:
                    if 'usedforsecurity' in str(e):
                        return _orig_openssl_sha1(data)
                    raise
            hashlib.openssl_sha1 = _patched_openssl_sha1
        
        # إصلاح md5
        if hasattr(hashlib, 'md5'):
            _orig_md5 = hashlib.md5
            def _patched_md5(data=b'', **kwargs):
                kwargs.pop('usedforsecurity', None)
                try:
                    return _orig_md5(data)
                except TypeError as e:
                    if 'usedforsecurity' in str(e):
                        return _orig_md5(data)
                    raise
            hashlib.md5 = _patched_md5
        
        # إصلاح sha1
        if hasattr(hashlib, 'sha1'):
            _orig_sha1 = hashlib.sha1
            def _patched_sha1(data=b'', **kwargs):
                kwargs.pop('usedforsecurity', None)
                try:
                    return _orig_sha1(data)
                except TypeError as e:
                    if 'usedforsecurity' in str(e):
                        return _orig_sha1(data)
                    raise
            hashlib.sha1 = _patched_sha1
        
        # إصلاح hashlib.new
        if hasattr(hashlib, 'new'):
            _orig_new = hashlib.new
            def _patched_new(name, data=b'', **kwargs):
                kwargs.pop('usedforsecurity', None)
                try:
                    return _orig_new(name, data, **kwargs)
                except TypeError as e:
                    if 'usedforsecurity' in str(e):
                        return _orig_new(name, data)
                    raise
            hashlib.new = _patched_new
        
        logging.info("تم تطبيق جميع إصلاحات hashlib بنجاح")
        return True
        
    except Exception as e:
        logging.error(f"فشل في تطبيق إصلاحات hashlib: {e}")
        return False

# تطبيق الإصلاح تلقائياً عند استيراد الملف
apply_hashlib_patch()
