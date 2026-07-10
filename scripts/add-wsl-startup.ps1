$wsShell = New-Object -ComObject WScript.Shell
$startup = $wsShell.SpecialFolders("Startup")
$shortcut = $wsShell.CreateShortcut($startup + "\WSL Ubuntu.lnk")
$shortcut.TargetPath = "wsl.exe"
$shortcut.Arguments = "-d Ubuntu-24.04"
$shortcut.Description = "Starter WSL Ubuntu ved Windows-pålogging"
$shortcut.WindowStyle = 7
$shortcut.Save()

Write-Host "✅ Snarvei opprettet i startup-mappe: $startup"
Get-ChildItem $startup | Format-Table Name
