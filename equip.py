#-----------------------------------------------------------------------------------------------------------------------#	
# Function: equip												                                                                               	#
# Purpose: test equipment driver library									                                                              #
# Parameters: accepts and returns refer to the code								                                                     	#
# Author: TJA														                                                                                #
# Date: 16/12/2021													                                                                            #
# Revision: A 														                                                                              #
# Status: development												                                                                          	#
#-----------------------------------------------------------------------------------------------------------------------#

#imports
import pyvisa
import binascii
import csv
import sys
import importlib # available changed from import imp - depricated
import os
import time

#set top level directory path
dirpath = '/home/instrument/Desktop/'
#append source directory
sys.path.append (dirpath+'vlc_rig')

import csvf
import user
#import macro

#-----------------------------------------------------------------------------------------------------------------------#	
# Purpose: Agilent Technologies N9000A CXA Signal Analyser Commands                                                     #
# Author: TJA													                                                                                 	#
# Date: 28/08/2021	(last update): 28/08/2021													                                                 	#          
# Revision: A 													                                                                                #
# Status: development											                                                                          		#
#-----------------------------------------------------------------------------------------------------------------------#
def init_cxa(addr_cxa):
 addr_cxa.clear()
 addr_cxa.term_chars="\n"
 RESET(addr_cxa)
 addr_cxa.write(":DISP:ENAB ON")
 addr_cxa.write(":INIT:CONT ON")
 return(ID(addr_cxa))
#-----------------------------------------------------------------------------------------------------------------------#
def reflev_cxa(addr_cxa, reflev):
 addr_cxa.write(":DISP:WIND:TRAC:Y:RLEV %s" %reflev)
 OPCQ(addr_cxa)
 time.sleep(0.2)
 return(0) 
#-----------------------------------------------------------------------------------------------------------------------#
def atten_cxa(addr_cxa,atten_mode,atten):
 if atten_mode == "AUTO":
  addr_cxa.write(":POW:ATT:AUTO ON")
  OPCQ(addr_cxa)
 elif atten_mode == "MAN":
  addr_cxa.write(":POW:ATT:AUTO OFF")
  OPCQ(addr_cxa)
  addr_cxa.write(":POW:ATT %s" %atten)
  OPCQ(addr_cxa)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def resbw_cxa(addr_cxa,resbw_mode,resbw):
 if resbw_mode == "AUTO":
  addr_cxa.write(":BAND:RES:AUTO ON")
  OPCQ(addr_cxa)
 elif resbw_mode == "MAN":
  addr_cxa.write(":BAND:RES:AUTO OFF")
  OPCQ(addr_cxa)
  addr_cxa.write(":BAND:RES %s" %resbw)
  OPCQ(addr_cxa)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def vidbw_cxa(addr_cxa,vidbw_mode,vidbw):
 if vidbw_mode == "AUTO":
  addr_cxa.write(":BAND:VID:AUTO ON")
  OPCQ(addr_cxa)
 elif vidbw_mode == "MAN":
  addr_cxa.write(":BAND:VID:AUTO OFF")
  OPCQ(addr_cxa)
  addr_cxa.write(":BAND:VID %s" %vidbw)
  OPCQ(addr_cxa)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def mrkrmode_cxa(addr_cxa,mrkr,mode):
 if mode == "NORMAL":
  addr_cxa.write(":CALC:MARK%s:STAT ON" %mrkr)
  OPCQ(addr_cxa)
  addr_cxa.write(":CALC:MARK%s:MODE POS" %mrkr)
  OPCQ(addr_cxa)
 elif mode == "DELTA":
  addr_cxa.write(":CALC:MARK%s:STAT ON" %mrkr)
  OPCQ(addr_cxa)
  addr_cxa.write(":CALC:MARK%s:MODE DELT" %mrkr)
  OPCQ(addr_cxa)
 elif mode == "BAND":
  addr_cxa.write(":CALC:MARK%s:STAT ON" %mrkr)
  OPCQ(addr_cxa)
  addr_cxa.write(":CALC:MARK%s:MODE BAND" %mrkr)
  OPCQ(addr_cxa)
 elif mode == "SPAN":
  addr_cxa.write(":CALC:MARK%s:STAT ON" %mrkr)
  OPCQ(addr_cxa)
  addr_cxa.write(":CALC:MARK%s:MODE SPAN" %mrkr)
  OPCQ(addr_cxa)
 elif mode == "OFF":
  addr_cxa.write(":CALC:MARK%s:STAT OFF" %mrkr)
  OPCQ(addr_cxa)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def freqcs_cxa(addr_cxa, centfreq, spanfreq):
 addr_cxa.write(":FREQ:CENT %s" %centfreq)
 OPCQ(addr_cxa)
 addr_cxa.write(":FREQ:SPAN %s" %spanfreq)
 OPCQ(addr_cxa)
 time.sleep(0.2)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------# 
def mrkrpksrch_cxa(addr_cxa,mrkr,mode):
 if mode == "PEAK":
  addr_cxa.write(":CALC:MARK%s:MAX" %mrkr)
  OPCQ(addr_cxa)
 elif mode == "NEXT":
  addr_cxa.write(":CALC:MARK%s:MAX:NEXT" %mrkr)
  OPCQ(addr_cxa)
 elif mode == "LEFT":
  addr_cxa.write(":CALC:MARK%s:MAX:LEFT" %mrkr)
  OPCQ(addr_cxa)
 elif mode == "RIGHT":
  addr_cxa.write(":CALC:MARK%s:MAX:RIGH" %mrkr)
  OPCQ(addr_cxa)
 elif mode == "MIN":
  addr_cxa.write(":CALC:MARK%s:MIN" %mrkr)
  OPCQ(addr_cxa)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def mrkrxoffset_cxa(addr_cxa,mrkr,offset):
 addr_cxa.write(":CALC:MARK%s:X %s" %(mrkr, offset))
 OPCQ(addr_cxa)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def xmrkrval_cxa(addr_cxa,mrkr):
 addr_cxa.write(":CALC:MARK%s:X?" %mrkr)
 xval = addr_cxa.read()
 #Convert string to float
 xval = str_strip(xval)	
 return(xval)
#-----------------------------------------------------------------------------------------------------------------------#
def ymrkrval_cxa(addr_cxa,mrkr):
 addr_cxa.write(":CALC:MARK%s:Y?" %mrkr)
 yval = addr_cxa.read()
 #Convert string to float
 yval = str_strip(yval)	
 return(yval)
#-----------------------------------------------------------------------------------------------------------------------#
def mrkrcenfreq_cxa(addr_cxa,mrkr):
 addr_cxa.write("CALC:MARK%s:FUNC:CENT" %mrkr)	
 OPCQ(addr_fsp)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def mrkrreflev_(addr_cxa,mrkr):
 addr_cxa.write("CALC:MARK%s:FUNC:REF" %mrkr)	
 OPCQ(addr_cxa)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def average_cxa(addr_cxa,state,count,type):
 if state == "OFF":
  addr_cxa.write(":AVER OFF")
  OPCQ(addr_cxa)
 elif state == "ON":
  addr_cxa.write(":AVER ON")
  OPCQ(addr_cxa)
  addr_fsp.write(":AVER:COUN %s" %count)
  OPCQ(addr_cxa)
  addr_cxa.write(":AVER:TYPE %s" %type)
  OPCQ(addr_cxa)
  addr_cxa.write("SWEep:TIME?")
  sweeptime = addr_cxa.read()
  sweeptime = str_strip(sweeptime)  
  addr_cxa.write("INIT;*WAI")
  delay = (sweeptime * count) + (2*sweeptime)
  time.sleep(delay)
 return(0)


