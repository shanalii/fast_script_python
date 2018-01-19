#!/bin/python
#A script to do de-dispersion on a single file, involving making a link to said file and running rfifind, DDplan.py, prepdata, and realfft on it.
#don't forget to do this on n04 -X!

#command line arguments are in the format: ddscript.bash DIRECTORY FILENAME
#boolean to check whether or not everything is in the right format and if the DIRECTORY and FILENAME are valid

#testing: python ddpythonv1.py /psrdata/pmb/PM0026 PM0026_00511.sf

import sys
import timeit
import os.path

##############################################

STARTTIME = timeit.default_timer()

print("*************************************************************")
print("PRESTO data processing - now in Python \n")
print("by Shana Li \n")
print("Arguments should be in the format: DIRECTORY FILENAME.")
print("Filename SHOULD INCLUDE file extension (.sf).")
print("************************************************************* \n")

DIRECTORY = sys.argv[1]
FILENAME = sys.argv[2]
PATHNAME = DIRECTORY + "/" + FILENAME

#check validity of the path to file
if not os.path.exists(PATHNAME):
	print("Invalid DIRECTORY and/or FILENAME. Please check input and try again. \n ************************************************************* \n")
	exit(0)

#create new folder for data processing; if the file has already been processed here, create new folder with indexed name
#folder name starts out with the FILENAME without the extension (assumed to be .sf)
foldername = FILENAME[:-3]
x = 1
while os.path.exists("./" + foldername):
 	if x == 1:
		foldername = foldername + "_" + str(x)
	else:
		foldername = foldername[:-(len(str(x-1))+1)] + "_" + str(x)
	x += 1
os.makedirs(foldername)

#create link to the file to process within the local folder
os.chdir(foldername)
os.symlink(PATHNAME, FILENAME)


##############################################

ENDTIME = timeit.default_timer()
TOTALTIME = (ENDTIME - STARTTIME)
print("Total time elapsed for processing " + "" + " : " + str(TOTALTIME) + " seconds.")

exit(0)
