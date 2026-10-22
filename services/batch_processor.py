
from poc_generator import generate_microstock_metadata


def process_batch(uploaded_files, on_progress=None):
    """
    Memproses beberapa gambar dan mengembalikan hasil setiap gambar.

    on_progress, jika diberikan, dipanggil setelah setiap gambar
    selesai diproses dengan argumen:
    (jumlah_selesai, total_gambar, nama_file).
    """
    batch_results = []
    total_files = len(uploaded_files)

    for index, uploaded_image in enumerate(uploaded_files):
        filename = uploaded_image.name

        try:
            uploaded_image.seek(0)
            metadata = generate_microstock_metadata(uploaded_image)

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

        if on_progress is not None:
            on_progress(index + 1, total_files, filename)

    return batch_results