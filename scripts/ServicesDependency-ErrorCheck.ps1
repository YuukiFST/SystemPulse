$services = Get-WmiObject -Class Win32_Service

foreach ($service in $services) {
    if ($service.StartMode -ne "Disabled") {
        continue
    }

    $dependentServices = Get-Service -Name $service.Name -DependentServices

    foreach ($dependentService in $dependentServices) {
        $serviceStartValue = (Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\$($dependentService.Name)").Start

        $isDisabled = $serviceStartValue -eq 4

        if (-not $isDisabled) {
            Write-Host "$($dependentService.Name) ($($serviceStartValue)) depends on $($service.Name) (4)"
        }
    }
}
Write-Host "You have no service dependency errors (No output = Good)"
Read-Host -Prompt "Press any key to continue"
