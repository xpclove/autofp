#Used successfully in PythonXY2.7.3 with py2exe ,wxPython 2.8.12 and matplotlib 1.2.0 
from distutils.core import setup
import  matplotlib
import py2exe

#----------------------------------------------------------------------------
includes=[
    "sip",
    "FileDialog",
"matplotlib",
"matplotlib.backends",
"matplotlib.figure",
"pylab",
"numpy",
"matplotlib.backends.backend_tkagg",
"matplotlib.backends.backend_wxagg",
]
#----------------------------------------------------------------------------
excludes=['_gtkagg', 
'_tkagg', 
'_agg2', 
'_cairo',
'_cocoaagg',
'_fltkagg',
'_gtk', 
'_gtkcairo']
#----------------------------------------------------------------------------
dll_excludes=['libgdk-win32-2.0-0.dll',
'libgobject-2.0-0.dll']
#----------------------------------------------------------------------------
options= {
		'py2exe':{ 
				"includes" : includes,
				'excludes':excludes,
				'dll_excludes':dll_excludes
				}
}
#----------------------------------------------------------------------------
data_files=matplotlib.get_py2exe_datafiles()
#----------------------------------------------------------------------------
#for windows program 
windows=[
{"script": "autofp.py","icon_resources":[(0,"AutoFP.ico")]}
]
#----------------------------------------------------------------------------
#for console program
console = [
{"script": "shautofp.py"}
]
#----------------------------------------------------------------------------
setup(
windows=windows, 
console=console,
options=options, 
data_files=data_files
)
