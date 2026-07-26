@echo off
echo Killing all RED processes...
taskkill /F /IM python.exe /T
taskkill /F /IM RedIsland.exe /T
taskkill /F /IM DynamicWin.exe /T
echo All instances killed.
pause
