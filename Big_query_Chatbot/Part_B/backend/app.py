"""
FastAPI Backend for BigQuery Chatbot - PRODUCTION VERSION
Uses Vertex AI + BigQuery for production
Includes Natural Language Summaries
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from config import Config
from llm_handler import LLMHandler
from bigquery_handler import BigQueryHandler
from schema_manager import SchemaManager
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BigQuery Chatbot API",
    description="Production API using Vertex AI + BigQuery",
    version="1.0.0"
)

# Enable CORS - Configure allowed origins for production
cors_origins = Config.CORS_ORIGINS.split(',') if Config.CORS_ORIGINS != '*' else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# RESPONSE MODE CONFIGURATION
# ============================================================================
# Set this to control what the chatbot returns:
# - "full": Returns Natural Language Summary + SQL + Table (Default)
# - "natural_language_only": Returns only Natural Language Summary
RESPONSE_MODE = "full"  # Change to "natural_language_only" for Mode 2

# Initialize handlers
llm_handler = None
bq_handler = None
schema_manager = None

try:
    Config.validate()
    bq_handler = BigQueryHandler()
    
    # Initialize schema manager first
    try:
        schema_manager = SchemaManager(bq_handler)
        schema_manager.discover_all_tables()
        logger.info("✅ Schema discovery completed")
    except Exception as e:
        logger.warning(f"⚠️ Schema discovery failed: {e}. LLM will work without schema info.")
        schema_manager = None
    
    # Initialize LLM handler with schema manager
    llm_handler = LLMHandler(schema_manager=schema_manager)
    
    logger.info("✅ Handlers initialized successfully")
except Exception as e:
    logger.error(f"❌ Error initializing handlers: {str(e)}")
    logger.error("Please check your configuration in .env file")


def extract_answer_with_logic(user_query: str, data: list, columns: list = None) -> str:
    """
    COMPLETELY GENERIC logic-based answer extraction
    Works with ANY data structure - analyzes actual returned data intelligently
    This is what makes chatbots preferred - they understand context from actual data!
    
    Args:
        user_query: Original user query
        data: Query results data (whatever SQL returned)
        columns: Column names from the results
        
    Returns:
        Answer string if extraction successful, None otherwise
    """
    if not data or not columns:
        logger.warning(f"⚠️ No data or columns. Data rows: {len(data) if data else 0}, Columns: {columns}")
        return None
    
    query_lower = user_query.lower().strip()
    logger.info(f"📊 Analyzing data structure - Columns: {columns}")
    logger.info(f"📊 Sample row data: {data[0] if data else 'None'}")
    
    # STEP 1: Intelligently identify column types from ACTUAL data (not assumptions!)
    name_like_cols = []
    value_cols = []
    id_cols = []
    
    for col in columns:
        col_lower = col.lower()
        # Check for ID columns FIRST (before name columns)
        # ID columns: ends with '_id' or 'id' and doesn't contain 'name'
        if (col_lower.endswith('_id') or (col_lower.endswith('id') and '_' in col_lower)) and 'name' not in col_lower:
            id_cols.append(col)
        # Name-like columns (contain person/entity names)
        # Must contain 'name' AND not be an ID column
        elif 'name' in col_lower and not col_lower.endswith('_id'):
            name_like_cols.append(col)
        # Value columns (numbers, amounts, etc.)
        elif any(term in col_lower for term in ['revenue', 'price', 'amount', 'cost', 'value', 'total', 'quantity', 'count', 'sum', 'avg']):
            value_cols.append(col)
        # Catch any remaining ID columns (standalone 'id')
        elif col_lower == 'id':
            id_cols.append(col)
    
    # Find requested field from query (ANY field user asks about)
    # Dynamic matching - no hardcoded phrases!
    requested_field_keywords = []
    
    # Essential stop words only (articles, prepositions, common verbs)
    # Don't exclude words that might be column names!
    stop_words = {'is', 'the', 'what', 'show', 'me', 'get', 'find', 'tell', 'and', 'or', 'of', 'for', 'a', 'an', 'give', 'only', 'highest', 'lowest', 'by', 'how', 'much', 'which', 'who', 'when', 'where'}
    
    # DYNAMIC PHRASE EXTRACTION: Extract multi-word phrases from query
    # Look for patterns like "customer id", "date of creation", etc.
    # Match them against actual column names in the data
    words = query_lower.split()
    
    # Extract multi-word phrases (2-3 words)
    for i in range(len(words) - 1):
        # Two-word phrases
        phrase_2 = f"{words[i]} {words[i+1]}"
        if i < len(words) - 2:
            # Three-word phrases
            phrase_3 = f"{words[i]} {words[i+1]} {words[i+2]}"
            # Check if this phrase matches any column (handle variations: spaces, underscores, camelCase)
            for col in columns:
                col_lower = col.lower()
                phrase_variants = [
                    phrase_3,
                    phrase_3.replace(' ', '_'),
                    phrase_3.replace(' ', ''),
                    phrase_3.replace(' of ', '_'),
                ]
                for variant in phrase_variants:
                    if variant in col_lower or col_lower in variant:
                        if (phrase_3, col) not in requested_field_keywords:
                            requested_field_keywords.append((phrase_3, col))
                            break
        
        # Check two-word phrases
        phrase_variants = [
            phrase_2,
            phrase_2.replace(' ', '_'),
            phrase_2.replace(' ', ''),
        ]
        for variant in phrase_variants:
            for col in columns:
                col_lower = col.lower()
                if variant in col_lower or col_lower in variant:
                    if (phrase_2, col) not in requested_field_keywords:
                        requested_field_keywords.append((phrase_2, col))
                    break
    
    # Also check individual words (fuzzy matching)
    for word in words:
        if word not in stop_words and len(word) > 2:
            for col in columns:
                col_lower = col.lower()
                # Multiple matching strategies:
                # 1. Exact substring match
                # 2. Word boundary match
                # 3. Partial match (for abbreviations)
                if (word in col_lower or col_lower in word or
                    re.search(rf'\b{re.escape(word)}\b', col_lower) or
                    re.search(rf'\b{re.escape(col_lower)}\b', word)):
                    if (word, col) not in requested_field_keywords:
                        requested_field_keywords.append((word, col))
    
    # Extract ALL names from query - MULTIPLE STRATEGIES
    extracted_names = set()
    
    # Strategy 1: Capitalized words (handles "John", "John Doe", "Alice Brown")
    capitalized_names = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', user_query)
    extracted_names.update(capitalized_names)
    
    # Strategy 2: Lowercase words that look like names
    # Pure capitalization-based - no hardcoded name list!
    # A lowercase word that appears capitalized in the data is likely a name
    # We'll match it during row matching, not here
    words = query_lower.split()
    for word in words:
        if word not in stop_words and len(word) > 2:
            # Check if this word, when capitalized, appears in any name-like column
            # This will be verified during actual data matching
            extracted_names.add(word.capitalize())
    
    # Strategy 3: Patterns like "give john email" or "john's email"
    # Extract word before "email" or after common verbs
    name_before_email = re.search(r'(\w+)\s+(?:email|e-mail)', query_lower)
    if name_before_email:
        name_word = name_before_email.group(1)
        if name_word not in stop_words:
            extracted_names.add(name_word.capitalize())
    
    # Strategy 4: "X and Y" patterns (case-insensitive)
    and_pattern = r'(\w+)\s+and\s+(\w+)'
    and_match = re.search(and_pattern, query_lower)
    if and_match:
        name1 = and_match.group(1)
        name2 = and_match.group(2)
        if name1 not in stop_words:
            extracted_names.add(name1.capitalize())
        if name2 not in stop_words:
            extracted_names.add(name2.capitalize())
    
    # Strategy 5: Possessive patterns like "John's" or "Alice's"
    possessive_pattern = r'(\w+)\'s'
    possessive_matches = re.findall(possessive_pattern, query_lower)
    for name in possessive_matches:
        if name not in stop_words:
            extracted_names.add(name.capitalize())
    
    logger.info(f"🔍 Extracted names: {extracted_names}")
    logger.info(f"🔍 Name-like columns found: {name_like_cols}")
    logger.info(f"🔍 Value columns found: {value_cols}")
    
    # STEP 2: If user asks about specific person(s) - find matching row(s)
    if extracted_names:
        matching_rows = []
        
        for row in data:
            # Check each name-like column for matches
            for name_col in name_like_cols:
                if name_col in row and row[name_col]:
                    row_name = str(row[name_col])
                    row_name_lower = row_name.lower()
                    
                    # Check if any extracted name matches this row
                    for ext_name in extracted_names:
                        ext_name_lower = ext_name.lower()
                        ext_words = ext_name_lower.split()
                        row_words = row_name_lower.split()
                        
                        # Flexible matching
                        if (ext_name_lower == row_name_lower or
                            ext_name_lower in row_name_lower or
                            row_name_lower.startswith(ext_name_lower) or
                            all(word in row_words for word in ext_words)):
                            matching_rows.append((row, row_name, name_col))
                            break
        
        if matching_rows:
            results = []
            # Now extract what user wants from matching rows
            for row, row_name, name_col in matching_rows:
                # Find what field user is asking about
                found_answer = False
                
                # Check if user asks for specific field by keyword
                # Priority: check exact matches first, then fuzzy matches
                for keyword, matching_col in requested_field_keywords:
                    if matching_col in row and row[matching_col] is not None:
                        val = str(row[matching_col]).strip()
                        if val and val != 'None':
                            results.append(f"{row_name}'s {matching_col} is {val}")
                            found_answer = True
                            break
                
                # Also check all columns (including ID columns) if user explicitly asks for them
                if not found_answer:
                    for keyword, matching_col in requested_field_keywords:
                        # Check if keyword matches any column name (case-insensitive)
                        for col in columns:
                            col_lower = col.lower()
                            keyword_lower = keyword.lower() if isinstance(keyword, str) else ''
                            # Match if keyword is in column name or column name contains keyword
                            if (keyword_lower in col_lower or col_lower in keyword_lower or 
                                keyword_lower.replace(' ', '_') in col_lower or
                                col_lower.replace('_', ' ') in keyword_lower):
                                if col in row and row[col] is not None:
                                    val = str(row[col]).strip()
                                    if val and val != 'None':
                                        results.append(f"{row_name}'s {col} is {val}")
                                        found_answer = True
                                        break
                        if found_answer:
                            break
                
                # If not found, check common fields user might ask about
                if not found_answer:
                    # Email
                    for col in columns:
                        if 'email' in col.lower() and col in row and row[col]:
                            val = str(row[col]).strip()
                            if val and val != 'None':
                                results.append(f"{row_name}'s email is {val}")
                                found_answer = True
                                break
                    
                    # Revenue/Amount/Price
                    if not found_answer:
                        for col in value_cols:
                            if col in row and row[col] is not None:
                                val = str(row[col]).strip()
                                if val and val != 'None':
                                    results.append(f"{row_name}'s {col} is {val}")
                                    found_answer = True
                                    break
                    
                    # If still nothing, return first non-name, non-id column
                    if not found_answer:
                        for col in columns:
                            if col != name_col and col not in id_cols and col in row and row[col] is not None:
                                val = str(row[col]).strip()
                                if val and val != 'None':
                                    results.append(f"{row_name}'s {col} is {val}")
                                    break
            
            if results:
                return "; ".join(results) if len(results) > 1 else results[0]
    
    # STEP 3: Aggregate queries (highest, lowest, max, min)
    if any(word in query_lower for word in ['highest', 'maximum', 'max', 'top', 'largest', 'biggest']):
        # Prioritize columns that match query keywords
        cols_to_check = []
        
        # First, check requested_field_keywords for exact matches
        for keyword, matching_col in requested_field_keywords:
            if matching_col in value_cols or matching_col in columns:
                cols_to_check.append(matching_col)
        
        # Also check if query mentions specific value terms
        for word in query_lower.split():
            if word not in stop_words:
                for col in value_cols:
                    if word in col.lower() or col.lower() in word:
                        if col not in cols_to_check:
                            cols_to_check.append(col)
        
        # If no specific match, use all value columns
        if not cols_to_check:
            cols_to_check = value_cols
        
        # Find numeric column
        for col in cols_to_check:
            try:
                max_val = None
                max_row = None
                for row in data:
                    val = row.get(col)
                    if val is not None:
                        try:
                            num_val = float(val)
                            if max_val is None or num_val > max_val:
                                max_val = num_val
                                max_row = row
                        except (ValueError, TypeError):
                            pass
                
                if max_row and max_val is not None:
                    # Try to find name
                    name = None
                    for name_col in name_like_cols:
                        if name_col in max_row and max_row[name_col]:
                            name = str(max_row[name_col])
                            break
                    if name:
                        return f"The highest {col} is {max_val} (belongs to {name})"
                    else:
                        return f"The highest {col} is {max_val}"
            except Exception:
                continue
    
    if any(word in query_lower for word in ['lowest', 'minimum', 'min', 'smallest', 'least']):
        # Prioritize columns that match query keywords
        cols_to_check = []
        
        # First, check requested_field_keywords for exact matches
        for keyword, matching_col in requested_field_keywords:
            if matching_col in value_cols or matching_col in columns:
                cols_to_check.append(matching_col)
        
        # Also check if query mentions specific value terms
        for word in query_lower.split():
            if word not in stop_words:
                for col in value_cols:
                    if word in col.lower() or col.lower() in word:
                        if col not in cols_to_check:
                            cols_to_check.append(col)
        
        # If no specific match, use all value columns
        if not cols_to_check:
            cols_to_check = value_cols
        
        for col in cols_to_check:
            try:
                min_val = None
                min_row = None
                for row in data:
                    val = row.get(col)
                    if val is not None:
                        try:
                            num_val = float(val)
                            if min_val is None or num_val < min_val:
                                min_val = num_val
                                min_row = row
                        except (ValueError, TypeError):
                            pass
                
                if min_row and min_val is not None:
                    name = None
                    for name_col in name_like_cols:
                        if name_col in min_row and min_row[name_col]:
                            name = str(min_row[name_col])
                            break
                    if name:
                        return f"The lowest {col} is {min_val} (belongs to {name})"
                    else:
                        return f"The lowest {col} is {min_val}"
            except Exception:
                continue
    
    # STEP 4: Count queries
    if 'count' in query_lower or 'how many' in query_lower:
        return f"There are {len(data)} record(s)"
    
    # STEP 5: Single row - return relevant field or all data
    if len(data) == 1:
        row = data[0]
        # Try to find what user is asking about
        for keyword, matching_col in requested_field_keywords:
            if matching_col in row and row[matching_col] is not None:
                return f"The {matching_col} is {row[matching_col]}"
        
        # Return first non-ID column value
        for col in columns:
            if col not in id_cols and col in row and row[col] is not None:
                val = str(row[col]).strip()
                if val and val != 'None':
                    return f"The {col} is {val}"
    
    # STEP 6: Multiple rows - return list of requested field
    # ONLY run this if no names were extracted (otherwise name-based filtering should have handled it)
    if len(data) > 1 and not extracted_names:
        # Find what column user is asking about
        for keyword, matching_col in requested_field_keywords:
            values = [str(row.get(matching_col)) for row in data if matching_col in row and row[matching_col] is not None]
            if values:
                unique_vals = list(dict.fromkeys(values))  # Remove duplicates, preserve order
                if len(unique_vals) <= 10:
                    return f"The {matching_col} values are: {', '.join(unique_vals)}"
                else:
                    return f"The {matching_col} values are: {', '.join(unique_vals[:10])} (and {len(unique_vals)-10} more)"
    
    logger.info("⚠️ Could not extract answer with logic - will use LLM fallback")
    return None  # Could not extract - will use LLM


def generate_natural_language_summary(user_query: str, sql_query: str, data: list, row_count: int, columns: list = None) -> str:
    """
    Generate an accurate natural language answer from query results
    Uses LOGIC FIRST, then LLM as fallback for better accuracy
    
    Args:
        user_query: Original user query from user
        sql_query: Generated SQL query
        data: Query results data (all rows)
        row_count: Number of rows returned
        columns: Column names from the query results
        
    Returns:
        Natural language answer string with exact values from the data
    """
    if not data or row_count == 0:
        return "No data found matching your query."
    
    # STEP 1: Try logic-based extraction FIRST (fast and accurate)
    if columns and len(data) > 0:
        logger.info(f"🔍 Attempting logic-based extraction for: {user_query}")
        logic_answer = extract_answer_with_logic(user_query, data, columns)
        if logic_answer:
            logger.info(f"✅ Logic extraction successful: {logic_answer[:100]}...")
            return logic_answer
    
    # STEP 2: Fallback to LLM if logic extraction failed
    if not llm_handler:
        # Final fallback without LLM
        if row_count == 1 and len(data) > 0 and columns:
            row = data[0]
            # Try simple field matching
            query_lower = user_query.lower()
            for col in columns:
                if col.lower() in query_lower:
                    val = row.get(col)
                    if val is not None:
                        return f"The {col} is {val}"
            return f"Found 1 record: {row}"
        return f"Found {row_count} record(s). Please check the data table below for details."
    
    try:
        # Use LLM as secondary option
        max_data_rows = 50
        data_to_analyze = data[:max_data_rows] if len(data) > max_data_rows else data
        
        # Format data
        if columns:
            data_str = "\n".join([
                f"Row {i+1}: " + ", ".join([f"{col}={row.get(col, 'N/A')}" for col in columns])
                for i, row in enumerate(data_to_analyze)
            ])
        else:
            data_str = "\n".join([f"Row {i+1}: {row}" for i, row in enumerate(data_to_analyze)])
        
        if len(data) > max_data_rows:
            data_str += f"\n[Note: Showing first {max_data_rows} of {row_count} total rows]"
        
        # Enhanced prompt
        summary_prompt = f"""You are a precise data analyst. Answer using EXACT values from the data.

