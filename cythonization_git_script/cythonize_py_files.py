import subprocess
import shutil
import os
import argparse


#list_py_files_dir = []
#list_non_py_files_dir = []
            
def get_py_files_path(script_path, src_dir_path):
    print("----------------------------------------------get py files path-----------------------------------------")
    command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path, src_dir_path]
    completed_process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    return completed_process.stdout.splitlines()
    
def get_pyd_files_path(script_path_pyd_files, src_dir_path):
    print("----------------------------------------------get pyd files path-----------------------------------------")
    command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path_pyd_files, src_dir_path]
    completed_process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    return completed_process.stdout.splitlines()
    
def get_non_py_files_path(script_path, src_dir_path):
    print("----------------------------------------------get non-py files path-----------------------------------------")
    command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path, src_dir_path]
    completed_process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    return completed_process.stdout.splitlines()


def get_exclude_py_files_path(list_py_files_path, list_exclude_files_name):
    list_exclude_py_file_path = []
    for path in list_py_files_path:
        file_name = os.path.basename(path)
        if file_name in list_exclude_files_name:
            list_exclude_py_file_path.append(path)
    return list_exclude_py_file_path

def get_modified_path(path_str, src_package_name, target_folder, prefix_output_path ):
    index = path_str.find(src_package_name)
    if index != -1:
        new_path = prefix_output_path + "/"+ os.path.join( target_folder, path_str[index + len(src_package_name)  : len(path_str)])
        return new_path
    

def start_cythonization(list_py_files_dir, exclude_files_name):
    print("---------------------------------------Cythonization process start---------------------------------------------")
    # Iterate over each py files and cythonized them. 
    for path in list_py_files_dir:
        file_name = os.path.basename(path)
        if not file_name in exclude_files_name:
            command = ["cythonize", "-i", path]
            completed_process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)


def move_pyd_files(list_pyd_files_path, src_package_name, target_package_name,prefix_output_path ):

    print("-------------------------------------Moving files process began-------------------------------------------")
    for file in list_pyd_files_path:
        source_path = file
        path_to_move_file = get_modified_path(file, src_package_name, target_package_name,prefix_output_path)
        #os.makedirs(os.path.dirname(path_to_move_file), exist_ok=True)
        #shutil.copy2(source_path, path_to_move_file)
        # Copy the file
        try:
            os.makedirs(os.path.dirname(path_to_move_file), exist_ok=True)
            shutil.copy(source_path, path_to_move_file)
                
        except OSError as e:
            # Handle the case where the file cannot be copied
            print(f"Error: {e}")
    

def move_non_py_files(list_non_py_files_path, src_package_name, target_package_name, prefix_output_path ):
    print("-----------------------------Moving non py files began-------------------------------")
    for file in list_non_py_files_path:
        source_path = file
        path_to_move_file = get_modified_path(file, src_package_name, target_package_name, prefix_output_path)
        # use path
        #Create the target directory if it doesn't exist
        os.makedirs(os.path.dirname(path_to_move_file), exist_ok=True)
        shutil.copy(source_path, path_to_move_file)


def move_excluded_py_files(list_path_exclude_py, src_package_name, target_package_name, prefix_output_path ):
    print("--------------------------------Moving py files----------------------")
    for file in list_path_exclude_py:
        source_path = file
        path_to_move_file = get_modified_path(file, src_package_name, target_package_name, prefix_output_path)
        #use function
        os.makedirs(os.path.dirname(path_to_move_file), exist_ok=True)
        shutil.copy(source_path, path_to_move_file)

def delete_files_with_extensions(directory, extensions):
    try:
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename.endswith(extensions):
                    file_path = os.path.join(root, filename)
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

   


def main(src_dir_path, src_package_name, cythonized_package_name):

    
    src_dir_path = src_dir_path
    src_package_name = src_package_name
    cythonize_package_name =cythonized_package_name
    
    # Add python files to exclude from cythonization.
    exclude_py_files_name = ["main.py","setup.py"]
    #exclude_py_files_name = lis_exclude_py_files
    #"main.py"

    # Delete extra files generated during cythonization process.
    file_extensions_to_delete = (".c", ".pyd")
    
    prefix_output_path = "./" + cythonize_package_name + "/" + src_package_name
    script_path_pyd_files = "./script_cythonization/get_pyd_file_paths.ps1"
    script_path_py_files = "./script_cythonization/find_py_files.ps1"
    script_path_non_py_files = "./script_cythonization/non_py_files.ps1"
    
    
    
    
    # get the list of Python file names from the source folder.
    list_path_py_files = get_py_files_path(script_path_py_files,src_dir_path)
    
    # get list of path for non python files from source folder.
    list_path_non_py_files = get_non_py_files_path(script_path_non_py_files, src_dir_path)
    
    # get list of path of python files that not to cythonize.
    list_path_exclude_py = get_exclude_py_files_path(list_path_py_files, exclude_py_files_name)
    
    # Start cythonization process on python files.
    start_cythonization(list_path_py_files, exclude_py_files_name)
    
    # get list of paths of cythonized files.
    list_pyd_files_path = get_pyd_files_path(script_path_pyd_files, src_dir_path)
    # move cythonized files from source package to a cythonized package.
    move_pyd_files(list_pyd_files_path, src_package_name, cythonize_package_name, prefix_output_path )
    
    # move non-python files from source package to a cythonized package.  
    move_non_py_files(list_path_non_py_files, src_package_name, cythonize_package_name,prefix_output_path )
    
    # move excluded py files from source package to a cythonized package.
    move_excluded_py_files(list_path_exclude_py, src_package_name, cythonize_package_name,prefix_output_path )
    
    # delete .c and .pyd files from src directory.
    delete_files_with_extensions(src_dir_path, file_extensions_to_delete)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("It cythonize the python packages")
    parser.add_argument('arg1', help = "name of dir (or src folder) to be cythonized")
    parser.add_argument('arg2', help = "name of the package")
    parser.add_argument('arg3', help = "cythonized folder name")
    args = parser.parse_args()
    print("input arguments")
    print(args.arg1, args.arg2, args.arg3)
    
    main(args.arg1, args.arg2, args.arg3)
