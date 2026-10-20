
import json

import streamlit as st

from poc_generator import generate_microstock_metadata


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
    "Periksa dan edit kembali metadata yang dihasilkan "
    "sebelum menggunakannya untuk pengiriman ke platform."
)

uploaded_file = st.file_uploader(
    "Unggah gambar",
    type=["jpg", "jpeg", "png", "webp"],
)

if uploaded_file is not None:
    st.subheader("Pratinjau gambar")
    st.image(uploaded_file, caption=uploaded_file.name, width="stretch")

    if st.button("Generate Metadata", type="primary"):
        try:
            with st.spinner("Sedang menganalisis gambar..."):
                metadata = generate_microstock_metadata(uploaded_file)

            st.success("Metadata berhasil dihasilkan.")

            st.subheader("Hasil Metadata")

            title = st.text_input(
                "Title",
                value=str(metadata.get("title", "")),
            )

            description = st.text_area(
                "Description",
                value=str(metadata.get("description", "")),
                height=120,
            )

            keywords = metadata.get("keywords", [])

            if not isinstance(keywords, list):
                keywords = []

            keywords_text = st.text_area(
                "Keywords (pisahkan dengan koma)",
                value=", ".join(str(keyword) for keyword in keywords),
                height=120,
            )

            st.caption(
                "Kamu dapat mengedit title, description, dan keywords "
                "sebelum menyimpan hasilnya."
            )

            edited_metadata = {
                "title": title,
                "description": description,
                "keywords": [
                    keyword.strip()
                    for keyword in keywords_text.split(",")
                    if keyword.strip()
                ],
            }

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

        except Exception as error:
            st.error(
                "Metadata gagal dihasilkan. Periksa koneksi internet "
                "dan konfigurasi API, lalu coba kembali."
            )
            st.caption(f"Detail error: {error}")
