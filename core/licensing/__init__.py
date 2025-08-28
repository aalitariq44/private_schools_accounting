#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة التراخيص
"""

from .license_manager import LicenseManager
from .hardware_info import HardwareInfo
from .activation_dialog import ActivationDialog, show_activation_dialog
from .license_system import LicenseSystem, initialize_license_system, quick_license_check

__all__ = [
    'LicenseManager', 
    'HardwareInfo', 
    'ActivationDialog', 
    'show_activation_dialog',
    'LicenseSystem',
    'initialize_license_system',
    'quick_license_check'
]
