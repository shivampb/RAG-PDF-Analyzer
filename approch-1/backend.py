import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain.schema import Document
import pypdf
import chromadb
import tempfile
import os

#  this is approch one in which we create a new vector store and collection store inside the temp folder
# and for every new user query and delete the temp folder and create a new one

async def process_pdf_query(file, query: str) -> str:
    temp_dir = None
    vector_store = None
    chroma_client = None
    collection_name = None
    
    try:
        # Create a unique temporary directory
        temp_dir = tempfile.mkdtemp(prefix="pdf_query_")
        print(f"Created temp directory: {temp_dir}")
        
        # Initialize Chroma client with the unique path
        chroma_client = chromadb.PersistentClient(path=temp_dir)
        collection_name = f"pdf_collection_{os.urandom(4).hex()}"
        
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
    
    # finally:
        # Ensure proper cleanup
        print("Starting cleanup...")
        try:
            # First delete the vector store
            if vector_store is not None:
                del vector_store
                
            # Then delete the collection
            if chroma_client is not None and collection_name is not None:
                try:
                    chroma_client.delete_collection(collection_name)
                except Exception as e:
                    print(f"Error deleting collection: {str(e)}")
                del chroma_client
            
            # Finally remove the temporary directory
            if temp_dir and os.path.exists(temp_dir):
                print("Files in temp directory before deletion:")
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        print(f"- {os.path.join(root, file)}")
                await asyncio.sleep(10)  # Give a small delay for resources to be released
                try:
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=False)  # Changed to False to see errors
                    print(f"Successfully deleted temp directory: {temp_dir}")
                except Exception as e:
                    print(f"Error deleting temp directory: {str(e)}")
                    
        except Exception as e:
            print(f"Cleanup error: {str(e)}")