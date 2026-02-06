// State Management
// ==================== //
let isQuerying = false;
let selectedFiles = [];
let currentProjectName = null;
let currentComparisonId = null;

// ==================== //
// Status Rotation Logic
// ==================== //
let statusInterval;
const statusPhrases = [
    "Querying models...",
    "Comparing perspectives...",
    "Synthesizing consensus...",
    "Analyzing data patterns...",
    "Finalizing report..."
];

function startStatusRotation() {
    const statusText = document.getElementById('loadingStatusText');
    if (!statusText) return;

    let index = 0;
    statusText.textContent = statusPhrases[0];
    statusText.style.opacity = 1;

    statusInterval = setInterval(() => {
        index = (index + 1) % statusPhrases.length;
        statusText.style.opacity = 0;
        setTimeout(() => {
            statusText.textContent = statusPhrases[index];
            statusText.style.opacity = 1;
        }, 200); // Wait for fade out
    }, 2000); // Change every 2 seconds
}

function stopStatusRotation() {
    if (statusInterval) {
        clearInterval(statusInterval);
        statusInterval = null;
    }
}

// ==================== //
// DOM Elements
// ==================== //
const questionInput = document.getElementById('questionInput');
const askButton = document.getElementById('askButton');
const visualizeBtn = document.getElementById('visualizeBtn');
const cameraBtn = document.getElementById('cameraBtn');
const cameraInput = document.getElementById('cameraInput');
const loadingState = document.getElementById('loadingState');
const consensusSection = document.getElementById('consensusSection');
const consensusContent = document.getElementById('consensusContent');
const vaultToggle = document.getElementById('vaultToggle');
const citationToggle = document.getElementById('citationToggle');
const thoughtToggle = document.getElementById('thoughtToggle');
const podcastToggle = document.getElementById('podcastToggle');
const councilToggle = document.getElementById('councilToggle');
const hardModeToggle = document.getElementById('hardModeToggle');
const workflowToggle = document.getElementById('workflowToggle');
const workflowArea = document.getElementById('workflowArea');
const workflowSelect = document.getElementById('workflowSelect');
const workflowResultsSection = document.getElementById('workflowResultsSection');
const workflowStepsContainer = document.getElementById('workflowStepsContainer');
const workflowProgressBarFill = document.getElementById('workflowProgressBarFill');
const workflowProgressText = document.getElementById('workflowProgressText');
const activeWorkflowName = document.getElementById('activeWorkflowName');
const workflowResetBtn = document.getElementById('workflowResetBtn');
const workflowExportBtn = document.getElementById('workflowExportBtn');
const pauseWorkflowBtn = document.getElementById('pauseWorkflowBtn');
const editStepModal = document.getElementById('editStepModal');
const editStepTextArea = document.getElementById('editStepTextArea');
const saveStepEditBtn = document.getElementById('saveStepEditBtn');
const cancelStepEditBtn = document.getElementById('cancelStepEditBtn');
const closeModalBtn = document.querySelector('.close-modal');

let currentWorkflowData = null;
let workflowIsPaused = false;
let currentStepIndex = 0;
let workflowContext = {};
let currentWorkflowResults = []; // Store full step results globally
let editingStepId = null;

// File Upload Elements
const fileUploadArea = document.getElementById('fileUploadArea');
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview'); // Still container
const uploadPlaceholder = fileUploadArea.querySelector('.upload-placeholder');
// Need to dynamically manage previews now


// Add highlight styles dynamically
function addHighlightStyles() {
    // Don't add if already exists
    if (document.getElementById('violation-highlight-styles')) return;

    const style = document.createElement('style');
    style.id = 'violation-highlight-styles';
    style.textContent = `
        .violation-highlight {
            background: rgba(255, 165, 0, 0.6);
            padding: 2px 6px;
            border-radius: 3px;
            box-shadow: 0 0 10px rgba(255, 165, 0, 0.8);
        }
        
        @keyframes pulse {
            0%, 100% { 
                background: rgba(255, 165, 0, 0.4);
                box-shadow: 0 0 5px rgba(255, 165, 0, 0.4);
            }
            50% { 
                background: rgba(255, 165, 0, 0.9);
                box-shadow: 0 0 20px rgba(255, 165, 0, 1);
            }
        }
    `;

    document.head.appendChild(style);
}

// Call once when page loads
addHighlightStyles();

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
        sandbag: document.getElementById('openai-sandbag'),
        bias: document.getElementById('openai-bias'),
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
        sandbag: document.getElementById('anthropic-sandbag'),
        bias: document.getElementById('anthropic-bias'),
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
        sandbag: document.getElementById('google-sandbag'),
        bias: document.getElementById('google-bias'),
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
        sandbag: document.getElementById('perplexity-sandbag'),
        bias: document.getElementById('perplexity-bias'),
        card: document.querySelector('.ai-card[data-ai="perplexity"]')
    }
};

// ==================== //
// Event Listeners
// ==================== //
askButton.addEventListener('click', () => handleAskAllAIs());
if (visualizeBtn) {
    visualizeBtn.addEventListener('click', () => handleAskAllAIs(true));
}
citationToggle.addEventListener('change', handleCitationToggle);
thoughtToggle.addEventListener('change', handleThoughtToggle);

questionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        handleAskAllAIs();
    }
});

// Role recommendation debounce
let recTimeout;
questionInput.addEventListener('input', () => {
    if (!councilToggle.checked) return;
    clearTimeout(recTimeout);
    recTimeout = setTimeout(checkForRecommendations, 1000);
});

councilToggle.addEventListener('change', () => {
    if (councilToggle.checked) {
        checkForRecommendations();
        document.getElementById('roleSelectors').classList.remove('hidden');
    } else {
        document.getElementById('roleSelectors').classList.add('hidden');
        document.getElementById('roleRecommendation').classList.add('hidden');
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
        handleFileSelect(e.dataTransfer.files);
    }
});

// Global Paste Support (Screenshots)
document.addEventListener('paste', (e) => {
    const items = (e.clipboardData || window.clipboardData).items;
    const files = [];
    if (items) {
        for (let i = 0; i < items.length; i++) {
            if (items[i].kind === 'file') {
                const file = items[i].getAsFile();
                if (file) files.push(file);
            }
        }
    }
    if (files.length > 0) {
        handleFileSelect(files);
        e.preventDefault(); // Stop image binary from pasting into textarea
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleFileSelect(e.target.files);
    }
});

// Camera Input Logic
if (cameraBtn) {
    cameraBtn.addEventListener('click', () => cameraInput.click());
}

if (cameraInput) {
    cameraInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileSelect(e.target.files);
        }
    });
}

