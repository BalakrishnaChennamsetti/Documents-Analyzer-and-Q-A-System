import streamlit as st
import requests

INGEST_URL = "http://localhost:8001/ingest"
QUERY_URL = "http://localhost:8002/query"

st.title("Multi-File Ingestion & Q&A System")

# Upload file
uploaded_file = st.file_uploader("Upload a file (CSV / PDF / TXT)", type=["csv", "pdf", "txt"])

# Only set uploaded file if not already in session_state
if uploaded_file and "uploaded" not in st.session_state:
    st.session_state.uploaded = uploaded_file
    st.session_state.ingested = False  # flag to check if ingestion is done

# Ingest the file only once
if "uploaded" in st.session_state and not st.session_state.get("ingested", False):
    st.success("File uploaded. Sending to ingestion service...")
    files = {"file": (st.session_state.uploaded.name, st.session_state.uploaded.getvalue())}
    try:
        res = requests.post(INGEST_URL, files=files)
        if res.status_code == 200:
            st.success("File successfully ingested into VectorDB!")
            st.session_state.ingested = True  # mark as ingested
        else:
            st.error(f"Error: {res.text}")
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to ingestion backend. Make sure it's running on port 8001.")

# Ask query
user_query = st.text_input("Ask something about the ingested file")
if st.button("Ask Query"):
    if not user_query:
        st.warning("Enter a question.")
    else:
        payload = {"query": user_query}
        try:
            st.info(f"Sending query: {user_query}")
            res = requests.post(QUERY_URL, json=payload)
            if res.status_code == 200:
                st.write("### Answer:")
                st.write(res.json().get("answer", "No answer returned"))
            else:
                st.error(f"Error: {res.text}")
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to RAG backend. Make sure it's running on port 8002.")
