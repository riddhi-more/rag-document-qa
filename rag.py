import os
from dotenv import load_dotenv
from groq import Groq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb


load_dotenv()  # ← must be here, before anything uses the key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#load the pdf document using PyPDFLoader and extract the text content from each page. 
# The load_pdf function takes the file path of the PDF document as input and returns a list of pages,
# where each page is represented as a dictionary containing the page content and metadata.
def load_pdf(file_path):
    loader = PyPDFLoader(file_path)
    pages= loader.load()
    return pages

pages = load_pdf("prompt.pdf")
# print(f"Total number pages in the pdf:{len(pages)}")
# print(f"First page in the pdf:{pages[0].page_content[:10]}")

#step 2: split the document into chunks
splitter= RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunk = splitter.split_documents(pages)
# print(f"Total number of chunks:{len(chunk)}")
# print(f"First chunk:{chunk[0].page_content[:10]}")

#step 3: create embeddings for the chunks
def create_embedding(chunks):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    # loads a free pre-trained model that converts text to numbers
    # runs 100% locally, no API needed
    #embedddings = model.encode([chunk.page_content for chunck in chunks]) OR
    texts = [chunk.page_content for chunk in chunks]
    # extracts just the text from each chunk
    # same list comprehension pattern you already know

    embeddings = model.encode(texts)
    # converts every chunk of text into a vector of numbers
    # returns a list of vectors — one per chunk
    return texts, embeddings

texts, embeddings = create_embedding(chunk)
print(f"Number of embeddings: {len(embeddings)}")
print(f"Embedding size: {len(embeddings[0])} numbers")
# print(texts)


#✅ Step 4 — STORE in vector database (ChromaDB)    
def insert_into_chromadb(texts, embeddings):
    clientDB = chromadb.Client()
    collection= clientDB.create_collection(name="pdf_chunks")
    collection.add(
        documents = texts,
        embeddings = embeddings,
        ids= [f"chunk_{i}" for i in range(len(texts))]
    )
    return collection

collection = insert_into_chromadb(texts, embeddings)
print(f"inserted {collection.count()}")

#✅ Step 5 — convert question into embedding 
def embed_questions(question):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    question_embedding = model.encode([question])
    return question_embedding

question =  "what service does this document describe?"
question_embed = embed_questions(question)
print(f"question embedding size: {len(question_embed[0])} numbers")


# ⬜ Step 6 — SEARCH for matching chunks in the vector database- compute the similarity between the question embedding and the chunk embeddings in the database, 
# and retrieve the most relevant chunks based on their similarity scores from chromadb
def search_chunks(collection, question_embedding, n_results=2):
    results = collection.query(
        query_embeddings=question_embedding,
        n_results=n_results
    )
    return results['documents'][0]

relevant_chunks = search_chunks(collection, question_embed)
print(f"Found {len(relevant_chunks)} relevant chunks")
# debug
# print(type(relevant_chunks))
# print(relevant_chunks)
# print(f"Most relevant chunk: {relevant_chunks[0]}")

# ⬜ Step 6 — SEARCH for matching chunks in the vector database- 
# compute the similarity between the question embedding and the chunk embeddings in the database,



def get_answer(question, relevant_chunks):
    context = "\n\n".join(relevant_chunks)
    prompt = f"""Answer the question using only the context below.
    If the answer is not in the context, say "I don't know".
    Context:
    {context}
    
    Question: 
    {question}
    """
    # this is how I make calls to my LLM using Groq's Python SDK. 
    # You can also use the Groq CLI or the REST API if you prefer.
    response = client.chat.completions.create(
        model = "llama-3.1-8b-instant",
        messages = [
            # {'role': 'user', 'content':prompt}]
            {'role': 'system', 'content':"Answer questions using only the provided context. If the answer is not in the context, say I don't know."},
            {'role': 'user', 'content':f"context:\n{context}\n\nQuestion:\n{question}"}]
    )
    return response.choices[0].message.content
answer = get_answer(question, relevant_chunks)

print(f"Question: {question}")
print(f"Answer: {answer}")