import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv()

def build_index(pdf_path):
    # Step 1 - Load PDF
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    print(f"Loaded {len(pages)} pages")

    # Step 2 - Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    chunks = splitter.split_documents(pages)
    print(f"Created {len(chunks)} chunks")

    # Step 3 - Create embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')
    texts = [chunk.page_content for chunk in chunks]
    embeddings = model.encode(texts)
    print(f"Created {len(embeddings)} embeddings")

    # Step 4 - Store in ChromaDB (persistent this time)
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    # Delete old collection if exists
    try:
        chroma_client.delete_collection("pdf_chunks")
    except:
        pass
    
    collection = chroma_client.create_collection("pdf_chunks")
    collection.add(
        documents=texts,
        embeddings=embeddings.tolist(),
        ids=[f"chunk_{i}" for i in range(len(texts))]
    )
    print(f"Stored {collection.count()} chunks in database")
    return True

if __name__ == "__main__":
    build_index("prompt.pdf")
    print("Index built successfully!")