#-----------------------------------------------------------------------------------------------------------------------#	
# Purpose: Agilent Technologies E4438C ESG Vector Signal Generator Commands                                             #
# Author: TJA													                                                                                 	#
# Date: 28/08/2021	(last update): 28/08/2021												                                                   	#          
# Revision: A 													                                                                                #
# Status: development											                                                                          		#
#-----------------------------------------------------------------------------------------------------------------------#
def init_esg(addr_esg):
 addr_esg.clear()
 addr_esg.term_chars="\n"
 RESET(addr_esg)
 return(ID(addr_esg))
#-----------------------------------------------------------------------------------------------------------------------#
def output_esg(addr_esg, state):
 if state == "ON":
  addr_esg.write("OUTP:STAT ON")
  OPCQ(addr_esg)
 elif state == "OFF":
  addr_esg.write("OUTP:STAT OFF")
  OPCQ(addr_esg)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def freq_esg(addr_esg, freq):
 addr_esg.write("FREQ %s Hz" %freq)
 OPCQ(addr_esg)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def lev_esg(addr_esg, level):
 addr_esg.write("POW %s dBm" %level)
 OPCQ(addr_esg)
 return(0)




#-----------------------------------------------------------------------------------------------------------------------#	
# Purpose: Agilent Technologies DSO6014A DSO Scope Commands                                                             #
# Author: TJA													                                                                                 	#
# Date: 28/08/2021	(last update): 28/08/2021											                                                     	#          
# Revision: A 													                                                                                #
# Status: development											                                                                          		#
#-----------------------------------------------------------------------------------------------------------------------#
def init_dso(addr_dso):
 addr_dso.clear()
 addr_dso.term_chars="\n"
 RESET(addr_dso)
 return(ID(addr_dso))
                     






#--------LEGACY DRIVERS BELOW THIS LINE---------------------------------------------------------------------------------#

#-----------------------------------------------------------------------------------------------------------------------#	
# Purpose: String stripping function used to remove characters returned by Prologix GPIB to IP adapter 	                #
# Author: TJA													                                                                                 	#
# Date: 28/08/2021												                                                                             	#          
# Revision: A 													                                                                                #
# Status: development											                                                                          		#
#-----------------------------------------------------------------------------------------------------------------------#
def str_strip(string_in):  
 string_in=str(string_in)
 if string_in.startswith("b") == True: # Indicates Prologix GPIB to IP interface in use
  string_in = string_in.lstrip("b")
  string_in = string_in.strip("'")
  num_out = float(string_in) 
 elif string_in.startswith("V") == True: # Indicated TTi PL303-P Volts looks like: "V1 18.00"
  num_out = float(string_in[3:])
 elif string_in.endswith("A") == True: # Indicated TTi PL303-P Amps looks like: "0.915A"
  num_out = float(string_in[:-2])
 else:
  num_out = float(string_in)
 return(num_out)
#-----------------------------------------------------------------------------------------------------------------------#
def strin_strout(string_in):  
 string_in=str(string_in)
 if string_in.startswith("b") == True: # Indicates Prologix GPIB to IP interface in use
  string_in = string_in.lstrip("b")
  string_in = string_in.strip("'")
  string_out = string_in 
 else:
  string_out = string_in
 return(string_out)                             
#-----------------------------------------------------------------------------------------------------------------------#	
# Purpose: Standard commands									                                                         	                #
# Author: TJA													                                                                                 	#
# Date: 28/08/2021												                                                                             	#          
# Revision: A 													                                                                                #
# Status: development											                                                                          		#
#-----------------------------------------------------------------------------------------------------------------------#
def OPCQ(addr):
 #addr.term_chars="\n"
 time.sleep(0.1)
 timestore = time.time()
 #10 second time out
 timeout = timestore + 10
 response = 0
 while True:
  addr.write("*OPC?")
  timecurrent = time.time()
  response = float(addr.read())
  if response != 0 or timecurrent > timeout:
    timediff = timecurrent - timestore
    if response != 0: 
     #print("Exiting...Response:%s received from *OPC?" %response)
     #print("Time taken %s" %timediff)
     break 
    elif timecurrent > timeout:
     #print("Exiting...Timeout %s" %timediff)
     break 
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def RESET(addr):
 time.sleep(0.25)
 addr.write("*RST")
 CLS(addr)
 OPCQ(addr)
 return(0) 
#-----------------------------------------------------------------------------------------------------------------------#
def ID(addr):
 addr.write("*IDN?")
 response = strin_strout(addr.read())
 return(response)  
#-----------------------------------------------------------------------------------------------------------------------#
def CLS(addr):
 addr.write("*CLS")
 time.sleep(1)
 return(0) 
#-----------------------------------------------------------------------------------------------------------------------#
def DCL(addr):
 addr.write("DCL")
 return(0) 
#-----------------------------------------------------------------------------------------------------------------------#
def STBQ(addr):
  addr.write("*STB?")
  response = addr.read()
  return(response) 
 
#-----------------------------------------------------------------------------------------------------------------------#	
# Purpose: R&S FSP spectrum analyser commands									                                                         	#
# Author: TJA													                                                                                 	#
# Date: 21/08/2021												                                                                             	#
# Revision: A 													                                                                                #
# Status: development											                                                                          		#
#-----------------------------------------------------------------------------------------------------------------------#
def init_fsp(addr_fsp):
 #addr_fsp.clear()
 addr_fsp.term_chars="\n"
 RESET(addr_fsp)
 addr_fsp.write("SYSTem:DISPlay:UPDate ON")
 return(ID(addr_fsp))
#-----------------------------------------------------------------------------------------------------------------------#
def freqss_fsp(addr_fsp, starfreq, stopfreq):
 addr_fsp.write(":FREQ:STAR %s" %starfreq)
 OPCQ(addr_fsp)
 addr_fsp.write(":FREQ:STOP %s" %stopfreq)
 OPCQ(addr_fsp)
 time.sleep(0.2)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def freqssrd_fsp(addr_fsp):
 addr_fsp.write(":FREQ:STAR?")
 time.sleep(0.2)
 freqstart = str_strip(addr_fsp.read())
 addr_fsp.write(":FREQ:STOP?")
 freqstop = str_strip(addr_fsp.read())
 time.sleep(0.2)
 return(freqstart,freqstop)
#-----------------------------------------------------------------------------------------------------------------------#
def freqcs_fsp(addr_fsp, centfreq, spanfreq):
 addr_fsp.write(":FREQ:CENT %s" %centfreq)
 OPCQ(addr_fsp)
 addr_fsp.write(":FREQ:SPAN %s" %spanfreq)
 OPCQ(addr_fsp)
 time.sleep(0.2)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def freqspan_fsp(addr_fsp, spanfreq):
 addr_fsp.write(":FREQ:SPAN %s" %spanfreq)
 OPCQ(addr_fsp)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def reflev_fsp(addr_fsp, reflev):
 addr_fsp.write(":DISP:WIND:TRAC:Y:RLEV %s" %reflev)
 OPCQ(addr_fsp)
 time.sleep(0.2)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------# 
