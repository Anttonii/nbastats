import os
import shutil
import sys

import pandas as pd

output_dir = "output"
dataset_zip_file = "nba-aba-baa-stats.zip"

player_totals = "Player Totals.csv"
player_shooting = "Player Shooting.csv"

players_json = "players.json"
alltime_json = "alltime.json"
seasonal_averages_json = "averages_season.json"
alltime_averages_json = "averages_alltime.json"
position_averages_json = "averages_position.json"


def unpack():
    if os.path.exists(output_dir):
        print(
            "Unpacking is designed to work with an empty output folder, please remove the folder before proceeding."
        )
        exit(1)

    print("Creating output folder.")
    os.mkdir(output_dir)

    if not os.path.exists(dataset_zip_file):
        print("Make sure to download the dataset first.")
        os.remove(output_dir)
        exit(1)

    print("Unpacking dataset..")
    shutil.unpack_archive(dataset_zip_file, output_dir)

    print("Unpacking successful, removing unnecessary files.")
    # Files that are preserved
    files_preserved = [player_totals, player_shooting]

    files = [
        file
        for file in os.listdir(output_dir)
        if os.path.isfile(os.path.join(output_dir, file))
    ]

    for file in files:
        if file not in files_preserved:
            os.remove(os.path.join(output_dir, file))


def get_all_time(df: pd.DataFrame) -> pd.DataFrame:
    """
    Builds the all time data frame on player to player basis by calculating totals and averages aggregated over the entire career
    here career being defined as the range of years accepted for processing (2013-2023)
    """
    grouped = df.groupby(by=["player"], as_index=False)

    # The stats to calculate totals of
    totals = [
        "g",  # Games played
        "mp",  # Minutes played
        "ft",  # Free throws made
        "orb",  # Offensive reounds
        "drb",  # Defensive rebounds
        "trb",  # Total rebounds
        "ast",  # Assists
        "stl",  # Steals
        "blk",  # Blocks
        "tov",  # Turnovers
        "pf",  # Personal fouls
        "pts",  # Points
    ]

    # The stats to calculate career averages of
    averages = [
        "fg_percent",  # Field goal percentage
        "x3p_percent",  # 3p percentage
        "x2p_percent",  # 2p percentage
        "e_fg_percent",  # Effective field foal percentage
        "ft_percent",  # Free throw percentage
        "avg_dist_fga",  # Average distance of a field goal attempt
        "fg_percent_from_x2p_range",  # FG% from 2p range
        "fg_percent_from_x0_3_range",  # FG% from right under the basket
        "fg_percent_from_x3_10_range",  # FG% from close range 2p
        "fg_percent_from_x10_16_range",  # FG% from mid range 2p
        "fg_percent_from_x16_3p_range",  # FG% from long range 2p
        "fg_percent_from_x3p_range",  # FG% from behind the 3p line
    ]

    # The stats to calculate average per game
    # in this case, calculate for all except the first row, that being the row of games played.
    averages_pg = totals[1:]

    # Process the aggregated data
    aggregate_dict = {total: "sum" for total in totals}
    aggregate_dict.update({average: "mean" for average in averages})

    # Rename the columns
    aggregated_columns = {total: f"total_{total}" for total in totals}
    aggregated_columns.update({average: f"average_{average}" for average in averages})

    aggregated = grouped.agg(aggregate_dict)
    aggregated.rename(columns=aggregated_columns, inplace=True)

    for per_game_average in averages_pg:
        aggregated[f"pga_{per_game_average}"] = (
            aggregated[f"total_{per_game_average}"] / aggregated["total_g"]
        )

    return aggregated


def get_league_averages(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Gets league averages on season to season basis, all time and for different positions.
    """
    # remove unnecessary values
    df.drop(["player_id", "seas_id", "player", "tm"], axis=1, inplace=True)
    positional_data = df.groupby(by=["season", "pos"]).mean().reset_index()

    df.drop("pos", axis=1, inplace=True)
    seasonal_data = df.groupby(by=["season"]).mean().reset_index()

    df.drop("season", axis=1, inplace=True)
    alltime_data = df.mean()

    return (seasonal_data, alltime_data, positional_data)


def generate_json(df, path, orient="records"):
    """
    Utility function for generating json outputs.
    """
    df.to_json(path, orient=orient)
    print(f"Output generated succesfully to: {path}")


def main():
    """
    Preprocess the dataset to be used.
    """
    # The first argument is a boolean value for whether or not to unpack.
    argc = len(sys.argv)
    if argc > 1:
        if sys.argv[1] == "1":
            unpack()

    # Use the players totals as a base dataframe and append from shooting
    # all the shooting specific data that we want to the part of the json.

    # Add or change the processing steps here if you want the output to
    # contain different data.
    operations = [
        (lambda x: x.sort_values(by=["player"])),
        (lambda x: x.reset_index(drop=True)),
        # Drop the seasons that don't have shooting percentage data and the latest season
        (lambda x: x.drop(x[x["season"] <= 2012].index, inplace=True)),
        (lambda x: x.drop(x[x["season"] > 2024].index, inplace=True)),
        (lambda x: x.drop(["lg", "experience", "birth_year"], axis=1, inplace=True)),
    ]

    totals_path = os.path.join(output_dir, player_totals)
    totals = pd.read_csv(totals_path)

    shooting_path = os.path.join(output_dir, player_shooting)
    shooting = pd.read_csv(shooting_path)

    for op in operations:
        op(totals)
        op(shooting)

    merged_df = totals.merge(shooting, how="outer")
    alltime_df = get_all_time(merged_df)
    (s_avg, at_avg, pos_avg) = get_league_averages(merged_df)

    players_json_path = os.path.join(output_dir, players_json)
    alltime_json_path = os.path.join(output_dir, alltime_json)
    seasonal_averages_json_path = os.path.join(output_dir, seasonal_averages_json)
    alltime_averages_json_path = os.path.join(output_dir, alltime_averages_json)
    position_averages_json_path = os.path.join(output_dir, position_averages_json)

    generate_json(merged_df, players_json_path)
    generate_json(alltime_df, alltime_json_path)
    generate_json(s_avg, seasonal_averages_json_path)
    generate_json(at_avg, alltime_averages_json_path, "index")
    generate_json(pos_avg, position_averages_json_path)


if __name__ == "__main__":
    main()
