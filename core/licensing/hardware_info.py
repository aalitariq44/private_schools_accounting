#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام جمع معلومات الهارد وير
"""

import platform
import subprocess
import uuid
import hashlib
import logging
from typing import Dict, Optional


class HardwareInfo:
    """فئة لجمع معلومات الهارد وير الخاصة بالجهاز"""
    
    def __init__(self):
        """تهيئة فئة معلومات الهارد وير"""
        self.logger = logging.getLogger(__name__)
    
    def get_motherboard_serial(self) -> str:
        """الحصول على رقم اللوحة الأم"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'baseboard', 'get', 'serialnumber'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and 'SerialNumber' not in line:
                            return line[:50]  # تحديد طول معقول
            else:
                # للأنظمة الأخرى (Linux/Mac)
                try:
                    result = subprocess.run(
                        ['dmidecode', '-s', 'baseboard-serial-number'],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        return result.stdout.strip()[:50]
                except:
                    pass
        except Exception as e:
            self.logger.warning(f"لا يمكن الحصول على رقم اللوحة الأم: {e}")
        
        # قيمة افتراضية بناءً على معلومات النظام
        return hashlib.md5(f"{platform.node()}{platform.machine()}".encode()).hexdigest()[:16]
    
    def get_cpu_id(self) -> str:
        """الحصول على معرف المعالج"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'processorid'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and 'ProcessorId' not in line:
                            return line[:50]
            else:
                # للأنظمة الأخرى
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        for line in f:
                            if 'serial' in line.lower():
                                return line.split(':')[1].strip()[:50]
                except:
                    pass
        except Exception as e:
            self.logger.warning(f"لا يمكن الحصول على معرف المعالج: {e}")
        
        # قيمة افتراضية بناءً على معلومات المعالج
        return hashlib.md5(f"{platform.processor()}{platform.machine()}".encode()).hexdigest()[:16]
    
    def get_mac_address(self) -> str:
        """الحصول على عنوان MAC للجهاز"""
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0, 2*6, 8)][::-1])
            return mac.replace(':', '').upper()[:12]
        except Exception as e:
            self.logger.warning(f"لا يمكن الحصول على عنوان MAC: {e}")
            return "000000000000"
    
    def get_primary_drive_serial(self) -> str:
        """الحصول على رقم القرص الصلب الرئيسي"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'diskdrive', 'get', 'serialnumber'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and 'SerialNumber' not in line and line != '':
                            return line[:50]
            else:
                # للأنظمة الأخرى
                try:
                    result = subprocess.run(
                        ['lsblk', '-o', 'SERIAL', '-n'],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        serials = result.stdout.strip().split('\n')
                        for serial in serials:
                            if serial.strip():
                                return serial.strip()[:50]
                except:
                    pass
        except Exception as e:
            self.logger.warning(f"لا يمكن الحصول على رقم القرص الصلب: {e}")
        
        # قيمة افتراضية بناءً على معلومات النظام
        return hashlib.md5(f"{platform.node()}{platform.system()}".encode()).hexdigest()[:16]
    
    def get_all_hardware_info(self) -> Dict[str, str]:
        """الحصول على جميع معلومات الهارد وير"""
        try:
            hardware_info = {
                'motherboard': self.get_motherboard_serial(),
                'cpu': self.get_cpu_id(),
                'mac': self.get_mac_address(),
                'drive': self.get_primary_drive_serial()
            }
            
            self.logger.info("تم جمع معلومات الهارد وير بنجاح")
            return hardware_info
            
        except Exception as e:
            self.logger.error(f"خطأ في جمع معلومات الهارد وير: {e}")
            raise
    
    def create_hardware_fingerprint(self) -> str:
        """إنشاء بصمة فريدة للجهاز"""
        try:
            hardware_info = self.get_all_hardware_info()
            fingerprint_data = ''.join([
                hardware_info['motherboard'],
                hardware_info['cpu'],
                hardware_info['mac'],
                hardware_info['drive']
            ])
            
            # إنشاء hash فريد
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:32]
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء بصمة الجهاز: {e}")
            raise
    
    def compare_hardware_info(self, stored_info: Dict[str, str]) -> Dict[str, bool]:
        """مقارنة معلومات الهارد وير الحالية مع المحفوظة"""
        try:
            current_info = self.get_all_hardware_info()
            comparison = {}
            
            for key in ['motherboard', 'cpu', 'mac', 'drive']:
                if key in stored_info and key in current_info:
                    comparison[key] = stored_info[key] == current_info[key]
                else:
                    comparison[key] = False
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"خطأ في مقارنة معلومات الهارد وير: {e}")
            raise
    
    def get_matching_count(self, stored_info: Dict[str, str]) -> int:
        """الحصول على عدد العناصر المتطابقة"""
        try:
            comparison = self.compare_hardware_info(stored_info)
            return sum(1 for match in comparison.values() if match)
            
        except Exception as e:
            self.logger.error(f"خطأ في حساب عدد العناصر المتطابقة: {e}")
            return 0
