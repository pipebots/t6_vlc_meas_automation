#-----------------------------------------------------------------------------------------------------------------------#	
# Function: vlc_led_test               							      				                                    #
# Purpose: VLC LED Test Script                                                 	                               		    #
# Parameters: 										                                                                    #
# Author: TJA														                                                    #
# Date: 06/12/2021													                                                    #
# Revision: A														                                                    #
# Status: In development											                                                    #
#-----------------------------------------------------------------------------------------------------------------------#

#imports
import pyvisa # available changed from visa
import binascii # available
import csv # available
import sys # available
import importlib # available changed from import imp - depricated
import os # available
import time # available

#set top level directory path
dirpath = '/home/instrument/Desktop/'

#append source directory
sys.path.append (dirpath+'vlc_rig')

import equip
import csvf
import user
#import macro

#-----------------------------------------------------------------------------------------------------------------------#
 
#echo information to the screen
#clear screen and display logo
#user.scrn_clr()
user.scrn_print("---------------------------------------------------------------","")
user.scrn_print("University of Leeds (c)2021","")
user.scrn_print("Author T J Amsdon","")
user.scrn_print("VLC Characterisation System","")
user.scrn_print("---------------------------------------------------------------","")

user.scrn_print("---------------------------------------------------------------","")
user.scrn_print("Ensure ALL required equipment is powered-up and initialised......","")
user.scrn_print("---------------------------------------------------------------","")
#input("PRESS ENTER TO CONTINUE")

#-----------------------------------------------------------------------------------------------------------------------#

#define test results and screen capture files
CSV_FILE_NAME_RESULTS="results.csv" #general test data
CSV_FILE_NAME_CAPTURES="captures.csv" #spectrum analyser screen captures
CSV_PATH="/home/instrument/Desktop/vlc_rig/"  

#-----------------------------------------------------------------------------------------------------------------------#
#MAIN() FUNCTION CALL BEGIN
def main():

 #pyVISA connections
 rm = pyvisa.ResourceManager("/lib/x86_64-linux-gnu/libivivisa.so")

 #test equipment list  
 addr_spec_an = rm.open_resource("TCPIP0::10.42.0.90::inst0::INSTR") #N9000A Signal Analyser
 addr_sig_gen = rm.open_resource("TCPIP0::10.42.0.38::inst0::INSTR") #E4438C Signal Generator
 addr_osc_scope = rm.open_resource("TCPIP0::10.42.0.60::inst0::INSTR") #DSO6014A Oscilloscope
 #addr_psu = rm.get_instrument("TCPIP0::10.42.0.72::18190::SOCKET") #72-13330 DC Power Supply

#-----------------------------------------------------------------------------------------------------------------------#

 #create datetime stamp
 dtstamp = csvf.csv_dtstamp()

#-----------------------------------------------------------------------------------------------------------------------#
 
 #!!!!!!!!!!!!!!!!!!!!!!!!USER DEFINED INPUT BEGIN!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
 #DUT description
 
 led_mfr_name = "Osram"                          # LED manufacturer (no spaces allowed)
 led_mfr_prtnum = "FW8-15265"                    # LED manufacturer part number (no spaces allowed)
 led_mfr_srnum = "15265A14300000065"             # LED manufacturer serial number (no spaces allowed)
 led_wavelength_nm = 470.0                       # LED wavelength (nm)
 led_fwd_volt = 2.75                             # LED forward voltage (V)
 led_fwd_current = 500                           # LED forward current (mA)
 led_view_angle = 35                             # LED angle of view (degrees)
 led_material = "InGaN"                          # LED semiconductor material


 #user information used in file headers and automated email function
 #!!!!!MS OUTLOOK MUST BE OPEN ON THE MACHINE AUTO EMAILING TO WORK!!!!!
  
 tester = "t.j.amsdon@leeds.ac.uk"        # email address of test operator (no spaces allowed)
 #!!!!!!!!!!!!!!!!!!!!!!!!USER DEFINED INPUT END!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
 
#-----------------------------------------------------------------------------------------------------------------------#

 #test equipment initialisation
 spec_an = equip.init_cxa(addr_spec_an)
 sig_gen = equip.init_esg(addr_sig_gen)
 osc_scope = equip.init_dso(addr_osc_scope)
 #psu = equip.init_psu(addr_psu) // need to setup names in equip file

 #Dummy place holder for the PSU
 psu = "72-13330 DC Power Supply"
#-----------------------------------------------------------------------------------------------------------------------# 
 
#-----------------------------------------------------------------------------------------------------------------------# 
 
 #create CSV results and capture files and create headers for each

