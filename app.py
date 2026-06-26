import os
import subprocess

# Launch Streamlit
if __name__ == "__main__":
    subprocess.run(["streamlit", "run", "app_ui/app_ui.py", "--server.port", "7860"])