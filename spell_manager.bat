@echo off
setlocal EnableDelayedExpansion

set "BASE_DIR=%~dp0spells"
set "META_DIR=%BASE_DIR%\metadata"
if not exist "%BASE_DIR%" mkdir "%BASE_DIR%"
if not exist "%META_DIR%" mkdir "%META_DIR%"

call :find_python
call :ensure_example

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

:ensure_example
set "EXAMPLE_NAME=example_firebolt"
set "EXAMPLE_TXT=%BASE_DIR%\%EXAMPLE_NAME%.txt"
if exist "%EXAMPLE_TXT%" exit /b

echo Creating example spell "%EXAMPLE_NAME%" so first-time users can see the format...
call :save_spell "%EXAMPLE_NAME%" "manifest,bind,vector,impulse"
exit /b

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
set "JSON_FILE=%META_DIR%\%NAME%.json"
set "CIRCLE_JSON=%META_DIR%\%NAME%_circle.json"
set "CIRCLE_PNG=%META_DIR%\%NAME%_circle.png"

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
  echo   "sigils": [!SIGIL_JSON!],
  echo   "circle_json": "%NAME%_circle.json",
  echo   "circle_image": "%NAME%_circle.png"
  echo }
)

if defined PYTHON_CMD (
  %PYTHON_CMD% "%~dp0circle_converter.py" %SIGIL_LINE:,= % --pretty > "%CIRCLE_JSON%"
  if errorlevel 1 (
    echo Failed to generate circle JSON preview metadata.
    exit /b 1
  )

  %PYTHON_CMD% "%~dp0json_to_image.py" "%CIRCLE_JSON%" "%CIRCLE_PNG%"
  if errorlevel 1 (
    echo Failed to generate circle image preview.
    exit /b 1
  )
) else (
  echo Python not found. Saved txt/json metadata but skipped circle preview generation.
)

exit /b

:find_python
set "PYTHON_CMD="
where py >nul 2>nul
if %errorlevel%==0 (
  set "PYTHON_CMD=py -3"
  exit /b
)

where python >nul 2>nul
if %errorlevel%==0 (
  set "PYTHON_CMD=python"
)
exit /b

:done
echo.
echo Finished.
endlocal
