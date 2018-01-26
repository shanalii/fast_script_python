#!/bin/python
#A script to do de-dispersion on a single file, involving making a link to said file and running rfifind, DDplan.py, prepdata, and realfft on it.
#don't forget to do this on n04 -X!

#command line arguments are in the format: ddscript.bash DIRECTORY FILENAME
#boolean to check whether or not everything is in the right format and if the DIRECTORY and FILENAME are valid

#testing: python ddpythonv1.py /psrdata/pmb/PM0026 PM0026_00511.sf

import sys, timeit, os.path, re, subprocess, linecache

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

print("************************************************************* \n")
#run rfifind
print("Running rfifind to detect and mask RFI: \n")
start = timeit.default_timer()
print("Filename: " + FILENAME + "\nTime: 2 \n")

#spawn a shell process to run rfifind
os.system("rfifind " + FILENAME + " -time 2 -o " + foldername + " >> /dev/null")

end = timeit.default_timer()
print("Time for rfifind: " + str(end - start) + " seconds.")
print("************************************************************* \n")

##############################################

print("************************************************************* \n")
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
	#numout
	if re.search("Spectra per file", line):
		numout = line.split()[4]
	#nsub
	if re.search("samples per spectra", line):
		nsub = line.split()[4]

#run DDplan.py
print("DM: 0 to 4000 \nTime resolution: 0.5 seconds \nCentral Frequency: " + cfreq + " MHz \nNumber of Channels: " + numchan + "\nTotal Bandwidth: " + bandw + " MHz \nSample Time: " + sampletime + " seconds") + "\n"
os.system("DDplan.py -l " +  ldm + " -d " + hdm + " -f " + cfreq + " -b " + bandw + " -n " + numchan + " -t " + sampletime + " -r " + tres + " -o " + foldername + " | tee " + foldername + "_ddplaninfo.txt >> /dev/null")
print("Results saved in " + foldername + "_ddplaninfo.txt. \n")

end = timeit.default_timer()
print("Time for DDplan: " + str(end - start) + " seconds.")
print("************************************************************* \n")

##############################################

print("************************************************************* \n")
print("Running subband de-dispersion using prepsubband:")
start = timeit.default_timer()

#call prepsubband on each call in DDplan, starting from line 14
i = 14
line = linecache.getline(foldername + "_ddplaninfo.txt", i)
while line != "\n":
	#put arguments into array
	args = line.split()
	#run prepsubband
	print("Low DM: " + args[0] + "\nDM step: " + args[2] + "\nNumber of DMs: " + args[4] + "\nNumout: " + str(float(numout)/float(args[3])) + "\nDownsample: " + args[3] +"\n")
	os.system("prepsubband -lodm " + args[0] + " -dmstep " + args[2] + " -numdms " + args[4] + " -numout " + str(int(numout)/int(args[3])) + " -downsamp " + args[3] + " -mask " + foldername + "_rfifind.mask -o " + foldername + " " + FILENAME + " >> /dev/null")
	i += 1
	line = linecache.getline(foldername + "_ddplaninfo.txt", i)

end = timeit.default_timer()
print("Time for de-dispersion: " + str(end - start) + " seconds.")
print("************************************************************* \n")

##############################################

print("************************************************************* \n")
print("Running realfft for Fourier transform:")
start = timeit.default_timer()

os.system("ls *.dat | xargs -n 1 --replace realfft {} >> /dev/null")

end = timeit.default_timer()
print("Time for realfft: " + str(end - start) + " seconds.")
print("************************************************************* \n")

##############################################

print("************************************************************* \n")
print("Running accelsearch to search for periodic candidates: \nUsing zmax = 0.")
start = timeit.default_timer()

os.system("ls *.fft | xargs -n 1 accelsearch -zmax 0 >> /dev/null")

end = timeit.default_timer()
print("Time for accelsearch: " + str(end - start) + " seconds.")
print("************************************************************* \n")

##############################################

print("************************************************************* \n")
print("Running ACCEL_sift.py to sift through periodic candidates:")
start = timeit.default_timer()

os.system("python $PRESTO/python/ACCEL_sift.py > cands.txt")
print("Results saved in cands.txt.")

end = timeit.default_timer()
print("Time for ACCEL_sift: " + str(end - start) + " seconds.")
print("************************************************************* \n")

##############################################

print("************************************************************* \n")
#fold best candidates using prepfold: referenced from Maura McLaughlin's siftandfold.bash:
print("Running prepfold to fold best candidates and generate plots:")
start = timeit.default_timer()

#make 2D list of best candidates and their attributes: ACCEL_0 filename (0), dat file name (1), candidate number (2), DM (3)
#period = str(float(words[7])/1000) (if ever needed)
cands = open("cands.txt", "r")
candlist = []
for line in cands:
	if re.search("ACCEL", line):
		words = line.split()
		accelstring = words[0].split(":")
		c = [accelstring[0], accelstring[0][:-8], accelstring[1], words[1]]
		candlist.append(c)

#loop prepfold through all viable candidates in candlist
for c in candlist:
	print("Running prepfold on candidate #" + str(candlist.index(c) + 1) + " of " + str(len(candlist)) + ":")
	#run prepfold command
	print("File: " + c[1] + "\nCandidate number: " + c[2] + "\nDM: " + c[3] + "\nnsub: " + nsub + "\n")
	os.system("prepfold -mask " + foldername + "_rfifind.mask -dm " + c[3] + " " + FILENAME + " -accelfile " + c[0] + ".cand -accelcand " + c[2] + " -noxwin -nosearch -o " + foldername + "_" + c[3] + " >> /dev/null")

#display png files
print("Folding finished, plots have been saved as the following .png files:")
for file in os.listdir(os.getcwd()):
    if file.endswith(".png"):
        print(file)

end = timeit.default_timer()
print("Time for folding candidates: " + str(end - start) + " seconds.")
print("************************************************************* \n")

##############################################

ENDTIME = timeit.default_timer()
TOTALTIME = (ENDTIME - STARTTIME)
print("Total time elapsed for processing : " + str(TOTALTIME) + " seconds.")

exit(0)
