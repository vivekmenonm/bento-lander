import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from dalle import generate_icon, generate_image

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a structured bento-style website layout generator.

Requirements:
- Return a strict JSON object with three keys: id, title, layout (array of blocks).
- Use a 4-column CSS grid layout. Each block must include colSpan and rowSpan (values: 1 or 2).
- Allowed block types: hero, skills, tools, companies, contact, education, philosophy, values.
- Icons ONLY in: skills, tools, companies, contact.
- NO icons in: philosophy, values, education.
- Hero block must include image, name, title, description.
- Use Tailwind CSS classes for styling (e.g. bg-white, text-gray-900).
- Use gradient backgrounds for hero blocks only.
- Do not include markdown, comments, or explanation — only return valid raw JSON.
"""

def generate_layout(user_prompt: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )
    content = completion.choices[0].message.content.strip()
    if content.startswith("```json"):
        content = content.replace("```json", "").replace("```", "").strip()
    elif content.startswith("```"):
        content = content.replace("```", "").strip()
    return content


def enrich_images(session_id, layout_store):
    try:
        raw_layout = layout_store[session_id]["layout"]
        layout_data = json.loads(raw_layout) if isinstance(raw_layout, str) else raw_layout

        for block in layout_data.get("layout", []):
            block_type = block.get("type", "")

            # Inject DALL·E icon for icon elements
            if block_type in ["skills", "tools", "companies", "contact"]:
                for element in block.get("content", {}).get("elements", []):
                    if element.get("type") == "icon" and not element.get("iconURL"):
                        label = element.get("label", "Generic Icon")
                        element["iconURL"] = generate_icon(f"Flat minimal icon for {label}, digital UI style")

            # Inject profile photo in hero block
            elif block_type == "hero":
                for element in block.get("content", {}).get("elements", []):
                    if element["type"] == "image" and not element.get("src", "").startswith("http"):
                        element["src"] = generate_image("Professional profile photo, headshot, centered on white background")

            # Optional: Generate project images or any custom section
            elif block_type == "projects":
                for element in block.get("content", {}).get("elements", []):
                    if element.get("type") == "image" and not element.get("src", "").startswith("http"):
                        title = element.get("label", "Tech Project")
                        element["src"] = generate_image(f"Tech portfolio project cover image for {title}")

        layout_store[session_id]["layout"] = layout_data
        layout_store[session_id]["status"] = "complete"

    except Exception as e:
        layout_store[session_id]["status"] = f"error: {str(e)}"


