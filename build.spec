# -*- mode: python ; coding: utf-8 -*-
"""
ملف إعدادات PyInstaller لتحويل التطبيق إلى exe
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
    # قوالب الطباعة
    ('core/printing', 'core/printing'),
    # ملفات الإعدادات
    ('printing_config.json', '.'),
    ('config.py', '.'),
    # مجلد البيانات
    ('data', 'data'),
    # الوثائق
    ('docs', 'docs'),
    # ملفات UI
    ('ui', 'ui'),
]

# الوحدات المخفية التي قد لا يجدها PyInstaller تلقائياً
hidden_imports = [
    'PyQt5.QtCore',
    'PyQt5.QtWidgets', 
    'PyQt5.QtGui',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtPrintSupport',
    'PyQt5.QtSql',
    'supabase',
    'storage3',
    'bcrypt',
    'reportlab',
    'arabic_reshaper',
    'bidi',
    'PIL',
    'jinja2',
    'dotenv',
    'logging',
    'pathlib',
    'sqlite3',
    'json',
    'datetime',
    'decimal',
    'os',
    'sys',
    'collections',
    're',
    'urllib',
    'hashlib',
    'base64',
    'io',
    'csv',
    'math',
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
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
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

# جمع كل الملفات في مجلد واحد
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PrivateSchoolsAccounting'
)
