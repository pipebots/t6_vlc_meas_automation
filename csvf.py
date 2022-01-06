#-----------------------------------------------------------------------------------------------------------------------#	
# Function: csv handling							                                                                                	#
# Purpose: writes and reads CSV files	       							                                                              #
# Parameters: accepts and returns refer to the code								                                                     	#
# Author: TJA														                                                                                #
# Date: 03/12/2021													                                                                            #
# Revision: 1.0														                                                                              #
# Status: finished												                                                                             	#
#-----------------------------------------------------------------------------------------------------------------------#

#imports
import csv
import time

#-----------------------------------------------------------------------------------------------------------------------#
def csv_dtstamp():
 localtime = time.localtime(time.time())     
 thour = str(localtime.tm_hour)
 tmin = str(localtime.tm_min) 
 tsec = str(localtime.tm_sec) 
 return(time.strftime("%Y%m%d") + thour + tmin + tsec)
#-----------------------------------------------------------------------------------------------------------------------#  
def csv_file(CSV_PATH,CSV_FILE_NAME, dtstamp, mfr_name, mfr_prtnum, mfr_srnum): 
 return(CSV_PATH + mfr_name + "_" + mfr_prtnum + "_" + mfr_srnum + "_" + dtstamp + "_" + CSV_FILE_NAME)
#-----------------------------------------------------------------------------------------------------------------------#   
def cal_file(CSV_PATH,CSV_FILE_NAME, dtstamp, calname): 
 return(CSV_PATH + calname + "_" + dtstamp + CSV_FILE_NAME)
#-----------------------------------------------------------------------------------------------------------------------#   
# Append existing CSV file     
def fappn(csvfn, prma, prmb, prmc, prmd, prme, prmf, prmg, prmh, prmi, prmj, prmk, prml, pramm, prmn, prmo, prmp, prmq, prmr, prms, prmt):
 with open(csvfn, 'a', newline='') as csvfile:
  filewriter = csv.writer(csvfile, delimiter=',')                    
  filewriter.writerow([prma, prmb, prmc, prmd, prme, prmf, prmg, prmh, prmi, prmj, prmk, prml, pramm, prmn, prmo, prmp, prmq, prmr, prms, prmt])
#-----------------------------------------------------------------------------------------------------------------------#   
# Append tracedata to existing CSV file
def fappn_trace(fd, safstart, safstop, string_in, notes):
  
  # Place "begin trace" in the CSV file
  fappn(fd, notes, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "")
  fappn(fd, "begin trace", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "")	
  
  # Determine how many sweep points are contained in the string
  swp_points = string_in.count(",")+1
  # Determine step size
  step_size = (safstop - safstart) / (swp_points - 1)
  # Determine the total number of characters in the string
  total_length = len(string_in)
  # Determine the total length of one sweep point from the start of the string
  
  # Initialise variables
  freq = 0
  counter = 0
  beg = 0
  end = string_in.find(",",0,total_length)
  
  # Strip the data points from the string  
  while (counter  < swp_points):
   
   # Calculate the current frequency for the sweep point
   freq = safstart + (step_size*counter)
   # Strip amplitude from the string
   amplitude = float(string_in[beg:end])   
   
   # Append the CSV file with the frequency and amplitude 
   fappn(fd, freq, amplitude, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "")	
   
   # Calculate the position of the sweep points in the string
   beg = string_in.find(",",end,total_length) + 1
   if (counter == (swp_points - 2)):
    end = beg + total_length  # This applies for the last sweep point in the string
   else:
    end = string_in.find(",",beg,total_length)    # This applies for all but the last sweep point in the string
   
   # Increment the counter
   counter = counter + 1
   
  # Place "end trace" in the CSV file 
  fappn(fd, "end trace", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "")	
  
  #Empty string_in (effectively empties the allocated memory) 
  string_in = ""
                            
  return(0)
  