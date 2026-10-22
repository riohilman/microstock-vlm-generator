from validators.metadata_schema import (
    validate_generated_metadata,
)


def make_valid_metadata():
    return {
        "title": "Business Finance Illustration",
        "description": (
            "Business finance illustration with money and charts."
        ),
        "keywords": [
            f"keyword{i}" for i in range(1, 31)
        ],
        "adobe_category_id": 8,
        "shutterstock_categories": [
            "Business/Finance",
            "Technology",
        ],
    }


def test_valid_metadata_passes_schema():
    assert validate_generated_metadata(
        make_valid_metadata()
    ) == []


def test_non_dictionary_response_is_rejected():
    issues = validate_generated_metadata("not a dictionary")

    assert any("objek JSON" in issue for issue in issues)


def test_missing_required_field_is_rejected():
    metadata = make_valid_metadata()
    del metadata["title"]

    issues = validate_generated_metadata(metadata)

    assert any("title" in issue for issue in issues)


def test_title_with_wrong_type_is_rejected():
    metadata = make_valid_metadata()
    metadata["title"] = 123

    issues = validate_generated_metadata(metadata)

    assert any("Title harus berupa string" in issue for issue in issues)


def test_description_over_150_characters_is_rejected():
    metadata = make_valid_metadata()
    metadata["description"] = "A" * 151

    issues = validate_generated_metadata(metadata)

    assert any("150 karakter" in issue for issue in issues)


def test_keywords_must_be_a_list():
    metadata = make_valid_metadata()
    metadata["keywords"] = "business, finance"

    issues = validate_generated_metadata(metadata)

    assert any("daftar string" in issue for issue in issues)


def test_keyword_count_outside_range_is_rejected():
    metadata = make_valid_metadata()
    metadata["keywords"] = ["keyword" + str(i) for i in range(10)]

    issues = validate_generated_metadata(metadata)

    assert any("25 dan 40" in issue for issue in issues)


def test_duplicate_keywords_are_rejected():
    metadata = make_valid_metadata()
    metadata["keywords"][1] = metadata["keywords"][0].upper()

    issues = validate_generated_metadata(metadata)

    assert any("duplikat" in issue for issue in issues)


def test_invalid_adobe_category_is_rejected():
    metadata = make_valid_metadata()
    metadata["adobe_category_id"] = 999

    issues = validate_generated_metadata(metadata)

    assert any("Adobe Stock" in issue for issue in issues)


def test_invalid_shutterstock_category_is_rejected():
    metadata = make_valid_metadata()
    metadata["shutterstock_categories"] = ["Not A Category"]

    issues = validate_generated_metadata(metadata)

    assert any("tidak valid" in issue for issue in issues)


def test_duplicate_shutterstock_categories_are_rejected():
    metadata = make_valid_metadata()
    metadata["shutterstock_categories"] = [
        "Technology",
        "Technology",
    ]

    issues = validate_generated_metadata(metadata)

    assert any("duplikat" in issue for issue in issues)