import os
import json
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_microstock_metadata(image_path: str):
    image = Image.open(image_path)
    
    prompt = """
    Analyze this image for a microstock platform submission.
    Generate metadata in JSON format strictly matching this structure:
    {
      "title": "Descriptive title (5-10 words)",
      "description": "Detailed description about object, style, composition, and context",
      "keywords": ["tag1", "tag2", ...]
    }

    Rules:
    1. Language MUST be English.
    2. Provide 25 to 40 relevant microstock keywords/tags.
    3. Do not include subjective or promotional words (e.g., 'best', 'stunning').
    """

    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=[image, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    return json.loads(response.text)

if __name__ == "__main__":
    test_image = "sample.jpg"
    if os.path.exists(test_image):
        metadata = generate_microstock_metadata(test_image)
        print(json.dumps(metadata, indent=2))
        
        with open("sample_output.json", "w") as f:
            json.dump(metadata, f, indent=2)
    else:
        print(f"File {test_image} tidak ditemukan. Siapkan 1 gambar sampel di direktori proyek.")