# BigQuery Chatbot - Production Package (Part_B)

Complete production-ready package for Team B to integrate the BigQuery Chatbot into their web application.

## 🎯 Overview

This package contains everything Team B needs to integrate a natural language BigQuery chatbot into their web application. The chatbot translates user queries into SQL, executes them on BigQuery, and provides natural language summaries of the results.

**Key Advantage: Schema-Agnostic Architecture** - Works with ANY BigQuery dataset without requiring configuration of table or column names!

## 📦 What's Included

```
Part_B/
├── backend/              # FastAPI backend server
│   ├── app.py           # Main FastAPI application
│   ├── config.py         # Configuration management
│   ├── llm_handler.py   # Vertex AI integration for NL2SQL
│   ├── bigquery_handler.py  # BigQuery operations
│   ├── schema_manager.py # Schema discovery and caching (NEW!)
│   ├── requirements.txt  # Python dependencies
│   └── .env.example     # Environment variables template
├── frontend/             # Embeddable chatbot widget
│   ├── chatbot-widget.js    # Widget JavaScript
│   ├── chatbot-widget.css   # Widget styles
│   └── embed-snippet.html   # Integration example
└── docs/                 # Complete documentation
    ├── INTEGRATION_GUIDE.md  # How to embed the widget
    ├── SETUP_GUIDE.md        # Backend setup instructions
    └── API_DOCUMENTATION.md  # API reference
```

## 🚀 Quick Start

### 1. Backend Setup

1. Navigate to `backend/` directory
2. Create `.env` file with your GCP credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Run server: `python app.py`

The system will automatically discover your BigQuery tables and schemas on startup!

See [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for detailed instructions.

### 2. Frontend Integration

Add to your HTML page:

```html
<link rel="stylesheet" href="path/to/chatbot-widget.css">
<script src="path/to/chatbot-widget.js"></script>
<script>
  ChatbotWidget.init({
    apiUrl: 'https://your-backend-url.com'
  });
</script>
```

See [INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md) for complete integration guide.

## ✨ Features

### Core Features
- **Natural Language to SQL**: Converts user questions to BigQuery SQL using Vertex AI
- **BigQuery Integration**: Executes queries on your BigQuery datasets
- **Natural Language Summaries**: Provides conversational explanations of results
- **Embeddable Widget**: Easy to integrate into any website
- **Modern UI**: Clean, responsive chat interface
- **Production Ready**: FastAPI backend with proper error handling

### 🎯 Schema-Agnostic Features (NEW!)

- **Zero Configuration Required**: No need to specify table or column names
- **Automatic Schema Discovery**: Automatically discovers all tables and columns in your dataset on startup
- **Dynamic SQL Generation**: LLM uses actual schema information to generate accurate SQL queries
- **Works with Any Data Structure**: Handles any BigQuery schema - customers, orders, products, analytics tables, etc.
- **Intelligent Answer Extraction**: Extracts answers from query results using actual column names
- **Smart Column Matching**: Handles various naming conventions (snake_case, camelCase, spaces)
- **Schema Caching**: Efficiently caches schema information for fast query processing

**Why This Matters**: You can deploy this chatbot with ANY BigQuery dataset without modifying code. It automatically adapts to your schema!

## 📚 Documentation

- **[Integration Guide](docs/INTEGRATION_GUIDE.md)**: Step-by-step widget integration
- **[Setup Guide](docs/SETUP_GUIDE.md)**: Backend configuration, schema discovery, and deployment
- **[API Documentation](docs/API_DOCUMENTATION.md)**: Complete API reference with schema-aware examples

## 🔧 Requirements

### Backend
- Python 3.8+
- Google Cloud Project with:
  - BigQuery API enabled
  - Vertex AI API enabled
  - Service Account with proper permissions:
    - `bigquery.datasets.get`
    - `bigquery.tables.get`
    - `bigquery.tables.list`
    - `bigquery.jobs.create`
    - `bigquery.jobs.get`

### Frontend
- Modern web browser
- No additional dependencies (pure HTML/CSS/JS)

## 🔐 Security

⚠️ **Important for Production**:
- Configure CORS to allow only your domains
- Use HTTPS for all connections
- Implement API authentication (currently optional)
- Set up rate limiting
- Keep GCP credentials secure

## 🏗️ Architecture

### Schema Discovery Flow

1. **Startup**: System discovers all tables in configured BigQuery dataset
2. **Schema Caching**: Schemas are cached for efficient access
3. **Query Processing**: 
   - User query → LLM receives actual schema information
   - LLM generates SQL using real table/column names
   - Query executes on BigQuery
   - Results processed with intelligent answer extraction
4. **Answer Generation**: Logic-based extraction with LLM fallback

### Components

- **`schema_manager.py`**: Handles schema discovery and caching
- **`llm_handler.py`**: Generates SQL using discovered schema information
- **`app.py`**: Orchestrates query processing with schema-aware logic
- **`bigquery_handler.py`**: Executes queries and retrieves schema information

## 🤝 Support

For questions or issues:
1. Check the documentation in `docs/`
2. Review error messages in browser console and backend logs
3. Verify schema discovery completed successfully (check startup logs)
4. Contact Team A for technical support

## 📝 License

Internal use only. See your organization's licensing terms.

---

**Version**: 2.0 (Schema-Agnostic)  
**Last Updated**: 2025  
**Maintained By**: Team A

---

## What's New in v2.0

- ✅ Schema-agnostic architecture
- ✅ Automatic schema discovery
- ✅ Dynamic SQL generation
- ✅ Zero configuration required
- ✅ Works with any BigQuery dataset
