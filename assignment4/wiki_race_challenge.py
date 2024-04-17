"""
Bonus task
"""
from __future__ import annotations
from requesting_urls import get_html
from bs4 import BeautifulSoup


def find_path(start: str, finish: str) -> list[str]:
    """Find the shortest path from `start` to `finish`

    Arguments:
      start (str): wikipedia article URL to start from
      finish (str): wikipedia article URL to stop at

    Returns:
      urls (list[str]):
        List of URLs representing the path from `start` to `finish`.
        The first item should be `start`.
        The last item should be `finish`.
        All items of the list should be URLs for wikipedia articles.
        Each article should have a direct link to the next article in the list.
    """
    path = [start]
    current_url = start

    while current_url != finish:
        response = get_html(current_url)
        soup = BeautifulSoup(response, "html.parser")
        next_link = soup.find("a", href=True, attrs={"href": lambda x: x and x.startswith("/wiki/")})
        
        if next_link:
            next_url = "https://en.wikipedia.org" + next_link["href"]
            path.append(next_url)
            current_url = next_url
        else:
            raise ValueError("No valid link found on the page.")

    assert path[0] == start
    assert path[-1] == finish
    return path


if __name__ == "__main__":
    start = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    finish = "https://en.wikipedia.org/wiki/Peace"
    path = find_path(start, finish)
    print(path)
