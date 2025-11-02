# BigQuery Chatbot - Setup Guide

Complete guide for setting up the BigQuery Chatbot backend and frontend for production use.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Google Cloud Platform Setup](#google-cloud-platform-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **Python 3.8+**: Backend runtime
- **pip**: Python package manager
- **Google Cloud Account**: With billing enabled
- **Web Browser**: For testing (Chrome, Firefox, Safari, Edge)

### Required Access

- Google Cloud Project with BigQuery enabled
- Vertex AI API access
- Service Account with appropriate permissions

---

## Google Cloud Platform Setup

### Step 1: Create or Select a GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your **Project ID** (you'll need this later)

### Step 2: Enable Required APIs

Enable these APIs in your project:

```bash
# Using gcloud CLI
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

Or enable manually:
1. Go to **APIs & Services** > **Library**
2. Search and enable:
   - BigQuery API
   - Vertex AI API
   - Cloud Resource Manager API

### Step 3: Create a Service Account

1. Go to **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Name: `bigquery-chatbot-sa`
4. Click **Create and Continue**

### Step 4: Assign Roles

Assign these roles to the service account:

- **BigQuery Data Viewer** (`roles/bigquery.dataViewer`)
- **BigQuery Job User** (`roles/bigquery.jobUser`)
- **Vertex AI User** (`roles/aiplatform.user`)

```bash
# Using gcloud CLI
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:bigquery-chatbot-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:bigquery-chatbot-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:bigquery-chatbot-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Step 5: Create and Download Key

1. In Service Accounts, click your service account
2. Go to **Keys** tab
3. Click **Add Key** > **Create New Key**
4. Choose **JSON** format
5. Save the file securely (e.g., `gcp-credentials.json`)

⚠️ **Security Warning**: Keep this file secure and never commit it to version control!

### Step 6: Set Up BigQuery Dataset

1. Go to **BigQuery** in GCP Console
2. Click **Create Dataset**
3. Dataset ID: Choose a name (e.g., `my_dataset`)
4. Location: Choose appropriate region
5. Create tables with your actual data structure

**Important**: The chatbot is **schema-agnostic** - it works with ANY table structure! You don't need to configure specific table or column names. Just ensure:
- Your tables exist in the dataset
- Service account has access to the dataset
- Tables have data (for testing)

**Example: Create Sample Table (for testing)**

```sql
CREATE TABLE `YOUR_PROJECT_ID.my_dataset.customers` (
  customer_id INT64,
  customer_name STRING,
  email STRING,
  revenue FLOAT64,
  created_at TIMESTAMP
);

-- Insert sample data
INSERT INTO `YOUR_PROJECT_ID.my_dataset.customers` VALUES
(1, 'John Doe', 'john@example.com', 5000.50, CURRENT_TIMESTAMP()),
(2, 'Jane Smith', 'jane@example.com', 7500.25, CURRENT_TIMESTAMP()),
(3, 'Bob Johnson', 'bob@example.com', 3200.00, CURRENT_TIMESTAMP());
```

**Note**: You can use your existing tables! The chatbot will automatically discover all tables and their schemas.

---

## Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd Part_B/backend
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

1. Create a `.env` file in the `Part_B/backend` directory:

```bash
# Copy example file if available, or create new
touch .env
```

2. Edit `.env` file with your configuration:

```env
# Google Cloud Project Configuration
GCP_PROJECT_ID=your-project-id
GCP_DATASET_ID=your-dataset-id
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/your/gcp-credentials.json

# BigQuery Configuration
BIGQUERY_LOCATION=US

# Vertex AI Configuration
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-flash

# API Configuration
API_PORT=8501
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Chatbot Settings
MAX_QUERY_LENGTH=500
MAX_RESULTS=100
```

**Configuration Details:**

- `GCP_PROJECT_ID`: Your GCP project ID
- `GCP_DATASET_ID`: Your BigQuery dataset ID
- `GOOGLE_APPLICATION_CREDENTIALS`: **Absolute path** to your service account JSON file
- `BIGQUERY_LOCATION`: Region where your BigQuery dataset is located (e.g., `US`, `EU`)
- `VERTEX_AI_LOCATION`: Region for Vertex AI (e.g., `us-central1`, `europe-west1`)
- `VERTEX_AI_MODEL`: Gemini model to use (`gemini-1.5-flash` or `gemini-1.5-pro`)
- `CORS_ORIGINS`: Comma-separated list of allowed origins (use `*` for development only)

### Step 5: Verify Configuration

Test your configuration:

```bash
python -c "from config import Config; Config.validate(); print('Configuration is valid!')"
```

---

## Frontend Setup

### Step 1: Verify Files

Ensure these files exist in the `Part_B/frontend` directory:
- `chatbot-widget.js`
- `chatbot-widget.css`
- `embed-snippet.html`

### Step 2: No Build Required

The frontend is pure HTML/CSS/JavaScript with no build step required!

---

## Running the Application

### Step 1: Start Backend Server

```bash
cd Part_B/backend
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --host 0.0.0.0 --port 8501
```

You should see:
```
🚀 BigQuery Chatbot - PRODUCTION API Server (FastAPI)
Mode: PRODUCTION (Vertex AI + BigQuery)
Server: http://localhost:8501
API Docs: http://localhost:8501/docs
✅ Handlers initialized successfully!
✅ Schema discovery completed
✅ Ready to process queries
✅ Natural language summaries enabled
```

**Schema Discovery**: On startup, the system automatically:
- Discovers all tables in your configured dataset
- Caches table schemas (columns, types, descriptions)
- Makes schema information available for SQL generation
- Logs how many tables and schemas were discovered

### Step 2: Test Backend

Open in browser:
- **API Docs**: http://localhost:8501/docs
- **Health Check**: http://localhost:8501/health

### Step 3: Test with Widget

1. Create a simple HTML page with the widget embedded
2. Update the `apiUrl` in the widget config to `http://localhost:8501`
3. Open the HTML page in a browser
4. Click the chat icon and test queries

---

## Testing

### Backend Testing

1. **Health Check**: Visit http://localhost:8501/health
2. **API Docs**: Visit http://localhost:8501/docs
3. **Test Query**: Use the API docs interface or curl:

```bash
curl "http://localhost:8501/?query=Show%20me%20all%20customers"
```

### Widget Testing

1. **Create Test Page**: Create an HTML file with widget embedded
2. **Check Console**: Open browser DevTools (F12)
3. **Test Interaction**: Send test queries
4. **Verify Responses**: Check for natural language summaries, SQL, and data tables

### Common Test Queries

The chatbot works with ANY schema! Try queries like:

```
1. "Show me the first 10 rows from [your-table-name]"
2. "Count all records in [table-name]"
3. "Get [entity] with highest [value-column]"
4. "What is [person-name]'s [field-name]?"
5. "List all [entities]"
```

**Examples** (adjust based on your actual tables):
- "Show me the first 10 rows from customers table"
- "Count all records in orders table"
- "Get customer with highest revenue"
- "What is John Doe's email?"
- "List all products"

**Note**: Since the system is schema-agnostic, replace generic examples with your actual table and column names!

---

## Deployment

### Backend Deployment Options

#### Option 1: Cloud Run (Recommended)

```bash
# Build and deploy to Cloud Run
gcloud run deploy bigquery-chatbot \
  --source Part_B/backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=your-project-id,GCP_DATASET_ID=your-dataset-id
```

#### Option 2: Compute Engine

1. Create VM instance
2. Install Python and dependencies
3. Set up systemd service to run FastAPI
4. Configure firewall rules
5. Use nginx as reverse proxy

#### Option 3: App Engine

Create `app.yaml`:

```yaml
runtime: python39

env_variables:
  GCP_PROJECT_ID: your-project-id
  GCP_DATASET_ID: your-dataset-id
```

### Frontend Deployment

The frontend files can be:
1. **Hosted on CDN**: Upload to CDN for fast global access
2. **Served from Web Server**: Host on your web server
3. **Embedded Directly**: Copy files to your application

### Production Checklist

- [ ] Update `apiUrl` to production backend URL in widget
- [ ] Enable HTTPS for backend
- [ ] Configure CORS for specific domains (not `*`)
- [ ] Set up monitoring and logging
- [ ] Configure rate limiting
- [ ] Set up backup for configuration
- [ ] Test on multiple browsers
- [ ] Test on mobile devices
- [ ] Set up CI/CD pipeline
- [ ] Document deployment process
- [ ] Set up error monitoring (e.g., Sentry)

---

## Troubleshooting

### Issue: Import Errors

**Symptom**: `ModuleNotFoundError`

**Solution**:
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Authentication Errors

**Symptom**: `Could not automatically determine credentials`

**Solution**:
1. Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
2. Ensure file exists and is readable
3. Check service account has proper permissions

```bash
# Set environment variable manually
export GOOGLE_APPLICATION_CREDENTIALS="/full/path/to/credentials.json"
```

### Issue: BigQuery Permission Denied

**Symptom**: `403 Forbidden` errors

**Solution**:
1. Verify service account has required roles
2. Check dataset and table permissions
3. Ensure project billing is enabled

### Issue: Vertex AI Errors

**Symptom**: `Vertex AI API not enabled`

**Solution**:
```bash
gcloud services enable aiplatform.googleapis.com
```

### Issue: CORS Errors in Browser

**Symptom**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:
1. Ensure backend CORS is configured
2. Check `CORS_ORIGINS` in `.env`
3. Update to include your domain

### Issue: Port Already in Use

**Symptom**: `Address already in use`

**Solution**:
```bash
# Find process using port 8501
# Windows:
netstat -ano | findstr :8501
# Linux/Mac:
lsof -i :8501

# Kill the process or use different port
python app.py --port 8502
```

### Issue: Schema Discovery Failed

**Symptom**: Warning in logs: `⚠️ Schema discovery failed`

**Solution**:
1. Verify service account has `bigquery.tables.list` permission
2. Check dataset ID is correct in `.env` file
3. Ensure dataset exists and is accessible
4. Check GCP project ID is correct
5. Verify BigQuery API is enabled

The system will still work without schema discovery, but SQL generation may be less accurate. Check startup logs for details.

---

## Next Steps

After successful setup:

1. Read [Integration Guide](INTEGRATION_GUIDE.md) for embedding the widget
2. Review [API Documentation](API_DOCUMENTATION.md) for API details
3. Customize the widget styling for your brand
4. Set up monitoring and logging
5. Plan for production deployment

---

## Support

For additional help:
- Check error messages in browser console
- Review FastAPI logs
- Check GCP logs in Cloud Console
- Consult Google Cloud documentation

---

**Setup Complete! 🎉**






