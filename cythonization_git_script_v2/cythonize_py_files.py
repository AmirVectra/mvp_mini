import subprocess
import shutil
import os
import argparse
import sys


def get_py_files_path(script_path, src_dir_path):
    print("---------- get py files ----------")
    command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path, src_dir_path]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"[ERROR] find_py_files.ps1 failed:\n{result.stderr}")
        sys.exit(1)
    return [p for p in result.stdout.splitlines() if p.strip()]


def get_pyd_files_path(script_path, src_dir_path):
    print("---------- get pyd files ----------")
    command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path, src_dir_path]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"[ERROR] get_pyd_file_paths.ps1 failed:\n{result.stderr}")
        sys.exit(1)
    return [p for p in result.stdout.splitlines() if p.strip()]


def get_non_py_files_path(script_path, src_dir_path):
    print("---------- get non-py files ----------")
    command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path, src_dir_path]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"[ERROR] non_py_files.ps1 failed:\n{result.stderr}")
        sys.exit(1)
    return [p for p in result.stdout.splitlines() if p.strip()]


def get_exclude_py_files_path(list_py_files_path, list_exclude_files_name):
    result = []
    for path in list_py_files_path:
        if os.path.basename(path) in list_exclude_files_name:
            result.append(path)
    return result


def get_modified_path(path_str, src_package_name, target_folder, prefix_output_path):
    # Normalize to forward slashes for consistent find
    path_str = path_str.replace("\\", "/")
    # Find the package root segment in the path
    marker = "/" + src_package_name + "/"
    index = path_str.find(marker)
    if index != -1:
        relative = path_str[index + len(marker):]
        new_path = prefix_output_path + "/" + target_folder + "/" + relative
        return new_path
    print(f"[WARN] Could not find '{src_package_name}' in path: {path_str}")
    return None


def generate_setup_py(list_py_files, exclude_files_name, src_dir_path, setup_out_path):
    """
    Generate a setup.py that cythonizes all eligible .py files.
    Uses Cython.Build.cythonize — compatible with Python 3.13 + Cython 3.x
    """
    extensions = []
    for path in list_py_files:
        fname = os.path.basename(path)
        if fname not in exclude_files_name:
            # Build dotted module name relative to src_dir_path parent
            abs_path = os.path.abspath(path).replace("\\", "/")
            abs_src  = os.path.abspath(src_dir_path).replace("\\", "/")
            # src_dir_path is the package root, e.g. .../src/mvp_lite
            # we want the module name relative to src parent (.../src)
            src_parent = os.path.dirname(abs_src)
            rel = os.path.relpath(abs_path, src_parent).replace("\\", "/")
            module_name = rel.replace("/", ".").removesuffix(".py")
            extensions.append((module_name, path.replace("\\", "/")))

    lines = [
        "from setuptools import setup",
        "from Cython.Build import cythonize",
        "from setuptools.extension import Extension",
        "",
        "extensions = [",
    ]
    for mod, src in extensions:
        lines.append(f'    Extension("{mod}", [r"{src}"]),')
    lines += [
        "]",
        "",
        "setup(",
        '    name="mvp_lite_cythonized",',
        "    ext_modules=cythonize(",
        "        extensions,",
        '        compiler_directives={"language_level": "3"},',
        "        nthreads=0,",  # 0 = single-threaded; avoids BrokenProcessPool on Windows CI
        "    ),",
        ")",
        "",
    ]
    with open(setup_out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"[INFO] Generated {setup_out_path}")


def start_cythonization(setup_py_path):
    print("---------- Cythonization via setup.py ----------")
    command = [sys.executable, setup_py_path, "build_ext", "--inplace"]
    result = subprocess.run(command, text=True)
    if result.returncode != 0:
        print("[ERROR] Cythonization failed — check output above.")
        sys.exit(1)
    print("[INFO] Cythonization complete.")


