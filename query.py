import os
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_answer(question):
    # Load existing database — no re-indexing!
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_collection("pdf_chunks")

    # Embed question
    model = SentenceTransformer('all-MiniLM-L6-v2')
    question_embedding = model.encode([question])

    # Search chunks
    results = collection.query(
        query_embeddings=question_embedding.tolist(),
        n_results=2
    )
    relevant_chunks = results['documents'][0]

    # Get answer from Groq
    context = "\n\n".join(relevant_chunks)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Answer only from the provided context. If not found say I don't know."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    question = "What is the refund policy?"
    answer = get_answer(question)
    print(f"Question: {question}")
    print(f"Answer: {answer}")
    