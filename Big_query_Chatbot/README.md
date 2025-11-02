# Pop-up Chatbot - BigQuery Natural Language Query Assistant

A powerful, embeddable chatbot widget that converts natural language queries into BigQuery SQL and provides conversational data insights.

## 🎯 Overview

This project provides a complete solution for adding an intelligent BigQuery chatbot to any website. The chatbot:
- Converts natural language questions to SQL queries using Google's Gemini AI
- Executes queries on BigQuery datasets
- Provides natural language summaries of results
- Offers a beautiful, modern pop-up chat interface
- **Schema-Agnostic (Part_B)**: Automatically works with ANY BigQuery dataset structure!

## 📁 Project Structure

```
Big_query_Chatbot/
├── Part_A/              # Demo Version (for testing and presentations)
│   ├── backend/         # FastAPI server with Gemini API + Mock data
│   ├── frontend/        # Embeddable chat widget
│   └── test-page/       # Demo page for showcasing
│
├── Part_B/              # Production Version (for Team B integration)
│   ├── backend/         # FastAPI server with Vertex AI + Real BigQuery
│   ├── frontend/        # Embeddable chat widget
│   └── docs/            # Complete integration documentation
│
└── TOGGLE_MODE_INSTRUCTIONS.md  # Guide for switching response modes
```

## 🚀 Quick Start

### For Demo/Testing (Part_A)

1. **Setup Backend:**
   ```bash
   cd Part_A/backend
   pip install -r requirements.txt
   # Create .env file with your GEMINI_API_KEY
   python app.py
   ```

2. **Open Demo Page:**
   - Open `Part_A/test-page/index.html` in your browser
   - The chat widget will appear as a pop-up

See [Part_A/README.md](Part_A/README.md) for detailed instructions.

### For Production Integration (Part_B)

1. **Setup Backend:**
   ```bash
   cd Part_B/backend
   pip install -r requirements.txt
   # Configure .env with GCP credentials
   python app.py
   ```

2. **Integrate Widget:**
   ```html
   <link rel="stylesheet" href="path/to/chatbot-widget.css">
   <script src="path/to/chatbot-widget.js"></script>
   <script>
     ChatbotWidget.init({ apiUrl: 'https://your-backend-url.com' });
   </script>
   ```

See [Part_B/README.md](Part_B/README.md) and [Part_B/docs/INTEGRATION_GUIDE.md](Part_B/docs/INTEGRATION_GUIDE.md) for complete documentation.

## ✨ Features

### Core Features
- 🤖 **Natural Language to SQL**: Ask questions in plain English
- 📊 **BigQuery Integration**: Direct connection to Google BigQuery
- 💬 **Natural Language Summaries**: Conversational explanations of results
- 🎨 **Modern UI**: Beautiful, responsive pop-up chat widget
- 🔧 **Two Response Modes**: Full response (SQL + Table) or Natural Language only
- 📦 **Easy Integration**: Embed into any website with a few lines of code

### Part_B Production Features (Schema-Agnostic)
- 🏗️ **Zero Configuration**: No need to specify table or column names
- 🔍 **Automatic Schema Discovery**: Discovers all tables and columns on startup
- 🎯 **Dynamic SQL Generation**: Uses actual schema information for accurate queries
- 💡 **Intelligent Answer Extraction**: Works with any data structure
- 🔄 **Smart Column Matching**: Handles various naming conventions (snake_case, camelCase, etc.)

## 🔄 Response Modes

The chatbot supports two response modes (configurable via comments in code):

1. **Mode 1 (Full Response)**: Natural Language Summary + SQL Query + Data Table
2. **Mode 2 (Natural Language Only)**: Only Natural Language Summary

See [TOGGLE_MODE_INSTRUCTIONS.md](TOGGLE_MODE_INSTRUCTIONS.md) for switching instructions.

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **AI/ML**: Google Gemini API / Vertex AI
- **Database**: Google BigQuery
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Deployment**: Any Python hosting service

## 📚 Documentation

- **[Part_A README](Part_A/README.md)**: Demo version setup
- **[Part_B README](Part_B/README.md)**: Production version overview
- **[Integration Guide](Part_B/docs/INTEGRATION_GUIDE.md)**: Widget integration steps
- **[Setup Guide](Part_B/docs/SETUP_GUIDE.md)**: Backend configuration
- **[API Documentation](Part_B/docs/API_DOCUMENTATION.md)**: API reference
- **[Toggle Mode Instructions](TOGGLE_MODE_INSTRUCTIONS.md)**: Response mode switching

## 🔐 Security Notes

⚠️ **Important**:
- Never commit `.env` files or API keys
- Configure CORS for production
- Use HTTPS in production
- Implement authentication for production use
- Keep GCP credentials secure

## 📝 License

Internal use only. See your organization's licensing terms.

## 🤝 Support

For questions or issues:
1. Check the documentation in respective folders
2. Review error messages in browser console and backend logs
3. Contact the development team

---

**Version**: 2.0 (Part_B Schema-Agnostic)  
**Last Updated**: 2025  
**Maintained By**: Development Team

---

## What's New in v2.0

- ✅ **Schema-Agnostic Architecture**: Part_B now works with ANY BigQuery dataset
- ✅ **Automatic Schema Discovery**: No configuration of table/column names required
- ✅ **Dynamic SQL Generation**: LLM uses actual schema information
- ✅ **Enhanced Answer Extraction**: Works with any data structure intelligently
- ✅ **Production Ready**: Fully tested and documented for Team B integration

