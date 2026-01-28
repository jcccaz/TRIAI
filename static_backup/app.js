// ==================== //
// State Management
// ==================== //
let isQuerying = false;
let selectedFile = null;

// ==================== //
// DOM Elements
// ==================== //
const questionInput = document.getElementById('questionInput');
const askButton = document.getElementById('askButton');
const loadingState = document.getElementById('loadingState');
const consensusSection = document.getElementById('consensusSection');
const consensusContent = document.getElementById('consensusContent');
const citationToggle = document.getElementById('citationToggle');
const thoughtToggle = document.getElementById('thoughtToggle');

// File Upload Elements
const fileUploadArea = document.getElementById('fileUploadArea');
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');
const uploadPlaceholder = fileUploadArea.querySelector('.upload-placeholder');
const fileNameDisplay = filePreview.querySelector('.file-name');
const removeFileBtn = filePreview.querySelector('.remove-file');

// Response elements
const responses = {
    openai: {
        model: document.getElementById('openai-model'),
        time: document.getElementById('openai-time'),
        cost: document.getElementById('openai-cost'),
        response: document.getElementById('openai-response'),
        thought: document.querySelector('#openai-thought .thought-content'),
        thoughtContainer: document.getElementById('openai-thought'),
        status: document.getElementById('openai-status'),
        card: document.querySelector('.ai-card[data-ai="openai"]')
    },
    anthropic: {
        model: document.getElementById('anthropic-model'),
        time: document.getElementById('anthropic-time'),
        cost: document.getElementById('anthropic-cost'),
        response: document.getElementById('anthropic-response'),
        thought: document.querySelector('#anthropic-thought .thought-content'),
        thoughtContainer: document.getElementById('anthropic-thought'),
        status: document.getElementById('anthropic-status'),
        card: document.querySelector('.ai-card[data-ai="anthropic"]')
    },
    google: {
        model: document.getElementById('google-model'),
        time: document.getElementById('google-time'),
        cost: document.getElementById('google-cost'),
        response: document.getElementById('google-response'),
        thought: document.querySelector('#google-thought .thought-content'),
        thoughtContainer: document.getElementById('google-thought'),
        status: document.getElementById('google-status'),
        card: document.querySelector('.ai-card[data-ai="google"]')
    },
    perplexity: {
        model: document.getElementById('perplexity-model'),
        time: document.getElementById('perplexity-time'),
        cost: document.getElementById('perplexity-cost'),
        response: document.getElementById('perplexity-response'),
        thought: document.querySelector('#perplexity-thought .thought-content'),
        thoughtContainer: document.getElementById('perplexity-thought'),
        status: document.getElementById('perplexity-status'),
        card: document.querySelector('.ai-card[data-ai="perplexity"]')
    }
};

// ==================== //
// Event Listeners
// ==================== //
askButton.addEventListener('click', handleAskAllAIs);
citationToggle.addEventListener('change', handleCitationToggle);
thoughtToggle.addEventListener('change', handleThoughtToggle);

questionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        handleAskAllAIs();
    }
});

// File Upload Logic
fileUploadArea.addEventListener('click', () => fileInput.click());

fileUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileUploadArea.classList.add('dragover');
});

fileUploadArea.addEventListener('dragleave', () => {
    fileUploadArea.classList.remove('dragover');
});

fileUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    fileUploadArea.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleFileSelect(e.target.files[0]);
    }
});

removeFileBtn.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent triggering upload click
    selectedFile = null;
    fileInput.value = ''; // Reset input
    filePreview.classList.add('hidden');
    uploadPlaceholder.classList.remove('hidden');
});

function handleFileSelect(file) {
    selectedFile = file;
    fileNameDisplay.textContent = file.name;
    uploadPlaceholder.classList.add('hidden');
    filePreview.classList.remove('hidden');
}

// Copy buttons
document.querySelectorAll('.copy-button').forEach(button => {
    button.addEventListener('click', handleCopyResponse);
});

// ==================== //
// Main Function
// ==================== //
async function handleAskAllAIs() {
    const question = questionInput.value.trim();

    if (!question) {
        alert('Please enter a question first!');
        return;
    }

    if (isQuerying) {
        return;
    }

    // Update UI state
    isQuerying = true;
    askButton.disabled = true;
    askButton.querySelector('.button-text').textContent = 'Querying...';
    loadingState.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    consensusSection.classList.add('hidden');

    // Reset all responses
    resetResponses();

    try {
        let response;

        // Check if we need to send a file
        if (selectedFile) {
            const formData = new FormData();
            formData.append('question', question);
            formData.append('file', selectedFile);

            response = await fetch('/api/ask', {
                method: 'POST',
                body: formData // No Content-Type header needed, browser sets boundary
            });
        } else {
            // Standard JSON request
            response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question })
            });
        }

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || 'API request failed');
        }

        const data = await response.json();

        // Update UI with responses using the "results" key
        const results = data.results;
        updateResponse('openai', results.openai);
        updateResponse('anthropic', results.anthropic);
        updateResponse('google', results.google);
        updateResponse('perplexity', results.perplexity);

        // Show Consensus
        if (data.consensus) {
            consensusContent.innerHTML = formatMarkdown(data.consensus);
            consensusSection.classList.remove('hidden');
        }

        // Show results
        loadingState.classList.add('hidden');
        resultsSection.classList.remove('hidden');

        // Apply toggle states
        handleCitationToggle();
        handleThoughtToggle();

        // Render Mermaid Charts if any
        mermaid.init();

    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
        loadingState.classList.add('hidden');
    } finally {
        // Reset UI state
        isQuerying = false;
        askButton.disabled = false;
        askButton.querySelector('.button-text').textContent = 'Ask All AIs';
    }
}

