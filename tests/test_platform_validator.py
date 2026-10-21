
from validators.platform_validator import (
    validate_adobe_metadata,
    validate_shutterstock_metadata,
)


def test_adobe_valid_metadata():
    issues = validate_adobe_metadata(
        filename="coffee.jpg",
        title="Fresh Coffee Cup",
        keyword_count=10,
        adobe_category_id=7,
    )

    assert issues == []


def test_adobe_title_too_long():
    issues = validate_adobe_metadata(
        filename="coffee.jpg",
        title="A" * 71,
        keyword_count=10,
        adobe_category_id=7,
    )

    assert any("Judul terlalu panjang" in issue for issue in issues)


def test_adobe_invalid_keyword_count():
    issues = validate_adobe_metadata(
        filename="coffee.jpg",
        title="Fresh Coffee Cup",
        keyword_count=0,
        adobe_category_id=7,
    )

    assert any("Jumlah keyword" in issue for issue in issues)


def test_shutterstock_valid_metadata():
    issues = validate_shutterstock_metadata(
        filename="coffee.jpg",
        description="A fresh cup of coffee on a wooden table.",
        keyword_count=10,
        category="Food and Drink",
        secondary_category="Objects",
    )

    assert issues == []


def test_shutterstock_description_too_long():
    issues = validate_shutterstock_metadata(
        filename="coffee.jpg",
        description="A" * 151,
        keyword_count=10,
        category="Food and Drink",
        secondary_category="Objects",
    )

    assert any("Deskripsi terlalu panjang" in issue for issue in issues)


def test_shutterstock_too_few_keywords():
    issues = validate_shutterstock_metadata(
        filename="coffee.jpg",
        description="A fresh cup of coffee.",
        keyword_count=6,
        category="Food and Drink",
        secondary_category="Objects",
    )

    assert any("Jumlah keyword" in issue for issue in issues)
