$wmiService = Get-Service -Name Winmgmt -ErrorAction SilentlyContinue
if ($null -eq $wmiService -or $wmiService.Status -ne 'Running') {
    Write-Error "error: WMI Service is Disabled..."
    exit 1
}

function FormatAndPrint {
    param (
        [string]$ClassName,
        [string]$DeviceId,
        [string]$DriverPath
    )
    $fullPath = "HKLM\SYSTEM\CurrentControlSet\Control\Class\$DriverPath"
    Write-Output "$ClassName : $fullPath"
}

$classes = @("Win32_VideoController", "Win32_NetworkAdapter")

foreach ($class in $classes) {
    $devices = Get-CimInstance -ClassName $class | Where-Object { $_.PNPDeviceID -like "PCI\VEN_*" }
    foreach ($device in $devices) {
        $deviceId = $device.PNPDeviceID

        $regPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\$deviceId"
        try {
            $driverValue = Get-ItemProperty -Path $regPath -Name "Driver" -ErrorAction Stop
            $driverPath = $driverValue.Driver
            FormatAndPrint -ClassName $class -DeviceId $deviceId -DriverPath $driverPath
        }
        catch {
            continue
        }
    }
    Write-Output ""
}

Read-Host -Prompt "Press Enter to continue"