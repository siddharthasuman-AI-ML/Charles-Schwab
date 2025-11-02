# Part_B Backend - Production Setup Guide

Complete setup guide for the production BigQuery Chatbot backend using Vertex AI + BigQuery.

## 🎯 Purpose

This is the **PRODUCTION VERSION** for Team B integration. It uses:
- **Vertex AI** (Gemini models via GCP)
- **Real BigQuery** (actual data execution)
- **FastAPI** production backend
- **Schema-Agnostic Architecture** - Works with ANY BigQuery dataset automatically!

## 📋 Prerequisites

- Google Cloud Platform account
- GCP project with billing enabled
- BigQuery dataset with data
- Service account with proper permissions:
  - `bigquery.datasets.get`
  - `bigquery.tables.get`
  - `bigquery.tables.list`
  - `bigquery.jobs.create`
  - `bigquery.jobs.get`

## ⚙️ Setup Steps

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure GCP

1. **Create Service Account:**
   - Go to GCP Console → IAM & Admin → Service Accounts
   - Create service account with name: `bigquery-chatbot-sa`

2. **Assign Roles:**
   - BigQuery Data Viewer
   - BigQuery Job User
   - Vertex AI User

3. **Download Credentials:**
   - Create and download JSON key file
   - Save securely (e.g., `gcp-credentials.json`)

### Step 3: Enable APIs

Enable these APIs in your GCP project:
- BigQuery API
- Vertex AI API
- Cloud Resource Manager API

### Step 4: Configure Environment

1. Create `.env` file:
```bash
cp env-template.txt .env
```

2. Edit `.env` with your values:
```env
GCP_PROJECT_ID=your-project-id
GCP_DATASET_ID=your-dataset-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/gcp-credentials.json
BIGQUERY_LOCATION=US
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-flash
API_PORT=8501
CORS_ORIGINS=*
```

### Step 5: Run the Server

```bash
python app.py
```

Server starts at: **http://localhost:8501**

**On Startup**: The system automatically:
- Discovers all tables in your configured dataset
- Caches table schemas (columns, types, descriptions)
- Makes schema information available for SQL generation
- Logs schema discovery status

## 🏗️ Architecture

### Schema-Agnostic Design

The backend uses a **schema-agnostic architecture** that works with ANY BigQuery dataset:

1. **Schema Discovery** (`schema_manager.py`):
   - Discovers all tables on startup
   - Caches schema information
   - Provides schema info to SQL generation

2. **Dynamic SQL Generation** (`llm_handler.py`):
   - Receives actual schema information
   - Generates SQL using real table/column names
   - No hardcoded assumptions

3. **Intelligent Answer Extraction** (`app.py`):
   - Works with any data structure
   - Dynamically matches columns
   - Handles various naming conventions

### Key Components

- **`app.py`**: Main FastAPI application and query orchestration
- **`llm_handler.py`**: Vertex AI integration for NL2SQL (schema-aware)
- **`bigquery_handler.py`**: BigQuery query execution and schema retrieval
- **`schema_manager.py`**: Schema discovery, caching, and retrieval
- **`config.py`**: Configuration management

## 📚 API Documentation

- **Interactive Docs**: http://localhost:8501/docs
- **Health Check**: http://localhost:8501/health

## ✅ Features

- Natural language to SQL conversion (schema-aware)
- Natural language summaries
- Real BigQuery integration
- **Automatic schema discovery**
- **Works with any dataset structure**
- FastAPI with auto docs
- Production-ready error handling

## 🔧 Configuration Details

See `docs/SETUP_GUIDE.md` for complete GCP setup instructions.

## 🆘 Troubleshooting

### Schema Discovery Issues

If schema discovery fails:
1. Check service account has `bigquery.tables.list` permission
2. Verify dataset ID is correct
3. Ensure dataset exists and is accessible
4. Check startup logs for error details

The system will still work without schema discovery, but SQL generation may be less accurate.

### Other Issues

See `docs/SETUP_GUIDE.md` for detailed troubleshooting.

---

**Ready for production integration!** 🚀

**Version**: 2.0 (Schema-Agnostic)