// Image Compression Helper
async function compressImage(file) {
    // Only compress images
    if (!file.type.startsWith('image/')) return file;

    // Skip small images (< 1MB)
    if (file.size < 1024 * 1024) return file;

    console.log(`📸 Compressing image: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);

    return new Promise((resolve) => {
        const img = new Image();
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        img.onload = () => {
            const MAX_WIDTH = 1200;
            const MAX_HEIGHT = 1200;
            let width = img.width;
            let height = img.height;

            if (width > height) {
                if (width > MAX_WIDTH) {
                    height *= MAX_WIDTH / width;
                    width = MAX_WIDTH;
                }
            } else {
                if (height > MAX_HEIGHT) {
                    width *= MAX_HEIGHT / height;
                    height = MAX_HEIGHT;
                }
            }

            canvas.width = width;
            canvas.height = height;
            ctx.drawImage(img, 0, 0, width, height);

            canvas.toBlob((blob) => {
                if (blob) {
                    const newFile = new File([blob], file.name, {
                        type: 'image/jpeg',
                        lastModified: Date.now()
                    });
                    console.log(`✅ Compressed to: ${(newFile.size / 1024 / 1024).toFixed(2)} MB`);
                    resolve(newFile);
                } else {
                    resolve(file); // Fallback
                }
            }, 'image/jpeg', 0.8); // 80% Quality
        };

        img.onerror = () => resolve(file);
        img.src = URL.createObjectURL(file);
    });
}

async function handleFileSelect(files) {
    if (!files || files.length === 0) return;

    // Show loading indicator for compression
    const uploadPlaceholder = document.querySelector('.upload-placeholder');
    if (uploadPlaceholder) uploadPlaceholder.textContent = 'Compressing...';

    // Add new files to our array
    for (let i = 0; i < files.length; i++) {
        try {
            const processedFile = await compressImage(files[i]);
            selectedFiles.push(processedFile);
        } catch (e) {
            console.error('Compression failed, using original', e);
            selectedFiles.push(files[i]);
        }
    }

    if (uploadPlaceholder) uploadPlaceholder.textContent = 'Drag & Drop files here or Click to Upload';
    updateFilePreview();
}

function updateFilePreview() {
    //Clear existing previews
    filePreview.innerHTML = '';

    if (selectedFiles.length === 0) {
        filePreview.classList.add('hidden');
        uploadPlaceholder.classList.remove('hidden');
        fileInput.value = ''; // Reset input to allow re-selecting same file
        return;
    }

    uploadPlaceholder.classList.add('hidden');
    filePreview.classList.remove('hidden');

    selectedFiles.forEach((file, index) => {
        const tag = document.createElement('div');
        tag.className = 'file-tag';
        tag.innerHTML = `
            <span class="file-name">${file.name}</span>
            <button class="remove-file" data-index="${index}">Ã—</button>
        `;

        tag.querySelector('.remove-file').addEventListener('click', (e) => {
            e.stopPropagation();
            removeFile(index);
        });

        filePreview.appendChild(tag);
    });
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFilePreview();
}

// Copy buttons
document.querySelectorAll('.copy-button').forEach(button => {
    button.addEventListener('click', handleCopyResponse);
});

const activeModels = new Set(['openai', 'anthropic', 'google', 'perplexity']);
document.querySelectorAll('.model-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
        const model = btn.dataset.model;
        if (activeModels.has(model)) {
            activeModels.delete(model);
            btn.classList.remove('active');
        } else {
            activeModels.add(model);
            btn.classList.add('active');
        }
    });
});

// Clear Deck Logic (Reset All)
const clearDeckBtn = document.getElementById('clearDeckBtn');
if (clearDeckBtn) {
    clearDeckBtn.addEventListener('click', () => {
        // 1. Clear Input
        if (questionInput) questionInput.value = '';

        // 2. Reset Consensus
        if (consensusSection) consensusSection.classList.add('hidden');
        if (consensusContent) consensusContent.innerHTML = 'Loading analysis...';

        // 3. Reset AI Cards (Response text & Status)
        ['openai', 'anthropic', 'google', 'perplexity'].forEach(ai => {
            const responseDiv = document.getElementById(`${ai}-response`);
            const statusDiv = document.getElementById(`${ai}-status`);
            const thoughtsDiv = document.getElementById(`${ai}-thought`);

            // Text Reset
            if (responseDiv) responseDiv.innerHTML = 'Waiting for response...';
            if (statusDiv) statusDiv.innerHTML = '';

            // Hide Thoughts
            if (thoughtsDiv) thoughtsDiv.classList.add('hidden');

            // Remove Violation/Sandbag Badges
            document.getElementById(`${ai}-sandbag`)?.classList.add('hidden');
            document.getElementById(`${ai}-bias`)?.classList.add('hidden');

            // REMOVE DYNAMIC VIOLATIONS (The Red Boxes)
            // They are usually appended to the .ai-response container or .ai-card
            const card = document.querySelector(`.ai-card[data-ai="${ai}"]`);
            if (card) {
                // Remove specific enforcement elements
                card.querySelectorAll('.violation-report').forEach(el => el.remove());
                card.querySelectorAll('.enforcement-report').forEach(el => el.remove());
                card.querySelectorAll('.penalty-box').forEach(el => el.remove());
                card.querySelectorAll('.interrogation-overlay').forEach(el => el.remove());

                // Clear any inline styles relating to warnings
                card.style.border = '';
                card.style.boxShadow = '';
            }
        });

        // 4. Hide Loading State
        if (loadingState) loadingState.classList.add('hidden');
        stopStatusRotation();

        console.log('Deck cleared: Violations removed.');
    });
}


// Recommendation Listeners
document.getElementById('useRecommendedBtn').addEventListener('click', applyRecommendation);
document.getElementById('customizeRolesBtn').addEventListener('click', () => {
    document.getElementById('roleRecommendation').classList.add('hidden');
});

async function checkForRecommendations() {
    const question = questionInput.value.trim();
    if (question.length < 10 || !councilToggle.checked) return;

    try {
        const response = await fetch('/api/recommend_roles', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        const data = await response.json();

        if (data.exists) {
            showRecommendation(data);
        } else {
            document.getElementById('roleRecommendation').classList.add('hidden');
        }
    } catch (err) {
        console.error('Recommendation Error:', err);
    }
}

function showRecommendation(data) {
    const recBox = document.getElementById('roleRecommendation');
    const categorySpan = document.getElementById('detectedCategory');
    const list = document.getElementById('recommendedRolesList');
    const rating = document.getElementById('recRating');

    categorySpan.textContent = data.category;
    rating.textContent = data.recommendation.avg_rating.toFixed(1) + '/4.0';

    list.innerHTML = `
        <li>✓ GPT: ${data.recommendation.gpt_role}</li>
        <li>✓ Claude: ${data.recommendation.claude_role}</li>
        <li>✓ Gemini: ${data.recommendation.gemini_role}</li>
        <li>✓ Perplexity: ${data.recommendation.perplexity_role}</li>
    `;

    // Store for application
    recBox.dataset.gpt = data.recommendation.gpt_role;
    recBox.dataset.claude = data.recommendation.claude_role;
    recBox.dataset.gemini = data.recommendation.gemini_role;
    recBox.dataset.perplexity = data.recommendation.perplexity_role;

    recBox.classList.remove('hidden');
}

function applyRecommendation() {
    const recBox = document.getElementById('roleRecommendation');

    document.getElementById('roleOpenAI').value = recBox.dataset.gpt;
    document.getElementById('roleAnthropic').value = recBox.dataset.claude;
    document.getElementById('roleGoogle').value = recBox.dataset.gemini;
    document.getElementById('rolePerplexity').value = recBox.dataset.perplexity;

    recBox.classList.add('hidden');

    // Add a little glow effect to show they changed
    document.querySelectorAll('.role-dropdown').forEach(d => {
        d.style.boxShadow = '0 0 15px var(--accent-gold)';
        setTimeout(() => d.style.boxShadow = '', 1000);
    });
}

// Card Rating Logic
document.querySelectorAll('.card-rate-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const ratingDiv = btn.closest('.card-rating');
        const aiProvider = ratingDiv.dataset.ai;
        const isUp = btn.classList.contains('up');
        const rating = isUp ? 1 : -1;

        // Toggle Active Stats
        ratingDiv.querySelectorAll('.card-rate-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        submitResponseRating(aiProvider, rating);
    });
});

async function submitResponseRating(aiProvider, rating) {
    if (!currentComparisonId) return;

    try {
        await fetch('/api/feedback/response', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                comparison_id: currentComparisonId,
                ai_provider: aiProvider,
                rating: rating
            })
        });
    } catch (err) {
        console.error('Error submitting response rating:', err);
    }
}

// Feedback Logic
// ==================== //
document.querySelectorAll('.rating-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.rating-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const rating = parseInt(btn.dataset.rating);

        // Always show comment area and submit button after a rating is picked
        document.querySelector('.feedback-comment').classList.remove('hidden');
        document.getElementById('submitFeedbackBtn').classList.remove('hidden');

        if (rating < 3) {
            // Low rating: specifically show issue checkboxes
            document.querySelector('.feedback-issues').classList.remove('hidden');
        } else {
            // High rating: hide specific issue checkboxes to keep it clean, but keep comment box
            document.querySelector('.feedback-issues').classList.add('hidden');
        }
    });
});

document.getElementById('submitFeedbackBtn').addEventListener('click', submitFeedback);

async function submitFeedback() {
    const activeRating = document.querySelector('.rating-btn.active');
    if (!activeRating) {
        alert('Please select a rating first!');
        return;
    }

    const rating = activeRating.dataset.rating;
    const feedbackText = document.getElementById('feedbackText').value;
    const too_generic = document.querySelector('input[name="too_generic"]').checked;
    const hallucinated = document.querySelector('input[name="hallucinated"]').checked;
    const mandate_fail = document.querySelector('input[name="mandate_fail"]').checked;
    const cushioning_present = document.querySelector('input[name="cushioning_present"]').checked;
    const visual_mismatch = document.querySelector('input[name="visual_mismatch"]').checked;
    const missing_details = document.querySelector('input[name="missing_details"]').checked;
    const wrong_roles = document.querySelector('input[name="wrong_roles"]').checked;
    const didnt_answer = document.querySelector('input[name="didnt_answer"]').checked;

    const payload = {
        comparison_id: currentComparisonId,
        rating: parseInt(rating),
        feedback_text: feedbackText,
        too_generic,
        hallucinated,
        mandate_fail,
        cushioning_present,
        visual_mismatch,
        missing_details,
        wrong_roles,
        didnt_answer,
        // Optional: Send roles too
        gpt_role: document.getElementById('roleOpenAI')?.value,
        claude_role: document.getElementById('roleAnthropic')?.value,
        gemini_role: document.getElementById('roleGoogle')?.value,
        perplexity_role: document.getElementById('rolePerplexity')?.value,
        query_text: questionInput.value
    };

    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            document.getElementById('submitFeedbackBtn').classList.add('hidden');
            document.querySelector('.rating-options').style.pointerEvents = 'none';
            document.querySelector('.feedback-issues').style.pointerEvents = 'none';
            document.querySelector('.feedback-comment').style.pointerEvents = 'none';
            document.getElementById('feedbackThanks').classList.remove('hidden');
        } else {
            alert('Failed to submit feedback');
        }
    } catch (err) {
        console.error('Feedback error:', err);
        alert('Submission error');
    }
}

// ==================== //
// Main Function
// ==================== //
async function handleAskAllAIs(forcedVisualize = false) {
    let question = questionInput.value.trim();

    if (forcedVisualize && !question.toLowerCase().includes('visual')) {
        question += " [Please generate a visual mockup/diagram for this query]";
    }

    if (!question) {
        alert('Please enter a question first!');
        return;
    }

    if (activeModels.size === 0) {
        alert('Please select at least one AI model!');
        return;
    }

    if (isQuerying) {
        return;
    }

    if (workflowToggle && workflowToggle.checked) {
        runWorkflowMode();
        return;
    }

    // Update UI state
    isQuerying = true;
    askButton.disabled = true;
    askButton.querySelector('.button-text').textContent = 'Querying...';
    loadingState.classList.remove('hidden');
    startStatusRotation();
    resultsSection.classList.add('hidden');
    consensusSection.classList.add('hidden');

    // Reset all responses
    resetResponses();

    // Video State: High Energy
    const bgVideo = document.getElementById('bgVideo');
    const processingVideo = document.getElementById('processingVideo');

    if (bgVideo && processingVideo) {
        bgVideo.classList.remove('active');
        processingVideo.classList.add('active');
        processingVideo.play(); // Ensure it plays
    }

    try {
        let response;

        // Check if we need to send a file
        if (selectedFiles.length > 0) {
            const formData = new FormData();
            formData.append('question', question);
            formData.append('use_vault', vaultToggle.checked);
            formData.append('podcast_mode', podcastToggle ? podcastToggle.checked : false);
            formData.append('council_mode', councilToggle ? councilToggle.checked : false);
            formData.append('hard_mode', hardModeToggle ? hardModeToggle.checked : false);
            formData.append('active_models', JSON.stringify(Array.from(activeModels)));

            // Append all files
            selectedFiles.forEach(file => {
                formData.append('files', file);
            });

            if (currentProjectName) {
                formData.append('project_name', currentProjectName);
            }

            // Add council roles if council mode is enabled
            if (councilToggle && councilToggle.checked) {
                const roles = getCouncilRoles();
                formData.append('council_roles', JSON.stringify(roles));
            }

            response = await fetch('/api/ask', {
                method: 'POST',
                body: formData // No Content-Type header needed, browser sets boundary
            });

            // Clear files after successful send (optional, but good UX)
            selectedFiles = [];
            updateFilePreview();

        } else {
            // Standard JSON request
            const payload = {
                question,
                use_vault: vaultToggle.checked,
                podcast_mode: podcastToggle ? podcastToggle.checked : false,
                council_mode: councilToggle ? councilToggle.checked : false,
                hard_mode: hardModeToggle ? hardModeToggle.checked : false,
                active_models: Array.from(activeModels),
                forced_visualize: forcedVisualize
            };
            if (currentProjectName) {
                payload.project_name = currentProjectName;
            }
            // Add council roles and visual profiles if council mode is enabled
            if (councilToggle && councilToggle.checked) {
                payload.council_roles = getCouncilRoles();
            }

            response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
        }

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || 'API request failed');
        }

        const data = await response.json();

        // Update UI with responses using the "results" key
        const results = data.results;

        // Hide/Show cards based on selection
        Object.keys(responses).forEach(key => {
            const card = responses[key].card;
            if (activeModels.has(key)) {
                card.style.display = 'flex';
                if (results[key]) updateResponse(key, results[key]);
            } else {
                card.style.display = 'none';
            }
        });

        // Show Consensus
        if (data.consensus) {
            consensusContent.innerHTML = formatMarkdown(data.consensus);
            consensusSection.classList.remove('hidden');
        }

        // Show results
        loadingState.classList.add('hidden');
        resultsSection.classList.remove('hidden');

        // Store comparison ID for feedback
        currentComparisonId = data.comparison_id;

        // Reset and Show Feedback Square
        resetFeedbackUI();
        if (currentComparisonId) {
            document.getElementById('feedbackSquare').classList.remove('hidden');
        }

        // Apply toggle states
        handleCitationToggle();
        handleThoughtToggle();

        // Initialize Mermaid
        mermaid.initialize({
            startOnLoad: false,
            theme: 'base',
            themeVariables: {
                primaryColor: '#1a1a1a',
                primaryTextColor: '#e5e5e5',
                primaryBorderColor: '#ffd700',
                lineColor: '#a3a3a3',
                secondaryColor: '#2a2a2a',
                tertiaryColor: '#1a1a1a'
            }
        });
        await mermaid.run();

    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
        loadingState.classList.add('hidden');
    } finally {
        // Reset UI state
        stopStatusRotation();
        isQuerying = false;
        askButton.disabled = false;
        askButton.querySelector('.button-text').textContent = 'Ask All AIs';

        // Video State: Return to Calm
        if (bgVideo && processingVideo) {
            processingVideo.classList.remove('active');
            setTimeout(() => processingVideo.pause(), 1500); // Pause after fade out to save resources
            bgVideo.classList.add('active');
        }
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
        if (responses[aiName].sandbag) responses[aiName].sandbag.classList.add('hidden');
        if (responses[aiName].bias) responses[aiName].bias.classList.add('hidden');

        // Clear any previous interrogation results
        const oldInterrogation = responses[aiName].card.querySelector('.interrogation-outcome');
        if (oldInterrogation) {
            oldInterrogation.remove();
        }

        // Reset card ratings
        const ratingDiv = responses[aiName].card.querySelector('.card-rating');
        if (ratingDiv) {
            ratingDiv.querySelectorAll('.card-rate-btn').forEach(b => b.classList.remove('active'));
        }
    });
}

function resetFeedbackUI() {
    document.getElementById('feedbackSquare').classList.add('hidden');
    document.getElementById('feedbackThanks').classList.add('hidden');
    document.getElementById('submitFeedbackBtn').classList.add('hidden'); // Hidden until low rating
    document.querySelector('.rating-options').classList.remove('hidden');
    document.querySelector('.feedback-issues').classList.add('hidden'); // Hidden until low rating
    document.querySelector('.feedback-comment').classList.add('hidden'); // Hidden until low rating
    document.querySelectorAll('.rating-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.feedback-issues input').forEach(i => i.checked = false);
    document.getElementById('feedbackText').value = '';

    // Restore pointer events
    document.querySelector('.rating-options').style.pointerEvents = 'auto';
    document.querySelector('.feedback-issues').style.pointerEvents = 'auto';
    document.querySelector('.feedback-comment').style.pointerEvents = 'auto';
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
        elements.status.textContent = 'âœ“ Success';
        elements.status.classList.add('success');
        elements.status.classList.remove('error');
    } else {
        elements.response.textContent = data.response;
        elements.response.classList.add('error');
        elements.status.textContent = 'âœ— Error';
        elements.status.classList.add('error');
        elements.status.classList.remove('success');
    }

    // Add Interrogate Button if successful
    if (data.success) {
        let actionsArea = elements.card.querySelector('.ai-meta');
        if (!actionsArea.querySelector('.interrogate-btn')) {
            const intBtn = document.createElement('button');
            intBtn.className = 'interrogate-btn';
            intBtn.innerHTML = `<span>🔍 Interrogate</span>`;
            // Use card-based interrogation, not drawer
            intBtn.onclick = async () => {
                // Use aiName directly from closure - guaranteed to be correct
                const modelName = aiName;
                console.log('🔵 Interrogate button clicked. Model (from closure):', modelName);

                const userQ = prompt("Enter your interrogation question:", "Is this claim accurate?");
                if (!userQ) return;

                // Call the card-based interrogation function
                await triggerCardInterrogation(modelName, data.response, userQ);
            };
            actionsArea.insertBefore(intBtn, actionsArea.firstChild);
        }
    }

    // Sandbagging Detection logic
    if (data.thought && data.response && data.success) {
        const thoughtLen = data.thought.length;
        const responseLen = data.response.length;

        // Remove existing classes first
        if (elements.sandbag) {
            elements.sandbag.classList.add('hidden');
            elements.sandbag.classList.remove('sandbag-warning', 'sandbag-critical');
        }

        // CRITICAL (Red): Generic/Refusal/Safety-heavy
        // Detected via 'narrative' bias OR extreme thought ratio (> 3.0) OR specific keywords
        const isGeneric = data.execution_bias === 'narrative' ||
            responseLen < 200 ||
            (responseLen > 0 && thoughtLen > responseLen * 3.0);

        // WARNING (Yellow): High Thought-to-Output ratio (Imbalance)
        // Detected via thought ratio (> 1.6)
        const isImbalanced = thoughtLen > responseLen * 1.6;

        if (elements.sandbag) {
            if (isGeneric) {
                elements.sandbag.textContent = '🚨 GENERIC / REFUSAL';
                elements.sandbag.classList.add('sandbag-critical'); // Red
                elements.sandbag.classList.remove('hidden');
            } else if (isImbalanced) {
                elements.sandbag.textContent = '⚠️ THOUGHT IMBALANCE';
                elements.sandbag.classList.add('sandbag-warning'); // Yellow
                elements.sandbag.classList.remove('hidden');
            }
        }
    }

    // Execution Bias Indicator
    if (data.execution_bias && elements.bias) {
        const bias = data.execution_bias;
        elements.bias.classList.remove('hidden', 'action-forward', 'advisory', 'narrative');
        elements.bias.classList.add(bias);

        // Formatted Label
        const labels = {
            'action-forward': '🟢 Action-Forward',
            'advisory': '🟡 Advisory',
            'narrative': '🔴 Narrative / Caution'
        };
        elements.bias.textContent = labels[bias] || bias;

        // Add descriptive tooltips
        const tooltips = {
            'action-forward': 'Direct execution protocol. High density, no hedging, specific numerical thresholds.',
            'advisory': 'Consultative approach. Provides options and frameworks with moderate hedging.',
            'narrative': 'High alignment tax. Verbose, caution-heavy, or refusal-adjacent output.'
        };
        elements.bias.title = tooltips[bias] || '';
    } else if (elements.bias) {
        elements.bias.classList.add('hidden');
    }

    // Enforcement Report Rendering
    if (data.enforcement && Object.keys(data.enforcement).length > 0) {
        renderEnforcementReport(elements.card, data.enforcement, aiName);
    } else {
        const existingReport = elements.card.querySelector('.enforcement-report');
        if (existingReport) existingReport.remove();
        const badge = elements.card.querySelector('.credibility-badge');
        if (badge) badge.remove();
    }
}

function renderEnforcementReport(card, enforcement, aiName) {
    // 1. Render Badge in Header
    const headerInfo = card.querySelector('.ai-info');
    if (!headerInfo) return;

    let badge = card.querySelector('.credibility-badge');
    if (!badge) {
        badge = document.createElement('span');
        badge.className = 'credibility-badge';
        headerInfo.appendChild(badge);
    }

    // Determine badge class
    const score = enforcement.current_credibility !== undefined ? enforcement.current_credibility : 100;
    let scoreClass = 'high';
    if (score < 70) scoreClass = 'low';
    else if (score < 90) scoreClass = 'medium';

    badge.className = `credibility-badge ${scoreClass}`;
    badge.textContent = `Truth Score: ${score}/100`;

    // 2. Render Report Body
    const responseDiv = card.querySelector('.ai-response');

    let reportDiv = card.querySelector('.enforcement-report');
    if (!reportDiv) {
        reportDiv = document.createElement('div');
        reportDiv.className = 'enforcement-report';
        // Insert before response
        if (responseDiv) card.insertBefore(reportDiv, responseDiv);
        else card.appendChild(reportDiv);
    }

    // Clean Pass?
    if (enforcement.status === 'PASSED') {
        reportDiv.className = 'enforcement-report clean';
        reportDiv.innerHTML = `
            <div class="enforcement-passed">
                Strict Adherence Verified (+0 Penalty)
            </div>
        `;
        return;
    }

    // Violation/Warning List
    reportDiv.className = 'enforcement-report'; // reset

    // CLICKABLE HEADER LINK
    let html = `<div class="enforcement-header clickable-header" onclick="scrollToFirstViolation(this, '${aiName}')" title="Jump to first violation evidence" style="cursor: pointer; display: flex; justify-content: space-between;">
                    <span>⚠️ Protocol Variance Detected</span>
                    <span style="opacity: 0.6; font-size: 0.9em;">🔗</span>
                </div>`;
    html += `<ul class="violation-list">`;

    if (enforcement.violations) {
        enforcement.violations.forEach(v => {
            html += `<li class="violation-item" data-ai="${aiName}" title="Click to find in verification">${v}</li>`;
        });
    }

    if (enforcement.warnings) {
        enforcement.warnings.forEach(w => {
            html += `<li class="warning-item">${w}</li>`;
        });
    }

    html += `</ul>`;
    reportDiv.innerHTML = html;

    // 3. INJECT INLINE BADGES (The new feature)
    if (enforcement.violations) {
        injectInlineBadges(card, enforcement.violations, aiName);
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
// ==================== //
// Formatting
// ==================== //
function formatMarkdown(text) {
    if (!text) return '';

    const placeholders = [];

    // Helper to store code blocks
    function store(content) {
        const id = `__PLACEHOLDER_${placeholders.length}__`;
        placeholders.push(content);
        return id;
    }

    // 1. Extract Mermaid Blocks (Preserve newlines)
    text = text.replace(/```mermaid\n([\s\S]*?)\n```/g, (match, code) => {
        return store(`<div class="mermaid">${code}</div>`);
    });

    // 2. Extract Standard Code Blocks & Renderable
    text = text.replace(/```(xml|svg|html)\n([\s\S]*?)\n```/g, (match, lang, code) => {
        const id = 'code-' + Math.random().toString(36).substr(2, 9);
        const encodedCode = encodeURIComponent(code);
        const btn = `<button class="render-btn" onclick="renderCode('${id}', '${lang}', '${encodedCode}')">â–¶ Render Preview</button>`;
        const html = `<pre><code class="language-${lang}">${code.replace(/</g, '&lt;')}</code></pre>
                      ${btn}
                      <div id="${id}" class="preview-box hidden"></div>`;
        return store(html);
    });

    text = text.replace(/```(\w*)\n([\s\S]*?)\n```/g, (match, lang, code) => {
        return store(`<pre><code class="language-${lang}">${code.replace(/</g, '&lt;')}</code></pre>`);
    });

    // 3. Extract Inline Code
    text = text.replace(/`([^`]+)`/g, (match, code) => {
        return store(`<code>${code.replace(/</g, '&lt;')}</code>`);
    });

    // --- Process Standard Text ---

    // 4. Bold / Italic
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // 4.1 Technical Auto-Linking (CVE, GHSA, RFC)
    // CVEs: CVE-YYYY-NNNN
    text = text.replace(/(CVE-\d{4}-\d{4,7})/gi, '<a href="https://nvd.nist.gov/vuln/detail/$1" target="_blank" class="tech-link">$1</a>');

    // GHSA: GHSA-xxxx-xxxx-xxxx
    text = text.replace(/(GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4})/gi, '<a href="https://github.com/advisories/$1" target="_blank" class="tech-link">$1</a>');

    // RFC: RFC NNNN
    text = text.replace(/RFC (\d+)/gi, '<a href="https://datatracker.ietf.org/doc/html/rfc$1" target="_blank" class="tech-link">RFC $1</a>');

    // 4.2 Images (New Support)
    text = text.replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1" style="max-width:100%; border-radius:4px; margin: 10px 0;">');

    // 5. Line breaks (only in non-code text)
    text = text.replace(/\n\n/g, '<br><br>').replace(/\n/g, '<br>');

    // --- Restore Placeholders ---
    placeholders.forEach((content, index) => {
        text = text.replace(`__PLACEHOLDER_${index}__`, content);
    });

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
// Contextual Operations (Highlight Menu)
// ==================== //
document.addEventListener('mouseup', handleTextSelection);
document.addEventListener('mousedown', (e) => {
    // Hide tooltip on click outside
    const tooltip = document.getElementById('selectionTooltip');
    if (tooltip && !tooltip.contains(e.target) && !window.getSelection().toString()) {
        tooltip.classList.add('hidden');
    }
});

function handleTextSelection(e) {
    const selection = window.getSelection();
    const text = selection.toString().trim();
    const tooltip = document.getElementById('selectionTooltip');

    // Only show if text is selected and inside a response container
    if (text.length < 5 || !isInsideResponse(selection.anchorNode)) {
        // Don't auto-hide immediately on mouseup if interacting with tooltip, 
        // but generally hide if selection is cleared.
        return;
    }

    // Create tooltip if not exists
    if (!tooltip) {
        createSelectionTooltip();
        // Re-run to position after creation
        setTimeout(() => handleTextSelection(e), 10);
        return;
    }

    // Position tooltip
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();

    // Position above selection
    tooltip.style.top = `${rect.top + window.scrollY - 60}px`;
    tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
    tooltip.classList.remove('hidden');

    // Store selection for actions
    tooltip.dataset.selectedText = text;

    // Identify provider (openai, anthropic, etc)
    const provider = getProviderFromNode(selection.anchorNode);
    if (provider) tooltip.dataset.provider = provider;
}

function isInsideResponse(node) {
    if (!node || node === document) return false;
    if (node.nodeType === Node.ELEMENT_NODE && node.id && node.id.includes('-response')) return true;
    return isInsideResponse(node.parentNode);
}

function getProviderFromNode(node) {
    if (!node || node === document) return null;
    if (node.nodeType === Node.ELEMENT_NODE && node.id && node.id.includes('-response')) {
        return node.id.split('-')[0]; // e.g., 'openai-response' -> 'openai'
    }
    return getProviderFromNode(node.parentNode);
}

function createSelectionTooltip() {
    // Inject CSS
    const style = document.createElement('style');
    style.textContent = `
        .selection-tooltip {
            position: absolute;
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid var(--accent-gold);
            border-radius: 8px;
            padding: 8px;
            display: flex;
            gap: 8px;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            backdrop-filter: blur(10px);
            transition: opacity 0.2s;
        }
        .selection-tooltip.hidden {
            display: none;
        }
        .tooltip-btn {
            background: transparent;
            border: 1px solid rgba(255,255,255,0.2);
            color: #fff;
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .tooltip-btn:hover {
            background: rgba(255, 215, 0, 0.1);
            border-color: var(--accent-gold);
            color: var(--accent-gold);
        }
    `;
    document.head.appendChild(style);

    const div = document.createElement('div');
    div.id = 'selectionTooltip';
    div.className = 'selection-tooltip hidden';
    div.innerHTML = `
        <button class="tooltip-btn" id="btnVizArt" title="Realistic Render">
            <span>🖼️</span>
        </button>
        <button class="tooltip-btn" id="btnVizBlue" title="Technical Blueprint">
            <span>📐</span>
        </button>
        <button class="tooltip-btn" id="btnVizChart" title="Data Chart">
            <span>📊</span>
        </button>
        <button class="tooltip-btn" id="btnInterrogateSelect" title="Forensic Interrogation">
            <span>🔍 Interrogate</span>
        </button>
    `;
    document.body.appendChild(div);

    // Context Helpers
    const runViz = (profile) => {
        triggerContextVisual(div.dataset.selectedText, div.dataset.provider, profile);
        div.classList.add('hidden');
        window.getSelection().removeAllRanges();
    };

    // Event Listeners
    document.getElementById('btnVizArt').addEventListener('click', (e) => { e.stopPropagation(); runViz('realistic'); });
    document.getElementById('btnVizBlue').addEventListener('click', (e) => { e.stopPropagation(); runViz('blueprint'); });
    document.getElementById('btnVizChart').addEventListener('click', (e) => { e.stopPropagation(); runViz('data-viz'); });

    document.getElementById('btnInterrogateSelect').addEventListener('click', (e) => {
        e.stopPropagation();
        triggerContextInterrogate(div.dataset.selectedText, div.dataset.provider);
        div.classList.add('hidden');
        window.getSelection().removeAllRanges();
    });
}

async function triggerContextVisual(text, provider, profile = 'realistic') {
    if (!text || !provider) return;

    // Reuse existing visual logic but with explicit text
    const btn = document.querySelector(`.visualize-btn[data-target="${provider}"]`);
    const originalContent = btn ? btn.innerHTML : '';
    if (btn) btn.innerHTML = '⏳';

    try {
        const response = await fetch('/visualize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                comparison_id: currentComparisonId,
                provider: provider,
                selected_text: text, // The Magic Override
                visual_profile: profile
            })
        });

        const data = await response.json();
        if (btn) btn.innerHTML = originalContent;

        if (data.chart_url) {
            showChartModal(data.chart_url, provider);
        } else if (data.error) {
            alert(data.error);
        }
    } catch (e) {
        console.error(e);
        if (btn) btn.innerHTML = originalContent;
    }
}

