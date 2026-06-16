"""
Custom PostgreSQL database backend with enhanced connection handling
Fixes "server didn't return client encoding" errors in serverless environments
"""

import logging
from django.db.backends.postgresql import base
from django.db.backends.postgresql.base import DatabaseWrapper as PostgreSQLDatabaseWrapper
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class DatabaseWrapper(PostgreSQLDatabaseWrapper):
    """
    Custom PostgreSQL database wrapper with enhanced connection handling
    """
    
    def get_connection_params(self):
        """
        Get connection parameters with enhanced error handling
        """
        params = super().get_connection_params()
        
        # Add specific parameters to handle encoding issues
        params.update({
            'client_encoding': 'UTF8',
            'connect_timeout': 60,
            'keepalives_idle': 600,
            'keepalives_interval': 30,
            'keepalives_count': 3,
            'application_name': 'fagiassets_vercel',
        })
        
        # Force SSL mode for Supabase
        if 'sslmode' not in params:
            params['sslmode'] = 'require'
        
        logger.info(f"Database connection parameters: {params}")
        return params
    
    def get_new_connection(self, conn_params):
        """
        Get new connection with enhanced error handling
        """
        try:
            # Try to establish connection
            connection = super().get_new_connection(conn_params)
            
            # Set client encoding explicitly
            with connection.cursor() as cursor:
                cursor.execute("SET client_encoding TO 'UTF8'")
                
            logger.info("Database connection established successfully")
            return connection
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            
            # If encoding error, try with different parameters
            if "didn't return client encoding" in str(e):
                logger.warning("Retrying connection with adjusted parameters...")
                
                # Remove problematic parameters and retry
                adjusted_params = conn_params.copy()
                adjusted_params.pop('client_encoding', None)
                adjusted_params.pop('keepalives_idle', None)
                adjusted_params.pop('keepalives_interval', None)
                adjusted_params.pop('keepalives_count', None)
                
                try:
                    connection = super().get_new_connection(adjusted_params)
                    
                    # Set encoding after connection
                    with connection.cursor() as cursor:
                        cursor.execute("SET client_encoding TO 'UTF8'")
                    
                    logger.info("Database connection established with adjusted parameters")
                    return connection
                    
                except Exception as retry_error:
                    logger.error(f"Retry connection also failed: {retry_error}")
                    raise
            
            # Re-raise original error if not encoding-related
            raise
    
    def init_connection_state(self):
        """
        Initialize connection state with enhanced error handling
        """
        try:
            super().init_connection_state()
            
            # Additional connection initialization
            with self.connection.cursor() as cursor:
                cursor.execute("SET timezone TO 'UTC'")
                cursor.execute("SET client_encoding TO 'UTF8'")
                
        except Exception as e:
            logger.warning(f"Connection state initialization partially failed: {e}")
            # Don't fail completely, just log the warning