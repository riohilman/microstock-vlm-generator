import pandas as pd
import json
import streamlit as st
from poc_generator import generate_microstock_metadata


ADOBE_CATEGORIES = {
    1: "Animals",
    2: "Buildings and Architecture",
    3: "Business",
    4: "Drinks",
    5: "The Environment",
    6: "States of Mind",
    7: "Food",
    8: "Graphic Resources",
    9: "Hobbies and Leisure",
    10: "Industry",
    11: "Landscape",
    12: "Lifestyle",
    13: "People",
    14: "Plants and Flowers",
    15: "Culture and Religion",
    16: "Science",
    17: "Social Issues",
    18: "Sports",
    19: "Technology",
    20: "Transport",
    21: "Travel",
}

SHUTTERSTOCK_CATEGORIES = [
    "Abstract",
    "Animals/Wildlife",
    "Arts",
    "Backgrounds/Textures",
    "Beauty/Fashion",
    "Buildings/Landmarks",
    "Business/Finance",
    "Celebrities",
    "Education",
    "Food and Drink",
    "Healthcare/Medical",
    "Holidays",
    "Industrial",
    "Interiors",
    "Miscellaneous",
    "Nature",
    "Objects",
    "Parks/Outdoor",
    "People",
    "Religion",
    "Science",
    "Signs/Symbols",
    "Sports/Recreation",
    "Technology",
    "Transportation",
    "Vintage",
]


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

uploaded_file = st.file_uploader(
    "Unggah gambar",
    type=["jpg", "jpeg", "png", "webp"],
)

