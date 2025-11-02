"""
BigQuery Handler MOCK VERSION for demo/testing
Returns sample data instead of executing real BigQuery queries
"""
from config import Config
import logging
import pandas as pd
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BigQueryHandler:
    """Mock BigQuery Handler - Returns sample data for demo"""
    
    def __init__(self):
        """Initialize Mock BigQuery Handler"""
        logger.info("🎬 Mock BigQuery Handler initialized (DEMO MODE)")
        logger.info("Note: This will return DEMO DATA, not real BigQuery results")
    
    def execute_query(self, sql_query: str) -> dict:
        """
        Mock execute - Returns sample data instead of querying BigQuery
        
        Args:
            sql_query: SQL query string (for display purposes only)
            
        Returns:
            Dictionary with 'success', 'data', 'row_count', and optional 'error' keys
        """
        try:
            logger.info(f"🎬 Mock executing query: {sql_query[:100]}...")
            
            # Generate sample data based on query type
            data = self._generate_sample_data(sql_query)
            
            # Apply WHERE clause filtering if present
            data = self._apply_where_clause(sql_query, data)
            
            # Get row count
            row_count = len(data)
            
            # Get column names
            columns = list(data[0].keys()) if data else []
            
            logger.info(f"✅ Mock query executed. Returned {row_count} sample rows.")
            logger.warning("⚠️ This is DEMO DATA for demonstration. Not real BigQuery results!")
            
            return {
                'success': True,
                'data': data,
                'row_count': row_count,
                'columns': columns,
                'query': sql_query,
                'demo_data': True  # Flag to indicate this is demo data
            }
            
        except Exception as e:
            logger.error(f"❌ Error in mock query execution: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'query': sql_query
            }
    
    def _apply_where_clause(self, sql_query: str, data: list) -> list:
        """
        Parse WHERE clause from SQL and filter data accordingly
        
        Args:
            sql_query: SQL query string
            data: Sample data to filter
            
        Returns:
            Filtered data list
        """
        if not data:
            return data
        
        sql_upper = sql_query.upper()
        
        # Check if WHERE clause exists
        if 'WHERE' not in sql_upper:
            return data
        
        # Extract WHERE clause
        where_match = re.search(r'WHERE\s+(.+?)(?:\s+ORDER\s+BY|\s+LIMIT|$)', sql_query, re.IGNORECASE | re.DOTALL)
        if not where_match:
            return data
        
        where_clause = where_match.group(1).strip()
        logger.info(f"🔍 Parsing WHERE clause: {where_clause[:100]}...")
        
        # Parse common WHERE patterns
        # Pattern 1: LOWER(customer_name) LIKE '%john%' or customer_name LIKE '%john%'
        name_like_pattern = r"(?:LOWER\()?(\w+(?:_name|_id))?\)?\s+(?:LIKE|like)\s+['\"]?%([^%]+)%['\"]?"
        name_match = re.search(name_like_pattern, where_clause, re.IGNORECASE)
        if name_match:
            column_name = name_match.group(1) if name_match.group(1) else 'customer_name'
            search_term = name_match.group(2).lower()
            logger.info(f"🔍 Filtering by {column_name} containing '{search_term}'")
            
            filtered_data = []
            for row in data:
                # Try to find the column (case-insensitive)
                row_value = None
                for key in row.keys():
                    if key.lower() == column_name.lower():
                        row_value = str(row[key]).lower() if row[key] else ''
                        break
                
                if row_value and search_term in row_value:
                    filtered_data.append(row)
            
            return filtered_data if filtered_data else data
        
        # Pattern 2: customer_name = 'John Doe'
        name_eq_pattern = r"(\w+(?:_name|_id))?\s*=\s*['\"]?([^'\"]+)['\"]?"
        name_eq_match = re.search(name_eq_pattern, where_clause, re.IGNORECASE)
        if name_eq_match:
            column_name = name_eq_match.group(1) if name_eq_match.group(1) else 'customer_name'
            search_term = name_eq_match.group(2).strip().lower()
            logger.info(f"🔍 Filtering by {column_name} = '{search_term}'")
            
            filtered_data = []
            for row in data:
                row_value = None
                for key in row.keys():
                    if key.lower() == column_name.lower():
                        row_value = str(row[key]).lower() if row[key] else ''
                        break
                
                if row_value == search_term:
                    filtered_data.append(row)
            
            return filtered_data if filtered_data else data
        
        # If no pattern matched, return original data
        return data
    
    def _generate_sample_data(self, sql_query: str) -> list:
        """
        Generate sample data based on the query
        
        Args:
            sql_query: SQL query to analyze
            
        Returns:
            List of sample data dictionaries
        """
        sql_upper = sql_query.upper()
        
        # Customer data (base dataset with names, emails, revenue)
        customer_data = [
            {
                'customer_id': 1,
                'customer_name': 'John Doe',
                'email': 'john@example.com',
                'revenue': 5000.50,
                'created_at': '2024-01-15'
            },
            {
                'customer_id': 2,
                'customer_name': 'Jane Smith',
                'email': 'jane@example.com',
                'revenue': 7500.25,
                'created_at': '2024-02-20'
            },
            {
                'customer_id': 3,
                'customer_name': 'Bob Johnson',
                'email': 'bob@example.com',
                'revenue': 3200.00,
                'created_at': '2024-03-10'
            },
            {
                'customer_id': 4,
                'customer_name': 'Alice Brown',
                'email': 'alice@example.com',
                'revenue': 9100.75,
                'created_at': '2024-04-05'
            },
            {
                'customer_id': 5,
                'customer_name': 'Charlie Wilson',
                'email': 'charlie@example.com',
                'revenue': 6300.30,
                'created_at': '2024-05-12'
            }
        ]
        
        # Check query type and return appropriate sample data
        if 'COUNT' in sql_upper:
            return [{'count': 150, 'total': 150}]
        
        # Tables that should return customer data: CUSTOMER, USER, REVENUE, SALES (if revenue mentioned)
        elif any(keyword in sql_upper for keyword in ['CUSTOMER', 'USER', 'REVENUE']) or \
             ('SALES' in sql_upper and 'REVENUE' in sql_upper):
            return customer_data
        
        elif 'ORDER' in sql_upper:
            return [
                {
                    'order_id': 101,
                    'customer_id': 1,
                    'order_date': '2024-10-15',
                    'total_amount': 250.00,
                    'status': 'Completed'
                },
                {
                    'order_id': 102,
                    'customer_id': 2,
                    'order_date': '2024-10-20',
                    'total_amount': 450.75,
                    'status': 'Processing'
                },
                {
                    'order_id': 103,
                    'customer_id': 3,
                    'order_date': '2024-10-25',
                    'total_amount': 320.50,
                    'status': 'Shipped'
                }
            ]
        
        elif 'PRODUCT' in sql_upper:
            return [
                {
                    'product_id': 1,
                    'product_name': 'Widget A',
                    'category': 'Electronics',
                    'price': 99.99,
                    'stock': 150
                },
                {
                    'product_id': 2,
                    'product_name': 'Gadget B',
                    'category': 'Electronics',
                    'price': 149.99,
                    'stock': 75
                },
                {
                    'product_id': 3,
                    'product_name': 'Tool C',
                    'category': 'Hardware',
                    'price': 49.99,
                    'stock': 200
                }
            ]
        
        elif 'SALES' in sql_upper:
            # Sales table - return customer data with revenue (same as customer table)
            return customer_data
        
        else:
            # If query mentions email, name, or person-related terms, return customer data
            if any(term in sql_upper for term in ['EMAIL', 'NAME', 'PERSON']):
                return customer_data
            
            # Generic sample data
            return [
                {
                    'id': 1,
                    'name': 'Sample Record 1',
                    'value': 100,
                    'date': '2024-01-01'
                },
                {
                    'id': 2,
                    'name': 'Sample Record 2',
                    'value': 200,
                    'date': '2024-01-02'
                },
                {
                    'id': 3,
                    'name': 'Sample Record 3',
                    'value': 300,
                    'date': '2024-01-03'
                }
            ]
    
    def get_dataset_tables(self, dataset_id: str = None) -> dict:
        """Mock get tables - Returns sample table list"""
        return {
            'success': True,
            'tables': [
                {'table_id': 'customers', 'table_type': 'TABLE'},
                {'table_id': 'orders', 'table_type': 'TABLE'},
                {'table_id': 'products', 'table_type': 'TABLE'}
            ],
            'dataset_id': dataset_id or Config.GCP_DATASET_ID,
            'demo_data': True
        }
    
    def get_table_schema(self, table_id: str, dataset_id: str = None) -> dict:
        """Mock get schema - Returns sample schema"""
        return {
            'success': True,
            'schema': [
                {'name': 'id', 'type': 'INTEGER', 'mode': 'REQUIRED'},
                {'name': 'name', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'value', 'type': 'FLOAT', 'mode': 'NULLABLE'},
            ],
            'table_id': table_id,
            'num_rows': 1000,
            'demo_data': True
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






