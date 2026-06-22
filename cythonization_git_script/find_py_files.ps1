param (
    [string]$directory_path
)

if (-not $directory_path) {
    Write-Error "Usage: find_py_files.ps1 <directory_path>"
    exit 1
}

if (-not (Test-Path $directory_path -PathType Container)) {
    Write-Error "Error: '$directory_path' is not a valid directory."
    exit 1
}

$py_files = Get-ChildItem -Recurse -File -Path $directory_path -Filter '*.py' |
    Select-Object -ExpandProperty FullName

$py_files -join [Environment]::NewLine