#automatically create CSV file for results and screen captures
 fd_results = csvf.csv_file(CSV_PATH,CSV_FILE_NAME_RESULTS, dtstamp, led_mfr_name, led_mfr_prtnum, led_mfr_srnum)
 fd_captures = csvf.csv_file(CSV_PATH,CSV_FILE_NAME_CAPTURES, dtstamp, led_mfr_name, led_mfr_prtnum, led_mfr_srnum)
 
 #create file headers 
 csvf.fappn(fd_results, "dt stamp", "tester", "mfct", "mfct prt num" , "serial num", "LED wavelenght (nm)", "LED forward voltage (V)", "LED forward current (V)", "LED angle of view (degrees)", "LED material", "", "", "", "", "", "", "", "", "", "")
 csvf.fappn(fd_results, dtstamp, tester, led_mfr_name, led_mfr_prtnum, led_mfr_srnum, led_wavelength_nm, led_fwd_volt, led_fwd_current, led_view_angle, led_material, "", "", "", "", "", "","", "", "", "")
 csvf.fappn(fd_captures, "dt stamp", "tester", "mfct", "mfct prt num" , "serial num", "LED wavelenght (nm)", "LED forward voltage (V)", "LED forward current (V)", "LED angle of view (degrees)", "LED material", "", "", "", "", "", "", "", "", "", "")
 csvf.fappn(fd_captures, dtstamp, tester, led_mfr_name, led_mfr_prtnum, led_mfr_srnum, led_wavelength_nm, led_fwd_volt, led_fwd_current, led_view_angle, led_material, "", "", "", "", "", "","", "", "", "")

 #append files with equipment lists
 csvf.fappn(fd_results, "spectrum analyser", "signal gen", "scope", "psu", "", "", "", "", "", "", "", "", "", "", "","", "", "", "", "")
 csvf.fappn(fd_results, spec_an, sig_gen, osc_scope, psu, psu, "", "", "", "", "", "", "", "", "", "","", "", "", "", "")
 csvf.fappn(fd_captures, "spectrum analyser", "signal gen", "scope", "psu", "", "", "", "", "", "", "", "", "", "", "","", "", "", "", "")
 csvf.fappn(fd_captures, spec_an, sig_gen, osc_scope, psu, "", "", "", "", "", "", "", "", "", "", "","", "", "", "", "")

#-----------------------------------------------------------------------------------------------------------------------#

 #echo information to the screen
 #clear screen and display logo
 #user.scrn_clr()

 #echo user email address to screen
 user.scrn_print("----Tester/User ID----",tester)
 user.scrn_print("---------------------------------------------------------------","")
 
 #echo DUT description to screen
 user.scrn_print("----LED description and DC settings----","")
 user.scrn_print("---------------------------------------------------------------","")
 user.scrn_print("manufaurer name", led_mfr_name)
 user.scrn_print("manufaurer part number", led_mfr_prtnum )
 user.scrn_print("manufaurer serial number", led_mfr_srnum)
 user.scrn_print("wavelength (nm)", led_wavelength_nm)
 user.scrn_print("forward voltage (V)", led_fwd_volt)
 user.scrn_print("forward current (mA)", led_fwd_current)
 user.scrn_print("angle of view (degrees)", led_view_angle)
 user.scrn_print("semiconductor material", led_material)
 user.scrn_print("---------------------------------------------------------------","")
 
 #echo test equipment found to screen
 user.scrn_print("----Test equipment found----","")
 user.scrn_print("---------------------------------------------------------------","")
 user.scrn_print("Spectrum analyser", spec_an)
 user.scrn_print("Signal generator", sig_gen)
 user.scrn_print("Scope", osc_scope)
 user.scrn_print("PSU", psu)
 user.scrn_print("---------------------------------------------------------------","")

 #echo test equipment found to screen
 user.scrn_print("----Test results and screen captures files----","")
 user.scrn_print("---------------------------------------------------------------","")
 user.scrn_print("Results file", fd_results)
 user.scrn_print("Captures file", fd_captures)
 user.scrn_print("---------------------------------------------------------------","")

#-----------------------------------------------------------------------------------------------------------------------#
 #!!!!!!!!!!!!!!!!!!!!!!!!USER DEFINED INPUT BEGIN!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 #test script definition 
 
 #sweep frequency settings (Hertz)
 freq_start = 1000000  
 freq_stop = 2000000
 sample_pts = 10
  
 #calcultaed parameter !!DO NOT CHANGE!! 
 step_size = (freq_stop - freq_start) / (sample_pts - 1)
 
 #sweep lists for voltage and temperature
 psu_list = [9.00,10.00,11.00,12.00,13.00,14.00,15.00,16.00,17.00,18.00,19.00]  #volts DO NOT EXCEED LNB SUPPLY RAILS
 temp_list = [25] #degrees Celcius
  
 #!!!!!!!!!!!!!!!!!!!!!!!!USER DEFINED INPUT END!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  
#-----------------------------------------------------------------------------------------------------------------------# 

 user.scrn_print("Test scripts starting......!", "")
 
 #!!!!!!!!!!!!!!!!!!!!!!!!USER DEFINED INPUT BEGIN!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 
#--------SANDBOX-BEGIN---------------------------#
 
 equip.lev_esg(addr_sig_gen, -10) #dBm
 equip.output_esg(addr_sig_gen, "ON")

 equip.reflev_cxa(addr_spec_an, 10)
 #equip.atten_cxa(addr_spec_an,"AUTO",0) 
 #equip.resbw_cxa(addr_spec_an,"AUTO",0) 
 #equip.vidbw_cxa(addr_spec_an,"AUTO",0) 

 freq_current = freq_start
 while(freq_current < (freq_stop + step_size)):
  equip.freq_esg(addr_sig_gen, freq_current)
  equip.freqcs_cxa(addr_spec_an, int(freq_current), 1000000)
  #equip.mrkrmode_cxa(addr_spec_an,1,"NORMAL")
  #equip.mrkrpksrch_cxa(addr_spec_an,1,"PEAK")
  freq_current = freq_current + step_size

 
#--------SANDBOX-END-----------------------------#

 addr_spec_an.close() 
 addr_sig_gen.close() 
 addr_osc_scope.close()
 #addr_psu.close()

 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------#
#MAIN() FUNCTION CALL END

#-----------------------------------------------------------------------------------------------------------------------#

#call main function
main()

#-----------------------------------------------------------------------------------------------------------------------#