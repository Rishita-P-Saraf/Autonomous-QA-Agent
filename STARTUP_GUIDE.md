# Beginner's Guide to Starting the Autonomous QA Agent

Welcome! This guide will teach you exactly how to start and use the application, step-by-step.

The application has two parts that need to run at the same time:
1.  **The Backend (The Brain)**: This handles all the logic, AI, and data processing.
2.  **The Frontend (The UI)**: This is the website you interact with.

---

## Step 1: Open the Project
Make sure you are inside the project folder in your terminal (PowerShell or Command Prompt).
You should see folders like `backend`, `assets`, etc.

## Step 2: Start the Backend
1.  Open a **new terminal window**.
2.  Run this command to start the "Brain":
    ```powershell
    uvicorn backend.app.main:app --reload --port 8000
    ```
3.  You will see messages saying `Uvicorn running on http://127.0.0.1:8000`. **Keep this terminal open!**

## Step 3: Start the Frontend
1.  Open a **second terminal window** (do not close the first one).
2.  Run this command to start the "Website":
    ```powershell
    streamlit run backend/streamlit_app/app.py
    ```
3.  This should automatically open your web browser to `http://localhost:8501`.
    - If it doesn't, just type `http://localhost:8501` into your browser's address bar.

---

## Step 4: How to Use the App

Now that the website is open, follow these steps to generate your test scripts.

### 1. Upload Documents
- Look for **"Step 1: Upload Support Documents"**.
- Click **"Browse files"**.
- Navigate to the `assets` folder in this project.
- Select these files:
    - `product_specs.md`
    - `ui_ux_guide.txt`
    - `api_endpoints.json`
- Click the **"Upload Support Documents"** button.

### 2. Upload the Website File
- Look for **"Step 2: Upload checkout.html"**.
- Click **"Browse files"**.
- Select `checkout.html` from the `assets` folder.
    - *Note:* You might see `checkout_final.html` or `checkout_v2.html`. **Please select `checkout.html`** as it is the main file we are testing.
- Click the **"Upload checkout.html"** button.

### 3. Build the "Brain"
- Scroll to **"Step 3: Build Knowledge Base"**.
- Click the **"Build Knowledge Base"** button.
- Wait for the green success message (e.g., "Knowledge Base Built!").

### 4. Generate Test Cases
- Scroll to **"Step 4: Generate Test Cases"**.
- (Optional) If you have a Groq API Key, enter it in the sidebar on the left. If not, the app will use a "Mock" mode to show you how it works.
- In the text box, type what you want to test.
    - *Example:* "Generate positive and negative test cases for the discount code feature."
- Click **"Generate Test Cases"**.
- You will see a preview of the generated test plan.

### 5. Generate the Python Script
- Scroll to **"Step 5: Generate Selenium Script"**.
- You can choose which test case to turn into code (default is 0, the first one).
- Click **"Generate Selenium Script"**.
- The app will write a Python script for you!

## Step 5: Run the Selenium Script

Now that you have the code, here is how to run it:

1.  **Copy the Code**: Click the copy button on the code block in the app.
2.  **Create a File**: Create a new file in your **main project folder** (where `backend` and `assets` folders are) called `test_script.py` and paste the code inside.
3.  **Install Selenium**: Open a terminal and run:
    ```powershell
    pip install selenium webdriver-manager
    ```
4.  **Run the Test**:
    ```powershell
    python test_script.py
    ```
    - This will open a Chrome browser controlled by the script and run the test!

---

## Troubleshooting
- **"Module not found"**: If you see an error about missing modules, run: `pip install -r backend/requirements.txt`
- **"Port already in use"**: If `uvicorn` says port 8000 is busy, try closing other python windows or restart your computer.

---

## Optional: How to use Ollama (Free Local AI)

If you want to run the AI entirely on your own computer (for free, without internet for the AI part), follow these steps:

### 1. Install Ollama
1.  Go to [https://ollama.com/download](https://ollama.com/download).
2.  Download the **Windows** installer.
3.  Run the installer and follow the instructions.

### 2. Download the Model
1.  Open a **new terminal** (PowerShell or Command Prompt).
2.  Run this command to download the "Brain" (Llama 3 model):
    ```powershell
    ollama run llama3
    ```
3.  It will start downloading (about 4.7 GB). Wait for it to finish.
4.  Once it says `>>>`, you can type "Hi" to test it, or just type `/bye` to exit.
5.  **Keep the Ollama app running** (you usually see a little llama icon in your taskbar).

### 3. Use it in the App
1.  Go to your web browser where the app is running (`http://localhost:8501`).
2.  In the **Sidebar** (left side), look for **"LLM Provider"**.
3.  Select **"Ollama"**.
4.  Now, when you click "Generate Test Cases" or "Generate Selenium Script", it will use your local Ollama instead of the cloud!
