import chromadb

# Initialize persistent client in the data/chromadb folder
client = chromadb.PersistentClient(path="data/chromadb")
collection = client.get_or_create_collection(name="pdf_knowledge")

def save_chunk(text, source_pdf, chunk_id):
    """
    Saves a single text chunk to the vector DB.
    """
    collection.add(
        documents=[text],
        metadatas=[{"source": source_pdf}],
        ids=[chunk_id]
    )

def search_db(query):
    results = collection.query(query_texts=[query], n_results=2)
    return results['documents'][0]