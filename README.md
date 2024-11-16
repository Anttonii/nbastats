# NBA Stats

A NBA shooting statistic visualiser. Choose your favorite player to view their statistics and where they are the most efficient shooting from! This repository only contains the python preprocessing steps to produce used dataset, the website integration will be available in the [portfolio-website](https://github.com/Anttonii/personal-website) repository.

## Fetching the dataset

This repository leverages [NBA Stats](https://www.kaggle.com/datasets/sumitrodatta/nba-aba-baa-stats) kaggle dataset so either download it using `kaggle` CLI with the command:

```
kaggle datasets download -d sumitrodatta/nba-aba-baa-stats
```

or if you are not familiar with `kaggle` from the command line, you can find help with the installation [here](https://www.kaggle.com/docs/api#interacting-with-datasets). Alternatively download the data manually and place it the root of this folder still zipped. After you've done so, run

```
python preprocess.py 1
```

to build your own `players.json` and `alltime.json` files into the output folder. Alternatively use the ones already provided. If you've already unpacked the dataset, run instead:

```
python preprocess.py 0
```

This repository uses `pandas` for data processing, which can be installed simply by:

```
pip install -r requirements.txt
```

## License

This repository is licensed under the MIT license.
