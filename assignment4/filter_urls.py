"""
Task 1.2, 1.3

Filtering URLs from HTML
"""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse


def find_urls(
    html: str,
    base_url: str = "https://en.wikipedia.org",
    output: str | None = None,
) -> set[str]:
    """
    Find all the url links in a html text using regex

    Arguments:
        html (str): html string to parse
        base_url (str): the base url to the wikipedia.org pages
        output (Optional[str]): file to write to if wanted
    Returns:
        urls (Set[str]) : set with all the urls found in html text
    """
    https_prefix = "https:"
    url_pattern = re.compile(r"<a\s+[^>]+>", flags=re.IGNORECASE)
    href_pattern = re.compile(r'href="([^"]+)"|(?:href="([^"]+)")', flags=re.IGNORECASE)
    return_set = set()
    
    for url in url_pattern.findall(html):
        match = href_pattern.search(url)
        if match:
            if re.search('^#', match.group(1)): #If url begins with #, skip it
                continue
            elif re.search('^/', match.group(1)):
                if re.search('^//', match.group(1)): #Protocol relative url
                    return_set.add(https_prefix + match.group(1))
                elif re.search('#', match.group(1)) and not re.search('^#', match.group(1)): #Fragmented url
                    fragments = re.search('#', match.group(1))
                    return_set.add(base_url + match.group(1)[:fragments.start()])
                elif re.search('\?', match.group(1)) or re.search('\(', match.group(1)):
                    return_set.add(base_url + match.group(1))
                else:
                    return_set.add(re.sub(match.group(1), (base_url+match.group(1)),match.group(1)))
            else:
                return_set.add(match.group(1))

    # Write to file if requested
    if output:
        print(f"Writing to: {output}")
        file = open(output, "w")
        for url in return_set:
            file.write(str(url))
            file.write('\n')
        file.close()

    return return_set


def find_articles(
    html: str,
    output: str | None = None,
    base_url: str = "https://en.wikipedia.org",
) -> set[str]:
    """Finds all the wiki articles inside a html text. Make call to find urls, and filter
    arguments:
        - text (str) : the html text to parse
        - output (str, optional): the file to write the output to if wanted
        - base_url (str, optional): the base_url to pass through to find_urls
    returns:
        - (Set[str]) : a set with urls to all the articles found
    """
    urls = find_urls(html)
    pattern = re.compile(pattern = r'^https?:\/\/[a-z]{2}\.wikipedia\.[a-z]{2,3}/wiki/[^:]+$', flags=re.IGNORECASE)
    articles = set()
    
    for url in urls:
        match = pattern.search(url)
        if match:
            articles.add(match.group(0))

    # Write to file if wanted
    if output:
        file = open(output, "w")
        for art in articles:
            file.write(str(art))
            file.write('\n')
        file.close()
    
    return articles


## Regex example
def find_img_src(html: str):
    """Find all src attributes of img tags in an HTML string

    Args:
        html (str): A string containing some HTML.

    Returns:
        src_set (set): A set of strings containing image URLs

    The set contains every found src attribute of an img tag in the given HTML.
    """
    # img_pat finds all the <img alt="..." src="..."> snippets
    # this finds <img and collects everything up to the closing '>'
    img_pat = re.compile(r"<img[^>]+>", flags=re.IGNORECASE)
    # src finds the text between quotes of the `src` attribute
    src_pat = re.compile(r'src="([^"]+)"', flags=re.IGNORECASE)
    src_set = set()
    # first, find all the img tags
    for img_tag in img_pat.findall(html):
        # then, find the src attribute of the img, if any
        match = src_pat.search(img_tag)
        if match:
            src_set.add(match.group(1))
    return src_set