// Card-based interrogation (shows results in AI card)
async function triggerCardInterrogation(modelName, responseText, question) {
    if (!modelName || !question) return;

    console.log('🎯 triggerCardInterrogation called with:', { modelName, question });

    const elements = responses[modelName];
    if (!elements) {
        console.error('No elements found for model:', modelName);
        return;
    }

    // Show loading state
    loadingState.classList.remove('hidden');
    const statusText = document.getElementById('loadingStatusText');
    const originalStatus = statusText ? statusText.textContent : 'Querying...';
    if (statusText) statusText.textContent = "🕵️ Interrogating Suspect...";

    //Find and add spinner to button
    const activeBtn = elements.card.querySelector('.interrogate-btn');
    if (activeBtn) {
        console.log('✅ Interrogate button found, adding spinner');
        activeBtn.classList.add('loading');
    }

    try {
        const payload = {
            model: modelName,
            question: question,
            previous_response: responseText
        };

        const response = await fetch('/interrogate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        loadingState.classList.add('hidden');
        if (statusText) statusText.textContent = originalStatus;
        if (activeBtn) activeBtn.classList.remove('loading');

        if (data.success) {
            console.log('📊 Interrogation Success');
            console.log('🔍 Calling displayInterrogationResult with modelName:', modelName);
            displayInterrogationResult(modelName, data, question);
        } else {
            alert(`Interrogation refused: ${data.response || data.error || 'Unknown Reason'}`);
        }
    } catch (e) {
        loadingState.classList.add('hidden');
        if (statusText) statusText.textContent = originalStatus;
        if (activeBtn) activeBtn.classList.remove('loading');
        alert(`Interrogation crashed: ${e.message}`);
        console.error(e);
    }
}

async function triggerContextInterrogate(text, provider) {
    if (!text || !provider) return;

    // Open modal directly with pre-filled context
    // We can reuse openInterrogation logic but pass specific claim

    // Prompt User for specific question about this claim?
    const userQ = prompt("Interrogate highlight:\n" + text.substring(0, 50) + "...\n\nEnter your specific challenge:", "Is this accurate?");
    if (!userQ) return;

    // Send to backend
    // Finding the card to show loading state
    loadingState.classList.remove('hidden');
    const statusText = document.getElementById('loadingStatusText');
    const originalStatus = statusText ? statusText.textContent : 'Querying...';
    if (statusText) statusText.textContent = "🕵️ Interrogating Suspect...";

    // Visual feedback on the card itself
    const elements = responses[provider];
    let activeBtn = null;
    if (elements && elements.card) {
        // Try multiple selectors to find the button
        activeBtn = elements.card.querySelector('.interrogate-btn') ||
            elements.card.querySelector('.interrogate-step-trigger') ||
            Array.from(elements.card.querySelectorAll('button')).find(b => b.innerText.includes('Interrogate'));

        if (activeBtn) {
            console.log('✅ Interrogate button found, adding spinner');
            activeBtn.dataset.originalText = activeBtn.innerText;
            activeBtn.classList.add('loading');
        } else {
            console.warn('⚠️ Interrogate button NOT found in card');
        }
    }

    try {
        const payload = {
            model: provider,
            question: userQ,
            previous_response: responses[provider].response.innerText,
            selected_text: text // The Magic Override
        };

        const response = await fetch('/interrogate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        loadingState.classList.add('hidden');
        if (statusText) statusText.textContent = originalStatus;
        if (activeBtn) {
            activeBtn.classList.remove('loading');
            // activeBtn.innerText = activeBtn.dataset.originalText || "Interrogate"; // Css handles transparency, no need to reset text 
        }

        if (data.success) {
            console.log('📊 Interrogation Success. Question:', userQ);
            console.log('🔍 About to call displayInterrogationResult with provider:', provider);
            // New logic using helper function
            displayInterrogationResult(provider, data, userQ);
        } else {
            alert(`Interrogation refused: ${data.response || data.error || 'Unknown Reason'}`);
        }
    } catch (e) {
        loadingState.classList.add('hidden');
        if (statusText) statusText.textContent = originalStatus;
        if (activeBtn) activeBtn.classList.remove('loading');

        alert(`Interrogation crashed: ${e.message}`);
        console.error(e);
    }
}

function displayInterrogationResult(modelName, result, userQuestion) {
    console.log('📋 displayInterrogationResult called with modelName:', modelName);
    const elements = responses[modelName];
    if (!elements) {
        console.error('❌ No elements found for model:', modelName);
        return;
    }
    const card = elements.card;

    // Update credibility score with animation
    const credibilityBadge = card.querySelector('.credibility-badge');
    if (credibilityBadge) {
        // Parse "Truth Score: 80/100" -> 80
        const currentText = credibilityBadge.textContent || "100";
        const oldScoreMatch = currentText.match(/(\d+)\/100/);
        const oldScore = oldScoreMatch ? parseInt(oldScoreMatch[1]) : 100;
        const newScore = result.new_credibility !== undefined ? result.new_credibility : oldScore;

        // Animate the number change
        animateScoreChange(credibilityBadge, oldScore, newScore);

        // Update class based on new score
        let scoreClass = 'high';
        if (newScore < 70) scoreClass = 'low';
        else if (newScore < 90) scoreClass = 'medium';
        credibilityBadge.className = `credibility-badge ${scoreClass}`;

        // Show change indicator if there's a change
        // We look at credibility_change from backend (negative usually)
        const changeVal = result.credibility_change || 0;
        if (changeVal !== 0) {
            const changeSpan = document.createElement('span');
            changeSpan.className = 'credibility-change';
            changeSpan.style.marginLeft = '8px';
            changeSpan.style.fontWeight = 'bold';
            changeSpan.textContent = changeVal >= 0 ? `▲ +${changeVal}` : `▼ ${changeVal}`;
            changeSpan.style.color = changeVal >= 0 ? '#10b981' : '#ef4444';

            // Remove old change span if exists
            const oldSpan = credibilityBadge.querySelector('.credibility-change');
            if (oldSpan) oldSpan.remove();

            credibilityBadge.appendChild(changeSpan);
        }
    }

    // Add outcome badge/card
    const outcomeDiv = document.createElement('div');
    // Using user provided classes
    outcomeDiv.className = `interrogation-outcome ${result.outcome ? result.outcome.toLowerCase() : 'unknown'}`;
    outcomeDiv.style.border = '1px solid var(--border-color)';
    outcomeDiv.style.marginTop = '15px';
    outcomeDiv.style.padding = '12px';
    outcomeDiv.style.borderRadius = '6px';
    outcomeDiv.style.background = 'rgba(0,0,0,0.2)';

    const outcomeColor = result.outcome === 'DEFENDED' ? '#10b981' : '#ef4444';

    outcomeDiv.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:8px;">
            <div>
                <strong style="color:${outcomeColor}; text-transform:uppercase; font-size:1.1em;">${result.outcome}</strong>
                <div style="font-size:0.8em; opacity:0.7;">${result.classification}</div>
            </div>
            <div style="text-align:right;">
                 ${result.credibility_change > 0 ?
            `<span style="color:#10b981; font-weight:bold;">SCORE INCREASED (+${result.credibility_change})</span>` :
            `<span style="color:#ef4444; font-weight:bold;">PENALTY APPLIED (${result.credibility_change})</span>`}
            </div>
        </div>

        <div style="margin-bottom:15px;">
            <div style="font-size:0.75em; color:var(--accent-gold); text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">PROSECUTION QUERY</div>
            <div style="font-style:italic; background:rgba(0,0,0,0.3); padding:8px; border-radius:4px; border-left:2px solid var(--accent-gold);">
                "${userQuestion || 'Verification of claim'}"
            </div>
        </div>

        <div style="margin-bottom:10px;">
            <div style="font-size:0.75em; color:${outcomeColor}; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">SUSPECT TESTIMONY</div>
            <div class="interrogation-defense-text" style="font-size:0.95em; border-left: 2px solid ${outcomeColor}; padding-left:12px; background:rgba(255,255,255,0.03);">
                ${formatMarkdown(result.defense || '')}
            </div>
        </div>

        ${result.violations && result.violations.length > 0 ? `
            <details open>
                <summary style="cursor:pointer; color:#ef4444; font-weight:bold;">🛑 Violations Detected (${result.violations.length})</summary>
                ${console.log('📝 Rendering violations for model:', modelName) || ''}
                <ul style="margin-top:5px; padding-left:20px; font-size:0.9em; color:#ffaaaa;">
                    ${result.violations.map(v => `<li class="violation-item" data-ai="${modelName}" title="Click to locate in text">${v}</li>`).join('')}
                </ul>
            </details>
        ` : ''}
    `;

    // Insert into card - append after the response element
    const responseElement = elements.response;
    if (responseElement && responseElement.parentElement) {
        // Insert after the response's parent container
        responseElement.parentElement.appendChild(outcomeDiv);
        // Scroll to it
        outcomeDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
        // Fallback: append to card directly
        card.appendChild(outcomeDiv);
        outcomeDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Check if we need to warn about consensus
    checkConsensusHealth();
}

// Helper to extract violation text from violation element
function extractViolationText(violationElement) {
    // The violation item contains text like:
    // "UNANCHORED_METRIC: '25%' found without visible justification"

    const text = violationElement.textContent;

    // Extract the quoted text
    const match = text.match(/'([^']+)'/);
    if (match) {
        return match[1]; // Returns "25%"
    }

    // Fallback: try to find any number
    const numberMatch = text.match(/\d+%|\$[\d,]+|\d+/);
    if (numberMatch) {
        return numberMatch[0];
    }

    return null;
}

window.scrollToContext = function (violationElement, modelName) {
    console.log('🎯 scrollToContext called with:', modelName);

    // 1. Find the AI's response card
    const aiCard = document.querySelector(`.ai-card[data-ai="${modelName}"]`);
    if (!aiCard) {
        console.error('AI card not found for:', modelName);
        return;
    }

    // 2. Get the violation text (the actual number/text to find)
    const violationText = extractViolationText(violationElement);
    if (!violationText) {
        console.error('Could not extract violation text');
        return;
    }

    console.log('Searching for:', violationText);

    // 3. Find the response text container
    const responseText = aiCard.querySelector(`#${modelName}-response`);

    if (!responseText) {
        console.error('Response text container not found');
        return;
    }

    // 4. Search for the text and highlight it
    const originalHtml = responseText.innerHTML;
    const escapedText = violationText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escapedText})`, 'gi');

    // Check if text exists
    if (!regex.test(originalHtml)) {
        console.warn(`Text "${violationText}" not found in response`);
        // Still scroll to the card so user knows which AI
        aiCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
    }

    // 5. Highlight the text
    responseText.innerHTML = originalHtml.replace(
        regex,
        '<mark class="violation-highlight" id="current-violation" style="background: rgba(255,215,0,0.6); padding: 4px; border: 2px solid #FFD700; border-radius: 4px;">$1</mark>'
    );

    // 6. Scroll to the highlighted text
    const highlighted = responseText.querySelector('#current-violation');
    if (highlighted) {
        highlighted.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // 7. Remove highlight after 5 seconds
    setTimeout(() => {
        responseText.innerHTML = originalHtml;
    }, 5000);
};

// Event delegation for violation clicks
document.addEventListener('click', function (e) {
    const violationItem = e.target.closest('.violation-item');
    if (violationItem) {
        const modelName = violationItem.dataset.ai; // Changed from dataset.model
        console.log('🔍 Violation clicked via event listener. Model:', modelName);
        if (modelName) {
            scrollToContext(violationItem, modelName);
        } else {
            console.error('❌ No AI name on violation item!');
        }
    }
});

function checkConsensusHealth() {
    let compromised = false;
    const scores = {};

    ['openai', 'anthropic', 'google', 'perplexity'].forEach(model => {
        const el = responses[model]?.card?.querySelector('.credibility-badge');
        if (el) {
            const scoreMatch = el.textContent.match(/(\d+)\/100/);
            if (scoreMatch) {
                const score = parseInt(scoreMatch[1]);
                scores[model] = score;
                if (score < 70) compromised = true;
            }
        }
    });

    const consensusSection = document.getElementById('consensusSection');
    const existingBtn = document.getElementById('resynthesizeBtn');

    if (compromised && consensusSection && !consensusSection.classList.contains('hidden')) {
        if (!existingBtn) {
            const btn = document.createElement('button');
            btn.id = 'resynthesizeBtn';
            btn.className = 'action-button warning-pulse';
            btn.style.marginTop = '15px';
            btn.style.width = '100%';
            btn.style.background = 'rgba(239, 68, 68, 0.2)';
            btn.style.border = '1px solid #ef4444';
            btn.style.color = '#ef4444';
            btn.innerHTML = '⚠️ Consensus Compromised by Low Credibility. <b>Click to Re-Synthesize</b>';

            btn.onclick = reSynthesizeConsensus;

            // Insert after the consensus content
            const content = document.getElementById('consensusContent');
            content.parentNode.insertBefore(btn, content.nextSibling);
        }
    }
}

async function reSynthesizeConsensus() {
    const btn = document.getElementById('resynthesizeBtn');
    if (btn) {
        btn.innerHTML = '⚙️ Re-Calibrating Council Decision...';
        btn.disabled = true;
    }

    const question = questionInput.value.trim();
    const responsesMap = {};
    const credibilityMap = {};

    ['openai', 'anthropic', 'google', 'perplexity'].forEach(model => {
        const textEl = responses[model]?.response;
        const credEl = responses[model]?.card?.querySelector('.credibility-badge');

        if (textEl && credEl) {
            responsesMap[model] = textEl.innerText; // Get full text including any previous interrogation results
            const scoreMatch = credEl.textContent.match(/(\d+)\/100/);
            if (scoreMatch) credibilityMap[model] = parseInt(scoreMatch[1]);
        }
    });

    try {
        const response = await fetch('/api/resynthesize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: question,
                responses: responsesMap,
                credibility: credibilityMap,
                council_mode: councilToggle.checked
            })
        });

        const data = await response.json();

        if (data.success) {
            const content = document.getElementById('consensusContent');
            content.innerHTML = formatMarkdown(data.consensus);
            content.style.border = '2px solid #ef4444'; // Visual indicator of update
            content.classList.add('flash-update'); // We can add animation if we had css, but border is fine

            // Update button to show success
            if (btn) {
                btn.innerHTML = '✅ Consensus Updated to Reflect Interrogations';
                btn.style.color = '#10b981';
                btn.style.borderColor = '#10b981';
                btn.style.background = 'rgba(16, 185, 129, 0.1)';
            }
        } else {
            alert('Resynthesis failed: ' + data.error);
            if (btn) {
                btn.innerHTML = '⚠️ Retry Re-Synthesis';
                btn.disabled = false;
            }
        }
    } catch (e) {
        console.error(e);
        alert('Resynthesis Error');
        if (btn) {
            btn.innerHTML = '⚠️ Retry Re-Synthesis';
            btn.disabled = false;
        }
    }
}

function animateScoreChange(element, from, to) {
    const duration = 1000; // 1 second
    const start = performance.now();

    // Preserve the structure "Truth Score: X/100" + optional span
    // We only want to update the X/100 part text node

    function update(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);

        // Ease out quart
        const ease = 1 - Math.pow(1 - progress, 4);

        const current = Math.floor(from + (to - from) * ease);

        // Update only the text node part to avoid killing the span child
        // This is tricky without strict DOM separation.
        // Let's just rebuild the text prefix.

        // Check if there is a child span
        const span = element.querySelector('span');

        element.firstChild.textContent = `Truth Score: ${current}/100 `;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}


// ==================== //
// History & UI Logic
// ==================== //
const historySidebar = document.getElementById('historySidebar');
const historyList = document.getElementById('historyList');
const historyToggle = document.getElementById('historyToggle');
const closeHistory = document.getElementById('closeHistory');

// Toggle History
if (historyToggle) {
    historyToggle.addEventListener('click', () => {
        historySidebar.classList.add('open');
        loadHistory();
    });
}

if (closeHistory) {
    closeHistory.addEventListener('click', () => {
        historySidebar.classList.remove('open');
    });
}

// Close when clicking outside
document.addEventListener('click', (e) => {
    if (historySidebar.classList.contains('open') &&
        !historySidebar.contains(e.target) &&
        !historyToggle.contains(e.target)) {
        historySidebar.classList.remove('open');
    }
});

async function loadHistory() {
    try {
        const response = await fetch('/api/history?limit=20');
        const historyData = await response.json();

        historyList.innerHTML = '';

        if (historyData.length === 0) {
            historyList.innerHTML = '<div style="padding:1rem; color:var(--text-muted); text-align:center;">No history found.</div>';
            return;
        }

        historyData.forEach(item => {
            const el = document.createElement('div');
            el.className = 'history-item';
            el.innerHTML = `
    < div class="history-content" >
                    <div class="history-question">${item.question || 'No Question'}</div>
                    <div class="history-meta">
                        <span>${new Date(item.timestamp).toLocaleDateString()}</span>
                        <span>${item.responses ? item.responses.length : 0} AIs</span>
                    </div>
                </div >
    <button class="delete-history-btn" title="Delete">🗑️</button>
`;

            // Click on valid area loads the item
            el.querySelector('.history-content').addEventListener('click', () => loadHistoryItem(item));

            // Delete button logic
            const deleteBtn = el.querySelector('.delete-history-btn');
            deleteBtn.addEventListener('click', async (e) => {
                e.stopPropagation(); // Prevent loading the item
                if (confirm('Delete this history item?')) {
                    try {
                        const res = await fetch(`/ api / history / ${item.id} `, { method: 'DELETE' });
                        const data = await res.json();
                        if (data.success) {
                            el.remove();
                        } else {
                            alert('Error deleting: ' + data.error);
                        }
                    } catch (err) {
                        alert('Delete failed');
                    }
                }
            });

            historyList.appendChild(el);
        });

    } catch (error) {
        console.error('Failed to load history:', error);
        historyList.innerHTML = '<div style="color:red; padding:1rem;">Failed to load history</div>';
    }
}

function loadHistoryItem(item) {
    // Populate the main input
    questionInput.value = item.question;

    // Reset UI first
    resetResponses();
    resultsSection.classList.remove('hidden');
    consensusSection.classList.add('hidden'); // Hide consensus unless we saved it (db schema update might be needed for consensus saving)

    // Populate responses
    if (item.responses) {
        item.responses.forEach(resp => {
            // Map db fields to UI fields
            // DB keys: ai_provider, model_name, response_text, response_time, success
            const aiKey = resp.ai_provider.toLowerCase();
            if (responses[aiKey]) {
                const uiData = {
                    model: resp.model_name,
                    time: resp.response_time,
                    cost: 0, // We don't save cost yet, maybe in future
                    has_citations: false, // We check regex below
                    thought: null, // We don't save thought trace yet
                    response: resp.response_text,
                    success: resp.success
                };

                // Simple regex check for citations in loaded text
                uiData.has_citations = /\[\d+\]|http/.test(uiData.response);

                updateResponse(aiKey, uiData);
            }
        });
    }

    // Close sidebar on mobile
    if (window.innerWidth < 768) {
        historySidebar.classList.remove('open');
    }
}

// ==================== //
// Project Management
// ==================== //
const projectsSidebar = document.getElementById('projectsSidebar');
const projectsToggle = document.getElementById('projectsToggle');
const closeProjects = document.getElementById('closeProjects');
const projectsList = document.getElementById('projectsList');
const newProjectInput = document.getElementById('newProjectInput');
const createProjectBtn = document.getElementById('createProjectBtn');

const currentProjectDisplay = document.getElementById('currentProjectDisplay');
const currentProjectNameSpan = document.getElementById('currentProjectName');
const clearProjectBtn = document.getElementById('clearProject');

// Export & Voice Elements
const exportBtn = document.getElementById('exportBtn');
const micBtn = document.getElementById('micBtn');
const listenBtn = document.getElementById('listenBtn');
const obsidianBtn = document.getElementById('obsidianBtn');

// Event Listeners
if (projectsToggle) {
    projectsToggle.addEventListener('click', () => {
        projectsSidebar.classList.add('open');
        loadProjects();
    });
}

if (listenBtn) listenBtn.addEventListener('click', toggleSpeech);
if (exportBtn) exportBtn.addEventListener('click', exportToMarkdown);
if (obsidianBtn) obsidianBtn.addEventListener('click', saveToObsidian);

if (micBtn) {
    micBtn.addEventListener('click', toggleVoiceInput);
}

// ... existing code ...

if (closeProjects) {
    closeProjects.addEventListener('click', () => {
        projectsSidebar.classList.remove('open');
    });
}

// Close sidebar on outside click
document.addEventListener('click', (e) => {
    if (projectsSidebar.classList.contains('open') &&
        !projectsSidebar.contains(e.target) &&
        !projectsToggle.contains(e.target)) {
        projectsSidebar.classList.remove('open');
    }
});

createProjectBtn.addEventListener('click', createProject);
newProjectInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') createProject();
});

clearProjectBtn.addEventListener('click', () => {
    currentProjectName = null;
    currentProjectDisplay.classList.add('hidden');
    // Optionally clear main UI or show toast
});

// Functions
async function loadProjects() {
    try {
        const response = await fetch('/api/projects');
        const projects = await response.json();

        projectsList.innerHTML = '';

        if (projects.length === 0) {
            projectsList.innerHTML = '<div style="padding:1rem; color:var(--text-muted);">No projects yet. Create one!</div>';
            return;
        }

        projects.forEach(name => {
            const el = document.createElement('div');
            el.className = `project - item ${name === currentProjectName ? 'active-project' : ''} `;
            el.innerHTML = `
    < div class="project-content" >
                    <span class="project-name">${name}</span>
                    <span class="project-arrow">→</span>
                </div >
    <button class="delete-project-btn" title="Delete Project">🗑️</button>
`;

            // Click on name/arrow to select project
            el.querySelector('.project-content').addEventListener('click', () => selectProject(name));

            // Delete button logic
            const deleteBtn = el.querySelector('.delete-project-btn');
            deleteBtn.addEventListener('click', async (e) => {
                e.stopPropagation();
                if (confirm(`Delete project "${name}" ? This cannot be undone.`)) {
                    try {
                        const res = await fetch(`/ api / projects / ${encodeURIComponent(name)} `, { method: 'DELETE' });
                        const data = await res.json();
                        if (data.success) {
                            // If deleting active project, clear it
                            if (name === currentProjectName) {
                                clearCurrentProject();
                            }
                            el.remove();
                        } else {
                            alert('Error deleting: ' + data.error);
                        }
                    } catch (err) {
                        alert('Delete failed');
                    }
                }
            });

            projectsList.appendChild(el);
        });
    } catch (error) {
        console.error('Failed to load projects:', error);
        projectsList.textContent = 'Error loading projects.';
    }
}

async function createProject() {
    const name = newProjectInput.value.trim();
    if (!name) return;

    try {
        const response = await fetch('/api/projects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        const data = await response.json();

        if (data.success) {
            newProjectInput.value = '';
            loadProjects();
            selectProject(data.project_name);
        } else {
            alert(data.error || 'Failed to create project');
        }
    } catch (error) {
        console.error('Error creating project:', error);
    }
}

function selectProject(name) {
    currentProjectName = name;
    currentProjectNameSpan.textContent = name;
    currentProjectDisplay.classList.remove('hidden');
    projectsSidebar.classList.remove('open');

    // Highlight active in list if visible
    document.querySelectorAll('.project-item').forEach(el => {
        el.classList.toggle('active-project', el.querySelector('.project-name').textContent === name);
    });
}

// ==================== //
// Power Features
// ==================== //

function generateMarkdown() {
    const question = questionInput.value.trim() || "Untitled Query";
    const consensus = consensusContent.innerText;
    const timestamp = new Date().toLocaleString();

    let md = `# TriAI Report: ${question} \n\n`;
    md += `** Date:** ${timestamp} \n`;
    if (currentProjectName) md += `** Project:** ${currentProjectName} \n`;
    md += `\n-- -\n\n## ðŸ¤– Consensus Analysis\n\n${consensus} \n\n-- -\n\n`;

    // Add individual responses
    Object.keys(responses).forEach(key => {
        const r = responses[key];
        const name = r.model.textContent || key.toUpperCase();
        const text = r.response.innerText;
        md += `## ${key.toUpperCase()} (${name}) \n\n${text} \n\n-- -\n\n`;
    });

    return { title: question, content: md };
}

