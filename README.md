# 🚀 AI Code Risk Analyzer  
### Decision-Aware Multi-Agent RAG for Enterprise Codebases

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)
![LLM](https://img.shields.io/badge/LLM-Groq%20LLaMA3.1-purple)
![Deployment](https://img.shields.io/badge/Deployed-Render%20%2B%20Streamlit-orange)

An AI-powered system that analyzes GitHub repositories and predicts the structural and semantic risk of modifying a specific function.

This project combines:

- 📊 Graph-based static code analysis  
- 🧠 LLM-powered risk reasoning (Groq / LLaMA 3.1)  
- 🔍 Dependency graph modeling  
- ⚡ FastAPI backend  
- 🎨 Streamlit multi-page UI  
- ☁️ Cloud deployment  

---

## 🌟 Why This Project?

Modern codebases are complex.

Changing one function can silently break:

- Downstream dependencies  
- Business-critical workflows  
- Security logic  
- Integration points  

This system answers:

> **"If I change this function, how risky is it?"**

---

# 🧠 Architecture Overview
User (Streamlit UI)
↓
FastAPI Backend (Render)
↓
Static Code Analyzer (AST)
↓
Dependency Graph Builder (NetworkX)
↓
Risk Engine (Structural Metrics)
↓
LLM Decision Agent (Groq - LLaMA 3.1)
↓
Final Risk Report



---

# ⚙️ Core Features

## 1️⃣ Repository Upload or GitHub Clone

- Upload ZIP repository  
- Or paste GitHub URL  
- Automatic function scanning  

---

## 2️⃣ Function-Level Risk Analysis

For any selected function, the system computes:

### 📊 Structural Metrics
- Impact Size  
- Dependency Depth  
- Reverse Dependencies  
- Centrality Score  
- Composite Risk Score  

---

## 3️⃣ AI Decision Agent

The LLM evaluates:

- Structural metrics  
- Function source code  
- Contextual signals  

Returns structured output:

```json
{
  "risk_level": "LOW | MEDIUM | HIGH",
  "confidence": 0.85,
  "reasoning": "...",
  "recommended_tests": ["..."]
}
```

## 4️⃣ Dependency Graph Visualization

- Interactive function dependency graph  
- Impact propagation analysis  
- Critical node identification  

Built using **NetworkX + PyVis**.

---

## 5️⃣ Repository-Wide Risk Ranking

Ranks all functions by structural risk.

Helps identify:

- Critical architecture nodes  
- Refactoring priorities  
- High-risk change zones  

---

# 🧩 Tech Stack

## Backend

- FastAPI  
- NetworkX  
- Groq LLaMA 3.1  
- Uvicorn  
- Python 3.11  

## Frontend

- Streamlit  
- Multi-page navigation  
- Interactive metrics  
- Graph visualization  

## Deployment

- Render (Backend)  
- Streamlit Cloud (Frontend)  

---

# 🚀 Local Setup

## 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/code-risk-engine.git
cd code-risk-engine
```

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## 3️⃣ Set Environment Variable
```bash
export GROQ_API_KEY=your_api_key_here
```

## 4️⃣ Run Backend
```bash
uvicorn api.app:app --reload
```
## 5️⃣ Run Streamlit UI
```bash
streamlit run ui/app.py
```
📊 Example Output
Risk Level: MEDIUM
Confidence: 80%

Impact Size: 4
Dependency Depth: 3
Reverse Dependencies: 4
Risk Score: 0.143

AI Reasoning:

The function has multiple downstream dependencies and moderate depth, indicating potential propagation of impact if modified.
