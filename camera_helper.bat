@echo off
REM PZDetector Camera LED Release Helper
REM Right-click this file and select "Run as administrator"

setlocal

if NOT "%1"=="" goto %1

cls
echo.
echo ========================================
echo   PZDetector Camera LED Release
echo ========================================
echo.
echo Your webcam LED is still on?
echo Just running this file will fix it!
echo.
pause

:release
cls
echo Releasing camera resources...
echo (This requires administrator privileges)
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "^
$cameras = Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue; ^
if ($cameras) { ^
  foreach ($cam in $cameras) { ^
    Write-Host 'Found camera:' $cam.Name -ForegroundColor Green; ^
    Write-Host 'Disabling...' -ForegroundColor Yellow; ^
    Disable-PnpDevice -InputObject $cam -Confirm:$false -ErrorAction SilentlyContinue | Out-Null; ^
    Start-Sleep -Milliseconds 800; ^
    Write-Host 'Re-enabling...' -ForegroundColor Yellow; ^
    Enable-PnpDevice -InputObject $cam -Confirm:$false -ErrorAction SilentlyContinue | Out-Null; ^
    Write-Host 'Done!' -ForegroundColor Green; ^
  } ^
} else { ^
  Write-Host 'No camera found. Check Device Manager.' -ForegroundColor Red; ^
}"

echo.
echo ========================================
echo   Camera LED should turn off now!
echo ========================================
echo.
pause
goto :eof

