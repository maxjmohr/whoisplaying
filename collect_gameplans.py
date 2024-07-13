from datetime import datetime
from lxml import etree
import pandas as pd
import requests

def collect_gameplans(team: str, url: str = ""):
    """Collect gameplans from transfermarkt.de
    Parameters:
    team: str
        Team to collect gameplans for
    url: str
        URL to collect gameplans from
    Returns:
    pd.DataFrame
        DataFrame with gameplans
    """
    if team not in ["Bayern 2", "1860", "Türkgücü"]:
        assert url != "", f"{datetime.now()} | URL is required for {team}. Go to transfermarkt > {team} > 'Spielplan nach Datum' > filter for 'Nur Heimspiele' > copy the URL and paste it here."
    else:
        # Map the team to the correct URL
        team_url_mapping = {
            "Bayern 2": "https://www.transfermarkt.de/fc-bayern-munchen-ii/spielplandatum/verein/28/plus/0?saison_id=2024&wettbewerb_id=&day=&heim_gast=heim&punkte=&datum_von=&datum_bis=",
            "1860": "https://www.transfermarkt.de/tsv-1860-munchen/spielplandatum/verein/72/plus/0?saison_id=2024&wettbewerb_id=&day=&heim_gast=heim&punkte=&datum_von=&datum_bis=",
            "Türkgücü": "https://www.transfermarkt.de/turkgucu-munchen/spielplandatum/verein/12456/plus/0?saison_id=2024&wettbewerb_id=&day=&heim_gast=heim&punkte=&datum_von=&datum_bis="
        }
        url = team_url_mapping[team]

    # Get the content of the page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    page = requests.get(url, headers=headers).content
    tree = etree.HTML(page)
    # Save the tree to a file
    with open("tree.html", "w") as f:
        f.write(etree.tostring(tree).decode())

    # Find table and get cokumn names along with data
    table = tree.find('.//div[@class="responsive-table"]/table')

    # Extract column names
    original_column_names = ["".join(th.itertext()).strip() for th in table.findall('.//thead//th')]
    
    # Define the desired columns
    desired_columns = ['Datum', 'Uhrzeit', 'Gegner']

    # Find the indices of the desired columns
    desired_indices = [original_column_names.index(col) for col in desired_columns]

    # Extract data rows
    data = []
    for row in table.findall('.//tbody//tr'):
        data_row = [td.text.strip() if td.text else "".join(td.itertext()).strip() for td in row.findall('.//td')]
        if len(data_row) > 5:
            data_row.pop(5)
        if len(data_row) == len(original_column_names):
            filtered_row = [data_row[idx] for idx in desired_indices]
            data.append(filtered_row)
        else:
            # Handle unexpected number of columns
            print(f"Skipping row with unexpected number of columns {data_row}")

    # Convert to DataFrame
    df = pd.DataFrame(data, columns=desired_columns)

    # Add home team
    df["Heim"] = team
    
    # Turn the date into a datetime object and map the weekday
    # First divide they weekday and date
    df["Wochentag"] = df["Datum"].str.split(" ", n=1).str[0]
    df["Datum"] = df["Datum"].str.split(" ", n=1).str[1]

    # Map the weekday
    weekday_mapping = {
        "Mo.": "Montag",
        "Di.": "Dienstag",
        "Mi.": "Mittwoch",
        "Do.": "Donnerstag",
        "Fr.": "Freitag",
        "Sa.": "Samstag",
        "So.": "Sonntag"
    }
    df["Wochentag"] = df["Wochentag"].map(weekday_mapping)

    # Turn the date into a datetime object and check that only future games are included
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%y")
    df = df[df["Datum"] >= datetime.now()]

    return df[["Wochentag", "Datum", "Uhrzeit", "Heim", "Gegner"]]

if __name__ == "__main__":
    team_gameplans_df = collect_gameplans("Bayern 2")
    print(team_gameplans_df)