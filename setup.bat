call winget install Python.Python.3.11

echo Creating venv
call py -3.11 -m venv subtitle_venv

echo Activating venv 
call .\subtitle_venv\Scripts\activate.bat

echo Installing requirements
call pip install -r requirements.txt