if uploaded_file is not None:
    st.subheader("Pratinjau gambar")
    st.image(
        uploaded_file,
        caption=uploaded_file.name,
        width="stretch",
    )

    if st.button("Generate Metadata", type="primary"):
        try:
            with st.spinner("Sedang menganalisis gambar..."):
                metadata = generate_microstock_metadata(uploaded_file)

            st.session_state["metadata"] = metadata
            st.session_state["filename"] = uploaded_file.name

        except Exception as error:
            st.error(
                "Metadata gagal dihasilkan. Periksa koneksi internet "
                "dan konfigurasi API, lalu coba kembali."
            )
            st.caption(f"Detail error: {error}")

    if "metadata" in st.session_state:
        metadata = st.session_state["metadata"]

        st.subheader("Hasil Metadata")

        title = st.text_input(
            "Title",
            value=str(metadata.get("title", "")),
            key="edited_title",
        )

        title_length = len(title.strip())
        st.caption(f"Panjang judul: {title_length} karakter")

        if not title.strip():
            st.warning("Judul tidak boleh kosong.")
        elif title_length > 70:
            st.warning(
                "Adobe Stock: judul melebihi batas 70 karakter."
            )

        if "," in title:
            st.warning(
                "Adobe Stock: hindari koma dalam judul CSV."
            )

        description = st.text_area(
            "Description",
            value=str(metadata.get("description", "")),
            height=120,
            key="edited_description",
        )

        description_length = len(description.strip())
        st.caption(
            f"Panjang deskripsi: {description_length} karakter"
        )

        if not description.strip():
            st.warning("Deskripsi tidak boleh kosong.")
        elif description_length > 150:
            st.warning(
                "Shutterstock: deskripsi melebihi batas "
                "150 karakter untuk pengiriman."
            )


        keywords = metadata.get("keywords", [])
        if not isinstance(keywords, list):
            keywords = []

        keywords_text = st.text_area(
            "Keywords (pisahkan dengan koma)",
            value=", ".join(str(keyword) for keyword in keywords),
            height=120,
            key="edited_keywords",
        )

        # Bersihkan spasi dan hapus keyword duplikat
        keywords_list = []
        seen_keywords = set()

        for keyword in keywords_text.split(","):
            keyword = keyword.strip()

            if keyword and keyword.casefold() not in seen_keywords:
                keywords_list.append(keyword)
                seen_keywords.add(keyword.casefold())

        # Tampilkan jumlah keyword setelah dibersihkan
        keyword_count = len(keywords_list)

        st.write(f"Jumlah keyword unik: **{keyword_count}**")

        if keyword_count > 49:
            st.warning(
                "Adobe Stock: jumlah keyword melebihi batas 49 "
                "berdasarkan template yang digunakan."
            )
        elif keyword_count == 0:
            st.warning("Tambahkan keyword yang relevan terlebih dahulu.")
        else:
            st.success("Jumlah keyword berada dalam batas pemeriksaan Adobe Stock.")

        if keyword_count < 7 or keyword_count > 50:
            st.warning(
                "Shutterstock: gunakan 7–50 keyword yang relevan."
            )
        else:
            st.success("Jumlah keyword berada dalam rentang pemeriksaan Shutterstock.")


        st.subheader("Kategori Microstock")

        # Ambil rekomendasi kategori dari AI
        recommended_adobe_id = metadata.get("adobe_category_id", 8)
        if recommended_adobe_id not in ADOBE_CATEGORIES:
            recommended_adobe_id = 8

        recommended_shutterstock = metadata.get(
            "shutterstock_categories", ["Miscellaneous"]
        )
        if not isinstance(recommended_shutterstock, list):
            recommended_shutterstock = ["Miscellaneous"]

        recommended_shutterstock = [
            category
            for category in recommended_shutterstock
            if category in SHUTTERSTOCK_CATEGORIES
        ]

        if not recommended_shutterstock:
            recommended_shutterstock = ["Miscellaneous"]

        adobe_category_id = st.selectbox(
            "Kategori Adobe Stock",
            options=list(ADOBE_CATEGORIES.keys()),
            index=list(ADOBE_CATEGORIES.keys()).index(recommended_adobe_id),
            format_func=lambda category_id: (
                f"{category_id} - {ADOBE_CATEGORIES[category_id]}"
            ),
            key="adobe_category",
        )

        shutterstock_category = st.selectbox(
            "Kategori Shutterstock (utama)",
            options=SHUTTERSTOCK_CATEGORIES,
            index=SHUTTERSTOCK_CATEGORIES.index(
                recommended_shutterstock[0]
            ),
            key="shutterstock_category",
        )

        # Rekomendasi kategori kedua dari AI, jika tersedia
        secondary_options = [
            category
            for category in SHUTTERSTOCK_CATEGORIES
            if category != shutterstock_category
        ]

        recommended_secondary = next(
            (
                category
                for category in recommended_shutterstock[1:]
                if category in secondary_options
            ),
            next(
                (
                    category
                    for category in secondary_options
                    if category == "Objects"
                ),
                secondary_options[0],
            ),
        )

        shutterstock_secondary = st.selectbox(
            "Kategori Shutterstock (kedua, opsional)",
            options=["Tidak ada"] + secondary_options,
            index=(
                secondary_options.index(recommended_secondary) + 1
                if len(recommended_shutterstock) > 1
                else 0
            ),
            key="shutterstock_secondary",
        )


        st.caption(
            "Kategori awal hanya pilihan bawaan. "
            "Pastikan kategori sesuai dengan isi gambar."
        )

        st.subheader("Metadata Tambahan Shutterstock")

        editorial = st.selectbox(
            "Editorial",
            options=["no", "yes"],
            index=0,
            key="shutterstock_editorial",
            help="Pilih yes jika gambar memenuhi ketentuan konten editorial Shutterstock.",
        )

        mature_content = st.selectbox(
            "Mature content",
            options=["no", "yes"],
            index=0,
            key="shutterstock_mature",
            help="Periksa apakah gambar termasuk konten dewasa menurut ketentuan Shutterstock.",
        )

        illustration = st.selectbox(
            "Illustration",
            options=["no", "yes"],
            index=0,
            key="shutterstock_illustration",
            help="Pilih yes jika aset merupakan ilustrasi sesuai definisi Shutterstock.",
        )


        edited_metadata = {
            "filename": st.session_state["filename"],
            "title": title,
            "description": description,
            "keywords": keywords_list,
            "adobe_category_id": adobe_category_id,
            "adobe_category_name": ADOBE_CATEGORIES[adobe_category_id],
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

        # Validasi nama file
        filename = edited_metadata["filename"]

        st.subheader("Validasi Nama File")
        st.caption(
            f"Nama file: {filename} "
            f"({len(filename)} karakter, termasuk ekstensi)"
        )

        if not filename.strip():
            st.error("Nama file tidak boleh kosong.")
        elif len(filename) > 30:
            st.warning(
                "Adobe Stock: nama file melebihi batas 30 karakter. "
                "Periksa nama file aset dan CSV sebelum mengunggah."
            )
        else:
            st.success(
                "Panjang nama file memenuhi batas Adobe Stock."
            )

        if filename != uploaded_file.name:
            st.error(
                "Nama file metadata berbeda dari gambar yang sedang "
                "diunggah. Generate ulang metadata sebelum ekspor."
            )

        # Validasi akhir untuk setiap platform
        filename = edited_metadata["filename"]
        title_value = edited_metadata["title"].strip()
        description_value = edited_metadata["description"].strip()
        keyword_count = len(edited_metadata["keywords"])

        adobe_valid = (
            bool(filename.strip())
            and len(filename) <= 30
            and bool(title_value)
            and len(title_value) <= 70
            and "," not in title_value
            and keyword_count >= 1
            and keyword_count <= 49
        )

        shutterstock_valid = (
            bool(filename.strip())
            and bool(description_value)
            and len(description_value) <= 150
            and 7 <= keyword_count <= 50
            and bool(edited_metadata["shutterstock_category"])
        )

        st.subheader("Status Validasi Ekspor")

        if adobe_valid:
            st.success("Adobe Stock: pemeriksaan dasar lulus.")
        else:
            st.warning(
                "Adobe Stock: periksa nama file, judul, dan jumlah keyword."
            )

        if shutterstock_valid:
            st.success("Shutterstock: pemeriksaan dasar lulus.")
        else:
            st.warning(
                "Shutterstock: periksa nama file, deskripsi, "
                "dan jumlah keyword."
            )

        st.subheader("Pratinjau Kategori")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Adobe Stock**")
            st.write(
                f"{edited_metadata['adobe_category_id']} - "
                f"{edited_metadata['adobe_category_name']}"
            )

        with col2:
            st.write("**Shutterstock**")
            st.write(edited_metadata["shutterstock_category"])

        st.download_button(
            label="Unduh Metadata JSON",
            data=json.dumps(
                edited_metadata,
                ensure_ascii=False,
                indent=2,
            ),
            file_name="microstock_metadata.json",
            mime="application/json",
        )

        st.subheader("Ekspor CSV")

        keywords_list = edited_metadata["keywords"]
        keywords_csv = ", ".join(keywords_list)


        # CSV Adobe Stock
        adobe_df = pd.DataFrame([
            {
                "Filename": edited_metadata["filename"],
                "Title": edited_metadata["title"],
                "Keywords": keywords_csv,
                "Category": edited_metadata["adobe_category_id"],
                "Releases": "",
            }
        ])

        adobe_csv = adobe_df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="Unduh CSV Adobe Stock",
            data=adobe_csv,
            file_name="adobe_stock_metadata.csv",
            mime="text/csv",
            key="download_adobe_csv",
            disabled=not adobe_valid,
        )


        # CSV Shutterstock
        shutterstock_categories = [
            edited_metadata["shutterstock_category"]
        ]

        secondary_category = edited_metadata[
            "shutterstock_secondary_category"
        ]

        if secondary_category:
            shutterstock_categories.append(secondary_category)

        shutterstock_df = pd.DataFrame([
            {
                "Filename": edited_metadata["filename"],
                "Description": edited_metadata["description"],
                "Keywords": keywords_csv,
                "Categories": ", ".join(shutterstock_categories),
                "Editorial": edited_metadata["editorial"],
                "Mature content": edited_metadata["mature_content"],
                "illustration": edited_metadata["illustration"],
            }
        ])

        shutterstock_csv = (
            shutterstock_df.to_csv(index=False).encode("utf-8-sig")
        )

        st.download_button(
            label="Unduh CSV Shutterstock",
            data=shutterstock_csv,
            file_name="shutterstock_metadata.csv",
            mime="text/csv",
            key="download_shutterstock_csv",
            disabled=not shutterstock_valid,
        )