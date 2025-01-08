import streamlit as st
import asyncio
from backend import process_pdf_query

# Streamlit UI
st.set_page_config(page_title="PDF Query App", layout="wide")

st.header("PDF Query App")
# Sidebar for uploading PDF
with st.sidebar:
    st.header("Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# User input for query
query = st.text_input("Enter your query")

if "chat_history" not in st.session_state:
    st.session_state['chat_history'] = []

# Check if file is uploaded and query is provided
if uploaded_file is not None and query:
    try:
        with st.spinner(f"Finding in {uploaded_file.name}..."):
            # Run the async function in the synchronous environment using asyncio.run
            response = asyncio.run(process_pdf_query(uploaded_file, query))

        st.session_state['chat_history'].insert(0,{
                "user": query,
                "ollama": response
        })

        # Display the response
        st.write("***Current Response:***", response)

        # printing the history of the chat  
        st.write("---------------------------------------------")
        st.header("Previous Responses:")
        for chat in st.session_state['chat_history']:
            st.write(f"**User**: {chat['user']}")
            st.write(f"**Ollama**: {chat['ollama']}")
            st.write("-----------------------------------------")

    except Exception as e:
        # Error handling
        st.error(f"An error occurred while processing the file or query: {e}")

else:
    # Prompt the user if file is not uploaded or query is empty
    if uploaded_file is None:
        st.warning("Please upload a PDF file.")
    if not query:
        st.warning("Please enter a query.")