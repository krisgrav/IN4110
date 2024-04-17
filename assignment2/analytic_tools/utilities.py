"""Module containing functions used to achieve the desired restructuring of the pollution_data directory
"""
# Include the necessary packages here
from pathlib import Path
from typing import Dict, List, Union
import shutil
import os


def get_diagnostics(dir: str | Path) -> Dict[str, int]:
    """Get diagnostics for the directory tree, with root directory pointed to by dir.
       Counts up all the files, subdirectories, and specifically .csv, .txt, .npy, .md and other files in the whole directory tree.

    Parameters:
        dir (str or pathlib.Path) : Absolute path to the directory of interest

    Returns:
        res (Dict[str, int]) : a dictionary of the findings with following keys: files, subdirectories, .csv files, .txt files, .npy files, .md files, other files.

    """
    res = {
        "files": 0,
        "subdirectories": 0,
        ".csv files": 0,
        ".txt files": 0,
        ".npy files": 0,
        ".md files": 0,
        "other files": 0,
    }

    dir_path = try_directory_path(dir)

    contents = list(dir_path.rglob("*"))

    for path in contents[1:]:
        if path.is_file():
            res["files"] += 1
            file_ext = path.suffix.lower()
            if file_ext == ".csv":
                res[".csv files"] += 1
            elif file_ext == ".txt":
                res[".txt files"] += 1
            elif file_ext == ".npy":
                res[".npy files"] += 1
            elif file_ext == ".md":
                res[".md files"] += 1
            else:
                res["other files"] += 1
        elif path.is_dir():
            res["subdirectories"] += 1
    return res


def display_diagnostics(dir: str | Path, contents: Dict[str, int]) -> None:
    """Display diagnostics for the directory tree, with root directory pointed to by dir.
        Objects to display: files, subdirectories, .csv files, .txt files, .npy files, .md files, other files.

    Parameters:
        dir (str or pathlib.Path) : Absolute path the directory of interest
        contents (Dict[str, int]) : a dictionary of the same type as return type of get_diagnostics, has the form:

            .. highlight:: python
            .. code-block:: python

                {
                    "files": 0,
                    "subdirectories": 0,
                    ".csv files": 0,
                    ".txt files": 0,
                    ".npy files": 0,
                    ".md files": 0,
                    "other files": 0,
                }

    Returns:
        None
    """
    dir_path = try_directory_path(dir)
    if not type(contents) == dict:
        raise TypeError("Expected argument is Dict[str, int]")
    print(f"\nDiagnostics for {dir_path}:")
    print("-" * 20)
    for key, value in contents.items():
        print(f"Number of {key}: {value}")
    print("-" * 20)


def display_directory_tree(dir: str | Path, maxfiles: int = 3) -> None:
    """Display a directory tree, with root directory pointed to by dir.
       Limit the number of files to be displayed for convenience to maxfiles.
       This tree is built with inspiration from the code written by "Flimm" at https://stackoverflow.com/questions/6639394/what-is-the-python-way-to-walk-a-directory-tree

    Parameters:
        dir (str or pathlib.Path) : Absolute path to the directory of interest
        maxfiles (int) : Maximum number of files to be displayed at each level in the tree, default to three.

    Returns:
        None

    """
    dir_path = try_directory_path(dir)
    if type(maxfiles) != int:
        raise TypeError("Expected argument is Integer")
    if maxfiles < 1:
        raise ValueError("Argument must be more than 1")
    
    print_dir(dir_path, maxfiles)

              
def is_gas_csv(path: str | Path) -> bool:
    """Checks if a csv file pointed to by path is an original gas statistics file.
        An original file must be called '[gas_formula].csv' where [gas_formula] is
        in ['CO2', 'CH4', 'N2O', 'SF6', 'H2'].

    Parameters:
         - path (str of pathlib.Path) : Absolute path to .csv file that will be checked

    Returns
         - (bool) : Truth value of whether the file is an original gas file
    """
    try:
        file_path = Path(path)
    except TypeError as te:
        raise TypeError(f"Invalid argument type: {str(te)}. You must provide a valid path-like object.")
    if not file_path.suffix.lower() == ".csv":
        raise ValueError(f"Expected .csv-file but got - {file_path.stem + file_path.suffix}")
    
    gasses = ["CO2", "CH4", "N2O", "SF6", "H2"]
    if file_path.stem.upper() in gasses:
        return True
    return False

        
