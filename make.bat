echo "step 1. start package!"
Call ./pack.bat
echo "step 2. start build!"
Call ./msi.bat
echo "step 3. start zip!"
Call "zip.py"