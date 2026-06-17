import subprocess
import shutil
import os


def get_py_files_path(script_path, src_dir_path):
    """Execute a PowerShell script and return Python file paths."""
    command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path, src_dir_path]
    completed_process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    return completed_process.stdout.splitlines()


def get_pyd_files_path(script_path_pyd_files, src_dir_path):
    """Execute a PowerShell script and return .pyd file paths."""
    command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path_pyd_files, src_dir_path]
    completed_process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    return completed_process.stdout.splitlines()


def get_non_py_files_path(script_path, src_dir_path):
    """Execute a PowerShell script and return non-Python file paths."""
    command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path, src_dir_path]
    completed_process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

    return completed_process.stdout.splitlines()


def get_exclude_py_files_path(list_py_files_path, list_exclude_files_name):
    """Return Python files that should be excluded from cythonization."""
    list_exclude_py_file_path = []
    for path in list_py_files_path:
        file_name = os.path.basename(path)
        if file_name in list_exclude_files_name:
            list_exclude_py_file_path.append(path)

    return list_exclude_py_file_path


def get_modified_path(path_str, src_package_name, target_folder, prefix_output_path):
    """Build the destination path while preserving relative structure."""

    index = path_str.find(src_package_name)
    if index == -1:
        return None
    relative_path = path_str[index + len(src_package_name):]
    return (prefix_output_path + "/" + os.path.join(target_folder, relative_path))


def start_cythonization(list_py_files_dir, exclude_files_name):
    """Compile Python files using Cython."""

    for path in list_py_files_dir:
        file_name = os.path.basename(path)
        if file_name in exclude_files_name:
            continue
        command = ["cythonize", "-i", path]
        completed_process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        if completed_process.returncode != 0: raise RuntimeError(f"Failed to compile {path}\\n{completed_process.stderr}")


def move_pyd_files(list_pyd_files_path, src_package_name, target_package_name, prefix_output_path):
    """Copy generated .pyd files into the target package."""

    for file in list_pyd_files_path:
        if not file.strip():
            continue
        path_to_move_file = get_modified_path(file, src_package_name, target_package_name, prefix_output_path)
        if path_to_move_file is None:
            continue
        os.makedirs(os.path.dirname(path_to_move_file), exist_ok=True)
        shutil.copy2(file, path_to_move_file)


def move_non_py_files(list_non_py_files_path, src_package_name, target_package_name, prefix_output_path):
    """Copy non-Python resource files."""

    for file in list_non_py_files_path:
        path_to_move_file = get_modified_path(file, src_package_name, target_package_name, prefix_output_path)
        if path_to_move_file is None:
            continue
        os.makedirs(os.path.dirname(path_to_move_file), exist_ok=True)
        shutil.copy(file, path_to_move_file)


def move_excluded_py_files(list_path_exclude_py, src_package_name, target_package_name, prefix_output_path):
    """Copy excluded Python files unchanged."""

    for file in list_path_exclude_py:
        path_to_move_file = get_modified_path(file, src_package_name, target_package_name, prefix_output_path)
        if path_to_move_file is None:
            continue
        os.makedirs(os.path.dirname(path_to_move_file), exist_ok=True)
        shutil.copy(file, path_to_move_file)


def delete_files_with_extensions(directory, extensions):
    """Delete generated files with specified extensions."""
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(extensions):
                file_path = os.path.join(root, filename)
                os.remove(file_path)


def main():
    """
    Execute the complete cythonization workflow.
    """

    src_root_dir = "mvp_lite_root"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    src_dir_path = os.path.join(project_root, src_root_dir)

    src_package_name = "mvp_lite_root"
    target_package_name = "cythonized_package"

    script_path_py_files = os.path.join(script_dir, "find_py_files.ps1")

    script_path_pyd_files = os.path.join(script_dir, "get_pyd_file_paths.ps1")
    script_path_non_py_files = os.path.join(script_dir, "non_py_files.ps1")
    exclude_py_files_name = ["__init__.py","setup.py", "mvp_lite_main.py"]
    prefix_output_path = ("./new_cythonized_package/" + src_package_name)
    file_extensions_to_delete = (".c", ".pyd")
    list_path_py_files = get_py_files_path(script_path_py_files, src_dir_path)
    list_path_non_py_files = get_non_py_files_path(script_path_non_py_files, src_dir_path)
    list_path_exclude_py = get_exclude_py_files_path(list_path_py_files, exclude_py_files_name)
    start_cythonization(list_path_py_files, exclude_py_files_name)
    list_pyd_files_path = get_pyd_files_path(script_path_pyd_files, src_dir_path)
    move_pyd_files(list_pyd_files_path, src_package_name, target_package_name, prefix_output_path)
    move_non_py_files(list_path_non_py_files, src_package_name, target_package_name, prefix_output_path)
    move_excluded_py_files(list_path_exclude_py, src_package_name, target_package_name, prefix_output_path)
    delete_files_with_extensions(src_dir_path, file_extensions_to_delete)


if __name__ == "__main__":
    main()
