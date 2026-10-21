
import pandas as pd


ADOBE_COLUMNS = [
    "Filename",
    "Title",
    "Keywords",
    "Category",
    "Releases",
]

SHUTTERSTOCK_COLUMNS = [
    "Filename",
    "Description",
    "Keywords",
    "Categories",
    "Editorial",
    "Mature content",
    "illustration",
]


def export_adobe_csv(rows):
    dataframe = pd.DataFrame(rows, columns=ADOBE_COLUMNS)
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def export_shutterstock_csv(rows):
    dataframe = pd.DataFrame(
        rows,
        columns=SHUTTERSTOCK_COLUMNS,
    )
    return dataframe.to_csv(index=False).encode("utf-8-sig")