/* KORUM-OS Logic - Fully Integrated (Telemetry, Interrogation, Charts) */

const PROTOCOL_CONFIGS = {
    "War Room": { openai: "strategist", anthropic: "containment", google: "takeover", perplexity: "scout" },
    "Deep Research": { openai: "analyst", anthropic: "researcher", google: "historian", perplexity: "scout" },
    "Creative Council": { openai: "writer", anthropic: "innovator", google: "marketing", perplexity: "social" },
    "Code Audit": { openai: "architect", anthropic: "integrity", google: "hacker", perplexity: "optimizer" },
    "System Core": { openai: "visionary", anthropic: "architect", google: "critic", perplexity: "researcher" }
};

let activeSelection = "";
let suggestedRoles = null;
let customRolesActive = false;

// Query pattern detection for smart suggestions
const QUERY_PATTERNS = {
    "War Room": ["crisis", "threat", "emergency", "attack", "vulnerability", "breach", "defend", "strategy", "takeover", "hostile"],
    "Deep Research": ["research", "study", "analyze", "investigate", "explain", "how does", "what is", "history", "scientific", "academic"],
    "Creative Council": ["creative", "design", "write", "story", "marketing", "campaign", "brand", "innovative", "idea", "concept"],
    "Code Audit": ["code", "bug", "debug", "security", "vulnerability", "review", "refactor", "optimize", "performance", "architecture"],
    "System Core": ["general", "help", "question", "advice"]
};

function analyzeQuery(query) {
    const lowerQuery = query.toLowerCase();
    let maxMatches = 0;
    let bestWorkflow = "System Core";

    for (const [workflow, keywords] of Object.entries(QUERY_PATTERNS)) {
        const matches = keywords.filter(kw => lowerQuery.includes(kw)).length;
        if (matches > maxMatches) {
            maxMatches = matches;
            bestWorkflow = workflow;
        }
    }

    return bestWorkflow;
}

function initViz() {
    positionNodes();
    setupInteractions();
    setupInterrogation();

    document.querySelectorAll('.node').forEach(n => {
        n.classList.add('selected');
        n.style.opacity = 1;
    });

    setInterval(pushHeartbeat, 4000);
    logTelemetry("System Initialized.", "system");
    logTelemetry("Neural Link: ESTABLISHED", "system");
}

function positionNodes() {
    const nodes = document.querySelectorAll(".node"); if (!nodes.length) return;
    const radius = 220;
    nodes.forEach((node, i) => {
        const angleRad = (i / nodes.length) * 2 * Math.PI;
        const x = radius * Math.cos(angleRad); const y = radius * Math.sin(angleRad);
        node.style.transform = `translate(${x}px, ${y}px)`;
    });
}

