rmdir /s /q dist 
rmdir /s /q build
mkdir dist
mkdir build
D:/Python27_x86/python.exe pack.py py2exe
D:/Python27_x86/python.exe release_dist.py