#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار التحديثات الجديدة للإعدادات المتقدمة
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from ui.pages.settings.advanced_settings_dialog import show_advanced_settings

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("اختبار الإعدادات المتقدمة")
        self.setGeometry(100, 100, 400, 200)
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        test_button = QPushButton("اختبار الإعدادات المتقدمة")
        test_button.clicked.connect(self.test_advanced_settings)
        layout.addWidget(test_button)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def test_advanced_settings(self):
        show_advanced_settings(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