QUESTION: "{user_query}"
SQL: {sql_query}
DATA ({row_count} rows):
{data_str}

IMPORTANT: Extract the EXACT answer from the data. If the data shows email='john@example.com' and user asks for John's email, answer: "John's email is john@example.com"

ANSWER:"""
        
        logger.info(f"🤖 Using LLM fallback for: {user_query}")
        # Use Vertex AI to generate summary (reuse the model from LLM handler)
        response = llm_handler.model.generate_content(summary_prompt)
        summary = response.text.strip()
        
        if summary.startswith("ANSWER:"):
            summary = summary[7:].strip()
        
        logger.info(f"✅ LLM generated answer: {summary[:100]}...")
        return summary
        
    except Exception as e:
        logger.error(f"❌ LLM error: {str(e)}")
        # Final fallback
        if row_count == 1 and len(data) > 0 and columns:
            row = data[0]
            for col in columns:
                if col.lower() in user_query.lower():
                    return f"The {col} is {row.get(col, 'N/A')}"
        return f"Found {row_count} record(s). Please check the data table below for details."


def process_chat_query(user_query: str) -> dict:
    """
    Process a chat query: Convert to SQL and execute on BigQuery
    Includes Natural Language Summary
    
    Args:
        user_query: Natural language query from user
        
    Returns:
        Dictionary with response data including natural language summary
    """
    if not llm_handler or not bq_handler:
        return {
            'success': False,
            'error': 'Handlers not initialized. Please check your configuration.'
        }
    
    try:
        # Step 1: Convert natural language to SQL with schema information
        logger.info(f"📝 Processing query: {user_query}")
        
        # Get schema information if schema_manager is available
        schema_info = None
        if schema_manager:
            schema_info = schema_manager.get_relevant_schemas(user_query)
        
        sql_result = llm_handler.natural_language_to_sql(user_query, schema_info=schema_info)
        
        if not sql_result['success']:
            return {
                'success': False,
                'error': sql_result.get('error', 'Failed to generate SQL'),
                'query': user_query
            }
        
        sql_query = sql_result['sql']
        logger.info(f"✅ Generated SQL: {sql_query[:100]}...")
        
        # Step 2: Execute SQL on BigQuery
        query_result = bq_handler.execute_query(sql_query)
        
        if not query_result['success']:
            return {
                'success': False,
                'error': query_result.get('error', 'Failed to execute query'),
                'sql': sql_query,
                'query': user_query
            }
        
        # Step 3: Generate Natural Language Summary
        logger.info("💬 Generating natural language summary...")
        natural_language_summary = generate_natural_language_summary(
            user_query=user_query,
            sql_query=sql_query,
            data=query_result['data'],
            row_count=query_result['row_count'],
            columns=query_result.get('columns', [])
        )
        
        # Step 4: Format response based on mode
        logger.info(f"✅ Returning {query_result['row_count']} rows with natural language summary")
        
        # Build base response with natural language summary (always included)
        response = {
            'success': True,
            'query': user_query,
            'summary': natural_language_summary,  # Natural language explanation (always included)
        }
        
        # ============================================================================
        # MODE 1: Full Response - Natural Language + SQL + Table
        # (Comment out this block for Mode 2 - Natural Language Only)
        # ============================================================================
        if RESPONSE_MODE == "full":
            response['sql'] = sql_query
            response['data'] = query_result['data']
            response['row_count'] = query_result['row_count']
            response['columns'] = query_result['columns']
        
        # ============================================================================
        # MODE 2: Natural Language Only
        # (Uncomment this block and comment out the block above for Mode 2)
        # ============================================================================
        # if RESPONSE_MODE == "natural_language_only":
        #     # No SQL or data included - only summary
        #     pass
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error processing query: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'query': user_query
        }


@app.get("/")
async def handle_query(query: str = Query(..., description="Natural language query")):
    """Handle chat queries from the widget"""
    try:
        if not query:
            raise HTTPException(status_code=400, detail="No query provided")
        
        logger.info(f"🔍 Received query: {query}")
        
        # Process the query
        result = process_chat_query(query)
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in request handler: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                'success': False,
                'error': str(e)
            }
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'ok',
        'mode': 'production',
        'handlers_ready': llm_handler is not None and bq_handler is not None,
        'api': 'FastAPI',
        'version': '1.0.0'
    }


if __name__ == '__main__':
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 BigQuery Chatbot - PRODUCTION API Server (FastAPI)")
    print("="*60)
    print("Mode: PRODUCTION (Vertex AI + BigQuery)")
    print("Server: http://localhost:8501")
    print("API Docs: http://localhost:8501/docs")
    print("="*60 + "\n")
    
    if llm_handler and bq_handler:
        print("✅ Handlers initialized successfully!")
        print("✅ Ready to process queries")
        print("✅ Natural language summaries enabled\n")
    else:
        print("❌ Error: Handlers not initialized")
        print("❌ Check your .env file and GCP credentials\n")
    
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Run the FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8501)
