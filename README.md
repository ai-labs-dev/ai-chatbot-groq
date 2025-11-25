# 🤖 AI Chatbot — Streamlit + Groq Llama 3

A simple and modern AI chatbot built using **Python**, **Streamlit**, and **Groq Llama 3**.  
It supports multi-turn conversation, a clean ChatGPT-style interface, and fast responses.

---

## Features

- **Groq Llama-3** powered chat (super fast)
- Multi-turn conversation memory
- Modern dark UI with chat bubbles
- Enter-to-send input (no send button)
- Clean and minimal code structure
- Works on desktop & mobile
- Easy to customize for any use-case

## 📦 Setup & Installation

### 1️Clone this repository
```bash
git clone https://github.com/YOUR-USERNAME/ai-chatbot-groq.git
cd ai-chatbot-groq

pip install -r requirements.txt

client = Groq(api_key="YOUR_GROQ_API_KEY")

streamlit run app.py
