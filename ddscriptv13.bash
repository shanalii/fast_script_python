#!/bin/bash
#A script to do de-dispersion on a single file, involving making a link to said file and running rfifind, DDplan.py, prepdata, and realfft on it.
#don't forget to do this on n04 -X!

#command line arguments are in the format: ddscript.bash directory filename
#boolean to check whether or not everything is in the right format and if the directory and filename are valid

STARTTIME="$(date -u +%s)"

echo "*************************************************************"
echo "PRESTO data processing"
echo -e "by Shana Li\n"
echo "Arguments should be in the format: directory filename."
echo "Filename should be sans file extension (.sf)."
echo "*************************************************************"

#set variables for directory and filename
directory=$1
filename=$2

echo -e "\n*************************************************************"
echo "Directory: $directory"
echo "Filename: $filename"

#if directory is invalid, exit
if [ ! -d $directory ]; then
	echo "Invalid directory."
	echo -e "*************************************************************\n"
	exit 0
fi

#if file doesn't exist, exit
if [ ! -e "$directory/$filename.sf" ]; then
	echo "Invalid filename."
	echo -e "*************************************************************\n"
	exit 0
fi

#if folder for this particular file already exists, delete it
if [ -d $filename ]; then
	echo -e "\nExisting files found, overwriting them now."
	rm -r $filename
	echo -e "Done.\n"
fi

#create new folder for data files
mkdir $filename
cd $filename

#create link to file in current directory in the folder
echo "Making link to file:"
ln -s $directory/$filename.sf ./ >> /dev/null
echo "Done."
echo -e "*************************************************************\n"


echo "*************************************************************"
#run rfifind
echo "Running rfifind:"
START="$(date -u +%s)"
echo -e "Start time: $START\n"
echo "Filename: $filename.sf"
echo -e "Time: 2 \n"

rfifind $filename.sf -time 2 -o $filename >> /dev/null

echo "Done."
END="$(date -u +%s)"
echo "End time: $END"
echo "Time for rfifind: $(($END - $START)) seconds."
echo -e "*************************************************************\n"


echo "*************************************************************"
echo "Running DDplan.py:"
START="$(date -u +%s)"
echo -e "Start time: $START\n"
#run DDplan.py:
#get variables needed:
#low dm
ldm=0
#high dm
hdm=4000
#time resolution
tres=0.5
#central frequency
cfreq=`readfile $filename.sf | grep "Central freq" | awk '{print $5}'`
#number of channels
numchan=`readfile $filename.sf | grep "Number of channels" | awk '{print $5}'`
#Parkes multibeam bandwidth
bandw=`readfile $filename.sf | grep "Total Bandwidth" | awk '{print $5}'`
#sample time
sampletime=`readfile $filename.sf | grep "Sample time" | awk '{print $5}'`
sampletime=0.000$sampletime

#run DDplan.py
echo "Central Frequency: $cfreq"
echo "Number of Channels: $numchan"
echo "Total Bandwidth: $bandw"
echo -e "Sample Time: $sampletime \n"

DDplan.py -l $ldm -d $hdm -f $cfreq -b $bandw -n $numchan -t $sampletime -r $tres -o $filename | tee ${filename}_ddplaninfo.txt >> /dev/null
echo "Done."
END="$(date -u +%s)"
echo "End time: $END"
echo "Time for DDplan: $(($END - $START)) seconds."
echo -e "*************************************************************\n"


echo "*************************************************************"
#subband de-dispersion: call prepsubband on each call in DDplan
#count the lines that contain the information for each call
echo "Running subband de-dispersion:"
START="$(date -u +%s)"
echo -e "Start time: $START\n"
numout=`readfile $filename.sf | grep "Spectra per file" | awk '{print $5}'`
lastline=14
line=`head -$lastline ${filename}_ddplaninfo.txt | tail -1`
while [ "$line" != "" ]; do
	((lastline++))
	line=`head -$lastline ${filename}_ddplaninfo.txt | tail -1`
done
echo -e "Looping prepsubband for $(( $lastline-14 )) calls.\n"

#loop prepsubband for all calls in ddplaninfo
for (( i=14; i<lastline; i++ ))
do
	#get the call from the current line in the file
	call=`head -$i ${filename}_ddplaninfo.txt | tail -1`

	#put call into an array
	IFS=' ' read -a arr <<<"$call"

	#get all the variables:
	#nsub
	nsub=`readfile $filename.sf | grep "samples per spectra" | awk '{print $5}'`

	#low dm
	ldm=${arr[0]}

	#dm step
	dms=${arr[2]}
	
	#number of dms
	ndm=${arr[4]}

	#downsamp
	ds=${arr[3]}

	#numout (numout from DDplan / downsamp)
	numo=$(( $numout/$ds ))
	
	#run prepsubband command
	echo "nsub: $nsub; Low DM: $ldm; DM step: $dms; Number of DMs: $ndm; Numout: $numo; Downsample: $ds"
	prepsubband -lodm $ldm -dmstep $dms -numdms $ndm -numout $numo -downsamp $ds -mask ${filename}_rfifind.mask -o $filename $filename.sf >> /dev/null
	echo -e "Done.\n"
done
END="$(date -u +%s)"
echo "End time: $END"
echo "Time for prepsubband: $(($END - $START)) seconds."
echo -e "*************************************************************\n"


#run realfft:
echo "*************************************************************"
echo "Running realfft:"
START="$(date -u +%s)"
echo -e "Start time: $START\n"
ls *.dat | xargs -n 1 --replace realfft {} >> /dev/null
echo "Done."
END="$(date -u +%s)"
echo "End time: $END"
echo "Time for realfft: $(($END - $START)) seconds."
echo -e "*************************************************************\n"

