# Use a slim Python 3.10 base image
FROM python:3.10-slim

# Set working directory
WORKDIR /FinRAG

# Copy your requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

# Copy the entire project to the container
COPY . .

# Grant execute permissions to the script in the bin folder
RUN chmod +x /FinRAG/bin/start.sh

# Set the entry point to run the script
CMD ["/bin/bash", "/FinRAG/bin/start.sh"]