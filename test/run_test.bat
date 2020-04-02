pytest -s -v --doctest-modules --doctest-glob="*.rst" --doctest-continue-on-failure --doctest-report udiff --continue-on-collection-errors -rfE

IF %ERRORLEVEL% NEQ 0 exit /B 1
exit /B 0

:: Vim: set ff=dos:
