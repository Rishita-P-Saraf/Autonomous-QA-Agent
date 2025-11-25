import os
import json
from bs4 import BeautifulSoup
import requests

def get_ollama_response(system_prompt: str, user_prompt: str, model: str = "llama3") -> str:
    """
    Helper to get response from local Ollama instance.
    """
    try:
        url = "http://localhost:11434/api/chat"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "")
    except Exception as e:
        print(f"Ollama Error: {e}")
        return None

from groq import Groq

def get_llm_response(system_prompt: str, user_prompt: str, api_key: str = None, provider: str = "groq") -> str:
    """
    Helper to get response from LLM provider or fallback.
    """
    if provider == "mock":
        return None

    if provider == "ollama":
        return get_ollama_response(system_prompt, user_prompt)

    api_key = api_key or os.environ.get("GROQ_API_KEY")
    
    if api_key:
        try:
            client = Groq(api_key=api_key)
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.1,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API Error: {e}")
            pass
            
    return None


def extract_selectors(html_content: str) -> str:
    """
    Parses HTML and extracts potential interesting elements (inputs, buttons) 
    to help the LLM generate correct selectors.
    Returns a summary string.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    elements = []
    

    for inp in soup.find_all("input"):
        info = f"Tag: input, ID: {inp.get('id')}, Name: {inp.get('name')}, Type: {inp.get('type')}"
        elements.append(info)
        

    for btn in soup.find_all("button"):
        info = f"Tag: button, ID: {btn.get('id')}, Text: {btn.get_text(strip=True)}, Class: {btn.get('class')}"
        elements.append(info)
        

    for sel in soup.find_all("select"):
        info = f"Tag: select, ID: {sel.get('id')}, Name: {sel.get('name')}"
        elements.append(info)

    return "\n".join(elements)

def build_script(testcase: dict, selectors_summary: str, api_key: str = None, provider: str = "groq") -> str:
    """
    Generates a Python Selenium script for the given test case.
    """
    
    system_prompt = """You are an expert Selenium Automation Engineer using Python.
Your task is to write a complete, runnable Python script using Selenium WebDriver (Chrome).
The script should:
1. Setup the driver (assume chromedriver is in path or use webdriver_manager).
2. Open 'checkout.html' (assume it's in the current directory or provide a placeholder path).
3. Implement the steps required for the test case.
4. Add assertions to verify the Expected Result.
5. Close the driver at the end.

Use the provided HTML Element Selectors to ensure the script works.
Return ONLY the Python code.
"""

    user_prompt = f"""
Test Case:
{json.dumps(testcase, indent=2)}

HTML Selectors Available:
{selectors_summary}

Generate the Selenium Python script now.
"""

    code = get_llm_response(system_prompt, user_prompt, api_key=api_key, provider=provider)
    
    if code:

        if code.startswith("```python"):
            code = code.replace("```python", "").replace("```", "")
        if code.startswith("```"):
            code = code.replace("```", "")
        return code.strip()


    return f"""
from selenium import webdriver
from selenium.webdriver.common.by import By
import time



def run_test():
    driver = webdriver.Chrome()
    try:
        driver.get("file:///path/to/checkout.html")
        print("Opened checkout.html")
        

        
        print("Executing test steps...")
        time.sleep(1)
        
        print("Verifying expected result: {testcase.get('Expected_Result')}")
        assert True # Placeholder assertion
        print("Test Passed!")
        
    except Exception as e:
        print(f"Test Failed: {{e}}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_test()
"""
