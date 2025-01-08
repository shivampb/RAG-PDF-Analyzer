import streamlit as st
import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain.schema import Document
import pypdf

# this approch is a reasonse that shows default tenet error because of execution of whole code after 
# every query and making db space full and not able to process the query

# Asynchronous function
async def main(file, query: str) -> str:
    print("start")
    reader = pypdf.PdfReader(file)

    text = ""
    for page in reader.pages:
        text += page.extract_text()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len
    )

    doc = Document(page_content=text)
    chunks = splitter.split_documents([doc])

    local_embedding = OllamaEmbeddings(model="nomic-embed-text:latest", base_url="http://127.0.0.1:11434")

    # Store embedding into Chroma vector store
    vector_store = Chroma.from_documents(documents=chunks, embedding=local_embedding, persist_directory=None)

    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={'k': 3})
    if retriever is None:
        return "No response found"
    else:
        retriever_chunks = retriever.invoke(query)

    merged_chunks = " ".join([chunks.page_content for chunks in retriever_chunks])

    llm = OllamaLLM(model="llama3.2:latest", base_url="http://127.0.0.1:11434/")
    response = llm.invoke(f"""Answer the following question Using PDF:
                            QUESTION: {query}. ANSWER: {merged_chunks}""")
    return response


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
            response = asyncio.run(main(uploaded_file, query))

        st.session_state['chat_history'].insert(0,{
                "user":query,
                "ollama":response
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


if "__main__" == __name__:
    st.run(main())
