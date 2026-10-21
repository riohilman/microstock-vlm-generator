
import pandas as pd

from exporters.csv_exporter import (
    export_adobe_csv,
    export_shutterstock_csv,
)


def test_export_adobe_csv_has_correct_columns():
    rows = [
        {
            "Filename": "icon.png",
            "Title": "Business Icon",
            "Keywords": "business, icon, finance",
            "Category": 8,
            "Releases": "",
        }
    ]

    csv_bytes = export_adobe_csv(rows)
    dataframe = pd.read_csv(
        __import__("io").BytesIO(csv_bytes),
        keep_default_na=False,
    )

    assert list(dataframe.columns) == [
        "Filename",
        "Title",
        "Keywords",
        "Category",
        "Releases",
    ]
    assert dataframe.iloc[0]["Filename"] == "icon.png"
    assert dataframe.iloc[0]["Title"] == "Business Icon"


def test_export_shutterstock_csv_has_correct_columns():
    rows = [
        {
            "Filename": "photo.jpg",
            "Description": "A business photo",
            "Keywords": "business, office, work",
            "Categories": "Business/Finance",
            "Editorial": False,
            "Mature content": False,
            "illustration": False,
        }
    ]

    csv_bytes = export_shutterstock_csv(rows)
    dataframe = pd.read_csv(
        __import__("io").BytesIO(csv_bytes),
        keep_default_na=False,
    )

    assert list(dataframe.columns) == [
        "Filename",
        "Description",
        "Keywords",
        "Categories",
        "Editorial",
        "Mature content",
        "illustration",
    ]
    assert dataframe.iloc[0]["Filename"] == "photo.jpg"
    assert dataframe.iloc[0]["Description"] == "A business photo"