"""
Module for parsing raw HTML data and extracting relevant
awards information.
"""

from bs4 import BeautifulSoup

def format_all_league(counter: dict) -> list:
    if counter is None:
        return
    format = []
    for category, count in counter.items():
        if 'Seeding' in category:
            continue # weird edge case for all-seeding teams
        if '1st' in category:
            team_name = "First Team"
        elif '2nd' in category:
            team_name = "Second Team"
        elif '3rd' in category:
            team_name = "Third Team"
        else:
            continue # this is for in season tournament teams

        # create the formatted string
        formatted_string = f"{count}x {category.replace(' (1st)', '').replace(' (2nd)', '').replace(' (3rd)', '')} {team_name}"
        format.append(formatted_string)
        
    return format

def seperate_all_league(soup: BeautifulSoup):
    # parses the HTML table for all-league info

    if soup is None:
        return
    
    td_elements = soup.find_all('td', class_='single')

    league_counts = {}
    for td in td_elements:
        text = td.get_text(strip=True)

        if text:
            category = text[7:]
            if category in league_counts:
                league_counts[category] += 1  # Increment count
            else:
                league_counts[category] = 1  # Initialize count

    return league_counts

def get_all_league_list(soup: BeautifulSoup) -> BeautifulSoup:
    # gets raw all-league data
    if soup is None:
        return []
    
    # div = soup.find('ul', id="leaderboard_all_league")
    """for some reason BeautifulSoup cannot find the div with
    id='leaderboard_all_league', this is probably a BeautifulSoup error.
    Alternatively, we manually find it via string methods"""

    soup_string = str(soup)
    start_index = soup_string.find('<div id="leaderboard_all_league"')
    end_index = soup_string.find('</div>', start_index) + len('</div>')

    if start_index != -1 and end_index != -1:
        specific_div = soup_string[start_index:end_index]
    else:
        print("Div with id 'leaderboard_all_league' not found.")
        return
    
    soup = BeautifulSoup(specific_div, 'html.parser')
    return soup


def get_awards_list(soup: BeautifulSoup) -> list:
    ul = soup.find('ul', id="bling")

    if ul is None:
        return ["Awards N/A"]
    
    awards = []
    for li in ul.find_all('li'):
        award_text = li.get_text(strip=True) 
        if "All-" in award_text:
            continue # want to make distinctions between 1st/2nd/3rd teams
        elif "Sportsmanship" in award_text:
            continue

        awards.append(award_text)

    return awards

def get_priority_awards(awards: list[str]) -> dict:
    d = {"Rings": 0, "All-Star": 0, "All-NBA": 0}
    for award in awards:
        if "All Star" in award:
            d["All-Star"] = award.split('x')[0]
        elif "All-NBA" in award:
            d['All-NBA'] += int(award.split('x')[0])
        elif "NBA Champ" in award:
            if "x" not in award:
                d['Rings'] = 1
            else:
                d['Rings'] = award.split('x')[0]
    # print(d)
    return d