@echo off
setlocal EnableDelayedExpansion

set "BASE_DIR=%~dp0spells"
if not exist "%BASE_DIR%" mkdir "%BASE_DIR%"

echo ================================
echo        Vector-Regnum Spells
echo ================================
echo 1^) Start a new spell
echo 2^) Edit an existing spell
echo 3^) Exit
set /p CHOICE=Choose an option ^(1-3^): 

if "%CHOICE%"=="1" goto :new_spell
if "%CHOICE%"=="2" goto :edit_spell
if "%CHOICE%"=="3" goto :done

echo Invalid choice.
goto :done

:new_spell
set /p SPELL_NAME=Spell name: 
if "%SPELL_NAME%"=="" (
  echo Spell name cannot be empty.
  goto :done
)

set /p SIGILS=Type sigils comma-separated ^(example: sigil,sigil,sigil2,sigil45^): 
if "%SIGILS%"=="" (
  echo Sigils cannot be empty.
  goto :done
)

call :save_spell "%SPELL_NAME%" "%SIGILS%"
echo Saved spell "%SPELL_NAME%".
goto :done

:edit_spell
echo.
echo Existing spells:
dir /b /a-d "%BASE_DIR%\*.txt" 2>nul
if errorlevel 1 (
  echo No existing spells found.
  goto :done
)

echo.
set /p SPELL_FILE=Type the spell file name to edit ^(without .txt^): 
if "%SPELL_FILE%"=="" goto :done

set "TXT_FILE=%BASE_DIR%\%SPELL_FILE%.txt"
if not exist "%TXT_FILE%" (
  echo Spell "%SPELL_FILE%" was not found.
  goto :done
)

echo.
echo Current plain text:
set /p CURRENT_SIGILS=<"%TXT_FILE%"
echo !CURRENT_SIGILS!
echo.
set /p NEW_SIGILS=Type updated comma-separated sigils ^(leave blank to keep current^): 
if "%NEW_SIGILS%"=="" set "NEW_SIGILS=!CURRENT_SIGILS!"

call :save_spell "%SPELL_FILE%" "%NEW_SIGILS%"
echo Updated spell "%SPELL_FILE%".
goto :done

:save_spell
set "NAME=%~1"
set "SIGIL_LINE=%~2"
set "TXT_FILE=%BASE_DIR%\%NAME%.txt"
set "JSON_FILE=%BASE_DIR%\%NAME%.json"

echo %SIGIL_LINE%>"%TXT_FILE%"

set "SIGIL_JSON="
for %%S in (%SIGIL_LINE:,= %) do (
  if defined SIGIL_JSON (
    set "SIGIL_JSON=!SIGIL_JSON!, \"%%~S\""
  ) else (
    set "SIGIL_JSON=\"%%~S\""
  )
)

>"%JSON_FILE%" (
  echo {
  echo   "name": "%NAME%",
  echo   "sigils_raw": "%SIGIL_LINE%",
  echo   "sigils": [!SIGIL_JSON!]
  echo }
)
exit /b

:done
echo.
echo Finished.
endlocal
