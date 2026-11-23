@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
set "PYTHON=%CD%\.venv\Scripts\python.exe"
set "RUNNER=publications\P01\analyses\run_local_pipeline.py"
set "DEFAULT_PARTS=%USERPROFILE%\FLIR_ADAS_v2"
set "DEFAULT_RUNS=%USERPROFILE%\P01_runs"
set "LAST_SUMMARY="

:menu
cls
echo ==============================================================
echo P01 Sensors - FLIR ADAS v2 - Windows / Andromeda
echo ==============================================================
echo 1. Install / update dependencies in .venv
echo 2. Check Python, CUDA and data archive
echo 3. Train and measure on validation (local only)
echo 4. Publish completed validation summary to GitHub PR
echo 5. Show experiment instructions
echo 0. Exit
echo.
choice /c 123450 /n /m "Select [1-5,0]: "
if errorlevel 6 goto end
if errorlevel 5 goto docs
if errorlevel 4 goto publish
if errorlevel 3 goto train
if errorlevel 2 goto check
if errorlevel 1 goto install
goto menu

:install
echo.
where py >nul 2>nul
if errorlevel 1 (
    echo Python launcher 'py' not found. Install Python 3.12 first.
    goto done
)
if not exist "%PYTHON%" (
    echo Creating local .venv using Python 3.12 ...
    py -3.12 -m venv ".venv"
    if errorlevel 1 goto failed
)
echo Installing project and Torch dependencies inside .venv ...
"%PYTHON%" -m pip install -e ".[torch]"
if errorlevel 1 goto failed
echo Installation completed. PyTorch CUDA must still be verified with menu 2.
goto done

:check
echo.
if not exist "%PYTHON%" (
    echo No .venv found. Run menu 1.
    goto done
)
"%PYTHON%" -c "import sys,torch,torchvision; print('Python:',sys.version.split()[0]); print('Torch:',torch.__version__); print('TorchVision:',torchvision.__version__); print('CUDA:',torch.cuda.is_available()); print('GPU:',torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'not available')"
if errorlevel 1 goto failed
call :parts
echo Checking original multipart archive directory:
echo "%PARTS_DIR%"
set "MISSING=0"
for /l %%N in (0,1,11) do (
    if %%N LSS 10 (
        if not exist "%PARTS_DIR%\FLIR_ADAS_v2.zip.0%%N" set "MISSING=1"
    ) else (
        if not exist "%PARTS_DIR%\FLIR_ADAS_v2.zip.%%N" set "MISSING=1"
    )
)
if "%MISSING%"=="1" (
    echo Some archive parts are missing. Provide original FLIR archive or a verified download manifest.
) else (
    echo All 12 archive part filenames exist. Content checks occur during the experiment.
)
goto done

:train
echo.
if not exist "%PYTHON%" (
    echo No .venv found. Select menu 1 first.
    goto done
)
call :parts
echo.
echo Review the original FLIR dataset licence before proceeding.
choice /c YN /n /m "Do you acknowledge permitted research use? [Y/N]: "
if errorlevel 2 goto menu
set "DEVICE=cuda"
choice /c YN /n /m "Train on NVIDIA CUDA GPU? [Y/N, N=CPU]: "
if errorlevel 2 set "DEVICE=cpu"
if /i "%DEVICE%"=="cuda" (
    "%PYTHON%" -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)"
    if errorlevel 1 (
        echo CUDA unavailable. Check menu 2 or select CPU explicitly.
        goto done
    )
)
set "RUN_ROOT=%DEFAULT_RUNS%"
set /p "RUN_ROOT=Results parent directory [default: %DEFAULT_RUNS%]: "
if not defined RUN_ROOT set "RUN_ROOT=%DEFAULT_RUNS%"
set "RUN_DIR=%RUN_ROOT%\run_%RANDOM%_%RANDOM%"
echo.
echo Training will save files in:
echo "%RUN_DIR%"
choice /c YN /n /m "Start training and validation? [Y/N]: "
if errorlevel 2 goto menu
"%PYTHON%" "%RUNNER%" --parts-dir "%PARTS_DIR%" --work-dir "%RUN_DIR%" --rights-acknowledged --device "%DEVICE%"
if errorlevel 1 goto failed
set "LAST_SUMMARY=%RUN_DIR%\summary.json"
echo.
echo Training completed. Results remain local until you select menu 4.
goto done

:publish
echo.
if not exist "%PYTHON%" (
    echo No .venv found. Select menu 1 first.
    goto done
)
where gh >nul 2>nul
if errorlevel 1 (
    echo GitHub CLI 'gh' not found. Install it and run 'gh auth login'.
    goto done
)
gh auth status >nul 2>nul
if errorlevel 1 (
    echo GitHub CLI not authenticated. Run 'gh auth login'.
    goto done
)
set "SUMMARY=%LAST_SUMMARY%"
if not defined SUMMARY (
    set /p "SUMMARY=Full path to completed summary.json: "
) else (
    echo Current session summary:
    echo "%SUMMARY%"
    choice /c YN /n /m "Publish this summary? [Y/N, N=choose another]: "
    if errorlevel 2 set /p "SUMMARY=Full path to completed summary.json: "
)
if not exist "%SUMMARY%" (
    echo Summary file not found. Publication cancelled.
    goto done
)
echo.
echo Only a sanitised validation summary goes to a GitHub PR.
echo No weights, raw images, test results or automatic merge.
choice /c YN /n /m "Publish summary now? [Y/N]: "
if errorlevel 2 goto menu
"%PYTHON%" "%RUNNER%" --publish-summary "%SUMMARY%"
if errorlevel 1 goto failed
goto done

:parts
set "PARTS_DIR=%DEFAULT_PARTS%"
set /p "PARTS_DIR=FLIR archive directory [default: %DEFAULT_PARTS%]: "
if not defined PARTS_DIR set "PARTS_DIR=%DEFAULT_PARTS%"
exit /b 0

:docs
echo.
echo See publications\P01\analyses\LOCAL_PIPELINE.md
echo Training uses source train and validation only. Held-out test is never opened.
goto done

:failed
echo.
echo Operation failed. Read the error above. No automatic retry or upload.

:done
echo.
pause
goto menu

:end
endlocal
exit /b 0
