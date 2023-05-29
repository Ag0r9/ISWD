import pandas as pd


def read_csv(filename: str) -> pd.DataFrame:
    return pd.read_csv(filename, sep=";", index_col=0)
