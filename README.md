# 🚀 Autonomous QA Agent

An intelligent, autonomous QA agent capable of constructing a "testing brain" from project documentation. It generates test cases and executable Selenium scripts grounded in the provided documentation.

---

## Features
- **Knowledge Base Ingestion**: Uploads and parses support documents (MD, TXT, JSON, PDF, HTML).
- **RAG Pipeline**: Generates test cases grounded in documentation using a Vector DB (FAISS) and LLM (Groq/Llama3).
- **Selenium Script Generation**: Converts test cases into runnable Python Selenium scripts.
- **Free Model Support**: Uses Groq (free tier) for high-performance inference.

---

## Project Folder Structure
```bash
OceanAI-assignment/
├── assets/
│   ├── api_endpoints.json
│   ├── checkout.html
│   ├── product_specs.md
│   └── ui_ux_guide.txt
│
├── backend/
│   └── app/
│       ├── __pycache__/
│       ├── services/
│       │   ├── __pycache__/
│       │   ├── embeddings.py
│       │   ├── parser.py
│       │   ├── rag_agent.py
│       │   ├── selenium_builder.py
│       │   └── vectorstore.py
│       └── main.py
│
├── streamlit_app/
│   ├── app.py
│   └── requirements.txt
│
├── venv/
│
├── .env
└── README.md

```
---

## Setup Instructions

### Prerequisites
- **Python 3.8+** required.

### Installation
1. **Clone the repository** (or extract the project folder).
2. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

### Environment Setup
1. **Create a `.env` file** in the project root (if not already present).
2. **Add your Groq API Key**:
   ```env
   GROQ_API_KEY=your_actual_api_key_here
   ```
   *Note: A `.env` file with a placeholder has been created for you.*

---

## How to Run

### 1. Start the Backend (FastAPI)
Open a terminal in the project root:
```bash
uvicorn backend.app.main:app --reload --port 8000
```

### 2. Start the Frontend (Streamlit)
Open a new terminal in the project root:
```bash
streamlit run backend/streamlit_app/app.py
```

Access the UI at `http://localhost:8501`.

---

## Usage Guide

### 1. Upload Assets
- Go to **Step 1** in the UI.
- Upload the support documents from the `assets/` folder (e.g., `product_specs.md`, `ui_ux_guide.txt`, `api_endpoints.json`).
- Go to **Step 2** and upload `assets/checkout.html`.

### 2. Build Knowledge Base
- Click **"Build Knowledge Base"** in **Step 3**.
- Wait for the success message confirming chunks were ingested.

### 3. Generate Test Cases
- Ensure your Groq API Key is set (in `.env` or UI sidebar).
- In **Step 4**, enter a request like: `"Generate positive test cases for discount code"`.
- Click **"Generate Test Cases"**.

### 4. Generate Selenium Script
- Once test cases are generated, go to **Step 5**.
- Select a test case index (default is `0`).
- Click **"Generate Selenium Script"**.
- Copy the generated Python code.

### 5. Run the Selenium Script
- Save the code to a file (e.g., `test_script.py`).
- Run it locally:
  ```bash
  python test_script.py
  ```
  *Ensure you have `chromedriver` installed or managed via `webdriver-manager` (included in requirements).*

---

## Support Documents Explanation

The project uses the following support documents to ground the QA agent:

- **`assets/product_specs.md`**: Defines the business logic, feature rules, and constraints (e.g., discount code validity, cart limits).
- **`assets/ui_ux_guide.txt`**: Provides UI styling guidelines, error message formats, and validation rules.
- **`assets/api_endpoints.json`**: Describes the mock API structure, expected responses, and data formats.
- **`assets/checkout.html`**: The target web page used to extract selectors and validate DOM interaction.


