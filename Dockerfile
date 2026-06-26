FROM python:3.10-slim

WORKDIR /FinRAG

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

# Copy application
COPY . .

# Simply run your application entry point directly
# No need for bin/start.sh or Docker-based database orchestration
CMD ["python", "main.py"]