import pandas as pd
import json
import streamlit as st
from poc_generator import generate_microstock_metadata
from config.platform_config import (
    ADOBE_CATEGORIES,
    SHUTTERSTOCK_CATEGORIES,
)
from validators.platform_validator import (
    validate_adobe_metadata,
    validate_shutterstock_metadata,
)
from exporters.csv_exporter import (
    export_adobe_csv,
    export_shutterstock_csv,
)

st.set_page_config(
    page_title="Microstock Metadata Generator",
    page_icon="🖼️",
    layout="wide",
)

st.title("Microstock Metadata Generator")
st.write(
    "Generate metadata berbahasa Inggris untuk gambar "
    "yang akan disiapkan ke platform microstock."
)

st.info(
    "Periksa dan edit metadata sebelum digunakan untuk "
    "pengiriman ke platform microstock."
)

uploaded_files = st.file_uploader(
    "Unggah satu atau beberapa gambar",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
)

# Pratinjau semua gambar yang dipilih
if uploaded_files:
    st.subheader("Daftar Gambar")

    st.write(f"Jumlah gambar dipilih: **{len(uploaded_files)}**")

    for index, uploaded_image in enumerate(uploaded_files, start=1):
        with st.expander(
            f"{index}. {uploaded_image.name}",
            expanded=False,
        ):
            st.image(
                uploaded_image,
                caption=uploaded_image.name,
                width="stretch",
            )

    st.subheader("Pemrosesan Batch")

    if st.button(
        "Generate Metadata untuk Semua Gambar",
        type="primary",
        key="generate_batch",
    ):
        batch_results = []

        progress = st.progress(0)
        status_text = st.empty()

        for index, uploaded_image in enumerate(uploaded_files):
            filename = uploaded_image.name

            status_text.text(
                f"Memproses {index + 1}/{len(uploaded_files)}: "
                f"{filename}"
            )

            try:
                uploaded_image.seek(0)

                with st.spinner(f"Menganalisis {filename}..."):
                    metadata = generate_microstock_metadata(
                        uploaded_image
                    )

                if not isinstance(metadata, dict):
                    raise ValueError(
                        "Hasil AI bukan objek metadata yang valid."
                    )

                batch_results.append({
                    "filename": filename,
                    "status": "success",
                    "metadata": metadata,
                    "error": "",
                })

            except Exception as error:
                batch_results.append({
                    "filename": filename,
                    "status": "error",
                    "metadata": {},
                    "error": str(error),
                })

            progress.progress(
                (index + 1) / len(uploaded_files)
            )

        st.session_state["batch_results"] = batch_results

        status_text.text("Pemrosesan batch selesai.")

    # Tampilkan ringkasan hasil batch
    if "batch_results" in st.session_state:
        results = st.session_state["batch_results"]

        successful = sum(
            result["status"] == "success"
            for result in results
        )
        failed = len(results) - successful

        st.subheader("Ringkasan Hasil Batch")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Gambar", len(results))
        col2.metric("Berhasil", successful)
        col3.metric("Gagal", failed)

        for result in results:
            if result["status"] == "success":
                st.success(f"Berhasil: {result['filename']}")
                st.caption(
                    f"Judul: "
                    f"{result['metadata'].get('title', '(kosong)')}"
                )
            else:
                st.error(f"Gagal: {result['filename']}")
                st.caption(f"Detail error: {result['error']}")