def reflevrd_fsp(addr_fsp):
 addr_fsp.write(":DISP:WIND:TRAC:Y:RLEV?")
 response = str_strip(addr_fsp.read())
 return(response) 
#-----------------------------------------------------------------------------------------------------------------------#
def atten_fsp(addr_fsp,atten_mode,atten):
 if atten_mode == "AUTO":
  addr_fsp.write(":POW:ATT:AUTO ON")
  OPCQ(addr_fsp)
 elif atten_mode == "MAN":
  addr_fsp.write(":POW:ATT:AUTO OFF")
  OPCQ(addr_fsp)
  addr_fsp.write(":POW:ATT %s" %atten)
  OPCQ(addr_fsp)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def preamp_fsp(addr_fsp,preamp_mode):
 if preamp_mode == "OFF":
  addr_fsp.write(":POW:GAIN OFF")
  OPCQ(addr_fsp)
 elif preamp_mode == "ON":
  addr_fsp.write(":POW:GAIN ON")
  OPCQ(addr_fsp)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def resbw_fsp(addr_fsp,resbw_mode,resbw):
 if resbw_mode == "AUTO":
  addr_fsp.write(":BAND:RES:AUTO ON")
  OPCQ(addr_fsp)
 elif resbw_mode == "MAN":
  addr_fsp.write(":BAND:RES:AUTO OFF")
  OPCQ(addr_fsp)
  addr_fsp.write(":BAND:RES %s" %resbw)
  OPCQ(addr_fsp)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def vidbw_fsp(addr_fsp,vidbw_mode,vidbw):
 if vidbw_mode == "AUTO":
  addr_fsp.write(":BAND:VID:AUTO ON")
  OPCQ(addr_fsp)
 elif vidbw_mode == "MAN":
  addr_fsp.write(":BAND:VID:AUTO OFF")
  OPCQ(addr_fsp)
  addr_fsp.write(":BAND:VID %s" %vidbw)
  OPCQ(addr_fsp)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def swpmode_fsp(addr_fsp,swp_mode):
 if swp_mode == "CONT":
  addr_fsp.write(":INIT:CONT ON")
  OPCQ(addr_fsp)
 elif swp_mode == "SINGLE":
  addr_fsp.write(":INIT:CONT OFF")
  OPCQ(addr_fsp)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def average_fsp(addr_fsp,state,count,type):
 if state == "OFF":
  addr_fsp.write(":AVER OFF")
  OPCQ(addr_fsp)
 elif state == "ON":
  addr_fsp.write(":AVER ON")
  OPCQ(addr_fsp)
  addr_fsp.write(":AVER:COUN %s" %count)
  OPCQ(addr_fsp)
  addr_fsp.write(":AVER:TYPE %s" %type)
  OPCQ(addr_fsp)
  addr_fsp.write("SWEep:TIME?")
  sweeptime = addr_fsp.read()
  sweeptime = str_strip(sweeptime)  
  addr_fsp.write("INIT;*WAI")
  delay = (sweeptime * count) + (2*sweeptime)
  time.sleep(delay)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def mrkrmode_fsp(addr_fsp,mrkr,mode):
 if mode == "NORMAL":
  addr_fsp.write(":CALC:MARK%s:STAT ON" %mrkr)
  OPCQ(addr_fsp)
  addr_fsp.write(":CALC:MARK%s:MODE POS" %mrkr)
  OPCQ(addr_fsp)
 elif mode == "DELTA":
  addr_fsp.write(":CALC:MARK%s:STAT ON" %mrkr)
  OPCQ(addr_fsp)
  addr_fsp.write(":CALC:MARK%s:MODE DELT" %mrkr)
  OPCQ(addr_fsp)
 elif mode == "BAND":
  addr_fsp.write(":CALC:MARK%s:STAT ON" %mrkr)
  OPCQ(addr_fsp)
  addr_fsp.write(":CALC:MARK%s:MODE BAND" %mrkr)
  OPCQ(addr_fsp)
 elif mode == "SPAN":
  addr_fsp.write(":CALC:MARK%s:STAT ON" %mrkr)
  OPCQ(addr_fsp)
  addr_fsp.write(":CALC:MARK%s:MODE SPAN" %mrkr)
  OPCQ(addr_fsp)
 elif mode == "OFF":
  addr_fsp.write(":CALC:MARK%s:STAT OFF" %mrkr)
  OPCQ(addr_fsp)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def mrknoise_fsp(addr_fsp,mrkr,state):
 addr_fsp.write(":CALC:MARK%s:FUNC:NOIS:STAT %s" %(mrkr,state))
 OPCQ(addr_fsp)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------# 
def mrknoiserd_fsp(addr_fsp,mrkr):
 addr_fsp.write(":CALC:MARK%s:FUNC:NOIS:RES?" %mrkr)
 xnoiseval = addr_fsp.read()
 #Convert string to float
 xnoiseval = str_strip(xnoiseval)
 return(xnoiseval) 
#-----------------------------------------------------------------------------------------------------------------------#
def mrkrpksrch_fsp(addr_fsp,mrkr,mode):
 if mode == "PEAK":
  addr_fsp.write(":CALC:MARK%s:MAX" %mrkr)
  OPCQ(addr_fsp)
 elif mode == "NEXT":
  addr_fsp.write(":CALC:MARK%s:MAX:NEXT" %mrkr)
  OPCQ(addr_fsp)
 elif mode == "LEFT":
  addr_fsp.write(":CALC:MARK%s:MAX:LEFT" %mrkr)
  OPCQ(addr_fsp)
 elif mode == "RIGHT":
  addr_fsp.write(":CALC:MARK%s:MAX:RIGH" %mrkr)
  OPCQ(addr_fsp)
 elif mode == "MIN":
  addr_fsp.write(":CALC:MARK%s:MIN" %mrkr)
  OPCQ(addr_fsp)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def mrkrxoffset_fsp(addr_fsp,mrkr,offset):
 addr_fsp.write(":CALC:MARK%s:X %s" %(mrkr, offset))
 OPCQ(addr_fsp)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def xmrkrval_fsp(addr_fsp,mrkr):
 addr_fsp.write(":CALC:MARK%s:X?" %mrkr)
 xval = addr_fsp.read()
 #Convert string to float
 xval = str_strip(xval)	
 return(xval)
#-----------------------------------------------------------------------------------------------------------------------#
def ymrkrval_fsp(addr_fsp,mrkr):
 addr_fsp.write(":CALC:MARK%s:Y?" %mrkr)
 yval = addr_fsp.read()
 #Convert string to float
 yval = str_strip(yval)	
 return(yval)
