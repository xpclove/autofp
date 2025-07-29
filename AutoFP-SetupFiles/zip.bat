"C:\Program Files\WinRAR\winrar.exe" d AutoFP.zip *.msi
set version=%1%
set msi=AutoFP_v_%version%.msi
copy /y AutoFP.msi %msi%
"C:\Program Files\WinRAR\winrar.exe" a AutoFP.zip %msi%
set zipfile=AutoFP_v_%version%.zip
copy /y AutoFP.zip %zipfile%