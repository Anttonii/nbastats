import shutil
import os

import pandas as pd

output_dir = 'output'
dataset_zip_file = 'nba-aba-baa-stats.zip'

player_totals = 'Player Totals.csv'
player_shooting = 'Player Shooting.csv'

output_json = 'players.json'


def unpack():
    if os.path.exists(output_dir):
        print("This function is designed to work with an empty output folder, please remove the folder before proceeding.")

    print("Creating output folder.")
    os.mkdir(output_dir)

    if not os.path.exists(dataset_zip_file):
        print("Make sure to download the dataset first.")
        exit(0)

    print("Unpacking dataset..")
    shutil.unpack_archive(dataset_zip_file, output_dir)


def main():
    """
    Preprocess the dataset to be used.
    """
    # unpack()

    # Files that are preserved
    files_preserved = [player_totals, player_shooting]

    files = [file for file in os.listdir(
        output_dir) if os.path.isfile(os.path.join(output_dir, file))]
    for file in files:
        if file not in files_preserved:
            os.remove(os.path.join(output_dir, file))

    # Use the players totals as a base dataframe and append from shooting
    # all the shooting specific data that we want to the part of the json.

    # Add or change the processing steps here if you want the output to
    # contain different data.
    operations = [
        (lambda x: x.sort_values(by=['player'])),
        (lambda x: x.reset_index(drop=True)),
        (lambda x: x.drop(x[x['season'] <= 2012].index, inplace=True))
    ]

    totals_path = os.path.join(output_dir, player_totals)
    totals = pd.read_csv(totals_path)

    shooting_path = os.path.join(output_dir, player_shooting)
    shooting = pd.read_csv(shooting_path)

    for op in operations:
        op(totals)
        op(shooting)

    merged_df = totals.merge(shooting, how="outer")

    output_json_path = os.path.join(output_dir, output_json)
    merged_df.to_json(output_json_path, orient='records')


if __name__ == '__main__':
    main()
