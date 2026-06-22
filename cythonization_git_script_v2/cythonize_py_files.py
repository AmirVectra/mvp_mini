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


def get_modified_path(path_str, src_package_name, prefix_output_path):
    """
    Rewrite a path so that everything from /<src_package_name>/ onward
    is placed under prefix_output_path/<src_package_name>/...
    Works for both src paths and build/lib.*/ paths.
    """
    path_str = path_str.replace("\\", "/")
    marker = "/" + src_package_name + "/"
    index = path_str.find(marker)
    if index != -1:
        relative = path_str[index + 1:]          # keeps "mvp_lite/subpkg/file.pyd"
        return prefix_output_path + "/" + relative
    print(f"[WARN] Could not find '{src_package_name}' in path: {path_str}")
    return None


def generate_setup_py(list_py_files, exclude_files_name, src_dir_path, setup_out_path):
    """
    Dynamically generate a setup.py for Cython 3.x / Python 3.13.
    Compiles into build/lib.*/ (no --inplace) to avoid CWD path issues on CI.
    """
    extensions = []
    for path in list_py_files:
        fname = os.path.basename(path)
        if fname not in exclude_files_name:
            abs_path = os.path.abspath(path).replace("\\", "/")
            abs_src  = os.path.abspath(src_dir_path).replace("\\", "/")
            src_parent = os.path.dirname(abs_src)          # .../src
            rel = os.path.relpath(abs_path, src_parent).replace("\\", "/")
            module_name = rel.replace("/", ".").removesuffix(".py")
            extensions.append((module_name, abs_path))

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
        "        nthreads=0,",   # single-threaded — avoids BrokenProcessPool on Windows CI
        "    ),",
        ")",
        "",
    ]
    with open(setup_out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"[INFO] Generated {setup_out_path}")


def start_cythonization(setup_py_path):
    print("---------- Cythonization via setup.py ----------")
    # No --inplace: .pyd files land in build/lib.win-amd64-cpython-3XX/
    # --inplace would try to copy to a 'mvp_lite/' folder at CWD (repo root)
    # which does not exist, causing "No such file or directory".
    command = [sys.executable, setup_py_path, "build_ext"]
    result = subprocess.run(command, text=True)
    if result.returncode != 0:
        print("[ERROR] Cythonization failed — check output above.")
        sys.exit(1)
    print("[INFO] Cythonization complete.")


def get_pyd_files_from_build():
    """
    Collect .pyd files from build/lib.*/ after setup.py build_ext (no --inplace).
    """
    build_dir = "./build"
    pyd_files = []
    if not os.path.exists(build_dir):
        print("[WARN] build/ directory not found after cythonization.")
        return pyd_files
    for root, _, files in os.walk(build_dir):
        for f in files:
            if f.endswith(".pyd"):
                pyd_files.append(os.path.join(root, f).replace("\\", "/"))
    print(f"[INFO] Found {len(pyd_files)} .pyd files in build/")
    return pyd_files


def build_wheel(src_dir_path, wheel_out_dir):
    """
    Build a wheel from the package using pip wheel.
    Runs from the mvp_lite_root directory (parent of src/).
    Requires a pyproject.toml or setup.cfg there.
    """
    print("---------- Building wheel ----------")
    os.makedirs(wheel_out_dir, exist_ok=True)
    # mvp_lite_root = parent of src/ = grandparent of mvp_lite/
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


def move_files(file_list, src_package_name, prefix_output_path):
    for file in file_list:
        dest = get_modified_path(file, src_package_name, prefix_output_path)
        if dest is None:
            print(f"[SKIP] Cannot determine destination for: {file}")
            continue
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(file, dest)
            print(f"[COPY] {file}  ->  {dest}")
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

    exclude_py_files_name  = ["main.py", "setup.py", "mvp_lite_main.py"]
    file_extensions_to_delete = (".c",)      # .pyd is in build/, not src/

    prefix_output_path = "./" + cythonized_package_name
    script_folder  = "./cythonization_git_script"
    setup_py_path  = script_folder + "/_generated_setup.py"

    script_py  = script_folder + "/find_py_files.ps1"
    script_non = script_folder + "/non_py_files.ps1"

    # --- Collect source file lists ---
    list_path_py_files     = get_py_files_path(script_py, src_dir_path)
    list_path_non_py_files = get_non_py_files_path(script_non, src_dir_path)
    list_path_exclude_py   = get_exclude_py_files_path(list_path_py_files, exclude_py_files_name)

    # --- Cythonize ---
    generate_setup_py(list_path_py_files, exclude_py_files_name, src_dir_path, setup_py_path)
    start_cythonization(setup_py_path)

    # --- Collect .pyd files from build/ ---
    list_pyd_files_path = get_pyd_files_from_build()

    # --- Copy everything to compiled_package/ ---
    print("---------- Moving pyd files ----------")
    move_files(list_pyd_files_path,    src_package_name, prefix_output_path)
    print("---------- Moving non-py files ----------")
    move_files(list_path_non_py_files, src_package_name, prefix_output_path)
    print("---------- Moving excluded py files ----------")
    move_files(list_path_exclude_py,   src_package_name, prefix_output_path)

    # --- Build wheel ---
    build_wheel(src_dir_path, wheel_out_dir)

    # --- Cleanup ---
    delete_files_with_extensions(src_dir_path, file_extensions_to_delete)
    if os.path.exists(setup_py_path):
        os.remove(setup_py_path)
        print(f"[DELETE] {setup_py_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cythonize a Python package and build a wheel")
    parser.add_argument("arg1", help="Path to the package to cythonize  (e.g. ./mvp_lite_root/src/mvp_lite)")
    parser.add_argument("arg2", help="Package name                       (e.g. mvp_lite)")
    parser.add_argument("arg3", help="Cythonized output folder name      (e.g. compiled_package)")
    parser.add_argument("arg4", help="Wheel output directory             (e.g. ./dist)")
    args = parser.parse_args()
    print("Args:", args.arg1, args.arg2, args.arg3, args.arg4)
    main(args.arg1, args.arg2, args.arg3, args.arg4)