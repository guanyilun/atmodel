from xlrd import open_workbook
from xlwt import Workbook
from xlsxwriter.workbook import Workbook
import os

c = 2.99792458*(10**8)
unit_conversions = {'THz':10**12,'Hz':1,'micron':10**(-6),'um':10**(-6),'m':1,'CM-1':c*10**2,'CM^-1':c*10**2}
unit_types = ['Frequency','frequency','Wavelength','wavelength','FREQ','Freq'] #unit types in order of preference

class ExcelReader:

    def __init__(self, file_location):
        self.file_location = file_location
        self.book = open_workbook(self.file_location, on_demand = True)
        self.sheet = self.book.sheet_by_index(0)
        self.row_offset = 1


    def set_freq_range_Hz(self,freq_start,freq_end):
        Row = self.row_offset #the first row we will test is the one following the rows skipped
        Current_Value = self.sheet.cell(Row, int(self.col)).value #this is the value from column 1 of the "Row" above

        #NOTE: this technique for determining rows to start and stop reading from assumes the columns have values in ascending order

        #look for the first row to read from by going through the data and finding the first value greater than or equal to the starting frequency
        while Current_Value < freq_start: #search through frequency column until we find the frequency we want to start at(the first frequency greater than what we enter)
            Row += 1 #if the row we look at is smaller than what we want, we go to the next row
            Current_Value = self.sheet.cell(Row, 1).value
        self.row_start = Row #the row we want to start reading from is the first row with a value that isn't less than the starting frequency we want

        #now that we have determined what value row to start reading from, we use the same technique to determine what row to terminate reading from
        while Current_Value <= freq_end: #search through column until we find the frequency we want to end at(the first frequency greater than what we enter)
            #inlcuding the equal sign establishes an inclusive range if one of the cells is equal to the desired ending frequency
            try:
                Row += 1
                Current_Value = self.sheet.cell(Row, 1).value
            except:
                Row -= 1
        self.row_end = Row - 1 #the row we want to end reading from is the last row the while loop iterated through which is one less than the "Row" it will give        


    def read_from_col(self, units, freq_start, freq_end, title = ' '): #reads independent variable(freq in Hz) terms to a namedtuple with the data
        if units != 0:
            self.col = self.indep_chooser(units)         #finds the first column with the correct units
        else:
            self.col = self.indep_chooser(0, title)
        self.set_freq_range_Hz(freq_start,freq_end)#finds which rows should be read from that column
        result = []
        for row in range(self.row_start, self.row_end + 1):
            value = self.sheet.cell(row, int(self.col)).value
            if value != None:
                result.append(value)
        return result


    def indep_chooser(self,units, title = ' '): #looks through all columns and returns the location of the first column with chosen units
        if units != 0:  #set units to 0 to choose column based on title
            try:
                for col in range(0,30):
                    self.col_title = str(self.sheet.cell(0,col))
                    self.col_title = self.col_title.strip()
                    self.col_type = self.col_title[7:self.col_title.find('(')-1]  #col_title looks like "text:u'type (units)'" -- this strips the 'text:u' from the type
                    self.col_units = self.col_title[self.col_title.find('(')+1:self.col_title.find(')')] #everything inside of parentheses are the units
                    if self.col_units == units:
                        return col
            except:
                print 'units ' + units + ' not found in file ' + self.file_location
        else: #if units = 0 check for column based on column type rather than units.
            try:
                for col in range(0,30):
                    self.col_title = str(self.sheet.cell(0,col))
                    self.col_title = self.col_title.strip()
                    self.col_type = self.col_title[7:-1]
                    if self.col_type == title:
                        return col
            except:
                print 'title ' + title + ' not found in file ' + self.file_location


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
