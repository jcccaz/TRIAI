<<<<<<< HEAD
# TriAI Compare - Enhancement Implementation Plan

## 🎯 Goal
Transform TriAI Compare into a full-featured AI workbench with:
- Document analysis
- Conversation history
- 4 AI models (add Perplexity)
- Flexible configuration

---

## 📦 Phase 1: Foundation (Start Now)

### 1.1 Database Layer
**Purpose**: Save all comparisons for history/review

**Tasks**:
- [ ] Create SQLite database schema
- [ ] Add `Comparison` table (id, question, timestamp, metadata)
- [ ] Add `Response` table (id, comparison_id, ai_name, response, time, model)
- [ ] Create database helper functions (save, retrieve, search)

**Files to create**:
- `database.py` - Database models and operations
- `comparisons.db` - SQLite database (auto-created)

**Estimated time**: 15 minutes

---

### 1.2 Add Perplexity AI
**Purpose**: Add 4th AI for search-enhanced responses

**Tasks**:
- [ ] Add Perplexity API integration
- [ ] Update frontend to show 4 cards (2x2 grid)
- [ ] Add PERPLEXITY_API_KEY to .env
- [ ] Update parallel query execution

**Files to modify**:
- `app.py` - Add query_perplexity()
- `templates/index.html` - Add 4th card
- `static/style.css` - Update grid to 2x2
- `.env` - Add PERPLEXITY_API_KEY

**Estimated time**: 20 minutes

---

### 1.3 Document Upload
**Purpose**: Upload PDFs, text files, images for AI analysis

**Tasks**:
- [ ] Add file upload UI component
- [ ] Create file processing backend (extract text from PDFs, images)
- [ ] Pass document context to all AIs
- [ ] Support multiple file formats (PDF, TXT, DOCX, images)

**Required libraries**:
```bash
pip install PyPDF2 python-docx Pillow pytesseract
```

**Files to create**:
- `document_processor.py` - Extract text from various formats

**Files to modify**:
- `app.py` - Add /upload endpoint
- `templates/index.html` - Add file upload UI
- `static/app.js` - Handle file upload

**Estimated time**: 30 minutes

---

### 1.4 History & Saved Comparisons
**Purpose**: Browse and review past comparisons

**Tasks**:
- [ ] Create history page/modal
- [ ] Add "Save" button to each comparison
- [ ] Display saved comparisons in a list
- [ ] Add search/filter functionality
- [ ] Export individual comparisons

**Files to create**:
- `templates/history.html` - History browser page

**Files to modify**:
- `app.py` - Add /history route, /api/save endpoint
- `templates/index.html` - Add "View History" button
- `static/style.css` - Style history components

**Estimated time**: 25 minutes

---

## 📦 Phase 2: Advanced Features (Later)

### 2.1 Flexible Configuration
- Adjustable temperature, max_tokens per AI
- Model selection (e.g., GPT-4o vs GPT-4o-mini)
- Custom system prompts per AI

### 2.2 Advanced Export
- Export to PDF with formatting
- Export to Markdown
- Batch export multiple comparisons

### 2.3 Cost Tracking
- Track API usage per query
- Monthly cost dashboard
- Budget alerts

### 2.4 Multi-turn Conversations
- Chat mode with all AIs
- Conversation threading
- Context management

---

## 🎯 Recommended Order (Do These Now)

**Session 1** (Today - ~1 hour):
1. ✅ Add Perplexity AI (20 min)
2. ✅ Database layer + Save functionality (30 min)
3. ✅ Basic history viewer (10 min)

**Session 2** (Next time - ~1 hour):
4. ✅ Document upload (30 min)
5. ✅ Enhanced history with search (20 min)
6. ✅ Export functionality (10 min)

---

## 📊 Database Schema

```sql
-- Comparisons table
CREATE TABLE comparisons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    document_content TEXT,
    document_name TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    saved BOOLEAN DEFAULT 0,
    tags TEXT
);

-- Responses table
CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comparison_id INTEGER,
    ai_provider TEXT NOT NULL,
    model_name TEXT NOT NULL,
    response_text TEXT NOT NULL,
    response_time REAL,
    success BOOLEAN,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comparison_id) REFERENCES comparisons(id)
);
```

---

## 🔑 New API Keys Needed

**Perplexity AI**:
- Sign up: https://www.perplexity.ai/settings/api
- Free tier: $5 credits
- Add to `.env`: `PERPLEXITY_API_KEY=pplx-xxxxx`

---

## 🎨 UI Changes

**Current**: 3 cards in a row (horizontal)
**New**: 2x2 grid (4 cards)

```
┌─────────────┬─────────────┐
│  GPT-4o     │  Claude 4   │
├─────────────┼─────────────┤
│  Gemini 2.5 │ Perplexity  │
└─────────────┴─────────────┘
```

**New Components**:
- 📁 File upload button
- 💾 Save comparison button
- 📜 View history button
- 🏷️ Tag input for saved comparisons

---

## 🚀 Ready to Start?

Say the word and I'll begin implementing:
1. Perplexity integration
2. Database layer
3. Save functionality

This will take about **1 hour total** to get working!
=======
# TriAI Compare - Enhancement Implementation Plan