function setupInteractions() {
    document.querySelectorAll('.node').forEach(node => node.addEventListener('click', () => node.classList.toggle('selected')));
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            logTelemetry(`Protocol Switched: ${link.dataset.role.toUpperCase()}`, "process");
            updateSystemStatus(`MODE: ${link.dataset.role}`);
        });
    });

    // SMART SUGGESTION SYSTEM
    const queryInput = document.getElementById('queryInput');
    const suggestionBox = document.getElementById('suggestionBox');
    const roleCustomization = document.getElementById('roleCustomization');
    let suggestionTimeout;

    queryInput?.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        clearTimeout(suggestionTimeout);

        if (query.length > 20) {
            suggestionTimeout = setTimeout(() => {
                const suggestedWorkflow = analyzeQuery(query);
                suggestedRoles = PROTOCOL_CONFIGS[suggestedWorkflow];

                document.getElementById('detectedCategory').textContent = suggestedWorkflow;
                document.getElementById('suggestedWorkflow').textContent = suggestedWorkflow;
                suggestionBox.classList.remove('hidden');

                // Pre-populate dropdowns
                if (suggestedRoles) {
                    document.getElementById('roleSelectOpenAI').value = suggestedRoles.openai;
                    document.getElementById('roleSelectAnthropic').value = suggestedRoles.anthropic;
                    document.getElementById('roleSelectGoogle').value = suggestedRoles.google;
                    document.getElementById('roleSelectPerplexity').value = suggestedRoles.perplexity;
                }

                logTelemetry(`Query Analyzed: ${suggestedWorkflow}`, "process");
            }, 800);
        } else {
            suggestionBox.classList.add('hidden');
            roleCustomization.classList.add('hidden');
        }
    });

    // Use Suggested Button
    document.getElementById('useSuggestedBtn')?.addEventListener('click', () => {
        const suggestedWorkflow = document.getElementById('suggestedWorkflow').textContent;
        const targetTab = document.querySelector(`.nav-links a[data-role="${suggestedWorkflow}"]`);
        if (targetTab) {
            targetTab.click();
        }
        suggestionBox.classList.add('hidden');
        roleCustomization.classList.add('hidden');
        customRolesActive = false;
        logTelemetry(`Applied Suggested Config: ${suggestedWorkflow}`, "system");
    });

    // Customize Roles Button
    document.getElementById('customizeBtn')?.addEventListener('click', () => {
        roleCustomization.classList.toggle('hidden');
        customRolesActive = !customRolesActive;
        logTelemetry("Custom Role Editor Opened", "system");
    });

    // Dismiss Suggestion
    document.getElementById('dismissSuggestionBtn')?.addEventListener('click', () => {
        suggestionBox.classList.add('hidden');
        roleCustomization.classList.add('hidden');
    });

    // Clear Button
    document.getElementById('clearInputBtn')?.addEventListener('click', () => {
        document.getElementById('queryInput').value = '';
        logTelemetry("Input Cleared", "system");
    });

    // Rotate Roles Button
    document.getElementById('rotateRolesBtn')?.addEventListener('click', (e) => {
        const btn = e.target;
        btn.style.transition = "transform 0.5s ease";
        btn.style.transform = "rotate(360deg)";
        setTimeout(() => btn.style.transform = "none", 500);

        rotateRoles();
        logTelemetry("Council Roles Rotated", "process");
    });

    document.querySelector('.trigger-scan')?.addEventListener('click', async (e) => {
        const queryField = document.getElementById('queryInput');
        const query = queryField.value.trim();
        if (!query) { alert("Protocol Violation: Query Required."); return; }

        triggerCouncil(query);
    });

    document.querySelector('.close-results')?.addEventListener('click', closeResults);
}

function rotateRoles() {
    const selects = document.querySelectorAll('.role-select');
    selects.forEach(select => {
        const options = Array.from(select.options);
        const currentIndex = select.selectedIndex;
        const nextIndex = (currentIndex + 1) % options.length;
        select.selectedIndex = nextIndex;
    });
    customRolesActive = true;
}

function updateSystemStatus(text) { const el = document.getElementById('system-status-val'); if (el) el.innerText = text.toUpperCase(); }

async function triggerCouncil(query) {
    const activeRoleName = document.querySelector('.nav-links a.active')?.dataset.role || 'System Core';

    document.body.classList.add("activated");
    const btn = document.querySelector('.trigger-scan');
    if (btn) btn.innerText = "COUNCIL CONVENING...";
    updateSystemStatus("PROCESSING");

    animateActivation();
    startProcessingLogs();

    const isV2 = document.getElementById('v2Toggle')?.checked;

    if (isV2) {
        // V2 Functional Pipeline
        updateSystemStatus("EXECUTING CHAIN");
        try {
            await executeReasoningChain(query);
        } catch (error) {
            console.error(error); showErrorCard(error.message); logTelemetry(`ERROR: ${error.message}`, "system"); resetUI();
        }
    } else {
        // V1 Council Mode
        try {
            await executeCouncil(query, activeRoleName);
        } catch (error) {
            console.error(error); showErrorCard(error.message); logTelemetry(`ERROR: ${error.message}`, "system"); resetUI();
        }
    }
}

