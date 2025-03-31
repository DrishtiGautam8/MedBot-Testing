import chromadb
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB Client
chroma_client = chromadb.PersistentClient(path="./medical_db")

# Get the medical knowledge collection
medical_collection = chroma_client.get_or_create_collection("medical_knowledge")

# Load Embedding Model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Define a search query
query_text = "What are the common symptoms of fever?"

# Convert query into embeddings
query_embedding = embedding_model.encode(query_text).tolist()

# Search in ChromaDB
results = medical_collection.query(
    query_embeddings=[query_embedding],
    n_results=2  # Retrieve top 2 most relevant results
)

# Print search results
print("🔎 Query Results:")
for doc_id, metadata in zip(results["ids"][0], results["metadatas"][0]):
    print(f"ID: {doc_id} - Text: {metadata['text']}")