def build_wheel(src_dir_path, wheel_out_dir):
    """
    Build a wheel from the cythonized package.
    Expects a pyproject.toml or setup.cfg in src_dir_path parent (repo root).
    """
    print("---------- Building wheel ----------")
    os.makedirs(wheel_out_dir, exist_ok=True)
    # Find the repo root (parent of src/)
    repo_root = os.path.abspath(os.path.join(src_dir_path, "..", ".."))
    command = [
        sys.executable, "-m", "pip", "wheel",
        ".",
        "--no-deps",
        "-w", os.path.abspath(wheel_out_dir),
    ]
    result = subprocess.run(command, cwd=repo_root, text=True)
    if result.returncode != 0:
        print("[ERROR] Wheel build failed — check output above.")
        sys.exit(1)
    print(f"[INFO] Wheel written to: {wheel_out_dir}")


def move_files(file_list, src_package_name, target_package_name, prefix_output_path):
    for file in file_list:
        dest = get_modified_path(file, src_package_name, target_package_name, prefix_output_path)
        if dest is None:
            print(f"[SKIP] Cannot determine destination for: {file}")
            continue
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(file, dest)
            print(f"[COPY] {file}  →  {dest}")
        except OSError as e:
            print(f"[ERROR] {e}")


def delete_files_with_extensions(directory, extensions):
    print(f"---------- Cleaning {extensions} from {directory} ----------")
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(extensions):
                fp = os.path.join(root, filename)
                os.remove(fp)
                print(f"[DELETE] {fp}")


def main(src_dir_path, src_package_name, cythonized_package_name, wheel_out_dir):

    exclude_py_files_name = ["main.py", "setup.py", "mvp_lite_main.py"]
    file_extensions_to_delete = (".c", ".pyd")

    # Output structure:  ./<cythonized_package_name>/<src_package_name>/...
    prefix_output_path = "./" + cythonized_package_name
    setup_py_path = "./cythonization_git_script/_generated_setup.py"

    script_py   = "./cythonization_git_script/find_py_files.ps1"
    script_pyd  = "./cythonization_git_script/get_pyd_file_paths.ps1"
    script_non  = "./cythonization_git_script/non_py_files.ps1"

    list_path_py_files     = get_py_files_path(script_py, src_dir_path)
    list_path_non_py_files = get_non_py_files_path(script_non, src_dir_path)
    list_path_exclude_py   = get_exclude_py_files_path(list_path_py_files, exclude_py_files_name)

    # Generate setup.py and cythonize
    generate_setup_py(list_path_py_files, exclude_py_files_name, src_dir_path, setup_py_path)
    start_cythonization(setup_py_path)

    # Collect generated .pyd files
    list_pyd_files_path = get_pyd_files_path(script_pyd, src_dir_path)

    # Move outputs to cythonized package folder
    print("---------- Moving pyd files ----------")
    move_files(list_pyd_files_path,     src_package_name, src_package_name, prefix_output_path)
    print("---------- Moving non-py files ----------")
    move_files(list_path_non_py_files,  src_package_name, src_package_name, prefix_output_path)
    print("---------- Moving excluded py files ----------")
    move_files(list_path_exclude_py,    src_package_name, src_package_name, prefix_output_path)

    # Build wheel
    build_wheel(src_dir_path, wheel_out_dir)

    # Cleanup .c and .pyd from source
    delete_files_with_extensions(src_dir_path, file_extensions_to_delete)
    # Also clean the generated setup.py
    if os.path.exists(setup_py_path):
        os.remove(setup_py_path)
        print(f"[DELETE] {setup_py_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cythonize a Python package and build a wheel")
    parser.add_argument("arg1", help="Path to the src folder to cythonize  (e.g. ./mvp_lite_root/src/mvp_lite)")
    parser.add_argument("arg2", help="Package name                          (e.g. mvp_lite)")
    parser.add_argument("arg3", help="Cythonized output folder name         (e.g. compiled_package)")
    parser.add_argument("arg4", help="Wheel output directory                (e.g. ./dist)")
    args = parser.parse_args()
    print("Args:", args.arg1, args.arg2, args.arg3, args.arg4)
    main(args.arg1, args.arg2, args.arg3, args.arg4)