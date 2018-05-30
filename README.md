# fast_script_python
A continuation of the 2017 summer FAST project, where the script is converted to the Python language.
The original Bash version of the script can be found here: https://github.com/shanalii/Pulsar-Scripts-NAOC-FAST.
The script runs the PRESTO search pipeline to process raw radio telescope data and searches for pulsars. It runs rfifind, DDplan.py, prepsubband, realfft, accelsearch, accelsift, and prepfold, and in the end generates plots of the most likely pulsar candidates. The PRESTO package is required to run this script. 

## Package Contents
* ddscript.py - The Python script
* ddscriptv13.bash - The most updated version of the original Bash script
* LICENSE - The MIT License under which this project is licensed
* README.md - This file
* ddpython_report.pdf - A written report on this project's motivations, process, and results

## Getting Started

Please view the wiki http://ism.bao.ac.cn/wiki/index.php/Pulsar_Summer_projects_2017 for detailed instructions to install the programs and packages necessary to run the program. 

### Prerequisites

Please install the following to run the script:

* Scott Ransom's PRESTO package (git://github.com/scottransom/presto.git)
* FFTW (http://www.fftw.org/)
* PGPLOT (http://www.astro.caltech.edu/~tjp/pgplot/)
* CFITSIO (https://heasarc.gsfc.nasa.gov/fitsio/fitsio.html)
* Tempo (git://git.code.sf.net/p/tempo/tempo)
* LaTeX2HTML (http://www.latex2html.org/)

### Running the Script

Run the program on the command line to process a raw radio telescope data file:

```
python ddpythonv1.py directory_of_data_file filename
```

## Authors

* **Shana Li** - https://github.com/shanalii

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

* Scott Ransom - Developer of the PRESTO data processing software - http://www.cv.nrao.edu/~sransom/presto/
* Professor Di Li - Advisor of summer project at NAOC and FAST in 2017
* Zhichen Pan - Postdoc advisor for summer project and this extension
* Maura McLaughlin - Advisor and author of a prepfold script, upon which part of this script was based
