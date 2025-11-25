
import fitz
import json
from typing import List
from bs4 import BeautifulSoup
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

def parse_html(html_content: str) -> str:
    """
    Parses HTML content and returns plain text.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text("\n")

def parse_json_bytes(file_bytes: bytes) -> str:
    """
    Parses JSON bytes and returns formatted string.
    """
    try:
        parsed = json.loads(file_bytes.decode("utf-8"))
        return json.dumps(parsed, indent=2)
    except Exception:
        return file_bytes.decode("utf-8", errors="ignore")

def parse_pdf_bytes(file_bytes: bytes) -> str:
    """
    Parses PDF bytes and returns text.
    """
    text = ""
    try:
        pdf = fitz.open(stream=file_bytes, filetype="pdf")
        for page in pdf:
            text += page.get_text()
    except Exception as e:
        text = f"[ERROR PARSING PDF] {str(e)}"
    return text

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """
    Chunks text into smaller pieces.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
    )
    return splitter.split_text(text)
