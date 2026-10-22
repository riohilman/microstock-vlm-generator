
import json
from unittest.mock import MagicMock, patch

import pytest

import poc_generator


def valid_metadata():
    return {
        "title": "Business Finance Illustration",
        "description": "Business finance illustration with money and charts.",
        "keywords": [f"keyword{i}" for i in range(1, 31)],
        "adobe_category_id": 8,
        "shutterstock_categories": ["Technology", "Business/Finance"],
    }


def mock_response(text):
    response = MagicMock()
    response.text = text
    return response


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
@patch("poc_generator.genai.Client")
@patch("poc_generator.Image.open")
def test_generator_accepts_valid_json(mock_image_open, mock_client_class):
    metadata = valid_metadata()

    mock_image = MagicMock()
    mock_image_open.return_value.__enter__.return_value.copy.return_value = mock_image

    mock_client = mock_client_class.return_value
    mock_client.models.generate_content.return_value = mock_response(
        json.dumps(metadata)
    )

    result = poc_generator.generate_microstock_metadata("sample.jpg")

    assert result == metadata
    mock_client.models.generate_content.assert_called_once()


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
@patch("poc_generator.genai.Client")
@patch("poc_generator.Image.open")
def test_generator_rejects_invalid_json(mock_image_open, mock_client_class):
    mock_image = MagicMock()
    mock_image_open.return_value.__enter__.return_value.copy.return_value = mock_image

    mock_client = mock_client_class.return_value
    mock_client.models.generate_content.return_value = mock_response(
        "{invalid json"
    )

    with pytest.raises(ValueError, match="bukan JSON yang valid"):
        poc_generator.generate_microstock_metadata("sample.jpg")


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
@patch("poc_generator.genai.Client")
@patch("poc_generator.Image.open")
def test_generator_rejects_invalid_schema(mock_image_open, mock_client_class):
    metadata = valid_metadata()
    metadata["title"] = 123

    mock_image = MagicMock()
    mock_image_open.return_value.__enter__.return_value.copy.return_value = mock_image

    mock_client = mock_client_class.return_value
    mock_client.models.generate_content.return_value = mock_response(
        json.dumps(metadata)
    )

    with pytest.raises(ValueError, match="tidak memenuhi skema"):
        poc_generator.generate_microstock_metadata("sample.jpg")


@patch.dict("os.environ", {}, clear=True)
def test_generator_rejects_missing_api_key():
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        poc_generator.generate_microstock_metadata("sample.jpg")