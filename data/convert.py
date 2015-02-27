#converts Masterfile to atmodel input files

import xlrd
from xlsxwriter.workbook import Workbook
file = xlrd.open_workbook ("Master Noise-a.xlsm")
galacticfile = xlrd.open_workbook ("Galactic Emission Profiles Combined.xlsx")

#open spreadsheet
cib_sheet = file.sheet_by_index(0)
zodi0_sheet = file.sheet_by_index(4)
zodi45_sheet = file.sheet_by_index(3)
zodi90_sheet = file.sheet_by_index(2)
galactic_sheet = galacticfile.sheet_by_index(0)

#read the sheet
def read(sheet, row_start, col):
	data = []
	try:
		row = row_start
		while True:
			data.append(sheet.cell(row,col).value)
			row = row + 1
	except:
		pass
	return data

cib_freq = read(cib_sheet, 19, 2)
cib_temp = read(cib_sheet, 19, 14)
zodi0_freq = read(zodi0_sheet, 5, 2)
zodi0_temp = read(zodi0_sheet, 5, 14)
zodi45_freq = read(zodi45_sheet, 5, 2)
zodi45_temp = read(zodi45_sheet, 5, 14)
zodi90_freq = read(zodi90_sheet, 7, 2)
zodi90_temp = read(zodi90_sheet, 7, 14)
galactic_freq = read(galactic_sheet, 1, 1)
galactic_tempDeCosta0 = read(galactic_sheet, 1, 7)
galactic_tempDeCosta90 = read(galactic_sheet, 1, 11)
galactic_tempSchlege0 = read(galactic_sheet, 1, 6)
galactic_tempSchlege90 = read(galactic_sheet, 1, 10)


def write(file, col1, col2, title1, title2):
	out_file = Workbook(file)
	sheet = out_file.add_worksheet()
	sheet.write (0,0,title1)
	sheet.write (0,1,title2)
	for i, val in enumerate(col1):
		sheet.write (i+1,0,val)
	for i, val in enumerate(col2):
		sheet.write (i+1,1,val)
	out_file.close()

write("Backgrounds/CIB/cib.xlsx",cib_freq,cib_temp,"Freq(Hz)","Temperature(K)")
write("Backgrounds/Zodiacal Emission/elat=0, elon=0.xlsx",zodi0_freq,zodi0_temp,"Freq(Hz)","Temperature(K)")
write("Backgrounds/Zodiacal Emission/elat=45, elon=0.xlsx",zodi45_freq,zodi45_temp,"Freq(Hz)","Temperature(K)")
write("Backgrounds/Zodiacal Emission/elat=90, elon=180.xlsx",zodi90_freq,zodi90_temp,"Freq(Hz)","Temperature(K)")
write("Backgrounds/Galactic Emission/glat=0, glong=0(DeCosta).xlsx", 
	galactic_freq,galactic_tempDeCosta0, "Freq (Hz)", "Temperature (K)")
write("Backgrounds/Galactic Emission/glat=90, glong=180(DeCosta).xlsx", 
	galactic_freq,galactic_tempDeCosta90, "Freq (Hz)", "Temperature (K)")
write("Backgrounds/Galactic Emission/glat=0, glong=0(Schlegel).xlsx", 
	galactic_freq,galactic_tempSchlege0, "Freq (Hz)", "Temperature(K)")
write("Backgrounds/Galactic Emission/glat=90, glong=180(Schlegel).xlsx", 
	galactic_freq,galactic_tempSchlege90, "Freq (Hz)", "Temperature (K)")
	
	

		


