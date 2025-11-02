"""
LLM Handler for Natural Language to SQL translation using Gemini API
DEMO VERSION - Uses google.generativeai instead of Vertex AI
"""
import google.generativeai as genai
from config import Config
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMHandler:
    """Handles Natural Language to SQL conversion using Gemini API (for demo)"""
    
    def __init__(self):
        """Initialize Gemini API"""
        try:
            # Configure Gemini API with your API key
            genai.configure(api_key=Config.GEMINI_API_KEY)
            
            # Initialize Gemini model
            # Using gemini-flash-latest (latest stable flash model)
            self.model = genai.GenerativeModel('gemini-flash-latest')
            logger.info("✅ Using model: gemini-flash-latest")
            
            logger.info("✅ Gemini API Handler initialized successfully (DEMO MODE)")
            logger.info("Note: This is DEMO MODE - using Gemini API, not Vertex AI")
            
        except Exception as e:
            logger.error(f"Error initializing Gemini API Handler: {str(e)}")
            raise
    
    def create_sql_prompt(self, user_query: str, dataset_id: str, table_schema: str = None) -> str:
        """
        Create a detailed prompt for SQL generation
        
        Args:
            user_query: Natural language query from user
            dataset_id: BigQuery dataset ID
            table_schema: Optional table schema information
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a BigQuery SQL expert. Convert the following natural language query into a valid BigQuery SQL query.

Dataset ID: {dataset_id}
Project ID: {Config.GCP_PROJECT_ID}

Available Tables:
- customers: Contains customer_id, customer_name, email, revenue, created_at
- orders: Contains order_id, customer_id, order_date, total_amount, status
- products: Contains product_id, product_name, category, price, stock

User Query: {user_query}

CRITICAL REQUIREMENTS:
1. Generate ONLY the SQL query, no explanations or markdown formatting
2. Use fully qualified table names: `{Config.GCP_PROJECT_ID}.{dataset_id}.table_name`
3. TABLE SELECTION GUIDELINES:
   - For queries about person names, emails, customers, or revenue: Use 'customers' table
   - For queries about orders or transactions: Use 'orders' table
   - For queries about products: Use 'products' table
   - Revenue is stored in the 'customers' table (not a separate 'sales' or 'revenue' table)
   - Use 'customers' table when query mentions email, person name, customer name, or revenue
4. SELECT ALL COLUMNS that might be relevant to answer the user's question:
   - If user asks about email, INCLUDE email column in SELECT
   - If user asks about a person's name, INCLUDE customer_name or name column in SELECT
   - If user asks about revenue, INCLUDE revenue column in SELECT (from customers table)
   - When in doubt, SELECT * or include commonly needed columns (customer_name, email, revenue, etc.)
5. Include appropriate WHERE clauses based on names/identifiers mentioned in the query:
   - Use LOWER(customer_name) LIKE '%name%' for case-insensitive name matching
   - Example: WHERE LOWER(customer_name) LIKE '%john%' for "john"
6. Include LIMIT {Config.MAX_RESULTS} to limit results
7. Include ORDER BY if query asks for highest/lowest/top:
   - ORDER BY revenue DESC for highest revenue queries
8. Ensure the query is safe (no DELETE, DROP, TRUNCATE)
9. Use standard SQL syntax compatible with BigQuery

IMPORTANT: 
- Always SELECT columns that are needed to answer the question!
- Use 'customers' table for person/email/revenue queries, NOT 'users' or 'sales' tables!

"""
        
        if table_schema:
            prompt += f"\nAvailable Table Schema:\n{table_schema}\n"
        
        prompt += "\nSQL Query:"
        
        return prompt
    
    def natural_language_to_sql(self, user_query: str, dataset_id: str = None, 
                                table_schema: str = None) -> dict:
        """
        Convert natural language query to SQL using Gemini API
        
        Args:
            user_query: Natural language query from user
            dataset_id: BigQuery dataset ID (uses Config default if not provided)
            table_schema: Optional table schema information
            
        Returns:
            Dictionary with 'sql', 'success', and optional 'error' keys
        """
        if not dataset_id:
            dataset_id = Config.GCP_DATASET_ID
        
        try:
            # Validate query length
            if len(user_query) > Config.MAX_QUERY_LENGTH:
                return {
                    'success': False,
                    'error': f'Query too long. Maximum length is {Config.MAX_QUERY_LENGTH} characters.'
                }
            
            # Create prompt
            prompt = self.create_sql_prompt(user_query, dataset_id, table_schema)
            
            logger.info(f"🔍 Generating SQL for query: {user_query[:100]}...")
            
            # Generate SQL using Gemini
            response = self.model.generate_content(prompt)
            
            # Extract SQL from response
            sql_query = response.text.strip()
            
            # Clean up the SQL (remove markdown code blocks if present)
            sql_query = self._clean_sql_response(sql_query)
            
            # Basic SQL validation
            if not self._validate_sql(sql_query):
                return {
                    'success': False,
                    'error': 'Generated SQL contains potentially unsafe operations.'
                }
            
            logger.info(f"✅ Generated SQL: {sql_query[:100]}...")
            
            return {
                'success': True,
                'sql': sql_query,
                'original_query': user_query
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating SQL: {str(e)}")
            return {
                'success': False,
                'error': f'Error generating SQL: {str(e)}'
            }
    
    def _clean_sql_response(self, sql_text: str) -> str:
        """Clean up SQL response by removing markdown formatting"""
        # Remove markdown code blocks
        sql_text = sql_text.replace('```sql', '').replace('```', '').strip()
        
        # Remove any leading/trailing whitespace
        sql_text = sql_text.strip()
        
        return sql_text
    
    def _validate_sql(self, sql_query: str) -> bool:
        """
        Basic validation to ensure SQL doesn't contain destructive operations
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            True if query is safe, False otherwise
        """
        sql_upper = sql_query.upper()
        
        # List of forbidden operations
        forbidden_keywords = [
            'DELETE', 'DROP', 'TRUNCATE', 'ALTER', 'CREATE',
            'INSERT', 'UPDATE', 'GRANT', 'REVOKE'
        ]
        
        for keyword in forbidden_keywords:
            # Use word boundaries to match whole words only (not substrings like "creation" containing "create")
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, sql_upper):
                logger.warning(f"⚠️ Forbidden keyword '{keyword}' found in SQL query")
                return False
        
        return True
    
    def get_table_schema_description(self, table_info: list) -> str:
        """
        Format table schema information for the prompt
        
        Args:
            table_info: List of table information dictionaries
            
        Returns:
            Formatted schema description
        """
        if not table_info:
            return "No schema information available"
        
        schema_text = "Available Tables:\n"
        for table in table_info:
            schema_text += f"- {table.get('table_name', 'unknown')}: "
            schema_text += f"{table.get('description', 'No description')}\n"
            if 'columns' in table:
                schema_text += "  Columns: " + ", ".join(table['columns']) + "\n"
        
        return schema_text






