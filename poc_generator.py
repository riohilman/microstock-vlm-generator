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
    image.load()
    
    prompt = """
    Analyze this image for a microstock platform submission.
    Generate metadata in English and return valid JSON using this exact structure:

    {
      "title": "Descriptive title",
      "description": "Detailed description of the image",
      "keywords": ["keyword1", "keyword2"],
      "adobe_category_id": 8,
      "shutterstock_categories": ["Technology", "Business"]
    }

    RULES FOR TITLE AND DESCRIPTION:
    1. Write in English.
    2. The title must accurately describe the image.
    3. The description must explain the main subject, style, composition,
       and relevant context.
    4. Avoid subjective or promotional words such as "best" or "stunning".
    5. The description must contain no more than 150 characters,
       including spaces.
    6. Write a concise, grammatically correct description that
       stays within the limit without cutting off a sentence.

    RULES FOR KEYWORDS:
    5. Provide 25 to 40 relevant English keywords.
    6. Put the most important keywords first.
    7. Avoid irrelevant, repetitive, or misleading keywords.

    ADOBE STOCK CATEGORY:
    Select exactly ONE category ID from this official category list:
    1 = Animals
    2 = Buildings and Architecture
    3 = Business
    4 = Drinks
    5 = The Environment
    6 = States of Mind
    7 = Food
    8 = Graphic Resources
    9 = Hobbies and Leisure
    10 = Industry
    11 = Landscape
    12 = Lifestyle
    13 = People
    14 = Plants and Flowers
    15 = Culture and Religion
    16 = Science
    17 = Social Issues
    18 = Sports
    19 = Technology
    20 = Transport
    21 = Travel

    SHUTTERSTOCK CATEGORIES:
    Select ONE or TWO categories from this exact list:
    Abstract
    Animals/Wildlife
    Arts
    Backgrounds/Textures
    Beauty/Fashion
    Buildings/Landmarks
    Business/Finance
    Celebrities
    Education
    Food and Drink
    Healthcare/Medical
    Holidays
    Industrial
    Interiors
    Miscellaneous
    Nature
    Objects
    Parks/Outdoor
    People
    Religion
    Science
    Signs/Symbols
    Sports/Recreation
    Technology
    Transportation
    Vintage

    CATEGORY SELECTION RULES:
    1. Choose categories based on the actual image content, not merely its
       color, visual style, or file name.
    2. For Adobe Stock, return the numeric category ID, not its name.
    3. For Shutterstock, return category names exactly as written above.
    4. Select the most relevant categories for the image's intended use.
    5. For icons, illustrations, and design assets, consider Graphic Resources
       for Adobe Stock when appropriate.
    6. Do not assume all illustrations belong to Graphic Resources.
    7. Return only valid JSON. Do not include Markdown or additional commentary.
    """

    response = client.models.generate_content(
        model='gemini-3.5-flash-lite',
        contents=[image, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    metadata = json.loads(response.text)

    # Pengaman: batasi deskripsi hingga 150 karakter,
    # tanpa memotong kata di tengah jika memungkinkan.
    description = str(metadata.get("description", "")).strip()

    if len(description) > 150:
        shortened = description[:150]
        if " " in shortened:
            shortened = shortened.rsplit(" ", 1)[0]
        metadata["description"] = shortened.rstrip(" .,;:-")
    else:
        metadata["description"] = description

    return metadata

if __name__ == "__main__":
    test_image = "sample.jpg"
    if os.path.exists(test_image):
        metadata = generate_microstock_metadata(test_image)
        print(json.dumps(metadata, indent=2))
        
        with open("sample_output.json", "w") as f:
            json.dump(metadata, f, indent=2)
    else:
        print(f"File {test_image} tidak ditemukan. Siapkan 1 gambar sampel di direktori proyek.")