if "batch_results" in st.session_state:
    st.subheader("Edit Metadata Setiap Gambar")

    batch_results = st.session_state["batch_results"]

    for index, result in enumerate(batch_results):
        if result["status"] != "success":
            continue

        metadata = result["metadata"]
        filename = result["filename"]

        # Namespace widget berdasarkan indeks agar setiap gambar
        # mempunyai state pengeditan sendiri.
        widget_prefix = f"batch_{index}"

        with st.expander(filename, expanded=(index == 0)):
            st.caption(f"Nama file: {filename}")

            title = st.text_input(
                "Title",
                value=str(metadata.get("title", "")),
                key=f"{widget_prefix}_title",
            )

            description = st.text_area(
                "Description",
                value=str(metadata.get("description", ""))[:150],
                height=100,
                max_chars=150,
                key=f"{widget_prefix}_description",
            )

            raw_keywords = metadata.get("keywords", [])
            if not isinstance(raw_keywords, list):
                raw_keywords = []

            keywords_text = st.text_area(
                "Keywords (pisahkan dengan koma)",
                value=", ".join(
                    str(keyword) for keyword in raw_keywords
                ),
                height=100,
                key=f"{widget_prefix}_keywords",
            )

            # Bersihkan spasi dan hapus duplikat keyword.
            keywords_list = []
            seen_keywords = set()

            for keyword in keywords_text.split(","):
                keyword = keyword.strip()

                if keyword and keyword.casefold() not in seen_keywords:
                    keywords_list.append(keyword)
                    seen_keywords.add(keyword.casefold())

            st.caption(
                f"Jumlah keyword unik: {len(keywords_list)}"
            )

            recommended_adobe_id = metadata.get(
                "adobe_category_id", 8
            )
            if (
                not isinstance(recommended_adobe_id, int)
                or recommended_adobe_id not in ADOBE_CATEGORIES
            ):
                recommended_adobe_id = 8

            adobe_category_id = st.selectbox(
                "Kategori Adobe Stock",
                options=list(ADOBE_CATEGORIES.keys()),
                index=list(ADOBE_CATEGORIES.keys()).index(
                    recommended_adobe_id
                ),
                format_func=lambda category_id: (
                    f"{category_id} - "
                    f"{ADOBE_CATEGORIES[category_id]}"
                ),
                key=f"{widget_prefix}_adobe_category",
            )

            recommended_shutterstock = metadata.get(
                "shutterstock_categories", ["Miscellaneous"]
            )

            if not isinstance(recommended_shutterstock, list):
                recommended_shutterstock = []

            recommended_shutterstock = [
                category
                for category in recommended_shutterstock
                if category in SHUTTERSTOCK_CATEGORIES
            ]

            if not recommended_shutterstock:
                recommended_shutterstock = ["Miscellaneous"]

            shutterstock_category = st.selectbox(
                "Kategori Shutterstock",
                options=SHUTTERSTOCK_CATEGORIES,
                index=SHUTTERSTOCK_CATEGORIES.index(
                    recommended_shutterstock[0]
                ),
                key=f"{widget_prefix}_shutterstock_category",
            )

            secondary_options = [
                category
                for category in SHUTTERSTOCK_CATEGORIES
                if category != shutterstock_category
            ]

            secondary_default = (
                recommended_shutterstock[1]
                if len(recommended_shutterstock) > 1
                and recommended_shutterstock[1] in secondary_options
                else "Tidak ada"
            )

            secondary_choices = ["Tidak ada"] + secondary_options

            shutterstock_secondary = st.selectbox(
                "Kategori Shutterstock kedua (opsional)",
                options=secondary_choices,
                index=secondary_choices.index(secondary_default),
                key=f"{widget_prefix}_shutterstock_secondary",
            )

            editorial = st.selectbox(
                "Editorial",
                options=["no", "yes"],
                key=f"{widget_prefix}_editorial",
            )

            mature_content = st.selectbox(
                "Mature content",
                options=["no", "yes"],
                key=f"{widget_prefix}_mature",
            )

            illustration = st.selectbox(
                "Illustration",
                options=["no", "yes"],
                key=f"{widget_prefix}_illustration",
            )

            # Simpan metadata hasil edit kembali ke item terkait.
            result["edited_metadata"] = {
                "filename": filename,
                "title": title,
                "description": description,
                "keywords": keywords_list,
                "adobe_category_id": adobe_category_id,
                "adobe_category_name": ADOBE_CATEGORIES[
                    adobe_category_id
                ],
                "shutterstock_category": shutterstock_category,
                "shutterstock_secondary_category": (
                    shutterstock_secondary
                    if shutterstock_secondary != "Tidak ada"
                    else ""
                ),
                "editorial": editorial,
                "mature_content": mature_content,
                "illustration": illustration,
            }

    st.session_state["batch_results"] = batch_results

    st.divider()
    st.subheader("Validasi dan Ekspor CSV Batch")

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

        # Validasi metadata menggunakan modul terpisah
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
                "; ".join(adobe_issues)
                if adobe_issues else "-"
            ),
            "Shutterstock": (
                "Lulus" if shutterstock_valid
                else "Perlu diperbaiki"
            ),
            "Masalah Shutterstock": (
                "; ".join(shutterstock_issues)
                if shutterstock_issues else "-"
            ),
            "Jumlah keyword": keyword_count,
        })

        # Masukkan metadata yang lolos validasi Adobe Stock
        if adobe_valid:
            adobe_rows.append({
                "Filename": filename,
                "Title": title,
                "Keywords": ", ".join(keywords),
                "Category": item["adobe_category_id"],
                "Releases": "",
            })

        # Masukkan metadata yang lolos validasi Shutterstock
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

    # Tampilkan hasil validasi
    if validation_summary:
        st.dataframe(
            pd.DataFrame(validation_summary),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info(
            "Belum ada metadata berhasil yang siap divalidasi. "
            "Jalankan batch terlebih dahulu."
        )

    # Ekspor satu CSV Adobe Stock dengan banyak baris
    st.markdown("### Adobe Stock")

    st.write(
        f"Jumlah gambar yang lolos validasi: **{len(adobe_rows)}**"
    )

    adobe_csv = export_adobe_csv(adobe_rows)

    st.download_button(
        label="Unduh CSV Adobe Stock (Batch)",
        data=adobe_csv,
        file_name="adobe_stock_batch.csv",
        mime="text/csv",
        disabled=len(adobe_rows) == 0,
        key="download_adobe_batch",
    )

    # Ekspor satu CSV Shutterstock dengan banyak baris
    st.markdown("### Shutterstock")

    st.write(
        "Jumlah gambar yang lolos validasi: "
        f"**{len(shutterstock_rows)}**"
    )

    shutterstock_csv = export_shutterstock_csv(shutterstock_rows)

    st.download_button(
        label="Unduh CSV Shutterstock (Batch)",
        data=shutterstock_csv,
        file_name="shutterstock_batch.csv",
        mime="text/csv",
        disabled=len(shutterstock_rows) == 0,
        key="download_shutterstock_batch",
    )

    st.caption(
        "Validasi ini merupakan pemeriksaan dasar aplikasi, "
        "bukan jaminan bahwa semua metadata akan diterima platform."
    )