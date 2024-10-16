# Check if there is an upgrade in progress
if (Test-Path ".\upgrade\upgrade_in_progress") {
    write-output "$(Get-Date -format u) - There is an upgrade in progress. Aborting..." >> .\upgrade\upgrade.log
    exit 1
}

write-output "0" | out-file ".\upgrade\upgrade_in_progress" -encoding ascii

# Delete previous upgrade.log
Remove-Item -Path ".\upgrade\upgrade.log" -ErrorAction SilentlyContinue

# Select powershell
if (Test-Path "$env:windir\sysnative") {
    write-output "$(Get-Date -format u) - Sysnative Powershell will be used to access the registry." >> .\upgrade\upgrade.log
    Set-Alias Start-NativePowerShell "$env:windir\sysnative\WindowsPowerShell\v1.0\powershell.exe"
} else {
    Set-Alias Start-NativePowerShell "$env:windir\System32\WindowsPowerShell\v1.0\powershell.exe"
}


function remove_upgrade_files {
    Remove-Item -Path ".\upgrade\*"  -Exclude "*.log", "upgrade_result" -ErrorAction SilentlyContinue
    Remove-Item -Path ".\securics-agent*.msi" -ErrorAction SilentlyContinue
    Remove-Item -Path ".\do_upgrade.ps1" -ErrorAction SilentlyContinue
}


function get_securics_installation_directory {
    Start-NativePowerShell {
        $path1 = "HKLM:\SOFTWARE\WOW6432Node\Securics, Inc.\Securics Agent"
        $key1 = "SecuricsInstallDir"

        $path2 = "HKLM:\SOFTWARE\WOW6432Node\ossec"
        $key2 = "Install_Dir"

        $SecuricsInstallDir = $null

        try {
            $SecuricsInstallDir = (Get-ItemProperty -Path $path1 -ErrorAction SilentlyContinue).$key1
        }
        catch {
            $SecuricsInstallDir = $null
        }

        if ($null -eq $SecuricsInstallDir) {
            try {
                $SecuricsInstallDir = (Get-ItemProperty -Path $path2 -ErrorAction SilentlyContinue).$key2
            }
            catch {
                $SecuricsInstallDir = $null
            }
        }

        if ($null -eq $SecuricsInstallDir) {
            Write-output "$(Get-Date -format u) - Couldn't find Securics in the registry. Upgrade will assume current path is correct" >> .\upgrade\upgrade.log
            $SecuricsInstallDir = (Get-Location).Path.TrimEnd('\')
        }

        return $SecuricsInstallDir
    }
}

# Check process status
function check-process
{
    $process_id = (Get-Process securics-agent).id
    $counter = 10
    while($process_id -eq $null -And $counter -gt 0)
    {
        $counter--
        Start-Service -Name "Securics"
        Start-Sleep 2
        $process_id = (Get-Process securics-agent).id
    }
    write-output "$(Get-Date -format u) - Process ID: $($process_id)." >> .\upgrade\upgrade.log
}

# Check new version and restart the Securics service
function check-installation
{
    $new_version = (Get-Content VERSION)
    $counter = 5
    while($new_version -eq $current_version -And $counter -gt 0)
    {
        write-output "$(Get-Date -format u) - Waiting for the Securics-Agent installation to end." >> .\upgrade\upgrade.log
        $counter--
        Start-Sleep 2
        $new_version = (Get-Content VERSION)
    }
    write-output "$(Get-Date -format u) - Restarting Securics-Agent service." >> .\upgrade\upgrade.log
    Get-Service -Name "Securics" | Start-Service
}

# Stop UI and launch the msi installer
function install
{
    kill -processname win32ui -ErrorAction SilentlyContinue -Force
    Remove-Item .\upgrade\upgrade_result -ErrorAction SilentlyContinue
    write-output "$(Get-Date -format u) - Starting upgrade process." >> .\upgrade\upgrade.log
    cmd /c start /wait (Get-Item ".\securics-agent*.msi").Name -quiet -norestart -log installer.log
}

# Check that the Securics installation runs on the expected path
$securicsDir = get_securics_installation_directory
$normalizedSecuricsDir = $securicsDir.TrimEnd('\')
$currentDir = (Get-Location).Path.TrimEnd('\')

if ($normalizedSecuricsDir -ne $currentDir) {
    Write-Output "$(Get-Date -format u) - Current working directory is not the Securics installation directory. Aborting." >> .\upgrade\upgrade.log
    Write-output "2" | out-file ".\upgrade\upgrade_result" -encoding ascii
    remove_upgrade_files
    exit 1
}

# Get current version
$current_version = (Get-Content VERSION)
write-output "$(Get-Date -format u) - Current version: $($current_version)." >> .\upgrade\upgrade.log

# Ensure no other instance of msiexec is running by stopping them
Get-Process msiexec | Stop-Process -ErrorAction SilentlyContinue -Force

# Install
install
check-installation

write-output "$(Get-Date -format u) - Installation finished." >> .\upgrade\upgrade.log

check-process

# Wait for agent state to be cleaned
Start-Sleep 10

# Check status file
function Get-AgentStatus {
    Select-String -Path '.\securics-agent.state' -Pattern "^status='(.+)'" | %{$_.Matches[0].Groups[1].value}
}

$status = Get-AgentStatus
$counter = 30
while($status -ne "connected"  -And $counter -gt 0)
{
    $counter--
    Start-Sleep 2
    $status = Get-AgentStatus
}
Write-Output "$(Get-Date -Format u) - Reading status file: status='$status'." >> .\upgrade\upgrade.log

If ($status -ne "connected")
{
    write-output "$(Get-Date -format u) - Upgrade failed." >> .\upgrade\upgrade.log
    write-output "2" | out-file ".\upgrade\upgrade_result" -encoding ascii
}
Else
{
    write-output "0" | out-file ".\upgrade\upgrade_result" -encoding ascii
    write-output "$(Get-Date -format u) - Upgrade finished successfully." >> .\upgrade\upgrade.log
    $new_version = (Get-Content VERSION)
    write-output "$(Get-Date -format u) - New version: $($new_version)." >> .\upgrade\upgrade.log
}

remove_upgrade_files

exit 0
