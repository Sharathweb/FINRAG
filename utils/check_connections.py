from pymilvus import connections

try:
    # Connect to your Milvus instance
    connections.connect("default", host="localhost", port="19530")
    
    # Retrieve connection info to verify
    addr = connections.get_connection_addr("default")
    print(f"Connection established successfully to: {addr}")
except Exception as e:
    print(f"Failed to connect: {e}")