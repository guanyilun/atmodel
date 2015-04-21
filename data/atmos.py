#converts Masterfile to atmodel input files

import xlrd
from xlsxwriter.workbook import Workbook
altitudes = [0,2,3,4,5,6,9,12,15,20,25,30,35,40]

#open spreadsheet
sites = []
for alt in altitudes:
	sites.append([xlrd.open_workbook("Atmosphere/Microwave-"+str(alt)+\
			"Km-45deg-200-2000cm-Radiance.xls").sheet_by_index(0),
		xlrd.open_workbook("Atmosphere/Microwave-"+str(alt)+\
			"Km-45deg-200-2000cm-Transmission.xls").sheet_by_index(0),
		xlrd.open_workbook("Atmosphere/Microwave-"+str(alt)+\
			"Km-45deg-2000-50000cm-Radiance.xls").sheet_by_index(0),
		xlrd.open_workbook("Atmosphere/Microwave-"+str(alt)+\
			"Km-45deg-2000-50000cm-Transmission.xls").sheet_by_index(0)])
			
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

def write(file, col1, col2, col3, title1, title2, title3):
	out_file = Workbook(file)
	sheet = out_file.add_worksheet()
	sheet.write (0,0,title1)
	sheet.write (0,1,title2)
	sheet.write (0,2,title3)
	for i, val in enumerate(col1):
		sheet.write (i+1,0,val)
	for i, val in enumerate(col2):
		sheet.write (i+1,1,val)
	for i, val in enumerate(col3):
		sheet.write (i+1,2,val)
	out_file.close()

freq = []
rad = []
trans = []
for site in sites:
	f = read(site[0],1,0)+ read(site[2],1,0)
	for i,f_i in enumerate(f):
		f[i] = f_i * 29979245800
	freq.append(f)
	rad.append(read(site[0],1,1)+ read(site[2],1,1))
	trans.append(read(site[1],1,1)+ read(site[3],1,1))

for i,alt in enumerate(altitudes):
	write("Backgrounds/Atmospheric sites/"+str(alt)+"Km.xlsx",\
		freq[i],rad[i],trans[i],"Freq (Hz)","TOTAL RAD","COMBIN TRANS")




	
	
	
	

		

