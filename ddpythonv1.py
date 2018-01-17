#!/bin/python
#A script to do de-dispersion on a single file, involving making a link to said file and running rfifind, DDplan.py, prepdata, and realfft on it.
#don't forget to do this on n04 -X!

#command line arguments are in the format: ddscript.bash directory filename
#boolean to check whether or not everything is in the right format and if the directory and filename are valid

import timeit

##############################################

STARTTIME = timeit.default_timer()

print("*************************************************************")
print("PRESTO data processing - now in Python")
print("by Shana Li \n")
print("************************************************************* \n")

print("From which directory do you want to process a file?")
directory=raw_input()
#check validity of directory

print("Which file do you want to open in " + directory + "?")
filename=raw_input()
#check validity of filename



##############################################

ENDTIME = timeit.default_timer()
TOTALTIME = (ENDTIME - STARTTIME)
print("Total time elapsed for processing " + "" + " : " + str(TOTALTIME) + " seconds.")

exit(0)
