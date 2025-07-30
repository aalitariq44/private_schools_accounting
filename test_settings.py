#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار صفحة الإعدادات
"""

import sys
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# تهيئة قاعدة البيانات
from core.database.connection import db_manager
db_manager.initialize_database()

# إنشاء تطبيق القاذ لاختبار الصفحة
app = QApplication(sys.argv)
app.setLayoutDirection(Qt.RightToLeft)

# إنشاء صفحة الإعدادات
from ui.pages.settings.settings_page import SettingsPage
settings_page = SettingsPage()
settings_page.show()

# تشغيل التطبيق
sys.exit(app.exec_())
