#converts Masterfile to atmodel input files

import xlrd
from xlsxwriter.workbook import Workbook
altitudes = [0,2,3,4,5,6,9,12,15,20,30,35,40]

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
			"Km-45deg-2000-50000cm-Transmission.xls").sheet_by_index(0),
		xlrd.open_workbook("Atmosphere/Microwave-"+str(alt)+\
			"Km-45deg-0-200cm-Radiance.xls").sheet_by_index(0),
		xlrd.open_workbook("Atmosphere/Microwave-"+str(alt)+\
			"Km-45deg-0-200cm-Transmission.xls").sheet_by_index(0)])
			
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

#For range 5-50 microns
freq1 = []
rad1 = []
trans1 = []
#For range 0.2-5 microns
freq2 = []
rad2 = []
trans2 = []
#For >50 microns
freq3 = []
rad3 = []
trans3 = []

for site in sites:
	f1 = read(site[0],1,0)
	f2 = read(site[2],1,0)
	f3 = read(site[4],1,0)
	for i,f1_i in enumerate(f1):
		f1[i] = f1_i * 29979245800
	for i,f2_i in enumerate(f2):
		f2[i] = f2_i * 29979245800
	for i,f3_i in enumerate(f3):
		f3[i] = f3_i * 29979245800
	freq1.append(f1)
	freq2.append(f2)
	freq3.append(f3)
	rad1.append(read(site[0],1,1))
	rad2.append(read(site[2],1,1))
	rad3.append(read(site[4],1,1))
	trans1.append(read(site[1],1,1))
	trans2.append(read(site[3],1,1))
	trans3.append(read(site[5],1,1))

for i,alt in enumerate(altitudes):
	write("Backgrounds/Atmospheric sites/"+str(alt)+"Km-5-50microns.xlsx",\
		freq1[i],rad1[i],trans1[i],"Freq (Hz)","TOTAL RAD","COMBIN TRANS")
	write("Backgrounds/Atmospheric sites/"+str(alt)+"Km-0_2-5microns.xlsx",\
		freq2[i],rad2[i],trans2[i],"Freq (Hz)","TOTAL RAD","COMBIN TRANS")
	write("Backgrounds/Atmospheric sites/"+str(alt)+"Km-50+microns.xlsx",\
		freq3[i],rad3[i],trans3[i],"Freq (Hz)","TOTAL RAD","COMBIN TRANS")


	
	
	
	

		


