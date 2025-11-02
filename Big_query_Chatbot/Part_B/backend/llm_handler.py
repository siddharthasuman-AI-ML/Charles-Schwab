"""
LLM Handler for Natural Language to SQL translation using Vertex AI Gemini
Schema-Agnostic Version - Uses dynamic schema discovery
"""
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from config import Config
import logging
import re
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMHandler:
    """Handles Natural Language to SQL conversion using Vertex AI Gemini"""
    
    def __init__(self, schema_manager=None):
        """
        Initialize Vertex AI and Gemini model
        
        Args:
            schema_manager: Optional SchemaManager instance for schema-aware SQL generation
        """
        try:
            # Initialize Vertex AI
            vertexai.init(
                project=Config.GCP_PROJECT_ID,
                location=Config.VERTEX_AI_LOCATION
            )
            
            # Initialize Gemini model
            self.model = GenerativeModel(Config.VERTEX_AI_MODEL)
            
            # Generation configuration for more controlled outputs
            self.generation_config = GenerationConfig(
                temperature=0.2,  # Lower temperature for more deterministic SQL
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            )
            
            # Store schema manager for dynamic schema access
            self.schema_manager = schema_manager
            
            logger.info("LLM Handler initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing LLM Handler: {str(e)}")
            raise
    
    def create_sql_prompt(self, user_query: str, dataset_id: str, 
                         schema_info: Optional[str] = None) -> str:
        """
        Create a detailed prompt for SQL generation with actual schema information
        
        Args:
            user_query: Natural language query from user
            dataset_id: BigQuery dataset ID
            schema_info: Schema information from SchemaManager (will be fetched if not provided)
            
        Returns:
            Formatted prompt string
        """
        # Get schema information from schema_manager if available and not provided
        if not schema_info and self.schema_manager:
            schema_info = self.schema_manager.get_relevant_schemas(user_query)
        
        # Fallback to full schema if available
        if not schema_info and self.schema_manager:
            schema_info = self.schema_manager.get_schema_summary()
        
        prompt = f"""You are a BigQuery SQL expert. Convert the following natural language query into a valid BigQuery SQL query.

Dataset ID: {dataset_id}
Project ID: {Config.GCP_PROJECT_ID}

"""
        
        # Add schema information if available
        if schema_info:
            prompt += f"""Available Tables and Columns:
{schema_info}

"""
        else:
            prompt += """Note: No schema information available. You must use table and column names mentioned in the user query or make reasonable assumptions based on the query context.

"""
        
        prompt += f"""User Query: {user_query}

CRITICAL REQUIREMENTS:
1. Generate ONLY the SQL query, no explanations or markdown formatting
2. Use fully qualified table names: `{Config.GCP_PROJECT_ID}.{dataset_id}.table_name`
3. TABLE SELECTION:
   - Analyze the available tables and columns listed above
   - Select the most appropriate table(s) based on the user query
   - Use actual table names from the schema (do not assume table names)
   - If multiple tables exist, choose the one most relevant to the query
4. COLUMN SELECTION:
   - SELECT ALL COLUMNS that are needed to answer the user's question
   - If user asks about a specific field (e.g., "email", "name", "revenue"), you MUST include that column in SELECT
   - Use actual column names from the schema provided above (check spelling and case)
   - When in doubt, SELECT * or include all potentially relevant columns
   - Ensure requested fields are included in the SELECT clause
5. WHERE CLAUSES:
   - Include appropriate WHERE clauses when names, IDs, or specific values are mentioned
   - Use LOWER(column_name) LIKE '%value%' for case-insensitive text matching
   - Match against actual column names from the schema
6. Include LIMIT {Config.MAX_RESULTS} to limit results
7. ORDER BY:
   - Include ORDER BY for queries asking for highest/lowest/top/bottom
   - Use actual column names from the schema
   - DESC for highest/top, ASC for lowest/bottom
8. Ensure the query is safe (no DELETE, DROP, TRUNCATE, ALTER, CREATE, INSERT, UPDATE)
9. Use standard SQL syntax compatible with BigQuery

IMPORTANT: 
- Always use the ACTUAL table and column names from the schema provided above
- Do not assume table or column names that are not in the schema
- SELECT columns that are explicitly requested or needed to answer the question
- Verify column names match exactly (case-sensitive)

"""
        
        prompt += "\nSQL Query:"
        
        return prompt
    
    def natural_language_to_sql(self, user_query: str, dataset_id: str = None, 
                                schema_info: Optional[str] = None) -> dict:
        """
        Convert natural language query to SQL using Gemini with schema-aware generation
        
        Args:
            user_query: Natural language query from user
            dataset_id: BigQuery dataset ID (uses Config default if not provided)
            schema_info: Optional schema information (will use schema_manager if available)
            
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
            
            # Create prompt with schema information
            prompt = self.create_sql_prompt(user_query, dataset_id, schema_info)
            
            logger.info(f"Generating SQL for query: {user_query[:100]}...")
            
            # Generate SQL using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
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
            
            logger.info(f"Generated SQL: {sql_query[:100]}...")
            
            return {
                'success': True,
                'sql': sql_query,
                'original_query': user_query
            }
            
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
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
                logger.warning(f"Forbidden keyword '{keyword}' found in SQL query")
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
