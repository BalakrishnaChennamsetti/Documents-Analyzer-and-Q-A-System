# streamlit_app.py
import streamlit as st
import requests

INGEST_URL = "http://localhost:8001/ingest"
QUERY_URL = "http://localhost:8002/query"

st.title("Multi-File Ingestion & Q&A System")

uploaded_file = st.file_uploader("Upload a file (CSV / PDF / TXT)", type=["csv", "pdf", "txt"])
user_query = st.text_input("Ask something about the ingested file")

if uploaded_file:
    st.success("File uploaded. Sending to ingestion service...")

    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    try:
        res = requests.post(INGEST_URL, files=files)
        if res.status_code == 200:
            st.success("File successfully ingested into VectorDB!")
        else:
            st.error(f"Error: {res.text}")
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to ingestion backend. Make sure it's running on port 8001.")

if st.button("Ask Query"):
    if not user_query:
        st.warning("Enter a question.")
    else:
        payload = {"query": user_query}
        try:
            res = requests.post(QUERY_URL, json=payload)
            if res.status_code == 200:
                st.write("### Answer:")
                st.write(res.json().get("answer", "No answer returned"))
            else:
                st.error(f"Error: {res.text}")
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to RAG backend. Make sure it's running on port 8002.")
