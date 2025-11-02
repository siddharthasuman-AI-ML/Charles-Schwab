# Toggle Response Mode Instructions

## Overview

The BigQuery Chatbot supports **two response modes** that can be easily toggled:

- **Mode 1 (Full Response)**: Returns Natural Language Summary + SQL Query + Data Table
- **Mode 2 (Natural Language Only)**: Returns only Natural Language Summary

This guide explains how to switch between these modes in both **Part_A** (Demo) and **Part_B** (Production).

---

## Quick Summary

| Mode | What User Sees |
|------|---------------|
| **Mode 1 (Full)** | ✅ Natural Language Summary<br>✅ Generated SQL Query<br>✅ Data Table with Results |
| **Mode 2 (Natural Language Only)** | ✅ Natural Language Summary only |

---

## Files to Modify

You need to modify **4 files** to switch modes:

### Backend Files:
1. `Part_A/backend/app.py` (Demo Version)
2. `Part_B/backend/app.py` (Production Version)

### Frontend Files:
3. `Part_A/frontend/chatbot-widget.js` (Demo Version)
4. `Part_B/frontend/chatbot-widget.js` (Production Version)

---

## Step-by-Step Instructions

### 🔄 Switching from Mode 1 to Mode 2 (Natural Language Only)

#### Step 1: Update Backend Files

**For `Part_A/backend/app.py`:**

1. **Change the RESPONSE_MODE variable** (Line 40):
   ```python
   # Change this:
   RESPONSE_MODE = "full"
   
   # To this:
   RESPONSE_MODE = "natural_language_only"
   ```

2. **Comment out the MODE 1 block** (Lines 566-570):
   ```python
   # Comment out this entire block:
   # if RESPONSE_MODE == "full":
   #     response['sql'] = sql_query
   #     response['data'] = query_result['data']
   #     response['row_count'] = query_result['row_count']
   #     response['columns'] = query_result['columns']
   ```

3. **Uncomment the MODE 2 block** (Lines 576-578):
   ```python
   # Uncomment this block:
   if RESPONSE_MODE == "natural_language_only":
       # No SQL or data included - only summary
       pass
   ```

**For `Part_B/backend/app.py`:**

1. **Change the RESPONSE_MODE variable** (Line 44):
   ```python
   # Change this:
   RESPONSE_MODE = "full"
   
   # To this:
   RESPONSE_MODE = "natural_language_only"
   ```

2. **Comment out the MODE 1 block** (Lines 626-630):
   ```python
   # Comment out this entire block:
   # if RESPONSE_MODE == "full":
   #     response['sql'] = sql_query
   #     response['data'] = query_result['data']
   #     response['row_count'] = query_result['row_count']
   #     response['columns'] = query_result['columns']
   ```

3. **Uncomment the MODE 2 block** (Lines 636-638):
   ```python
   # Uncomment this block:
   if RESPONSE_MODE == "natural_language_only":
       # No SQL or data included - only summary
       pass
   ```

#### Step 2: Update Frontend Files

**For `Part_A/frontend/chatbot-widget.js` and `Part_B/frontend/chatbot-widget.js`:**

