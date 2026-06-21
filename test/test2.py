"""
Description: Utility script to verify the connection to the Milvus vector database.
"""

import logging
from pymilvus import connections, utility

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def verify_milvus_connection(alias: str = "default", host: str = "localhost", port: str = "19530"):
    """
    Establishes and verifies a connection to the Milvus server.
    """
    try:
        # Establish connection
        connections.connect(alias=alias, host=host, port=port)
        
        # Verify connection status
        connection_info = utility.get_connection_addr(alias=alias)
        logger.info(f"Successfully connected to Milvus server at: {connection_info}")
        
        # Check if the connection is active
        if utility.get_connection_addr(alias=alias):
            logger.info("Milvus server is responsive.")
            
    except Exception as e:
        logger.error(f"Failed to connect to Milvus: {e}")

if __name__ == "__main__":
    verify_milvus_connection()