# 🚀 Deployment Instructions: Omani AI Therapist

## 1. Introduction

This guide provides **end-to-end deployment instructions** for the **Omani AI Therapist**, ensuring it runs reliably and securely in a production environment. It includes containerization, cloud deployment, environment configuration, monitoring, and update strategies.

---

**1. Clone the repository:**

```bash
git clone [Enter your GitHub repository URL here]
cd [Your repository folder name]
```
2. Create and activate a virtual environment:

```bash
python -m venv venv
```
For Linux/macOS:

```bash
source venv/bin/activate
```
For Windows:

```bash
venv\Scripts\activate
```
3. Install dependencies:

```bash
pip install -r requirements.txt
```
4. Set up API Key:

Create a file named .env in the root directory and add your key:

```bash
YOUR_API_KEY_VARIABLE_NAME=YOUR_API_KEY_HERE
```
Example:
```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
✅ .gitignore already excludes .env to keep it secure.
```
5. Run the app:

```bash
Copy
Edit
streamlit run app.py
```
It will launch automatically in your browser.

### Click "Deploy"

Now you have the application deployed and working on Streamlit