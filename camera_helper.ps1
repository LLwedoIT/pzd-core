# Camera Helper Script - Release camera resources on Windows
# Usage: powershell -ExecutionPolicy Bypass -File camera_helper.ps1 -Action release

param(
    [string]$Action = "release"
)

Write-Host "PZDetector Camera Helper" -ForegroundColor Cyan

# Define functions first
function ReleaseCamera {
    Write-Host "[Camera] Releasing camera resources..." -ForegroundColor Yellow
    
    try {
        # Find camera device
        $cameras = Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue
        
        if ($cameras -eq $null) {
            Write-Host "[Camera] No camera device found" -ForegroundColor Red
            return
        }
        
        foreach ($camera in $cameras) {
            Write-Host "[Camera] Found: $($camera.Name)" -ForegroundColor Green
            
            # Disable then immediately re-enable to force release
            Write-Host "[Camera] Disabling device..." -ForegroundColor Yellow
            Disable-PnpDevice -InputObject $camera -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
            
            Start-Sleep -Milliseconds 500
            
            Write-Host "[Camera] Re-enabling device..." -ForegroundColor Yellow
            Enable-PnpDevice -InputObject $camera -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
            
            Write-Host "[Camera] Reset complete!" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "[Camera] Error: $($_)" -ForegroundColor Red
    }
}

function DisableCamera {
    Write-Host "[Camera] Disabling camera..." -ForegroundColor Yellow
    
    try {
        $cameras = Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue
        
        foreach ($camera in $cameras) {
            Write-Host "[Camera] Disabling: $($camera.Name)" -ForegroundColor Green
            Disable-PnpDevice -InputObject $camera -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
        }
        
        Write-Host "[Camera] Camera disabled" -ForegroundColor Green
    }
    catch {
        Write-Host "[Camera] Error: $($_)" -ForegroundColor Red
    }
}

function EnableCamera {
    Write-Host "[Camera] Enabling camera..." -ForegroundColor Yellow
    
    try {
        $cameras = Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue
        
        foreach ($camera in $cameras) {
            Write-Host "[Camera] Enabling: $($camera.Name)" -ForegroundColor Green
            Enable-PnpDevice -InputObject $camera -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
        }
        
        Write-Host "[Camera] Camera enabled" -ForegroundColor Green
    }
    catch {
        Write-Host "[Camera] Error: $($_)" -ForegroundColor Red
    }
}

function CheckCameraStatus {
    Write-Host "[Camera] Checking status..." -ForegroundColor Yellow
    
    try {
        $cameras = Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue
        
        if ($cameras -eq $null) {
            Write-Host "[Camera] No camera device found" -ForegroundColor Red
            return
        }
        
        foreach ($camera in $cameras) {
            Write-Host "[Camera] $($camera.Name)" -ForegroundColor Green
            Write-Host "  Status: $($camera.Status)" -ForegroundColor Cyan
            Write-Host "  Device ID: $($camera.InstanceId)" -ForegroundColor Cyan
        }
    }
    catch {
        Write-Host "[Camera] Error: $($_)" -ForegroundColor Red
    }
}

# Now call function based on action parameter
switch ($Action.ToLower()) {
    "release" {
        ReleaseCamera
    }
    "disable" {
        DisableCamera
    }
    "enable" {
        EnableCamera
    }
    "status" {
        CheckCameraStatus
    }
    default {
        Write-Host "Usage: camera_helper.ps1 -Action [release|disable|enable|status]"
    }
}
