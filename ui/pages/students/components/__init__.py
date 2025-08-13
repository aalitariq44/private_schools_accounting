#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مكونات صفحة تفاصيل الطالب
"""

from .additional_fees_popup import AdditionalFeesPopup
from .student_info_widget import StudentInfoWidget
from .installments_table_widget import InstallmentsTableWidget
from .styles import get_student_details_styles

__all__ = [
    'AdditionalFeesPopup',
    'StudentInfoWidget', 
    'InstallmentsTableWidget',
    'get_student_details_styles'
]
