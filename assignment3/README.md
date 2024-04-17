# IN3110_instapy

IN3110_instapy is a package for turning your images into beatiful greyscale (color2grey) or sepia (color2sepia) pictures. The filters are implemented using three different implementations: pure python, numba & numpy. 

## Installation
Download folders and place in desired directory.

Use terminal to navigate to folder directory (path/assignment3).

Install package using: 
 $ pip install . 

## Usage
### Image Filtering
To use image filtering, navigate to project directory (path/assignment3).

To use package run:
  * $ python3 -m in3110_instapy <>arguments<>

#### Example usage
Add gray filter with python implementation, without saving the image:
  * $ python3 -m in3110_instapy "test/rain.jpg"

Add gray filter with python implementation, and save image:
  *  $ python3 -m in3110_instapy "test/rain.jpg" -o "new_name"

Add sepia filter with numba implementation, without saving the image:
  *  $ python3 -m in3110_instapy "test/rain.jpg" -se -i "numba"

Add sepia filter, and rescale image to half the size:
  * $ python3 -m in3110_instapy "test/rain.jpg" -se -sc 2


Required arguments:
| Argument | Function |
| -------- | -------- |
| file | The filename to apply filter to |

Optional arguments:
| Argument | Function |
| -------- | -------- |
| -h, --help | show this help message and exit |
| -o, --out | The output filename |
| -g, --gray | Apply gray filter |
| -se, --sepia | Apply sepia filter |
| -sc, --scale | Scale-factor for resizing image |
| -i {python,numba,numpy}, --implementation {python,numba,numpy} | Select filter-implementation |

Default values
| Argument | Value |
| -------- | -------- |
| Filter | Gray |
| Scale | 1 |
| Implementation | Python |

### Testing
To run tests, navigate to project directory (path/assignment3).

Run command:
  * $ pytest