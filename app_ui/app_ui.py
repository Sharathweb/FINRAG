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
            if response.status_code == 422:
                st.error("422 Error: " + str(response.json()))
            result = response.json().get("data", {})
            answer = result.get("answer", "Error: No answer returned.")
            chunks = result.get("chunks", [])
            
            st.markdown(answer)
            
            # Feature: Citations/Chunks Expander
            if chunks:
                with st.expander("View Source Citations"):
                    for chunk in chunks:
                        st.write(f"**Source:** {chunk['index']} (Score: {chunk['score']:.2f})")
                        st.text(chunk['chunk'])
                        
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")