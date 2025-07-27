#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update students table structure - second round of changes
"""

import sqlite3
import os
from pathlib import Path
import config

def update_students_table_v2():
    """Update students table structure - second version"""
    try:
        # Connect to database
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create a new table with the desired structure
        cursor.execute("""
            CREATE TABLE students_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                school_id INTEGER NOT NULL,
                grade TEXT NOT NULL,
                section TEXT NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT,
                total_fee DECIMAL(10,2) NOT NULL DEFAULT 0,
                start_date DATE NOT NULL DEFAULT CURRENT_DATE,
                status TEXT DEFAULT 'نشط',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
            )
        """)
        
        # Copy data from old table to new table
        cursor.execute("""
            INSERT INTO students_new (
                id, full_name, school_id, grade, section, gender, phone,
                total_fee, start_date, status, created_at, updated_at
            )
            SELECT 
                id, full_name, school_id, grade, section, gender, phone,
                total_fee, 
                COALESCE(start_date, date('now')) as start_date, 
                COALESCE(status, 'نشط') as status, 
                created_at, updated_at
            FROM students
        """)
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE students")
        cursor.execute("ALTER TABLE students_new RENAME TO students")
        
        # Recreate indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_school_id ON students(school_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_name ON students(full_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_grade ON students(grade)")
        
        conn.commit()
        print("Students table updated successfully!")
        
    except Exception as e:
        print(f"Error updating students table: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_students_table_v2()