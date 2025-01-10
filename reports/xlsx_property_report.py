from ast import literal_eval
from odoo import http
from odoo.http import request
import io
import xlsxwriter

class XlsxPropertyReport(http.Controller):

    # handle end point, <string:property_ids> handle data by ids ,auth="user": login user can access report
    @http.route("/property/excel/report/<string:property_ids>", type="http", auth="user")
    def download_property_excel_report(self, property_ids):
        # transfer from string to list
        # using method browse to get records by their ids
        property_ids = request.env['property'].browse(literal_eval(property_ids))
        print(property_ids)
        # store file in memory for all data
        output = io.BytesIO()
        # handle work_book(excel file)
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        # handle work_sheet in work_book, name of sheet
        worksheet = workbook.add_worksheet('Properties')
        # handle header of sheet (report)
        # 1- add format to header
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center'})
        # 2- add format to data (string)
        string_format = workbook.add_format({'border': 1, 'align': 'center'})
        # 2- add format to price, num after(,##), if no value (00.00)
        price_format = workbook.add_format({'num_format': '$##,###00.00', 'border': 1, 'align': 'center'})
        # define headers data, [display names of column]
        headers = ['Name', 'Postcode', 'Selling Price', 'Garden']
        # to write all values, use enumerate to retrieve col_num and value
        for col_num, header in enumerate(headers):
            # write headers in work_sheet (row, column, value, format)
            # worksheet.write(0, 0, 'Name', header_format)
            worksheet.write(0, col_num, header, header_format)
        # write data (dynamic)
        row_num = 1
        for property in property_ids:
            worksheet.write(row_num, 0, property.name, string_format)
            worksheet.write(row_num, 1, property.postcode, string_format)
            worksheet.write(row_num, 2, property.selling_price, price_format)
            worksheet.write(row_num, 3, 'Yes' if property.garden else 'No', string_format)
            row_num += 1
        # end of report
        workbook.close()
        # read file in memory from beginning
        output.seek(0)

        # name of file when user download it
        file_name = 'Property Report.xlsx'

        # return response, value of output, headers
        return request.make_response(
            output.getvalue(),
            headers=[
                # type that handle excel sheet
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename={file_name}'),
            ]
        )