async function executeReasoningChain(query) {
    logTelemetry("Initiating V2 Functional Pipeline...", "system");

    // Check Hacker Toggle
    const hackerMode = document.getElementById('hackerToggle')?.checked || false;

    const payload = {
        query: query,
        depth: "standard",
        hacker_mode: hackerMode
    };

    const response = await fetch('/api/v2/reasoning_chain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
    const data = await response.json();

    if (data.success) {
        renderChainResults(data.pipeline_result);
    } else {
        throw new Error(data.error || "Pipeline Failed");
    }
    resetUI();
}

function renderChainResults(result) {
    const container = document.querySelector(".results-content");
    container.innerHTML = "";
    const grid = document.createElement("div");
    grid.className = "results-grid";

    // Helper to create phase cards
    const createCard = (title, model, content, phase) => {
        const card = document.createElement("div");
        card.className = `agent-card ${model.toLowerCase().includes('gpt') ? 'openai' : model.toLowerCase().includes('claude') ? 'anthropic' : 'google'}`;

        // Use centralized formatter
        const displayContent = formatV2Content(content, phase);

        card.innerHTML = `
            <div class="agent-header">
                <div>
                    <div class="agent-name">${title}</div>
                    <div class="agent-model">${model}</div>
                </div>
                <div class="agent-meta"><span>${phase}</span></div>
            </div>
            <div class="agent-response">${displayContent}</div>
        `;

        // Click to expand matches card content format
        card.addEventListener('click', () => {
            openCardModal({
                name: title,
                meta: `<div class="agent-meta"><span>${phase}</span><span>${model}</span></div>`,
                content: displayContent // Pre-formatted HTML
            });
        });

        return card;
    };

    // 1. Deconstruction (Claude)
    grid.appendChild(createCard("PHASE 1: DECONSTRUCTION", "Claude 3.5 Sonnet", result.constraints, "CONSTRAINT ANALYSIS"));

    // 2. Construction (GPT-4o)
    grid.appendChild(createCard("PHASE 2: ARCHITECTURE", "GPT-4o", result.standard_solution, "STANDARD MODEL"));

    // 3. Stress Test (Gemini)
    grid.appendChild(createCard("PHASE 3: STRESS TEST", "Gemini 2.5", result.failure_analysis, "FAILURE PHYSICS"));

    // 4. Synthesis (GPT-4o)
    grid.appendChild(createCard("PHASE 4: EXECUTION", "GPT-4o", result.final_artifact, "FINAL DIRECTIVE"));

    container.appendChild(grid);
    document.querySelector(".results-container").classList.add("visible");
    logTelemetry("Pipeline Execution Complete.", "system");
}

function formatV2Content(content, phase) {
    let displayContent = "";

    // SPECIAL RENDERING FOR PHASE 1 (JSON)
    if (phase === "CONSTRAINT ANALYSIS" && typeof content === 'object') {
        displayContent += `<div style="margin-bottom:10px;"><strong style="color:#00FF9D">CORE GOAL:</strong><br>${content.core_goal || "N/A"}</div>`;

        if (content.explicit_constraints?.length) {
            displayContent += `<strong style="color:#FFB020">EXPLICIT CONSTRAINTS:</strong><ul style="margin-top:5px; padding-left:20px; color:#ddd;">`;
            content.explicit_constraints.forEach(c => displayContent += `<li>${c}</li>`);
            displayContent += `</ul>`;
        }

        if (content.implied_constraints?.length) {
            displayContent += `<br><strong style="color:#00BFFF">IMPLIED CONSTRAINTS:</strong><ul style="margin-top:5px; padding-left:20px; color:#ddd;">`;
            content.implied_constraints.forEach(c => displayContent += `<li>${c}</li>`);
            displayContent += `</ul>`;
        }
    } else {
        // Standard Text Formatting for Phases 2-4
        displayContent = formatV2Text(typeof content === 'object' ? JSON.stringify(content, null, 2) : content);
    }
    return displayContent;
}

function formatV2Text(text) {
    if (!text) return "";
    return text
        .replace(/^## (.*?)$/gm, '<h3 style="color:#00FF9D; margin-top:15px; border-bottom:1px solid #333; padding-bottom:5px;">$1</h3>') // H2 -> H3 Styled
        .replace(/^### (.*?)$/gm, '<h4 style="color:#FFB020; margin-top:10px;">$1</h4>') // H3 -> H4 Styled
        .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#FFF;">$1</strong>') // Bold -> White Strong
        .replace(/^- (.*?)$/gm, '• $1<br>') // List items
        .replace(/\n\d\. (.*?)$/gm, '<div style="margin-left:10px; margin-bottom:4px;"><strong>$1</strong></div>'); // Numbered lists (fixed regex)
}

async function executeCouncil(query, roleName) {
    let roleConfig;

    // Use custom roles if user has customized them
    if (customRolesActive) {
        roleConfig = {
            openai: document.getElementById('roleSelectOpenAI').value,
            anthropic: document.getElementById('roleSelectAnthropic').value,
            google: document.getElementById('roleSelectGoogle').value,
            perplexity: document.getElementById('roleSelectPerplexity').value
        };
        logTelemetry("Using Custom Role Configuration", "process");
    } else {
        roleConfig = PROTOCOL_CONFIGS[roleName] || PROTOCOL_CONFIGS['System Core'];
    }

    const payload = { question: query, council_mode: true, council_roles: roleConfig, active_models: ["openai", "anthropic", "google", "perplexity"] };

    const response = await fetch('/api/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
    const data = await response.json();
    renderResults(data, roleName);
    resetUI();
}

function renderResults(data, roleName) {
    console.log("DEBUG: Full response data:", data);
    console.log("DEBUG: Individual results:", data.results);
    const container = document.querySelector(".results-content");
    const grid = document.createElement("div"); grid.className = "results-grid";

    // Consensus
    const consensusCard = document.createElement("div"); consensusCard.className = "consensus-card";
    consensusCard.innerHTML = `<div class="consensus-title"><span style="font-size:16px">🏛️</span> COUNCIL DECISION: ${roleName.toUpperCase()}</div><div class="consensus-body">${formatText(data.consensus || "No consensus reached.")}</div>`;
    grid.appendChild(consensusCard);

    // Agents
    ["openai", "anthropic", "google", "perplexity"].forEach(provider => {
        const res = data.results[provider];
        if (!res || !res.success) return;
        const card = document.createElement("div"); card.className = `agent-card ${provider}`;
        let metaHtml = `<div class="agent-meta">`;
        if (res.time) metaHtml += `<span>⏱ ${res.time}s</span>`;
        if (res.cost > 0) metaHtml += `<span>💰 $${res.cost.toFixed(5)}</span>`;
        metaHtml += `</div>`;
        let badgeHtml = "";
        if (res.enforcement) {
            const score = res.enforcement.truth_score || 0;
            let color = "#ff4444"; if (score > 80) color = "#00FF9D"; else if (score > 50) color = "#FFB020";
            badgeHtml += `<div class="bs-meter" style="border-left: 3px solid ${color}; padding-left: 8px; margin-bottom: 8px;"><div style="font-size:10px; color:${color}; font-weight:700;">TRUTH SCORE: ${score}/100</div></div>`;
        }
        card.innerHTML = `<div class="agent-header"><div><div class="agent-name">${getProviderName(provider)}</div><div class="agent-model">${res.model || provider}</div></div>${metaHtml}</div>${badgeHtml}<div class="agent-response">${formatText(res.response)}</div>`;

        // Make card clickable
        card.addEventListener('click', () => {
            openCardModal({
                name: getProviderName(provider),
                meta: metaHtml,
                content: res.response,
                model: res.model || provider
            });
        });

        grid.appendChild(card);
    });

    container.innerHTML = ""; container.appendChild(grid);
    document.querySelector(".results-container").classList.add("visible");
    logTelemetry("Consensus Reached. Displaying Output.", "system");

    // RENDER CHARTS
    setTimeout(() => {
        if (window.mermaid) mermaid.init(undefined, document.querySelectorAll('.mermaid'));
    }, 500);
}

/* INTERROGATION ENGINE */
function setupInterrogation() {
    const tooltip = document.getElementById('interrogation-tooltip');

    document.addEventListener('mouseup', (e) => {
        const selection = window.getSelection().toString().trim();
        if (selection && selection.length > 5) {
            // Show Tooltip
            activeSelection = selection;
            tooltip.style.display = 'flex';
            tooltip.style.left = `${e.pageX + 10}px`;
            tooltip.style.top = `${e.pageY - 40}px`;
        } else {
            tooltip.style.display = 'none';
        }
    });

    document.getElementById('btn-challenge').addEventListener('click', () => {
        if (activeSelection) {
            const query = `CHALLENGE THIS CLAIM: "${activeSelection}". Verify accuracy, check for hallucinations, and provide counter-evidence.`;
            tooltip.style.display = 'none';

            // UI Feedback
            const queryInput = document.getElementById('queryInput');
            queryInput.value = query;
            queryInput.classList.add('flash-active'); // Add a flash effect (CSS needed or ignored)
            setTimeout(() => queryInput.classList.remove('flash-active'), 500);

            triggerCouncil(query);
        }
    });

    document.getElementById('btn-viz').addEventListener('click', () => {
        if (activeSelection) {
            const query = `VISUALIZE THIS DATA: "${activeSelection}". Create a Mermaid JS chart (flowchart or pie) representing this structure.`;
            tooltip.style.display = 'none';

            // UI Feedback
            const queryInput = document.getElementById('queryInput');
            queryInput.value = query;

            triggerCouncil(query);
        }
    });
}

/* TELEMETRY ENGINE */
function pushHeartbeat() {
    if (document.body.classList.contains("activated")) return;
    const msgs = ["System: Monitoring...", "Latency: 12ms", "Link: Stable", "Memory: OK", "Scanning for Inputs..."];
    logTelemetry(msgs[Math.floor(Math.random() * msgs.length)], "system");
}

function logTelemetry(msg, type) {
    const feed = document.getElementById('telemetry-feed'); if (!feed) return;
    const now = new Date(); const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
    const item = document.createElement("div"); item.className = `log-entry ${type}`;
    item.innerHTML = `<span class="timestamp">${timeStr}</span> <span class="log-msg">${msg}</span>`;
    feed.appendChild(item);
    if (feed.children.length > 12) feed.removeChild(feed.children[0]);
    feed.scrollTop = feed.scrollHeight;
}

function startProcessingLogs() {
    const logs = [{ msg: "Initializing Neural Handshake...", type: "system" }, { msg: "GPT-4o: Deconstructing Query...", type: "openai" }, { msg: "Perplexity: Scanning External Sources...", type: "perplexity" }, { msg: "Claude 3.5: Validating Architecture...", type: "anthropic" }, { msg: "Gemini: Cross-Referencing Data...", type: "google" }, { msg: "Aggregating Semantic Vectors...", type: "process" }, { msg: "Enforcing Truth Contracts...", type: "system" }];
    let i = 0;
    const interval = setInterval(() => {
        if (i >= logs.length || !document.body.classList.contains("activated")) { clearInterval(interval); return; }
        logTelemetry(logs[i].msg, logs[i].type); i++;
    }, 800);
}

// UTILS
function getProviderName(key) { const names = { openai: "Strategic Core", anthropic: "Architect", google: "Critic", perplexity: "Intel" }; return names[key] || key; }
function formatText(text) {
    if (!text) return "";
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/### (.*?)\n/g, '<h4 style="color:#FFF; margin:10px 0;">$1</h4>')
        .replace(/- (.*?)\n/g, '• $1<br>')
        .replace(/```mermaid([\s\S]*?)```/g, '<div class="mermaid">$1</div>'); // Map to mermaid class for render
}
function showErrorCard(msg) { const container = document.querySelector(".results-content"); container.innerHTML = `<div class="consensus-card" style="border-color: red;"><div class="consensus-title" style="color:red;">SYSTEM FAILURE</div><div class="consensus-body">${msg}</div></div>`; document.querySelector(".results-container").classList.add("visible"); }
function closeResults() { const container = document.querySelector(".results-container"); if (container) container.classList.remove("visible"); setTimeout(() => { document.body.classList.remove("activated"); updateSystemStatus("READY"); }, 500); }
function resetUI() { const btn = document.querySelector('.trigger-scan'); const field = document.querySelector('.glass-textarea'); if (btn) btn.innerText = "Convene Council"; if (field) field.disabled = false; updateSystemStatus("READY"); }
function animateActivation() {
    const nodes = document.querySelectorAll('.node.selected'); if (nodes.length === 0) return;
    nodes.forEach((node, i) => { setTimeout(() => { node.classList.add("energized"); fireLightning(node); const interval = setInterval(() => { if (document.body.classList.contains("activated")) fireLightning(node); else { clearInterval(interval); node.classList.remove("energized"); } }, 1200 + Math.random() * 1500); }, i * 300); });
}
function fireLightning(node) {
    const svg = document.getElementById('lightning-layer'); if (!svg) return;
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path"); path.classList.add("lightning-path");
    const color = getComputedStyle(node).getPropertyValue('--node-color').trim() || '#FFF'; path.style.stroke = color; svg.appendChild(path);
    const duration = 400; const startTime = Date.now(); const sphere = document.querySelector('.sphere-container');
    function animate() { const elapsed = Date.now() - startTime; if (elapsed > duration) { path.remove(); sphere?.classList.remove('impact'); return; } const nodeRect = node.getBoundingClientRect(); const svgRect = svg.getBoundingClientRect(); const startX = nodeRect.left + nodeRect.width / 2 - svgRect.left; const startY = nodeRect.top + nodeRect.height / 2 - svgRect.top; const endX = svgRect.width / 2; const endY = svgRect.height / 2; const d = generateLightningPath(startX, startY, endX, endY, 8); path.setAttribute("d", d); path.style.opacity = Math.random() > 0.5 ? 1 : 0.3; if (Math.random() > 0.8) sphere?.classList.add('impact'); else sphere?.classList.remove('impact'); requestAnimationFrame(animate); } animate();
}
function generateLightningPath(x1, y1, x2, y2, segments) { let d = `M ${x1} ${y1}`; const dx = x2 - x1; const dy = y2 - y1; const len = Math.sqrt(dx * dx + dy * dy); const normalX = -dy / len; const normalY = dx / len; for (let i = 1; i < segments; i++) { const t = i / segments; let px = x1 + dx * t; let py = y1 + dy * t; const jitter = (Math.random() - 0.5) * 50 * (1 - t); px += normalX * jitter; py += normalY * jitter; d += ` L ${px} ${py}`; } d += ` L ${x2} ${y2}`; return d; }

// CARD EXPANSION MODAL
let currentModalData = null;

function openCardModal(cardData) {
    currentModalData = cardData;
    const modal = document.getElementById('cardModal');
    document.getElementById('modalTitle').textContent = cardData.name;
    document.getElementById('modalMeta').innerHTML = cardData.meta;
    document.getElementById('modalContent').innerHTML = formatText(cardData.content);
    modal.classList.add('visible');

    // Re-render mermaid charts in modal
    if (window.mermaid) {
        setTimeout(() => mermaid.init(undefined, document.querySelectorAll('.card-modal .mermaid')), 100);
    }

    logTelemetry(`Expanded Card: ${cardData.name}`, "system");
}

function closeCardModal() {
    const modal = document.getElementById('cardModal');
    modal.classList.remove('visible');
    currentModalData = null;
}

// Modal button handlers - Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('closeModal')?.addEventListener('click', (e) => {
        e.stopPropagation();
        closeCardModal();
    });

    document.getElementById('modalCopyBtn')?.addEventListener('click', () => {
        if (currentModalData) {
            navigator.clipboard.writeText(currentModalData.content);
            logTelemetry("Response Copied to Clipboard", "system");
            alert("✓ Response copied to clipboard!");
        }
    });

    document.getElementById('modalVisualizeBtn')?.addEventListener('click', () => {
        if (currentModalData) {
            const query = `VISUALIZE THIS DATA: "${currentModalData.content.substring(0, 500)}...". Create a Mermaid JS chart representing this structure.`;
            closeCardModal();
            document.getElementById('queryInput').value = query;
            triggerCouncil(query);
        }
    });

    document.getElementById('modalDownloadBtn')?.addEventListener('click', () => {
        if (currentModalData) {
            const blob = new Blob([currentModalData.content], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentModalData.name.replace(/\s+/g, '_')}_response.md`;
            a.click();
            URL.revokeObjectURL(url);
            logTelemetry(`Downloaded: ${currentModalData.name}`, "system");
        }
    });

    // Close modal on overlay click
    document.getElementById('cardModal')?.addEventListener('click', (e) => {
        if (e.target.id === 'cardModal') closeCardModal();
    });
});


window.addEventListener('load', initViz);
