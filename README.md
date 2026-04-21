# 🔬 InsightEngine Pro — Multimodal Research Auditor

An AI-powered research paper auditor built with **Streamlit**, **LangChain**, and **Plotly**.
It extracts deep intelligence from academic PDFs and renders it through a stunning dark-themed dashboard.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Evidence Strength Score** | AI rates 0–100 how well-supported the paper's claims are |
| **Research DNA Barcode** | Paragraph-by-paragraph sentiment mapped to a color strip (Green/Blue/Red) |
| **Methodology Breakdown** | Auto-extracted donut chart of how the paper spends its methodology |
| **Mermaid Flowchart** | AI generates a Mermaid.js flowchart of the research pipeline |
| **Knowledge Graph** | Interactive network of key entities and their relationships |
| **Claim Verification** | Each claim rated Strong/Moderate/Weak with a "Jump to Page" button |
| **Reference Health Check** | Citation freshness histogram + color-coded pills |
| **Conflict of Interest Agent** | Scans for undisclosed funding or COI language |
| **Ask the Paper Chatbot** | Sidebar RAG-style Q&A grounded in the paper text |
| **Audio Abstract** | gTTS-generated audio of the abstract and key contributions |
| **Radar Chart** | Evidence · Novelty · Reproducibility · Recency · Methodology scores |
| **Document Fingerprint** | SHA-256 hash for integrity/plagiarism tracking |
| **Inline PDF Viewer** | Side-by-side PDF with scroll-to-page from claim buttons |

---

## 🚀 Quick Start

```bash
# 1. Clone / copy files
cd insight_engine

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🔑 API Key

- Enter your **OpenAI API key** in the sidebar to analyse real PDFs with GPT-4o-mini.
- Leave it blank to use the built-in **demo data** (no API call needed — great for judging!).

---

## 📐 Architecture

```
app.py
  ├── CSS theming (dark Space Mono / Syne aesthetic)
  ├── Session state management
  ├── PDF extraction (pypdf)
  ├── LangChain → OpenAI GPT-4o-mini
  │     ├── ANALYSIS_PROMPT → JSON schema output
  │     └── CHAT_PROMPT → RAG Q&A
  ├── Plotly charts (barcode, donut, radar, histogram, network)
  ├── Mermaid.js flowchart (streamlit-mermaid)
  ├── PDF viewer (streamlit-pdf-viewer)
  └── gTTS audio generation
```

---

## 📁 File Structure

```
insight_engine/
├── app.py            ← Main Streamlit application
├── requirements.txt  ← Python dependencies
└── README.md         ← This file
```

---

## 🏆 What Makes This Award-Worthy

1. **No hallucination guard** — every claim is linked back to a specific page in the PDF
2. **Holistic scoring** — 5 independent dimensions, not just a summary
3. **Zero-API demo mode** — judges can explore immediately without any setup
4. **Production-grade dark UI** — Space Mono + Syne typography, CSS variables, micro-animations
5. **Conflict-of-interest detection** — proactively flags undisclosed affiliations

---

## 📜 License

MIT — free to use, modify, and distribute.