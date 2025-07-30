rmdir /s /q dist 
rmdir /s /q build
mkdir dist
mkdir build
C:/Python27/python.exe pack.py py2exe
C:/Python27/python.exe release_dist.py