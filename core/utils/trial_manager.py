#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""إدارة النسخة التجريبية وحدودها.

توفر هذه الوحدة دوال بسيطة للتحقق من حدود النسخة التجريبية
(عدد الطلاب، المعلمين، الموظفين) قبل السماح بالإضافة.
"""
from typing import Tuple
import logging

import config
from core.database.connection import db_manager

ENTITY_LIMITS = {
    'students': lambda: config.TRIAL_STUDENTS_LIMIT,
    'teachers': lambda: config.TRIAL_TEACHERS_LIMIT,
    'employees': lambda: config.TRIAL_EMPLOYEES_LIMIT,
    'external_income': lambda: 4,  # حد النسخة التجريبية المطلوب للإيرادات الخارجية
    'expenses': lambda: 4,         # حد النسخة التجريبية المطلوب للمصروفات
}

MESSAGES = {
    'students': "هذه نسخة تجريبية: الحد الأقصى للطلاب هو {limit} طالب فقط.",
    'teachers': "هذه نسخة تجريبية: الحد الأقصى للمعلمين هو {limit} معلمين فقط.",
    'employees': "هذه نسخة تجريبية: الحد الأقصى للموظفين هو {limit} موظفين فقط.",
    'external_income': "هذه نسخة تجريبية: الحد الأقصى للإيرادات الخارجية هو {limit} فقط.",
    'expenses': "هذه نسخة تجريبية: الحد الأقصى للمصروفات هو {limit} فقط.",
}

def is_trial_mode() -> bool:
    return getattr(config, 'TRIAL_MODE', False)


def get_current_count(table: str) -> int:
    try:
        row = db_manager.execute_fetch_one(f"SELECT COUNT(*) as c FROM {table}")
        return int(row['c']) if row else 0
    except Exception as e:
        logging.error(f"فشل في إحضار عدد السجلات من {table}: {e}")
        return 0


def can_add_entity(table: str, additional: int = 1) -> Tuple[bool, str]:
    """التحقق مما إذا كان يمكن إضافة كيان (أو مجموعة كيانات) في وضع النسخة التجريبية.

    Args:
        table: اسم الجدول (students / teachers / employees)
        additional: عدد السجلات المراد إضافتها (1 افتراضياً)

    Returns:
        (مسموح؟, رسالة في حال عدم السماح وإلا فارغة)
    """
    if not is_trial_mode():
        return True, ""
    if table not in ENTITY_LIMITS:
        return True, ""
    limit = ENTITY_LIMITS[table]()
    current = get_current_count(table)
    if current + additional > limit:
        msg_tpl = MESSAGES.get(table, "تم تجاوز حد النسخة التجريبية")
        return False, msg_tpl.format(limit=limit)
    return True, ""

__all__ = [
    'is_trial_mode', 'can_add_entity'
]
