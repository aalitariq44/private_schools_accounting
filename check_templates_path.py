#!/usr/bin/env python3

import sys
sys.path.append('.')
import os

from core.printing.template_manager import TemplateManager

manager = TemplateManager()
print(f'Templates path: {manager.templates_path}')
print(f'Path exists: {os.path.exists(manager.templates_path)}')

if os.path.exists(manager.templates_path):
    files = os.listdir(manager.templates_path)
    print(f'Files in path: {files}')
    
    if 'student_list.html' in files:
        print('✅ student_list.html exists')
    else:
        print('❌ student_list.html missing')
else:
    print('❌ Templates directory does not exist')
