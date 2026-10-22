
from validators.platform_validator import (
    validate_adobe_metadata,
    validate_shutterstock_metadata,
)


def process_metadata_results(batch_results):
    adobe_rows = []
    shutterstock_rows = []
    validation_summary = []

    for result in batch_results:
        if result["status"] != "success":
            continue

        item = result.get("edited_metadata")
        if not item:
            continue

        filename = item["filename"]
        title = item["title"].strip()
        description = item["description"].strip()
        keywords = item["keywords"]
        keyword_count = len(keywords)

        adobe_issues = validate_adobe_metadata(
            filename=filename,
            title=title,
            keyword_count=keyword_count,
            adobe_category_id=item["adobe_category_id"],
        )

        shutterstock_issues = validate_shutterstock_metadata(
            filename=filename,
            description=description,
            keyword_count=keyword_count,
            category=item["shutterstock_category"],
            secondary_category=item["shutterstock_secondary_category"],
        )

        adobe_valid = len(adobe_issues) == 0
        shutterstock_valid = len(shutterstock_issues) == 0

        validation_summary.append({
            "Filename": filename,
            "Adobe Stock": (
                "Lulus" if adobe_valid else "Perlu diperbaiki"
            ),
            "Masalah Adobe Stock": (
                "; ".join(adobe_issues) if adobe_issues else "-"
            ),
            "Shutterstock": (
                "Lulus" if shutterstock_valid else "Perlu diperbaiki"
            ),
            "Masalah Shutterstock": (
                "; ".join(shutterstock_issues)
                if shutterstock_issues else "-"
            ),
            "Jumlah keyword": keyword_count,
        })

        if adobe_valid:
            adobe_rows.append({
                "Filename": filename,
                "Title": title,
                "Keywords": ", ".join(keywords),
                "Category": item["adobe_category_id"],
                "Releases": "",
            })

        if shutterstock_valid:
            categories = [item["shutterstock_category"]]
            secondary = item["shutterstock_secondary_category"]

            if secondary and secondary not in categories:
                categories.append(secondary)

            shutterstock_rows.append({
                "Filename": filename,
                "Description": description,
                "Keywords": ", ".join(keywords),
                "Categories": ", ".join(categories),
                "Editorial": item["editorial"],
                "Mature content": item["mature_content"],
                "illustration": item["illustration"],
            })

    return adobe_rows, shutterstock_rows, validation_summary