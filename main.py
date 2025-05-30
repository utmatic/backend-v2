from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import tempfile
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import random

app = FastAPI()

# --- CORS: Allow multiple origins ---
ALLOWED_ORIGINS = [
    "https://frontend-v2-eight-rosy.vercel.app",
    # add more as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data models ---
class LinkReport(BaseModel):
    url: str
    http_status: Optional[int]
    status_method: Optional[str]
    content_flags: Optional[List[str]]
    error: Optional[str]

class PDFReport(BaseModel):
    links: List[LinkReport]

# --- User Agents List ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

# --- Full browser headers ---
def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/",
        "DNT": "1",  # Do Not Track
        "Upgrade-Insecure-Requests": "1",
    }

KEYWORDS = [
    "not valid", "not available", "out of stock", "product not found",
    "obsolete", "discontinued", "no longer available", "404 not found",
    "page not found", "temporarily unavailable", "unavailable"
]

def extract_links_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    links = set()
    for page in doc:
        for link in page.get_links():
            if 'uri' in link:
                links.add(link['uri'])
    return list(links)

def check_link_status(url):
    # Try HEAD first, then fallback to GET if 403 or method not allowed
    headers = get_headers()
    error = None
    try:
        resp = requests.head(url, allow_redirects=True, timeout=6, headers=headers)
        if resp.status_code == 403 or resp.status_code == 405 or resp.status_code == 401:
            # Try GET if forbidden, unauthorized, or method not allowed
            resp = requests.get(url, allow_redirects=True, timeout=8, headers=headers, stream=True)
            return resp.status_code, "GET", None
        return resp.status_code, "HEAD", None
    except requests.exceptions.RequestException as e:
        error = f"HEAD fail: {str(e)}"
        try:
            resp = requests.get(url, allow_redirects=True, timeout=8, headers=headers, stream=True)
            return resp.status_code, "GET", error
        except requests.exceptions.RequestException as e2:
            return None, None, f"{error}; GET fail: {str(e2)}"

def analyze_link_content(url):
    headers = get_headers()
    try:
        resp = requests.get(url, timeout=10, headers=headers)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(" ", strip=True).lower()
        hits = [kw for kw in KEYWORDS if kw in text]
        return hits
    except Exception:
        return ["fetch_error"]

def is_cloud_blocked(status_code, error_msg):
    # Heuristic: if all links get 403/451 or errors mentioning block, likely IP-level block
    if status_code in {403, 451}:
        return True
    if error_msg and ("blocked" in error_msg or "Cloudflare" in error_msg):
        return True
    return False

@app.post("/check_pdf_links", response_model=PDFReport)
async def check_pdf_links(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        pdf_path = tmp.name

    links = extract_links_from_pdf(pdf_path)
    report_items = []
    all_forbidden = True
    forbidden_count = 0

    for link in links:
        status, method, error = check_link_status(link)
        analysis = None
        if status == 200:
            analysis = analyze_link_content(link)
            all_forbidden = False
        elif is_cloud_blocked(status, error):
            forbidden_count += 1

        report_items.append(LinkReport(
            url=link,
            http_status=status,
            status_method=method,
            content_flags=analysis,
            error=error
        ))

    # If all links failed due to 403/451, likely IP ban: include a hint
    if len(links) > 0 and forbidden_count == len(links):
        report_items.append(LinkReport(
            url="ALL LINKS",
            http_status=403,
            status_method=None,
            content_flags=[],
            error="All links returned 403/451. Likely your cloud provider's IP is blocked by these sites."
        ))

    return PDFReport(links=report_items)
