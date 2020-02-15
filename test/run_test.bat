set NOSE_EXCLUDE=recursion
iptest -- -vx

ipython -h
IF %ERRORLEVEL% NEQ 0 exit /B 1
ipython3 -h
IF %ERRORLEVEL% NEQ 0 exit /B 1
exit /B 0

:: Vim: set ff=dos:
