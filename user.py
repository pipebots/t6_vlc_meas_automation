#-----------------------------------------------------------------------------------------------------------------------#	
# Function: user							                                                                                        	#
# Purpose: generates user menus and handles user input		                                                              #
# Parameters: accepts and returns refer to the code								                                                     	#
# Author: TJA														                                                                                #
# Date: 25/09/2014													                                                                            #
# Revision: 1.0														                                                                              #
# Status: finished												                                                                             	#
#-----------------------------------------------------------------------------------------------------------------------#
#imports 
import os

def scrn_clr():
 os.system('cls')
 return(0)

def scrn_print(msg,param):
 if param != "":
  param = str(param)
  print(msg + ": " + param)
 else:
  print(msg)
 return(0)