#accelsearch for periodic signals
echo "Running accelsearch:"
START="$(date -u +%s)"
echo -e "Start time: $START\n"
ls *.fft | xargs -n 1 accelsearch -zmax 0 >> /dev/null
echo "Done."
END="$(date -u +%s)"
echo "End time: $END"
echo "Time for accelsearch: $(($END - $START)) seconds."
echo -e "*************************************************************\n"


#sift through periodic candidates
echo "*************************************************************"
echo -e "Running ACCEL_sift.py:"
START="$(date -u +%s)"
echo -e "Start time: $START\n"
python "$PRESTO/python/ACCEL_sift.py" | tee cands.txt >> /dev/null
echo "Done. Candidate info saved in cands.txt."
END="$(date -u +%s)"
echo "End time: $END"
echo "Time for ACCEL_sift: $(($END - $START)) seconds."
echo -e "*************************************************************\n"


#fold best candidates: (referenced from Maura's siftandfold.bash)
echo "*************************************************************"
echo "Folding candidates:"
START="$(date -u +%s)"
echo -e "Start time: $START\n"
#make list of candidate names
candlist=`grep "ACCEL" cands.txt | awk '{print $1}'`
#make into array
candarr=($candlist)

#make list of respective DMs of best candidates from cands.txt
dmslist=`grep "ACCEL" cands.txt | awk '{print $2}'`
#make into array
dmsarr=($dmslist)

#make list of respective periods of best candidates
periodslist=`grep "ACCEL" cands.txt | awk '{print $8/1000.}'`
#make into array
periodsarr=($periodslist)

#get total number of best candidates to loop through them
tot=`grep "ACCEL" cands.txt | wc | awk '{print $1}'`

nsub=`readfile $filename.sf | grep "samples per spectra" | awk '{print $5}'`

#loop prepfold through all viable candidates
for (( i=0; i<tot; i++ ))
do
	echo "Running prepfold on candidate # $(( $i+1 )) out of $tot:"
	
	#get filename of ACCEL_0 cands file and candnum
	line=${candarr[$i]}
	accelfilename="$(cut -d':' -f1 <<< $line)"
	candnum="${line: -1}"

	#get dat filename
	length=$(( ${#accelfilename}-8 ))
	datfilename="${accelfilename: 0:$length}"

	#run prepfold command
	echo -e "File: $datfilename; Candidate number: $candnum; DM: ${dmsarr[$i]}; nsub: $nsub \n"
	
	#fold raw data
	prepfold -mask ${filename}_rfifind.mask -dm ${dmsarr[$i]} $filename.sf -accelfile $accelfilename.cand -accelcand $candnum -noxwin -nosearch -o ${filename}_${dmsarr[$i]} >> /dev/null

done

echo -e "\nDone. Plots have been saved as .png files:"
ls *.png
END="$(date -u +%s)"
echo "End time: $END"
echo "Time for folding candidates: $(($END - $START)) seconds."
echo -e "*************************************************************\n"
#open all the plots
#eog *.png

ENDTIME="$(date -u +%s)"
echo -e "Total time elapsed for processing $filename: $(($ENDTIME - $STARTTIME)) seconds.\n"

#bash ../ddscriptv13.bash /psrdata/pmb/PM0026 PM0026_00511 & bash ../ddscriptv13.bash /psrdata/pmb/PM0058 PM0058_036D1 & bash ../ddscriptv13.bash /psrdata/pmb/PM0109 PM0109_00331 & bash ../ddscriptv13.bash /psrdata/pmb/PM0001 PM0001_00161 & bash ../ddscriptv13.bash /psrdata/pmb/PM0038 PM0038_01821 & bash ../ddscriptv13.bash /psrdata/pmb/PM0042 PM0042_00391 & bash ../ddscriptv13.bash /psrdata/pmb/PM0137 PM0137_041B1 & bash ../ddscriptv13.bash /psrdata/pmb/PM0125 PM0125_077C1 & bash ../ddscriptv13.bash /psrdata/pmb/PM0039 PM0039_00551 & bash ../ddscriptv13.bash /psrdata/pmb/PM0056 PM0056_020B1 & bash ../ddscriptv13.bash /psrdata/pmb/PM0035 PM0035_02931 & bash ../ddscriptv13.bash /psrdata/pmb/PM0085 PM0085_02541 & bash ../ddscriptv13.bash /psrdata/pmb/PM0054 PM0054_015A1 & bash ../ddscriptv13.bash /psrdata/pmb/PM0102 PM0102_00591 & bash ../ddscriptv13.bash /psrdata/pmb/PM0002 PM0002_0089a1 & bash ../ddscriptv13.bash /psrdata/pmb/PM0141 PM0141_0097b1 & bash ../ddscriptv13.bash /psrdata/pmb/PM0137 PM0137_039B1 & bash ../ddscriptv13.bash /psrdata/pmb/PM0149 PM0149_01081 & bash ../ddscriptv13.bash /psrdata/pmb/PM0011 PM0011_0323c1 & bash ../ddscriptv13.bash /psrdata/pmb/PM0148 PM0148_01971 & bash ../ddscriptv13.bash /psrdata/pmb/PM0132 PM0132_06271 & bash ../ddscriptv13.bash /psrdata/pmb/PM0140 PM0140_00641 & bash ../ddscriptv13.bash /psrdata/pmb/PM0060 PM0060_0206d1 & bash ../ddscriptv13.bash /psrdata/pmb/PM0143 PM0143_0051

exit 0
