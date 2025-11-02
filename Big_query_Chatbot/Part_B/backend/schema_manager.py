"""
Schema Manager for BigQuery Chatbot - Production Version
Handles schema discovery, caching, and intelligent schema retrieval
"""
from bigquery_handler import BigQueryHandler
from config import Config
import logging
from typing import Dict, List, Optional, Set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages BigQuery schema discovery, caching, and retrieval"""
    
    def __init__(self, bq_handler: BigQueryHandler):
        """
        Initialize SchemaManager with BigQuery handler
        
        Args:
            bq_handler: BigQueryHandler instance for executing queries
        """
        self.bq_handler = bq_handler
        self.dataset_id = Config.GCP_DATASET_ID
        self.project_id = Config.GCP_PROJECT_ID
        
        # Cache for discovered schemas
        # Structure: {table_id: {'schema': [...], 'num_rows': int, 'description': str}}
        self._schema_cache: Dict[str, Dict] = {}
        self._tables_list: List[Dict] = []
        
        logger.info("SchemaManager initialized")
    
    def discover_all_tables(self) -> bool:
        """
        Discover all tables in the dataset and cache their schemas
        
        Returns:
            True if discovery successful, False otherwise
        """
        try:
            logger.info(f"Discovering tables in dataset: {self.dataset_id}")
            
            # Get list of tables
            tables_result = self.bq_handler.get_dataset_tables(self.dataset_id)
            
            if not tables_result.get('success'):
                error = tables_result.get('error', 'Unknown error')
                logger.error(f"Failed to discover tables: {error}")
                return False
            
            self._tables_list = tables_result.get('tables', [])
            logger.info(f"Found {len(self._tables_list)} tables")
            
            # Cache schema for each table
            for table_info in self._tables_list:
                table_id = table_info['table_id']
                try:
                    schema_result = self.bq_handler.get_table_schema(table_id, self.dataset_id)
                    
                    if schema_result.get('success'):
                        self._schema_cache[table_id] = {
                            'schema': schema_result.get('schema', []),
                            'num_rows': schema_result.get('num_rows', 0),
                            'description': schema_result.get('description', ''),
                            'full_table_id': table_info['full_table_id']
                        }
                        logger.info(f"Cached schema for table: {table_id} ({len(schema_result.get('schema', []))} columns)")
                    else:
                        logger.warning(f"Failed to get schema for table {table_id}: {schema_result.get('error')}")
                
                except Exception as e:
                    logger.warning(f"Error caching schema for table {table_id}: {str(e)}")
            
            logger.info(f"✅ Schema discovery completed. Cached {len(self._schema_cache)} table schemas")
            return True
            
        except Exception as e:
            logger.error(f"Error during schema discovery: {str(e)}")
            return False
    
    def get_table_schema(self, table_id: str) -> Optional[Dict]:
        """
        Get cached schema for a specific table
        
        Args:
            table_id: Table ID to get schema for
            
        Returns:
            Schema dictionary or None if not found
        """
        return self._schema_cache.get(table_id)
    
    def get_schema_summary(self) -> str:
        """
        Get a formatted summary of all schemas for LLM prompt generation
        
        Returns:
            Formatted string with all table schemas
        """
        if not self._schema_cache:
            return "No schemas discovered yet. Please ensure schema discovery has been completed."
        
        summary_lines = []
        summary_lines.append(f"Dataset: {self.project_id}.{self.dataset_id}\n")
        summary_lines.append(f"Total Tables: {len(self._schema_cache)}\n")
        summary_lines.append("=" * 80 + "\n")
        
        for table_id, table_info in self._schema_cache.items():
            schema = table_info.get('schema', [])
            num_rows = table_info.get('num_rows', 0)
            description = table_info.get('description', '')
            
            summary_lines.append(f"\nTable: {table_id}")
            if description:
                summary_lines.append(f"Description: {description}")
            summary_lines.append(f"Rows: {num_rows:,}" if num_rows else "Rows: Unknown")
            summary_lines.append(f"Columns ({len(schema)}):")
            
            for col in schema:
                col_name = col.get('name', '')
                col_type = col.get('type', '')
                col_mode = col.get('mode', '')
                col_desc = col.get('description', '')
                
                mode_str = f" ({col_mode})" if col_mode == 'REPEATED' else ""
                desc_str = f" - {col_desc}" if col_desc else ""
                summary_lines.append(f"  - {col_name}: {col_type}{mode_str}{desc_str}")
            
            summary_lines.append("")
        
        return "\n".join(summary_lines)
    
    def get_relevant_schemas(self, user_query: str) -> str:
        """
        Get schemas for tables relevant to the user query based on keyword matching
        
        Args:
            user_query: User's natural language query
            
        Returns:
            Formatted string with relevant table schemas
        """
        if not self._schema_cache:
            return self.get_schema_summary()
        
        query_lower = user_query.lower()
        
        # Keywords that might indicate table relevance
        # We'll match against table names and column names
        relevant_tables = []
        
        for table_id, table_info in self._schema_cache.items():
            # Check if table name matches query
            if table_id.lower() in query_lower:
                relevant_tables.append(table_id)
                continue
            
            # Check if any column names match query
            schema = table_info.get('schema', [])
            for col in schema:
                col_name = col.get('name', '').lower()
                # Check for keyword matches (email, name, id, date, revenue, etc.)
                if any(keyword in query_lower and keyword in col_name for keyword in 
                       ['email', 'name', 'id', 'date', 'revenue', 'amount', 'total', 'customer', 'user', 'order']):
                    relevant_tables.append(table_id)
                    break
        
        # If no specific matches, return all schemas (let LLM decide)
        if not relevant_tables:
            return self.get_schema_summary()
        
        # Return only relevant schemas
        summary_lines = []
        summary_lines.append(f"Dataset: {self.project_id}.{self.dataset_id}\n")
        summary_lines.append(f"Relevant Tables: {', '.join(relevant_tables)}\n")
        summary_lines.append("=" * 80 + "\n")
        
        for table_id in relevant_tables:
            table_info = self._schema_cache.get(table_id)
            if not table_info:
                continue
            
            schema = table_info.get('schema', [])
            num_rows = table_info.get('num_rows', 0)
            description = table_info.get('description', '')
            
            summary_lines.append(f"\nTable: {table_id}")
            if description:
                summary_lines.append(f"Description: {description}")
            summary_lines.append(f"Rows: {num_rows:,}" if num_rows else "Rows: Unknown")
            summary_lines.append(f"Columns ({len(schema)}):")
            
            for col in schema:
                col_name = col.get('name', '')
                col_type = col.get('type', '')
                col_mode = col.get('mode', '')
                col_desc = col.get('description', '')
                
                mode_str = f" ({col_mode})" if col_mode == 'REPEATED' else ""
                desc_str = f" - {col_desc}" if col_desc else ""
                summary_lines.append(f"  - {col_name}: {col_type}{mode_str}{desc_str}")
            
            summary_lines.append("")
        
        return "\n".join(summary_lines)
    
    def find_columns_by_hint(self, hint: str) -> List[Dict]:
        """
        Find columns across all tables that match a semantic hint
        
        Args:
            hint: Semantic hint (e.g., 'email', 'name', 'id', 'date', 'revenue')
            
        Returns:
            List of column dictionaries with table info
        """
        hint_lower = hint.lower()
        matching_columns = []
        
        # Common patterns for different hints
        patterns = {
            'email': ['email', 'mail', 'e_mail'],
            'name': ['name', 'title', 'label'],
            'id': ['id', 'identifier', '_id'],
            'date': ['date', 'time', 'timestamp', 'created', 'updated'],
            'revenue': ['revenue', 'amount', 'total', 'price', 'cost', 'value']
        }
        
        # Find matching pattern
        search_patterns = [hint_lower]
        for key, patterns_list in patterns.items():
            if key in hint_lower:
                search_patterns.extend(patterns_list)
        
        for table_id, table_info in self._schema_cache.items():
            schema = table_info.get('schema', [])
            for col in schema:
                col_name = col.get('name', '').lower()
                
                # Check if column name matches any pattern
                for pattern in search_patterns:
                    if pattern in col_name:
                        matching_columns.append({
                            'table_id': table_id,
                            'column_name': col.get('name'),
                            'column_type': col.get('type'),
                            'full_table_id': table_info.get('full_table_id')
                        })
                        break
        
        return matching_columns
    
    def refresh_cache(self) -> bool:
        """
        Force refresh of schema cache
        
        Returns:
            True if refresh successful, False otherwise
        """
        self._schema_cache.clear()
        self._tables_list.clear()
        return self.discover_all_tables()
    
    def get_all_table_ids(self) -> List[str]:
        """
        Get list of all discovered table IDs
        
        Returns:
            List of table ID strings
        """
        return list(self._schema_cache.keys())
    
    def get_table_column_names(self, table_id: str) -> List[str]:
        """
        Get list of column names for a specific table
        
        Args:
            table_id: Table ID
            
        Returns:
            List of column name strings
        """
        table_info = self._schema_cache.get(table_id)
        if not table_info:
            return []
        
        schema = table_info.get('schema', [])
        return [col.get('name') for col in schema if col.get('name')]

