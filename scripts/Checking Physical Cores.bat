@echo off & setlocal enabledelayedexpansion

for /f "delims=" %%i in ('powershell -Command "(Get-CimInstance -ClassName Win32_Processor).Manufacturer"') do set "Manufacturer=%%i"

if /i "%Manufacturer%"=="GenuineIntel" set "Manufacturer=Intel"
if /i "%Manufacturer%"=="AuthenticAMD" set "Manufacturer=AMD"

set "TechName=Unknown"
if /i "%Manufacturer%"=="Intel" set "TechName=Hyper-Threading"
if /i "%Manufacturer%"=="AMD" set "TechName=SMT"

if "%TechName%"=="Unknown" (
    echo Unknown CPU manufacturer: %Manufacturer%
    exit /b 1
)

for /f %%i in ('powershell -Command "(Get-CimInstance -ClassName Win32_Processor | Measure-Object -Property NumberOfCores -Sum).Sum"') do set "PHYSICAL_CORES=%%i"

set "LOGICAL_CORES=%NUMBER_OF_PROCESSORS%"

set "HT_STATUS=Disabled"
if %LOGICAL_CORES% GTR %PHYSICAL_CORES% set "HT_STATUS=Enabled"

set "E_CORE_STATUS=Disabled"
set "HYBRID=0"
set "P_CORES=0"
set "E_CORES=0"

if /i "%Manufacturer%"=="Intel" (
    if "%HT_STATUS%"=="Enabled" (
        set /a "P_CORES = LOGICAL_CORES - PHYSICAL_CORES"
        set /a "E_CORES = 2 * PHYSICAL_CORES - LOGICAL_CORES"
    ) else (
        set /a "P_CORES = PHYSICAL_CORES - (LOGICAL_CORES - PHYSICAL_CORES)"
        set /a "E_CORES = LOGICAL_CORES - P_CORES"
    )

    if !P_CORES! GTR 0 if !E_CORES! GTR 0 (
        set "HYBRID=1"
        set "E_CORE_STATUS=Enabled"
    ) else (
        for /f "delims=" %%i in ('powershell -Command "(Get-CimInstance Win32_Processor).Name"') do set "CPU_NAME=%%i"
        echo !CPU_NAME! | findstr /i "12" >nul && set "HYBRID=1" && set "E_CORE_STATUS=Enabled"
        echo !CPU_NAME! | findstr /i "13" >nul && set "HYBRID=1" && set "E_CORE_STATUS=Enabled"
        echo !CPU_NAME! | findstr /i "14" >nul && set "HYBRID=1" && set "E_CORE_STATUS=Enabled"
    )
)

echo.
echo   CPU Manufacturer: %Manufacturer%
if /i "%Manufacturer%"=="Intel" echo   E-Core: %E_CORE_STATUS%
echo   %TechName% Status: %HT_STATUS%
echo   Physical Cores: %PHYSICAL_CORES%
echo   Logical Processors: %LOGICAL_CORES%
if %HYBRID% equ 1 (
    echo   P-Cores: %P_CORES%
    echo   E-Cores: %E_CORES%
)

set "output="
set "p_core_list="
set "e_core_list="
set "core_list="
set "thread_list="

set /a "MAX_CPU = %LOGICAL_CORES% - 1"

if %HYBRID% equ 1 (
    if "%HT_STATUS%"=="Enabled" (
        set /a "P_END = P_CORES * 2 - 1"
        set /a "E_START = P_CORES * 2"
        set /a "E_END = E_START + E_CORES - 1"
    ) else (
        set /a "P_END = P_CORES - 1"
        set /a "E_START = P_CORES"
        set /a "E_END = E_START + E_CORES - 1"
    )
    
    for /L %%i in (0,1,%MAX_CPU%) do (
        if %%i leq !P_END! (
            if "%HT_STATUS%"=="Enabled" (
                set /a "mod=%%i %% 2"
                if !mod! == 0 (
                    set "core_label=P-Core"
                    set "p_core_list=!p_core_list! %%i"
                ) else (
                    set "core_label=P-Thread"
                )
            ) else (
                set "core_label=P-Core"
                set "p_core_list=!p_core_list! %%i"
            )
        ) else if %%i geq !E_START! if %%i leq !E_END! (
            set "core_label=E-Core"
            set "e_core_list=!e_core_list! %%i"
        ) else (
            set "core_label=Unknown"
        )
        set "output=!output! %%i (!core_label!)"
    )
) else (
    for /L %%i in (0,1,%MAX_CPU%) do (
        if "%HT_STATUS%"=="Enabled" (
            set /a "mod=%%i %% 2"
            if !mod! == 0 (
                set "core_label=Core"
                set "core_list=!core_list! %%i"
            ) else (
                set "core_label=Thread"
                set "thread_list=!thread_list! %%i"
            )
        ) else (
            set "core_label=Core"
            set "core_list=!core_list! %%i"
        )
        set "output=!output! %%i (!core_label!)"
    )
)

echo.
echo   Logical Processor Map:
echo   %output%

if %HYBRID% equ 1 (
    echo.
    if not "!p_core_list!"=="" echo   P-Cores: !p_core_list!
    if not "!e_core_list!"=="" echo   E-Cores: !e_core_list!
) else if "%HT_STATUS%"=="Enabled" (
    echo.
    echo   Physical Cores: %core_list%
    echo   Threads:       %thread_list%
)

echo.
echo   Press any key to exit...
pause >nul
