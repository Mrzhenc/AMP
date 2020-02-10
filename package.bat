@echo off

set dir=bin

if not exist %dir% (
	md %dir%
) else (
	rd /s /q %dir% && md %dir%
)

cd %dir%

copy ..\fav.ico .\
copy ..\*.py .\

pyinstaller -Fw login_window.py -i ../fav.ico -p E:\Python\Python38-32\Lib\site-packages\pywin32_system32