#-----------------------------------------------------------------------------------------------------------------------#
def mrkrcenfreq_fsp(addr_fsp,mrkr):
 addr_fsp.write("CALC:MARK%s:FUNC:CENT" %mrkr)	
 OPCQ(addr_fsp)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def mrkrreflev_fsp(addr_fsp,mrkr):
 addr_fsp.write("CALC:MARK%s:FUNC:REF" %mrkr)	
 OPCQ(addr_fsp)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def maxhold_fsp(addr_fsp, state):
  if state == "ON":
   addr_fsp.write(":DISP:WIND:TRAC1:MODE WRIT")
   OPCQ(addr_fsp)
   addr_fsp.write(":DISP:WIND:TRAC1:MODE MAXH")
   OPCQ(addr_fsp)
  if state == "OFF":
   addr_fsp.write(":DISP:WIND:TRAC1:MODE WRIT")
   OPCQ(addr_fsp)  
  return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def view_fsp(addr_fsp, state):
  if state == "ON":
   addr_fsp.write(":DISP:WIND:TRAC1:MODE WRIT")
   OPCQ(addr_fsp)
   addr_fsp.write(":DISP:WIND:TRAC1:MODE VIEW")
   OPCQ(addr_fsp)
  if state == "OFF":
   addr_fsp.write(":DISP:WIND:TRAC1:MODE WRIT")
   OPCQ(addr_fsp)  
  return(0)  
#-----------------------------------------------------------------------------------------------------------------------#
def readtrace_fsp(addr_fsp, trace, fd, notes):
 (safstart,safstop)=freqssrd_fsp(addr_fsp)
 addr_fsp.write(":FORM ASC")
 addr_fsp.write(":TRAC? TRACE%s" %trace)
 datastore = "" 
 flag = 0
 istr_len = 1
 str_len = 1
 while (str_len >= istr_len):
  time.sleep(0.1)
  tracedata = addr_fsp.read()
  tracedata = tracedata.decode("utf-8")
  datastore = datastore + tracedata
  
  if flag == 0:
   istr_len = len(tracedata) 
   str_len = istr_len
  if flag != 0: 
   str_len = len(tracedata)

  flag = flag + 1 
  
 csvf.fappn_trace(fd, safstart, safstop, datastore, notes)
 
 #Empty string_in (effectively empties the allocated memory) 
 tracedata = ""
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
#UNTESTED
def cfgchanpwr_fsp(addr_fsp,state,bw,avgstate,count):
 if state == "ON":
  addr_fsp.write("INIT:CHP")
  OPCQ(addr_fsp)
  addr_fsp.write("CHP:BAND:INT %s" %bw)
  OPCQ(addr_fsp)
  addr_fsp.write("CHP:AVER:STAT %s" %avgstate)
  OPCQ(addr_fsp)
  addr_fsp.write("CHP:AVER:COUN %s" %count)
  OPCQ(addr_fsp)
  addr_fsp.write("CHP:AVER:TCON REP")
  OPCQ(addr_fsp)
 elif state == "OFF":
  addr_fsp.write("CONF:SAN")
  OPCQ(addr_fsp)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
#UNTESTED
def chanpwr_fsp(addr_fsp,wait):
 addr_fsp.write("INIT:CHP")
 time.sleep(wait)
 addr_fsp.write("FETC:CHP?")
 chanpwr = addr_fsp.read()
 #Convert string to float
 chanpwr = str_strip(chanpwr)	
 return(chanpwr)
#-----------------------------------------------------------------------------------------------------------------------#	
# Purpose: Agilent E4433 commands									                                                                  		#
# Author: TJA														                                                                                #
# Date: 15/08/2021												                                                                            	#
# Revision: A 													                                                                              	#
# Status: development												                                                                          	#
#-----------------------------------------------------------------------------------------------------------------------#
def init_4433(addr_4433):
 #addr_4433.clear()
 addr_4433.term_chars="\n"
 RESET(addr_4433)
 addr_4433.write("OUTP:STAT OFF")
 OPCQ(addr_4433)
 addr_4433.write("POW:OFFS 0 dB")
 OPCQ(addr_4433)
 addr_4433.write("FREQ 100000000 Hz")
 OPCQ(addr_4433)
 addr_4433.write("POW -143 dBm")
 OPCQ(addr_4433)
 addr_4433.write("FM1:STAT OFF")
 OPCQ(addr_4433)
 addr_4433.write("FM1:SOUR INT")
 OPCQ(addr_4433)
 addr_4433.write("FM1 0 Hz")
 OPCQ(addr_4433)
 addr_4433.write("FM1:INT:FREQ 1000 Hz")
 OPCQ(addr_4433)
 addr_4433.write("FM2:STAT OFF")
 OPCQ(addr_4433)
 addr_4433.write("FM2:SOUR INT")
 OPCQ(addr_4433)
 addr_4433.write("FM2 0 Hz")
 OPCQ(addr_4433)
 addr_4433.write("FM2:INT:FREQ 1000 Hz")
 OPCQ(addr_4433)
 return(ID(addr_4433))
#-----------------------------------------------------------------------------------------------------------------------#
def output_4433(addr_4433, state):
 if state == "ON":
  addr_4433.write("OUTP:STAT ON")
  OPCQ(addr_4433)
 elif state == "OFF":
  addr_4433.write("OUTP:STAT OFF")
  OPCQ(addr_4433)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def offset_4433(addr_4433, offset):
 addr_4433.write("POW:OFFS %s dB" %offset)
 OPCQ(addr_4433)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def set_4433(addr_4433, freq, level):
 addr_4433.write("FREQ %s Hz" %freq)
 OPCQ(addr_4433)
 addr_4433.write("POW %s dBm" %level)
 OPCQ(addr_4433)
 addr_4433.write("OUTP:STAT ON")
 OPCQ(addr_4433)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def freq_4433(addr_4433, freq):
 addr_4433.write("FREQ %s Hz" %freq)
 OPCQ(addr_4433)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def lev_4433(addr_4433, level):
 addr_4433.write("POW %s dBm" %level)
 OPCQ(addr_4433)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def fm_4433(addr_4433, state, source, tonefreq, dev):
 if state == "ON":
  addr_4433.write("FM%s:STAT ON" %source)
  OPCQ(addr_4433)
  addr_4433.write("FM%s:SOUR INT" %source)
  OPCQ(addr_4433)
  addr_4433.write("FM%s %s Hz" %(source,dev))
  OPCQ(addr_4433)
  addr_4433.write("FM%s:INT:FREQ %s Hz" %(source,tonefreq))
  OPCQ(addr_4433)
 elif state == "OFF":
  addr_4433.write("FM%s:STAT OFF" %source)
  OPCQ(addr_4433)
 return(0)      
#-----------------------------------------------------------------------------------------------------------------------#
def am_4433(addr_4433, state, modfreq, modlev):
 if state == "ON":
  addr_4433.write("AM:STAT ON")
  OPCQ(addr_4433)
  addr_4433.write("AM:SOUR INT")
  OPCQ(addr_4433)
  addr_4433.write("AM:DEPT %s PCT" %modlev)
  OPCQ(addr_4433)
  addr_4433.write("AM:INT:FREQ %s Hz" %modfreq)
  OPCQ(addr_4433)
 elif state == "OFF":
  addr_4433.write("AM:STAT OFF")
  OPCQ(addr_4433)
 return(0)

