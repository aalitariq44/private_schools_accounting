#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_table.py <table_name>")
        sys.exit(1)

    table_name = sys.argv[1]
    try:
        info = db_manager.get_table_info(table_name)
        if info:
            print(f"Table '{table_name}' structure:")
            for column in info:
                print(f"  {column['name']}: {column['type']} {'NOT NULL' if column['notnull'] else ''} {'PRIMARY KEY' if column['pk'] else ''}")
        else:
            print(f"Table '{table_name}' does not exist or has no columns.")
    except Exception as e:
        print(f"Error checking table '{table_name}': {e}")
