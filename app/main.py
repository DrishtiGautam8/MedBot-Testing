from flask import Flask, Blueprint, request, jsonify, render_template
import os
import json
from dotenv import load_dotenv
from .rag import generate_rag_response
from .analysis_engine import analyze_query
from .embeddings import embed_text

# Load Knowledge Base
knowledge_base_path = os.path.join(os.path.dirname(__file__), 'data', 'knowledge_base.json')
with open(knowledge_base_path, 'r') as file:
    KNOWLEDGE_BASE = json.load(file)

# Load environment variables
load_dotenv()

# Initialize Flask App and Blueprint
app = Flask(__name__)
main = Blueprint('main', __name__)

# Map models to API names
MODEL_MAP = {
    "MISTRAL": "mixtral-8x7b-32768",
    "LLAMA": "llama-3.3-70b-versatile",
    "GEMINI": "gemini-2.0-pro-exp-02-05"

    
}

@main.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@main.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        query = data.get('query')
        model = data.get('model')

        if not query or not model:
            return jsonify({'error': 'Query and model are required'}), 400

        response = generate_rag_response(query, model)

        if 'error' in response:
            return jsonify({'error': response['error']}), 500
        
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': f'Failed to analyze: {str(e)}'}), 500

@main.route('/api/query', methods=['POST'])

@app.route('/api/query', methods=['POST'])
def handle_query():
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        model = data.get('model', 'GEMINI').upper()
        location = data.get('location', 'India')
        use_mock = data.get('useMock', False)

        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400
        
        if model not in MODEL_MAP:
            return jsonify({"error": f"Invalid model. Supported models: {', '.join(MODEL_MAP.keys())}"}), 400
        
        # Log the request
        print(f"Processing query: '{query}' using model: {model}")

        # Generate response using RAG
        if not use_mock:
            model_name = MODEL_MAP[model]
            embedded_query = embed_text(query)
            analysis_result = analyze_query(query)
            result = generate_rag_response(query, model_name, KNOWLEDGE_BASE, location, analysis_result)
        else:
            result = get_mock_response(query, model)

        return jsonify({
            "result": result,
            "model": model
        })

    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Mock response function for when API key is not available
def get_mock_response(query, model):
    context = search_knowledge_base(query)
    return f"""
<p><strong>Medical Assessment</strong></p>
<p>Based on the symptoms you've described, here are some possibilities:</p>
<ul>
  <li>This is a simulated response from the {model} model.</li>
  <li>Potential conditions may be listed in the knowledge base.</li>
</ul>
<p><strong>Recommendation:</strong></p>
<p>Please consult with a healthcare professional for proper diagnosis and treatment.</p>
<p><strong>Knowledge Base Context:</strong></p>
<p>{context}</p>
<div class="medical-disclaimer">
  <p>This is not medical advice. Always consult with a healthcare provider.</p>
</div>
"""

def search_knowledge_base(query):
    context = []
    query_lower = query.lower()
    
    for symptom, conditions in KNOWLEDGE_BASE.get("common_symptoms", {}).items():
        if symptom in query_lower:
            context.append(f"{symptom.capitalize()}: {', '.join(conditions)}")
    
    if "medical_advice" in KNOWLEDGE_BASE:
        context.append(KNOWLEDGE_BASE["medical_advice"].get("general", ""))
    
    return "\n".join(context) if context else "No specific information found in knowledge base."

# Register blueprint with the Flask app
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)
