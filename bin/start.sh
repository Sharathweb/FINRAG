#!/bin/bash
cd "$(dirname "$0")/.."
python main.py &
sleep 5
streamlit run app_ui/app_ui.py --server.port $PORT --server.address 0.0.0.0
