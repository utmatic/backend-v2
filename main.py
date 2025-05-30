import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import tempfile
import uuid

# For document processing
import fitz  # PyMuPDF for PDFs
import docx
import asyncio

# For link shortener (stub)
import hashlib

# For UTM
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

# For AI (stubbed, replace with real LLM integration)
def ai_generate_text(prompt: str) -> str:
    # Replace with real LLM call (OpenAI, etc.)
    return f"[AI GENERATED] {prompt[:200]}..."

# ----- FastAPI app -----
app = FastAPI(
    title="Content Repurposing Engine",
    description="Generate repurposed content snippets from long-form documents."
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set your allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Helper functions -----
def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def extract_text(file: UploadFile, tmp_path: str) -> str:
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(tmp_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(tmp_path)
    elif ext == ".txt":
        return extract_text_from_txt(tmp_path)
    else:
        return ""  # Skips unsupported files

def build_utm_url(url: str, utm_params: Dict[str, str]) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query))
    query.update(utm_params)
    parsed = parsed._replace(query=urlencode(query))
    return urlunparse(parsed)

def short_link(url: str) -> str:
    # Replace with real shortener (Bitly API, etc.)
    fake_hash = hashlib.sha256(url.encode()).hexdigest()[:8]
    return f"https://short.url/{fake_hash}"

# ----- Pydantic models -----
class OutputItem(BaseModel):
    main_text: str
    cta_text: str
    cta_link: str
    full_text: str
    char_count: int

class RepurposeResponse(BaseModel):
    outputs: List[OutputItem]
    meta: Dict[str, Any]

# ----- Preset endpoints -----
@app.get("/api/presets/channels")
def get_channels():
    return [
        "newsletter", "linkedin", "twitter", "facebook_ad", "custom"
    ]

@app.get("/api/presets/flows")
def get_flows():
    return [
        "nurture", "urgency", "teaser_to_reveal", "custom"
    ]

@app.get("/api/presets/tones")
def get_tones():
    return [
        "conversational", "authoritative", "friendly", "urgent", "witty"
    ]

@app.get("/api/presets/ctas")
def get_ctas(channel: Optional[str] = None):
    ctas = [
        "Learn more", "Sign up", "Download now", "Get started", "Read more",
        "See details", "Try it free"
    ]
    # Could filter by channel if desired
    return ctas

# ----- Main repurpose endpoint -----
@app.post("/api/repurpose", response_model=RepurposeResponse)
async def repurpose(
    files: List[UploadFile] = File(...),
    channel: str = Form(...),
    num_outputs: int = Form(...),
    flow: str = Form(...),
    tone: str = Form(...),
    char_limit: Optional[int] = Form(None),
    char_reserved_for_link: Optional[int] = Form(None),
    cta_type: str = Form(...),
    cta_text: Optional[str] = Form(None),
    destination_url: Optional[str] = Form(None),
    utm_source: Optional[str] = Form(None),
    utm_medium: Optional[str] = Form(None),
    utm_campaign: Optional[str] = Form(None),
    shorten_links: Optional[bool] = Form(False)
):
    # 1. Extract all text
    all_texts = []
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp.flush()
            text = extract_text(file, tmp.name)
            all_texts.append(text)
    big_text = "\n\n".join([t for t in all_texts if t.strip()])

    if not big_text:
        return JSONResponse({"outputs": [], "meta": {"error": "No text extracted from files."}}, status_code=400)

    # 2. Build UTM parameters
    utm_params = {}
    if utm_source: utm_params["utm_source"] = utm_source
    if utm_medium: utm_params["utm_medium"] = utm_medium
    if utm_campaign: utm_params["utm_campaign"] = utm_campaign

    # 3. Generate outputs
    outputs = []
    for i in range(num_outputs):
        # 3.1 Determine CTA
        if cta_type == "custom" and cta_text:
            cta = cta_text
        elif cta_type == "preset":
            # Could randomize or cycle
            preset_ctas = get_ctas()
            cta = preset_ctas[i % len(preset_ctas)]
        else:  # AI-generated CTA (stub)
            cta = ai_generate_text(f"Generate a strong CTA for {channel}, flow {flow}, tone {tone}.")

        # 3.2 Build link
        link = destination_url or "https://example.com"
        if utm_params:
            link = build_utm_url(link, utm_params)
        if shorten_links:
            link = short_link(link)

        # 3.3 Text generation (stub)
        effective_char_limit = char_limit or 300
        reserved = char_reserved_for_link or 0
        prompt = f"Summarize this content for a {channel} post, step {i+1} in a '{flow}' campaign, tone: {tone}. Max {effective_char_limit - reserved} characters. Content: {big_text[:2000]}"
        main_text = ai_generate_text(prompt)[:(effective_char_limit - reserved)]

        # 3.4 Assemble full output
        full_text = f"{main_text.strip()} {cta.strip()} {link}".strip()
        char_count = len(full_text)
        outputs.append(OutputItem(
            main_text=main_text.strip(),
            cta_text=cta.strip(),
            cta_link=link,
            full_text=full_text,
            char_count=char_count
        ))

    meta = {
        "channel": channel,
        "tone": tone,
        "char_limit": char_limit,
        "cta_type": cta_type,
        "flow": flow
    }
    return RepurposeResponse(outputs=outputs, meta=meta)
