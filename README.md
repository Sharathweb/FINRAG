FinRAG: Financial Retrieval Augmented Generation
1. Prerequisites & Setup
1.1 Install Miniconda
Download: Miniconda Linux Installers

Install Python 3.10.14:

Bash
wget https://repo.anaconda.com/miniconda/Miniconda3-py310_24.4.0-0-Linux-x86_64.sh
bash Miniconda3-py310_24.4.0-0-Linux-x86_64.sh
Configure Environment Variables:

Bash
export PATH=$HOME/miniconda3/bin:$PATH
1.2 Initialize Milvus Vector Database
Start Milvus using docker-compose:

Bash
cd docker
docker-compose up -d
Terminology: docker-compose ensures that services run as "daemons" (background processes) so they persist even after you close your terminal.

Milvus UI: Access the dashboard at http://{your_server_ip}:3100/.

1.3 Download Embedding & Rerank Models
Create the model directory: mkdir -p /data/WoLLM

Download the models:

Bash
git clone https://www.modelscope.cn/maidalun/bce-embedding-base_v1.git /data/WoLLM/bce-embedding-base_v1
git clone https://www.modelscope.cn/maidalun/bce-reranker-base_v1.git /data/WoLLM/bce-reranker-base_v1
Definitions:

Embedding Model: Converts text into fixed-dimension vectors for semantic search.

Rerank Model: Refines search results to improve the accuracy of retrieved context.

Update Configuration: Ensure EMBEDDING_MODEL and RERANK_MODEL paths in conf/config.py match your local directory paths.

1.4 Dependencies Setup
Create Virtual Environment: python -m venv .venv

Activate Environment: source .venv/bin/activate

Install Requirements: pip install -r requirements.txt

1.5 Configuration
Edit conf/config.py to match your specific environment settings. Each variable is commented for clarity.

Adjust docker/docker-compose.yml if you need to change ports or IP bindings.

1.6 Environment Variables
Important: Copy the environment template: cp .env_user .env

Configure your LLM and Object Storage (OSS) credentials inside the newly created .env file.

2. Launching the Application
2.1 Standard Start
Bash
python main.py
2.2 Production Start (Script-based)
Bash
bash bin/start.sh
To-Do List
[ ] RAG Optimization

[ ] Multi-level indexing

[ ] Multi-query expansion

[ ] Query rewriting/optimization

[ ] Advanced text parsing pipelines