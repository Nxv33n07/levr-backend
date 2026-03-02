# Sorted AI — Levr Financial Advisory Service

A high-precision FastAPI service for financial query classification and human-like advisory responses (Sorted AI) optimized for the Indian financial ecosystem.

---

## 🚀 Overview

Sorted AI is designed to convert unstructured user queries into structured financial intent and actionable, expert-level advice. It doesn't just give information; it finds leaks, identifies gaps, and offers to take action.

### Key Features
*   **Precise Tagging**: Classifies queries into 8 domains (Credit Card, Loans, Tax, Insurance, Investment, Banking, Others).
*   **Expert Advisory**: Generates human-like, conversational responses in 4 lines or less.
*   **Action-Oriented**: Focuses on immediate next steps like comparing, calculating, or flagging.
*   **Indian Context**: Native support for INR, 80C, NPS, UPI, ELSS, and Indian lending/insurance players.

---

## 📂 Project Structure

```bash
app/
├── main.py          # API entry point & GET/POST routing
├── config.py        # Environment-based settings (Pydantic)
├── models.py        # Request/Response schemas (Pydantic)
├── routes.py        # Controller logic for Tagger & Chat
├── tagger/          # Query classification engine
│   ├── prompts.py   # Intent extraction & classification rules
│   └── service.py   # LLM provider integration for tagging
└── chat/            # Advisory response engine (Sorted AI)
    ├── prompts.py   # Human-expert personality & few-shot examples
    └── service.py   # Robust JSON parsing & sanitization
```

---

## 🛠️ Quick Start

### 1. Prerequisites
*   Python 3.10+
*   Groq API Key (or OpenAI/Gemini/Grok)

### 2. Installation
```bash
# Clone and enter directory
cd back-end

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file based on the example:
```bash
cp .env.example .env
```
Add your `GROQ_API_KEY` to the `.env` file.

### 4. Run the Server
```bash
python -m app.main
# Service starts on http://localhost:8000
```

---

## 📖 API Documentation

### POST `/tag`
**Classification Engine**
Categorizes a financial query with high confidence.

**Request:**
```json
{
  "query": "Should I invest in ELSS for 80C tax saving?",
  "include_reasoning": true
}
```

---

### POST `/chat` (Sorted AI)
**Advisory Engine**
Generates a human-expert response with structured data.

**Request:**
```json
{
  "query": "Which credit card should I use for flights vs groceries?"
}
```

**Response Sample:**
```json
{
  "success": true,
  "data": {
    "primary_tag": "credit_card",
    "primary_confidence": 0.95,
    "secondary_tag": null,
    "interpreted_query": "User wants to optimize credit card usage for rewards",
    "response": "Most people leave serious rewards on the table by swiping the wrong card.\nI can map exactly which card wins on flights, groceries, and dining.\nSome combos unlock 4–5x the points you're currently earning.\nShare your card names and I'll do the full mapping right now.",
    "suggestions": ["Spending category to card mapping", "Reward points audit"],
    "related_topics": ["Credit Card Reward Optimization", "Milestone Benefits"]
  }
}
```

---

## 🏷️ Financial Domains

| Tag | Scope |
| :--- | :--- |
| `credit_card` | Comparison, Rewards, Milestone benefits, Limits |
| `loans` | Home/Personal loans, EMIs, Refinance, Credit Card Debt |
| `tax` | Income tax, ITR, 80C, 80D deductions, Refunds |
| `insurance` | Health, Life, Term, Comparison, Claims settlement |
| `investment` | Mutual Funds, SIP, Stocks, Portfolio allocation, Retirement |
| `banking` | FD, Savings accounts, Hidden charges, Account switch |
| `others` | UPI, Payments, Budgeting, Expense tracking |

---

## 🐳 Docker Usage

Build and run the containerized service:
```bash
# Build & Start
docker-compose up -d --build

# Logs
docker logs -f levr-backend
```

---

## ☁️ Cloud Deployment (Sorted AI)

The service is pre-configured for **Railway** or **Render** using the provided `Dockerfile`.

1.  **Repo**: Push this code to a GitHub repository.
2.  **Connect**: Link the repo to Railway/Render.
3.  **Variables**: Add `GROQ_API_KEY` and `LLM_PROVIDER=groq` in the environment tab.
4.  **Port**: The API uses the dynamic `$PORT` provided by the host.

---

## 🧪 Interactive Docs
Once running, visit:
*   **Swagger UI**: `http://localhost:8000/docs`
*   **ReDoc**: `http://localhost:8000/redoc`
# levr-backend
