""" Test script executing all the necessary unit tests for the functions in analytic_tools/utilities.py module
    which is a part of the analytic_tools package
"""

# Include the necessary packages here
from pathlib import Path
import pytest

# This should work if analytic_tools has been installed properly in your environment
from analytic_tools.utilities import (
    get_dest_dir_from_csv_file,
    get_diagnostics,
    is_gas_csv,
    merge_parent_and_basename,
    display_directory_tree
)


@pytest.mark.task12
def test_get_diagnostics(example_config):
    """Test functionality of get_diagnostics in utilities module

    Parameters:
        example_config (pytest fixture): a preconfigured temporary directory containing the example configuration
                                     from Figure 1 in assignment2.md

    Returns:
    None
    """
    get_diagnostics(example_config)


@pytest.mark.task12
@pytest.mark.parametrize(
    "exception, dir",
    [
        (NotADirectoryError, "Not_a_real_directory"),
        (TypeError, 123),
        (TypeError, False),
        (NotADirectoryError, "/Users/kristiangravermoen/Kode/IN3110-privatefork/assignment2/tests/test_utilities.py")
        # add more combinations of (exception, dir) here
    ],
)
def test_get_diagnostics_exceptions(exception, dir):
    """Test the error handling of get_diagnostics function

    Parameters:
        exception (concrete exception): The exception to raise
        dir (str or pathlib.Path): The parameter to pass as 'dir' to the function

    Returns:
        None
    """
    # Use pytest.raises to catch an exception and assign it to 'e'
    with pytest.raises(exception) as e:
        get_diagnostics(dir)
    # Check if the raised exception matches the expected exception
    # Compare the type of the raised exception (e.value) with the expected exception
    assert type(e.value) == exception, f"Expected exception-type {exception} but got {type(e.value)}"


@pytest.mark.task22
def test_is_gas_csv():
    """
        Test functionality of is_gas_csv from utilities module
        Runs test inside try-except to not terminate program when exception is rised from is_gas_csv

    Parameters:
        None

    Returns:
        None
    """
    test_paths = [
        "directory/co2.csv",
        "directory/CO2.csv",
        "directory/CO2-csv",
        "directory/co2_string.csv",
        "directory/co2string.csv",
        "directory/CO2.TXT",
        "directory/CO2.TXT.csv",
        "directory/co2.CSV",
        "directory/co2.CSV",
        "directory/co2_CSV",
        "directory/CO2.zip",
    ]
    for path in test_paths:
        try:
            result = is_gas_csv(path)
            assert isinstance(result, bool), f"Expected result bool but got {type(result)}"
        except Exception as e:
            print(f"Error occured in '{path}': {e}")
        


@pytest.mark.task22
@pytest.mark.parametrize(
    "exception, path",
    [
        (ValueError, Path(__file__).parent.absolute()),
        (ValueError, Path("directory/subdirectory")),
        (ValueError, Path("directory/c02.txt")),
        (TypeError, 1),
        (TypeError, False),
        (TypeError, Path("directory/c02.txt")),
        (ValueError, 1)
    ],
)
def test_is_gas_csv_exceptions(exception, path):
    """Test the error handling of is_gas_csv function

    Parameters:
        exception (concrete exception): The exception to raise
        path (str or pathlib.Path): The parameter to pass as 'path' to function

    Returns:
        None
    """
    try:
        is_gas_csv(path)
    except Exception as e:
        assert isinstance(e, exception), f"Expected exception {exception} but got {type(e)}"
   

#@pytest.mark.task24
def test_get_dest_dir_from_csv_file(example_config):
    """Test functionality of get_dest_dir_from_csv_file in utilities module.
    Uses a stack to traverse all subfolders and files of example_config and tests get_dest_dir_from_csv_file on files.

    Parameters:
        example_config (pytest fixture): a preconfigured temporary directory containing the example configuration
            from Figure 1 in assignment2.md

    Returns:
        None
    """
    display_directory_tree(example_config)
    stack = [example_config]
    while stack:
        current_dir = stack.pop()
        for item in current_dir.iterdir():
            if item.is_file():
                try:
                    result = get_dest_dir_from_csv_file(example_config, item)
                except Exception as e:
                    result = None
                    print(f"Error occured: {e}\n")
                if result:
                        assert isinstance(result, Path), "Returned element is not a pathlib.Path object"
            elif item.is_dir():
                stack.append(item)
    display_directory_tree(example_config)


@pytest.mark.task24
@pytest.mark.parametrize(
    "exception, dest_parent, file_path",
    [
        (ValueError, Path(__file__).parent.absolute(), "foo.txt"),
        (ValueError, Path(__file__).parent.absolute(), "directory/subdirectory"),
        (ValueError, Path(__file__).parent.absolute(), "C02_ark.csv"),
        (TypeError, False, "foo.txt"),
        (NotADirectoryError, "directory/subdirectory", "co2.csv"),
        (NotADirectoryError, "co2.csv", "co2.csv")
    ],
)
def test_get_dest_dir_from_csv_file_exceptions(exception, dest_parent, file_path):
    """Test the error handling of get_dest_dir_from_csv_file function

    Parameters:
        exception (concrete exception): The exception to raise
        dest_parent (str or pathlib.Path): The parameter to pass as 'dest_parent' to the function
        file_path (str or pathlib.Path): The parameter to pass as 'file_path' to the function

    Returns:
        None
    """
    try:
        get_dest_dir_from_csv_file(dest_parent, file_path)
    except Exception as e:
        assert isinstance(e, exception), f"Expected exception {exception} but got {type(e)}"

@pytest.mark.task26
def test_merge_parent_and_basename():
    """Test functionality of merge_parent_and_basename from utilities module

    Parameters:
        None

    Returns:
        None
    """
    test_paths = [
        "directory/file.txt",
        "directory/subdirectory",
        "file.txt",
        "directory",
        False,
        123
    ]
    for path in test_paths:
        try:
            result = merge_parent_and_basename(path)
        except Exception as e:
            result = None
            print(f"Error occured on path '{path}': {e}\n")
        if result:
            assert isinstance(result, str), f"Expected return-type String, but got {type(result)}\n"


@pytest.mark.task26
@pytest.mark.parametrize(
    "exception, path",
    [
        (TypeError, 33),
        (TypeError, False),
        (ValueError, "file.txt"),
        (ValueError, "directory")
    ],
)
def test_merge_parent_and_basename_exceptions(exception, path):
    """Test the error handling of merge_parent_and_basename function

    Parameters:
        exception (concrete exception): The exception to raise
        path (str or pathlib.Path): The parameter to pass as 'pass' to the function

    Returns:
        None
    """
    try:
        merge_parent_and_basename(path)
    except Exception as e:
        assert isinstance(e, exception), f"Expected exception {exception} but got {type(e)}"
    
