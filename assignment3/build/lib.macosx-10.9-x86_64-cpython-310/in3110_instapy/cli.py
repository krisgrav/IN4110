"""Command-line (script) interface to instapy"""
from __future__ import annotations

import argparse
import sys
from PIL import Image

import in3110_instapy
import numpy as np
from PIL import Image

from . import io


def run_filter(
    file: str,
    out_file: str = None,
    implementation: str = "python",
    filter: str = "color2gray",
    scale: int = 1,
) -> None:
    """Run the selected filter"""

    # load the image from a file
    image = io.read_image(file)
    if scale != 1:
        # Resize image, if needed
        img = Image.open(file)
        resized_image = img.resize((img.width // scale, img.height // scale))
        image = np.asarray(resized_image)
    # Apply the filter
    filtered = in3110_instapy.get_filter(filter, implementation)(image)
    if out_file:
        # save the file
        io.write_image(filtered, out_file + ".jpg")
    else:
        # not asked to save, display it instead
        io.display(filtered)

def main(argv=None):
    """Parse the command-line and call run_filter with the arguments"""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Instapy image-filters")
    filter = parser.add_mutually_exclusive_group()

    # filename is positional and required
    parser.add_argument(
        "file",
        help="The filename to apply filter to"
    )
    parser.add_argument(
        "-o", 
        "--out", 
        help="The output filename"
    )

    # Add required arguments
    filter.add_argument(
        "-g",
        "--gray",
        action = "store_const",
        const = "color2gray",
        dest="filter",
        help="Apply gray filter",
    )
    filter.add_argument(
        "-se",
        "--sepia",
        action="store_const",
        const="color2sepia",
        dest="filter",
        help="Apply sepia filter",
    )

    parser.add_argument(
        "-sc",
        "--scale", 
        help="Scale for resizing image",
    )

    parser.add_argument(
        "-i",
        "--implementation",
        choices=["python","numba","numpy"], #TODO Add Cython
        default="python",
        help="Select filter-implementation",
    )

    # parse arguments and call run_filter
    arguments = vars(parser.parse_args())
    
    run_filter_arguments = {
        "file": arguments["file"],
    }

    # Check if optional arguments are applied, and add to arguments dictionary if True 
    if arguments["out"]:
        run_filter_arguments["out_file"] = arguments["out"]
    if arguments["implementation"] is not None:
        run_filter_arguments["implementation"] = arguments["implementation"]
    if arguments["filter"] is not None:
        run_filter_arguments["filter"] = arguments["filter"]
    if arguments["scale"]:
        run_filter_arguments["scale"] = int(arguments["scale"])
    
    # Run run_filter() with arguments from command-line
    run_filter(**run_filter_arguments)

