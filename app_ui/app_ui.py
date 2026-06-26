import streamlit as st
import requests

# 1. Page Config
st.set_page_config(page_title="FinRAG Dashboard", layout="wide")
st.title("📊 FinRAG Financial Dashboard")

# 2. Session State for Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Sidebar for Configuration
with st.sidebar:
    st.header("Settings")
    category_id = st.text_input("Category ID", value="101")
    if st.button("Clear History"):
        st.session_state.messages = []

# 4. Allowing user to upload new pdf and send it to the backend
with st.sidebar:
    st.header("Data Management")
    uploaded_file = st.file_uploader("Upload a new PDF", type="pdf")
    if uploaded_file is not None:
        if st.button("Index Document"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            # Assuming your backend expects a categoryId as a form field
            data = {"categoryId": "101"} 
            response = requests.post("http://127.0.0.1:8000/update_vector", files=files, data=data)
            if response.status_code == 200:
                st.success(f"Successfully indexed {uploaded_file.name}")
            else:
                st.error("Failed to index file.")

# 5. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Chat Logic
if prompt := st.chat_input("Ask about financial reports..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call your FastAPI backend
    with st.chat_message("assistant"):
        payload = {
            "chatId": "ui-session",
            "ownerId": "default",
            "chatName": "Dashboard Chat",
            "initInputs": {"categoryIds": [category_id]},
            "initOpening": "",
            "chatMessages": [{"role": "user", "rawContent": prompt}]
        }
        
        try:
            # Pointing to your FastAPI server running on localhost:8000
            response = requests.post("http://127.0.0.1:8000/chat", json=payload)

            #raw_text = response.text

            #st.write("--- DEBUG INFO ---")
            #st.write(f"Status Code: {response.status_code}")
            #st.write(f"Raw Response Body: {raw_text}")
            #st.write(f"Is it a string? {isinstance(raw_text, str)}")

            #print(f"DEBUG: Status Code: {response.status_code}")
            #print(f"DEBUG: Response Content: {response.text}")
            #print(f"DEBUG: Type of response is {type(response.json())}")
            
            if response.status_code == 200:
                # Safely parse JSON
                full_json = response.json()
                
                # Check for success key from your ResponseFactory
                if full_json.get("success", False):
                    result = full_json.get("data", {})
                    answer = result.get("answer", "Error: No answer returned.")
                    chunks = result.get("chunks", [])
                    
                    st.markdown(answer)
                    
                    # Feature: Citations/Chunks Expander
                    if chunks:
                        with st.expander("View Source Citations"):
                            for item in chunks:
                                if isinstance(item, dict):
                                    st.write(f"**Source:** {item.get('index', 'N/A')} (Score: {item.get('score', 0):.2f})")
                                    st.text(item.get('chunk', ''))
                                else:
                                    st.text(item)
                                
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    # Backend-side error (e.g., Milvus released)
                    st.error(f"Backend Error: {full_json.get('message', 'Unknown error')}")
            
            else:
                # HTTP-side error (e.g., 500 Internal Server Error)
                st.error(f"Server returned status {response.status_code}: {response.text}")
                
        except Exception as e:
            # Catch network or parsing errors
            st.error(f"Frontend connection error: {e}")