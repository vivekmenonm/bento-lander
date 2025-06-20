from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
import json

from generator import generate_layout, enrich_images

layout_store = {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

@app.post("/generate-layout-progressive")
async def generate_layout_with_icons(request: PromptRequest, background_tasks: BackgroundTasks):
    try:
        session_id = str(uuid4())
        raw_layout = generate_layout(request.prompt)

        if not raw_layout.strip().startswith("{"):
            return JSONResponse(status_code=500, content={"error": "Generated layout is not valid JSON"})

        layout_store[session_id] = {
            "layout": raw_layout,
            "status": "partial"
        }

        background_tasks.add_task(enrich_images, session_id, layout_store)

        return {
            "session_id": session_id,
            "layout": json.loads(raw_layout),
            "status": "partial"
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Layout generation failed: {str(e)}"})

@app.get("/get-layout/{session_id}")
async def get_layout(session_id: str):
    if session_id not in layout_store:
        return JSONResponse(status_code=404, content={"error": "Layout not found"})

    session_data = layout_store[session_id]
    layout = session_data.get("layout", "")

    if isinstance(layout, str):
        if not layout.strip():
            return JSONResponse(status_code=400, content={"error": "Layout is empty or invalid"})
        try:
            parsed_layout = json.loads(layout)
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Failed to parse layout JSON: {str(e)}"})
    else:
        parsed_layout = layout

    return {
        "layout": parsed_layout,
        "status": session_data["status"]
    }