// 1. Export to Markdown (Download)
function exportToMarkdown() {
    const { title, content } = generateMarkdown();
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `TriAI_${title.replace(/[^a-z0-9]/gi, '_').substring(0, 50)}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// 2. Save directly to Obsidian Vault
async function saveToObsidian() {
    const { title, content } = generateMarkdown();
    const safeTitle = title.replace(/[^a-z0-9 ]/gi, '').trim().substring(0, 50) || "Report";
    const filename = `TriAI - ${safeTitle}.md`;

    // UI Feedback - Start
    const originalText = obsidianBtn.innerHTML;
    obsidianBtn.innerHTML = '<span class="icon">â³</span> Saving...';
    obsidianBtn.disabled = true;

    try {
        const response = await fetch('/api/save_to_obsidian', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: filename,
                content: content
            })
        });

        const result = await response.json();

        if (result.success) {
            obsidianBtn.innerHTML = '<span class="icon">âœ“</span> Saved!';
            obsidianBtn.style.borderColor = '#10b981';
            setTimeout(() => {
                obsidianBtn.innerHTML = originalText;
                obsidianBtn.style.borderColor = '';
                obsidianBtn.disabled = false;
            }, 3000);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Save failed:', error);
        alert('Failed to save to Obsidian: ' + error.message);
        obsidianBtn.innerHTML = '<span class="icon">âœ—</span> Failed';
        setTimeout(() => {
            obsidianBtn.innerHTML = originalText;
            obsidianBtn.disabled = false;
        }, 3000);
    }
}

// 2. Voice Input
let recognition;
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';

    recognition.onstart = function () {
        micBtn.classList.add('listening');
        micBtn.style.color = '#ef4444'; // Red for recording
        // Optional logic to show "Listening..."
    };

    recognition.onend = function () {
        micBtn.classList.remove('listening');
        micBtn.style.color = '';
    };

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        questionInput.value += (questionInput.value ? " " : "") + transcript;
        // Auto-resize or focus if needed
        questionInput.focus();
    };
}

function toggleVoiceInput() {
    if (!recognition) {
        alert("Voice input not supported in this browser. Try Chrome or Edge.");
        return;
    }


    if (micBtn.classList.contains('listening')) {
        recognition.stop();
    } else {
        recognition.start();
    }
}

// 3. Text-to-Speech (Global Manager)
let speechSynth = window.speechSynthesis;
let speechUtterance = null;
let podcastQueue = [];
let isPodcastPlaying = false;
let availableVoices = [];

// Ensure voices are loaded
function loadVoices() {
    availableVoices = speechSynth.getVoices();
    console.log("Voices loaded:", availableVoices.length);
}

// Initialize voices
loadVoices();
if (speechSynth.onvoiceschanged !== undefined) {
    speechSynth.onvoiceschanged = loadVoices;
}

function toggleSpeech() {
    if (speechSynth.speaking || isPodcastPlaying) {
        // Stop Everything
        speechSynth.cancel();
        isPodcastPlaying = false;
        podcastQueue = [];
        updateListenButton(false);
    } else {
        // Start Speaking
        const text = consensusContent.innerText;
        if (!text || text.includes('Loading analysis...')) return;

        // Check format - simplified check
        if (text.match(/Host [A1]/i)) {
            console.log("Podcast Mode Detected");
            playPodcast(text);
        } else {
            console.log("Normal Mode Detected");
            playNormal(text);
        }
        updateListenButton(true);
    }
}

function playNormal(text) {
    speechUtterance = new SpeechSynthesisUtterance(text);
    speechUtterance.lang = 'en-US';

    // Voice Selection
    const voice = availableVoices.find(v => v.name.includes("Google US English") || v.name.includes("Microsoft Zira")) || availableVoices[0];
    if (voice) speechUtterance.voice = voice;

    speechUtterance.onend = () => updateListenButton(false);
    speechUtterance.onerror = (e) => {
        console.error("Speech Error:", e);
        updateListenButton(false);
    };
    speechSynth.speak(speechUtterance);
}

function playPodcast(text) {
    isPodcastPlaying = true;
    // Split by newlines
    const lines = text.split('\n').filter(line => line.trim() !== '');
    podcastQueue = [];

    // Assign Voices - Ensure we have distinct ones if possible
    const voiceA = availableVoices.find(v => v.name.includes("Google US English") || v.name.includes("Microsoft David")) || availableVoices[0];
    const voiceB = availableVoices.find(v => v.name.includes("Google UK English Female") || v.name.includes("Microsoft Zira")) || availableVoices.find(v => v !== voiceA) || voiceA;

    lines.forEach(line => {
        let speaker = null;
        let content = line;

        // Flexible regex to catch "**Host A**", "Host A:", "**Host 1**", etc.
        if (line.match(/\**Host\s*[A1]\**[:\.]?/i)) {
            speaker = 'A';
            content = line.replace(/\**Host\s*[A1]\**[:\.]?/gi, '').trim();
        } else if (line.match(/\**Host\s*[B2]\**[:\.]?/i)) {
            speaker = 'B';
            content = line.replace(/\**Host\s*[B2]\**[:\.]?/gi, '').trim();
        }

        // If content is just metadata, ignore it
        if (content.length < 2) return;

        if (content && speaker) {
            const utt = new SpeechSynthesisUtterance(content);
            utt.voice = (speaker === 'B') ? voiceB : voiceA;
            // Slightly different pitch/rate for variety
            if (speaker === 'B') { utt.pitch = 1.1; utt.rate = 1.05; }
            else { utt.pitch = 1.0; utt.rate = 1.0; }

            podcastQueue.push(utt);
        } else if (content && podcastQueue.length > 0) {
            // Append to previous speaker if no speaker tag found but previous exists
            // Optional: Handle continuation lines if needed, for now simplistic approach
        }
    });

    if (podcastQueue.length === 0) {
        console.warn("Podcast parsing failed, falling back to normal read.");
        playNormal(text);
        return;
    }

    playNextPodcastLine();
}

function playNextPodcastLine() {
    if (!isPodcastPlaying) return;

    if (podcastQueue.length === 0) {
        isPodcastPlaying = false;
        updateListenButton(false);
        return;
    }

    const utt = podcastQueue.shift();
    utt.onend = () => playNextPodcastLine();
    utt.onerror = (e) => console.error("Podcast Line Error:", e);

    // Small delay between speakers for realism
    setTimeout(() => {
        if (isPodcastPlaying) speechSynth.speak(utt);
    }, 200);
}

function updateListenButton(isSpeaking) {
    if (isSpeaking) {
        listenBtn.innerHTML = '<span class="icon">â¹ï¸</span> Stop';
        listenBtn.classList.add('active-voice');
        listenBtn.style.borderColor = '#eab308'; // Warn/Gold color
        listenBtn.style.color = '#eab308';
    } else {
        listenBtn.innerHTML = '<span class="icon">ðŸ”Š</span> Listen';
        listenBtn.classList.remove('active-voice');
        listenBtn.style.borderColor = ''; // Reset to default
        listenBtn.style.color = '';
    }
}

// 4. Individual Card Download
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.download-card-btn');
    if (btn) {
        const target = btn.dataset.target;
        const respData = responses[target];
        if (!respData || !respData.response) return;

        const question = questionInput.value.trim() || "Untitled Query";
        const modelName = respData.model.textContent || target.toUpperCase();
        const content = respData.response.innerText;
        const timestamp = new Date().toLocaleString();

        let md = `# TriAI Individual Report: ${target.toUpperCase()} \n\n`;
        md += `** Query:** ${question} \n`;
        md += `** Model:** ${modelName} \n`;
        md += `** Date:** ${timestamp} \n\n`;
        md += `-- -\n\n${content} \n`;

        const blob = new Blob([md], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `TriAI_${target}_${new Date().getTime()}.md`;
        a.click();
        URL.revokeObjectURL(url);
    }
});

