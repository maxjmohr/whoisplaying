import argparse
from collect_gameplans import collect_gameplans
import pandas as pd
from typing import List

if __name__ == "__main__":
    teams_native = ["Bayern 2", "1860", "Türkgücü"]

    # Parse arguments
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="Collect the gameplans of the teams playing at Grunwalder Stadion",
        description="Natively the gameplans from Bayern 2, 1860 and Türkgücü are collected. Add any other teams if you want to collect their gameplans as well.",
        epilog="Output stored in your folder",
        usage="%(prog)s [options]",
    )
    parser.add_argument(
        "-t",
        "--teams",
        type=List[str],
        help="teams to add (add in the format [Bayern 2, 1860, ...]",
        required=False,
    )
    parser.add_argument(
        "-urls",
        "--urls",
        type=List[str],
        help="team urls to add (add in the format [https://..., https://..., ...]",
        required=False,
    )
    args: argparse.Namespace = parser.parse_args()

    # Collect the gameplans
    df = pd.DataFrame(columns=["Wochentag", "Datum", "Uhrzeit", "Heim", "Gegner"])
    for team in teams_native:
        df = pd.concat([df, collect_gameplans(team)], ignore_index=True)

    if args.teams:
        for i in range(args.teams):
            df = pd.concat([df, collect_gameplans(args.teams[i], args.urls[i])], ignore_index=True)

    # Order from the earliest to the latest game and reindex
    df = df.sort_values(by=["Datum", "Uhrzeit"])
    df = df.reset_index(drop=True)

    # Format the date
    df["Datum"] = df["Datum"].dt.strftime("%d.%m.%Y")

    print(df)
    
    # Save data to a markdown file
    markdown_str = df.to_markdown()
    with open("gameplans.md", "w") as f:
        f.write(markdown_str)