import chromadb

# Initialize ChromaDB Client
chroma_client = chromadb.PersistentClient(path="./medical_db")

# Get the medical knowledge collection
medical_collection = chroma_client.get_or_create_collection("medical_knowledge")

# Fetch all stored documents
results = medical_collection.get()

# Print stored documents
print("Stored Medical Documents in ChromaDB:")
for doc_id, metadata in zip(results["ids"], results["metadatas"]):
    print(f"ID: {doc_id} - Text: {metadata['text']}")