// 5. Individual Card Visualization
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.visualize-btn');
    if (btn) {
        const target = btn.dataset.target;
        const respData = responses[target];
        if (!respData || !respData.response) return;

        // Show loading state
        const icon = btn.querySelector('.icon');
        const originalIcon = icon.textContent;
        icon.textContent = '⏳';
        btn.disabled = true;

        // Get current comparison ID (stored globally when comparison is created)
        const comparisonId = currentComparisonId;
        if (!comparisonId) {
            alert('No comparison ID found. Please re-run the query.');
            icon.textContent = originalIcon;
            btn.disabled = false;
            return;
        }

        // Send visualization request to backend
        fetch('/visualize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                comparison_id: comparisonId,
                provider: target
            })
        })
            .then(response => response.json())
            .then(data => {
                icon.textContent = originalIcon;
                btn.disabled = false;

                if (data.error) {
                    alert(`Visualization failed: ${data.error} `);
                    return;
                }

                // Display chart in a modal or inline
                if (data.chart_url) {
                    showChartModal(data.chart_url, target);
                } else if (data.message) {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Visualization error:', error);
                icon.textContent = originalIcon;
                btn.disabled = false;
                alert('Failed to generate visualization. Please try again.');
            });
    }
});

function showChartModal(chartUrl, provider) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('chartModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'chartModal';
        modal.className = 'modal';
        modal.innerHTML = `
    < div class="modal-content" style = "max-width: 900px;" >
                <div class="modal-header">
                    <h3>📊 Data Visualization</h3>
                    <button class="close-modal" onclick="document.getElementById('chartModal').style.display='none'">×</button>
                </div>
                <div class="modal-body" style="text-align: center;">
                    <img id="chartModalImg" src="" alt="Chart" style="max-width: 100%; height: auto;">
                </div>
            </div >
    `;
        document.body.appendChild(modal);
    }

    // Show modal with chart
    document.getElementById('chartModalImg').src = chartUrl + '?t=' + new Date().getTime();
    modal.style.display = 'flex';
}


