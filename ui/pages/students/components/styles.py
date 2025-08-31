#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
الأنماط المشتركة لصفحة تفاصيل الطالب
"""

# استيراد وحدة أحجام الخطوط
from ui.font_sizes import FontSizeManager


def get_student_details_styles(cairo_family="Arial", font_size_name="متوسط"):
    """الحصول على أنماط صفحة تفاصيل الطالب مع حجم خط ديناميكي"""

    # الحصول على أحجام الخطوط من FontSizeManager
    font_sizes = FontSizeManager.get_font_sizes(font_size_name)

    cairo_font = f"'{cairo_family}', 'Cairo', 'Segoe UI', Tahoma, Arial"

    return f"""
        /* الإطار الرئيسي */
        QWidget {{
            background-color: #F8F9FA;
            font-family: {cairo_font};
            font-size: {font_sizes['base']}px;
        }}

        /* شريط الرجوع */
        #backToolbar {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3498DB, stop:1 #2980B9);
            border-radius: 0px;
            color: white;
            margin-bottom: 15px;
            padding: 5px;
        }}

        #backButton {{
            background-color: #2980B9;
            border: 2px solid #2471A3;
            color: white;
            padding: 10px 16px;
            border-radius: 0px;
            font-weight: bold;
            font-size: {font_sizes['buttons']}px;
            font-family: {cairo_font};
        }}

        #backButton:hover {{
            background-color: #2471A3;
            border-color: #1F618D;
        }}

        #pageTitle {{
            font-size: {font_sizes['summary_title']}px;
            font-weight: bold;
            color: white;
            background-color: transparent;
            font-family: {cairo_font};
        }}

        #refreshButton, #primaryButton, #additionalFeesButton {{
            background-color: #2980B9;
            border: 2px solid #2471A3;
            color: white;
            padding: 10px 16px;
            border-radius: 0px;
            font-weight: bold;
            font-size: {font_sizes['buttons']}px;
            font-family: {cairo_font};
        }}

        #refreshButton:hover, #primaryButton:hover, #additionalFeesButton:hover {{
            background-color: #2471A3;
            border-color: #1F618D;
        }}

        /* قائمة حجم الخط */
        #filterLabel {{
            font-weight: 600;
            color: white;
            margin-right: 4px;
            font-size: {font_sizes['filter_label']}px;
            font-family: {cairo_font};
            background-color: transparent;
        }}

        #filterCombo {{
            padding: 4px 6px;
            border: 1px solid #C3C7CA;
            border-radius: 0px;
            background: #FFFFFF;
            min-width: 85px;
            font-size: {font_sizes['filter_combo']}px;
            font-family: {cairo_font};
        }}

        /* قسم معلومات الطالب */
        #studentInfoFrame {{
            background-color: white;
            border: 2px solid #E0E0E0;
            border-radius: 0px;
            margin: 8px 5px;
            padding: 5px;
        }}

        #sectionTitle {{
            font-size: {font_sizes['summary_title']}px;
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498DB;
            font-family: {cairo_font};
        }}

        #studentName {{
            font-size: {font_sizes['summary_title']}px;
            font-weight: bold;
            color: #2C3E50;
            font-family: {cairo_font};
        }}

        #infoValue {{
            font-size: {font_sizes['base']}px;
            color: #34495E;
            background-color: #F8F9FA;
            padding: 6px 10px;
            border-radius: 0px;
            border: 1px solid #E0E0E0;
            font-family: {cairo_font};
            cursor: pointer;
        }}

        #infoValue:hover {{
            background-color: #E9ECEF;
            border-color: #ADB5BD;
        }}

        /* الملخص المالي */
        #financialSummary {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #ECF0F1, stop:1 #D5DBDB);
            border: 2px solid #BDC3C7;
            border-radius: 0px;
            margin-top: 20px;
            padding: 5px;
        }}

        #totalFee {{
            font-size: {font_sizes['base']}px;
            font-weight: bold;
            color: #2C3E50;
            background-color: rgba(52, 152, 219, 0.15);
            padding: 8px 15px;
            border-radius: 0px;
            border: 2px solid rgba(52, 152, 219, 0.3);
            font-family: {cairo_font};
        }}

        #paidAmount {{
            font-size: {font_sizes['base']}px;
            font-weight: bold;
            color: #27AE60;
            background-color: rgba(39, 174, 96, 0.15);
            padding: 8px 15px;
            border-radius: 0px;
            border: 2px solid rgba(39, 174, 96, 0.3);
            font-family: {cairo_font};
        }}

        #remainingAmount {{
            font-size: {font_sizes['base']}px;
            font-weight: bold;
            background-color: rgba(231, 76, 60, 0.15);
            padding: 8px 15px;
            border-radius: 0px;
            border: 2px solid rgba(231, 76, 60, 0.3);
            font-family: {cairo_font};
        }}

        #installmentsCount {{
            font-size: {font_sizes['base']}px;
            font-weight: bold;
            color: #8E44AD;
            background-color: rgba(142, 68, 173, 0.15);
            padding: 8px 15px;
            border-radius: 0px;
            border: 2px solid rgba(142, 68, 173, 0.3);
            font-family: {cairo_font};
        }}

        /* إطار الأقساط */
        #installmentsFrame {{
            background-color: white;
            border: 2px solid #E0E0E0;
            border-radius: 0px;
            margin: 8px 5px;
            padding: 5px;
        }}

        /* الجداول */
        #installmentsTable, #feesTable {{
            background-color: white;
            border: 2px solid #E0E0E0;
            border-radius: 0px;
            gridline-color: #F0F0F0;
            font-size: {font_sizes['table']}px;
            font-family: {cairo_font};
            margin: 10px 0px;
        }}

        #installmentsTable::item, #feesTable::item {{
            padding: 12px;
            border-bottom: 1px solid #F0F0F0;
            font-family: {cairo_font};
        }}

        #installmentsTable::item:selected, #feesTable::item:selected {{
            background-color: #E3F2FD;
            color: #1976D2;
        }}

        #installmentsTable QHeaderView::section, #feesTable QHeaderView::section {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #34495E, stop:1 #2C3E50);
            border: 1px solid #2C3E50;
            padding: 12px;
            font-weight: bold;
            color: white;
            font-size: {font_sizes['table_header']}px;
            font-family: {cairo_font};
        }}

        /* الأزرار */
        #addButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #27AE60, stop:1 #229954);
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 0px;
            font-weight: bold;
            font-size: {font_sizes['buttons']}px;
            font-family: {cairo_font};
        }}

        #addButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #229954, stop:1 #1E8449);
        }}

        #deleteButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #E74C3C, stop:1 #C0392B);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 0px;
            font-weight: bold;
            font-size: {font_sizes['buttons']}px;
            font-family: {cairo_font};
        }}

        #deleteButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #C0392B, stop:1 #A93226);
        }}

        #printButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #9B59B6, stop:1 #8E44AD);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 0px;
            font-weight: bold;
            font-size: {font_sizes['buttons']}px;
            font-family: {cairo_font};
        }}

        #printButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #8E44AD, stop:1 #7D3C98);
        }}

        /* نافذة الرسوم الإضافية المنبثقة */
        #headerFrame {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3498DB, stop:1 #2980B9);
            border-radius: 0px;
            color: white;
            margin-bottom: 15px;
        }}

        #popupTitle {{
            font-size: {font_sizes['summary_title']}px;
            font-weight: bold;
            color: white;
            font-family: {cairo_font};
        }}

        #studentInfo {{
            font-size: {font_sizes['base']}px;
            color: #ECF0F1;
            font-family: {cairo_font};
        }}

        #feesSummaryFrame {{
            background-color: #F8F9FA;
            border: 2px solid #BDC3C7;
            border-radius: 0px;
            margin: 15px 0px;
        }}

        #feesFrame {{
            background-color: white;
            border: 2px solid #E0E0E0;
            border-radius: 0px;
            margin: 8px 0px;
        }}

        #feesCount, #feesTotal, #feesPaid, #feesUnpaid {{
            font-size: {font_sizes['base']}px;
            font-weight: bold;
            padding: 8px 15px;
            border-radius: 0px;
            font-family: {cairo_font};
        }}

        #feesCount {{
            color: #2C3E50;
            background-color: rgba(44, 62, 80, 0.1);
            border: 2px solid #E0E0E0;
        }}

        #feesTotal {{
            color: #2C3E50;
            background-color: rgba(44, 62, 80, 0.1);
            border: 2px solid #E0E0E0;
        }}

        #feesPaid {{
            color: #27AE60;
            background-color: rgba(39, 174, 96, 0.1);
            border: 2px solid rgba(39, 174, 96, 0.3);
        }}

        #feesUnpaid {{
            color: #E74C3C;
            background-color: rgba(231, 76, 60, 0.1);
            border: 2px solid rgba(231, 76, 60, 0.3);
        }}

        #payButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #F39C12, stop:1 #E67E22);
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 0px;
            font-weight: bold;
            font-size: {font_sizes['buttons']}px;
            font-family: {cairo_font};
        }}

        #closeButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #95A5A6, stop:1 #7F8C8D);
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 0px;
            font-weight: bold;
            font-size: {font_sizes['buttons']}px;
            font-family: {cairo_font};
        }}

        /* قسم الملاحظات */
        #notesFrame {{
            background-color: white;
            border: 2px solid #E0E0E0;
            border-radius: 0px;
            margin: 8px 5px;
            padding: 5px;
        }}

        #notesText {{
            background-color: #F8F9FA;
            border: 2px solid #E0E0E0;
            border-radius: 0px;
            padding: 10px;
            font-family: {cairo_font};
            font-size: {font_sizes['base']}px;
            color: #2C3E50;
            line-height: 1.5;
        }}

        #notesText:read-only {{
            background-color: #F8F9FA;
            color: #7F8C8D;
        }}

        #editButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3498DB, stop:1 #2980B9);
            color: white;
            border: none;
            padding: 8px 14px;
            border-radius: 0px;
            font-weight: bold;
            font-size: {font_sizes['buttons']}px;
            font-family: {cairo_font};
        }}

        #editButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2980B9, stop:1 #2471A3);
        }}

        #saveButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #27AE60, stop:1 #229954);
            color: white;
            border: none;
            padding: 8px 14px;
            border-radius: 0px;
            font-weight: bold;
            font-size: {font_sizes['buttons']}px;
            font-family: {cairo_font};
        }}

        #saveButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #229954, stop:1 #1E8449);
        }}

        #cancelButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #95A5A6, stop:1 #7F8C8D);
            color: white;
            border: none;
            padding: 8px 14px;
            border-radius: 0px;
            font-weight: bold;
            font-size: {font_sizes['buttons']}px;
            font-family: {cairo_font};
        }}

        #cancelButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #7F8C8D, stop:1 #707B7C);
        }}
    """
