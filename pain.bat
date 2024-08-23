@echo off
setlocal enabledelayedexpansion

:restart
:: Clear the contents of the pain_table.txt file at the start without adding a new line
break > pain_table.txt
:: Clear the console and ask for initial pain score at time 0
cls
set /p pain0="Enter the starting pain score (0-100) at time point 0: "

:: Calculate the target pain score for 80% reduction
set /a targetPainScore=pain0*20/100

:: Initialize the table with the target pain score
echo Time 0^| Pain Score: %pain0% ^| Target for 80%% Reduction: %targetPainScore% >> pain_table.txt

set timePoint=0

:loop
:: Clear the console
cls

:: Display the updated table
type pain_table.txt

:: Ask for pain score at the next time point
set /p painNow="Enter the pain score (0-100) at next time point, 'r' to restart, or 'q' to quit: "
if /i "%painNow%"=="q" goto end
if /i "%painNow%"=="r" goto restart

:: Calculate percentage reduction
set /a reductionPercentage=((pain0 - painNow) * 100) / pain0

:: Get current time point number
set /a timePoint+=1

:: Output the new row to the table
echo Time %timePoint%^| Pain Score: %painNow% ^| Reduction: %reductionPercentage%%% >> pain_table.txt

:: Loop again
goto loop

:end
echo Script finished. Exiting.
