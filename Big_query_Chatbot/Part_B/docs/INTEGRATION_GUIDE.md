# BigQuery Chatbot - Integration Guide

This guide will help Team B integrate the BigQuery Chatbot widget into their web application.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Integration Steps](#integration-steps)
5. [Configuration Options](#configuration-options)
6. [Customization](#customization)
7. [Troubleshooting](#troubleshooting)
8. [Examples](#examples)

---

## Overview

The BigQuery Chatbot is a fully self-contained widget that can be embedded into any website with just a few lines of code. It provides a natural language interface to query BigQuery databases.

**Key Features:**
- 🎯 Drop-in integration (no dependencies)
- 🎨 Modern, responsive design
- 🔒 Secure API communication
- ⚡ Real-time query results
- 📱 Mobile-friendly
- 💬 Natural language summaries
- 🏗️ **Schema-agnostic**: Works with ANY BigQuery dataset automatically

---

## Prerequisites

Before integrating the chatbot, ensure you have:

1. **Backend Server Running**: The FastAPI backend must be deployed and accessible
2. **CORS Configured**: Backend must allow requests from your domain
3. **BigQuery Access**: Backend must have proper GCP credentials configured
4. **Modern Browser**: Widget supports all modern browsers (Chrome, Firefox, Safari, Edge)

**Note**: The chatbot automatically discovers your BigQuery schema on startup - no need to configure table or column names! It works with any dataset structure.

---

## Quick Start

The fastest way to integrate the chatbot:

### 1. Copy Widget Files

Copy these files to your project:
```
your-project/
├── assets/
│   ├── chatbot-widget.js
│   └── chatbot-widget.css
```

### 2. Add to Your HTML

Add this code just before the closing `</body>` tag:

```html
<!-- BigQuery Chatbot Widget -->
<link rel="stylesheet" href="assets/chatbot-widget.css">
<script src="assets/chatbot-widget.js"></script>
<script>
  ChatbotWidget.init({
    apiUrl: 'https://your-backend-url.com'
  });
</script>
```

### 3. Test

Open your website and click the chat icon in the bottom-right corner!

---

## Integration Steps

### Step 1: Include CSS File

Add the widget stylesheet to your HTML `<head>` section:

```html
<head>
  <!-- Your existing head content -->
  <link rel="stylesheet" href="path/to/chatbot-widget.css">
</head>
```

### Step 2: Include JavaScript File

Add the widget JavaScript before the closing `</body>` tag:

```html
<body>
  <!-- Your existing body content -->
  
  <script src="path/to/chatbot-widget.js"></script>
</body>
```

### Step 3: Initialize Widget

Add initialization code after the JavaScript file:

```html
<script>
  ChatbotWidget.init({
    apiUrl: 'https://your-backend-url.com',
    position: 'bottom-right',
    theme: 'light'
  });
</script>
```

### Step 4: Update Backend URL

Replace `'https://your-backend-url.com'` with your actual backend server URL.

**Example URLs:**
- Local development: `http://localhost:8501`
- Production: `https://api.yourcompany.com/chatbot`

---

## Configuration Options

### Basic Configuration

```javascript
ChatbotWidget.init({
  apiUrl: 'https://your-backend-url.com',  // Required
  position: 'bottom-right',                 // Optional
  theme: 'light'                            // Optional
});
```

### Configuration Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `apiUrl` | string | Yes | - | URL of the backend API server |
| `position` | string | No | `'bottom-right'` | Widget position on screen |
| `theme` | string | No | `'light'` | Color theme (currently only 'light') |

### Alternative Initialization (Auto-Initialize)

You can also use auto-initialization:

```html
<script>
  // Define config before loading widget
  window.BQ_CHATBOT_CONFIG = {
    apiUrl: 'https://your-backend-url.com'
  };
</script>
<script src="path/to/chatbot-widget.js"></script>
```

The widget will automatically initialize when the page loads.

---

## Customization

### CSS Variables

You can customize the widget's appearance by overriding CSS variables:

```html
<style>
  :root {
    --bq-primary-color: #your-brand-color;
    --bq-primary-hover: #your-hover-color;
    /* Add more custom variables */
  }
</style>
```

### Available CSS Variables

```css
:root {
  --bq-primary-color: #4285f4;      /* Primary brand color */
  --bq-primary-hover: #357ae8;      /* Hover state color */
  --bq-secondary-color: #34a853;    /* Secondary accent */
  --bq-background: #ffffff;         /* Background color */
  --bq-surface: #f8f9fa;            /* Surface color */
  --bq-border: #e0e0e0;             /* Border color */
  --bq-text-primary: #202124;       /* Primary text */
  --bq-text-secondary: #5f6368;     /* Secondary text */
  --bq-error: #ea4335;              /* Error color */
}
```

### Custom Positioning

To change the widget position, modify the CSS:

```css
.bq-chatbot-container {
  bottom: 20px;  /* Distance from bottom */
  right: 20px;   /* Distance from right */
}
```

---

## Troubleshooting

### Widget Not Appearing

**Check:**
1. CSS and JS files are loaded correctly (check browser console)
2. No JavaScript errors in console
3. Files paths are correct
4. Widget initialization code is present

### CORS Errors

**Symptoms:** Console shows "CORS policy" errors

**Solution:**
1. Configure CORS on your backend server
2. Add your domain to allowed origins
3. For FastAPI, check CORS_ORIGINS in .env file

### API Connection Failed

**Symptoms:** Messages not sending, "Error" responses

**Check:**
1. Backend server is running
2. `apiUrl` is correct
3. Network connectivity
4. Backend health endpoint is accessible

### Styling Issues

**Check:**
1. CSS file is loaded before widget initialization
2. No conflicting CSS from your site
3. Check browser developer tools for CSS errors

### Widget Overlapping Content

**Solution:**
```css
/* Add z-index to your content if needed */
.your-content {
  z-index: 1;
}

/* Widget has z-index: 9999 by default */
```

---

## Examples

### Example 1: Basic Integration

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>My Website</title>
  <link rel="stylesheet" href="assets/chatbot-widget.css">
</head>
<body>
  <h1>Welcome to My Website</h1>
  
  <script src="assets/chatbot-widget.js"></script>
  <script>
    ChatbotWidget.init({
      apiUrl: 'https://api.mycompany.com/chatbot'
    });
  </script>
</body>
</html>
```

### Example 2: Custom Colors

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>My Website</title>
  <link rel="stylesheet" href="assets/chatbot-widget.css">
  <style>
    :root {
      --bq-primary-color: #ff6b6b;
      --bq-primary-hover: #ee5a5a;
    }
  </style>
</head>
<body>
  <h1>Welcome to My Website</h1>
  
  <script src="assets/chatbot-widget.js"></script>
  <script>
    ChatbotWidget.init({
      apiUrl: 'https://api.mycompany.com/chatbot'
    });
  </script>
</body>
</html>
```

### Example 3: React/Vue Integration

For React or Vue applications:

```javascript
// In your component's mounted/useEffect hook
useEffect(() => {
  // Dynamically load CSS
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = '/assets/chatbot-widget.css';
  document.head.appendChild(link);
  
  // Dynamically load JS
  const script = document.createElement('script');
  script.src = '/assets/chatbot-widget.js';
  script.onload = () => {
    window.ChatbotWidget.init({
      apiUrl: 'https://api.mycompany.com/chatbot'
    });
  };
  document.body.appendChild(script);
  
  return () => {
    // Cleanup if needed
    document.head.removeChild(link);
    document.body.removeChild(script);
  };
}, []);
```

---

## Best Practices

1. **Load Order**: Always load CSS before JavaScript
2. **API URL**: Use environment variables for API URLs
3. **Error Handling**: Monitor browser console for errors
4. **Testing**: Test on multiple browsers and devices
5. **Performance**: Widget is lightweight, but test page load times
6. **Security**: Always use HTTPS in production
7. **Updates**: Keep widget files updated with latest version

---

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review [API Documentation](API_DOCUMENTATION.md)
3. Check [Setup Guide](SETUP_GUIDE.md) for backend configuration
4. Contact Team A for technical support

---

## Version Information

- **Widget Version**: 1.0
- **Last Updated**: 2025
- **Compatibility**: All modern browsers
- **Dependencies**: None (self-contained)
- **Backend**: FastAPI with Vertex AI + BigQuery

---

**Happy Integrating! 🚀**






