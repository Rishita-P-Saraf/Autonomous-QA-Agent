
from dotenv import load_dotenv
import os
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pathlib import Path
import json
import uuid
import traceback


from .services import parser as parser_mod
from .services import embeddings as emb_mod
from .services import vectorstore as vs_mod
from .services import rag_agent as rag_mod
from .services import selenium_builder as sb_mod

app = FastAPI(title="Autonomous QA Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parents[2]
ASSETS_DIR = BASE_DIR / "assets"
KB_DIR = BASE_DIR / "kb"
ASSETS_DIR.mkdir(exist_ok=True)
KB_DIR.mkdir(exist_ok=True)

EMBEDDER = None
VECTOR_STORE = None
HTML_CONTENT = ""
INGESTED_CHUNKS = []
GENERATED_TESTCASES = {}

@app.on_event("startup")
def startup_event():
    global EMBEDDER, VECTOR_STORE

    try:
        EMBEDDER = emb_mod.EmbeddingModel()
        dim = EMBEDDER.model.get_sentence_embedding_dimension()
        VECTOR_STORE = vs_mod.FaissStore(dim=dim)
        app.logger = getattr(app, "logger", None)
    except Exception as e:
        print("Failed to initialize embedding model or vector store:", e)
        raise


def _save_file_to_assets(upload: UploadFile, filename: str = None) -> Path:
    filename = filename or upload.filename
    dest = ASSETS_DIR / filename

    with dest.open("wb") as f:
        f.write(upload.file.read())
    return dest

def _parse_and_chunk(file_path: Path, filename: str):
    """
    Parse a file based on extension, return text string.
    """
    ext = file_path.suffix.lower()
    raw_text = ""
    with file_path.open("rb") as f:
        b = f.read()
    if ext in [".md", ".txt"]:

        raw_text = b.decode("utf-8", errors="ignore")
    elif ext in [".html", ".htm"]:
        raw_text = parser_mod.parse_html(b.decode("utf-8", errors="ignore"))
    elif ext == ".json":
        raw_text = parser_mod.parse_json_bytes(b)
    elif ext == ".pdf":
        raw_text = parser_mod.parse_pdf_bytes(b)
    else:

        try:
            raw_text = b.decode("utf-8", errors="ignore")
        except Exception:
            raw_text = ""
    return raw_text



@app.post("/upload_support_doc")
async def upload_support_doc(file: UploadFile = File(...)):
    """
    Upload a support document (md/txt/json/pdf/html). File is saved to assets/.
    Returns basic metadata.
    """
    try:
        saved = _save_file_to_assets(file)
        return JSONResponse({"status": "ok", "filename": saved.name, "path": str(saved)})
    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}\n{tb}")

@app.post("/upload_checkout_html")
async def upload_checkout_html(file: UploadFile = File(...)):
    """
    Upload the checkout.html file. We store its raw HTML (text) in memory for later selector extraction.
    """
    global HTML_CONTENT
    try:
        saved = _save_file_to_assets(file, filename="checkout.html")

        content = saved.read_text(encoding="utf-8", errors="ignore")
        HTML_CONTENT = content
        return JSONResponse({"status": "ok", "filename": saved.name, "message": "checkout.html uploaded and parsed"})
    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Failed to upload checkout.html: {e}\n{tb}")

@app.post("/build_kb")
async def build_kb():
    """
    Build the knowledge base from all files present in assets/.
    - Parses each file
    - Chunks text
    - Embeds chunks and adds to FAISS store with metadata
    """
    global INGESTED_CHUNKS, VECTOR_STORE, EMBEDDER
    INGESTED_CHUNKS = []
    try:
        assets = list(ASSETS_DIR.iterdir())
        all_texts = []
        metadatas = []
        for p in assets:

            if p.is_file() and p.suffix.lower() in [".md", ".txt", ".json", ".pdf", ".html", ".htm"]:
                raw = _parse_and_chunk(p, p.name)
                if not raw or raw.strip() == "":
                    continue

                chunks = parser_mod.chunk_text(raw, chunk_size=800, overlap=100)
                for idx, c in enumerate(chunks):
                    meta = {
                        "source": p.name,
                        "chunk_id": idx,
                        "char_start": idx * (800 - 100),
                        "char_end": min(len(raw), (idx + 1) * 800),
                        "text_preview": c[:200],
                    }
                    all_texts.append(c)
                    metadatas.append(meta)
        if not all_texts:
            return JSONResponse({"status": "no_data", "message": "No valid files/chunks found in assets/ to build KB."})
        vectors = EMBEDDER.embed(all_texts)
        VECTOR_STORE.add(vectors.astype("float32"), metadatas)
        INGESTED_CHUNKS = metadatas
        return JSONResponse({"status": "ok", "ingested_chunks": len(all_texts)})
    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Failed to build KB: {e}\n{tb}")

