import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load Embedding Model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize ChromaDB Client
chroma_client = chromadb.PersistentClient(path="./medical_db")

# Create or get the medical knowledge collection
medical_collection = chroma_client.get_or_create_collection("medical_knowledge")

# Function to load medical data from JSON and store it in ChromaDB
def load_medical_data(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as file:
        medical_data = json.load(file)

    doc_id = 0  # Use a counter for unique IDs

    # Iterate through the nested JSON and extract relevant information
    for category, conditions in medical_data.items():
        for condition, details in conditions.items():
            if isinstance(details, list):  # If values are a list (e.g., "fever": [causes...])
                text = f"{condition}: {', '.join(details)}"
            elif isinstance(details, dict):  # If values are a dict (e.g., "migraine": {symptoms, triggers...})
                text = f"{condition}: " + ", ".join(f"{key}: {', '.join(value)}" for key, value in details.items())

            # Convert text to embedding and add to ChromaDB
            embedding = embedding_model.encode(text).tolist()
            medical_collection.add(ids=[str(doc_id)], embeddings=[embedding], metadatas=[{"text": text}])
            doc_id += 1  # Increment ID

    print("✅ Medical data successfully loaded into ChromaDB!")

# Path to JSON file
json_file_path = "app\data\knowledge_base.json"

# Load and store medical data
load_medical_data(json_file_path)
