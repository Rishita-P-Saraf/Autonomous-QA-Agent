

import streamlit as st
from dotenv import load_dotenv
load_dotenv()
import requests
import json

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Autonomous QA Agent", layout="wide")
st.title("Autonomous QA Agent for Test Case & Selenium Script Generation")


st.sidebar.header("Configuration")
provider = st.sidebar.selectbox("LLM Provider", ["Ollama", "Groq", "Mock"])
api_key = ""
if provider == "Groq":
    api_key = st.sidebar.text_input("Groq API Key (Optional)", type="password", help="Leave empty to use Mock or Environment Variable")
elif provider == "Ollama":
    st.sidebar.info("Ensure Ollama is running locally (http://localhost:11434). Model: llama3")
elif provider == "Mock":
    st.sidebar.warning("Using Mock Mode. No AI will be used.")



st.header("Step 1: Upload Support Documents")
support_files = st.file_uploader(
    "Upload your support docs (MD, TXT, JSON, PDF, HTML)", 
    type=["md", "txt", "json", "pdf", "html"], 
    accept_multiple_files=True
)

if st.button("Upload Support Documents") and support_files:
    for f in support_files:
        files = {"file": (f.name, f, f.type)}
        r = requests.post(f"{API_URL}/upload_support_doc", files=files)
        if r.status_code == 200:
            st.success(f"Uploaded: {f.name}")
        else:
            st.error(f"Failed: {f.name} | {r.text}")


st.header("Step 2: Upload checkout.html")
checkout_file = st.file_uploader("Upload checkout.html", type=["html"])

if st.button("Upload checkout.html") and checkout_file:
    files = {"file": (checkout_file.name, checkout_file, checkout_file.type)}
    r = requests.post(f"{API_URL}/upload_checkout_html", files=files)
    if r.status_code == 200:
        st.success("checkout.html uploaded successfully")
    else:
        st.error(f"Failed: {r.text}")


st.header("Step 3: Build Knowledge Base")
if st.button("Build Knowledge Base"):
    r = requests.post(f"{API_URL}/build_kb")
    if r.status_code == 200:
        res = r.json()
        st.success(f"Knowledge Base Built! Chunks ingested: {res.get('ingested_chunks', 0)}")
    else:
        st.error(f"Failed to build KB: {r.text}")


st.header("Step 4: Generate Test Cases")
user_request = st.text_input("Enter your test case request (e.g., discount code test cases)")

if st.button("Generate Test Cases") and user_request:
    data = {"user_request": user_request}
    headers = {"x-llm-provider": provider.lower()}
    if api_key:
        headers["x-groq-api-key"] = api_key
        
    r = requests.post(f"{API_URL}/generate_testcases", data=data, headers=headers)
    if r.status_code == 200:
        res = r.json()
        tc_id = res.get("testcases_id")
        st.session_state["tc_id"] = tc_id
        st.success("Test cases generated! ID: " + tc_id)
        st.text_area("Preview:", res.get("preview", "")[:2000], height=300)
    else:
        st.error(f"Failed to generate test cases: {r.text}")


st.header("Step 5: Generate Selenium Script")
tc_id = st.session_state.get("tc_id", None)
testcase_index = st.number_input("Test case index (0 for first)", min_value=0, value=0)

if tc_id and st.button("Generate Selenium Script"):
    data = {"testcases_id": tc_id, "testcase_index": testcase_index}
    headers = {"x-llm-provider": provider.lower()}
    if api_key:
        headers["x-groq-api-key"] = api_key
        
    r = requests.post(f"{API_URL}/generate_selenium_script", data=data, headers=headers)
    if r.status_code == 200:
        st.success("Selenium Script Generated!")
        st.code(r.text, language="python")
    else:
        st.error(f"Failed: {r.text}")
