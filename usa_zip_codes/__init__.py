# -*- coding: utf-8 -*-
import xlrd

from odoo import api, SUPERUSER_ID, _


def add_geographical_data(cr, re):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    file_path = 'usa_zip_codes/static/src/xls/zip_code_database.xlsx'

    workbook = xlrd.open_workbook(file_path)
    sheet = workbook.sheet_by_index(0)  # Assuming the data is in the first sheet

    for row in range(1, sheet.nrows):  # Skip header row (if any)
        record_data = {
            'zip_code': str(int(sheet.cell_value(row, 0))),
            'city': sheet.cell_value(row, 1),
            'state': sheet.cell_value(row, 2),
            'latitude': sheet.cell_value(row, 3),
            'longitude': sheet.cell_value(row, 4)
        }
        

        env['geographical'].create(record_data)