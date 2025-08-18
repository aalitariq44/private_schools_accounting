# -*- mode: python ; coding: utf-8 -*-
"""
ملف إعدادات PyInstaller لإنشاء توزيع احترافي
نظام محاسبة المدارس الخاصة - النسخة النهائية
"""

import sys
import os
from pathlib import Path

# مسار المشروع
project_root = os.path.abspath('.')

# البيانات الإضافية التي يجب تضمينها
added_files = [
    # الخطوط والموارد
    ('app/resources', 'app/resources'),
    # الوحدات الأساسية
    ('app', 'app'),
    ('core', 'core'),
    ('ui', 'ui'),
    # ملفات الإعدادات
    ('printing_config.json', '.'),
    ('config.py', '.'),
    # مجلد البيانات
    ('data', 'data'),
    # الوثائق
    ('docs', 'docs'),
    # ملفات أخرى مهمة
    ('.env', '.'),
]

# الوحدات المخفية
hidden_imports = [
    'PyQt5.QtCore',
    'PyQt5.QtWidgets', 
    'PyQt5.QtGui',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtPrintSupport',
    'PyQt5.QtSql',
    'PyQt5.sip',
    'supabase',
    'storage3',
    'bcrypt',
    'reportlab.pdfgen',
    'reportlab.lib',
    'reportlab.platypus',
    'arabic_reshaper',
    'bidi.algorithm',
    'PIL.Image',
    'PIL.ImageTk',
    'jinja2.ext',
    'dotenv',
    'logging.handlers',
    'pathlib',
    'sqlite3',
    'json',
    'datetime',
    'decimal',
    'os',
    'sys',
    'collections.abc',
    're',
    'urllib.parse',
    'hashlib',
    'base64',
    'io',
    'csv',
    'math',
    'locale',
    'platform',
    'threading',
    'queue',
    'traceback',
]

# إعداد التحليل
a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'test_*',
        'tests',
        'testing',
        '_tests',
        'unittest',
        'nose',
        'pytest',
        'tkinter',
        'matplotlib.tests',
        'numpy.tests',
        'scipy.tests',
        'pandas.tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# تنظيف البيانات المكررة
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# إعداد التطبيق القابل للتنفيذ
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PrivateSchoolsAccounting',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # تطبيق GUI بدون نافذة Console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/resources/images/icon.ico' if os.path.exists('app/resources/images/icon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)

# جمع كل الملفات في مجلد واحد للتوزيع
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PrivateSchoolsAccounting_Distribution'
)