#-----------------------------------------------------------------------------------------------------------------------#	
# Purpose: marconi 2024 commands										                                                                  	#
# Author: TJA														                                                                                #
# Date: 15/08/2021													                                                                            #
# Revision: A 													                                                                              	#
# Status: development													                                                                          #
#-----------------------------------------------------------------------------------------------------------------------#
def init_2024(addr_2024):
 #addr_2024.clear()
 addr_2024.term_chars="\n"
 RESET(addr_2024)
 addr_2024.write(":OUTPUT:DISABLE")
 OPCQ(addr_2024)
 addr_2024.write(":CFRQ:VALUE 100000000HZ;INC 1KHZ")
 OPCQ(addr_2024)
 addr_2024.write(":RFLV:UNITS DBM;TYPE PD;VALUE -140;INC 0.5;OFF")
 OPCQ(addr_2024)
 addr_2024.write(":RFLV:OFFS:VALUE 0;DISABLE")
 OPCQ(addr_2024)
 addr_2024.write(":MODE AM,FM")
 OPCQ(addr_2024)
 addr_2024.write(":MOD:OFF")
 OPCQ(addr_2024)
 addr_2024.write(":FM1:DEVN 0KHZ;INC 1KHZ;INT;OFF")
 OPCQ(addr_2024)
 addr_2024.write(":FM1:MODF:VALUE 1.0HZ;SIN")
 OPCQ(addr_2024)
 addr_2024.write(":FM2:DEVN 0KHZ;INC 1KHZ;INT;OFF")
 OPCQ(addr_2024)
 addr_2024.write(":FM2:MODF:VALUE 1.0HZ;SIN")
 OPCQ(addr_2024)
 return(ID(addr_2024))
#-----------------------------------------------------------------------------------------------------------------------#
def output_2024(addr_2024, state):
 if state == "ON":
  addr_2024.write(":OUTPUT:ENABLE")
  OPCQ(addr_2024)
 elif state == "OFF":
  addr_2024.write(":OUTPUT:DISABLE")
  OPCQ(addr_2024)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def set_2024(addr_2024, freq, level):
 addr_2024.write(":CFRQ:VALUE %sHZ;INC 1KHZ" %freq)
 OPCQ(addr_2024)
 addr_2024.write(":RFLV:UNITS DBM;TYPE PD;VALUE %s;INC 0.5;ON" %level)
 OPCQ(addr_2024)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def freq_2024(addr_2024, freq):
 addr_2024.write(":CFRQ:VALUE %sHZ;INC 1KHZ" %freq)
 OPCQ(addr_2024)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def lev_2024(addr_2024, level):
 addr_2024.write(":RFLV:UNITS DBM;TYPE PD;VALUE %s;INC 0.5;ON" %level)
 OPCQ(addr_2024)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def fm_2024(addr_2024, state, source, tonefreq, dev):
 if state == "ON":
  addr_2024.write(":MODE FM")
  OPCQ(addr_2024)
  addr_2024.write(":MOD:ON")
  OPCQ(addr_2024)
  addr_2024.write(":FM%s:DEVN %sHZ;INC 1KHZ;INT;ON" %(source,dev))  
  OPCQ(addr_2024)
  addr_2024.write(":FM%s:MODF:VALUE %sHZ;SIN" %(source,tonefreq))
  OPCQ(addr_2024)
 elif state == "OFF":
  addr_2024.write(":MODE AM,FM")
  OPCQ(addr_2024)
  addr_2024.write(":MOD:OFF")
  OPCQ(addr_2024)
  addr_2024.write(":FM%s:DEVN 0KHZ;INC 1KHZ;INT;OFF" %source)  
  OPCQ(addr_2024)
  addr_2024.write(":FM%s:MODF:VALUE 1.0HZ;SIN" %source)
  OPCQ(addr_2024)
 return(0)      
#-----------------------------------------------------------------------------------------------------------------------#
def am_2024(addr_2024, state, source, modfreq, mdepth):
 if state == "ON":
  addr_2024.write(":MODE AM")
  OPCQ(addr_2024)
  addr_2024.write(":MOD:ON")
  OPCQ(addr_2024)
  addr_2024.write(":AM%s:DEPTH %sPCT;INT;ON" %(source,mdepth))  
  OPCQ(addr_2024)
  addr_2024.write(":AM%s:MODF:VALUE %sKHZ;SIN" %(source,modfreq))
  OPCQ(addr_2024)
 if state == "OFF":
  addr_2024.write(":MODE AM,FM")
  OPCQ(addr_2024)
  addr_2024.write(":MOD:OFF")
  OPCQ(addr_2024)
  addr_2024.write(":AM%s:DEPTH 25PCT;INT;OFF" %source)  
  OPCQ(addr_2024)
  addr_2024.write(":AM%s:MODF:VALUE 1KHZ;SIN" %source) 
  OPCQ(addr_2024)
 return(0)

#-----------------------------------------------------------------------------------------------------------------------#	
# Purpose: model 8x5-M signal generator commands									                                                      #
# Author: TJA														                                                                                #
# Date: 19/08/2021													                                                                            #
# Revision: A 														                                                                              #
# Status: development												                                                                           	#
#-----------------------------------------------------------------------------------------------------------------------#
def init_8x5m(addr_8x5m):
 addr_8x5m.clear()
 addr_8x5m.term_chars="\n"  
 RESET(addr_8x5m)
 return(ID(addr_8x5m))
#-----------------------------------------------------------------------------------------------------------------------#
def output_8x5m(addr_8x5m, state):
 if state == "ON":
  addr_8x5m.write("OUTP:STAT ON")
  OPCQ(addr_8x5m)
 elif state == "OFF":
  addr_8x5m.write("OUTP:STAT OFF")
  OPCQ(addr_8x5m)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def set_8x5m(addr_8x5m, freq, level):
 addr_8x5m.write("SOUR:FREQ:CW %s Hz" %freq)
 OPCQ(addr_8x5m)
 addr_8x5m.write("SOUR:POW:ATT:AUTO ON")
 OPCQ(addr_8x5m)
 addr_8x5m.write("SOUR:POW:LEV %s dBm" %level)
 OPCQ(addr_8x5m)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def freq_8x5m(addr_8x5m, freq):
 addr_8x5m.write("SOUR:FREQ:CW %s Hz" %freq)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def lev_8x5m(addr_8x5m, level):
 addr_8x5m.write("SOUR:POW:ATT:AUTO ON")
 OPCQ(addr_8x5m)
 addr_8x5m.write("SOUR:POW:LEV %s dBm" %level)
 OPCQ(addr_8x5m)
 return(0)

#-----------------------------------------------------------------------------------------------------------------------#	
# Purpose: R&S SFC-U Compact Modulator commands			        						                                                #
# Author: TJA														                                                                                #
# Date: 17/09/2021													                                                                            #
# Revision: A 														                                                                              #
# Status: development												                                                                           	#
#-----------------------------------------------------------------------------------------------------------------------#
def init_sfc(addr_sfc):
 addr_sfc.open()
 addr_sfc.clear()
 addr_sfc.term_chars="\n"  
 RESET(addr_sfc)            
 return(ID(addr_sfc))
