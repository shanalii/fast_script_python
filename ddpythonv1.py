#!/bin/python
#A script to do de-dispersion on a single file, involving making a link to said file and running rfifind, DDplan.py, prepdata, and realfft on it.
#don't forget to do this on n04 -X!

#command line arguments are in the format: ddscript.bash DIRECTORY FILENAME
#boolean to check whether or not everything is in the right format and if the DIRECTORY and FILENAME are valid

#testing: python ddpythonv1.py /psrdata/pmb/PM0026 PM0026_00511.sf

import sys, timeit, os.path, re, subprocess

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
print("Data will be processed into the folder " + foldername + ". \n")

#create link to the file to process within the local folder
os.chdir(foldername)
os.symlink(PATHNAME, FILENAME)
print("Link to file " + FILENAME + " made. \n************************************************************* \n")

##############################################

#run rfifind
print("Running rfifind to detect and mask RFI: \n")
start = timeit.default_timer()
print("Filename: " + FILENAME + "\nTime: 2 \n")

#spawn a shell process to run rfifind
os.system("rfifind " + FILENAME + " -time 2 -o " + foldername + " >> /dev/null")

end = timeit.default_timer()
print("Time for rfifind: " + str(end - start) + " seconds.")

##############################################

print("Running DDplan.py to compose de-dispersion plan:")
start = timeit.default_timer()

#constant values
#low dm
ldm = "0"
#high dm
hdm = "4000"
#time resolution
tres = "0.5"


#make txt version of binary file header
fname = foldername + ".txt"
os.system("readfile " + FILENAME + " > " + fname)
f = open(fname, "r")

#obtain values from file
for line in f:
	#central frequency
	if re.search("Central freq", line):
		cfreq = line.split()[4]
	#number of channels
	if re.search("Number of channels", line):
		numchan = line.split()[4]
	#bandwidth
	if re.search("Total Bandwidth", line):
		bandw = line.split()[4]
	#sample time
	if re.search("Sample time", line):
		sampletime = str(float(line.split()[4]) / 1000000)

#run DDplan.py
print("DM: 0 to 4000 \nTime resolution: 0.5 seconds \nCentral Frequency: " + cfreq + " MHz \nNumber of Channels: " + numchan + "\nTotal Bandwidth: " + bandw + " MHz \nSample Time: " + sampletime + " seconds") + "\n"
os.system("DDplan.py -l " +  ldm + " -d " + hdm + " -f " + cfreq + " -b " + bandw + " -n " + numchan + " -t " + sampletime + " -r " + tres + " -o " + foldername + " | tee " + foldername + "_ddplaninfo.txt >> /dev/null")
print("Results saved in " + foldername + "_ddplaninfo.txt. \n")

end = timeit.default_timer()
print("Time for DDplan: " + str(end - start) + " seconds.")

##############################################

print("Running realfft for Forier transform:")
start = timeit.default_timer()

os.system("ls *.dat | xargs -n 1 --replace realfft {} >> /dev/null")

end = timeit.default_timer()
print("Time for realfft: " + str(end - start) + " seconds.")

##############################################

print("Running accelsearch to search for periodic candidates: \nUsing zmax = 0.")
start = timeit.default_timer()

os.system("ls *.fft | xargs -n 1 accelsearch -zmax 0 >> /dev/null")

end = timeit.default_timer()
print("Time for accelsearch: " + str(end - start) + " seconds.")

##############################################

print("Running ACCEL_sift.py to sift through periodic candidates:")
start = timeit.default_timer()

os.system("python $PRESTO/python/ACCEL_sift.py > cands.txt")
print("Results saved in cands.txt.")

end = timeit.default_timer()
print("Time for ACCEL_sift: " + str(end - start) + " seconds.")

##############################################
'''
#folding goes here.


#display png files
print("Folding finished, plots have been saved as the following .png files:")
for file in os.listdir(os.getcwd()):
    if file.endswith(".png"):
        print(file)
'''
##############################################

ENDTIME = timeit.default_timer()
TOTALTIME = (ENDTIME - STARTTIME)
print("Total time elapsed for processing " + "" + " : " + str(TOTALTIME) + " seconds.")

exit(0)
