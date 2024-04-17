"""
Task 2 (IN4110 only)

parsing dates from wikipedia
"""

from __future__ import annotations

import re

# create array with all names of months
month_names = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def get_date_patterns() -> tuple[str, str, str]:
    """Return strings containing regex pattern for year, month, day
    arguments:
        None
    return:
        year, month, day (tuple): Containing regular expression patterns for each field
    """
    # Regex to capture days, months and years with numbers
    # year should accept a 4-digit number between at least 1000-2029
    year = r"\b(?P<year>(?:1\d{3}|20[0-2]\d))\b"
    # month should accept month names or month numbers
    month_patterns = [
        r"\b[jJ]an(?:uary)?\b",
        r"\b[fF]eb(?:ruary)?\b",
        r"\b[mM]ar(?:ch)?\b",
        r"\b[aA]pr(?:il)?\b",
        r"\b[mM]ay\b",
        r"\b[jJ]un(?:e)?\b",
        r"\b[jJ]ul(?:y)?\b",
        r"\b[aA]ug(?:ust)?\b",
        r"\b[sS]ep(?:tember)?\b",
        r"\b[oO]ct(?:ober)?\b",
        r"\b[nN]ov(?:ember)?\b",
        r"\b[dD]ec(?:ember)?\b",
        r"\b(?:0?[1-9]|1[0-2])\b"
    ]

    month = r"(?P<month>(?:" + "|".join(month_patterns) + "))"

    # day should be a number, which may or may not be zero-padded
    day = r"(?P<day>\b(?:0\d|1\d|2\d|3[0-1])\b|\b(?:\d|1\d|2\d|3[0-1])\b)"

    return year, month, day


def convert_month(s: str) -> str:
    """Converts a string month to number (e.g. 'September' -> '09'.

    You don't need to use this function,
    but you may find it useful.

    arguments:
        month_name (str) : month name
    returns:
        month_number (str) : month number as zero-padded string
    """

    month_dict = {
        "january": "01", "jan": "01",
        "february": "02", "feb": "02",
        "march": "03", "mar": "03",
        "april": "04", "apr": "04",
        "may": "05",                
        "june": "06", "jun": "06",
        "july": "07", "jul": "07",
        "august": "08", "aug": "08",
        "september": "09", "sep": "09",
        "october": "10", "oct": "10",
        "november": "11", "nov": "11",
        "december": "12", "dec": "12"
    }

    if s.isdigit():
        return s

    month = month_dict.get(s.lower())

    if month:
        return month    
    raise ValueError(f"Could not resolve month-number from string: {s}")
    
    
def zero_pad(n: str):
    """zero-pad a number string

    turns '2' into '02'

    You don't need to use this function,
    but you may find it useful.
    """
    if int(n) > 0:
        return n.zfill(2)
    else:
        raise ValueError(f"Invalid number: {n}")


def find_dates(text: str, output: str | None = None) -> list:
    """Finds all dates in a text using reg ex

    arguments:
        text (string): A string containing html text from a website
        output (str, Optional) : The file to write the output to if wanted
    return:
        results (List): A list with all the dates found
    """

    year, month, day = get_date_patterns()

    # Date on format YYYY/MM/DD - ISO
    ISO = rf"{year}-{month}-{day}"

    # Date on format DD/MM/YYYY
    DMY = rf"{day}\s{month}\s{year}"

    # Date on format MM/DD/YYYY
    MDY = rf"{month}\s{day},\s{year}"

    # Date on format YYYY/MM/DD
    YMD = rf"{year}\s{month}\s{day}"

    # list with all supported formats
    formats = [ISO, DMY, MDY, YMD]
    dates = []

    for f in formats: 
        matches = re.finditer(f, text)
        for match in matches:
            year = match.group("year")
            month = match.group("month")
            day = match.group("day")
            dates.append((f"{year}/{convert_month(month)}/{zero_pad(day)}", match.start()))

    sorted_dates = sorted(dates, key=lambda x:x[1]) #Sort dates based on indices
    dates = list(map(lambda x: x[0], sorted_dates)) #Remove indices from tupple, and keep only date
    
    # Write to file if wanted
    if output:
        print(f"Writing to: {output}")
        file = open(output, "w")
        for date in dates:
            file.write(str(date))
            file.write('\n')
        file.close()

    return dates
