import streamlit as st
import asyncio
from backend import PDFQueryProcessor

# Initialize the processor in session state if it doesn't exist
if 'pdf_processor' not in st.session_state:
    st.session_state.pdf_processor = PDFQueryProcessor()

# Streamlit UI
st.set_page_config(page_title="PDF Query App", layout="wide")
st.header("PDF Query App")

# Sidebar for uploading PDF
with st.sidebar:
    st.header("Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# Initialize PDF when new file is uploaded
if uploaded_file is not None:
    file_name = uploaded_file.name
    if 'current_file' not in st.session_state or st.session_state.current_file != file_name:
        with st.spinner("Processing PDF..."):
            asyncio.run(st.session_state.pdf_processor.cleanup())  # Cleanup old resources
            st.session_state.pdf_processor = PDFQueryProcessor()  # Create new processor
            success = asyncio.run(st.session_state.pdf_processor.initialize_pdf(uploaded_file))
            if success:
                st.session_state.current_file = file_name
                st.success("PDF processed successfully!")
            else:
                st.error("Failed to process PDF")

# User input for query
query = st.text_input("Enter your query")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Process query
if uploaded_file is not None and query:
    try:
        with st.spinner("Processing query..."):
            response = asyncio.run(st.session_state.pdf_processor.process_query(query))

        st.session_state.chat_history.insert(0, {
            "user": query,
            "ollama": response
        })

        # Display the response
        st.write("***Current Response:***", response)

        # Print chat history
        st.write("---------------------------------------------")
        st.header("Previous Responses:")
        for chat in st.session_state.chat_history:
            st.write(f"**User**: {chat['user']}")
            st.write(f"**Ollama**: {chat['ollama']}")
            st.write("-----------------------------------------")

    except Exception as e:
        st.error(f"An error occurred: {e}")

else:
    if uploaded_file is None:
        st.warning("Please upload a PDF file.")
    if not query:
        st.warning("Please enter a query.")

# Cleanup when the app is closing
def cleanup_on_exit():
    if 'pdf_processor' in st.session_state:
        asyncio.run(st.session_state.pdf_processor.cleanup())

# Register cleanup
import atexit
atexit.register(cleanup_on_exit)
