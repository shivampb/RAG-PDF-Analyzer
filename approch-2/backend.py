import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain.schema import Document
import pypdf
import chromadb
import tempfile
import os

class PDFQueryProcessor:
    def __init__(self):
        self.temp_dir = None
        self.vector_store = None
        self.chroma_client = None
        self.collection_name = None
        self.llm = OllamaLLM(
            model="llama3.2:latest",
            base_url="http://127.0.0.1:11434/"
        )

    async def initialize_pdf(self, file) -> bool:
        try:
            # Create a unique temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix="pdf_query_")
            print(f"Created temp directory: {self.temp_dir}")
            
            # Initialize Chroma client
            self.chroma_client = chromadb.PersistentClient(path=self.temp_dir)
            self.collection_name = f"pdf_collection_{os.urandom(4).hex()}"
            
            # Extract text from PDF
            reader = pypdf.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            # Split text into chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
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

            # Create and use vector store
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=local_embedding,
                client=self.chroma_client,
                collection_name=self.collection_name
            )
            return True

        except Exception as e:
            print(f"Error in initialization: {str(e)}")
            await self.cleanup()
            return False

    async def process_query(self, query: str) -> str:
        try:
            if not self.vector_store:
                return "Please initialize with a PDF first."

            # Get relevant chunks
            retriever = self.vector_store.as_retriever(
                search_type="similarity", 
                search_kwargs={'k': 3}
            )
            
            retriever_chunks = retriever.invoke(query)
            if not retriever_chunks:
                return "No relevant information found in the PDF."

            merged_chunks = " ".join([chunk.page_content for chunk in retriever_chunks])
            
            prompt = f"""Based on the following context from the PDF, please answer the question.
            Context: {merged_chunks}
            
            Question: {query}
            
            Please provide a clear and concise answer based only on the context provided."""

            response = self.llm.invoke(prompt)
            return response if "error" not in response else "No response found"

        except Exception as e:
            print(f"Error in query processing: {str(e)}")
            return f"An error occurred: {str(e)}"

    async def cleanup(self):
        print("Starting cleanup...")
        try:
            if self.vector_store is not None:
                del self.vector_store
                
            if self.chroma_client is not None and self.collection_name is not None:
                try:
                    self.chroma_client.delete_collection(self.collection_name)
                except Exception as e:
                    print(f"Error deleting collection: {str(e)}")
                del self.chroma_client
            
            if self.temp_dir and os.path.exists(self.temp_dir):
                print("Files in temp directory before deletion:")
                for root, dirs, files in os.walk(self.temp_dir):
                    for file in files:
                        print(f"- {os.path.join(root, file)}")
                await asyncio.sleep(1)
                try:
                    import shutil
                    shutil.rmtree(self.temp_dir, ignore_errors=False)
                    print(f"Successfully deleted temp directory: {self.temp_dir}")
                except Exception as e:
                    print(f"Error deleting temp directory: {str(e)}")
                    
        except Exception as e:
            print(f"Cleanup error: {str(e)}")