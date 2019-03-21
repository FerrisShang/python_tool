import xlrd
import xlwt
from xlutils.copy import copy


def create_xls(filename):
    wb = xlwt.Workbook()
    ws = wb.add_sheet('A Test Sheet')
    ws.write(0, 0, 'Test')
    ws.write(1, 0, 1)
    ws.write(1, 1, 2)
    ws.write(1, 2, xlwt.Formula("A2+B2"))
    wb.save(filename)
    print('create xls done')


def dump_xls(filename):
    wb = xlrd.open_workbook(filename)
    for sheet_name in wb.sheet_names():
        print('sheet', sheet_name)
        sheet = wb.sheet_by_name(sheet_name)
        print('rows:', sheet.nrows)
        for i in range(sheet.nrows):
            print('\t', sheet.row_values(i))
        print('')


def modify_xls(filename):
    rb = xlrd.open_workbook(filename)
    wb = copy(rb)
    rs = rb.sheet_by_index(0)
    ws = wb.get_sheet(0)

    ws.write(1, 0, rs.cell_value(1, 0) + 1)
    wb.save(filename)


if __name__ == '__main__':
    file_name = 'example.xls'
    create_xls(file_name)
    dump_xls(file_name)
    for i in range(5):
        modify_xls(file_name)
        dump_xls(file_name)