#-----------------------------------------------------------------------------------------------------------------------#
def freq_sfc(addr_sfc, freq):
 addr_sfc.write("SOUR:FREQ:ACTual:CENTer %s HZ" %freq)
 OPCQ(addr_sfc)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------# 
def lev_sfc(addr_sfc, lev):
 addr_sfc.write("SOURce:POWer %s dBm" %lev)
 OPCQ(addr_sfc)
 return(0) 
#-----------------------------------------------------------------------------------------------------------------------# 
def set_sfc(addr_sfc, freq, lev):
 addr_sfc.write("SOUR:FREQ:ACTual:CENTer %s HZ" %freq)
 addr_sfc.write("SOURce:POWer %s dBm" %lev)
 OPCQ(addr_sfc)
 return(0) 
#-----------------------------------------------------------------------------------------------------------------------# 
def out_sfc(addr_sfc, state):
 addr_sfc.write("OUTPut:STATe %s" %state)
 OPCQ(addr_sfc)
 return(0)  
#-----------------------------------------------------------------------------------------------------------------------#
def mod_sfc(addr_sfc, state):
 # Modulation ON or OFF. Modulation OFF provides a CW output
 addr_sfc.write("SOURce:MODulator:STATe %s" %state)
 OPCQ(addr_sfc)
 addr_sfc.write("SOURce:MODulator:STAT?")
 response = addr_sfc.read()
 return(response) 
#-----------------------------------------------------------------------------------------------------------------------#
def specpol_sfc(addr_sfc, pol):
 # Set IQ polarity NORM = Normal, INV = Inverted
 addr_sfc.write("SOUR:DM:POL %s" %pol)
 OPCQ(addr_sfc)
 addr_sfc.write("SOUR:DM:POL?")
 response = addr_sfc.read()
 return(response)
#-----------------------------------------------------------------------------------------------------------------------#
'''
Modulation Settings

TRANsmission commands available/not available in this driver
DVBC............Available
DVBS............Available
DVBT............Available
VSB.............Available
J83B............Available
ISDBt...........Available
DTMB............Available
DVS2............Available
DIRectv.........Available
TDMB............Available
MEDiaflo.... ...Available
CMMB............Available
T2DVb...........Available
ATSM............Available
'''
def trans_sfc(addr_sfc, trans):
 if trans == "DVBS":
  addr_sfc.write("SOURce:DM:TRANsmission DVBS")
 if trans == "DVBS2":
  addr_sfc.write("SOURce:DM:TRANsmission DVS2")
 if trans == "DIRECTV":
  addr_sfc.write("SOURce:DM:TRANsmission DIRectv")
 if trans == "DVBC": 
  addr_sfc.write("SOURce:DM:TRANsmission DVBC")
 if trans == "DVBC2": 
  addr_sfc.write("SOURce:DM:TRANsmission C2DVb") 
 if trans == "DVBT": 
  addr_sfc.write("SOURce:DM:TRANsmission DVBT") 
 if trans == "DVBT2": 
  addr_sfc.write("SOURce:DM:TRANsmission T2DVb") 
 if trans == "J83B": 
  addr_sfc.write("SOURce:DM:TRANsmission J83B")   
 if trans == "VSB": 
  addr_sfc.write("SOURce:DM:TRANsmission VSB") 
 if trans == "ISDBT": 
  addr_sfc.write("SOURce:DM:TRANsmission ISDBt") 
 if trans == "DTMB": 
  addr_sfc.write("SOURce:DM:TRANsmission DTMB")   
 if trans == "TDMB": 
  addr_sfc.write("SOURce:DM:TRANsmission TDMB")      
 if trans == "MEDIAFLO": 
  addr_sfc.write("SOURce:DM:TRANsmission MEDiaflo")
 if trans == "CMMB": 
  addr_sfc.write("SOURce:DM:TRANsmission CMMB") 
 if trans == "ATSM": 
  addr_sfc.write("SOURce:DM:TRANsmission ATSM") 
 OPCQ(addr_sfc)
 addr_sfc.write("SOURce:DM:TRANsmission:STAN?") 
 response = addr_sfc.read()
 return(response)
 
#-----------------------------------------------------------------------------------------------------------------------#
def dvbs_sfc(addr_sfc, constel, input, payload, sequence, coderate, rolloff, source, stuffing, symbolrate, testsignal, tspackets, reedsolomon, special):

 #example: dvbs_sfc(addr_sfc, "QPSK", "ASI1", "PRBS", "P23_1", "R2_3", 0.25, "TESTsignal", "OFF", "27.5000e6", "TTSP", "H184", "ON", "OFF")
 
 # SFC-U Modulation Screen
 # Transmission DVBS 
 print("Transmission: %s" %trans_sfc(addr_sfc, "DVBS"))
 #Spectrum NORMAL
 print("Spectrum: %s" %specpol_sfc(addr_sfc, "NORM"))
 #Turn Modulation ON
 print("Modulation: %s" %mod_sfc(addr_sfc, "ON"))
 
 # SFC-U Input Signal Screen
 # Source EXTernal(default),TSPLayer,TESTsignal
 addr_sfc.write("SOURce:IQCoder:DVBS:SOUR %s" %source)
 print("Input source: %s" %source)
 # ASI Input ASI1 or ASI2
 addr_sfc.write("SOURce:IQCoder:DVBS:INPut %s", input)
 print("ASI Input: %s" %input)  
 # Stuffing ON/OFF
 addr_sfc.write("SOURce:IQCoder:DVBS:STUF %s" %stuffing)
 print("stuffing: %s" %stuffing)
 # Test signal TS packet = TTSP, PRBS before conv. = PBEC
 addr_sfc.write("SOURce:IQCoder:DVBS:SOUR %s" %testsignal)
 print("Test signal: %s" %testsignal)
 
 # SFC-U Coding Screen
 # Symbol Rate range 0.100000e6 S/s to 45.000000e6 S/s   default 27.5000e6 S/s
 # Example SOURce:IQCoder:DVBS:SYMBols:RATE 22.5000e6  
 addr_sfc.write("SOURce:IQCoder:DVBS:SYMBols:RATE %s" %symbolrate)
 print("Symbol rate %s" %symbolrate)
 # Constellation QPSK = S4, 8PSK = S8, 16QAM = S16
 if constel == "QPSK":
  addr_sfc.write("SOURce:IQCoder:DVBS:CONS S4")
 if constel == "8PSK":
  addr_sfc.write("SOURce:IQCoder:DVBS:CONS S8") 
 if constel == "16QAM":
  addr_sfc.write("SOURce:IQCoder:DVBS:CONS S16")  
 print("Constellation: %s" %constel)  
 # Roll off 0.2, 0.25, 0.35
 addr_sfc.write("SOURce:IQCoder:DVBS:ROLL %s" %rolloff)
 print("Roll off: %s" %rolloff)
 # Code Rate 1/2 = R1_2, 2/3 = R2_3, 3/4 = R3_4, 5/6 = R5_6, 7/8 = R7_8, 8/9 = R8_9
 addr_sfc.write("SOURce:IQCoder:D VBS:RATE %s" %coderate)
 print("Code rate: %s" %coderate)
 
 # SFC-U Special Screen 
 # Special Settings ON/OFF 
 addr_sfc.write("SOURce:IQCoder:DVBS:SPECial:SETT:STAT %s" %special)
 print("Special settings: %s" %special)
 # Reed Solomon ON/OFF 
 addr_sfc.write("SOURce:IQCoder:DVBS:SPECial:REED %s" %reedsolomon)
 print("Reed Solomon: %s" %reedsolomon)
 
 # SFC-U Settings Screen 
 # TS Packets Head / 184 payload = H184, Sync / 187 payload = S187 
 addr_sfc.write("SOURce:IQCoder:DVBS:TSP %s" %tspackets)
 print("Test TS packet: %s" %tspackets)
 # Payload PRBS = PRBS, Hex 00 = H00, Hex FF = HFF 
 addr_sfc.write("SOURce:IQCoder:DVBS:PAYL %s" %payload)
 print("Payload Test: %s" %payload) 
 # PRBS 2^23 - 1 (ITU-T O.151) = P23_1, 2^15 - 1 (ITU-T O.151) = P15_1
 addr_sfc.write("SOURce:IQCoder:DVBS:PRBS:SEQ %s" %sequence)
 print("PRBS sequence: %s" %sequence)  

 OPCQ(addr_sfc)
 return(0)