// ==================== //
// Council Mode Role Selectors
// ==================== //
const roleSelectors = document.getElementById('roleSelectors');

// Show/Hide role selectors when Council Mode is toggled
councilToggle.addEventListener('change', () => {
    if (councilToggle.checked) {
        roleSelectors.classList.remove('hidden');
    } else {
        roleSelectors.classList.add('hidden');
    }
});

// Function to get current role assignments
function getCouncilRoles() {
    return {
        openai: {
            role: document.getElementById('roleOpenAI').value,
            visual_profile: document.getElementById('visualOpenAI').value
        },
        anthropic: {
            role: document.getElementById('roleAnthropic').value,
            visual_profile: document.getElementById('visualAnthropic').value
        },
        google: {
            role: document.getElementById('roleGoogle').value,
            visual_profile: document.getElementById('visualGoogle').value
        },
        perplexity: {
            role: document.getElementById('rolePerplexity').value,
            visual_profile: document.getElementById('visualPerplexity').value
        }
    };
}

// ==================== //
// Initialization
// ==================== //
console.log('TriAI Compare loaded successfully');

// ==================== //
// Workflow Mode Logic  //
// ==================== //

// Initial Fetch of Workflows
async function fetchWorkflows() {
    try {
        const response = await fetch('/api/workflows');
        const workflows = await response.json();

        workflowSelect.innerHTML = '<option value="">-- Choose a workflow --</option>';

        // Sort keys by the workflow NAME, not the ID
        const sortedIds = Object.keys(workflows).sort((a, b) => {
            return workflows[a].name.localeCompare(workflows[b].name);
        });

        sortedIds.forEach(id => {
            const option = document.createElement('option');
            option.value = id;
            option.textContent = workflows[id].name;
            workflowSelect.appendChild(option);
        });
    } catch (err) {
        console.error('Error fetching workflows:', err);
    }
}

