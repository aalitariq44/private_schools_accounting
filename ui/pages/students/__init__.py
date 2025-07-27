#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
حزمة صفحات إدارة الطلاب
"""

from .students_page import StudentsPage
from .student_details_page import StudentDetailsPage
from .add_installment_dialog import AddInstallmentDialog
from .add_additional_fee_dialog import AddAdditionalFeeDialog

__all__ = [
    'StudentsPage', 
    'StudentDetailsPage', 
    'AddInstallmentDialog', 
    'AddAdditionalFeeDialog'
]
