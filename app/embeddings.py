import os
import json
from google.generativeai import GenerativeModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("Groq_API_KEY")

# Path to the knowledge base file
KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(__file__), "data", "knowledge_base.json")

# Available models
AVAILABLE_MODELS = {
    "GEMINI": "gemini-2.0-pro-exp-02-05",
    "MISTRAL": "mixtral-8x7b-32768",
    "LLAMA": "llama-3.3-70b-versatile"
}

class AnalysisEngine:
    def __init__(self, model_name):
        if model_name not in AVAILABLE_MODELS:
            raise ValueError(f"Model '{model_name}' not supported. Choose from {list(AVAILABLE_MODELS.keys())}")
        
        self.model = AVAILABLE_MODELS[model_name]

        if model_name == "GEMINI":
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            self.client = GenerativeModel(model_name=self.model)
        
        elif model_name in ["MISTRAL", "LLAMA"]:
            from groq import Groq
            self.client = Groq(api_key=GROQ_API_KEY)

        print(f"✅ Analysis engine initialized with '{model_name}'")

    def generate_response(self, prompt):
        try:
            print(f"\n🔎 Generating response using {self.model}...\n")
            if self.model == AVAILABLE_MODELS["GEMINI"]:
                response = self.client.generate_content(prompt)
                return response.text
            elif self.model in [AVAILABLE_MODELS["MISTRAL"], AVAILABLE_MODELS["LLAMA"]]:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
            else:
                raise ValueError(f"❌ Unsupported model: {self.model}")
        except Exception as e:
            print(f"❌ Error generating response: {str(e)}")
            return None

# === ✅ Embedding Functions ===
def load_documents():
    """Load documents from knowledge_base.json."""
    print("📂 Loading documents from knowledge_base.json...")
    try:
        with open(KNOWLEDGE_BASE_PATH, "r") as file:
            knowledge_base = json.load(file)

            documents = []
            for symptom, causes in knowledge_base.get("common_symptoms", {}).items():
                documents.append(f"{symptom}: {'; '.join(causes)}")

            for condition, details in knowledge_base.get("common_conditions", {}).items():
                symptoms = "; ".join(details.get("symptoms", []))
                risk_factors = "; ".join(details.get("risk_factors", []))
                warning_signs = "; ".join(details.get("warning_signs", []))
                documents.append(f"{condition}: Symptoms: {symptoms}. Risk factors: {risk_factors}. Warning signs: {warning_signs}")

            for advice in knowledge_base.get("medical_advice", {}).get("emergency_signs", []):
                documents.append(f"Emergency Sign: {advice}")

            for category, steps in knowledge_base.get("first_aid", {}).items():
                if isinstance(steps, list):
                    documents.append(f"{category}: {'; '.join(steps)}")
                elif isinstance(steps, dict):
                    documents.append(f"{category}: {'; '.join(steps.get('steps', []))}")

            print(f"✅ Loaded {len(documents)} documents from knowledge_base.json")
            return documents
    except Exception as e:
        print(f"❌ Error loading knowledge base: {str(e)}")
        return []

def split_documents():
    print("✂️ Splitting documents into chunks...")
    documents = load_documents()
    chunks = [doc[:256] for doc in documents]
    print(f"✅ Split into {len(chunks)} chunks")
    return chunks

def create_embeddings():
    print("🧠 Creating embeddings...")
    chunks = split_documents()
    embeddings = [f"Embedding for: {chunk}" for chunk in chunks]
    print(f"✅ Created {len(embeddings)} embeddings")
    return embeddings
def embed_text(text):
    print(f"🧠 Embedding text: {text}")
    return f"Embedding for: {text}"

# === ✅ TEST CODE ===
if __name__ == "__main__":
    print("\n🚀 Testing Analysis Engine...")

    # Test with Groq's MISTRAL
    mistral_engine = AnalysisEngine("MISTRAL")
    prompt = "What is hyperpyrexia? in 50 words or less."
    response = mistral_engine.generate_response(prompt)
    print(f"\n👉 MISTRAL Response:\n{response}")

    # Test with Groq's LLAMA
    llama_engine = AnalysisEngine("LLAMA")
    prompt = "What is hyperpyrexia? in 50 words or less."
    response = llama_engine.generate_response(prompt)
    print(f"\n👉 LLAMA Response:\n{response}")

    # Test with Gemini
    gemini_engine = AnalysisEngine("GEMINI")
    prompt = "What is hyperpyrexia? in 50 words or less."
    response = gemini_engine.generate_response(prompt)
    print(f"\n👉 GEMINI Response:\n{response}")

    # Test embeddings
    docs = load_documents()
    print("\n📄 Loaded Documents:", docs[:3])  # Display first 3 docs for verification

    chunks = split_documents()
    print("\n✂️ Split Documents:", chunks[:3])  # Display first 3 chunks

    embeddings = create_embeddings()
    print("\n🧠 Embeddings:", embeddings[:3])  # Display first 3 embeddings
