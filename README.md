# AutoFP

AutoFP website <http://physiworld.vipsinaapp.com/>

## Requirement：
	OS platforms：
                         Windows XP/7/8/8.1/10/11	or  Linux
	Dependence library (already packaged in AutoFP.msi):
			 			 diffpy/SrRietveld/PyFullProf     http://www.diffpy.org/doc/srrietveld/
                         python2.7			https://www.python.org/download/releases/2.7/
                         pyqt4 	            https://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.10.4/
                         numpy              http://www.scipy.org/scipylib/download.html
                         matplotlib         http://matplotlib.org/
	Refinement software: 
                         FullProf 2016 (fp2k) 		     http://www.ill.eu/sites/fullprof/

## How to use?
Python2 UI program entry (Windows, Linux)

		autofp.py

Python2 Shell program entry (Windows, Linux)

		pyhton shautofp.py -c 1 -a *.pcr
		-c 1 : cycle number 1
		-a : autoselect parameters
		*.pcr : task pcr path


How to compile *.msi for Windows ? (Windows)

		run make.bat to creat autofp.msi (it needs software "AdvancedInstaller")

Program setting (Windows, Linux)

	(AutoFP Directory)/setting.txt

For more detailed documentation, check out this URL <http://physiworld.vipsinaapp.com/document.html>

## Reference:
1. [A GUI for highly automated Rietveld refinement using an expert system algorithm based on FullProf (2016 )](http://webfile.sinacloud.net/autofp/kc5011.pdf)

2. [Design and Application of AutoFP: A Program for High-Throughput and Automated Rietveld Refinement Based on AI Algorithm(2016 )](http://webfile.sinacloud.net/autofp/autofp.pdf)