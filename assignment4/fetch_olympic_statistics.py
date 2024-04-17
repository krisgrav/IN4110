"""
Task 4

collecting olympic statistics from wikipedia
"""

from __future__ import annotations
from pathlib import Path
from requesting_urls import get_html
from bs4 import BeautifulSoup
import re
import os
import matplotlib.pyplot as plt


# Countries to submit statistics for
scandinavian_countries = ["Norway", "Denmark", "Sweden"]

# Summer sports to submit statistics for
summer_sports = ["Sailing", "Athletics", "Handball", "Football", "Cycling", "Archery"]


def report_scandi_stats(url: str, sports_list: list[str], work_dir: str | Path) -> None:
    """
    Given the url, extract and display following statistics for the Scandinavian countries:

      -  Total number of gold medals for for summer and winter Olympics
      -  Total number of gold, silver and bronze medals in the selected summer sports from sport_list
      -  The best country in number of gold medals in each of the selected summer sports from sport_list

    Display the first two as bar charts, and the last as an md. table and save in a separate directory.

    Parameters:
        url (str) : url to the 'All-time Olympic Games medal table' wiki page
        sports_list (list[str]) : list of summer Olympic games sports to display statistics for
        work_dir (str | Path) : (absolute) path to your current working directory

    Returns:
        None
    """

    # Make a call to get_scandi_stats
    # Plot the summer/winter gold medal stats
    # Iterate through each sport and make a call to get_sport_stats
    # Plot the sport specific stats
    # Make a call to find_best_country_in_sport for each sport
    # Create and save the md table of best in each sport stats

    work_dir = Path(work_dir)
    country_dict = get_scandi_stats(url)

    stats_dir = work_dir / "olympic_games_results"
    
    if not os.path.exists(stats_dir):
        os.makedirs(stats_dir)

    plot_scandi_stats(country_dict, stats_dir)


    best_in_sport = []
    # Valid values for medal ["Gold" | "Silver" |"Bronze"]
    medal = "Gold"
    md_file_path = f"{stats_dir}/best_of_sport_by_{medal}.md"
    with open(md_file_path, "w") as md_file:
        md_file.write("| Sport | Best Country |" + "\n")
        md_file.write("|:----------|:----------|" + "\n")
    for sport in sports_list:
        results: dict[str, dict[str, int]] = {}
        for country in scandinavian_countries:
            result = get_sport_stats(f"https://en.wikipedia.org/wiki/{country}_at_the_Olympics", sport)
            results[country] = {
                "Gold": result["Gold"],
                "Silver": result["Silver"],
                "Bronze": result["Bronze"]
            }
        plot_sport_stats(results, sport, stats_dir)

        best_country = find_best_country_in_sport(results, medal)
        with open(md_file_path, "a") as md_file:
            md_file.write(f"| {sport} | {best_country} |\n")
    md_file.close()
        
        

        



def get_scandi_stats(
    url: str,
) -> dict[str, dict[str, str | dict[str, int]]]:
    """Given the url, extract the urls for the Scandinavian countries,
       as well as number of gold medals acquired in summer and winter Olympic games
       from 'List of NOCs with medals' table.

    Parameters:
      url (str): url to the 'All-time Olympic Games medal table' wiki page

    Returns:
      country_dict: dictionary of the form:
        {
            "country": {
                "url": "https://...",
                "medals": {
                    "Summer": 0,
                    "Winter": 0,
                },
            },
        }

        with the tree keys "Norway", "Denmark", "Sweden".
    """
    base_url = "https://en.wikipedia.org"

    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="wikitable sortable") #Table of NCOs with medals is the first table of class wikitable sortable
    soup = BeautifulSoup(str(table), "html.parser")

    scandi_pattern = re.compile(r'\b(?:' + '|'.join(scandinavian_countries) + r')\b', re.IGNORECASE) #regex pattern for scandi countries
    anchors = soup.find_all("a", text=scandi_pattern) #Find all achors containing a country from Scandinavia
    
    rows = []

    for a in anchors: #Iterate all anchors found, and find their <tr> parent
        parent = a
        while parent and parent.name != "tr":
            parent = parent.parent
        if parent and parent.name == "tr":
            rows.append(parent)

    country_dict: dict[str, dict[str, str | dict[str, int]]] = {}

    for row in rows:
        soup = BeautifulSoup(str(row), 'html.parser')
        country = soup.find('a').text #name of country is ritten in the first anchor.
        
        table_data = soup.find_all("td")
        summer_gold = int(table_data[2].text) #Summer gold is 3rd td in the tr.
        winter_gold = int(table_data[7].text) #Winter gold is 8th td in the tr.

        url = f"{base_url}/wiki/{country}_at_the_Olympics"

        country_dict[country] = {
            "url":url,
            "medals":{
                "Summer":summer_gold,
                "Winter":winter_gold
            }
        }

    return country_dict


