
from config.platform_config import (
    ADOBE_CATEGORIES,
    SHUTTERSTOCK_CATEGORIES,
)


def validate_generated_metadata(metadata):
    """
    Memvalidasi struktur dan tipe data metadata hasil AI.

    Mengembalikan daftar pesan kesalahan.
    Jika daftar kosong, metadata lolos validasi skema.
    """

    issues = []

    if not isinstance(metadata, dict):
        return ["Respons AI harus berupa objek JSON."]

    required_fields = {
        "title",
        "description",
        "keywords",
        "adobe_category_id",
        "shutterstock_categories",
    }

    missing_fields = required_fields - metadata.keys()

    for field in sorted(missing_fields):
        issues.append(f"Field wajib tidak ditemukan: {field}.")

    # Validasi title
    title = metadata.get("title")

    if "title" in metadata:
        if not isinstance(title, str):
            issues.append("Title harus berupa string.")
        elif not title.strip():
            issues.append("Title tidak boleh kosong.")
        elif len(title.strip()) > 70:
            issues.append("Title melebihi 70 karakter.")

    # Validasi description
    description = metadata.get("description")

    if "description" in metadata:
        if not isinstance(description, str):
            issues.append("Description harus berupa string.")
        elif not description.strip():
            issues.append("Description tidak boleh kosong.")
        elif len(description.strip()) > 150:
            issues.append("Description melebihi 150 karakter.")

    # Validasi keywords
    keywords = metadata.get("keywords")

    if "keywords" in metadata:
        if not isinstance(keywords, list):
            issues.append("Keywords harus berupa daftar string.")
        else:
            if not all(
                isinstance(keyword, str) and keyword.strip()
                for keyword in keywords
            ):
                issues.append(
                    "Setiap keyword harus berupa string "
                    "yang tidak kosong."
                )

            if not 25 <= len(keywords) <= 40:
                issues.append(
                    "Jumlah keywords harus antara 25 dan 40."
                )

            valid_keywords = [
                keyword.strip().casefold()
                for keyword in keywords
                if isinstance(keyword, str) and keyword.strip()
            ]

            if len(valid_keywords) != len(set(valid_keywords)):
                issues.append("Keywords tidak boleh duplikat.")

    # Validasi kategori Adobe Stock
    adobe_category_id = metadata.get("adobe_category_id")

    if "adobe_category_id" in metadata:
        if (
            isinstance(adobe_category_id, bool)
            or not isinstance(adobe_category_id, int)
            or adobe_category_id not in ADOBE_CATEGORIES
        ):
            issues.append(
                "adobe_category_id harus berupa ID kategori "
                "Adobe Stock yang valid."
            )

    # Validasi kategori Shutterstock
    shutterstock_categories = metadata.get(
        "shutterstock_categories"
    )

    if "shutterstock_categories" in metadata:
        if not isinstance(shutterstock_categories, list):
            issues.append(
                "shutterstock_categories harus berupa daftar."
            )
        else:
            if not 1 <= len(shutterstock_categories) <= 2:
                issues.append(
                    "Shutterstock harus memiliki satu atau "
                    "dua kategori."
                )

            if not all(
                isinstance(category, str)
                and category in SHUTTERSTOCK_CATEGORIES
                for category in shutterstock_categories
            ):
                issues.append(
                    "Terdapat kategori Shutterstock yang tidak valid."
                )

            valid_categories = [
                category
                for category in shutterstock_categories
                if isinstance(category, str)
                and category in SHUTTERSTOCK_CATEGORIES
            ]

            if len(valid_categories) != len(set(valid_categories)):
                issues.append(
                    "Kategori Shutterstock tidak boleh duplikat."
                )

    return issues