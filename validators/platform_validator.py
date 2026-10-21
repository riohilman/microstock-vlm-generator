
from config.platform_config import (
    ADOBE_CATEGORIES,
    SHUTTERSTOCK_CATEGORIES,
)


def validate_adobe_metadata(
    filename,
    title,
    keyword_count,
    adobe_category_id,
):
    issues = []

    if not filename.strip():
        issues.append("Nama file kosong.")

    if len(filename) > 30:
        issues.append("Nama file melebihi 30 karakter.")

    if not title:
        issues.append("Judul kosong.")

    if len(title) > 70:
        issues.append(
            f"Judul terlalu panjang ({len(title)} karakter; "
            "maksimal 70)."
        )

    if "," in title:
        issues.append(
            "Judul mengandung koma; hapus koma sebelum ekspor."
        )

    if not (1 <= keyword_count <= 49):
        issues.append(
            f"Jumlah keyword {keyword_count}; "
            "gunakan 1–49 keyword."
        )

    if adobe_category_id not in ADOBE_CATEGORIES:
        issues.append("Kategori Adobe Stock tidak valid.")

    return issues


def validate_shutterstock_metadata(
    filename,
    description,
    keyword_count,
    category,
    secondary_category,
):
    issues = []

    if not filename.strip():
        issues.append("Nama file kosong.")

    if not description:
        issues.append("Deskripsi kosong.")

    if len(description) > 150:
        issues.append(
            f"Deskripsi terlalu panjang ({len(description)} "
            "karakter; maksimal 150)."
        )

    if not (7 <= keyword_count <= 50):
        issues.append(
            f"Jumlah keyword {keyword_count}; "
            "gunakan 7–50 keyword."
        )

    if category not in SHUTTERSTOCK_CATEGORIES:
        issues.append(
            "Kategori utama Shutterstock tidak valid."
        )

    if (
        secondary_category
        and secondary_category not in SHUTTERSTOCK_CATEGORIES
    ):
        issues.append(
            "Kategori kedua Shutterstock tidak valid."
        )

    return issues