def get_sport_stats(country_url: str, sport: str) -> dict[str, int]:
    """Given the url to country specific performance page, get the number of gold, silver, and bronze medals
      the given country has acquired in the requested sport in summer Olympic games.

    Parameters:
        - country_url (str) : url to the country specific Olympic performance wiki page
        - sport (str) : name of the summer Olympic sport in interest. Should be used to filter rows in the table.

    Returns:
        - medals (dict[str, int]) : dictionary of number of medal acquired in the given sport by the country
                          Format:
                          {"Gold" : x, "Silver" : y, "Bronze" : z}
    """
    
    html = get_html(country_url)
    soup = BeautifulSoup(html, "html.parser")
    id_pattern = re.compile(r'medals_by_summer_sport', re.IGNORECASE) #Ignoring case-sensitivity in medals_by_summer_sport
    table = soup.find('span', {'id': id_pattern}).find_parent('table', {'class': 'multicol'}) #Using summer sport to find medals table, and then finding the table wrapping both summer and winter sports
 
    medals = {
        "Gold": 0,
        "Silver": 0,
        "Bronze": 0,
    }

    soup = BeautifulSoup(str(table), "html.parser")
    sport_pattern = re.compile(r'\b{}\b'.format(re.escape(sport)), re.IGNORECASE) #Ignoring case sensitivity in sport-name
    sport_anchor = soup.find("a", string=sport_pattern) #Finding the exact sport in the table coiintaining all sports, then finding its first tr-parent
    if sport_anchor:
        sport_row = sport_anchor.find_parent("tr")
        sport_medals = sport_row.find_all("td")

        medals["Gold"] = int(sport_medals[0].text)
        medals["Silver"] = int(sport_medals[1].text)
        medals["Bronze"] = int(sport_medals[2].text)
    else:
        medals["Gold"] = 0
        medals["Silver"] = 0
        medals["Bronze"] = 0

    return medals


def find_best_country_in_sport(
    results: dict[str, dict[str, int]], medal: str = "Gold"
) -> str:
    """Given a dictionary with medal stats in a given sport for the Scandinavian countries, return the country
        that has received the most of the given `medal`.

    Parameters:
        - results (dict) : a dictionary of country specific medal results in a given sport. The format is:
                        {"Norway" : {"Gold" : 1, "Silver" : 2, "Bronze" : 3},
                         "Sweden" : {"Gold" : 1, ....},
                         "Denmark" : ...
                        }
        - medal (str) : medal type to compare for. Valid parameters: ["Gold" | "Silver" |"Bronze"]. Should be used as a key
                          to the medal dictionary.
    Returns:
        - best (str) : name of the country(ies) leading in number of gold medals in the given sport
                       If one country leads only, return its name, like for instance 'Norway'
                       If two countries lead return their names separated with '/' like 'Norway/Sweden'
                       If all or none of the countries lead, return string 'None'
    """
    
    valid_medals = {"Gold", "Silver", "Bronze"}
    if medal not in valid_medals:
        raise ValueError(
            f"{medal} is invalid parameter for ranking, must be in {valid_medals}"
        )

    # Get the requested medals and determine the best
    best = "None"

    max_count = 0
    countries = []
    for country, medals in results.items():
        if medals[medal] > max_count:
            max_count = medals[medal]
            countries = [country]
        elif medals[medal] == max_count:
            countries.append(country)
    
    if len(countries) == 1:
        best = countries[0]
    elif len(countries) == 2:
        best = f"{countries[0]}/{countries[1]}"

    return best


