@echo off

set dir=bin
set cur_dir=%cd%
set install_dir="%cur_dir%\amp"

if not exist %install_dir% (
    md %install_dir%
)

if not exist %dir% (
    md %dir%
) else (
    rd /s /q %dir% && md %dir%
)

robocopy .\icon %install_dir%\icon /E /MT:8 

cd %dir%
copy ..\fav.ico .\
copy ..\*.py .\

pyinstaller -Fw login_window.py -i .\fav.ico -p E:\Python\Python38-32\Lib\site-packages\pywin32_system32
copy .\dist\login_window.exe %install_dir%