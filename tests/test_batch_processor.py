
from io import BytesIO

from services.batch_processor import process_batch


def create_fake_image(filename):
    image = BytesIO(b"fake image data")
    image.name = filename
    return image


def test_process_batch_success(monkeypatch):
    def fake_generator(image):
        return {"title": f"Metadata for {image.name}"}

    monkeypatch.setattr(
        "services.batch_processor.generate_microstock_metadata",
        fake_generator,
    )

    images = [
        create_fake_image("image1.jpg"),
        create_fake_image("image2.jpg"),
    ]

    results = process_batch(images)

    assert len(results) == 2
    assert results[0]["status"] == "success"
    assert results[1]["status"] == "success"
    assert results[0]["metadata"]["title"] == "Metadata for image1.jpg"


def test_process_batch_continues_after_error(monkeypatch):
    def fake_generator(image):
        if image.name == "broken.jpg":
            raise ValueError("Simulasi gambar gagal")

        return {"title": f"Metadata for {image.name}"}

    monkeypatch.setattr(
        "services.batch_processor.generate_microstock_metadata",
        fake_generator,
    )

    images = [
        create_fake_image("first.jpg"),
        create_fake_image("broken.jpg"),
        create_fake_image("third.jpg"),
    ]

    results = process_batch(images)

    assert len(results) == 3
    assert results[0]["status"] == "success"
    assert results[1]["status"] == "error"
    assert "Simulasi gambar gagal" in results[1]["error"]
    assert results[2]["status"] == "success"


def test_process_batch_calls_progress_callback(monkeypatch):
    monkeypatch.setattr(
        "services.batch_processor.generate_microstock_metadata",
        lambda image: {"title": "Test"},
    )

    progress_updates = []
    images = [
        create_fake_image("one.jpg"),
        create_fake_image("two.jpg"),
    ]

    results = process_batch(
        images,
        on_progress=lambda completed, total, filename: (
            progress_updates.append((completed, total, filename))
        ),
    )

    assert len(results) == 2
    assert progress_updates == [
        (1, 2, "one.jpg"),
        (2, 2, "two.jpg"),
    ]