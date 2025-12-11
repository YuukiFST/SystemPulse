@Echo Off
SetLocal EnableDelayedExpansion
Title Disk Corruption Checker
Set Version=3.0
color 0B

OpenFiles >Nul 2>&1
If %ErrorLevel% NEQ 0 (
    Echo This Script Needs To Be Run As Administrator.
    Echo Restarting Script As Administrator...
    Timeout /t 2 /NoBreak >Nul 2>&1

    Powershell -Command "Start-Process Cmd -ArgumentList '/c %~s0' -Verb RunAs"
    Exit
)

PowerShell "Write-Host 'Quick Disk Check' -ForegroundColor Blue"
For %%D In (C D E F G H I J K L M N O P Q R S T U V W X Y Z) Do (
    If Exist %%D:\ (
    ChkDsk %%D: /Scan
    )
)
Cls

PowerShell "Write-Host 'Full Disk Check With Fixing And Bad Sector Recovery' -ForegroundColor Blue"
For %%D In (C D E F G H I J K L M N O P Q R S T U V W X Y Z) Do (
    If Exist %%D:\ (
    Echo Y | ChkDsk %%D: /F /R
    )
)
Cls

If Not Exist C:\Windows\Temp (
    PowerShell "Write-Host 'C:\Windows\Temp Folder Not Found , Creating It' -ForegroundColor Yellow"
    MkDir C:\Windows\Temp
)

PowerShell "Write-Host 'Granting Permissions To %TEMP% Folder' -ForegroundColor Green"
IcaCls "%TEMP%" /Grant Everyone:(OI)(CI)F /T >Nul 2>&1
Cls

PowerShell "Write-Host 'Granting Permissions To %USERPROFILE%\AppData\Local\Temp Folder' -ForegroundColor Green"
IcaCls "%USERPROFILE%\AppData\Local\Temp" /grant Everyone:(OI)(CI)F /T >Nul 2>&1
Cls

PowerShell "Write-Host 'Granting Permissions To C:\Windows\Temp Folder' -ForegroundColor Green"
IcaCls "C:\Windows\Temp" /Grant Everyone:(OI)(CI)F /T >Nul 2>&1
Cls

PowerShell "Write-Host 'Granting Permissions To C:\Windows\Prefetch Folder' -ForegroundColor Green"
IcaCls "C:\Windows\Prefetch" /Grant Everyone:(OI)(CI)F /T >Nul 2>&1
Cls

PowerShell "Write-Host 'Dism.Exe - ScanHealth' -ForegroundColor Blue"
Dism.Exe /Online /Ceanup-Image /CheckHealth
Cls

PowerShell "Write-Host 'Dism.Exe - CheckHealth' -ForegroundColor Blue"
Dism.Exe /Online /Ceanup-Image /ScanHealth
Cls

PowerShell "Write-Host 'Dism.Exe - RestoreHealth' -ForegroundColor Blue"
Dism.Exe /Online /Ceanup-Image /RestoreHealth
Cls

PowerShell "Write-Host 'Dism.Exe - AnalyzeComponentStore' -ForegroundColor Blue"
Dism.Exe /Online /Cleanup-Image /AnalyzeComponentStore
Cls

PowerShell "Write-Host 'Dism.Exe - StartComponentCleanup' -ForegroundColor Blue"
Dism.Exe /Online /Cleanup-Image /StartComponentCleanup
Cls

PowerShell "Write-Host 'Dism.exe - StartComponentCleanup ResetBase' -ForegroundColor Blue"
Dism.Exe /Online /Cleanup-Image /StartComponentCleanup /ResetBase
Cls

PowerShell "Write-Host 'SFC - Verify Only' -ForegroundColor Blue"
Sfc /VerifyOnly
Cls

PowerShell "Write-Host 'SFC - Scan 1' -ForegroundColor Blue"
Sfc /ScanNow
Cls

PowerShell "Write-Host 'SFC - Scan 2' -ForegroundColor Blue"
Sfc /ScanNow
Cls

PowerShell "Write-Host 'Running Disk Cleanup' -ForegroundColor Blue"
CleanMgr /SageRun:1 >Nul 2>&1
Cls

PowerShell "Write-Host 'Clearing All Event Logs' -ForegroundColor Blue"
For /F "Tokens=*" %%G In ('Wevtutil El') Do (
    Wevtutil Cl "%%G" >Nul 2>&1 || PowerShell "Write-Host 'Failed To Clear Log: %%G' -ForegroundColor Red"
)
Cls

PowerShell "Write-Host 'Clearing DNS Cache' -ForegroundColor Blue"
IpConfig /FlushDns >Nul 2>&1

PowerShell "Write-Host 'Clearing Temporary Folders...' -ForegroundColor Blue"
For /D %%G In ("%TEMP%\*") Do Rd /S /Q "%%G"
Del /Q "%TEMP%\*" >Nul 2>&1
For /D %%G In ("%USERPROFILE%\AppData\Local\Temp\*") Do Rd /S /Q "%%G"
Del /Q "%USERPROFILE%\AppData\Local\Temp\*" >Nul 2>&1
For /D %%G In ("C:\Windows\Temp\*") Do Rd /S /Q "%%G"
Del /Q "C:\Windows\Temp\*" >Nul 2>&1
For /D %%G In ("C:\Windows\Prefetch\*") Do Rd /S /Q "%%G"
Del /Q "C:\Windows\Prefetch\*" >Nul 2>&1

PowerShell "Write-Host 'All Operations Completed Successfully! , You May Restart Your PC.' -ForegroundColor Green"
Timeout 2 >Nul 2>&1
EndLocal
Exit

