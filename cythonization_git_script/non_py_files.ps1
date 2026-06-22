param (
    [string]$directory_path
)

if (-not $directory_path) {
    Write-Error "Usage: non_py_files.ps1 <directory_path>"
    exit 1
}

if (-not (Test-Path $directory_path -PathType Container)) {
    Write-Error "Error: '$directory_path' is not a valid directory."
    exit 1
}

$non_py_files = Get-ChildItem -Recurse -File -Path $directory_path |
    Where-Object { $_.Name -notmatch '\.(py|pyx|pyd|c)$' } |
    Select-Object -ExpandProperty FullName

$non_py_files -join [Environment]::NewLine
