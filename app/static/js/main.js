// DOM Elements
const submitBtn = document.getElementById('submit-btn');
const clearBtn = document.getElementById('clear-btn');
const symptomsTextarea = document.getElementById('symptoms-textarea');
const charCount = document.getElementById('char-count');
const assessmentContainer = document.getElementById('assessment-container');
const modelButtons = document.querySelectorAll('.model-button');
const modelName = document.querySelector('.model-name');
const modelInfo = document.querySelector('.model-info');
const mockToggle = document.getElementById('mock-toggle');
const copyBtn = document.getElementById('copy-btn');
const saveBtn = document.getElementById('save-btn');

// State Variables
let selectedModel = 'GEMINI'; // Default model
// Model mapping
const MODEL_MAP = {
    "mixtral-8x7b-32768": "MISTRAL",
    "llama-3.3-70b-versatile": "LLAMA",
    "gemini-2.0-pro-exp-02-05": "GEMINI"
};

// ✅ Handle Form Submission (Fetch API)
submitBtn.addEventListener('click', async () => {
    const query = symptomsTextarea.value.trim();
    if (!query) {
        alert('Please describe your symptoms first!');
        return;
    }

    // ✅ Fix: Map model name to short key
    const mappedModel = MODEL_MAP[selectedModel] || selectedModel;

    const requestData = {
        query: query,
        model: mappedModel, // ✅ Send the mapped model
        location: 'India',
        useMock: mockToggle.checked
    };

    assessmentContainer.innerHTML = `<p>⏳ Analyzing symptoms...</p>`;

    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();

        if (data.error) {
            assessmentContainer.innerHTML = `<p class="error">❌ ${data.error}</p>`;
        } else {
            assessmentContainer.innerHTML = `<p>${data.result}</p>`;
        }
    } catch (error) {
        assessmentContainer.innerHTML = `<p class="error">❌ Failed to analyze symptoms. Please try again later.</p>`;
        console.error('Error:', error);
    }
});

// ============================
// ✅ Handle Model Selection
// ============================
modelButtons.forEach((button) => {
    button.addEventListener('click', () => {
        modelButtons.forEach((btn) => btn.classList.remove('active'));
        button.classList.add('active');

        // Update selected model
        selectedModel = button.getAttribute('data-model').toUpperCase();

        // Update UI model info
        modelName.textContent = button.querySelector('span').textContent;
        modelInfo.textContent = `Specialized symptom analysis using ${selectedModel} model.`;
    });
});

// ============================
// ✅ Character Counter Update
// ============================
symptomsTextarea.addEventListener('input', () => {
    charCount.textContent = `${symptomsTextarea.value.length} characters`;
});

// ============================
// ✅ Handle Clear Form
// ============================
clearBtn.addEventListener('click', () => {
    symptomsTextarea.value = '';
    charCount.textContent = `0 characters`;
    assessmentContainer.innerHTML = `
        <div class="empty-state">
            <div class="icon-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"></path>
                </svg>
            </div>
            <p>Describe your symptoms to receive a health assessment</p>
        </div>
    `;
});

// ============================
// ✅ Handle Form Submission (Fetch API)
// ============================
submitBtn.addEventListener('click', async () => {
    const query = symptomsTextarea.value.trim();
    if (!query) {
        alert('Please describe your symptoms first!');
        return;
    }

    // Prepare data
    const requestData = {
        query: query,
        model: selectedModel,
        location: 'India',
        useMock: mockToggle.checked
    };

    // Loading state
    assessmentContainer.innerHTML = `<p>⏳ Analyzing symptoms...</p>`;

    try {
        const response = await fetch('/api/query', { // ✅ Fixed endpoint
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();

        // ✅ Handle Response Data
        if (data.error) {
            assessmentContainer.innerHTML = `<p class="error">❌ ${data.error}</p>`;
        } else if (typeof data.result === 'object') {
            // ✅ Handle object response
            assessmentContainer.innerHTML = `<pre>${JSON.stringify(data.result, null, 2)}</pre>`;
        } else {
            // ✅ Handle string response
            assessmentContainer.innerHTML = `<p>${data.result}</p>`;
        }
    } catch (error) {
        assessmentContainer.innerHTML = `<p class="error">❌ Failed to analyze symptoms. Please try again later.</p>`;
        console.error('Error:', error);
    }
});

// ============================
// ✅ Copy to Clipboard
// ============================
copyBtn.addEventListener('click', () => {
    const text = assessmentContainer.textContent;
    if (!text) return;

    navigator.clipboard.writeText(text).then(() => {
        alert('✅ Copied to clipboard!');
    }).catch((err) => {
        console.error('Error copying text:', err);
    });
});

// ============================
// ✅ Save to File
// ============================
saveBtn.addEventListener('click', () => {
    const text = assessmentContainer.textContent;
    if (!text) return;

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'health-assessment.txt';
    a.click();
    URL.revokeObjectURL(url);
});

// ============================
// ✅ Advanced Options Toggle
// ============================
const advancedToggle = document.getElementById('advanced-toggle');
const advancedContent = document.getElementById('advanced-content');

advancedToggle.addEventListener('click', () => {
    advancedContent.classList.toggle('hidden');
});

console.log('✅ JS Loaded!');
