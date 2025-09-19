import streamlit as st
import os
import json
import tempfile
from processor import process_pdf # <-- Import the backend logic

# --- STREAMLIT UI ---

st.set_page_config(layout="wide", page_title=" PDF Structure Extractor")

st.title(" PDF Structure Extractor")
st.markdown("Upload a PDF file to analyze its structure. The application will identify headings, paragraphs, tables, and charts, and then display the extracted content in a structured JSON format.")

# Initialize session state to store results
if 'json_result' not in st.session_state:
    st.session_state.json_result = None

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    if st.button("Process PDF"):
        # Use a temporary file to safely handle the uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        with st.spinner('Analyzing document... This may take a moment.'):
            try:
                # Call the backend function from processor.py
                json_data = process_pdf(tmp_file_path)
                st.session_state.json_result = json_data
                st.success("Processing complete!")
            except Exception as e:
                st.error(f"An error occurred during processing: {e}")
                st.exception(e) # Also display the full traceback for debugging
            finally:
                # Clean up the temporary file
                os.unlink(tmp_file_path)

# Display results if they exist in the session state
if st.session_state.json_result:
    st.divider()
    st.header("Extraction Results")

    # Convert result to a pretty-printed JSON string for display and download
    json_string = json.dumps(st.session_state.json_result, indent=4)
    
    st.download_button(
        label="Download JSON",
        file_name=f"{os.path.splitext(st.session_state.json_result['document_path'])[0]}.json",
        mime="application/json",
        data=json_string,
    )

    # Display the JSON output in the app
    st.json(json_string, expanded=True)