# src/ui.py (Streamlit UI)

import streamlit as st
import requests
import json
from code_analyzer.config import load_config

config = load_config()
API_URL = f"http://{config['backend']['host']}:{config['backend']['port']}"

st.title("Code Analyzer UI")

# Fetch supported languages and modes
try:
    response = requests.get(f"{API_URL}/getParser")
    response.raise_for_status()
    data = response.json()
    languages = data["languages"]
    modes = data["modes"]
except Exception as e:
    st.error(f"Failed to connect to backend: {e}")
    st.stop()

# UI Elements
language = st.selectbox("Select Language", languages)
mode = st.selectbox("Select Mode", modes)
uploaded_file = st.file_uploader("Upload Code File", type=["py", "js", "java", "txt"])

if st.button("Analyze") and uploaded_file:
    with st.spinner("Analyzing..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            data = {"language": language, "mode": mode}
            response = requests.post(f"{API_URL}/parse", files=files, data=data)
            response.raise_for_status()
            results = response.json()["results"]

            st.success("Analysis Complete!")
            st.json(results)  # Display results as JSON; can format better if needed

        except requests.HTTPError as he:
            st.error(f"API Error: {he.response.json()['detail']}")
        except Exception as e:
            st.error(f"Unexpected Error: {e}")

# Custom Parser Info
st.sidebar.title("Custom Parsers")
st.sidebar.info("Add new languages by placing <language>.yaml files in src/code_analyzer/queries/custom/. Restart backend to load.")