#-----------------------------------------------------------------------------------------------------------------------# 
#DVB-S2 Settings
def dvbs2_sfc(addr_sfc, constel, input, fecframe, payload, pilots, sequence, coderate, rolloff, source, stuffing, symbolrate, testsignal, tspackets):

#example: dvbs2_sfc(addr_sfc, "QPSK", "ASI1", "NORM", "PRBS", "ON", "P23_1", "R2_3", 0.25, "TESTsignal", "OFF", "27.5000e6", "TTSP", "H184")

 # SFC-U Modulation Screen
 # Transmission DVBS 
 print("Transmission: %s" %trans_sfc(addr_sfc, "DVBS2"))
 #Spectrum NORMAL
 print("Spectrum: %s" %specpol_sfc(addr_sfc, "NORM"))
 #Turn Modulation ON
 print("Modulation: %s" %mod_sfc(addr_sfc, "ON"))

 # SFC-U Input Signal Screen
 # Source EXTernal(default),TSPLayer,TESTsignal
 addr_sfc.write("SOURce:IQCoder:DVBS2:SOUR %s" %source)
 print("Input source: %s" %source)
 # ASI Input ASI1 or ASI2
 addr_sfc.write("SOURce:IQCoder:DVBS2:INPut %s", input)
 print("ASI Input: %s" %input)  
 # Stuffing ON/OFF
 addr_sfc.write("SOURce:IQCoder:DVBS2:STUF %s" %stuffing)
 print("stuffing: %s" %stuffing)
 # Test signal TS packet = TTSP, PRBS before conv. = PBEC
 addr_sfc.write("SOURce:IQCoder:DVBS2:SOUR %s" %testsignal)
 print("Test signal: %s" %testsignal)

 # SFC-U Coding Screen
 # Symbol Rate range 0.100000e6 S/s to 45.000000e6 S/s   default 20.0000e6 S/s
 # Example SOURce:IQCoder:DVBS2:SYMBols:RATE 22.5000e6  
 addr_sfc.write("SOURce:IQCoder:DVBS2:SYMBols:RATE %s" %symbolrate)
 print("Symbol rate %s" %symbolrate)
 # Constellation QPSK = S4, 8PSK = S8, 16APSK = A16, 32APSK = A32
 if constel == "QPSK":
  addr_sfc.write("SOURce:IQCoder:DVBS2:CONStel S4")
 if constel == "8PSK":
  addr_sfc.write("SOURce:IQCoder:DVBS2:CONStel S8") 
 if constel == "16APSK":
  addr_sfc.write("SOURce:IQCoder:DVBS2:CONStel A16") 
 if constel == "32APSK":
  addr_sfc.write("SOURce:IQCoder:DVBS2:CONStel A32")   
 print("Constellation: %s" %constel)  
 # FEC Frame Normal = NORM, Short = SHOR
 addr_sfc.write("SOURce:IQCoder:DVBS2:FECFrame %s" %fecframe)
 print("FECFrame: %s" %fecframe)
 # Pilots ON/OFF 
 addr_sfc.write("SOURce:IQCoder:DVBS2:PILots %s" %pilots) 
 print("Pilots: %s" %pilots)
 # Roll off 0.15, 0.2, 0.25, 0.35
 addr_sfc.write("SOURce:IQCoder:DVBS2:ROLLoff %s" %rolloff)
 print("Roll off: %s" %rolloff)
 # Code Rate 1/4 = R1_4, 1/3 = R1_3, 2/5 = R2_5, 1/2 = R1_2,3/5 = R3_5, 2/3 = R2_3, 
 # 3/4 = R3_4, 4/5 = R4_5, 5/6 = R5_6, 6/7 = R6_7, 7/8 = R7_8, 8/9 = R8_9, 9/10 = R9_10
 addr_sfc.write("SOURce:IQCoder:DVBS2:RATE %s" %coderate)
 print("Code rate: %s" %coderate)

 # SFC-U Settings Screen 
 # TS Packets Head / 184 payload = H184, Sync / 187 payload = S187 
 addr_sfc.write("SOURce:IQCoder:DVBS:TSP %s" %tspackets)
 print("Test TS packet: %s" %tspackets)
 # Payload PRBS = PRBS, Hex 00 = H00, Hex FF = HFF 
 addr_sfc.write("SOURce:IQCoder:DVBS2:PAYL %s" %payload)
 print("Payload Test: %s" %payload) 
 # PRBS 2^23 - 1 (ITU-T O.151) = P23_1, 2^15 - 1 (ITU-T O.151) = P15_1
 addr_sfc.write("SOURce:IQCoder:DVBS:PRBS:SEQ %s" %sequence)
 print("PRBS sequence: %s" %sequence) 

 #Turn Modulation ON
 mod_sfc(addr_sfc, "ON")

 OPCQ(addr_sfc)
 return(0)

#-----------------------------------------------------------------------------------------------------------------------#
def cnadd_sfc(addr_sfc, state, cn):
 addr_sfc.write("SOURce:NOISe:MODE AWGN")
 addr_sfc.write("SOURce:NOISe:COUPling %s" %state)
 
 if state == "ON":
  addr_sfc.write("SOURce:NOISe:STATe ADD")
  addr_sfc.write("SOURce:NOISe:AWGN ON")
 elif state == "OFF":
  addr_sfc.write("SOURce:NOISe:STATe OFF")
  addr_sfc.write("SOURce:NOISe:AWGN OFF")
  
 addr_sfc.write("SOURce:NOISe:CN %s" %cn)
 OPCQ(addr_sfc) 
 return(0) 
 
#-----------------------------------------------------------------------------------------------------------------------#	
# Purpose: TTi TG5011A Arb generator commands			        						                                                  #
# Author: TJA														                                                                                #
# Date: 21/08/2021													                                                                            #
# Revision: A 														                                                                              #
# Status: development												                                                                           	#
#-----------------------------------------------------------------------------------------------------------------------#
def init_tg5011a(addr_tg5011a):
 addr_tg5011a.clear()
 addr_tg5011a.term_chars="\r\n"
 RESET(addr_tg5011a)
 return(ID(addr_tg5011a))