@app.post("/generate_testcases")
async def generate_testcases(
    user_request: str = Form(...), 
    top_k: int = 5,
    x_groq_api_key: str = Header(None),
    x_llm_provider: str = Header("groq")
):
    """
    RAG pipeline:
    - Embed the user's request
    - Retrieve top_k chunks from VECTOR_STORE
    - Call the LLM agent to generate structured testcases (JSON text)
    Stores the generated testcases in memory and returns an id to fetch them.
    """
    global GENERATED_TESTCASES, VECTOR_STORE, EMBEDDER
    if VECTOR_STORE is None:
        raise HTTPException(status_code=500, detail="Vector store not initialized. Call /build_kb first.")
    try:
        q_vec = EMBEDDER.embed([user_request]).astype("float32")
        retrieved = VECTOR_STORE.query(q_vec, top_k=top_k)  # list of metadata dicts

        context_chunks = []
        for r in retrieved:

            source_name = r.get("source")
            preview = r.get("text_preview", "")

            context_chunks.append(f"Filename: {source_name}\n\n{preview}\n")

        generated_text = rag_mod.generate_testcases(context_chunks, user_request, api_key=x_groq_api_key, provider=x_llm_provider)

        tc_id = str(uuid.uuid4())
        GENERATED_TESTCASES[tc_id] = {"request": user_request, "retrieved": retrieved, "output": generated_text}
        return JSONResponse({"status": "ok", "testcases_id": tc_id, "preview": generated_text[:1000]})
    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate testcases: {e}\n{tb}")

@app.get("/testcases/{tc_id}")
async def get_testcases(tc_id: str):
    """
    Retrieve previously generated testcases by id.
    """
    if tc_id not in GENERATED_TESTCASES:
        raise HTTPException(status_code=404, detail="Testcases id not found")
    return JSONResponse(GENERATED_TESTCASES[tc_id])

@app.post("/generate_selenium_script")
async def generate_selenium_script(
    testcases_id: str = Form(...), 
    testcase_index: int = Form(0),
    x_groq_api_key: str = Header(None),
    x_llm_provider: str = Header("groq")
):
    """
    Generate a runnable Selenium Python script for one selected testcase.
    Inputs:
      - testcases_id: id received from /generate_testcases
      - testcase_index: index into the JSON array or the selection
    Behavior:
      - Parses the stored agent output (attempt JSON parse)
      - Extract selectors from uploaded checkout.html
      - Calls selenium_builder to create Python code
    """
    global GENERATED_TESTCASES, HTML_CONTENT
    if testcases_id not in GENERATED_TESTCASES:
        raise HTTPException(status_code=404, detail="testcases_id not found")
    item = GENERATED_TESTCASES[testcases_id]
    out_text = item.get("output", "")

    try:
        parsed = json.loads(out_text)
        if not isinstance(parsed, list) or len(parsed) == 0:
            raise ValueError("Parsed testcases not a list or empty.")
        if testcase_index < 0 or testcase_index >= len(parsed):
            raise HTTPException(status_code=400, detail="testcase_index out of range")
        testcase = parsed[testcase_index]
    except Exception:

        testcase = {
            "Test_ID": f"TC-UNKNOWN-{testcases_id[:8]}",
            "Feature": "Unknown (raw agent output)",
            "Steps": [f"Follow agent output: {out_text[:400]}"],
            "Expected_Result": "As per agent output",
            "Grounded_In": [d.get("source") for d in item.get("retrieved", [])]
        }

    if not HTML_CONTENT or HTML_CONTENT.strip() == "":
        raise HTTPException(status_code=400, detail="checkout.html not uploaded. Upload via /upload_checkout_html")


    selectors = sb_mod.extract_selectors(HTML_CONTENT)

    script_code = sb_mod.build_script(testcase, selectors, api_key=x_groq_api_key, provider=x_llm_provider)


    return PlainTextResponse(script_code, media_type="text/x-python")

@app.get("/health")
async def health():
    return {"status": "ok", "kb_chunks": len(INGESTED_CHUNKS), "has_html": bool(HTML_CONTENT)}


@app.get("/assets")
async def list_assets():
    files = []
    for f in ASSETS_DIR.iterdir():
        if f.is_file():
            files.append({"name": f.name, "path": str(f), "size": f.stat().st_size})
    return JSONResponse({"assets": files})
