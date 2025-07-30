AutoFP is an auto tools for FullProf Rietveld refinement released under GPL v3 LICENSE.
AutoFP (http://physiworld.sinaapp.com/autofp.html)
Authors: Xiaopeng Cui, etc
Email: autofp@163.com
Shanghai University, Department of Physics 

English version

Dependence：
 OS platforms：
                         Windows XP，Windows 7 ,Windows 8, Windows 10
 Dependence library (already packaged in AutoFP):
						 diffpy/SrRietveld/PyFullProf http://www.diffpy.org/doc/srrietveld/
                         python2.7 https://www.python.org/download/releases/2.7/
                         pyqt4 	  http://www.riverbankcomputing.com/software/pyqt/download
                         numpy     http://www.scipy.org/scipylib/download.html
                         matplotlib http://matplotlib.org/
                         
 Refinement Software 
                         FullProf 		  http://www.ill.eu/sites/fullprof/
How to use AutoFP：
steps:
			 Launch AutoFP
                         select "Auto" tab
                         click "open" or drag PCR file to the UI to open the PCR file
                         click "autoselect" button to select the refinement parameters automatically
						    "cycle=0" represent auto-select the cycles number;
							"cycle=n>0" represent run n cycles
                         click "run" button  to autorun  the refinement 
Attention ：
 1. how to make PCR file：
                      
                         Please use FullProf to make right PCR file，AutoFP need a PCR file a DAT file, please ensure they have the same filename, 
                         such as Y2O3.pcr，Y2O3.dat.
                         Pleae put them in a empty folder which is easy to control.
                        
                       2. About examples：
                         examples are in the folder(such as C:\Program Files(x86)\AutoFP\AutoFP), example.zip 
                         example instrution:  example.txt
					   3. Video of AutoFP Demo(http://pmedia.shu.edu.cn/autofp/document.html)         
                         the Demo of PbSO4 refinement with AutoFP PbSO4 Neutron CW Demo 
				         the Demo of Y2O3 refinement with AutoFP  Y2O3 Xray Demo 
					  
                         
Chinese version

程序依赖：

   	运行平台：
			Windows XP，Windows 7 ,Windows 8

	依赖库(已经打包于程序内，无需额外安装）:
			python2.7 https://www.python.org/download/releases/2.7/
			pyqt4 	  http://www.riverbankcomputing.com/software/pyqt/download
			numpy     http://www.scipy.org/scipylib/download.html
			matplotlib
			diffpy
	精修软件
			FullProf 		  http://www.ill.eu/sites/fullprof/

程序使用说明：

	启动 AutoFP
	选择 Auto 标签页
	open 按钮 打开pcr文件
	autoselect 按钮自动选择精修参数
	点击run按钮 自动精修

附加说明：

	1.PCR文件制作：
	  	请使用FullProf制作出正确PCR文件，本程序运行需要PCR文件和DAT文件，请确保二者文件名			相同，如Y2O3.pcr，Y2O3.dat。 请将二者置于一个空文件夹下，便于程序控制，另外请确保
		文件路径名不包含中文，否则程序不能打开PCR文件。
	2. 例子说明：
		例子在程序文件夹(如C:\Program Files(x86)\AutoFP\)目录下 example.zip 
		例子说明 example.txt
		目前所有例子精修结果均已达到Fullprof原始例子水平