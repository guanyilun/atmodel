#comments made by Aaron Guan, Lois Shen, Quincy Cheung

from scipy import interpolate
import numpy as np
import matplotlib.pyplot as plt
import sys
import xlrd
import xlwt
import wx
import xlsxwriter
import os
import excel
import gc
import file_refs
import cal
import time
import pylab
import const
from excel import ExcelXWriter, ExcelReader
import config

class atmodel(wx.Frame):
    def __init__(self, parent , title):
        super(atmodel, self).__init__(parent, title=title, size=(700, 568))
        self.InitUI()
        self.Centre()
        self.Show()     
    # Set up GUI using wx
    def InitUI(self):
        
        # Creating Panel 
        panel = wx.Panel(self)
        
        # Set panel font
        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(14)
        
        # Create main container structures
        content = wx.BoxSizer(wx.VERTICAL)

        top = wx.BoxSizer(wx.HORIZONTAL)
        top_left = wx.BoxSizer(wx.VERTICAL)
        top_right = wx.BoxSizer(wx.VERTICAL)

        bottom = wx.BoxSizer(wx.HORIZONTAL)
        bottom_left = wx.BoxSizer(wx.VERTICAL)
        bottom_right = wx.BoxSizer(wx.VERTICAL)
        
    # Top_left
        top_left_fgs = wx.FlexGridSizer(0, 2, 6, 6)  # declare FlexibleGridSizer
        
    # Top_left -> parameters
        parameters = ['Specify Parameters', 'Spectral Resolution:',
                      'Mirror Diameter(m):', 'Mirror Temperature(K):',
                      'Choose a Site:', 'Choose a Source:', 'Choose Backgrounds:',
                      'Specify Starting Frequency(THz)', 'Specify Ending Frequency(THz)', 'Signal to Noise Ratio',
                      'Specify Dependent Minimum: 10 to the', 'Specify Dependent Maximum: 10 to the']
    
        # Observation sites
        sites = ["Last Used", '13_7Km SOFIA', '30KmBalloon', '40KmBalloon', 'CCAT-0732g', 'CCAT-0978g', 'DomeA-01g', 'DomeA-014g', 'DomeC-015g',
                 'DomeC-024g', 'MaunaKea-1g', 'MaunaKea-15g', 'SantaBarbara-01g', 'SantaBarbara-30g', 'SouthPole-023g',
                 'SouthPole-032g', 'WhiteMountain-115g', 'WhiteMountain-175g', 'Choose New']
    
        # Source galaxies    
        sources = ["Last Used", 'Choose New', '3C219', 'ARP220_z=1', 'M89', 'Maffei2', 'MRK231_z=1', 'NGC0315', 'NGC262', 'NGC958_z=1', 'NGC1052', 'NGC1097',
				 'NGC1566', 'NGC3351', 'NGC4725', 'NGC6764', 'NGC7793', 'NGC7832', 'PSRB0531-21', 'South America']
    
        # Sources of noise    
        backgrounds = ['Cosmic Infrared Background', 'Cosmic Microwave Background', 'Galactic Emission', 'Thermal Mirror Emission',
                       'Atmospheric Radiance', 'Zodiacal Emission', 'Cumulative']
        
    # Top_left -> Controls
        parameter_labels = [wx.StaticText(panel, label=parameters[i]) for i in range(12)]
        
        self.input_SpecRes = wx.TextCtrl(panel, value=config.SpecRes_Default)
        self.input_MirrorDiam = wx.TextCtrl(panel, value=config.MirrorDiam_Default)
        self.input_MirrorTemp = wx.TextCtrl(panel, value=config.MirrorTemp_Default)
        self.input_StartFreq = wx.TextCtrl(panel, value=config.StartFreq_Default)
        self.input_StopFreq = wx.TextCtrl(panel, value=config.StopFreq_Default)
        self.input_SigNoise = wx.TextCtrl(panel, value=config.SigNoise_Default)
        self.input_DependMin = wx.TextCtrl(panel, value=config.DependMin_Default)
        self.input_DependMax = wx.TextCtrl(panel, value=config.DependMax_Default)
        
        self.parameter_site_combo = wx.ComboBox(panel, choices=sites, style=wx.CB_READONLY) 
        self.parameter_source_combo = wx.ComboBox(panel, choices=sources, style=wx.CB_READONLY)

        self.dependent_limits_checkbox = wx.CheckBox(panel, label='Manually Input Range of Dependent Axis')
        
        # Top_left -> fill up contents 
        parameter_labels[0].SetFont(font)  # set a title font
        top_left_fgs.Add(parameter_labels[0], flag=wx.EXPAND | wx.BOTTOM, border=6)
        top_left_fgs.Add(wx.StaticText(panel), flag=wx.EXPAND)  # empty grid
        
        #each line represents a row in interface
        #parameters are referenced above in the list "parameters"
                            #left column: name of parameter     right column: text box/drop menu for user input
        top_left_fgs.AddMany([(parameter_labels[1], 0, wx.EXPAND), (self.input_SpecRes, 0, wx.EXPAND),
                              (parameter_labels[2], 0, wx.EXPAND), (self.input_MirrorDiam, 0, wx.EXPAND),
                              (parameter_labels[3], 0, wx.EXPAND), (self.input_MirrorTemp, 0, wx.EXPAND),
                              (parameter_labels[4], 0, wx.EXPAND), (self.parameter_site_combo, 0, wx.EXPAND),
                              (parameter_labels[5], 0, wx.EXPAND), (self.parameter_source_combo, 0, wx.EXPAND),
                              (parameter_labels[7], 0, wx.EXPAND), (self.input_StartFreq, 0, wx.EXPAND),
                              (parameter_labels[8], 0, wx.EXPAND), (self.input_StopFreq, 0, wx.EXPAND),
                              (parameter_labels[9], 0, wx.EXPAND), (self.input_SigNoise, 0, wx.EXPAND),
                              self.dependent_limits_checkbox, (wx.StaticText(panel, label='')),
                              (parameter_labels[10], 0, wx.EXPAND), (self.input_DependMin, 0, wx.EXPAND),
                              (parameter_labels[11], 0, wx.EXPAND), (self.input_DependMax, 0, wx.EXPAND)])
                    
        top_left.Add(top_left_fgs, flag=wx.EXPAND)

        # Top_left -> Bind eventhandler
        # self.parameter_site_combo.Bind(wx.EVT_COMBOBOX, self.onCustom)

        # Top_right
        #drop bars to determine which background noise file should be used:
        file_choice = ['Last Used', "Default", "Choose New"] #Used for CIB, CMB, Atmospheric Radiance
        #extra details needed for:
        galactic_directions = ['Last Used', 'g_long = 0, g_lat = 0', 'g_long = 0, g_lat = 45', 'g_long = 0, g_lat = +90', 'g_long = 0, g_lat = -90', 'Choose New'] #ecliptic coordinates for Galactic Emission
        zodiacal_directions = ['Last Used', 'g_long = 0, g_lat = 0', 'g_long = 0, g_lat = 45', 'g_long = 0, g_lat = 90', 'Choose New'] #ecliptic coordinates for Zodiacal Emission
        thermal_mirror_materials = ['Be', 'Al', 'Au', 'Ag'] #mirror material for Thermal Mirror Emission
        
        
    # Top_right -> controls
        #create checkboxes and drop menus for background in the top right
        self.background_checkboxs = [wx.CheckBox(panel, label=backgrounds[i]) for i in range(len(backgrounds))]
        self.CIB_file_choice = wx.ComboBox(panel, choices=file_choice, style=wx.CB_READONLY)
        self.CMB_file_choice = wx.ComboBox(panel, choices=file_choice, style=wx.CB_READONLY)
        self.galactic_direction_combo = wx.ComboBox(panel, choices=galactic_directions, style=wx.CB_READONLY) 
        self.thermal_mirror_material_combo = wx.ComboBox(panel, choices=thermal_mirror_materials, style=wx.CB_READONLY)
        self.zodiacal_direction_combo = wx.ComboBox(panel, choices=zodiacal_directions, style=wx.CB_READONLY)
        #a drop bar is not necessary for "Atmospheric Radiance" since the file is chosen in "Choose a Site" on the left
        
    # Top_right -> fill up contents
        #label checkboxes and drop menus for backgroundes in top right
        top_right.Add(parameter_labels[6], flag=wx.BOTTOM, border=6)
        top_right.Add(self.background_checkboxs[0], flag=wx.BOTTOM, border=3)
        top_right.Add(self.CIB_file_choice, flag=wx.LEFT, border=20)
        top_right.Add(self.background_checkboxs[1], flag=wx.BOTTOM, border=3)
        top_right.Add(self.CMB_file_choice, flag=wx.LEFT, border=20)
        top_right.Add(self.background_checkboxs[2], flag=wx.BOTTOM, border=3)
        top_right.Add(self.galactic_direction_combo, flag=wx.LEFT, border=20)
        top_right.Add(self.background_checkboxs[3], flag=wx.BOTTOM | wx.TOP, border=3)
        top_right.Add(self.thermal_mirror_material_combo, flag=wx.LEFT, border=20)
        top_right.Add(self.background_checkboxs[4], flag=wx.BOTTOM | wx.TOP, border=3)
        top_right.Add(self.background_checkboxs[5], flag=wx.BOTTOM, border=3)
        top_right.Add(self.zodiacal_direction_combo, flag=wx.LEFT, border=20)
        top_right.Add(self.background_checkboxs[6], flag=wx.BOTTOM, border=3)
        #CUMALATIVE NEEDS CUSTOM FEATURE
        
    # Bottom_left -> Controls
        #create list of what calculation should be done
        generate_label = wx.StaticText(panel, label='Generates:')
        generate_label.SetFont(font)  # Title

        self.check_Noise = wx.CheckBox(panel, label="Total Noise")
        self.check_Temp = wx.CheckBox(panel, label="Total Temperature")
        self.check_Signal = wx.CheckBox(panel, label="Total Signal")
        self.check_IntTime = wx.CheckBox(panel, label="Integration Time")

        #drop bars for bottom left
        BLING_units = ['photons/s-Hz^1/2', 'W/Hz^1/2 (Default)']
        self.BLING_units= wx.ComboBox(panel, choices=BLING_units, style=wx.CB_READONLY)
        
        # set default values
        self.check_Noise.SetValue(config.Noise_Default)
        self.check_Temp.SetValue(config.Temp_Default)
        self.check_Signal.SetValue(config.Signal_Default)
        self.check_IntTime.SetValue(config.IntTime_Default)

    # Bottom_left -> Fill up contents
        bottom_left.Add(generate_label, flag=wx.BOTTOM, border=10)
        bottom_left.Add(self.check_Noise, flag=wx.BOTTOM, border=2)
        bottom_left.Add(self.BLING_units, flag=wx.BOTTOM, border=4)
        bottom_left.Add(self.check_Temp, flag=wx.BOTTOM, border=2)
        bottom_left.Add(self.check_Signal, flag=wx.BOTTOM, border=2)
        bottom_left.Add(self.check_IntTime, flag=wx.BOTTOM, border=2)

    # Bottom_right
        # Bottom_right -> Output -> Controls
        #create textbox for outputting a data file
        #type in "name_of_file.type_of_file" and data will be written into it after generating plot
        #output file will be created in same location as this python file
        output_sizer = wx.BoxSizer(wx.HORIZONTAL)
        output_label = wx.StaticText(panel, label='Output to:')
        self.output_input = wx.TextCtrl(panel, size=(200, 30))
        output_button = wx.Button(panel, size=(80, 30), label='Browse')
        
    # Bottom_right -> Output -> Fill up contents
        bottom_right.Add(output_label, flag=wx.TOP, border=20)
        output_sizer.Add(self.output_input, flag=wx.EXPAND)
        output_sizer.Add(output_button)
        bottom_right.Add(output_sizer, flag=wx.BOTTOM, border=8)

    # Bottom_right -> Buttons
        #click generate to run calculation, create plot, and write output file
        generate_button = wx.Button(panel, label='Generate')
        cancel_button = wx.Button(panel, label='Cancel')
        
    # Bottom_right -> Buttons -> Fill up
        bottom_right.Add(generate_button, flag=wx.EXPAND | wx.BOTTOM, border=3)
        bottom_right.Add(cancel_button, flag=wx.EXPAND)

    # Bottom_right -> Function Bindings
        output_button.Bind(wx.EVT_BUTTON, self.onBrowse)
        generate_button.Bind(wx.EVT_BUTTON, self.onGenerate)
        cancel_button.Bind(wx.EVT_BUTTON, self.onCancel)
        
        # Fill up contents
        top.Add(top_left, flag=wx.RIGHT | wx.BOTTOM, border=25)
        top.Add(top_right, flag=wx.TOP | wx.BOTTOM, border=25)
        bottom.Add(bottom_left, flag=wx.RIGHT, border=35)
        bottom.Add(bottom_right, flag=wx.LEFT, border=35)
        content.Add(top, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        content.Add(bottom, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        panel.SetSizer(content)

    def onCustom(self, e): 
        # Generate frame and grid
        self.site_dialog = wx.Frame(self, title="Custom Site Files:", size=(300, 150)) 
        site_dialog_fgs = wx.FlexGridSizer(2, 3, 6, 6)  # declare FlexibleGridSizer

        # Generate
        self.site_dialog_labels = [wx.StaticText(self.site_dialog, label="Specify radiance file:"), wx.StaticText(self.site_dialog, label="specify transimission file:"), wx.StaticText(self.site_dialog, label=""), wx.StaticText(self.site_dialog, label="")]
        site_dialog_buttons = [wx.Button(self.site_dialog, label="Browse") for i in range(2)]
        site_dialog_ok = wx.Button(self.site_dialog, label="Ok")
        site_dialog_fgs.Add(self.site_dialog_labels[0], flag=wx.EXPAND | wx.TOP | wx.LEFT, border=20)
        site_dialog_fgs.Add(self.site_dialog_labels[2], flag=wx.EXPAND | wx.TOP, border=20)
        site_dialog_fgs.Add(site_dialog_buttons[0], flag=wx.EXPAND | wx.TOP | wx.RIGHT, border=20)
        site_dialog_fgs.Add(self.site_dialog_labels[1], flag=wx.EXPAND | wx.LEFT, border=20)
        site_dialog_fgs.Add(self.site_dialog_labels[3], flag=wx.EXPAND, border=20)
        site_dialog_fgs.Add(site_dialog_buttons[1], flag=wx.EXPAND | wx.RIGHT, border=20)
        site_dialog_fgs.AddMany([wx.StaticText(self.site_dialog, label="") for i in range(2)])
        site_dialog_fgs.Add(site_dialog_ok, flag=wx.EXPAND | wx.RIGHT, border=20)
        self.site_dialog.SetSizer(site_dialog_fgs)
        site_dialog_ok.Bind(wx.EVT_BUTTON, self.onDialogOk)

        self.site_dialog.Center()
        self.site_dialog.Show()

    def onRadianceBrowse(self, e):
        file_dialog = wx.FileDialog(self, style=wx.FD_SAVE)
        if file_dialog.ShowModal() == wx.ID_OK:  
            file_dialog.Destroy()      
        return
    def onTransmissionBrowse(self, e):
        return
    def onDialogOk(self, e):
        self.site_dialog.Destroy()

    def onBrowse(self, e):
        file_dialog = wx.FileDialog(self, style=wx.FD_OPEN)
        if file_dialog.ShowModal() == wx.ID_OK:
            self.path = file_dialog.GetPath()

            self.output_input.Clear()
            self.output_input.WriteText(self.path)  
        file_dialog.Destroy()        
        
    def onGenerate(self, e): #what follows are the functions
        
# initialization -> Parse inputs

        #There must be inputs for resolution, starting frequency, and ending frequency
        freq_start = float(self.input_StartFreq.GetValue())  #get starting frequency input as a float
        freq_end = float(self.input_StopFreq.GetValue())  #get ending frequency input as a float
        #the other inputs are only required to have entries if they are needed in the calculation that is checked

        if self.check_Noise.IsChecked() or self.check_Signal.IsChecked() or self.check_IntTime.IsChecked():  #only need resolution if any option other than "Total Temperature" is checked
            resol = float(self.input_SpecRes.GetValue())  #get resolution input as a float

        path = self.output_input.GetValue()  #get input as name of file to be written
        site = self.parameter_site_combo.GetValue()  #get name of chosen site
        source = self.parameter_source_combo.GetValue()  #get name of chosen source


# Calculate BLING
        if self.check_Noise.IsChecked() or self.check_IntTime.IsChecked():  #only do BLING calculations if "Total Noise" or "Integration Time" is checked
            start_time = time.time()  #begins clock for calculation time   
            bling_squared = 0  #checking boxes for different backgrounds will add values to this "bling_squared" array
                #the squares of BLINGs are added up since the final result is equal to BLINGs added in quadrature
            title_bling = []  #append names of which backgrounds are checked to put in title

#if "Cosmic Infrared Background" box or "Cumulative" is checked
            if self.background_checkboxs[0].IsChecked() or self.background_checkboxs[6].IsChecked():
##                index = self.CIB_file_choice.GetCurrentSelection()  #creates "index"=0, 1, & 2 depending on file for selection
##                if index == 0:  #if "Last Used" is selected
##                    ######CONSIDERING FITTING FUNCTION
##                elif index == 1:  #if "Default" is selected, use default file in file_refs.py    
                title_bling.append('Cosmic Infrared Background')
                cib_excel = file_refs.CIB_ref  #name excel file to read from
                cib = ExcelReader(cib_excel)
                print "Reading array from", cib_excel
                freqNoise = np.array(cib.read_from_col('Hz',freq_start * 1e12, freq_end * 1e12), dtype="float")  #create array of frequency(Hz) from 2nd column of excel file, reading as floats
                freqNoise_THz = freqNoise * 10 ** (-12)  #create array that converts "freqNoise" into THz
                print "len(freq)=", len(freqNoise)
                temp = np.array(cib.read_from_col('K',freq_start * 1e12, freq_end * 1e12), dtype="float")  #create array of temperature(K) from 5th column of excel file, reading as floats
                print "len(temp)=", len(temp)
                bling_squared += cal.bling_sub(freqNoise, temp, resol)  #calculate and add BLING(squared) of Cosmic Infrared Background to "bling_squared"

#if "Cosmic Microwave Background" or "Cumulative" box is checked
            if self.background_checkboxs[1].IsChecked() or self.background_checkboxs[6].IsChecked():
                title_bling.append('Cosmic Microwave Background')                
                index = self.CMB_file_choice.GetCurrentSelection()  #creates "index"=0, 1, or 2 depending on file for selection               
                if index == 0:  #if "Last Used" is selected
                    read_last_used = open("last used CMB file.txt", "r")  #read from "last used CMB file.txt"
                    cmb_file = read_last_used.read()
                elif index == 1:  #if "Default" is selected, use default file in file_refs.py
                    cmb_file = file_refs.CMB_ref
                elif index == 2:  #if "Choose New" is selected, open browser
                     # create window to let user know to pick the file
                    message_dialog = wx.MessageDialog(self, message='Select file for Cosmic Microwave Background')
                    if message_dialog.ShowModal() == wx.ID_OK:
                        message_dialog.Destroy()

                    # open file browser
                    file_dialog = wx.FileDialog(self, style=wx.FD_OPEN)
                    if file_dialog.ShowModal() == wx.ID_OK:
                        cmb_file = file_dialog.GetPath()
                    file_dialog.Destroy()

                # save into "last used CMB file.txt"
                write_last_used = open("last used CMB file.txt", "w")
                write_last_used.write(str(cmb_file))
                write_last_used.close()
                
                # perform calculations
                CMB = ExcelReader(cmb_file)
                print "Reading array from", cmb
                freqNoise = np.array(CMB.read_from_col('Hz',freq_start * 1e12, freq_end * 1e12), dtype="float")  #create array of frequency(Hz) from 2nd column of excel file, reading as floats
                freqNoise_THz = freqNoise * 10 ** (-12)  #create array that converts "freqNoise" into THz
                bling_squared += cal.bling_CMB(freqNoise, resol)  #calculate and add BLING(squared) of Cosmic Microwave Background to "bling_squared"

#if "Galactic Emission" or "Cumulative" box is checked
            if self.background_checkboxs[2].IsChecked() or self.background_checkboxs[6].IsChecked():
                index = self.galactic_direction_combo.GetCurrentSelection()  #creates "index"=0, 1, 2, 3, 4, or 5 depending on file for selection 
                if index == 0:  #if "Last Used" is selected
                    title_bling.append('Galactic Emission')
                    read_last_used = open("last used GE file.txt", "r")  #read from "last used GE file.txt"
                    ge_file = read_last_used.read()
                elif index == 1:  #if (g_long=0, g_lat=0) is selected, use the 1st default file in file_refs.py
                    title_bling.append('Galactic Emission(g_long=0, g_lat=0)')
                    ge_file = file_refs.Galatic_Emission_refs[0]  #index here(0) refers to file_refs.py not "self.galactic_direction_combo"
                elif index == 2:  #if (g_long=0, g_lat=45) is selected, use the 2nd default file in file_refs.py
                    title_bling.append('Galactic Emission(g_long=0, g_lat=45)')
                    ge_file = file_refs.Galatic_Emission_refs[1]  #index here(1) refers to file_refs.py not "self.galactic_direction_combo"
                elif index == 3:  #if (g_long=0, g_lat=90) is selected, use the 3rd default file in file_refs.py
                    title_bling.append('Galactic Emission(g_long=0, g_lat=90)')
                    ge_file = file_refs.Galatic_Emission_refs[2]  #index here(2) refers to file_refs.py not "self.galactic_direction_combo"
                elif index == 4:  #if (g_long=0, g_lat=-90) is selected, use the 4th default file in file_refs.py
                    title_bling.append('Galactic Emission(g_long=0, g_lat=-90)')
                    ge_file = file_refs.Galatic_Emission_refs[3]  #index here(3) refers to file_refs.py not "self.galactic_direction_combo"
                elif index == 5:  #if "Choose New" is selected, open browser
                    title_bling.append('Galactic Emission')
                    # create window to let user know to pick the file
                    message_dialog = wx.MessageDialog(self, message='Select file for Galactic Temperature')
                    if message_dialog.ShowModal() == wx.ID_OK:
                        message_dialog.Destroy()

                    # open file browser
                    file_dialog = wx.FileDialog(self, style=wx.FD_OPEN)
                    if file_dialog.ShowModal() == wx.ID_OK:
                        ge_file = file_dialog.GetPath()
                    file_dialog.Destroy()

                # save into "last used GE file.txt"
                write_last_used = open("last used GE file.txt", "w")
                write_last_used.write(str(ge_file))
                write_last_used.close()

                # perform calculations
                GE = ExcelReader(ge_file)
                freqNoise = np.array(GE.read_from_col('Hz',freq_start * 1e12, freq_end * 1e12), dtype='float')  #create array of frequency(Hz) from 2nd column of excel file, reading as floats
                freqNoise_THz = freqNoise * 10 ** (-12)  #create array that converts "freqNoise" into THz
                temp = np.array(GE.read_from_col('K',freq_start * 1e12, freq_end * 1e12), dtype='float')  #create array of temperature(K) from 9th column of excel file, reading as floats
                bling_squared += cal.bling_sub(freqNoise, temp, resol)  #calculate and add BLING(squared) of Galactic Emission to "bling_squared"

#if "Thermal Mirror Emission" or "Cumulative" box is checked 
            if self.background_checkboxs[3].IsChecked() or self.background_checkboxs[6].IsChecked():
                mirror_temp = float(self.input_MirrorTemp.GetValue())  #only need mirror temperature input if "Thermal Mirror Emission" is checked
                index = self.thermal_mirror_material_combo.GetCurrentSelection()  #creates "index"=0, 1, 2, or 3 depending on which material is selected
                if index == 0:  #if "Be" is selected
                    title_bling.append('Thermal Mirror Emission(Beryllium)')
                if index == 1:  #if "Al" is selected
                    title_bling.append('Thermal Mirror Emission(Aluminum)')
                if index == 2:  #if "Au" is selected
                    title_bling.append('Thermal Mirror Emission(Gold)')
                if index == 3:  #if "Ag" is selected
                    title_bling.append('Thermal Mirror Emission(Silver)')
                tme = ExcelReader(file_refs.TME_ref)  #name excel file to read from
                freqNoise = np.array(tme.read_from_col('Hz',freq_start * 1e12, freq_end * 1e12), dtype = 'float')  #create array of frequency(Hz) from 2nd column of excel file, reading as floats
                freqNoise_THz = freqNoise * 10 ** (-12)  #create array that converts "freqNoise" into THz
                sigma = const.sigma[index]  #from file "const", get "Material Constant" depending on which material is selected
                wavelength = np.array(tme.read_from_col('um',freq_start * 1e12, freq_end * 1e12), dtype = 'float')  #create array of wavelengths(microns)
                bling_squared += cal.bling_TME(freqNoise, resol, sigma, mirror_temp, wavelength)  #calculate and add BLING(squared) of Thermal Mirror Emission to "bling_sqared"

#if "Atmospheric Radiance" or "Cumulative" box is checked
            if self.background_checkboxs[4].IsChecked() or self.background_checkboxs[6].IsChecked():
                title_bling.append('Atmospheric Radiance')
                if site == "Choose New":  #if "Choose New" is selected, open browser
                    # create window to let user know to pick the file
                    message_dialog = wx.MessageDialog(self, message='Select file for site radiance')
                    if message_dialog.ShowModal() == wx.ID_OK:
                        message_dialog.Destroy()

                    # open file browser
                    file_dialog = wx.FileDialog(self, style=wx.FD_OPEN)
                    if file_dialog.ShowModal() == wx.ID_OK:
                        ar_file = file_dialog.GetPath()
                    file_dialog.Destroy()
                elif site == "Last Used":  #if "Last Used" is selected
                    read_last_used = open("last used AR file.txt", "r")  #read from "last used AR file.txt"
                    ar_file = read_last_used.read()
                else:  #if default file is selected, find file
                    ar_file = file_refs.atm_rad_refs[site]  #name excel file to read from, depending on site chosen
                    title_bling.append('[' + str(site) + ']')  #if site is chosen from list of known sites, can include name in plot title

                # save into "last used AR file.txt"
                write_last_used = open("last used AR file.txt", "w")
                write_last_used.write(str(ar_file))
                write_last_used.close()

                # perform calculations
                AR = ExcelReader(ar_file)
                freqNoise = np.array(AR.read_from_col('Hz',freq_start * 1e12, freq_end * 1e12), dtype='float')  #create array of frequency(Hz) from 2nd column of excel file, reading as floats
                freqNoise_THz = freqNoise * 10 ** (-12)  #create array that converts "freqNoise" into THz
                rad = np.array(AR.read_from_col(0,freq_start * 1e12, freq_end * 1e12,'TOTAL RAD'), dtype='float')  #create array of radiance(W/cm^2/st/cm^-1) from 5th column of excel file, reading as floats
                bling_squared += cal.bling_AR(freqNoise, rad, resol)  #calculate and add BLING(squared) of Atmospheric Radiance to "bling_squared"

#if "Zodiacial Emission" or "Cumulative" box is checked
            if self.background_checkboxs[5].IsChecked() or self.background_checkboxs[6].IsChecked():
                index = self.zodiacal_direction_combo.GetCurrentSelection()  #creates "index"=0, 1, 2, 3, or 4 depending on which ecliptic coordinates are selected
                if index == 0:  #if "Last Used" is selected
                    title_bling.append('Zodiacal Emission')
                    read_last_used = open("last used ZE file.txt", "r")  #read from "last used ZE file.txt"
                    ze = read_last_used.read()
                if index == 1:  #if (g_long=0,g_lat=0) is selected, use the 1st default file in file_refs.py
                    title_bling.append('Zodiacal Emission(g_long=0,g_lat=0)')
                    ze = file_refs.ZODI_refs[0]  #index here(0) refers to file_refs.py not "self.zodiacal_direction_combo"
                if index == 2:  #if (g_long=0,g_lat=45) is selected, use the 2nd default file in file_refs.py
                    title_bling.append('Zodiacal Emission(g_long=0,g_lat=45)')
                    ze = file_refs.ZODI_refs[1]  #index here(1) refers to file_refs.py not "self.zodiacal_direction_combo"
                if index == 3:  #if (g_long=0,g_lat=90) is selected, use the 3rd default file in file_refs.py
                    title_bling.append('Zodiacal Emission(g_long=0,g_lat=90)')
                    ze = file_refs.ZODI_refs[2]  #index here(2) refers to file_refs.py not "self.zodiacal_direction_combo"
                if index == 4:  #if "Choose New" is selected
                    title_bling.append('Zodiacal Emission')
                    # create window to let user know to pick the file
                    message_dialog = wx.MessageDialog(self, message='Select file for Zodiacal Temperature')
                    if message_dialog.ShowModal() == wx.ID_OK:
                        message_dialog.Destroy()

                    # open file browser
                    file_dialog = wx.FileDialog(self, style=wx.FD_OPEN)
                    if file_dialog.ShowModal() == wx.ID_OK:
                        ze = file_dialog.GetPath()
                    file_dialog.Destroy()
                    
                # save into "last used ZE file.txt"
                write_last_used = open("last used ZE file.txt", "w")
                write_last_used.write(str(ze))
                write_last_used.close()

                # perform calculations
                ZE = ExcelReader(ze)
                freqNoise = np.array(ZE.read_from_col('Hz',freq_start * 1e12, freq_end * 1e12), dtype='float')  #create array of frequency(Hz) from 2nd column of excel file, reading as floats
                freqNoise_THz = freqNoise * 10 ** (-12)  #create array that converts "freqNoise" into THz
                temp = np.array(ZE.read_from_col('K',freq_start * 1e12, freq_end * 1e12), dtype='float')  #create array of temperature(K) from 5th column of excel file, reading as floats
                bling_squared += cal.bling_sub(freqNoise, temp, resol)  #calculate and add BLING(squared) of Zodiacal Emission to "bling_squared"
            
            bling_TOT = (bling_squared) ** 0.5  #"bling_squared" is the sum of the squared bling of each background so "bling_TOT" is the radical of "bling_squared" since the result is the BLINGS added in quadrature
				#BLING_TOT is in W/Hz^1/2
            
			#we also convert W/Hz^1/2 to photons/s-Hz^1/2 by Power(watts)=N(photons/s)*h*nu where nu is in Hz and h is Planck's Constant
            energy = freqNoise*const.h
            bling_TOT_photon = np.divide(bling_TOT,energy)
			
            end_time = time.time()  #stops clock for calculation time
            print "BLING calculation DONE"
            print "Time used for BLING calculation: ", end_time - start_time, " seconds"

            if self.background_checkboxs[6].IsChecked():  #setting title to 'Noise[Total]' if all BLINGs are checked
                title_bling = '[Total]'


# Calculate Antenna Temperature
        if self.check_Temp.IsChecked():
            start_time = time.time()  #begins clock for calculation time   
            temperature = 0  #checking boxes for different backgrounds will add values to this "temperature" array
            title_temp = []  #append names of which backgrounds are checked to put in title

#if "Cosmic Infrared Background" box is checked
            if self.background_checkboxs[0].IsChecked() or self.background_checkboxs[6].IsChecked():
                title_temp.append('Cosmic Infrared Background')
                cib_excel = file_refs.CIB_ref  #name excel file to read from
                cib = ExcelReader(cib_excel)
                print "Reading array from", cib_excel
                freqNoise = np.array(cib.read_from_col('Hz',freq_start * 1e12, freq_end * 1e12), dtype="float")  #create array of frequency(Hz) from 2nd column of excel file, reading as floats
                freqNoise_THz = freqNoise * 10 ** (-12)  #create array that converts "freqNoise" into THz
                temp = np.array(cib.read_from_col('K',freq_start * 1e12, freq_end * 1e12), dtype="float")  #create array of temperature(K) from 5th column of excel file, reading as floats
                temperature += temp  #no calculations are needed to add temperature of Cosmic Infrared Background to "temperature"

#if "Cosmic Microwave Background" box is checked
            if self.background_checkboxs[1].IsChecked() or self.background_checkboxs[6].IsChecked():
                if self.background_checkboxs[1].IsChecked() or self.background_checkboxs[6].IsChecked():
                    title_temp.append('Cosmic Microwave Background')                
                    index = self.CMB_file_choice.GetCurrentSelection()  #creates "index"=0, 1, or 2 depending on file for selection               
                if index == 0:  #if "Last Used" is selected
                    read_last_used = open("last used CMB file.txt", "r")  #read from "last used GE file.txt"
                    cmb = read_last_used.read()
                elif index == 1:  #if "Default" is selected, use default file in file_refs.py
                    cmb = file_refs.CMB_ref
                elif index == 2:  #if "Choose New" is selected, open browser
                     # create window to let user know to pick the file
                    message_dialog = wx.MessageDialog(self, message='Select file for Cosmic Microwave Background')
                    if message_dialog.ShowModal() == wx.ID_OK:
                        message_dialog.Destroy()

                    # open file browser
                    file_dialog = wx.FileDialog(self, style=wx.FD_OPEN)
                    if file_dialog.ShowModal() == wx.ID_OK:
                        cmb = file_dialog.GetPath()
                    file_dialog.Destroy()

                # save into "last used CMB file.txt"
                write_last_used = open("last used CMB file.txt", "w")
                write_last_used.write(str(cmb))
                write_last_used.close()
                
                # perform calculations
                CMB = ExcelReader(cmb)                
                print "Reading array from", cmb
                freqNoise = np.array(CMB.read_from_col('Hz',freq_start * 1e12, freq_end * 1e12), dtype="float")  #create array of frequency(Hz) from 2nd column of excel file, reading as floats
                freqNoise_THz = freqNoise * 10 ** (-12)  #create array that converts "freqNoise" into THz
                temperature += cal.temp_CMB(freqNoise)  #calculate and add temperature of Cosmic Microwave Background to "temperature"

#if "Galactic Emission" box is checked
            if self.background_checkboxs[2].IsChecked() or self.background_checkboxs[6].IsChecked():
                index = self.galactic_direction_combo.GetCurrentSelection()  #creates "index"=0, 1, 2, 3, 4, or 5 depending on file for selection 
                if index == 0:  #if "Last Used" is selected
                    title_bling.append('Galactic Emission')
                    read_last_used = open("last used GE file.txt", "r")  #read from "last used GE file.txt"
                    ge = read_last_used.read()
                elif index == 1:  #if (g_long=0, g_lat=0) is selected, use the 1st default file in file_refs.py
                    title_bling.append('Galactic Emission(g_long=0, g_lat=0)')
                    ge = file_refs.Galatic_Emission_refs[0]  #index here(0) refers to file_refs.py not "self.galactic_direction_combo"
                elif index == 2:  #if (g_long=0, g_lat=45) is selected, use the 2nd default file in file_refs.py
                    title_bling.append('Galactic Emission(g_long=0, g_lat=45)')
                    ge = file_refs.Galatic_Emission_refs[1]  #index here(1) refers to file_refs.py not "self.galactic_direction_combo"
                elif index == 3:  #if (g_long=0, g_lat=90) is selected, use the 3rd default file in file_refs.py
                    title_bling.append('Galactic Emission(g_long=0, g_lat=90)')
                    ge = file_refs.Galatic_Emission_refs[2]  #index here(2) refers to file_refs.py not "self.galactic_direction_combo"
                elif index == 4:  #if (g_long=0, g_lat=-90) is selected, use the 4th default file in file_refs.py
                    title_bling.append('Galactic Emission(g_long=0, g_lat=-90)')
                    ge = file_refs.Galatic_Emission_refs[3]  #index here(3) refers to file_refs.py not "self.galactic_direction_combo"
                elif index == 5:  #if "Choose New" is selected, open browser
                    title_bling.append('Galactic Emission')
                    # create window to let user know to pick the file
                    message_dialog = wx.MessageDialog(self, message='Select file for Galactic Temperature')
                    if message_dialog.ShowModal() == wx.ID_OK:
                        message_dialog.Destroy()

                    # open file browser
                    file_dialog = wx.FileDialog(self, style=wx.FD_OPEN)
                    if file_dialog.ShowModal() == wx.ID_OK:
                        ge = file_dialog.GetPath()
                    file_dialog.Destroy()

                # perform calculations
                GE = ExcelReader(ge)
                freqNoise = np.array(GE.read_from_col('Hz',freq_start * 1e12, freq_end * 1e12), dtype='float')  #create array of frequency(Hz) from 2nd column of excel file, reading as floats
                freqNoise_THz = freqNoise * 10 ** (-12)  #create array that converts "freqNoise" into THz
                temp = np.array(GE.read_from_col('K',freq_start * 1e12, freq_end * 1e12), dtype='float')  #create array of temperature(K) from 9th column of excel file, reading as floats
                temperature += temp  #no calculations are needed to add temperature of Galactic Emission to "temperature"

#if "Thermal Mirror Emission" box is checked 
            if self.background_checkboxs[3].IsChecked() or self.background_checkboxs[6].IsChecked():
                mirror_temp = float(self.input_MirrorTemp.GetValue())  #only need mirror temperature input if "Thermal Mirror Emission" is checked
                index = self.thermal_mirror_material_combo.GetCurrentSelection()  #creates "index"=0, 1, 2, or 3 depending on which material is selected
                if index == 0:  #if "Be" is selected
                    title_temp.append('Thermal Mirror Emission(Beryllium)')
                if index == 1:  #if "Al" is selected
                    title_temp.append('Thermal Mirror Emission(Aluminum)')
                if index == 2:  #if "Au" is selected
                    title_temp.append('Thermal Mirror Emission(Gold)')
                if index == 3:  #if "Ag" is selected
                    title_temp.append('Thermal Mirror Emission(Silver)')
                tme = ExcelReader(file_refs.TME_ref)  #name excel file to read from
                freqNoise = np.array(tme.read_from_col('Hz',freq_start * 1e12, freq_end * 1e12), dtype = 'float')  #create array of frequency(Hz) from 2nd column of excel file, reading as floats
                freqNoise_THz = freqNoise * 10 ** (-12)  #create array that converts "freqNoise" into THz
                sigma = const.sigma[index]  #from file "const", get "Material Constant" depending on which material is selected
                wavelength = np.array(tme.read_from_col('um',freq_start * 1e12, freq_end * 1e12), dtype = 'float')  #create array of wavelengths(microns)
                temperature += cal.temp_TME(freqNoise, sigma, mirror_temp, wavelength)  #calculate and add temperature of Thermal Mirror Emission to "temperature"

#if "Atmospheric Radiance" box is checked
            if self.background_checkboxs[4].IsChecked() or self.background_checkboxs[6].IsChecked():
                title_temp.append('Atmospheric Radiance')  #title depends on name of site chosen
                if site == "Choose New":  #if "Choose New" is selected, open browser
                    # create window to let user know to pick the file
                    message_dialog = wx.MessageDialog(self, message='Select file for site radiance')
                    if message_dialog.ShowModal() == wx.ID_OK:
                        message_dialog.Destroy()

                    # open file browser
                    file_dialog = wx.FileDialog(self, style=wx.FD_OPEN)
                    if file_dialog.ShowModal() == wx.ID_OK:
                        ar_file = file_dialog.GetPath()
                    file_dialog.Destroy()
                elif site == "Last Used":  #if "Last Used" is selected
                    read_last_used = open("last used AR file.txt", "r")  #read from "last used AR file.txt"
                    ar_file = read_last_used.read()
                else:  #if default file is selected, find file
                    ar_file = file_refs.atm_rad_refs[site]  #name excel file to read from, depending on site chosen
                    title_temp.append('[' + str(site) + ']')  #if site is chosen from list of known sites, can include name in plot title

                # save into "last used AR file.txt"
                write_last_used = open("last used AR file.txt", "w")
                write_last_used.write(str(ar_file))
                write_last_used.close()

                # perform calculations
                AR_temp = ExcelReader(ar_file)
                freqNoise = np.array(AR_temp.read_from_col('Hz',freq_start * 1e12, freq_end * 1e12), dtype='float')  #create array of frequency(Hz) from 2nd column of excel file, reading as floats
                freqNoise_THz = freqNoise * 10 ** (-12)  #create array that converts "freqNoise" into THz
                rad = np.array(AR_temp.read_from_col(0,freq_start * 1e12, freq_end * 1e12,'TOTAL RAD'), dtype='float')  #create array of radiance(W/cm^2/st/cm^-1) from 5th column of excel file, reading as floats
                temperature += cal.temp_AR(freqNoise, rad)  #calculate and add temperature of Atmospheric Radiance to "temperature"

#if "Zodiacial Emission" box is checked
            if self.background_checkboxs[5].IsChecked() or self.background_checkboxs[6].IsChecked():
                index = self.zodiacal_direction_combo.GetCurrentSelection()  #creates "index"=0, 1, 2, 3, or 4 depending on which ecliptic coordinates are selected
                if index == 0:  #if "Last Used" is selected
                    title_temp.append('Zodiacal Emission')
                    read_last_used = open("last used ZE file.txt", "r")  #read from "last used ZE file.txt"
                    ze = read_last_used.read()
                if index == 1:  #if (g_long=0,g_lat=0) is selected, use the 1st default file in file_refs.py
                    title_temp.append('Zodiacal Emission(g_long=0,g_lat=0)')
                    ze = file_refs.ZODI_refs[0]  #index here(0) refers to file_refs.py not "self.zodiacal_direction_combo"
                if index == 2:  #if (g_long=0,g_lat=45) is selected, use the 2nd default file in file_refs.py
                    title_temp.append('Zodiacal Emission(g_long=0,g_lat=45)')
                    ze = file_refs.ZODI_refs[1]  #index here(1) refers to file_refs.py not "self.zodiacal_direction_combo"
                if index == 3:  #if (g_long=0,g_lat=90) is selected, use the 3rd default file in file_refs.py
                    title_temp.append('Zodiacal Emission(g_long=0,g_lat=90)')
                    ze = file_refs.ZODI_refs[2]  #index here(2) refers to file_refs.py not "self.zodiacal_direction_combo"
                if index == 4:  #if "Choose New" is selected
                    title_temp.append('Zodiacal Emission')
                    # create window to let user know to pick the file
                    message_dialog = wx.MessageDialog(self, message='Select file for Zodiacal Temperature')
                    if message_dialog.ShowModal() == wx.ID_OK:
                        message_dialog.Destroy()

                    # open file browser
                    file_dialog = wx.FileDialog(self, style=wx.FD_OPEN)
                    if file_dialog.ShowModal() == wx.ID_OK:
                        ze = file_dialog.GetPath()
                    file_dialog.Destroy()
                    
                # save into "last used ZE file.txt"
                write_last_used = open("last used ZE file.txt", "w")
                write_last_used.write(str(ze))
                write_last_used.close()

                # perform calculations
                ZE = ExcelReader(ze)                
                freqNoise = np.array(ZE.read_from_col('Hz',freq_start * 1e12, freq_end * 1e12), dtype='float')  #create array of frequency(Hz) from 2nd column of excel file, reading as floats
                freqNoise_THz = freqNoise * 10 ** (-12)  #create array that converts "freqNoise" into THz
                temp = np.array(ZE.read_from_col('K',freq_start * 1e12, freq_end * 1e12), dtype='float')  #create array of temperature(K) from 5th column of excel file, reading as floats
                temperature += temp  #no calculations are needed to add temperature of Zodiacal Emission to "temperature"
            
            end_time = time.time()  #stops clock for calculation time
            print "Temperature calculation DONE"
            print "Time.GetValue() used for temperature calculation: ", end_time - start_time, " seconds"

            if self.background_checkboxs[6].IsChecked():  #setting title to 'Temperature[Total]' if all backgrounds are checked
                title_temp = '[Total]'


# Calculate Total Signal
        if self.check_Signal.IsChecked() or self.check_IntTime.IsChecked():  #only do signal calculation if "Total Signal" or "Integration Time" is checked
# Calculate Source Intensity
            d = float(self.input_MirrorDiam.GetValue())  #only need mirror diameter input if "Total Signal" is checked
            if source == "Choose New":  #find file of custom source
                # create window to let user know to pick the file
                message_dialog = wx.MessageDialog(self, message='Select file for source')
                if message_dialog.ShowModal() == wx.ID_OK:
                    message_dialog.Destroy()

                # open file browser
                file_dialog = wx.FileDialog(self, style=wx.FD_OPEN)
                if file_dialog.ShowModal() == wx.ID_OK:
                    self.source = file_dialog.GetPath()
                    si = self.source
                file_dialog.Destroy()
            elif source == "Last Used":
                read_last_used = open("last used SI file.txt", "r") #read from "last used SI file.txt"
                si = read_last_used.read()
            else:  #if source not custom, find file in file_refs.py
                si = file_refs.source_refs[source]  #find file of source galaxy
            
            # perform calculations
            SI = ExcelReader(si)
            freq = np.array(SI.read_from_col('Hz',freq_start * 1e12, freq_end * 1e12), dtype='float')  #create list of frequency(Hz) from 2nd column of excel file
            inte = np.array(SI.read_from_col('W M-2 Hz-1',freq_start * 1e12, freq_end * 1e12), dtype='float')  #create list of intensity(Jy) from 6th column of excel file, reading as floats
            print "Reading from source. DONE"
            
            # save into "last used SI file.txt"
            write_last_used = open("last used SI file.txt", "w")
            write_last_used.write(str(si))
            write_last_used.close()
            
# Calculate Total Signal
            if site == "Choose New":  #find file of custom site
                # create window to let user know to pick the file
                message_dialog = wx.MessageDialog(self, message='Select file for site')
                if message_dialog.ShowModal() == wx.ID_OK:
                    message_dialog.Destroy()

                # open file browser
                file_dialog = wx.FileDialog(self, style=wx.FD_OPEN)
                if file_dialog.ShowModal() == wx.ID_OK:
                    self.site_trans = file_dialog.GetPath()
                    at = self.site_trans
                file_dialog.Destroy()
            elif site == "Last Used":
                read_last_used = open("last used AT file.txt", "r") #read from "last used AT file.txt"
                at = read_last_used.read()
            else:  #if site not custom, find file in file_refs.py
                at = file_refs.atm_tran_refs[site]  #find file of site transmission

            # perform calculations    
            AT = ExcelReader(at)
            tau = np.array(AT.read_from_col(0,freq_start * 1e12, freq_end * 1e12,'COMBIN TRANS'), dtype='float')  #create array of transmission from 5th column of excel file, reading as floats
            print "Reading from Atmosphere Transmission. DONE"

            # save into "last used AT file.txt"
            write_last_used = open("last used AT file.txt", "w")
            write_last_used.write(str(at))
            write_last_used.close()

            # final Signal calculations
            print "Calculating Total Signal.."
            start_time = time.time()  #begins clock for calculation time
            ts = cal.TS(freq, inte, tau, d, resol)  #returns array of total signal from inputs
            end_time = time.time()  #stops clock for calculation time
            print "Total Signal calculation DONE"
            print "Time used for Total Signal calculation: ", end_time - start_time, " seconds"
            freq_THz = freq * 10 ** (-12)  #create array that converts "freq" into THz


# Plotting and writing file
# instead of having a plotter module, a plotting function is defined here so the y-axis range is adjustable though it may be wiser to define this in a module
        def loglogplot(x, y):
            print "Start plotting..."
##            pos = np.where(np.abs(np.diff(y)) >= .0015)[0] + 1  #jumps over .0015 THz(1.5 GHz) are not connected
##            #x = np.insert(x, pos, np.nan)  #replace values in "x" that correspond to nonpositives in "y" with "not a number"s
##            y = np.insert(y, pos, np.nan)  #replace nonpositives in "y" with "not a number"s
            #for reason yet to be determined, the preceding 3 lines don't work with "Integration Time" so that calculation has its own plotting function
            #also, these 3 lines didn't work with a noise calculation in photons.  however it did work with the exact same noise calculation in watts.
            
            pylab.plot(x, y)
            pylab.xscale('log')
            pylab.yscale('log')
            pylab.xlim(freq_start, freq_end)  #define x-axis range by inputs
            if self.dependent_limits_checkbox.IsChecked():  #if "Manually Input Range of Dependent Axis" box is checked, values must be input for following 2 boxes
                start_magnitude = float(self.input_DependMin.GetValue())  #get order of magnitude for y-axis minumum
                dep_start = 10 ** start_magnitude  #turn order of magnitude into value of minimum
                end_magnitude = float(self.input_DependMax.GetValue())  #get order of magnitude for y-axis maximum
                dep_end = 10 ** end_magnitude  #turn order of magnitude into value of maximum
                pylab.ylim(dep_start, dep_end)


#if "Total Noise" is checked
        if self.check_Noise.IsChecked():
            # write file
            xw = ExcelXWriter(path)  #create xlsx file named after the input
            #each of the following adds a new column
            xw.write_col('freq(cm^-1)', freqNoise / (3 * 10**10))
            xw.write_col('freq(Hz)', freqNoise)
            xw.write_col('freq(THz)', freqNoise_THz)
            xw.write_col('wavelength(um)', (3 * 10**8) / freqNoise * 10**6) 
            xw.write_col('Total Noise_BLING(W Hz^(-1/2))', bling_TOT)
            xw.write_col('Total Noise_BLING(Photon/s Hz^(-1/2))', bling_TOT_photon)

            # draw plot
            if self.BLING_units.GetValue() == "photons/s-Hz^1/2": #Noise plot if photon/sec is selected
                loglogplot(freqNoise_THz, bling_TOT_photon)
                pylab.ylabel("BLING(photons/s-Hz^1/2)")
            else: #Noise plot if Watts is selected
                loglogplot(freqNoise_THz, bling_TOT)
                pylab.ylabel("BLING(W*Hz^(-1/2))")
            pylab.xlabel("Frequency(THz)")
            title = "Noise" + str(title_bling) + " vs. Frequency at Spectral Resolution of " + str(resol) + ".\nFrequency is from " + str(freq_start) + " to " + str(freq_end) + "THz.  "
            if self.background_checkboxs[3].IsChecked() or self.background_checkboxs[6].IsChecked():  #if "Thermal Mirror Emission" is included, add "mirror_temp" to the title
                title = title + "Mirror has temperature " + str(mirror_temp) + "K.  "
            if self.background_checkboxs[4].IsChecked() or self.background_checkboxs[6].IsChecked():  #if "Atmospheric" is included, add the site to the title
                title = title + str(site) + " is the site."
            pylab.suptitle(title, fontsize=10)            
            pylab.show()


#if "Total Temperature" is checked
        if self.check_Temp.IsChecked():
            # write file
            xw = ExcelXWriter(path)  #create xlsx file named after the input
            #each of the following adds a new column
            xw.write_col('freq(cm^-1)', freqNoise / (3 * 10**10))
            xw.write_col('freq(Hz)', freqNoise)
            xw.write_col('freq(THz)', freqNoise_THz)
            xw.write_col('wavelength(um)', (3 * 10**8) / freqNoise * 10**6) 
            xw.write_col('Total Temperature(K)', temperature)

            # draw plot
            loglogplot(freqNoise_THz, temperature)  #plot of Temperature is log(base 10)-scaled
            pylab.ylabel("Temperature(Kelvin)")
            pylab.xlabel("Frequency(THz)")
            title = "Temperature" + str(title_temp) + " vs. Frequency.\nFrequency is from " + str(freq_start) + " to " + str(freq_end) + "THz.  "
            if self.background_checkboxs[3].IsChecked() or self.background_checkboxs[6].IsChecked():  #if "Thermal Mirror Emission" is included, add "mirror_temp" to the title
                title = title + "Mirror has temperature " + str(mirror_temp) + "K.  "
            if self.background_checkboxs[4].IsChecked() or self.background_checkboxs[6].IsChecked():  #if "Atmospheric" is included, add the site to the title
                title = title + str(site) + " is the site."
            pylab.suptitle(title, fontsize=10)            
            pylab.show()


#if "Total Signal" is checked
        if self.check_Signal.IsChecked():
            # draw plot
            loglogplot(freq_THz, ts)  #plot of signal is log(base 10)-scaled
            pylab.ylabel("Signal(W)")
            pylab.xlabel("Frequency(THz)")
            pylab.suptitle("Total Signal vs. Frequency at " + str(site) + " from " + str(source) + ".\nSpectral Resolution is " + str(resol) + " and frequency is from " + str(freq_start) + " to " + str(freq_end) + "THz.\nMirror has diameter " + str(d) + "m.", fontsize=10)
            pylab.show()

            # write file
            xw = ExcelXWriter(path)  #creates xlsx file with the name inputted
            #each of the following adds a new column
            xw.write_col('freq(cm^-1)', freq / (3 * 10**10))
            xw.write_col('freq(Hz)', freq)
            xw.write_col('freq(THz)', freq_THz)
            xw.write_col('wavelength(um)', (3 * 10**8) / freq * 10**6)
            xw.write_col('Total signal(W)', ts)


#if "Integration Time" is checked
        if self.check_IntTime.IsChecked():
            ratio = float(self.input_SigNoise.GetValue())  #"Signal to Noise Ratio" is only new input if "Integration Time" is checked(inputs for Signal and Noise are still necessary)

            # draw plot
            integration_time = cal.IT(bling_TOT, ratio, ts)  #returns array of integration time after signal and BLING are calculated
            print "Integration Time is " + str(integration_time)            
            # don't use "loglogplot" function because it doesn't work with "Integration Time"(it puts "not a number" between each value without deleting the old value so the list alternates between data and "not a number"s)
            loglogplot(freq_THz,integration_time)
            pylab.plot(freq_THz, integration_time)
            pylab.xscale('log')
            pylab.yscale('log')
            pylab.xlim(freq_start, freq_end)  #define x-axis range by inputs
            if self.dependent_limits_checkbox.IsChecked():  #if "Manually Input Range of Dependent Axis" box is checked, values must be input for following 2 boxes
                start_magnitude = float(self.input_DependMin.GetValue())  #get order of magnitude for y-axis minumum
                dep_start = 10 ** start_magnitude  #turn order of magnitude into value of minimum
                end_magnitude = float(self.input_DependMax.GetValue())  #get order of magnitude for y-axis maximum
                dep_end = 10 ** end_magnitude  #turn order of magnitude into value of maximum
                pylab.ylim(dep_start, dep_end)            
            pylab.ylabel("Integration Time(sec)")
            pylab.xlabel("Frequency(THz)")
            title = "Integration time vs. Frequency at " + str(site) + " from " + str(source) + ".\nSpectral Resolution is " + str(resol) + " and frequency is from " + str(freq_start) + " to " + str(freq_end) + "THz.\nSignal to Noise ratio is " + str(ratio) + " and mirror diameter is " + str(d) + "m."
            if self.background_checkboxs[3].IsChecked() or self.background_checkboxs[6].IsChecked():  #if "Thermal Mirror Emission" is included, add "mirror_temp" to the title
                title = title + "  Mirror has temperature " + str(mirror_temp) + "K."
            pylab.suptitle(title, fontsize=10)
            pylab.show()
            
            # write file
            xw = ExcelXWriter(path)  #creates xlsx file with the name inputted
            #each of the following adds a new column
            xw.write_col('freq(cm^-1)', freq / (3 * 10**10))
            xw.write_col('freq(Hz)', freq)
            xw.write_col('freq(THz)', freq_THz)
            xw.write_col('wavelength(um)', (3 * 10**8) / freq * 10**6)
            xw.write_col('BLING(W*Hz^(-1/2))', bling_TOT)
            xw.write_col('Signal(W)', ts)
            xw.write_col('Integration Time(s)', integration_time)

            
        # xw.save()
        print "Plotting. DONE"
        
       
        # message box alert
        message_dialog = wx.MessageDialog(self, message='Successfully Generated!')
        message_dialog.SetTitle("Successful!")
        if message_dialog.ShowModal() == wx.ID_OK:
            message_dialog.Destroy()

    def onCancel(self, e):
        self.Destroy()
        
if __name__ == '__main__':
  
    app = wx.App()
    atmodel(None, title='Atmosphere Modeling for Telescope')
    app.MainLoop()
