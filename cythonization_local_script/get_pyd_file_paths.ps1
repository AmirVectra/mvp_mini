param (
    [string]$directory_path
)

# Check if the directory path is provided as an argument
if (-not $directory_path) {
    Write-Host "Usage: $([System.IO.Path]::GetFileNameWithoutExtension($MyInvocation.MyCommand.Name)) <directory_path>"
    exit 1
}

# Check if the provided path is a valid directory
if (-not (Test-Path $directory_path -PathType Container)) {
    Write-Host "Error: '$directory_path' is not a valid directory."
    exit 1
}

# Find and collect all .py files in the provided directory and its subdirectories
$py_files = Get-ChildItem -Recurse -File -Path $directory_path -Filter '*.pyd' | ForEach-Object {
    $_.FullName
}

# Join the array elements into a single string with null separators
$py_files_string = $py_files -join [Environment]::NewLine
Write-Host $py_files_string
