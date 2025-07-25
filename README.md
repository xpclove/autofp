# AutoFP

AutoFP website <http://physiworld.sinaapp.com/autofp.html>

## Requirement：
	OS platforms：
                         Windows XP/7/8/8.1/10/11	or  Linux
	Dependence library (already packaged in AutoFP.msi):
			 			 diffpy/SrRietveld/PyFullProf     http://www.diffpy.org/doc/srrietveld/
                         python2.7          https://www.python.org/download/releases/2.7/
                         pyqt4 	         http://www.riverbankcomputing.com/software/pyqt/download
                         numpy              http://www.scipy.org/scipylib/download.html
                         matplotlib         http://matplotlib.org/
	Refinement software: 
                         FullProf(fp2k) 		     http://www.ill.eu/sites/fullprof/

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

For more detailed documentation, check out this URL <http://physiworld.sinaapp.com/document.html>