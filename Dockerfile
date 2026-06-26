FROM python:3.11-slim

WORKDIR /FinRAG

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

# Copy application
COPY . .

RUN chmod +x start.sh

# Simply run your application entry point directly
# No need for bin/start.sh or Docker-based database orchestration
CMD ["./start.sh"]