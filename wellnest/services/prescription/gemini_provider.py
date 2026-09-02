
from io import BytesIO
from pathlib import Path

import frappe
from PIL import Image
from google import genai
from google.genai import types

from .models import Prescription


def clean_response(obj):
    if isinstance(obj, dict):
        cleaned = {}

        for key, value in obj.items():
            value = clean_response(value)

            if value not in (None, {}, []):
                cleaned[key] = value

        return cleaned

    if isinstance(obj, list):
        cleaned = [clean_response(item) for item in obj]
        return [item for item in cleaned if item not in (None, {}, [])]

    return obj


def _get_client():
    api_key = frappe.get_site_config().get("gemini_api_key")

    if not api_key:
        frappe.throw("Gemini API key is not configured.")

    return genai.Client(api_key=api_key)


BASE_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BASE_DIR / "prescription_prompt.txt"

if not PROMPT_PATH.exists():
    raise FileNotFoundError(f"Prompt file not found: {PROMPT_PATH}")

PROMPT = PROMPT_PATH.read_text(encoding="utf-8")


def parse_prescription(image_bytes: bytes):
    """Parse a prescription image using Gemini 2.5 Flash."""

    client = _get_client()

    image = Image.open(BytesIO(image_bytes))

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            PROMPT,
            image,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Prescription,
            temperature=0,
        ),
    )

    usage = response.usage_metadata

    print("\n========== Prescription Parsing ==========")
    print("Model           : Gemini 2.5 Flash")
    print(f"Prompt Tokens   : {usage.prompt_token_count:,}")
    print(f"Response Tokens : {usage.candidates_token_count:,}")
    print(f"Total Tokens    : {usage.total_token_count:,}")
    print("==========================================\n")

    result = response.parsed.model_dump(exclude_none=True)

    return clean_response(result)