fetchWorkflows();

workflowToggle.addEventListener('change', () => {
    if (workflowToggle.checked) {
        workflowArea.classList.remove('hidden');
        if (councilToggle.checked) councilToggle.click();
        resultsSection.classList.add('hidden');
        consensusSection.classList.add('hidden');
    } else {
        workflowArea.classList.add('hidden');
        workflowResultsSection.classList.add('hidden');
    }
});

// Pause/Stop Workflow Logic
if (pauseWorkflowBtn) {
    pauseWorkflowBtn.addEventListener('click', () => {
        if (confirm('Stop the current workflow?')) {
            stopWorkflow();
            workflowProgressText.textContent = '❌ Stopped by user.';
            pauseWorkflowBtn.classList.add('hidden');
        }
    });
}

async function runWorkflowMode() {
    const question = questionInput.value.trim();
    const workflowId = workflowSelect.value;

    if (!workflowId) {
        alert('Please select a workflow template!');
        return;
    }

    // Reset state
    isQuerying = true;
    askButton.disabled = true;
    askButton.querySelector('.button-text').textContent = 'Project Initializing...';
    loadingState.classList.remove('hidden');
    startStatusRotation();

    // Video State: High Energy
    const bgVideo = document.getElementById('bgVideo');
    const processingVideo = document.getElementById('processingVideo');

    if (bgVideo && processingVideo) {
        bgVideo.classList.remove('active');
        processingVideo.classList.add('active');
        processingVideo.play();
    }

    workflowStepsContainer.innerHTML = '';
    workflowProgressBarFill.style.width = '0%';
    workflowProgressText.textContent = 'Initializing...';
    workflowResultsSection.classList.remove('hidden');
    workflowFinalActions.classList.add('hidden');
    pauseWorkflowBtn.classList.remove('hidden');

    workflowContext = { 'initial_goal': question };
    currentStepIndex = 0;
    workflowIsPaused = false;

    try {
        // Start the Job
        const runResponse = await fetch('/api/workflow/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: question,
                workflow_id: workflowId,
                hard_mode: hardModeToggle.checked
            })
        });

        const initData = await runResponse.json();
        if (initData.error) throw new Error(initData.error);

        const jobId = initData.job_id;
        console.log(`Workflow started: ${jobId} `);

        // Load template for metadata
        const workflowsRes = await fetch('/api/workflows');
        const workflowsData = await workflowsRes.json();
        currentWorkflowData = workflowsData[workflowId];
        activeWorkflowName.textContent = `Project: ${currentWorkflowData.name} `;

        // Start Polling
        pollWorkflowStatus(jobId);

    } catch (err) {
        alert(`Workflow Init Error: ${err.message} `);
        stopWorkflow();
    }
}

function pollWorkflowStatus(jobId) {
    const renderedStepIds = new Set();

    const interval = setInterval(async () => {
        if (!isQuerying) {
            clearInterval(interval);
            return;
        }

        try {
            const response = await fetch(`/ api / workflow / status / ${jobId} `);
            const data = await response.json();

            if (data.error) {
                clearInterval(interval);
                alert(`Polling Error: ${data.error} `);
                stopWorkflow();
                return;
            }

            const totalSteps = currentWorkflowData.steps.length;
            currentWorkflowResults = data.results || [];

            // Render new results
            currentWorkflowResults.forEach((step) => {
                if (!renderedStepIds.has(step.step)) {
                    if (renderedStepIds.size > 0) {
                        const arrow = document.createElement('div');
                        arrow.className = 'pipeline-arrow';
                        workflowStepsContainer.appendChild(arrow);
                    }
                    const card = createStepCard(step);
                    workflowStepsContainer.appendChild(card);
                    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

                    renderedStepIds.add(step.step);
                    workflowContext[step.key || `step_${step.step} `] = step.data.response;
                }
            });

            // Update Header Status
            const progress = Math.round((renderedStepIds.size / totalSteps) * 100);
            workflowProgressBarFill.style.width = `${progress}% `;
            workflowProgressText.textContent = `${progress}% Complete`;

            if (data.status === 'complete') {
                clearInterval(interval);
                finishWorkflow();
            } else if (data.status === 'failed') {
                clearInterval(interval);
                alert(`Workflow Failed: ${data.error || 'Unknown Error'} `);
                stopWorkflow();
            }

        } catch (err) {
            console.error('Polling cycle error:', err);
        }
    }, 2000);
}

