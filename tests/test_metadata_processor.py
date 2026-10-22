
from services.metadata_processor import process_metadata_results


def make_result(
    filename="business.png",
    title="Business Finance Icon",
    description="Business finance illustration",
    keywords=None,
):
    if keywords is None:
        keywords = [
            "business",
            "finance",
            "money",
            "office",
            "investment",
            "banking",
            "icon",
            "vector",
        ]

    return {
        "filename": filename,
        "status": "success",
        "metadata": {},
        "error": "",
        "edited_metadata": {
            "filename": filename,
            "title": title,
            "description": description,
            "keywords": keywords,
            "adobe_category_id": 8,
            "shutterstock_category": "Business/Finance",
            "shutterstock_secondary_category": "",
            "editorial": False,
            "mature_content": False,
            "illustration": True,
        },
    }


def test_valid_metadata_is_prepared_for_both_platforms():
    results = [make_result()]

    adobe_rows, shutterstock_rows, summary = (
        process_metadata_results(results)
    )

    assert len(adobe_rows) == 1
    assert len(shutterstock_rows) == 1
    assert len(summary) == 1
    assert adobe_rows[0]["Filename"] == "business.png"
    assert shutterstock_rows[0]["Filename"] == "business.png"
    assert summary[0]["Adobe Stock"] == "Lulus"
    assert summary[0]["Shutterstock"] == "Lulus"


def test_failed_batch_result_is_skipped():
    failed_result = {
        "filename": "broken.png",
        "status": "error",
        "metadata": {},
        "error": "Simulasi error",
    }

    adobe_rows, shutterstock_rows, summary = (
        process_metadata_results([failed_result])
    )

    assert adobe_rows == []
    assert shutterstock_rows == []
    assert summary == []


def test_metadata_without_edits_is_skipped():
    result = {
        "filename": "not_edited.png",
        "status": "success",
        "metadata": {"title": "Example"},
        "error": "",
    }

    adobe_rows, shutterstock_rows, summary = (
        process_metadata_results([result])
    )

    assert adobe_rows == []
    assert shutterstock_rows == []
    assert summary == []


def test_adobe_and_shutterstock_validation_are_independent():
    result = make_result(
        title="",
        description="Business finance illustration",
    )

    adobe_rows, shutterstock_rows, summary = (
        process_metadata_results([result])
    )

    assert adobe_rows == []
    assert len(shutterstock_rows) == 1
    assert summary[0]["Adobe Stock"] == "Perlu diperbaiki"
    assert summary[0]["Shutterstock"] == "Lulus"