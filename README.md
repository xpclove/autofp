# AutoFP
AutoFP is an automated Fullprof refinement software that supports UI interfaces, as well as command-line and high-throughput modes. With it, you can efficiently solve the crystal structure analysis of X-ray diffraction and Neutron diffraction patterns.  Now, AutoFP support Python 3!
AutoFP Website: <http://physiworld.vipsinaapp.com/autofp.html>.  Shanghai University, Department of Physics  
GitHub: <https://github.com/xpclove/autofp>, Gitee: <https://gitee.com/xpclove/autofp>  
Email : autofp@163.com  
Authors : Xiaopeng Cui, etc.  

## Requirement

**OS Platforms:**  
- Windows XP/7/8/10/11 (x86/x64)  
- Linux (x86/x64)

**Dependency Libraries** (already packaged in AutoFP.msi (x86)):  
- [diffpy/SrRietveld/PyFullProf](http://www.diffpy.org/doc/srrietveld/) （http://www.diffpy.org/doc/srrietveld/)  
- [Python2.7 / Python 3 +](https://www.python.org/downloads/) (https://www.python.org/downloads/)  
- [PyQT4](https://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.4/) (https://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.4/)
- [Numpy](http://www.scipy.org/scipylib/download.html) (http://www.scipy.org/scipylib/download.html)
- [Matplotlib](http://matplotlib.org/) （http://matplotlib.org/) 
- `future` (install via `pip install future`, enables AutoFP support for both Python 2.7 and Python 3 +)

**Refinement Software:**  
- FullProf (Windows: fp2k.exe / Linux: fp2k) [http://www.ill.eu/sites/fullprof/](http://www.ill.eu/sites/fullprof/) （http://www.ill.eu/sites/fullprof/）


## How To Use AutoFP?
Python UI program entry (Windows, Linux)

		python autofp.py start UI
		1) click "Open" *.pcr file( with *.dat in the same folder), "Autoslect", "Run"
		2) click "Autoselect" button to select the refinement parameters
				"cycle = 0 " represent auto-select the cycles number;
				"cycle = n > 0 " represent run n cycles
		3) click "Run" button  to autorun  the refinement 

Python Shell program entry (Windows, Linux)

		pyhton shautofp.py -c 1 -a *.pcr
			-c 1 : cycle number 1；set "-c 0" indicates the automatic determination of the number of cycles
			-a : autoselect parameters
			*.pcr : Fullprof task pcr path ( with *.dat in the same folder)


How to compile *.msi for Windows ? ( It is recommended to use Windows 7/8 to compile )

		You can use the already compiled MSI installation package in AutoFP_v_xxx.zip. Or you can recompile it.
		Run make.bat to creat autofp.msi(msi.bat needs software "AdvancedInstaller" )
		pack.bat needs to configure the directory of python2.7 and install py2exe version 0.6.9

Program setting (Windows, Linux)

	(AutoFP Directory)/setting.txt

	 "fp2k_path": "pathto\\fp2k.exe"	
	  # This key indicates the absolute path of fullprof core fp2k. If you set it to "fp2k", the program will use the built-in fullprof 2017 version of fp2k. Windows: fp2k.exe (Fullprof 2017), Linux: fp2k(Fullprof 2021 -> Ubuntu 20.04+)。
	  # If you use Ubuntu 16.04, plese use Fullprof 2017.

## Document:
For more detailed documentation, check out this URL <http://physiworld.vipsinaapp.com/document.html>

Python2.7 Autofp UI Video tutorial:  
[1) Y2O3 Xray demo @ Windows](http://physiworld.vipsinaapp.com/demo.html)   
[2) PbSO4 Neutron CW demo @ Windows](http://physiworld.vipsinaapp.com/demo_pbso4_cw.html)

Example:  
The examples are in the Program folder (such as C:\Program Files(x86)\AutoFP\) with the directory bane example.zip. At present, the refined results of all the examples have reached the level of the original Fullprof examples.

## Reference:
1. [Xiaopeng Cui, etc. A GUI for highly automated Rietveld refinement using an expert system algorithm based on FullProf ( 2015 )](http://webfile.sinacloud.net/autofp/kc5011.pdf)  
2. [Xiaopeng Cui, etc. Design and Application of AutoFP: A Program for High-Throughput and Automated Rietveld Refinement Based on AI Algorithm ( 2016 )](http://webfile.sinacloud.net/autofp/autofp.pdf)