"""This is the mane script orchestrating the restructuring and plotting of the content of the pollution_data directory.
"""

# Import necessary packages here
from pathlib import Path
import shutil
import os
import tempfile

from analytic_tools.utilities import (
    display_directory_tree,
    is_gas_csv,
    try_directory_path,
    get_dest_dir_from_csv_file,
    merge_parent_and_basename,   
    delete_directories
)

from analytic_tools.plotting import (
    plot_pollution_data
)


def restructure_pollution_data(pollution_dir: str | Path, dest_dir: str | Path) -> None:
    """This function searches the tree of pollution_data directory pointed to by pollution_dir for .csv files
        that satisfy the criteria described in the assignment. It then moves a renamed copy of these files to gas-specific
        sub-directories in dest_dir, which will be created based on the gasses present in pollution_data directory.

    Parameters:
        - pollution_dir (str or pathlib.Path) : The absolute path to pollution_data directory
        - dest_dir (str or pathlib.Path) : The absolute path to new directory where gas-specific subdirectories will
                                     be created, which must be pollution_data_restructured/by_gas

    Returns:
    None

    Pseudocode:
    1. Iterate through the contents of `pollution_dir`
    2. Find valid .csv files for gasses ([`[gas_formula].csv` files of correct gas types).
    3. Create/assign new directory to store them under `dest_dir` using `get_dest_dir_from_csv_file`
    4. Assign a new name using `merge_parent_and_basename` and copy the file to the new destination.
       If the file happens already to exist there, it should be overwritten.
    """
    pollution_dir = try_directory_path(pollution_dir)
    dest_dir = try_directory_path(dest_dir)

    contents = list(pollution_dir.rglob("*"))

    for path in contents:
        try:
            result = is_gas_csv(path)
        except Exception:
            result = None
        if result:
            new_dir = get_dest_dir_from_csv_file(dest_dir, path)
            new_name = (merge_parent_and_basename(path) + ".csv")
            shutil.copy2(path, Path(new_dir / new_name))
        

def analyze_pollution_data(work_dir: str | Path) -> None:
    """Do the restructuring of the pollution_data and plot
       the statistics showing emissions of each gas as function of all the corresponding
       sources. The new structure and the plots are saved in a separate directory under work_dir

    Parameters:
        - work_dir (str or pathlib.Path) : Absolute path to the working directory that
                                    contains the pollution_data directory and where the new directories will be created

    Returns:
    None

    Pseudocode:
    - Create pollution_data_restructured in work_dir
    - Populate it with a by_gas subdirectory
    - Make a call to restructure_pollution_data
    - Populate pollution_data_restructured with a subdirectory named figures
    - Make a call to plot_pollution_data
    """
    work_dir = try_directory_path(work_dir)

    pollution_dir = Path(work_dir / "pollution_data")
    restructured_dir = Path(work_dir / "pollution_data_restructured")
    restructured_dir.mkdir(parents=False, exist_ok=True)

    by_gas_dir = Path(restructured_dir / "by_gas")
    by_gas_dir.mkdir(parents=False, exist_ok=True)

    restructure_pollution_data(pollution_dir, by_gas_dir)

    figures_dir = Path(restructured_dir / "figures")
    figures_dir.mkdir(parents=False, exist_ok=True)

    plot_pollution_data(by_gas_dir, figures_dir)


def analyze_pollution_data_tmp(work_dir: str | Path) -> None:
    """Do the restructuring of the pollution_data in a temporary directory and create the figures
       showing emissions of each gas as function of all the corresponding
       sources. The new figures are saved in a real directory under work_dir.

    Parameters:
        - work_dir (str or pathlib.Path) : Absolute path to the working directory that
                                    contains the pollution_data directory and where the figures will be saved

    Returns:
    None

    Pseudocode:
    - Create a temporary directory and copy pollution_data directory to it
    - Perform the same operations as in analyze_pollution_data
    - Copy (or directly save) the figures to a directory named `figures` under the original working directory pointed to by `work_dir`
    """
    work_dir = try_directory_path(work_dir)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        pollution_data_dir = Path(work_dir / "pollution_data")
        shutil.copytree(pollution_data_dir, temp_dir / "pollution_data")

        restructured_dir = temp_dir / "pollution_data_restructured"
        restructured_dir.mkdir(parents=False, exist_ok=True)

        by_gas_dir = restructured_dir / "by_gas"
        by_gas_dir.mkdir(parents=False, exist_ok=True)

        restructure_pollution_data(temp_dir / "pollution_data", by_gas_dir)

        figures_dir = restructured_dir / "figures"
        figures_dir.mkdir(parents=False, exist_ok=True)

        plot_pollution_data(by_gas_dir, figures_dir)

        work_figures_dir = work_dir / "figures"
        work_figures_dir.mkdir(parents=False, exist_ok=True)
        for figure in figures_dir.iterdir():
            if figure.suffix == ".png":
                shutil.copy(figure, work_figures_dir)


if __name__ == "__main__":
    work_dir = "/Users/kristiangravermoen/Kode/IN3110-privatefork/assignment2"
    pollution_restructured = work_dir + os.sep + "pollution_data_restructured"
    
    analyze_pollution_data(work_dir)
    display_directory_tree(work_dir)
    delete_directories([Path(work_dir + os.sep + "pollution_data_restructured")])