## 🎯 Goal
Transform TriAI Compare into a full-featured AI workbench with:
- Document analysis
- Conversation history
- 4 AI models (add Perplexity)
- Flexible configuration

---

## 📦 Phase 1: Foundation (Start Now)

### 1.1 Database Layer
**Purpose**: Save all comparisons for history/review

**Tasks**:
- [ ] Create SQLite database schema
- [ ] Add `Comparison` table (id, question, timestamp, metadata)
- [ ] Add `Response` table (id, comparison_id, ai_name, response, time, model)
- [ ] Create database helper functions (save, retrieve, search)

**Files to create**:
- `database.py` - Database models and operations
- `comparisons.db` - SQLite database (auto-created)

**Estimated time**: 15 minutes

---

### 1.2 Add Perplexity AI
**Purpose**: Add 4th AI for search-enhanced responses

**Tasks**:
- [ ] Add Perplexity API integration
- [ ] Update frontend to show 4 cards (2x2 grid)
- [ ] Add PERPLEXITY_API_KEY to .env
- [ ] Update parallel query execution

**Files to modify**:
- `app.py` - Add query_perplexity()
- `templates/index.html` - Add 4th card
- `static/style.css` - Update grid to 2x2
- `.env` - Add PERPLEXITY_API_KEY

**Estimated time**: 20 minutes

---

### 1.3 Document Upload
**Purpose**: Upload PDFs, text files, images for AI analysis

**Tasks**:
- [ ] Add file upload UI component
- [ ] Create file processing backend (extract text from PDFs, images)
- [ ] Pass document context to all AIs
- [ ] Support multiple file formats (PDF, TXT, DOCX, images)

**Required libraries**:
```bash
pip install PyPDF2 python-docx Pillow pytesseract
```

**Files to create**:
- `document_processor.py` - Extract text from various formats

**Files to modify**:
- `app.py` - Add /upload endpoint
- `templates/index.html` - Add file upload UI
- `static/app.js` - Handle file upload

**Estimated time**: 30 minutes

---

### 1.4 History & Saved Comparisons
**Purpose**: Browse and review past comparisons

**Tasks**:
- [ ] Create history page/modal
- [ ] Add "Save" button to each comparison
- [ ] Display saved comparisons in a list
- [ ] Add search/filter functionality
- [ ] Export individual comparisons

**Files to create**:
- `templates/history.html` - History browser page

**Files to modify**:
- `app.py` - Add /history route, /api/save endpoint
- `templates/index.html` - Add "View History" button
- `static/style.css` - Style history components

**Estimated time**: 25 minutes

---

## 📦 Phase 2: Advanced Features (Later)

### 2.1 Flexible Configuration
- Adjustable temperature, max_tokens per AI
- Model selection (e.g., GPT-4o vs GPT-4o-mini)
- Custom system prompts per AI

### 2.2 Advanced Export
- Export to PDF with formatting
- Export to Markdown
- Batch export multiple comparisons

### 2.3 Cost Tracking
- Track API usage per query
- Monthly cost dashboard
- Budget alerts

### 2.4 Multi-turn Conversations
- Chat mode with all AIs
- Conversation threading
- Context management

---

## 🎯 Recommended Order (Do These Now)

**Session 1** (Today - ~1 hour):
1. ✅ Add Perplexity AI (20 min)
2. ✅ Database layer + Save functionality (30 min)
3. ✅ Basic history viewer (10 min)

**Session 2** (Next time - ~1 hour):
4. ✅ Document upload (30 min)
5. ✅ Enhanced history with search (20 min)
6. ✅ Export functionality (10 min)

---

## 📊 Database Schema

```sql
-- Comparisons table
CREATE TABLE comparisons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    document_content TEXT,
    document_name TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    saved BOOLEAN DEFAULT 0,
    tags TEXT
);

-- Responses table
CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comparison_id INTEGER,
    ai_provider TEXT NOT NULL,
    model_name TEXT NOT NULL,
    response_text TEXT NOT NULL,
    response_time REAL,
    success BOOLEAN,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comparison_id) REFERENCES comparisons(id)
);
```

---

## 🔑 New API Keys Needed

**Perplexity AI**:
- Sign up: https://www.perplexity.ai/settings/api
- Free tier: $5 credits
- Add to `.env`: `PERPLEXITY_API_KEY=pplx-xxxxx`

---

## 🎨 UI Changes

**Current**: 3 cards in a row (horizontal)
**New**: 2x2 grid (4 cards)

```
┌─────────────┬─────────────┐
│  GPT-4o     │  Claude 4   │
├─────────────┼─────────────┤
│  Gemini 2.5 │ Perplexity  │
└─────────────┴─────────────┘
```

**New Components**:
- 📁 File upload button
- 💾 Save comparison button
- 📜 View history button
- 🏷️ Tag input for saved comparisons

---

## 🚀 Ready to Start?

Say the word and I'll begin implementing:
1. Perplexity integration
2. Database layer
3. Save functionality

This will take about **1 hour total** to get working!
>>>>>>> 6added3 (Initial commit: TriApp multi-AI comparison tool with GPT-5.2, Claude 4.5 Sonnet, Gemini 3.0, and Perplexity Pro support)
