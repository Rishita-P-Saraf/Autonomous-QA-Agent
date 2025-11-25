import os
import json
from typing import List
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

def get_llm_response(system_prompt: str, user_prompt: str, api_key: str = None, provider: str = "groq") -> tuple:
    """
    Helper to get response from LLM provider (Groq or Ollama) or fallback.
    Returns: (response_text, error_message)
    """
    if provider == "mock":
        return None, "Provider set to Mock"

    if provider == "ollama":
        resp = get_ollama_response(system_prompt, user_prompt)
        if resp:
            return resp, None
        return None, "Ollama call failed"


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
                temperature=0.2,
            )
            return chat_completion.choices[0].message.content, None
        except Exception as e:
            print(f"Groq API Error: {e}")
            return None, f"Groq API Error: {str(e)}"
            
    print("Using Mock Response (No valid Groq API Key or Error)")
    return None, "No valid Groq API Key found in env or args"

def generate_testcases(context_chunks: List[str], user_request: str, api_key: str = None, provider: str = "groq") -> str:
    """
    Generates structured test cases based on the provided context and user request.
    """
    
    context_str = "\n\n".join(context_chunks)
    
    system_prompt = """You are an expert QA Automation Engineer. 
Your goal is to generate comprehensive test cases based STRICTLY on the provided project documentation.
Do not hallucinate features not mentioned in the context.
Output must be a JSON list of objects with the following keys:
- Test_ID (e.g., TC-001)
- Feature
- Test_Scenario
- Expected_Result
- Grounded_In (Filename of the doc source)

Return ONLY the JSON array. No markdown formatting or extra text.
"""

    user_prompt = f"""
Context from documentation:
{context_str}

User Request: {user_request}

Generate test cases now.
"""

    response_text, error_msg = get_llm_response(system_prompt, user_prompt, api_key=api_key, provider=provider)
    
    if response_text:

        if response_text.strip().startswith("```"):
            try:
                response_text = response_text.strip().split("\n", 1)[1].rsplit("\n", 1)[0]
            except IndexError:
                pass
        return response_text


    return json.dumps([
        {
            "Test_ID": "TC-MOCK-001",
            "Feature": f"Mock Feature (Error: {error_msg})",
            "Test_Scenario": f"Mock test for: {user_request}",
            "Expected_Result": "Should work as expected",
            "Grounded_In": "product_specs.md"
        }
    ], indent=2)
