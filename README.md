# AutoFP
AutoFP is an automated Fullprof refinement software that supports UI interfaces, as well as command-line and high-throughput modes. With it, you can efficiently solve the crystal structure analysis of X-ray diffraction and neutron diffraction patterns.
AutoFP website <http://physiworld.vipsinaapp.com/>. Contact: autofp@163.com

## Requirement：
	OS platforms：
                         Windows XP/7/8/10/11(x86/x64)	or  Linux(x86/x64)
	Dependence library (already packaged in AutoFP.msi):
			 			 diffpy/SrRietveld/PyFullProf     http://www.diffpy.org/doc/srrietveld/
                         python2.7			https://www.python.org/download/releases/2.7/
                         pyqt4 	            https://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.10.4/
                         numpy              http://www.scipy.org/scipylib/download.html
                         matplotlib         http://matplotlib.org/
	Refinement software: 
                         FullProf  (Windows: fp2k.exe / Linux: fp2k) http://www.ill.eu/sites/fullprof/


## How to use?
Python2.7 UI program entry (Windows, Linux)

		python autofp.py
		Then click "Open" pcr file, "Autoslect", "run" 

Python2.7 Shell program entry (Windows, Linux)

		pyhton shautofp.py -c 1 -a *.pcr
		-c 1 : cycle number 1；set "-c 0" indicates the automatic determination of the number of cycles
		-a : autoselect parameters
		*.pcr : Fullprof task pcr path


How to compile *.msi for Windows ? (Windows)

		run make.bat to creat autofp.msi (it needs software "AdvancedInstaller" <13.0 )

Program setting (Windows, Linux)

	(AutoFP Directory)/setting.txt

	 "fp2k_path": "pathto\\fp2k.exe"	
	  # This key indicates the absolute path of fullprof fp2k. If you set it to "fp2k", the program will use the built-in fullprof 2017 version of fp2k. Windows: fp2k.exe (Fullprof 2017), Linux: fp2k(Fullprof 2017 -> Ubuntu 16.04)。
	  # If you use Ubuntu 20.04+, plese use Fullprof 2021+.

## Document:
For more detailed documentation, check out this URL <http://physiworld.vipsinaapp.com/document.html>

Python2.7 Autofp UI Video tutorial: 

[1) Y2O3 Xray demo @ Windows 8](http://physiworld.vipsinaapp.com/demo.html) 

[2) PbSO4 Neutron CW demo @ Windows 8](http://physiworld.vipsinaapp.com/demo_pbso4_cw.html)

## Reference:
1. [A GUI for highly automated Rietveld refinement using an expert system algorithm based on FullProf (2016 )](http://webfile.sinacloud.net/autofp/kc5011.pdf)

2. [Design and Application of AutoFP: A Program for High-Throughput and Automated Rietveld Refinement Based on AI Algorithm(2016 )](http://webfile.sinacloud.net/autofp/autofp.pdf)