function createStepCard(step) {
    const card = document.createElement('div');
    card.id = `step - card - ${step.step} `;
    card.className = 'workflow-step-card';
    const colors = getModelColors(step.model);
    card.style.setProperty('--step-color', colors.hex);

    const success = step.data.success;
    const statusClass = success ? 'complete' : 'error';
    const statusText = success ? '✓ Complete' : '❌ Failed';

    // Find instruction from template
    const stepTemplate = currentWorkflowData.steps.find(s => s.id === step.step);
    const instruction = stepTemplate ? stepTemplate.instruction : "Step execution.";

    card.innerHTML = `
    < div class="step-status-row" >
            <div class="status-badge ${statusClass}">${statusText}</div>
            <div class="step-id">STEP ${step.step}: ${step.role.toUpperCase()}</div>
            <div class="step-actions">
                <button class="step-btn interrogate-step-trigger" data-model="${step.model}" data-step="${step.step}" data-role="${step.role}">Interrogate</button>
                <button class="step-btn" onclick="openEditModal('${step.key}', ${step.step})">Edit Output</button>
                <button class="step-btn" onclick="copyToClipboard(this, \`${step.data.response.replace(/`/g, '\\`')}\`)">Copy</button>
            </div>
        </div >
        <div class="step-header">
            <span class="step-role" style="color:${colors.hex}">${step.role.toUpperCase()} (${step.model})</span>
        </div>
        <div class="step-instruction">Objective: ${instruction}</div>
        <div class="step-enforcement-area"></div>
        <div class="step-response">${formatMarkdown(step.data.response)}</div>
`;

    // Render Enforcement Report if available
    if (step.data.enforcement) {
        const enfArea = card.querySelector('.step-enforcement-area');
        const enforcement = step.data.enforcement;

        // Render Badge
        const score = enforcement.current_credibility !== undefined ? enforcement.current_credibility : 100;
        let scoreClass = 'high';
        if (score < 70) scoreClass = 'low';
        else if (score < 90) scoreClass = 'medium';

        const badgeHtml = `< div class="credibility-badge ${scoreClass}" style = "display:inline-block; margin-bottom:10px;" > Truth Score: ${score} /100</div > `;
        enfArea.innerHTML = badgeHtml;

        // Render Violations
        if (enforcement.violations && enforcement.violations.length > 0) {
            let vHtml = `< div class="enforcement-report" ><div class="enforcement-header">⚠️ Protocol Variance Detected</div><ul class="violation-list">`;
            enforcement.violations.forEach(v => {
                vHtml += `<li class="violation-item" data-ai="${step.model}" title="Click to find in output">${v}</li>`;
            });
            vHtml += `</ul></div > `;
            enfArea.innerHTML += vHtml;
        }
    }

    return card;
}

function getModelColors(model) {
    const colors = {
        'openai': { hex: 'var(--accent-openai)', rgb: '16, 163, 127' },
        'anthropic': { hex: 'var(--accent-anthropic)', rgb: '249, 115, 22' },
        'google': { hex: 'var(--accent-google)', rgb: '234, 179, 8' },
        'perplexity': { hex: 'var(--accent-perplexity)', rgb: '6, 182, 212' }
    };
    return colors[model] || { hex: 'var(--accent-gold)', rgb: '212, 175, 55' };
}

function updateAskButtonStatus(text) {
    askButton.querySelector('.button-text').textContent = text;
}

function stopWorkflow() {
    isQuerying = false;
    askButton.disabled = false;
    askButton.querySelector('.button-text').textContent = 'Ask All AIs';
    loadingState.classList.add('hidden');
    stopStatusRotation();

    // Reset Video State
    const bgVideo = document.getElementById('bgVideo');
    const processingVideo = document.getElementById('processingVideo');

    if (bgVideo && processingVideo) {
        processingVideo.classList.remove('active');
        setTimeout(() => processingVideo.pause(), 1500);
        bgVideo.classList.add('active');
    }
}

function finishWorkflow() {
    stopWorkflow();
    workflowFinalActions.classList.remove('hidden');
    pauseWorkflowBtn.classList.add('hidden');
}

// Global scope functions for dynamic buttons
window.openEditModal = function (key, stepId) {
    editingStepId = stepId;
    const content = workflowContext[key] || "";
    editStepTextArea.value = content;
    editStepModal.classList.remove('hidden');
};

saveStepEditBtn.addEventListener('click', () => {
    const newContent = editStepTextArea.value;
    const templateStep = currentWorkflowData.steps.find(s => s.id === editingStepId);
    const key = templateStep ? templateStep.key : `step_${editingStepId} `;

    workflowContext[key] = newContent;

    // Update the UI card as well
    const card = document.getElementById(`step - card - ${editingStepId} `);
    if (card) {
        const responseDiv = card.querySelector('.step-response');
        responseDiv.innerHTML = formatMarkdown(newContent);
    }

    editStepModal.classList.add('hidden');
});

[cancelStepEditBtn, closeModalBtn].forEach(btn => {
    btn.addEventListener('click', () => editStepModal.classList.add('hidden'));
});

// Export Logic
workflowExportBtn.addEventListener('click', async () => {
    let report = `# Discovery Report: ${currentWorkflowData.name} \n`;
    report += `Generated: ${new Date().toLocaleString()} \n`;
    report += `Goal: ${workflowContext.initial_goal} \n\n`;

    currentWorkflowData.steps.forEach(step => {
        const key = step.key || `step_${step.id} `;
        report += `## STEP ${step.id}: ${step.role.toUpperCase()} (${step.model}) \n`;
        report += `${workflowContext[key] || "No output."} \n\n`;
        report += `-- -\n\n`;
    });

    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `TriAI_Discovery_${currentWorkflowData.name.replace(/\s+/g, '_')}.md`;
    a.click();
});

workflowResetBtn.addEventListener('click', () => {
    workflowResultsSection.classList.add('hidden');
    questionInput.value = '';
    questionInput.focus();
});
// ==================== //
// Interrogation Logic  //
// ==================== //
const interrogationDrawer = document.getElementById('interrogationDrawer');
const closeInterrogation = document.getElementById('closeInterrogation');
const interrogationHistory = document.getElementById('interrogationHistory');
const interrogationInput = document.getElementById('interrogationInput');
const submitInterrogation = document.getElementById('submitInterrogation');
const interrogationLoading = document.getElementById('interrogationLoading');

let currentInterrogationModel = '';
let currentInterrogationContext = '';
let currentInterrogationRole = '';

window.openInterrogation = function (model, response, role = 'Expert') {
    currentInterrogationModel = model;
    currentInterrogationContext = response;
    currentInterrogationRole = role;

    interrogationHistory.innerHTML = '';
    addInterrogationBubble('ai', response, model, role);

    interrogationDrawer.classList.add('open');
};

// Event Delegation for Interrogation Triggers
document.addEventListener('click', (e) => {
    if (e.target && e.target.classList.contains('interrogate-step-trigger')) {
        const model = e.target.dataset.model;
        const stepId = e.target.dataset.step;
        const role = e.target.dataset.role;

        // Find the full response from currentWorkflowResults
        const step = currentWorkflowResults.find(s => s.step == stepId);
        const response = step ? step.data.response : (workflowContext[stepId] || "");

        openInterrogation(model, response, role);
    }
});

closeInterrogation.addEventListener('click', () => {
    interrogationDrawer.classList.remove('open');
});

submitInterrogation.addEventListener('click', runInterrogation);
interrogationInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        runInterrogation();
    }
});

async function runInterrogation() {
    const question = interrogationInput.value.trim();
    if (!question || !currentInterrogationModel) return;

    addInterrogationBubble('user', question);
    interrogationInput.value = '';
    interrogationLoading.classList.remove('hidden');

    try {
        const res = await fetch('/interrogate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: currentInterrogationModel,
                question: question,
                previous_response: currentInterrogationContext,
                project_context: JSON.stringify(workflowContext)
            })
        });

        const data = await res.json();
        interrogationLoading.classList.add('hidden');

        if (data.success) {
            addInterrogationBubble('ai', data.response, currentInterrogationModel, currentInterrogationRole);
            // Update context so follow-ups have memory of the interrogation
            currentInterrogationContext += `\n\nUser Question: ${question} \nYour Follow - up: ${data.response} `;
        } else {
            addInterrogationBubble('ai', `Error: ${data.error || 'Failed to interrogate expert.'} `, 'system', 'System');
        }
    } catch (err) {
        interrogationLoading.classList.add('hidden');
        addInterrogationBubble('ai', `Protocol Error: ${err.message} `, 'system', 'System');
    }
}

function addInterrogationBubble(type, content, model, role) {
    const bubble = document.createElement('div');
    bubble.className = `interrogation - bubble ${type} `;

    if (type === 'ai') {
        const colors = getModelColors(model);
        bubble.style.setProperty('--card-accent', colors.hex);
        bubble.innerHTML = `< strong > ${role.toUpperCase()} (${model}):</strong > <br>${formatMarkdown(content)}`;
    } else {
        bubble.textContent = content;
    }

    interrogationHistory.appendChild(bubble);
    interrogationHistory.scrollTop = interrogationHistory.scrollHeight;
}

// ==================== //
// 🚀 New Features: Clickable Header & Badges //
// ==================== //

// 1. Scroll Clickable Header
window.scrollToFirstViolation = function (headerElement, modelName) {
    const reportDiv = headerElement.closest('.enforcement-report');
    if (!reportDiv) return;

    // Find first violation item
    const firstViolation = reportDiv.querySelector('.violation-item');
    if (firstViolation) {
        // Visual feedback on header
        headerElement.style.opacity = '0.5';
        setTimeout(() => headerElement.style.opacity = '1', 200);

        // Call existing context locator
        if (window.scrollToContext) {
            window.scrollToContext(firstViolation, modelName);
        }
    }
};

// 2. Inject Badges
window.injectInlineBadges = function (card, violations, modelName) {
    if (!violations || violations.length === 0) return;

    // Target the response text
    // .response-text covers normal cards, .ai-response covers raw
    const targetDiv = card.querySelector('.response-text') || document.getElementById(`${modelName}-response`);

    if (!targetDiv) return;

    let html = targetDiv.innerHTML;
    let modified = false;

    violations.forEach(v => {
        // Parse format: "TYPE: 'quoted text'"
        // E.g. UNANCHORED_METRIC: '25%' found...
        const match = v.match(/^([A-Z_]+):\s*'([^']+)'/);

        if (match) {
            const type = match[1];
            const textToFind = match[2];

            // Skip duplicates
            if (html.includes(`data-violation="${type}"`) && html.includes(textToFind)) return;

            const escaped = textToFind.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            const regex = new RegExp(`(${escaped})`, '');

            // Badge Style: Tiny, red, high-signal
            const badgeHtml = `<span class="violation-badge" 
                                     data-violation="${type}" 
                                     onclick="event.stopPropagation(); triggerCardInterrogation('${modelName}', document.getElementById('${modelName}-response').innerText, 'Explain this ${type} violation')" 
                                     title="${v}"
                                     style="
                                        font-size: 0.65em; 
                                        vertical-align: middle;
                                        margin-left: 4px; 
                                        padding: 2px 4px; 
                                        border-radius: 4px; 
                                        background: rgba(220, 38, 38, 0.2); 
                                        color: #fca5a5; 
                                        border: 1px solid rgba(220, 38, 38, 0.6); 
                                        cursor: pointer;
                                        display: inline-flex;
                                        align-items: center;
                                        font-family: 'JetBrains Mono', monospace;
                                        font-weight: bold;
                                        letter-spacing: 0.5px;
                                        transition: all 0.2s;
                                        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                                     "
                                     onmouseover="this.style.background='rgba(220, 38, 38, 0.4)'; this.style.transform='scale(1.05)'"
                                     onmouseout="this.style.background='rgba(220, 38, 38, 0.2)'; this.style.transform='scale(1)'"
                                     >
                                     ${type}
                               </span>`;

            if (regex.test(html)) {
                // Wrap text + add badge
                // Note: we use previousElementSibling in onclick, so we need a wrapper or sibling
                // Using a span for the text makes it targetable
                html = html.replace(regex, `<span class="flagged-content" style="background: rgba(220, 38, 38, 0.1); border-bottom: 2px dotted #ef4444; color: inherit;">$1</span>${badgeHtml}`);
                modified = true;
            }
        }
    });

    if (modified) {
        targetDiv.innerHTML = html;
        console.log(`✅ Injected inline badges for ${modelName}`);
    }
};

