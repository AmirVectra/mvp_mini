param (
    [string]$directory_path
)

if (-not $directory_path) {
    Write-Error "Usage: get_pyd_file_paths.ps1 <directory_path>"
    exit 1
}

if (-not (Test-Path $directory_path -PathType Container)) {
    Write-Error "Error: '$directory_path' is not a valid directory."
    exit 1
}

$pyd_files = Get-ChildItem -Recurse -File -Path $directory_path -Filter '*.pyd' |
    Select-Object -ExpandProperty FullName

$pyd_files -join [Environment]::NewLine
