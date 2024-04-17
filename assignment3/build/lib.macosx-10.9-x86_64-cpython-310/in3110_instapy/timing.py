from __future__ import annotations

import time
from typing import Callable

from . import get_filter, io
import in3110_instapy



def time_one(filter_function: Callable, *arguments, calls: int = 3) -> float:
    """Return the time for one call

    When measuring, repeat the call `calls` times,
    and return the average.

    Args:
        filter_function (callable):
            The filter function to time
        *arguments:
            Arguments to pass to filter_function
        calls (int):
            The number of times to call the function,
            for measurement
    Returns:
        time (float):
            The average time (in seconds) to run filter_function(*arguments)
    """
    # run the filter function `calls` times
    # return the _average_ time of one call
    execution_times = []
    for i in range(calls):
        start = time.perf_counter()
        filter_function(arguments[0])
        end = time.perf_counter()
        execution_times.append(end-start)
    return sum(execution_times) / len(execution_times)
    


def make_reports(filename: str = "test/rain.jpg", calls: int = 3):
    """
    Make timing reports for all implementations and filters,
    run for a given image.

    Args:
        filename (str): the image file to use
    """

    # load the image
    image = io.read_image(filename)
    # create report 
    report = open("timing-report.txt", "a")
    report.write(50 * "-" + "\n")
    report.write(f"Timing performed using {filename}: {image.shape[0]}x{image.shape[1]}")

    print(50 * "-")
    print(f"Timing performed using {filename}: {image.shape[0]}x{image.shape[1]}")

    # iterate through the filters
    filter_names = filter_names = ["color2gray", "color2sepia"]
    for filter_name in filter_names:
        # get the reference filter function
        reference_filter = in3110_instapy.get_filter(filter_name, "python")
        # time the reference implementation
        reference_time = time_one(reference_filter, image, calls)
        report.write(
            f"\nReference (pure Python) filter time {filter_name}: {reference_time:.3}s ({calls=})\n"
        )
        print(
            f"\nReference (pure Python) filter time {filter_name}: {reference_time:.3}s ({calls=})\n"
        )
        # iterate through the implementations
        implementations = ["numpy", "numba"] #TODO: Add Cython
        for implementation in implementations:
            filter = in3110_instapy.get_filter(filter_name,implementation)
            # time the filter
            filter_time = time_one(filter, image, calls)
            # compare the reference time to the optimized time
            speedup = float(reference_time/filter_time)
            report.write(
                f"Timing: {implementation} {filter_name}: {filter_time:.3}s ({speedup=:.2f}x)\n"
            )
            print(
                f"Timing: {implementation} {filter_name}: {filter_time:.3}s ({speedup=:.2f}x)"
            )
    report.write("\n" + 50 * "-" + "\n")
    print(50 * "-")

if __name__ == "__main__":
    # run as `python -m in3110_instapy.timing`
    make_reports()
