python main.py --host 0.0.0.0 --port 8000 &
streamlit run app_ui/app_ui.py --server.port $PORT --server.address 0.0.0.0
