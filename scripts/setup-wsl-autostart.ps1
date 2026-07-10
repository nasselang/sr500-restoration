# Setup WSL + OpenClaw auto-start on Windows boot
# Run this in PowerShell as Administrator

$taskName = "Start WSL Ubuntu"
$description = "Starter WSL Ubuntu-distro på Windows-oppstart, som trigger OpenClaw Gateway via systemd"

# Create a logon trigger task - runs wsl.exe silently to start the distro
$action = New-ScheduledTaskAction -Execute "wsl.exe" -Argument "-d Ubuntu-24.04 -- cd /home/johnny"
$trigger = New-ScheduledTaskTrigger -AtLogon
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -RunLevel Limited

Register-ScheduledTask -TaskName $taskName `
    -Description $description `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Force

Write-Host "✅ WSL autostart task '$taskName' er opprettet."
Write-Host "   WSL vil starte når du logger på Windows."
Write-Host "   OpenClaw Gateway starter automatisk via systemd inni WSL."
Write-Host ""
Write-Host "📝 Sjekk at tasken finnes:"
Write-Host "   schtasks /Query /TN '$taskName' /V"