def get_dest_dir_from_csv_file(dest_parent: str | Path, file_path: str | Path) -> Path:
    """Given a file pointed to by file_path, derive the correct gas_[gas_formula] directory name.
        Checks if a directory "gas_[gas_formula]", exists and if not, it creates one as a subdirectory under dest_parent.

        The file pointed to by file_path must be a valid file. A valid file must be called '[gas_formula].csv' where [gas_formula]
        is in ['CO2', 'CH4', 'N2O', 'SF6', 'H2'].

    Parameters:
        - dest_parent (str or pathlib.Path) : Absolute path to parent directory where gas_[gas_formula] should/will exist
        - file_path (str or pathlib.Path) : Absolute path to file that gas_[gas_formula] directory will be derived from

    Returns:
        - (pathlib.Path) : Absolute path to the derived directory

    """
    dest_parent = try_directory_path(dest_parent)
    try:
        file_path = Path(file_path)
    except TypeError as te:
        raise TypeError(f"Invalid argument type: {str(te)}. You must provide a valid path-like object.")
    if not file_path.suffix.lower() == ".csv":
        raise ValueError(f"Expected .csv-file but got: {file_path.stem + file_path.suffix}")
    if not is_gas_csv(file_path):
        raise ValueError(f"Argument file_path does not point to a original file but {file_path.name}")

    dest_name = "gas_" + file_path.stem
    dest_path = Path(dest_parent / dest_name)

    if dest_path.exists():
        return dest_path
    else:
        dest_path.mkdir()
        return dest_path


def merge_parent_and_basename(path: str | Path) -> str:
    """This function merges the basename and the parent-name of a path into one, uniting them with "_" character.
       It then returns the basename of the resulting path.

    Parameters:
        - path (str or pathlib.Path) : Absolute path to modify

    Returns:
        - new_base (str) : New basename of the path
    """
    try:
        file_path = Path(path)
    except TypeError as te:
        raise TypeError(f"Invalid argument type: {str(te)}. You must provide a valid path-like object.")
    if not file_path.name or not file_path.parent.name:
        raise ValueError("Path must have both a filename and a parent directory.")

    new_base = f"{file_path.parent.name}_{file_path.stem}"
    return new_base


def delete_directories(path_list: List[str | Path]) -> None:
    """Prompt the user for permission and delete the objects pointed to by the paths in path_list if
       permission is given. If the object is a directory, its whole directory tree is removed.

    Parameters:
        - path_list (List[str | Path]) : a list of absolute paths to all the objects to be removed.


    Returns:
    None
    """
    print("The following directories will be deleted:\n")
    for dir_path in path_list:
        print(f"- {dir_path}\n")

    user_input = input("Do you want to proceed? (y/n): ").lower()
    if user_input != "y":
        print("Deletion aborted.")
        return

    for dir_path in path_list:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Deleted directory: {dir_path}\n")


def try_directory_path(dir: str | Path) -> Path:
    """
    Try to convert the provided argument to a valid directory path, and perform validation checks.

    Parameters:
        dir (str or Path): The argument to convert to a directory path.

    Returns:
        Path: A valid directory path object.

    Raises:
        TypeError: If the provided argument is not a valid path-like object.
        NotADirectoryError: If the specified path does not exist or is not a directory.
    """
    try:
        dir_path = Path(dir)
    except TypeError as te:
        raise TypeError(f"Invalid argument type: {str(te)}. You must provide a valid path-like object.")
    #Check if the spesified path exists
    if not dir_path.exists():
            raise NotADirectoryError(f"The specified path '{dir}' does not exist.")
    # Check if the specified path is a directory
    if not dir_path.is_dir():
        raise NotADirectoryError(f"The specified path '{dir}' is not a directory.")
    return dir_path


def print_dir(dir_path: Path, maxfiles: int, level: int = 0) -> None:
    """
    Recursively print the directory tree with a specified maximum number of files to display per directory.

    Parameters:
        dir_path (Path): The path to the directory to start printing from.
        maxfiles (int): The maximum number of files to display in each directory.
        level (int, optional): The current level of recursion, used for indentation. Defaults to 0.

    Returns:
        None
    """
    if(level == 0):
        print(dir_path.name + "/")
    level += 1
    prefix = "    " * level
    directory = list(dir_path.iterdir())
    directory.sort(key=lambda entry: entry.name)
    files_displayed = 0
    for entry in directory:
        if( entry.is_dir()):
            print(prefix + entry.name + "/")
            print_dir(entry, maxfiles, level)
    for entry in directory:
        if(entry.exists() and entry.is_file()):
            if(files_displayed < maxfiles and entry.exists()):
                print(prefix + "- " +entry.name)
                files_displayed += 1
            elif(files_displayed == maxfiles and entry.exists()):
                print(prefix + "...( more files)")
                files_displayed = 0
                break


def list_subdirectories(dir: str | Path) -> List[Union[str, Path]]:
    """Get a list of all subdirectories as Path objects within the specified directory.

    Parameters:
        path (str or pathlib.Path): The path to the directory to search for subdirectories.

    Returns:
        List[pathlib.Path]: A list of pathlib.Path objects representing the subdirectories.

    """
    dir_path = try_directory_path(dir)
    subdirectories = []
    for dir_path, dir_names, _ in os.walk(dir_path):
        subdirectories.extend([Path(dir_path) / dir_name for dir_name in dir_names])
    return subdirectories