// ==================== //
// Response Handling
// ==================== //
function resetResponses() {
    Object.keys(responses).forEach(aiName => {
        responses[aiName].response.textContent = 'Waiting for response...';
        responses[aiName].response.classList.remove('error');
        responses[aiName].thought.textContent = '';
        responses[aiName].thoughtContainer.classList.add('hidden');
        responses[aiName].time.textContent = '-- s';
        responses[aiName].cost.textContent = '$0.000';
        responses[aiName].status.textContent = '';
        responses[aiName].status.classList.remove('success', 'error');
        responses[aiName].card.classList.remove('hidden-by-filter');
        responses[aiName].card.dataset.hasCitations = 'false';
    });
}

function updateResponse(aiName, data) {
    const elements = responses[aiName];
    if (!elements) return;

    // Update model name
    if (data.model) {
        elements.model.textContent = data.model;
    }

    // Update response time & cost
    elements.time.textContent = `${data.time}s`;
    elements.cost.textContent = `$${data.cost?.toFixed(4) || '0.0000'}`;

    // Update citation data
    elements.card.dataset.hasCitations = data.has_citations;

    // Update thought Trace if available
    if (data.thought) {
        elements.thought.innerHTML = formatMarkdown(data.thought);
        elements.thoughtContainer.dataset.hasThought = 'true';
    } else {
        elements.thoughtContainer.dataset.hasThought = 'false';
    }

    // Update response text
    if (data.success) {
        elements.response.innerHTML = formatMarkdown(data.response);
        elements.response.classList.remove('error');
        elements.status.textContent = '✓ Success';
        elements.status.classList.add('success');
        elements.status.classList.remove('error');
    } else {
        elements.response.textContent = data.response;
        elements.response.classList.add('error');
        elements.status.textContent = '✗ Error';
        elements.status.classList.add('error');
        elements.status.classList.remove('success');
    }
}

function handleCitationToggle() {
    const isChecked = citationToggle.checked;
    const grid = document.querySelector('.results-grid');
    if (isChecked) {
        grid.classList.add('citations-only');
    } else {
        grid.classList.remove('citations-only');
    }
}

function handleThoughtToggle() {
    const isChecked = thoughtToggle.checked;

    Object.keys(responses).forEach(aiName => {
        const container = responses[aiName].thoughtContainer;
        const hasThought = container.dataset.hasThought === 'true';

        if (isChecked && hasThought) {
            container.classList.remove('hidden');
        } else {
            container.classList.add('hidden');
        }
    });
}

// ==================== //
// Formatting
// ==================== //
function formatMarkdown(text) {
    if (!text) return '';

    // 1. Detect and wrap Mermaid blocks
    // Format: ```mermaid ... ```
    text = text.replace(/```mermaid\n([\s\S]*?)\n```/g, '<div class="mermaid">$1</div>');

    // 2. Wrap standard code blocks and detect renderable content
    text = text.replace(/```(xml|svg|html)\n([\s\S]*?)\n```/g, (match, lang, code) => {
        // Create a unique ID for this block
        const id = 'code-' + Math.random().toString(36).substr(2, 9);
        const encodedCode = encodeURIComponent(code);

        let btn = '';
        if (lang === 'svg' || lang === 'html' || lang === 'xml') {
            // Add Render Button
            btn = `<button class="render-btn" onclick="renderCode('${id}', '${lang}', '${encodedCode}')">▶ Render Preview</button>`;
        }

        return `<pre><code class="language-${lang}">${code}</code></pre>
                ${btn}
                <div id="${id}" class="preview-box hidden"></div>`;
    });

    text = text.replace(/```(\w*)\n([\s\S]*?)\n```/g, '<pre><code class="language-$1">$2</code></pre>');

    // 3. Inline code
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

    // 4. Bold / Italic
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // 5. Line breaks to <br> (simple handling)
    text = text.replace(/\n\n/g, '<br><br>').replace(/\n/g, '<br>');

    return text;
}

// Global function for rendering code
window.renderCode = function (containerId, lang, encodedCode) {
    const container = document.getElementById(containerId);
    const code = decodeURIComponent(encodedCode);

    container.classList.remove('hidden');
    container.innerHTML = ''; // Clear previous

    const iframe = document.createElement('iframe');
    container.appendChild(iframe);

    // Write content to iframe
    const doc = iframe.contentWindow.document;
    doc.open();

    if (lang === 'svg' || (lang === 'xml' && code.includes('<svg'))) {
        doc.write(`
            <style>
                body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background: #fff; }
                svg { max-width: 95%; max-height: 95%; }
            </style>
            ${code}
        `);
    } else {
        // HTML
        doc.write(code);
    }

    doc.close();
};

// ==================== //
// Copy Functionality
// ==================== //
function handleCopyResponse(e) {
    const button = e.currentTarget;
    const targetAI = button.getAttribute('data-target');
    const responseText = responses[targetAI].response.textContent;

    // Copy to clipboard
    navigator.clipboard.writeText(responseText).then(() => {
        // Visual feedback
        const originalHTML = button.innerHTML;
        button.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M13.5 4L6 11.5L2.5 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
        button.style.color = '#10b981';

        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.style.color = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy to clipboard');
    });
}

// ==================== //
// Initialization
// ==================== //
console.log('TriAI Compare loaded successfully');
