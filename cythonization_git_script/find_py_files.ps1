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



# Find and collect all .py files in the provided directory and its subdirectories
$py_files = Get-ChildItem -Recurse -File -Path $directory_path -Filter '*.py' | ForEach-Object {
    $_.FullName
}

# Join the array elements into a single string with null separators
$py_files_string = $py_files -join [Environment]::NewLine
Write-Error $py_files_string
