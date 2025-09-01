# -*- mode: python ; coding: utf-8 -*-
"""
ملف إعدادات PyInstaller لبناء توزيع احترافي
"""

import os
import sys

# البيانات والموارد المطلوبة
datas = []

# إضافة الملفات والمجلدات الموجودة
if os.path.exists('app'):
    datas.append(('app', 'app'))
if os.path.exists('core'):
    datas.append(('core', 'core'))
if os.path.exists('ui'):
    datas.append(('ui', 'ui'))
if os.path.exists('data'):
    datas.append(('data', 'data'))
if os.path.exists('docs'):
    datas.append(('docs', 'docs'))
if os.path.exists('config.py'):
    datas.append(('config.py', '.'))
if os.path.exists('printing_config.json'):
    datas.append(('printing_config.json', '.'))

# الوحدات المخفية الأساسية
hiddenimports = [
    'PyQt5.QtCore',
    'PyQt5.QtWidgets',
    'PyQt5.QtGui',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtPrintSupport',
    'PyQt5.QtSql',
    'supabase',
    'reportlab',
    'arabic_reshaper',
    'bidi',
    'PIL',
    'bcrypt',
    'dotenv',
    'sqlite3',
    'json',
    'datetime',
    'decimal',
    'logging'
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'tkinter'
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join('app', 'resources', 'images', 'icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PrivateSchoolsAccounting_beta'
)
