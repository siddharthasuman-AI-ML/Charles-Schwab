# Part_A - Demo Version

This folder contains the **DEMO VERSION** of the BigQuery Chatbot for showing to seniors.

## 📁 Structure

```
Part_A/
├── backend/              # FastAPI demo server
│   ├── app.py           # Main server
│   ├── config.py        # Configuration
│   ├── llm_handler.py   # Gemini API handler
│   ├── bigquery_handler.py  # Mock data handler
│   └── requirements.txt # Dependencies
├── frontend/            # Chat widget
│   ├── chatbot-widget.js
│   ├── chatbot-widget.css
│   └── embed-snippet.html
└── test-page/          # Demo page
    ├── index.html
    └── styles.css
```

## 🎯 What's Included

- **Backend**: FastAPI server with Gemini API + Mock data
- **Frontend**: Complete chat widget
- **Test Page**: "Hello World" demo page with chatbot
- **Natural Language Summaries**: AI-generated explanations

## 🚀 Quick Demo Setup

### 1. Setup Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
python app.py
```

### 2. Open Demo Page

Open `test-page/index.html` in your browser.

### 3. Demo to Seniors!

- Click chat widget
- Ask questions
- Show natural language summaries
- Show SQL generation
- Show data tables

## ✨ Demo Features

- 💬 **Natural Language Queries**: Ask in plain English
- 🤖 **AI-Powered**: Gemini generates SQL and summaries
- 📊 **Beautiful UI**: Modern, responsive chat widget
- 📈 **Data Visualization**: Tables with results
- 🎨 **Professional Design**: Ready to impress!

## ⚠️ Important Notes

- **Demo Mode**: Uses mock data, not real BigQuery
- **API Key Required**: Need Gemini API key (free tier available)
- **Local Only**: Runs on localhost for demo purposes

## 📖 For Production

If you need the production version with real BigQuery integration, see **Part_B** folder.

---

**Ready to demo!** 🎬






