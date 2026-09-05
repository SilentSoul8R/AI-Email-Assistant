# AI Email Generator ✉️⚡
 
Stop staring at a blank subject line. Give it a topic, a tone, and a few bullet points, and it hands you back an email that actually sounds like a human wrote it (a fast, articulate human who never says "I hope this email finds you well").
 
Powered by Groq, so it's not just smart, it's absurdly fast.
 
## What it actually does
 
You type:
- **Topic**, what the email is about
- **Tone**, professional, friendly, persuasive, apologetic, urgent, whatever fits
- **Our points**, the key stuff that has to be in there
It gives you back:
- A real subject line (not "Subject: Update")
- A properly structured email with your points woven in naturally, not just listed like a grocery receipt
- A clear closing and call to action
- Something you can download as a `.txt` and send, no editing required
## Tech stack
 
| Layer | Tool |
|---|---|
| Brain | Groq (free tier, several models to choose from) |
| Face | Streamlit |
| Body | Python |
| Home | GitHub → Streamlit Cloud |
 
## Running it locally / in Colab
 
```bash
pip install -r requirements.txt
```
 
Set your Groq API key as an environment variable (never hardcode it):
 
```python
import os
os.environ["GROQ_API_KEY"] = "your_key_here"
```
 
Then run:
 
```bash
streamlit run app.py
```
 
## Deploying on Streamlit Cloud
 
1. Push this repo to GitHub.
2. Create a new app on [Streamlit Cloud](https://share.streamlit.io) pointing at it.
3. Go to **App settings → Secrets** and add:
```
   GROQ_API_KEY = "your_key_here"
```
4. Hit deploy. Your key stays server side the whole time, it never touches the browser, never shows up in the UI, never leaks into your commits.
## Get a Groq API key
 
Free, no credit card, takes about 30 seconds: [console.groq.com](https://console.groq.com)
 
## Model options
 
All models in the dropdown are on Groq's free developer tier (rate limited, not paid):
 
- **GPT OSS 120B**, the quality pick
- **GPT OSS 20B**, the speed demon, highest rate limits
- **Compound / Compound Mini**, can browse the web if your email needs current facts
- **Qwen 3.6 / 3.8 27B**, preview models, strong writers, could get renamed or retired by Groq without much warning
## A quick warning about "free" models
 
Groq occasionally retires models (RIP `llama-3.1-8b-instant` and `llama-3.3-70b-versatile`, moved to Enterprise pricing). If a model in the dropdown ever starts throwing errors, swap to `openai/gpt-oss-120b` or `openai/gpt-oss-20b`, those are the current, stable, free workhorses.
 
## Why this exists
 
Because writing "just a quick follow up email" should not take twenty minutes and four Google searches for how to phrase "per my last message" without sounding passive aggressive.
 
## License
 
Do whatever you want with it. Send great emails.
 
