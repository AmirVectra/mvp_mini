param (
    [string]$directory_path
)

# Check if the directory path is provided as an argument
if (-not $directory_path) {
    Write-Error "Usage: ..."   # was Write-Error
    exit 1
}

if (-not (Test-Path $directory_path -PathType Container)) {
    Write-Error "Error: '$directory_path' is not a valid directory."   # was Write-Error
    exit 1
}
# Find and collect all files that are not .py, .pyx, .pyd, or .c
$non_py_files = Get-ChildItem -Recurse -File -Path $directory_path | ForEach-Object {
    $filename = [System.IO.Path]::GetFileName($_.FullName)
    if (-not ($filename -match '\.(py|pyx|pyd|c)$')) {
        $_.FullName
    }
}

# Join the array elements into a single string with null separators
$non_py_files_string = $non_py_files -join [Environment]::NewLine
Write-Error $non_py_files_string