# Define your own plotting functions and optional helper functions
def plot_scandi_stats(
    country_dict: dict[str, dict[str, str | dict[str, int]]],
    output_parent: str | Path | None = None,
) -> None:
    """Plot the number of gold medals in summer and winter games for each of the scandi countries as bars.

    Parameters:
      results (dict[str, dict[str, int]]) : a nested dictionary of country names and the corresponding number of summer and winter
                            gold medals from 'List of NOCs with medals' table.
                            Format:
                            {"country_name": {"Summer" : x, "Winter" : y}}
      output_parent (str | Path) : parent file path to save the plot in
    Returns:
      None
    """
    # Extract data for plotting
    countries = list(country_dict.keys())
    summer_medals = [country_dict[country]['medals']['Summer'] for country in countries]
    winter_medals = [country_dict[country]['medals']['Winter'] for country in countries]
    
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.2
    index = range(len(countries))

    summer_bars = ax.bar(index, summer_medals, bar_width, label='Summer Medals', color="red")
    winter_bars = ax.bar([p + bar_width for p in index], winter_medals, bar_width, label='Winter Medals', color="blue")

    ax.set_xlabel('Countries', fontweight='bold')
    ax.set_ylabel('Number of Gold Medals', fontweight='bold')
    ax.set_title('Number of Gold Medals for Scandinavian Countries', fontweight='bold')
    ax.set_xticks([p + bar_width / 2 for p in index])
    ax.set_xticklabels(countries)
    ax.legend()

    for i, v in enumerate(summer_medals):
        ax.text(i, v + 0.1, str(v), ha='center', va='bottom', color='black', fontweight='bold')
    for i, v in enumerate(winter_medals):
        ax.text(i + bar_width, v + 0.1, str(v), ha='center', va='bottom', color='black', fontweight='bold')

    # Save or show the plot
    if output_parent:
        output_path = Path(output_parent) / 'total_medal_ranking.png'
        plt.savefig(output_path)
    else:
        plt.show()


def plot_sport_stats(
    country_dict: dict[str, dict[str, int]],
    sport:str,
    output_parent: str | Path | None = None,
    
) -> None:
    """Plot the medal counts (Gold, Silver, and Bronze) for each country as grouped bars.

    Parameters:
        country_dict (dict[str, dict[str, int]]) : a dictionary of country names and their medal counts.
                        Format: {"country_name": {"Gold": x, "Silver": y, "Bronze": z}}
        output_parent (str | Path) : parent file path to save the plot in
    Returns:
        None
    """
    countries = list(country_dict.keys())
    medals = ["Gold", "Silver", "Bronze"]
    medal_counts = [[country_dict[country][medal] for medal in medals] for country in countries]

    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.2
    opacity = 0.8
    index = range(len(countries))

    colors = ['gold', 'silver', '#CD7F32']  # Yellow for gold, grey for silver, brown for bronze

    for i, medal in enumerate(medals):
        bars = ax.bar([p + bar_width * i for p in index], [counts[i] for counts in medal_counts],
                      bar_width, alpha=opacity, label=f'{medal} Medals', color=colors[i])
        for bar in bars:
            height = bar.get_height()
            ax.annotate('{}'.format(int(height)),  # Format height as integer
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    ax.set_xlabel('Countries', fontweight="bold")
    ax.set_ylabel(f'Number of Medals in {sport}', fontweight="bold")
    ax.set_title(f"Number of medals in {sport} for Scandinavian countries")
    ax.set_xticks([p + bar_width for p in index])
    ax.set_xticklabels(countries)
    ax.legend()

    if output_parent:
        plt.savefig(output_parent / f"{sport}_medal_ranking.png")
    else:
        plt.show()


# run the whole thing if called as a script, for quick testing
if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/All-time_Olympic_Games_medal_table"

    #My code in here (remove commented code to run)
    #-----------------------------------------------------------------------------
    #4.1
    """ scandi_stats = get_scandi_stats(url) """

    #4.2
   # url = "https://en.wikipedia.org/wiki/Sweden_at_the_Olympics"
    """ for country in scandinavian_countries:
        url = f"https://en.wikipedia.org/wiki/{country}_at_the_Olympics"
        sport_stats = get_sport_stats(url, "Archery") """

    #4.3

    """ results = {}
    for country in scandinavian_countries:
        sport_stats = get_sport_stats(f"https://en.wikipedia.org/wiki/{country}_at_the_Olympics", "sailing")
        results[country] = {
            "Gold":sport_stats["Gold"],
            "Silver":sport_stats["Silver"],
            "Bronze":sport_stats["Bronze"]
        }
    best = find_best_country_in_sport(results, "Gold") """
    
    #4.4
    work_dir = os.getcwd()
    report_scandi_stats(url, summer_sports, work_dir)
    #-----------------------------------------------------------------------------
    #My code in here



    




