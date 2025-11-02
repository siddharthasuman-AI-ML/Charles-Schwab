"""
BigQuery Handler for executing SQL queries and managing BigQuery operations
"""
from google.cloud import bigquery
from config import Config
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BigQueryHandler:
    """Handles BigQuery connections and query execution"""
    
    def __init__(self):
        """Initialize BigQuery client"""
        try:
            self.client = bigquery.Client(
                project=Config.GCP_PROJECT_ID,
                location=Config.BIGQUERY_LOCATION
            )
            logger.info("BigQuery Handler initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing BigQuery Handler: {str(e)}")
            raise
    
    def execute_query(self, sql_query: str) -> dict:
        """
        Execute a SQL query on BigQuery
        
        Args:
            sql_query: SQL query string to execute
            
        Returns:
            Dictionary with 'success', 'data', 'row_count', and optional 'error' keys
        """
        try:
            logger.info(f"Executing query: {sql_query[:100]}...")
            
            # Configure query job
            job_config = bigquery.QueryJobConfig(
                use_query_cache=True,
                use_legacy_sql=False
            )
            
            # Execute query
            query_job = self.client.query(sql_query, job_config=job_config)
            
            # Wait for query to complete and get results
            results = query_job.result()
            
            # Convert to pandas DataFrame for easy manipulation
            df = results.to_dataframe()
            
            # Convert DataFrame to list of dictionaries
            data = df.to_dict('records')
            
            # Get row count
            row_count = len(data)
            
            logger.info(f"Query executed successfully. Returned {row_count} rows.")
            
            return {
                'success': True,
                'data': data,
                'row_count': row_count,
                'columns': list(df.columns) if not df.empty else [],
                'query': sql_query
            }
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'query': sql_query
            }
    
    def get_dataset_tables(self, dataset_id: str = None) -> dict:
        """
        Get list of tables in a dataset
        
        Args:
            dataset_id: BigQuery dataset ID (uses Config default if not provided)
            
        Returns:
            Dictionary with 'success', 'tables', and optional 'error' keys
        """
        if not dataset_id:
            dataset_id = Config.GCP_DATASET_ID
        
        try:
            dataset_ref = f"{Config.GCP_PROJECT_ID}.{dataset_id}"
            tables = self.client.list_tables(dataset_ref)
            
            table_list = []
            for table in tables:
                table_list.append({
                    'table_id': table.table_id,
                    'table_type': table.table_type,
                    'full_table_id': f"{dataset_ref}.{table.table_id}"
                })
            
            logger.info(f"Found {len(table_list)} tables in dataset {dataset_id}")
            
            return {
                'success': True,
                'tables': table_list,
                'dataset_id': dataset_id
            }
            
        except Exception as e:
            logger.error(f"Error listing tables: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_table_schema(self, table_id: str, dataset_id: str = None) -> dict:
        """
        Get schema information for a specific table
        
        Args:
            table_id: Table ID
            dataset_id: BigQuery dataset ID (uses Config default if not provided)
            
        Returns:
            Dictionary with 'success', 'schema', and optional 'error' keys
        """
        if not dataset_id:
            dataset_id = Config.GCP_DATASET_ID
        
        try:
            table_ref = f"{Config.GCP_PROJECT_ID}.{dataset_id}.{table_id}"
            table = self.client.get_table(table_ref)
            
            schema_info = []
            for field in table.schema:
                schema_info.append({
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode,
                    'description': field.description or ''
                })
            
            logger.info(f"Retrieved schema for table {table_id}")
            
            return {
                'success': True,
                'schema': schema_info,
                'table_id': table_id,
                'num_rows': table.num_rows,
                'description': table.description or ''
            }
            
        except Exception as e:
            logger.error(f"Error getting table schema: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_query_syntax(self, sql_query: str) -> dict:
        """
        Validate SQL query syntax without executing it (dry run)
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            Dictionary with 'success' and optional 'error' keys
        """
        try:
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            query_job = self.client.query(sql_query, job_config=job_config)
            
            # If no exception, query is valid
            bytes_processed = query_job.total_bytes_processed
            
            logger.info(f"Query validation successful. Will process {bytes_processed} bytes.")
            
            return {
                'success': True,
                'bytes_processed': bytes_processed,
                'message': 'Query syntax is valid'
            }
            
        except Exception as e:
            logger.error(f"Query validation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def format_results_for_display(self, query_results: dict) -> str:
        """
        Format query results for display in chat
        
        Args:
            query_results: Results dictionary from execute_query
            
        Returns:
            Formatted string for display
        """
        if not query_results.get('success'):
            return f"Error: {query_results.get('error', 'Unknown error')}"
        
        data = query_results.get('data', [])
        row_count = query_results.get('row_count', 0)
        
        if row_count == 0:
            return "No results found."
        
        # Create a simple text table
        df = pd.DataFrame(data)
        return df.to_string(index=False, max_rows=10)