1. **Comment out the MODE 1 block** (Lines 290-306):
   ```javascript
   // Comment out this entire block:
   // // Show SQL query
   // if (response.sql) {
   //     content += `
   //         <div class="bq-sql-block">
   //             <div class="bq-sql-label">Generated SQL:</div>
   //             <code class="bq-sql-code">${this.escapeHtml(response.sql)}</code>
   //         </div>
   //     `;
   // }
   // 
   // // Show results table
   // if (response.data && response.data.length > 0) {
   //     content += `<p><strong>Results:</strong> (${response.row_count} rows)</p>`;
   //     content += this.formatDataTable(response.data, response.columns);
   // } else {
   //     content += '<p>✅ Query executed successfully, but no data was returned.</p>';
   // }
   ```

2. **Uncomment the MODE 2 block** (Lines 311-313):
   ```javascript
   // Uncomment this block:
   if (response.summary) {
       // Only summary shown - no SQL or table
       // content += '<p class="bq-message-hint">💡 Natural language summary only mode</p>';
   }
   ```

---

### 🔄 Switching from Mode 2 to Mode 1 (Full Response)

#### Step 1: Update Backend Files

**For `Part_A/backend/app.py`:**

1. **Change the RESPONSE_MODE variable** (Line 40):
   ```python
   # Change this:
   RESPONSE_MODE = "natural_language_only"
   
   # To this:
   RESPONSE_MODE = "full"
   ```

2. **Uncomment the MODE 1 block** (Lines 566-570):
   ```python
   # Uncomment this entire block:
   if RESPONSE_MODE == "full":
       response['sql'] = sql_query
       response['data'] = query_result['data']
       response['row_count'] = query_result['row_count']
       response['columns'] = query_result['columns']
   ```

3. **Comment out the MODE 2 block** (Lines 576-578):
   ```python
   # Comment out this block:
   # if RESPONSE_MODE == "natural_language_only":
   #     # No SQL or data included - only summary
   #     pass
   ```

**For `Part_B/backend/app.py`:**

1. **Change the RESPONSE_MODE variable** (Line 44):
   ```python
   # Change this:
   RESPONSE_MODE = "natural_language_only"
   
   # To this:
   RESPONSE_MODE = "full"
   ```

2. **Uncomment the MODE 1 block** (Lines 626-630):
   ```python
   # Uncomment this entire block:
   if RESPONSE_MODE == "full":
       response['sql'] = sql_query
       response['data'] = query_result['data']
       response['row_count'] = query_result['row_count']
       response['columns'] = query_result['columns']
   ```

3. **Comment out the MODE 2 block** (Lines 636-638):
   ```python
   # Comment out this block:
   # if RESPONSE_MODE == "natural_language_only":
   #     # No SQL or data included - only summary
   #     pass
   ```

#### Step 2: Update Frontend Files

**For `Part_A/frontend/chatbot-widget.js` and `Part_B/frontend/chatbot-widget.js`:**

1. **Uncomment the MODE 1 block** (Lines 290-306):
   ```javascript
   // Uncomment this entire block:
   // Show SQL query
   if (response.sql) {
       content += `
           <div class="bq-sql-block">
               <div class="bq-sql-label">Generated SQL:</div>
               <code class="bq-sql-code">${this.escapeHtml(response.sql)}</code>
           </div>
       `;
   }
   
   // Show results table
   if (response.data && response.data.length > 0) {
       content += `<p><strong>Results:</strong> (${response.row_count} rows)</p>`;
       content += this.formatDataTable(response.data, response.columns);
   } else {
       content += '<p>✅ Query executed successfully, but no data was returned.</p>';
   }
   ```

2. **Comment out the MODE 2 block** (Lines 311-313):
   ```javascript
   // Comment out this block:
   // if (response.summary) {
   //     // Only summary shown - no SQL or table
   //     // content += '<p class="bq-message-hint">💡 Natural language summary only mode</p>';
   // }
   ```

---

## How to Find the Code Blocks

### Backend Files

1. **Find RESPONSE_MODE variable:**
   - Search for `RESPONSE_MODE = "full"` or `RESPONSE_MODE = "natural_language_only"`
   - **Part_A**: Around line 40
   - **Part_B**: Around line 44

2. **Find MODE 1 block:**
   - Search for `if RESPONSE_MODE == "full":`
   - **Part_A**: Around line 566
   - **Part_B**: Around line 626

3. **Find MODE 2 block:**
   - Search for `if RESPONSE_MODE == "natural_language_only":`
   - **Part_A**: Around line 576
   - **Part_B**: Around line 636

### Frontend Files

1. **Find MODE 1 block:**
   - Search for `// MODE 1: Show SQL and Table`
   - Both Part_A and Part_B: Around line 286-290

2. **Find MODE 2 block:**
   - Search for `// MODE 2: Only Natural Language`
   - Both Part_A and Part_B: Around line 309-311

---

## Important Notes

1. **Always modify both Part_A and Part_B** if you want consistency across demo and production.

2. **Restart the backend server** after making backend changes:
   - For Part_A: `cd Part_A/backend && python app.py`
   - For Part_B: `cd Part_B/backend && python app.py`

3. **Hard refresh the browser** after making frontend changes:
   - Windows/Linux: `Ctrl + Shift + R` or `Ctrl + F5`
   - Mac: `Cmd + Shift + R`

4. **Natural Language Summary is always included** in both modes - it's the base response that cannot be disabled.

5. **Part_B is schema-agnostic** - toggle mode works regardless of your BigQuery schema. The mode only affects what is displayed to the user, not how queries are processed.

---

## Testing After Changes

After switching modes, test with sample queries:

- "Show me all customers"
- "Count total records"
- "Get top 5 customers by revenue"
- "What is John Doe's email?" (Part_B - works with any schema)

**Expected Results:**
- **Mode 1**: You should see Summary + SQL + Table
- **Mode 2**: You should see Summary only

---

## Troubleshooting

### Issue: Still seeing SQL and Table after switching to Mode 2

**Solution:**
1. Make sure you changed `RESPONSE_MODE` to `"natural_language_only"` in backend files
2. Make sure you commented out the SQL/Table display block in frontend files
3. Restart the backend server
4. Hard refresh the browser (Ctrl+Shift+R)

### Issue: Mode 1 not showing SQL and Table

**Solution:**
1. Make sure `RESPONSE_MODE = "full"` in backend files
2. Make sure the SQL/Table display block is uncommented in frontend files
3. Check browser console for JavaScript errors
4. Verify the backend is returning `sql`, `data`, and `columns` in the response

### Issue: Line numbers don't match

**Solution:**
1. Use the search function in your editor to find `RESPONSE_MODE` or `MODE 1:` markers
2. The code blocks are clearly marked with comment headers like `# MODE 1:` or `// MODE 1:`
3. Line numbers may vary slightly - use search instead of relying on exact line numbers

---

## Current Configuration Location

In each backend file (`app.py`), look for:

```python
# ============================================================================
# RESPONSE MODE CONFIGURATION
# ============================================================================
# Set this to control what the chatbot returns:
# - "full": Returns Natural Language Summary + SQL + Table (Default)
# - "natural_language_only": Returns only Natural Language Summary
RESPONSE_MODE = "full"  # Change to "natural_language_only" for Mode 2
```

This is where you change the mode!

**Part_A Location**: Line 40  
**Part_B Location**: Line 44

---

## Questions?

If you encounter any issues or need clarification, check the inline comments in the code files - they clearly mark what needs to be commented/uncommented for each mode.

The toggle mode functionality works independently of the schema-agnostic features in Part_B. You can toggle between modes regardless of what BigQuery tables or columns you're using.
