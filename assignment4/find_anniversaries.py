"""
Task 3

Collecting anniversaries from Wikipedia
"""
from __future__ import annotations

from pathlib import Path
from bs4 import BeautifulSoup

import pandas as pd

import re

import os

from requesting_urls import get_html

# Month names to submit for, from Wikipedia:Selected anniversaries namespace
months_in_namespace = [
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


def extract_anniversaries(html: str, month: str) -> list[str]:
    """Extract all the passages from the html which contain an anniversary, and save their plain text in a list.
        For the pages in the given namespace, all the relevant passages start with a month href
         <p>
            <b>
                <a href="/wiki/April_1" title="April 1">April 1</a>
            </b>
            :
            ...
        </p>

    Parameters:
        - html (str): The html to parse
        - month (str): The month in interest, the page name of the Wikipedia:Selected anniversaries namespace

    Returns:
        - ann_list (list[str]): A list of the highlighted anniversaries for a given month
                                The format of each element in the list is:
                                '{Month} {day}: Event 1 (maybe some parentheses); Event 2; Event 3, something, something\n'
                                {Month} can be any month in the namespace and {day} is a number 1-31
    """

    # parse the HTML
    soup = BeautifulSoup(html, "html.parser")

    # Get all the paragraphs:
    paragraphs = soup.find_all("p")

    # Filter the passages to keep only the highlighted anniversaries
    ann_list = []

    month = month.capitalize() #Wiki has all months capitalized
    anniversary_pattern = fr'(?:<p><b>|<p>)<a\s+href="/wiki/{month}_\d+"' #Regex finds <a> tags with correct href, only preceded by <p> or <p><b>
    anchor_pattern = r'<a[^>]*\stitle="([^"]*)"'
    
    for paragraph in paragraphs:
        if re.search(anniversary_pattern, str(paragraph), re.IGNORECASE): # Check if the paragraph contains an <a> tag with an href attribute
            title = re.search(anchor_pattern, str(paragraph)).group(1) #Get title from anchor-tag
            paragraph_text = paragraph.get_text(strip=True).split(':', 1)
            if len(paragraph_text) > 1:
                ann_list.append(f'{title}:{paragraph_text[1]}')
            else:
                ann_list.append(title)
    
    return ann_list


def anniversary_list_to_df(ann_list: list[str]) -> pd.DataFrame:
    """Transform the list of anniversaries into a pandas dataframe.

    Parameters:
        ann_list (list[str]): A list of the highlighted anniversaries for a given month
                                The format of each element in the list is:
                                '{Month} {day}: Event 1 (maybe some parenthesis); Event 2; Event 3, something, something\n'
                                {Month} can be any month in months list and {day} is a number 1-31
    Returns:
        df (pd.Dataframe): A (dense) dataframe with columns ["Date"] and ["Event"] where each row represents a single event
    """
    # Store the split parts of the string as a table
    ann_table = [] #Uncertain what is ment by "Table", so i used a list of lists like in the test

    event_pattern = r';(?![^(]*\))'
    for ann in ann_list:
        date, separator, event = ann.strip().partition(":")
        if event:
            events = re.split(event_pattern, event)
            for event in events:
                ann_table.append([date, event.strip()])
    
    # Headers for the dataframe
    headers = ["Date", "Event"]
    df = pd.DataFrame(ann_table, columns=headers)
    return df


def anniversary_table(
    namespace_url: str, month_list: list[str], work_dir: str | Path
) -> None:
    """Given the namespace_url and a month_list, create a markdown table of highlighted anniversaries for all of the months in list,
        from Wikipedia:Selected anniversaries namespace

    Parameters:
        - namespace_url (str):  Full url to the "Wikipedia:Selected_anniversaries/" namespace
        - month_list (list[str]) - List of months of interest, referring to the page names of the namespace
        - work_dir (str | Path) - (Absolute) path to your working directory

    Returns:
        None
    """
    # Loop through all months in month_list
    # Extract the html from the url (use one of the already defined functions from earlier)
    # Gather all highlighted anniversaries as a list of strings
    # Split into date and event
    # Render to a df dataframe with columns "Date" and "Event"
    # Save as markdown table

    work_dir = Path(work_dir)
    output_dir = work_dir / "tables_of_anniversaries"

    if not os.path.exists(output_dir): # Create destination folder if it dosent already exist
        os.makedirs(output_dir)

    for month in month_list:
        page_url = namespace_url + month
        html = get_html(page_url)
        
        # Get the list of anniversaries
        ann_list = extract_anniversaries(html, month)

        # Render to a dataframe
        df = anniversary_list_to_df(ann_list)

        # Convert to an .md table
        table = df.to_markdown(index=False)

         #Save the output
        file_path =  f"{output_dir}/anniversaries_{month.lower()}.md"
        with open(file_path, "w") as file:
            file.write(table)


if __name__ == "__main__":
    # make tables for all the months
    work_dir = os.getcwd()
    namespace_url = "https://en.wikipedia.org/wiki/Wikipedia:Selected_anniversaries/"
    anniversary_table(namespace_url, months_in_namespace, work_dir)

def test():
    sample_HTML = """
    <p></p>
    <p>Nothing about a month here</p>
    <p>October 3:</p>
    <p><a href="/wiki/October_1" title="October 1">October 1</a></p>
    <p><b><a href="/wiki/October_19" title="October 19">October 19</a></b></p>
    <p><b><a href="/wiki/October_19" title="October 19">October 19</a></b>: Det var i der herrens år 2; Og ogsa noe i år 3; Og noe skjer her (21:58); Bingbong (Bing;bong)</p>
    <p>Text that should not be there<b><a href="/wiki/October_10" title="October 10">October 10</a></b></p>
    <p><a href="October_29" title="October 29">October 29</a></p>

    <table>
    </table>
    """

    annlist = extract_anniversaries(sample_HTML, "october")
    annlist.append("December 1: just a beautiful day (always?); Winter is coming (No daylight past 15:00)")

    df = anniversary_list_to_df(annlist)
    namespace_url = "https://en.wikipedia.org/wiki/Wikipedia:Selected_anniversaries/"
    directory = os.getcwd()

    anniversary_table(namespace_url, months_in_namespace, directory)
