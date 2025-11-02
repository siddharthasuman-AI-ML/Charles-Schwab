# Part_A Backend - Demo Setup Guide

Quick setup guide for the demo version of the BigQuery Chatbot.

## 🎬 Purpose

This is the **DEMO VERSION** for showing to seniors. It uses:
- **Gemini API** (your personal API key)
- **Mock Data** (no real BigQuery needed)
- **FastAPI** backend

## ⚡ Quick Start

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure API Key

1. Create `.env` file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Gemini API key:
```env
GEMINI_API_KEY=your-actual-api-key-here
```

Get your API key from: https://aistudio.google.com/app/apikey

### Step 3: Run the Server

```bash
python app.py
```

The server will start at: **http://localhost:8501**

### Step 4: Test the Demo

1. Open `../test-page/index.html` in your browser
2. Click the chat widget (bottom-right)
3. Try queries like:
   - "Show me customers"
   - "Count total records"
   - "Get top 5 by revenue"

## 📋 Features

- ✅ Natural language to SQL conversion
- ✅ Natural language summaries
- ✅ Mock data for demo
- ✅ FastAPI with auto-generated docs
- ✅ Beautiful chat widget UI

## 🔍 API Documentation

Once the server is running, visit:
- **API Docs**: http://localhost:8501/docs
- **Health Check**: http://localhost:8501/health

## 📝 Notes

- This version uses **demo/mock data** - not real BigQuery
- Perfect for demonstrations without GCP setup
- For production use, see **Part_B**

## 🆘 Troubleshooting

**Error: Missing GEMINI_API_KEY**
- Make sure you created `.env` file
- Check that `GEMINI_API_KEY=your-key` is set

**Port already in use:**
- Change `API_PORT` in `.env` to a different port

**Module not found:**
- Run: `pip install -r requirements.txt`

## ✅ Ready for Demo!

Once the server is running and the test page loads, you're ready to demo to your seniors! 🚀






