#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح مؤقت لمشكلة FONTS_DIR في config.py
"""

import sys
from pathlib import Path

# إضافة المجلد الرئيسي للتطبيق إلى المسار
sys.path.insert(0, str(Path(__file__).parent))

# إصلاح مؤقت لمشكلة FONTS_DIR
import config

# إضافة FONTS_DIR إذا لم يكن موجوداً
if not hasattr(config, 'FONTS_DIR'):
    config.FONTS_DIR = config.RESOURCES_DIR / "fonts"
    print(f"تم إضافة FONTS_DIR: {config.FONTS_DIR}")

# استيراد التطبيق الرئيسي
from main import main

if __name__ == "__main__":
    print("🚀 تشغيل التطبيق الأصلي مع إصلاح FONTS_DIR...")
    main()
