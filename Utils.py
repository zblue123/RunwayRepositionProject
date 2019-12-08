import math
import os
from tempfile import TemporaryFile

import xlrd
import xlwt

from Aircraft import AircraftType, Aircraft


# nonlinear time cost using data from airline reimbursements
def timeCost(arrivalTime, currentTime, additionalTime):
    totalWaitTime = additionalTime + currentTime - arrivalTime

    return 220/(1+math.e**(-1*0.025*(totalWaitTime-90)))-220/(1+math.e**(-1*0.025*(0-90)))


# read in aircraft info, parse to data
def setup():
    aircraftList = []
    os.chdir(r'C:/Users/zblue/Documents/Fall 2017/Algorithms for Nonlinear Optimization/')
    unMergeExcelCell('AircraftInfo_final.xls')
    workbook = xlrd.open_workbook('AircraftInfo_temp2_unmerged.xls', formatting_info=True)
    sheet = workbook.sheet_by_index(0)
    row_idx = 1
    while row_idx < sheet.nrows:
        name = sheet.cell(row_idx, 0).value + ' '
        if type(sheet.cell(row_idx, 1).value) is str:
            name += sheet.cell(row_idx, 1).value
        else:
            name += str(int(sheet.cell(row_idx, 1).value))

        if not sheet.cell(row_idx, 2).value == '':
            if type(sheet.cell(row_idx, 2).value) is str:
                name += '-' + sheet.cell(row_idx, 2).value
            else:
                name += '-' + str(int(sheet.cell(row_idx, 2).value))

        myACDict = {'Light': AircraftType.TURBOPROP, 'Medium': AircraftType.NARROW, 'Heavy': AircraftType.HEAVY}
        acType = myACDict[sheet.cell(row_idx, 3).value]

        inService = sheet.cell(row_idx, 4).value
        if inService == '':
            inService = 0
        capacity = sheet.cell(row_idx, 5).value
        if capacity == '':
            capacity = 0
        fuelBurn = sheet.cell(row_idx, 6).value
        if fuelBurn == '':
            fuelBurn = 0
        aircraftList.append((Aircraft(name, acType, capacity, fuelBurn, 3), inService))

        row_idx += 1
    return aircraftList


# un merge cells in excel, convenience method
def unMergeExcelCell(path):
    if not os.path.exists(path):
        print(("Could not find the excel file: " % path))
        return

    # read merged cells for all sheets
    book = xlrd.open_workbook(path, formatting_info=True)

    # open excel file and write
    excel = xlwt.Workbook()
    for rd_sheet in book.sheets():
        # for each sheet
        wt_sheet = excel.add_sheet(rd_sheet.name)

        written_cells = []

        # over write for merged cells
        for crange in rd_sheet.merged_cells:
            # for each merged_cell
            rlo, rhi, clo, chi = crange
            cell_value = rd_sheet.cell(rlo, clo).value
            for rowx in range(rlo, rhi):
                for colx in range(clo, chi):
                    wt_sheet.write(rowx, colx, cell_value)
                    written_cells.append((rowx, colx))

        # write all un-merged cells
        for r in range(0, rd_sheet.nrows):
            for c in range(0, rd_sheet.ncols):
                if (r, c) in written_cells:
                    continue
                cell_value = rd_sheet.cell(r, c).value
                wt_sheet.write(r, c, cell_value)

    # save the un-merged excel file
    (origin_file, ext) = os.path.splitext(path)
    unmerge_excel_file = origin_file + '_unmerged' + ext
    excel.save(unmerge_excel_file)


# write output to excel file
def output(data):
    book = xlwt.Workbook()
    sheet = book.add_sheet('Sheet1')
    for row, array in enumerate(data):
        for col, value in enumerate(array):
            sheet.write(row, col, value)
    name = "output.xls"
    book.save(name)
    book.save(TemporaryFile())
