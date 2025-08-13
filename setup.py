#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف إعداد التطبيق لتحويله إلى exe
"""

from setuptools import setup, find_packages
import sys
import os

# معلومات التطبيق
APP_NAME = "Private Schools Accounting"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "نظام محاسبة المدارس الأهلية"
APP_AUTHOR = "Private Schools Team"

# قراءة المتطلبات من requirements.txt
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name=APP_NAME.lower().replace(' ', '_'),
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    author=APP_AUTHOR,
    packages=find_packages(),
    install_requires=read_requirements(),
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'private-schools-accounting=main:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.txt', '*.md', '*.json', '*.sql'],
        'app': ['resources/**/*'],
        'ui': ['**/*.ui', '**/*.qss'],
        'core': ['**/*.json'],
        'data': ['**/*'],
        'docs': ['**/*'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Office/Business :: Financial :: Accounting',
    ],
)
