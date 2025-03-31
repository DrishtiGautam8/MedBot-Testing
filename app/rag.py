import os
from .analysis_engine import AnalysisEngine
from .embeddings import load_documents, split_documents, create_embeddings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ChromaDB path and embedding model
CHROMA_PATH = './chroma_db'
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Initialize embedding function
embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={'device': 'cpu'})

# ✅ Load ChromaDB (with metadata)
vectorstore = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embedding_function,
    collection_metadata={"topic": "medical_info"}
)

# Initialize models
mistral_engine = AnalysisEngine("MISTRAL")
llama_engine = AnalysisEngine("LLAMA")
gemini_engine = AnalysisEngine("GEMINI")

# 🔎 Retrieve context from ChromaDB
# 🔎 Retrieve context from ChromaDB
def retrieve_context(query):
    try:
        print(f"\n🔎 Retrieving context for query: '{query}'\n")
        # Remove `search_type="similarity"`
        results = vectorstore.similarity_search(query, k=5) 

        if not results:
            return "No relevant context found."

        context = "\n".join([result.page_content for result in results])
        print(f"🧠 Retrieved Context:\n{context}\n")
        return context

    except Exception as e:
        print(f"❌ Error retrieving context: {e}")
        return f"Error: {e}"

# 🚀 Generate response using selected model
def generate_response(query, model_name):
    context = retrieve_context(query)
    
    if not context or "Error" in context:
        return {"error": context}

    try:
        if model_name == "MISTRAL":
            response = mistral_engine.generate_response(f"{context}\n{query}")
        elif model_name == "LLAMA":
            response = llama_engine.generate_response(f"{context}\n{query}")
        elif model_name == "GEMINI":
            response = gemini_engine.generate_response(f"{context}\n{query}")
        else:
            response = f"❌ Model '{model_name}' not supported."

        print(f"\n👉 **{model_name} Response:**\n{response or '❌ No response generated.'}")
        return {"model": model_name, "response": response}

    except Exception as e:
        print(f"❌ Error generating response for {model_name}: {e}")
        return {"error": f"Failed to generate response using {model_name}: {str(e)}"}


def generate_rag_response(query, model_name):
    return generate_response(query, model_name)

__all__ = ["generate_response", "generate_rag_response"]


if __name__ == "__main__":
    # Test context retrieval
    print(retrieve_context("What are the symptoms of hyperpyrexia?"))

    # Test response generation
    print(generate_response("What are the symptoms of hyperpyrexia?", "MISTRAL"))
    print(generate_response("What are the symptoms of hyperpyrexia?", "LLAMA"))
    print(generate_response("What are the symptoms of hyperpyrexia?", "GEMINI"))
