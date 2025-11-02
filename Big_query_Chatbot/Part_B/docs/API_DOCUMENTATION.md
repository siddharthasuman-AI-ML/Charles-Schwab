# BigQuery Chatbot - API Documentation

Complete API reference for the BigQuery Chatbot backend (FastAPI).

## Table of Contents

1. [Overview](#overview)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [Endpoints](#endpoints)
5. [Request/Response Formats](#requestresponse-formats)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Examples](#examples)

---

## Overview

The BigQuery Chatbot API provides a simple interface for converting natural language queries to SQL and executing them on BigQuery. Responses include natural language summaries.

**Key Feature**: The API is **schema-agnostic** - it automatically discovers and works with ANY BigQuery dataset structure without requiring configuration of table or column names.

**API Type**: RESTful API  
**Data Format**: JSON  
**Protocol**: HTTP/HTTPS  
**Framework**: FastAPI

---

## Base URL

### Development
```
http://localhost:8501
```

### Production
```
https://your-backend-domain.com
```

---

## Authentication

Currently, the API uses **no authentication** for simplicity. For production deployments, consider implementing:

- API Key authentication
- OAuth 2.0
- JWT tokens
- IP whitelisting

### Future Authentication (Planned)

```http
Authorization: Bearer YOUR_API_KEY
```

---

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint**: `GET /health`

**Description**: Returns API status and configuration info.

**Response**:
```json
{
  "status": "ok",
  "mode": "production",
  "handlers_ready": true,
  "api": "FastAPI",
  "version": "1.0.0"
}
```

**Example**:
```bash
curl http://localhost:8501/health
```

---

### 2. Chat Query

Process a natural language query.

**Endpoint**: `GET /?query={query}`

**Method**: GET

**Description**: Converts natural language to SQL, executes on BigQuery, and generates a natural language summary.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Natural language query |

**Example Request**:
```bash
curl "http://localhost:8501/?query=Show%20me%20top%2010%20customers"
```

**Note**: The query uses actual table and column names from your schema. Replace "customers" with your actual table names.

**Success Response** (200 OK):
```json
{
  "success": true,
  "query": "Show me top 10 customers",
  "summary": "The query returned 10 customer records showing their details including customer ID, name, email, and revenue information.",
  "sql": "SELECT * FROM `project.dataset.customers` LIMIT 10",
  "data": [
    {
      "customer_id": 1,
      "customer_name": "John Doe",
      "email": "john@example.com",
      "revenue": 5000.50
    }
  ],
  "row_count": 10,
  "columns": ["customer_id", "customer_name", "email", "revenue"]
}
```

**Schema-Agnostic Behavior**: The SQL query and response columns will match your actual BigQuery schema. The system automatically:
- Uses discovered table names
- Generates SQL with actual column names
- Returns results with your actual data structure

**Error Response** (200 OK with error):
```json
{
  "success": false,
  "error": "Failed to generate SQL: Invalid query",
  "query": "invalid query text"
}
```

---

## Request/Response Formats

### Request Format

**Query Parameter (Current)**:
```
GET /?query={url_encoded_query}
```

### Response Format

#### Success Response

```json
{
  "success": true,
  "query": "Original natural language query",
  "summary": "Natural language summary of the results",
  "sql": "Generated SQL query",
  "data": [
    {
      "column1": "value1",
      "column2": "value2"
    }
  ],
  "row_count": 10,
  "columns": ["column1", "column2"]
}
```

#### Error Response

```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "query": "Original query that caused the error",
  "sql": "Generated SQL (if error occurred during execution)"
}
```

---

## Error Handling

### Error Types

#### 1. SQL Generation Errors

**Causes**:
- Query too long (> 500 characters)
- Ambiguous query
- Vertex AI API issues

**Example**:
```json
{
  "success": false,
  "error": "Query too long. Maximum length is 500 characters.",
  "query": "very long query..."
}
```

#### 2. SQL Execution Errors

**Causes**:
- Invalid SQL syntax
- Table doesn't exist
- Permission denied
- BigQuery quota exceeded

**Example**:
```json
{
  "success": false,
  "error": "Table 'project.dataset.nonexistent' not found",
  "query": "Show me data from nonexistent table",
  "sql": "SELECT * FROM `project.dataset.nonexistent`"
}
```

#### 3. Configuration Errors

**Causes**:
- Missing environment variables
- Invalid credentials
- API not enabled

**Example**:
```json
{
  "success": false,
  "error": "Initialization error: Missing required configuration: GCP_PROJECT_ID"
}
```

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success (check `success` field in response) |
| 400 | Bad Request (malformed request) |
| 500 | Internal Server Error |
| 503 | Service Unavailable (backend down) |

---

## Rate Limiting

### Current Implementation

No rate limiting implemented. Each request is processed immediately.

### Recommended for Production

Implement rate limiting to prevent abuse:

```
Rate Limit: 60 requests per minute per IP
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1609459200
```

---

## Examples

### Example 1: Basic Query

**Request**:
```bash
curl -G "http://localhost:8501/" \
  --data-urlencode "query=Show me all customers"
```

**Response**:
```json
{
  "success": true,
  "query": "Show me all customers",
  "summary": "Found 50 customer records in the database. The data includes customer ID, name, email, and revenue details for each customer.",
  "sql": "SELECT * FROM `project.dataset.customers` LIMIT 100",
  "data": [...],
  "row_count": 50,
  "columns": ["customer_id", "customer_name", "email", "revenue"]
}
```

---

### Example 2: Aggregation Query

**Request**:
```bash
curl -G "http://localhost:8501/" \
  --data-urlencode "query=Count total customers"
```

**Response**:
```json
{
  "success": true,
  "query": "Count total customers",
  "summary": "The dataset contains a total of 150 customers.",
  "sql": "SELECT COUNT(*) as total_customers FROM `project.dataset.customers`",
  "data": [
    {
      "total_customers": 150
    }
  ],
  "row_count": 1,
  "columns": ["total_customers"]
}
```

---

### Example 3: JavaScript/Fetch

```javascript
async function queryBigQuery(userQuery) {
  const apiUrl = 'http://localhost:8501/';
  const url = `${apiUrl}?query=${encodeURIComponent(userQuery)}`;
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.success) {
      console.log('Summary:', data.summary);
      console.log('SQL:', data.sql);
      console.log('Results:', data.data);
      return data;
    } else {
      console.error('Error:', data.error);
      return null;
    }
  } catch (error) {
    console.error('Request failed:', error);
    return null;
  }
}

// Usage
queryBigQuery('Show me top 10 customers');
```

---

### Example 4: Python/Requests

```python
import requests
import json

def query_bigquery(user_query):
    api_url = 'http://localhost:8501/'
    params = {'query': user_query}
    
    try:
        response = requests.get(api_url, params=params)
        data = response.json()
        
        if data['success']:
            print(f"Summary: {data['summary']}")
            print(f"SQL: {data['sql']}")
            print(f"Results: {json.dumps(data['data'], indent=2)}")
            return data
        else:
            print(f"Error: {data['error']}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

# Usage
query_bigquery('Show me top 10 customers')
```

---

### Example 5: cURL with Error Handling

```bash
# Successful query
curl -G "http://localhost:8501/" \
  --data-urlencode "query=Show customers with revenue over 5000"

# Error response
curl -G "http://localhost:8501/" \
  --data-urlencode "query=Delete all customers"
```

---

## Widget Integration

The chatbot widget automatically handles API communication. Example from widget:

```javascript
// Widget handles this automatically
async function callAPI(query) {
  const apiEndpoint = `${config.apiUrl}/?query=${encodeURIComponent(query)}`;
  
  const response = await fetch(apiEndpoint, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    }
  });
  
  return await response.json();
}
```

---

## Security Considerations

### Current Implementation

⚠️ **Production Recommendations**:
- No authentication (add for production)
- No rate limiting (implement to prevent abuse)
- CORS configured via environment variables
- Basic input validation

### Recommended for Production

1. **Authentication**: Implement API key or OAuth
2. **Rate Limiting**: Prevent abuse
3. **Input Validation**: Strict validation of user input
4. **CORS**: Restrict to specific domains
5. **HTTPS**: Encrypt all traffic
6. **Logging**: Log all requests for audit
7. **Monitoring**: Set up alerts for unusual activity

---

## Performance

### Typical Response Times

- **Query Generation**: 1-3 seconds (Vertex AI)
- **Query Execution**: 0.5-5 seconds (BigQuery)
- **Summary Generation**: 1-2 seconds (Vertex AI)
- **Total**: 2.5-10 seconds

### Optimization Tips

1. **Caching**: Cache common queries
2. **Connection Pooling**: Reuse BigQuery connections
3. **Async Processing**: Process queries asynchronously
4. **Query Optimization**: Optimize generated SQL
5. **CDN**: Serve widget files from CDN

---

## Changelog

### Version 1.0 (Current)

- Initial release
- Natural language to SQL conversion using Vertex AI
- BigQuery query execution
- Natural language summaries
- FastAPI-based backend
- GET endpoint for chat queries

### Planned Features

- POST endpoint for chat
- Authentication system
- Rate limiting
- Query history
- WebSocket support for real-time updates
- Advanced error handling
- Query caching

---

## Support

For API issues:
1. Check backend logs
2. Verify configuration
3. Test with curl/Postman
4. Review [Setup Guide](SETUP_GUIDE.md)
5. Check [Troubleshooting](INTEGRATION_GUIDE.md#troubleshooting)

---

**API Documentation v1.0**






