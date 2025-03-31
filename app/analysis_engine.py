import os
import json
import chromadb
from groq import Groq
from google.generativeai import GenerativeModel
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer  # ✅ Load embedding model

# Load environment variables
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("Groq_API_KEY")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Available models
AVAILABLE_MODELS = {
    "MISTRAL": "mistral-saba-24b",
    "LLAMA": "llama-3.3-70b-versatile",
    "GEMINI": "gemini-2.0-pro-exp-02-05"
}

class AnalysisEngine:
    def __init__(self, model_name):
        if model_name not in AVAILABLE_MODELS:
            raise ValueError(f"Model '{model_name}' not supported. Choose from {list(AVAILABLE_MODELS.keys())}")
        
        self.model = AVAILABLE_MODELS[model_name]
        
        # ✅ Load ChromaDB Client
        self.chroma_client = chromadb.PersistentClient(path="./medical_db")
        self.medical_collection = self.chroma_client.get_or_create_collection("medical_knowledge")

        # ✅ Load SentenceTransformer for embeddings
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        if model_name == "GEMINI":
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            self.client = GenerativeModel(model_name=self.model)
        else:
            self.client = Groq(api_key=GROQ_API_KEY)

        print(f"✅ RAG Engine initialized with '{model_name}' and ChromaDB")

    def search_medical_knowledge(self, query):
        """Finds relevant medical information using **vector search**"""
        query_embedding = self.embedding_model.encode(query).tolist()

        # 🔎 Perform similarity search in ChromaDB
        results = self.medical_collection.query(
            query_embeddings=[query_embedding],
            n_results=3  # Retrieve top 3 matches
        )

        if not results["metadatas"] or not results["metadatas"][0]:
            return ["No relevant medical information found."]

        # Extract text from metadata
        return [meta["text"] for meta in results["metadatas"][0]]

    def generate_response(self, prompt):
        try:
            relevant_info = self.search_medical_knowledge(prompt)  # ✅ Uses ChromaDB
            relevant_text = "\n".join(relevant_info)

            formatted_prompt = f"""
            You are a medical AI assistant. Given the following symptoms, provide:
            1. **Prognosis** (What could it be? Answer in 2-3 lines.)
            2. **Possible Remedies** (3-4 lines or less.)
            3. **Medical Advisory** (Which specialist should the user see?)
            4. **Precautions** (What should the user avoid?)

            Symptoms: {prompt}

            Relevant Medical Information:
            {relevant_text}

            Please keep your response concise and structured.
            """

            print(f"\n🔎 Generating response using {self.model} with RAG and Vector Search...\n")
            if self.model == "gemini-2.0-pro-exp-02-05":
                response = self.client.generate_content(formatted_prompt)
                return response.text
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": formatted_prompt}]
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error generating response: {str(e)}")
        return None


#  Move analyze_query outside the class
def analyze_query(query, model_name):
    """Processes user query and returns relevant medical information"""
    engine = AnalysisEngine(model_name)  # Create engine instance
    return engine.generate_response(query)


#  Export both symbols
__all__ = ["AnalysisEngine", "analyze_query"]
