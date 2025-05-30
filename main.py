from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import tempfile
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# CORS: allow your deployed frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-v2-eight-rosy.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class LinkReport(BaseModel):
    url: str
    http_status: Optional[int]
    content_flags: Optional[List[str]]

class PDFReport(BaseModel):
    links: List[LinkReport]

def extract_links_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    links = set()
    for page in doc:
        for link in page.get_links():
            if 'uri' in link:
                links.add(link['uri'])
    return list(links)

def check_link_status(url):
    try:
        resp = requests.head(url, allow_redirects=True, timeout=5)
        return resp.status_code
    except Exception:
        return None

KEYWORDS = [
    "not valid", "not available", "out of stock", "product not found",
    "obsolete", "discontinued", "no longer available"
]

def analyze_link_content(url):
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(" ", strip=True).lower()
        hits = [kw for kw in KEYWORDS if kw in text]
        return hits
    except Exception:
        return ["fetch_error"]

@app.post("/check_pdf_links", response_model=PDFReport)
async def check_pdf_links(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        pdf_path = tmp.name

    links = extract_links_from_pdf(pdf_path)
    report_items = []
    for link in links:
        status = check_link_status(link)
        analysis = None
        if status == 200:
            analysis = analyze_link_content(link)
        report_items.append(LinkReport(
            url=link,
            http_status=status,
            content_flags=analysis
        ))

    return PDFReport(links=report_items)
