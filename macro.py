#-----------------------------------------------------------------------------------------------------------------------#	
# Function: macro                               		      				                                            #
# Purpose: contains all available test macros                                       	                                #
# Parameters: accepts none, returns none								                                                #
# Author: TJA														                                                    #
# Date: 16/12/2021													                                                    #
# Revision: A														                                                    #
# Status: work in progress											                                                            #
#-----------------------------------------------------------------------------------------------------------------------#
# Measurements Available                                                                                                #
#-----------------------------------------------------------------------------------------------------------------------#
# Frequency Response
# ----Measures the frequency response of an LED using the ESG (source) and CXA (sink)

# Power consumption (VI) (measured on all above tests) (Completed)

# Temperature (measured on all above tests) (Completed)
#-----------------------------------------------------------------------------------------------------------------------#

#imports
import visa
import binascii
import csv
import sys
import imp
import os
import time

#set top level directory path
dirpath = '/home/instrument/Desktop/'

#append source directory
sys.path.append (dirpath+'vlc_rig')

import equip
import csvf
import user
#import levcor

#-----------------------------------------------------------------------------------------------------------------------#	
# Purpose: LED Frequency Response Test                                                  	                            #
# Parameters:                                                                               		                    #
# Author: TJA														                                                    #
# Date: 16/12/2021   												                                                    #
# Revision: A 														                                                    #
# Status: Finished											                                                            #
#-----------------------------------------------------------------------------------------------------------------------#

def cgaint(fd_results, addr_spec_an, addr_sig_gen, addr_psu, spec_an_freq, sig_gen_freq, sig_gen_lev, psu_voltage, temp, hdrenable):
 
 if (hdrenable == 0): # First pass of the phase noise test, place header in results file
  user.scrn_print("Frequency Response Test Running"  ,"")
  csvf.fappn(fd_results, "###", "Frequency Response", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "")	
  csvf.fappn(fd_results, "LNB IF (Hz)", "Signal Generator Freq", "Spec An Measured IF Noise Level (dBm)", "Thermal Noise Reference (dBm/Hz)", "Input Referred RF (Hz)", "Conversion Gain (dB)", "Upconverter LO (Hz)", "LNB LO (Hz)", "Measured Supply Voltage (V)", "Measured Supply Current (A)", "Calculated Power (W)", "Temp deg C", "", "", "", "", "", "", "", "")	 
 
 #setup signal generator
 #output frequency and level
 equip.freq_esg(addr_sig_gen, sig_gen_freq) #Hz
 equip.lev_esg(addr_sig_gen, sig_gen_lev) #dBm
 equip.output_esg(addr_sig_gen, "ON") #Turn signal generator ON

  #setup spectrum analyser
 #ref level and atten
 equip.reflev_cxa(addr_spec_an, 10)  # sets reference level high to prevent signal going outside the graticule
 equip.atten_cxa(addr_spec_an,"AUTO",0)
 #res and vid bw 
 equip.resbw_cxa(addr_spec_an,"AUTO",0) 
 equip.vidbw_cxa(addr_spec_an,"AUTO",0) 
 #set marker mode to NORMAL
 equip.mrkrmode_cxa(addr_spec_an,1,"NORMAL")
 #set spectrum analyser span to 1MHz
 equip.freqcs_cxa(addr_spec_an, int(freqc_fsp), 1000000)

 #peak search 
 equip.mrkrpksrch_cxa(addr_spec_an,1,"PEAK")


 #ref level
 equip.reflev_cxa(addr_spec_an, int(equip.ymrkrval_cxa(addr_spec_an, 1)) + 10) # add 10dB headroom onto the ref lev
 
 time.sleep(1.2)
 
 #place marker at analyser centre freq
 equip.mrkrxoffset_cxa(addr_spec_an,1,(spec_an_freq))
 
 #video averaging ON
 #equip.average_fsp(addr_fsp,"ON",50,"VID")
    
 #video averaging OFF
 #equip.average_fsp(spec_an_freq,,"OFF",50,"VID")
 
 #voltage = equip.vread_pl303(addr_pl303, 1)
 #current = equip.iread_pl303(addr_pl303, 1)
 #power = voltage * current

# Dummy values
 voltage = 1
 current = 0.5
 power = voltage * current

 #setup signal generator
 #output level
 equip.lev_esg(addr_sig_gen, -100) #dBm
 equip.output_esg(addr_sig_gen, "ON") #Turn signal generator ON
                                                                               	                          
 csvf.fappn(fd_results, spec_an_freq, markerx_noise, markery_noise, thermal_noise, upconv_rf, conv_gain, upconv_lo, lnb_lo, voltage, current, power, temp, "", "", "", "", "", "", "","")                                 
 return (0) 