import math
import os
from xlrd import open_workbook
from xlsxwriter.workbook import Workbook

c = 299792458
unit_conversions = {'THz':10**12,'Hz':1,'micron':10**(-6),'um':10**(-6),'m':1,'CM-1':c*10**2,'CM^-1':c*10**2}
unit_types = ['Frequency','frequency','Wavelength','wavelength','FREQ','Freq'] #unit types in order of preference

class ExcelReader:

    def __init__(self, file_location):
        self.file_location = file_location
        self.book = open_workbook(self.file_location, on_demand = True)
        self.sheet = self.book.sheet_by_index(0)


    def set_freq_range_Hz(self, freq_start, freq_end):
        try:
            self.col = self.indep_chooser('Hz')
        except NameError:
            self.col = self.indep_chooser(0, 'Frequency')

        if float(self.sheet.cell(self.row_offset + 2, self.col).value) \
           < float(self.sheet.cell(self.row_offset + 1, self.col).value):
            self.asc = False
        else:
            self.asc = True

        row = self.row_offset + 1
        try:
            while self.asc \
                  and float(self.sheet.cell(row, self.col).value) < freq_start \
                or not self.asc \
                  and float(self.sheet.cell(row, self.col).value) > freq_end:
                row = row + 1
            self.row_start = max(self.row_offset + 1, row - 1)

        # no data in range
        except Exception:
            self.row_start = 0
            self.row_end = 0
            return

        try:
            while self.asc \
                  and float(self.sheet.cell(row, self.col).value) < freq_end \
                or not self.asc \
                  and float(self.sheet.cell(row, self.col).value) > freq_start:
                row = row + 1
            self.row_end = row + 1 # read one extra row for interpolation

        # reached the end of data
        except Exception:
            self.row_end = row


    def read_from_col(self, units, freq_start, freq_end, title = ' '): #reads independent variable(freq in Hz) terms to a namedtuple with the data
        # determine first and last row to read
        self.set_freq_range_Hz(freq_start, freq_end)

        # read all rows until finished or non-numerical value encountered
        result = []
        try:
            self.col = self.indep_chooser(units, title)
            for row in range(self.row_start, self.row_end):
                value = float(self.sheet.cell(row, self.col).value)
                result.append(value)
        except Exception:
            pass
        return result


    def indep_chooser(self, units, title = ' '): #looks through all columns and returns the location of the first column with chosen units
        toprow = False
        row = 0
        while not toprow:
            if units != 0:  #set units to 0 to choose column based on title
                try:
                    for col in range(0,30):
                        self.col_title = str(self.sheet.cell(row,col))
                        self.col_title = self.col_title.strip()
                        self.col_type = self.col_title[7:self.col_title.find('(')-1]  #col_title looks like "text:u'type (units)'" -- this strips the 'text:u' from the type
                        self.col_units = self.col_title[self.col_title.find('(')+1:self.col_title.find(')')] #everything inside of parentheses are the units
                        if self.col_units == units:
                            toprow = True
                            self.row_offset = row
                            return col
                except:
                    row += 1
                    if row > 100:
                        raise NameError("Units '" + units + "' not found")
            else: #if units = 0 check for column based on column type rather than units.
                try:
                    for col in range(0,30):
                        self.col_title = str(self.sheet.cell(row,col))
                        self.col_title = self.col_title.strip()
                        self.col_type = self.col_title[7:-1]
                        if self.col_type == title:
                            toprow = True
                            self.row_offset = row
                            return col
                except:
                    row += 1
                    if row > 100:
                        raise NameError("Title '" + title + "' not found")


#to generate XLSX format excel format
class ExcelXWriter:
    def __init__(self, path):
        self.path = path
        self.book = Workbook(path)
        self.sheet = self.book.add_worksheet()
        self.column_to_fill = 0

    def write_col(self, column_name, column_content):
        row = 0
        self.sheet.write(row, self.column_to_fill, column_name)
        row += 1
        for x in column_content:
            self.sheet.write(row, self.column_to_fill, x)
            row += 1
        self.column_to_fill += 1
    # write_note(self, note):
    def save(self):
        self.book.close()


def inp_to_freq(entry,units):#takes input and returns equivalent freq in Hz
    if units == 'micron' or units == 'm' or units == 'um':
        return (c/(entry*unit_conversions[units]))
    else:
        freq_Hz = entry*unit_conversions[units]
        return freq_Hz
