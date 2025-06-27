from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from vertexai.generative_models import GenerativeModel, GenerationConfig
import vertexai
from google import genai
from google.genai import types
import asyncio
from dotenv import load_dotenv
import os
import re
import tiktoken  

load_dotenv()

app = FastAPI()

# Google Cloud project details
project = os.getenv("GENAI_PROJECT")
location = os.getenv("GENAI_LOCATION")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "peppy-linker-332510-c7733d076051.json"

vertexai.init(project=project, location=location)


# Pydantic model
class PromptInput(BaseModel):
    prompt: str

# Load base system prompt from file
def load_system_prompt() -> str:
    with open("prompts/bento_prompt_new.txt", "r", encoding="utf-8") as file:
        return file.read()

# Replace placeholder with actual prompt
def build_prompt(user_prompt: str) -> str:
    template = load_system_prompt()
    return template.replace("[Target Persona: e.g., a baker who recently opened a bakery]", user_prompt)

def clean_code_fence(message: str) -> str:
    return re.sub(r"```(?:json)?\s*|\s*```", "", message).strip()

# Token count using GPT tokenizer (approximation)
def count_tokens(text: str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-4")  # Closest available tokenizer
    return len(encoding.encode(text))


# Endpoint
# Non-streaming generation endpoint
@app.post("/generate-bento-site")
async def generate_bento_site(data: PromptInput):
    try:
        prompt = build_prompt(data.prompt)
        model = GenerativeModel("gemini-2.5-flash")

        response = model.generate_content(
            prompt,
            generation_config=GenerationConfig(
                temperature=1.0,
                top_p=1.0,
                max_output_tokens=65535,
            )
        )
        clean_output = clean_code_fence(response.text)
        output = response.text.strip()
        token_count = count_tokens(output)

        return {"output": clean_output, "tokens": token_count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))