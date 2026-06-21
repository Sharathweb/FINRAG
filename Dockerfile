# Use a slim Python 3.10 base image
FROM python:3.10-slim

# Environment settings
# Set language and timezone to UTC for consistent server behavior
ENV LANG=C.UTF-8
ENV TZ=UTC

# Set the working directory
WORKDIR /FinRAG

# Copy application code to the container
COPY . /FinRAG

# Install dependencies
# Using Aliyun mirror for faster downloads within China
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

# Expose the API port
EXPOSE 8000

# Set the entry point script
# Ensure /bin/start.sh has execute permissions before building
CMD ["/bin/bash", "/bin/start.sh"]