#-----------------------------------------------------------------------------------------------------------------------#
def configarb_tg5011a(addr_tg5011a, arbnumber):
  #print(addr_tg5011a.ask("ARB1DEF?"))
  addr_tg5011a.write("ARBLOAD ARB%s" %arbnumber)
  OPCQ(addr_tg5011a)
  #Set frequency (For a command with four bytes this is 1/(9bits*4words*1.5ms)=18.51851851851852 Hz )
  addr_tg5011a.write("FREQ 18.518518518")
  OPCQ(addr_tg5011a)
  #Select Burst
  #Set Burst type to multiple (1)
  addr_tg5011a.write("BSTCOUNT 1")
  OPCQ(addr_tg5011a)
  addr_tg5011a.write("BSTPHASE 0")
  OPCQ(addr_tg5011a)
  addr_tg5011a.write("BST NCYC")
  OPCQ(addr_tg5011a)
  #Select Trigger
  #Set trigger to manual
  addr_tg5011a.write("TRGSRC MAN")
  OPCQ(addr_tg5011a)
  #Turn generator output on
  addr_tg5011a.write("OUTPUT ON")
  OPCQ(addr_tg5011a)
  return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def readwav_tg5011a(addr_tg5011a, filename, arbnumber):
  addr_tg5011a.write("ARB%s?" %arbnumber)
  OPCQ(addr_tg5011a)
  #fetch first two characters 
  addr_tg5011a.term_chars=None
  headervalue = addr_tg5011a.visalib.read(addr_tg5011a.session, 2)
  #check first is # (hex 23)
  #if it is, second character defines the number of bytes to follow. Fetch this number.
  numberofbytes = addr_tg5011a.visalib.read(addr_tg5011a.session, int(chr((headervalue[1]))))
  f = open(filename, 'wb')
  f.write(addr_tg5011a.read(int(numberofbytes))) 
  addr_tg5011a.term_chars="\r\n"
#-----------------------------------------------------------------------------------------------------------------------#
def trigger_tg5011a(addr_tg5011a):
  addr_tg5011a.write("*TRG")
  addr_tg5011a.write("*CLS")
  return(0) 
#-----------------------------------------------------------------------------------------------------------------------#
def writewav_tg5011a(addr_tg5011a, filename, arbnumber):
 addr_tg5011a.write("ARBDEF ARB%s,PORT%s,ON" %(arbnumber,arbnumber))
 OPCQ(addr_tg5011a)
 #load data from file
 #f = open('C:\data\Perl\PCB_Sim\waveform.wfm', 'rb')
 f = open(filename, 'rb')
 wavedata=f.read()
 #strip existing header
 #add new header (#...)
 #calculate how many bytes in wavedata
 lengthofwave=len(wavedata)
 # for i in (str(lengthofwave)):
 # headerdata.append(ord(i))
 # "#"+str(len(str(lengthofwave)))+str(lengthofwave)
 # convert header data to ascii numbers
 # headerdata_ascii=""
 # for i,c in enumerate(headerdata):
 # headerdata_ascii=headerdata_ascii + str(ord(headerdata[i]))
 # headerdata_ascii=bytearray(headerdata)
 headerdata="#"
 headerdata+=str(len(str(lengthofwave)))
 headerdata+=str(lengthofwave)
 #write to generator
 addr_tg5011a.term_chars=""
 addr_tg5011a.send_end=False
 
 count = addr_tg5011a.visalib.write(addr_tg5011a.session, "ARB%s " %arbnumber)
 
 count = addr_tg5011a.visalib.write(addr_tg5011a.session, headerdata)
 
 addr_tg5011a.values_format = 5
 
 #############################################
 #  Write binary to device using visa32.dll  #
 #############################################
 #bufferToWrite = "*IDN?" #*IDN? typically tells devices to return identification
 #bytesToWrite = len(bufferToWrite) + 1
 bytesWritten = c_int(0) 
 #Function Prototype: ViStatus viWrite(ViSession vi, ViBuf buf, ViUInt32 count, ViPUInt32 retCount)
 
 if constants.NOEQUIP:
  returnValue = 0
 else:
  returnValue = dll.viWrite(addr_tg5011a.session, wavedata, len(wavedata), byref(bytesWritten))
 
 
 if returnValue != 0:
  print ("Could not write binary data to device. Error: ", returnValue)
  return(returnValue)
  print ("Bytes Written: ", bytesWritten)
  print ("ReturnValue: ", returnValue, "\n")
  #############################################
 addr_tg5011a.values_format = 0
 print(addr_tg5011a.visalib.write(addr_tg5011a.session,"\n"))
 addr_tg5011a.term_chars="\r\n"
 time.sleep(2)
 
#-----------------------------------------------------------------------------------------------------------------------#	
# Purpose: TTi PL303-P PSU commands			        						                                                            #
# Author: TJA														                                                                                #
# Date: 21/08/2021													                                                                            #
# Revision: A 														                                                                              #
# Status: development												                                                                           	#
#-----------------------------------------------------------------------------------------------------------------------#
def init_pl303(addr_pl303):
 addr_pl303.clear()
 addr_pl303.term_chars="\r\n"
 RESET(addr_pl303)      
 vset_pl303(addr_pl303, 1, 0)    
 OPCQ(addr_pl303)     
 iset_pl303(addr_pl303, 1, 0)
 OPCQ(addr_pl303)
 allout_pl303(addr_pl303, "OFF")
 OPCQ(addr_pl303)
 return(ID(addr_pl303))
#-----------------------------------------------------------------------------------------------------------------------#
def allout_pl303(addr_pl303, state):
 if state == "ON":
  addr_pl303.write("OPALL 1")
  OPCQ(addr_pl303)
 elif state == "OFF":
  addr_pl303.write("OPALL 0") 
  OPCQ(addr_pl303)
 return(0)
#-----------------------------------------------------------------------------------------------------------------------#
def out_pl303(addr_pl303, state, source):
 if state == "ON":
  addr_pl303.write("OP%s 1" %source)
  OPCQ(addr_pl303)
 elif state == "OFF":
  addr_pl303.write("OP%s 0" %source) 
  OPCQ(addr_pl303)
 return(0) 
#-----------------------------------------------------------------------------------------------------------------------# 
def vset_pl303(addr_pl303, source, voltage):          
 addr_pl303.write("V%s %s" %(source, voltage))
 OPCQ(addr_pl303)
 return(0) 
#-----------------------------------------------------------------------------------------------------------------------#  
def iset_pl303(addr_pl303, source, current):          
 addr_pl303.write("I%s %s" %(source, current))
 OPCQ(addr_pl303)
 return(0)  
#-----------------------------------------------------------------------------------------------------------------------#  
def iread_pl303(addr_pl303, source):          
 ireadback = addr_pl303.ask("I%sO?" %source)
 #Convert string to float
 ireadback = str_strip(ireadback)	
 return(ireadback)
#-----------------------------------------------------------------------------------------------------------------------# 
def vread_pl303(addr_pl303, source):          
 vreadback = addr_pl303.ask("V%s?" %source)
 #Convert string to float
 vreadback = str_strip(vreadback)
 return(vreadback)