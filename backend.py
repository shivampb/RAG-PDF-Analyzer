import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain.schema import Document
import pypdf
import chromadb
import tempfile
import os

async def process_pdf_query(file, query: str) -> str:
    temp_dir = None
    try:
        # Create a unique temporary directory
        temp_dir = tempfile.mkdtemp(prefix="pdf_query_")
        
        # Initialize Chroma client with the unique path
        chroma_client = chromadb.PersistentClient(path=temp_dir)
        collection_name = f"pdf_collection_{os.urandom(4).hex()}"  # Create unique collection name
        
        # Extract text from PDF
        reader = pypdf.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # Split text into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,  # Reduced overlap for efficiency
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        doc = Document(page_content=text)
        chunks = splitter.split_documents([doc])

        # Initialize embedding model
        local_embedding = OllamaEmbeddings(
            model="nomic-embed-text:latest", 
            base_url="http://127.0.0.1:11434"
        )

        # Create and use vector store with unique collection
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=local_embedding,
            client=chroma_client,
            collection_name=collection_name
        )

        # Get relevant chunks
        retriever = vector_store.as_retriever(
            search_type="similarity", 
            search_kwargs={'k': 3}
        )
        
        retriever_chunks = retriever.invoke(query)
        if not retriever_chunks:
            return "No relevant information found in the PDF."

        merged_chunks = " ".join([chunk.page_content for chunk in retriever_chunks])
        # print(merged_chunks)
        
        # Generate response using LLM
        llm = OllamaLLM(
            model="llama3.2:latest", # Changed to llama2 as it's more commonly available
            base_url="http://127.0.0.1:11434/"
        )
        
        prompt = f"""Based on the following context from the PDF, please answer the question.
        Context: {merged_chunks}
        
        Question: {query}
        
        Please provide a clear and concise answer based only on the context provided."""

        response = llm.invoke(prompt)
        if "error" in response:
            return "No response found"
        print("success")
        return response

    except Exception as e:
        print(f"Error in processing: {str(e)}")
        return f"An error occurred: {str(e)}"
    
    finally:
        # Clean up: Delete collection and remove temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                # Force close any open handles
                if 'vector_store' in locals():
                    del vector_store
                if 'chroma_client' in locals():
                    chroma_client.delete_collection(collection_name)
                    del chroma_client
                
                # Remove temporary directory and its contents
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"Cleanup error: {str(e)}")