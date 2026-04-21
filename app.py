"""
InsightEngine Pro — Multimodal Research Auditor
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import re
import random
import hashlib
from datetime import datetime

import math
import nltk
from collections import Counter

# Ensure VADER lexicon is available
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

# ── Page config (MUST be first Streamlit call) ──────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="InsightEngine Pro",
    page_icon="🔬",
    initial_sidebar_state="expanded",
)

# ── Inject custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');

:root {
  --bg:         #0a0c14;
  --surface:    #111420;
  --surface2:   #181c2e;
  --border:     #252a40;
  --accent:     #5b8af0;
  --accent2:    #a78bfa;
  --accent3:    #34d399;
  --warn:       #f59e0b;
  --danger:     #f87171;
  --text:       #e2e8f0;
  --muted:      #64748b;
  --mono:       'Space Mono', monospace;
  --sans:       'Syne', sans-serif;
  --body:       'Inter', sans-serif;
}

html, body, [data-testid="stApp"] {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: var(--body);
}

/* Hide Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none; }

/* Custom scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* ── Hero banner ── */
.hero {
  background: linear-gradient(135deg, #0d1117 0%, #131929 50%, #0d1117 100%);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px 36px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
}
.hero::before {
  content: '';
  position: absolute;
  top: -60px; right: -60px;
  width: 220px; height: 220px;
  background: radial-gradient(circle, rgba(91,138,240,0.15) 0%, transparent 70%);
  border-radius: 50%;
}
.hero-title {
  font-family: var(--sans);
  font-size: 2.1rem;
  font-weight: 800;
  background: linear-gradient(90deg, #5b8af0, #a78bfa, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 6px 0;
  letter-spacing: -0.5px;
}
.hero-sub {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--muted);
  letter-spacing: 2px;
  text-transform: uppercase;
}

/* ── Metric cards ── */
.metric-row { display: flex; gap: 12px; margin: 16px 0; }
.metric-card {
  flex: 1;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 20px;
  position: relative;
}
.metric-card .label {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--muted);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.metric-card .value {
  font-family: var(--sans);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text);
}
.metric-card .badge {
  position: absolute;
  top: 14px; right: 14px;
  font-size: 1.2rem;
}
.metric-card .delta {
  font-size: 0.72rem;
  color: var(--accent3);
  margin-top: 4px;
}

/* ── Section headers ── */
.section-head {
  font-family: var(--sans);
  font-size: 1rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: 0.3px;
  margin: 20px 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-head::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

/* ── Claim cards ── */
.claim-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid;
  border-radius: 8px;
  padding: 14px 18px;
  margin-bottom: 10px;
  transition: border-color 0.2s;
}
.claim-strong  { border-left-color: #34d399; }
.claim-moderate { border-left-color: #f59e0b; }
.claim-weak    { border-left-color: #f87171; }
.claim-title {
  font-family: var(--mono);
  font-size: 0.8rem;
  color: var(--text);
  margin-bottom: 6px;
}
.claim-meta {
  font-size: 0.72rem;
  color: var(--muted);
}

/* ── Reference pill ── */
.ref-pill {
  display: inline-block;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 4px 12px;
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--muted);
  margin: 3px;
}
.ref-fresh { border-color: #34d399; color: #34d399; }
.ref-mid   { border-color: #f59e0b; color: #f59e0b; }
.ref-stale { border-color: #f87171; color: #f87171; }

/* ── Chat bubble ── */
.chat-user {
  background: var(--accent);
  color: #fff;
  padding: 10px 16px;
  border-radius: 16px 16px 4px 16px;
  margin: 8px 0 8px 40px;
  font-size: 0.85rem;
}
.chat-ai {
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 10px 16px;
  border-radius: 16px 16px 16px 4px;
  margin: 8px 40px 8px 0;
  font-size: 0.85rem;
  line-height: 1.55;
}
.chat-label {
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--muted);
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 4px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: var(--text) !important; }

/* ── Tab styling ── */
[data-testid="stTabs"] [role="tab"] {
  font-family: var(--mono) !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.5px;
}

/* ── Streamlit elements override ── */
.stButton > button {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  font-family: var(--mono) !important;
  font-size: 0.72rem !important;
  border-radius: 6px !important;
  transition: border-color 0.2s, background 0.2s !important;
}
.stButton > button:hover {
  border-color: var(--accent) !important;
  background: rgba(91,138,240,0.1) !important;
}
.stTextInput input, .stTextArea textarea {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  font-family: var(--body) !important;
  border-radius: 8px !important;
}
div[data-testid="stAlert"] {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}
.stProgress > div > div {
  background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
}

/* ── Barcode container ── */
.barcode-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  margin: 12px 0;
}
.barcode-label {
  font-family: var(--mono);
  font-size: 0.62rem;
  color: var(--muted);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 10px;
}

/* ── Status badge ── */
.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  font-family: var(--mono);
  font-size: 0.65rem;
  letter-spacing: 0.5px;
}
.badge-green { background: rgba(52,211,153,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
.badge-yellow { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.badge-red { background: rgba(248,113,113,0.15); color: #f87171; border: 1px solid rgba(248,113,113,0.3); }
.badge-blue { background: rgba(91,138,240,0.15); color: #5b8af0; border: 1px solid rgba(91,138,240,0.3); }

/* ── Knowledge graph placeholder ── */
.kg-node {
  display: inline-block;
  background: var(--surface2);
  border: 1px solid var(--accent);
  border-radius: 20px;
  padding: 5px 14px;
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--accent);
  margin: 4px;
}
.kg-edge {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--muted);
  padding: 2px 8px;
}

/* ── Fingerprint / hash display ── */
.fingerprint {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--accent3);
  letter-spacing: 1px;
  word-break: break-all;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  margin-top: 8px;
}

/* ── Timeline ── */
.timeline-item {
  display: flex;
  gap: 14px;
  margin-bottom: 14px;
  align-items: flex-start;
}
.timeline-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  background: var(--accent);
  margin-top: 4px;
  flex-shrink: 0;
}
.timeline-content { flex: 1; }
.timeline-date {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--muted);
}
.timeline-text { font-size: 0.82rem; color: var(--text); }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
for key, default in {
    "target_page": 1,
    "analysis_done": False,
    "chat_history": [],
    "paper_data": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Helpers ──────────────────────────────────────────────────────────────────

def paper_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


# ── Local NLP analyser (no API key required) ──────────────────────────────────

def _sentences(text: str) -> list:
    try:
        return nltk.sent_tokenize(text)
    except Exception:
        return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def _extract_title(text: str) -> str:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # First non-trivial line that isn't all-caps noise
    for line in lines[:15]:
        if 10 < len(line) < 200 and not line.startswith("http"):
            return line
    return "Untitled Paper"


def _extract_abstract(text: str) -> str:
    m = re.search(r'(?i)abstract[:\s]*([\s\S]{100,1200}?)(?=\n\s*\n|\nintroduction|\n1\.)', text)
    if m:
        return " ".join(m.group(1).split())
    # fallback: first 3 sentences
    sents = _sentences(text)
    return " ".join(sents[:3])


def _sentiment_barcode(text: str, n: int = 30) -> list:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    sents = _sentences(text)
    step = max(1, len(sents) // n)
    result = []
    for i in range(0, min(len(sents), n * step), step):
        score = sia.polarity_scores(sents[i])["compound"]
        if score >= 0.05:   result.append("positive")
        elif score <= -0.05: result.append("negative")
        else:                result.append("objective")
        if len(result) == n:
            break
    return result or ["objective"] * n


def _score_evidence(text: str) -> int:
    strong = len(re.findall(r'\b(p\s*[<=>]\s*0\.0\d|confidence interval|statistically significant|validated|cross.validat|benchmark|baseline|outperform)', text, re.I))
    weak   = len(re.findall(r'\b(suggest|may|might|could|preliminary|limited|small sample|future work)', text, re.I))
    raw = min(100, 40 + strong * 4 - weak * 2)
    return max(10, raw)


def _score_novelty(text: str) -> int:
    hits = len(re.findall(r'\b(novel|first|new approach|propose|introduce|state.of.the.art|outperform|breakthrough|innovative)', text, re.I))
    return min(95, 35 + hits * 5)


def _score_reproducibility(text: str) -> int:
    hits = len(re.findall(r'\b(code|github|open.source|available|reproducib|dataset released|implementation|hyperparameter|ablation)', text, re.I))
    return min(95, 30 + hits * 6)


def _methodology_breakdown(text: str) -> dict:
    sections = {
        "Data Collection":   len(re.findall(r'\b(dataset|data collect|corpus|annotate|crawl|sampl)', text, re.I)),
        "Model Architecture": len(re.findall(r'\b(layer|encoder|decoder|transformer|network|architecture|model)', text, re.I)),
        "Training":          len(re.findall(r'\b(train|epoch|batch|loss|optim|gradient|learning rate)', text, re.I)),
        "Evaluation":        len(re.findall(r'\b(accuracy|f1|precision|recall|AUC|BLEU|ROUGE|metric|evaluat)', text, re.I)),
        "Ablation Study":    len(re.findall(r'\b(ablat|variant|without|w/o|component|contribution)', text, re.I)),
    }
    sections = {k: max(1, v) for k, v in sections.items()}
    total = sum(sections.values())
    return {
        "labels": list(sections.keys()),
        "values": [round(v / total * 100) for v in sections.values()],
    }


def _extract_claims(text: str, n: int = 5) -> list:
    sents = _sentences(text)
    claim_patterns = re.compile(
        r'\b(achiev|outperform|demonstrat|show|result|accura|improv|reduc|increas|signific)', re.I
    )
    scored = [(s, len(claim_patterns.findall(s))) for s in sents if 30 < len(s) < 300]
    scored.sort(key=lambda x: -x[1])
    claims = []
    for s, score in scored[:n]:
        strength = "Strong" if score >= 3 else "Moderate" if score >= 1 else "Weak"
        claims.append({"text": s[:120], "page_hint": 1, "strength": strength,
                       "rationale": f"Keyword density score: {score}"})
    return claims


def _extract_entities(text: str) -> list:
    entities = []
    for m in re.finditer(r'\b([A-Z][a-zA-Z]+-?\d*(?:\s[A-Z][a-zA-Z]+){0,3})\b', text):
        e = m.group(1).strip()
        if 3 < len(e) < 50 and not e.isupper():
            entities.append(e)
    counts = Counter(entities).most_common(10)
    result = []
    for name, _ in counts:
        if re.search(r'\b(dataset|corpus|bench)', name, re.I):  t = "Dataset"
        elif re.search(r'\b(university|institute|lab|center)', name, re.I): t = "Institution"
        elif re.search(r'\b(network|model|transformer|bert|gpt)', name, re.I): t = "Method"
        else: t = "Other"
        result.append({"entity": name, "type": t})
    return result


def _extract_references(text: str) -> list:
    refs = []
    for m in re.finditer(r'([A-Z][^.\n]{5,80}?)[\.\s]+\(?([12][0-9]{3})\)?', text):
        year = int(m.group(2))
        if 1950 <= year <= datetime.now().year:
            refs.append({"citation": m.group(1).strip()[:80], "year": year,
                         "journal": "Unknown", "impact": "Unknown"})
    seen, unique = set(), []
    for r in refs:
        key = r["citation"][:30]
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique[:12] or [{"citation": "No references detected", "year": datetime.now().year,
                            "journal": "N/A", "impact": "Unknown"}]


def _extract_coi(text: str):
    m = re.search(r'(?i)(conflict.{0,10}interest|disclosure|funding|grant|sponsor)[^\n]{0,300}', text)
    return m.group(0).strip() if m else None


def _build_mermaid(text: str) -> str:
    headings = re.findall(r'(?m)^(?:\d+\.?\s+)?([A-Z][A-Za-z ]{3,40})$', text)
    headings = [h.strip() for h in headings if len(h.strip()) > 4][:6]
    if len(headings) < 2:
        headings = ["Introduction", "Methodology", "Experiments", "Results", "Conclusion"]
    nodes = [f'    {chr(65+i)}[{h}]' for i, h in enumerate(headings)]
    edges = " --> ".join(chr(65+i) for i in range(len(headings)))
    return "graph LR\n" + "\n".join(nodes) + "\n    " + edges


def _chat_answer(question: str, paper_text: str) -> str:
    """Simple keyword search over paper sentences."""
    q_words = set(re.findall(r'\w+', question.lower())) - {"the","a","is","in","of","and","to","what","how","why","does"}
    sents = _sentences(paper_text)
    scored = [(s, sum(1 for w in q_words if w in s.lower())) for s in sents]
    scored.sort(key=lambda x: -x[1])
    top = [s for s, sc in scored[:3] if sc > 0]
    return " ".join(top) if top else "I could not find a relevant passage in the paper for that question."


def analyse_pdf_locally(paper_text: str) -> dict:
    t = paper_text
    return {
        "title":                  _extract_title(t),
        "abstract_summary":       _extract_abstract(t),
        "evidence_strength_score": _score_evidence(t),
        "evidence_rationale":     "Scored by keyword density: statistical terms, validation language, and hedging words.",
        "methodology_breakdown":  _methodology_breakdown(t),
        "sentiment_barcode":      _sentiment_barcode(t),
        "claims":                 _extract_claims(t),
        "entities":               _extract_entities(t),
        "relationships":          [],
        "references":             _extract_references(t),
        "conflict_of_interest":   _extract_coi(t),
        "mermaid_flowchart":      _build_mermaid(t),
        "limitations":            [s[:120] for s in _sentences(re.sub(r'[\s\S]*?(?=limitation)', '', t, flags=re.I))[:4]] or ["No limitations section detected."],
        "novelty_score":          _score_novelty(t),
        "reproducibility_score":  _score_reproducibility(t),
        "key_contributions":      [s[:120] for s in _sentences(t) if re.search(r'\b(contribut|propose|introduc|present)', s, re.I)][:3] or ["See abstract for contributions."],
    }


def color_for_strength(s: str) -> str:
    s = s.lower()
    if "strong" in s:   return "claim-strong"
    if "moderate" in s: return "claim-moderate"
    return "claim-weak"


def strength_emoji(s: str) -> str:
    s = s.lower()
    if "strong" in s:   return "🟢"
    if "moderate" in s: return "🟡"
    return "🔴"


def ref_class(year: int) -> str:
    age = datetime.now().year - year
    if age <= 5:  return "ref-fresh"
    if age <= 12: return "ref-mid"
    return "ref-stale"


# ── Demo data (shown when no PDF uploaded) ───────────────────────────────────

DEMO_DATA = {
    "title": "Deep Learning for Carbon Sequestration Prediction in Boreal Forests",
    "abstract_summary": "This paper proposes a transformer-based model to predict carbon sequestration rates in boreal forests using satellite imagery. The model achieves 94.2% accuracy on a held-out test set of 1,200 forest patches. Results suggest AI-driven monitoring could reduce field survey costs by 60%.",
    "evidence_strength_score": 74,
    "evidence_rationale": "Strong quantitative results with clear metrics. However, external validation on non-boreal biomes is absent and sample selection criteria lack detail.",
    "methodology_breakdown": {
        "labels": ["Data Collection", "Model Architecture", "Training", "Evaluation", "Ablation Study"],
        "values": [22, 35, 18, 17, 8]
    },
    "sentiment_barcode": [
        "objective","objective","positive","objective","negative","objective",
        "positive","positive","objective","negative","objective","positive",
        "objective","positive","objective","negative","positive","objective",
        "positive","positive","objective","positive","objective","negative",
        "positive","objective","objective","positive","positive","objective"
    ],
    "claims": [
        {"text": "Model achieves 94.2% prediction accuracy", "page_hint": 5, "strength": "Strong", "rationale": "Backed by 5-fold cross-validation on 1,200 samples with p < 0.001"},
        {"text": "60% reduction in field survey costs", "page_hint": 8, "strength": "Moderate", "rationale": "Based on cost estimates from a single partner institution; not independently verified"},
        {"text": "No significant overfitting observed", "page_hint": 6, "strength": "Moderate", "rationale": "Training vs. validation loss curves shown but held-out test period is only 6 months"},
        {"text": "Outperforms all prior baselines", "page_hint": 7, "strength": "Strong", "rationale": "Comprehensive comparison table against 7 prior methods with statistical significance"},
        {"text": "Generalises to tropical rainforests", "page_hint": 11, "strength": "Weak", "rationale": "Only one small tropical dataset tested; confidence intervals are very wide"},
    ],
    "entities": [
        {"entity": "Vision Transformer (ViT)", "type": "Method"},
        {"entity": "Landsat-8 Imagery", "type": "Dataset"},
        {"entity": "Carbon Flux Network", "type": "Institution"},
        {"entity": "Cross-entropy Loss", "type": "Method"},
        {"entity": "Boreal Forest Patches", "type": "Dataset"},
        {"entity": "CO₂ Sequestration Rate", "type": "Finding"},
        {"entity": "Sentinel-2", "type": "Dataset"},
        {"entity": "Finnish Meteorological Institute", "type": "Institution"},
    ],
    "relationships": [
        {"from": "Vision Transformer (ViT)", "relation": "trained on", "to": "Landsat-8 Imagery"},
        {"from": "Vision Transformer (ViT)", "relation": "predicts", "to": "CO₂ Sequestration Rate"},
        {"from": "Carbon Flux Network", "relation": "provided", "to": "Boreal Forest Patches"},
        {"from": "Finnish Meteorological Institute", "relation": "validated", "to": "CO₂ Sequestration Rate"},
        {"from": "Sentinel-2", "relation": "supplements", "to": "Landsat-8 Imagery"},
    ],
    "references": [
        {"citation": "Vaswani et al., Attention Is All You Need", "year": 2017, "journal": "NeurIPS", "impact": "High"},
        {"citation": "Pan et al., Global Forest Carbon", "year": 2022, "journal": "Nature Climate Change", "impact": "High"},
        {"citation": "Dosovitskiy et al., ViT", "year": 2020, "journal": "ICLR", "impact": "High"},
        {"citation": "Smith & Jones, Remote Sensing Methods", "year": 2011, "journal": "Remote Sensing Environ.", "impact": "Medium"},
        {"citation": "Brown et al., Carbon Accounting", "year": 2015, "journal": "Forest Ecology", "impact": "Medium"},
        {"citation": "Garcia, Satellite Validation Study", "year": 2023, "journal": "arXiv", "impact": "Low"},
        {"citation": "Wilson et al., Boreal Ecology", "year": 2008, "journal": "Ecology Letters", "impact": "Medium"},
        {"citation": "Chen & Liu, Deep Learning Survey", "year": 2021, "journal": "IEEE TPAMI", "impact": "High"},
    ],
    "conflict_of_interest": "Lead author (Dr. A. Nielsen) is a paid scientific advisor to GreenSat Ltd., which sells satellite analysis software. No formal disclosure appears in the paper.",
    "mermaid_flowchart": "graph LR\n    A[Satellite Image Acquisition\nLandsat-8 & Sentinel-2] --> B[Preprocessing\nAtmospheric Correction]\n    B --> C[Patch Extraction\n256×256 tiles]\n    C --> D[Vision Transformer\nViT-B/16]\n    D --> E[Regression Head]\n    E --> F[CO₂ Prediction\nkg C / m² / yr]\n    F --> G[Evaluation\n5-fold CV]\n    G --> H{Accuracy > 90%?}\n    H -->|Yes| I[Deploy to Monitoring API]\n    H -->|No| D",
    "limitations": [
        "Tested exclusively on boreal biomes; tropical generalisability unproven",
        "Ground-truth labels from a single flux-tower network with known gaps",
        "Model latency (2.3s/patch) may limit real-time applications",
        "No uncertainty quantification provided for individual predictions",
    ],
    "novelty_score": 81,
    "reproducibility_score": 63,
    "key_contributions": [
        "First transformer-based architecture applied to pan-boreal carbon flux mapping",
        "A new public benchmark dataset: BorealCarbonBench-1200",
        "Cost-efficiency analysis framework for AI vs. field surveys",
    ],
}

# ── PDF text extraction ───────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    except Exception:
        return ""

# ── UI Components ─────────────────────────────────────────────────────────────

def render_hero():
    st.markdown("""
    <div class="hero">
      <div class="hero-title">🔬 InsightEngine Pro</div>
      <div class="hero-sub">Multimodal Research Auditor · Evidence Intelligence · AI-Powered</div>
    </div>
    """, unsafe_allow_html=True)


def render_metrics(data: dict):
    ev  = data["evidence_strength_score"]
    nov = data["novelty_score"]
    rep = data["reproducibility_score"]
    refs = data["references"]
    fresh = sum(1 for r in refs if datetime.now().year - r["year"] <= 5)

    def score_color(v):
        if v >= 75: return "#34d399"
        if v >= 50: return "#f59e0b"
        return "#f87171"

    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card">
        <div class="label">Evidence Strength</div>
        <div class="value" style="color:{score_color(ev)}">{ev}<span style="font-size:1rem;color:var(--muted)">/100</span></div>
        <div class="delta">{"↑ Well-supported" if ev>=70 else "↓ Needs scrutiny"}</div>
        <div class="badge">⚖️</div>
      </div>
      <div class="metric-card">
        <div class="label">Novelty Index</div>
        <div class="value" style="color:{score_color(nov)}">{nov}<span style="font-size:1rem;color:var(--muted)">/100</span></div>
        <div class="delta">{"↑ Highly original" if nov>=70 else "Incremental advance"}</div>
        <div class="badge">💡</div>
      </div>
      <div class="metric-card">
        <div class="label">Reproducibility</div>
        <div class="value" style="color:{score_color(rep)}">{rep}<span style="font-size:1rem;color:var(--muted)">/100</span></div>
        <div class="delta">{"↑ Good" if rep>=70 else "⚠ Gaps exist"}</div>
        <div class="badge">🔁</div>
      </div>
      <div class="metric-card">
        <div class="label">Fresh Citations</div>
        <div class="value" style="color:{score_color(int(fresh/max(len(refs),1)*100))}">{fresh}<span style="font-size:1rem;color:var(--muted)">/{len(refs)}</span></div>
        <div class="delta">≤5 years old</div>
        <div class="badge">📚</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_barcode(sentiments: list):
    color_map = {"positive": "#34d399", "negative": "#f87171", "objective": "#5b8af0"}
    colors = [color_map.get(s, "#5b8af0") for s in sentiments]

    # Build barcode as a bar chart (one bar per segment, no gaps)
    fig = go.Figure(go.Bar(
        x=list(range(len(colors))),
        y=[1] * len(colors),
        marker_color=colors,
        hovertext=sentiments,
        hoverinfo="text",
    ))
    fig.update_layout(
        height=56,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False, showgrid=False, zeroline=False),
        yaxis=dict(visible=False, showgrid=False, zeroline=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        bargap=0,
        showlegend=False,
    )
    st.markdown('<div class="barcode-label">🧬 PAPER DNA BARCODE — Emotional Flow (Green=Positive · Blue=Objective · Red=Critical)</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Compact legend
    pos = sentiments.count("positive")
    neg = sentiments.count("negative")
    obj = sentiments.count("objective")
    total = len(sentiments)
    lcol1, lcol2, lcol3 = st.columns(3)
    lcol1.markdown(f'<span class="badge badge-green">🟢 Positive {pos/total*100:.0f}%</span>', unsafe_allow_html=True)
    lcol2.markdown(f'<span class="badge badge-blue">🔵 Objective {obj/total*100:.0f}%</span>', unsafe_allow_html=True)
    lcol3.markdown(f'<span class="badge badge-red">🔴 Critical {neg/total*100:.0f}%</span>', unsafe_allow_html=True)


def render_methodology_chart(breakdown: dict):
    fig = px.pie(
        names=breakdown["labels"],
        values=breakdown["values"],
        hole=0.55,
        color_discrete_sequence=["#5b8af0","#a78bfa","#34d399","#f59e0b","#f87171","#06b6d4"],
    )
    fig.update_traces(textposition='outside', textfont_size=11, textfont_color="#e2e8f0")
    fig.update_layout(
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        showlegend=True,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", size=11),
            orientation="v",
        ),
        margin=dict(l=0,r=0,t=20,b=0),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_claims(claims: list):
    for c in claims:
        cls = color_for_strength(c["strength"])
        em  = strength_emoji(c["strength"])
        st.markdown(f"""
        <div class="claim-card {cls}">
          <div class="claim-title">{em} {c['text']}</div>
          <div class="claim-meta">
            Strength: <b>{c['strength']}</b> &nbsp;·&nbsp; {c['rationale']}
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"📌 Jump to page {c['page_hint']}", key=f"claim_{c['text'][:20]}"):
            st.session_state.target_page = c["page_hint"]
            st.rerun()


def render_knowledge_graph(entities: list, relationships: list):
    # Entity type → color
    type_color = {
        "Method": "#5b8af0", "Finding": "#34d399", "Dataset": "#a78bfa",
        "Institution": "#f59e0b", "Drug": "#f87171", "Other": "#64748b",
    }
    # Build plotly scatter network
    import math
    n = len(entities)
    angles = [2*math.pi*i/n for i in range(n)]
    ex = [math.cos(a) for a in angles]
    ey = [math.sin(a) for a in angles]
    entity_idx = {e["entity"]: i for i, e in enumerate(entities)}

    edge_x, edge_y = [], []
    for r in relationships:
        if r["from"] in entity_idx and r["to"] in entity_idx:
            i, j = entity_idx[r["from"]], entity_idx[r["to"]]
            edge_x += [ex[i], ex[j], None]
            edge_y += [ey[i], ey[j], None]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines",
                             line=dict(color="#252a40", width=1.5), hoverinfo="none"))
    for ent, i in entity_idx.items():
        t = entities[i]["type"]
        fig.add_trace(go.Scatter(
            x=[ex[i]], y=[ey[i]],
            mode="markers+text",
            marker=dict(size=16, color=type_color.get(t,"#64748b"), line=dict(color="#0a0c14",width=2)),
            text=[ent], textposition="top center",
            textfont=dict(color="#e2e8f0", size=9, family="Space Mono"),
            hovertemplate=f"<b>{ent}</b><br>Type: {t}<extra></extra>",
            showlegend=False,
        ))
    fig.update_layout(
        height=340,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,20,32,1)",
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        margin=dict(l=0,r=0,t=0,b=0),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("**Relationships detected:**")
    for r in relationships:
        st.markdown(
            f'<span class="kg-node">{r["from"]}</span>'
            f'<span class="kg-edge"> ──{r["relation"]}──▶ </span>'
            f'<span class="kg-node">{r["to"]}</span>',
            unsafe_allow_html=True
        )


def render_references(refs: list):
    now = datetime.now().year
    fresh = [r for r in refs if now - r["year"] <= 5]
    mid   = [r for r in refs if 5 < now - r["year"] <= 12]
    stale = [r for r in refs if now - r["year"] > 12]

    c1, c2, c3 = st.columns(3)
    c1.metric("🟢 Fresh (≤5 yr)", len(fresh))
    c2.metric("🟡 Aging (6-12 yr)", len(mid))
    c3.metric("🔴 Stale (>12 yr)", len(stale))

    # Timeline chart
    years = [r["year"] for r in refs]
    fig = px.histogram(x=years, nbins=15,
                       color_discrete_sequence=["#5b8af0"],
                       labels={"x":"Year","y":"Count"})
    fig.update_layout(
        height=180,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,20,32,1)",
        font_color="#e2e8f0",
        margin=dict(l=0,r=0,t=10,b=0),
        xaxis=dict(gridcolor="#252a40"),
        yaxis=dict(gridcolor="#252a40"),
        bargap=0.1,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    for r in refs:
        cls = ref_class(r["year"])
        st.markdown(
            f'<span class="ref-pill {cls}">📄 {r["citation"]} ({r["year"]}) — {r["journal"]} [{r["impact"]}]</span>',
            unsafe_allow_html=True
        )


def render_mermaid(mermaid_str: str):
    try:
        import streamlit_mermaid as stmd
        stmd.st_mermaid(mermaid_str, height="340px")
    except Exception:
        st.code(mermaid_str, language="text")


def render_audio(text: str):
    try:
        from gtts import gTTS
        tts = gTTS(text=text[:500], lang="en", slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3")
    except Exception as e:
        st.warning(f"Audio generation unavailable: {e}")


def render_fingerprint(pdf_bytes: bytes):
    h = paper_hash(pdf_bytes)
    st.markdown(f"""
    <div style="margin-top:8px">
      <div class="barcode-label">📋 DOCUMENT FINGERPRINT (SHA-256)</div>
      <div class="fingerprint">{h}</div>
    </div>
    """, unsafe_allow_html=True)


def render_pdf(pdf_bytes: bytes, target_page: int):
    try:
        from streamlit_pdf_viewer import pdf_viewer
        pdf_viewer(pdf_bytes, scroll_to_page=target_page, height=640)
    except Exception:
        st.info("Install `streamlit-pdf-viewer` for inline PDF rendering.")
        st.download_button("⬇ Download PDF", pdf_bytes, "paper.pdf", "application/pdf")


def render_coi(coi):
    if coi:
        st.markdown(f"""
        <div style="background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.3);
                    border-radius:8px;padding:14px 18px;margin-bottom:12px">
          <div style="font-family:var(--mono);font-size:0.65rem;color:#f87171;
                      letter-spacing:1px;text-transform:uppercase;margin-bottom:6px">
            ⚠ Conflict of Interest Detected
          </div>
          <div style="font-size:0.82rem;color:#e2e8f0">{coi}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-green">✓ No COI Detected</span>', unsafe_allow_html=True)


def render_limitations(lims: list):
    for i, l in enumerate(lims, 1):
        st.markdown(f"""
        <div style="display:flex;gap:10px;margin-bottom:8px;align-items:flex-start">
          <span style="font-family:var(--mono);font-size:0.65rem;color:var(--warn);
                       background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2);
                       border-radius:4px;padding:1px 7px;flex-shrink:0">L{i}</span>
          <span style="font-size:0.82rem;color:var(--text)">{l}</span>
        </div>
        """, unsafe_allow_html=True)


def render_contributions(contribs: list):
    for c in contribs:
        st.markdown(f"""
        <div style="display:flex;gap:10px;margin-bottom:6px;align-items:flex-start">
          <span style="color:#34d399;flex-shrink:0">✦</span>
          <span style="font-size:0.82rem;color:var(--text)">{c}</span>
        </div>
        """, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.success("✅ Runs fully offline — no API key needed", icon="🔒")
    st.markdown("---")

    if st.session_state.analysis_done and st.session_state.paper_data:
        data = st.session_state.paper_data
        coi = data.get("conflict_of_interest")
        render_coi(coi)
        st.markdown("---")

    st.markdown("### 💬 Ask the Paper")
    if not st.session_state.analysis_done:
        st.caption("Upload and analyse a paper first.")
    else:
        # Display history
        for msg in st.session_state.chat_history[-6:]:
            role = msg["role"]
            bubble = "chat-user" if role == "user" else "chat-ai"
            label  = "YOU" if role == "user" else "AI AUDITOR"
            st.markdown(f'<div class="chat-label">{label}</div><div class="{bubble}">{msg["content"]}</div>',
                        unsafe_allow_html=True)

        question = st.chat_input("Ask about methodology, limitations…")
        if question:
            st.session_state.chat_history.append({"role":"user","content":question})
            paper_text = st.session_state.get("paper_text", "")
            answer = _chat_answer(question, paper_text) if paper_text.strip() else \
                "No paper text available. Please upload a PDF first."
            st.session_state.chat_history.append({"role":"assistant","content":answer})
            st.rerun()


# ── Main layout ───────────────────────────────────────────────────────────────

render_hero()

pdf_col, analysis_col = st.columns([1, 1], gap="large")

with pdf_col:
    st.markdown('<div class="section-head">📄 Source Document</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Research PDF", type="pdf", label_visibility="collapsed")

    run_analysis = False

    if uploaded_file:
        st.session_state["pdf_bytes"] = uploaded_file.getvalue()

    pdf_bytes = st.session_state.get("pdf_bytes") if uploaded_file else None

    if pdf_bytes:
        render_fingerprint(pdf_bytes)
        render_pdf(pdf_bytes, st.session_state.target_page)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚀 Run Full Analysis", use_container_width=True):
                run_analysis = True
        with col_b:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.analysis_done = False
                st.session_state.paper_data = None
                st.session_state.chat_history = []
                st.session_state.pop("pdf_bytes", None)
                st.rerun()
    else:
        # Demo mode
        st.info("📂 No PDF uploaded — showing **demo mode** with sample data.", icon="ℹ️")
        if st.button("▶ Load Demo Analysis", use_container_width=True):
            run_analysis = True


# ── Run analysis ──────────────────────────────────────────────────────────────

if run_analysis:
    with st.spinner("🔬 Auditing research paper…"):
        pdf_bytes = st.session_state.get("pdf_bytes")
        if pdf_bytes:
            paper_text = extract_text_from_pdf(pdf_bytes)
            st.session_state["paper_text"] = paper_text
            if not paper_text.strip():
                st.warning("⚠️ Could not extract text from PDF (possibly scanned/image-based). Showing demo data.")
                data = DEMO_DATA
            else:
                data = analyse_pdf_locally(paper_text)
        else:
            data = DEMO_DATA

        st.session_state.paper_data = data
        st.session_state.analysis_done = True
    st.rerun()


# ── Analysis panel ────────────────────────────────────────────────────────────

with analysis_col:
    if not st.session_state.analysis_done or not st.session_state.paper_data:
        st.markdown("""
        <div style="height:400px;display:flex;align-items:center;justify-content:center;
                    flex-direction:column;gap:16px;color:var(--muted);text-align:center">
          <div style="font-size:3rem">🔬</div>
          <div style="font-family:var(--mono);font-size:0.8rem;letter-spacing:1px">
            AWAITING ANALYSIS
          </div>
          <div style="font-size:0.8rem;max-width:260px">
            Upload a PDF or load the demo to begin the audit
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        data = st.session_state.paper_data

        # Title
        st.markdown(f"""
        <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;
                    padding:16px 20px;margin-bottom:16px">
          <div style="font-family:var(--sans);font-size:1.05rem;font-weight:700;color:var(--text)">
            {data.get('title','Untitled Paper')}
          </div>
          <div style="font-size:0.8rem;color:var(--muted);margin-top:6px">
            {data.get('abstract_summary','')}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Score cards
        render_metrics(data)

        # ── Tabs ──
        tab_overview, tab_evidence, tab_viz, tab_refs, tab_audio, tab_advanced = st.tabs([
            "📊 Overview", "⚖️ Evidence", "🔄 Visuals", "📚 References", "🎧 Audio", "🧠 Deep Dive"
        ])

        with tab_overview:
            st.markdown('<div class="section-head">🧬 Research DNA Barcode</div>', unsafe_allow_html=True)
            render_barcode(data.get("sentiment_barcode", []))

            st.markdown('<div class="section-head">🗺️ Methodology Breakdown</div>', unsafe_allow_html=True)
            render_methodology_chart(data.get("methodology_breakdown", {"labels":[],"values":[]}))

            st.markdown('<div class="section-head">✨ Key Contributions</div>', unsafe_allow_html=True)
            render_contributions(data.get("key_contributions", []))

        with tab_evidence:
            st.markdown(f"""
            <div class="barcode-label" style="margin-bottom:8px">EVIDENCE RATIONALE</div>
            <div style="font-size:0.83rem;color:var(--text);margin-bottom:16px">
              {data.get('evidence_rationale','')}
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-head">🔍 Claim Verification</div>', unsafe_allow_html=True)
            render_claims(data.get("claims", []))

            st.markdown('<div class="section-head">⚠ Limitations</div>', unsafe_allow_html=True)
            render_limitations(data.get("limitations", []))

        with tab_viz:
            st.markdown('<div class="section-head">🔄 Methodology Flowchart (Mermaid)</div>', unsafe_allow_html=True)
            render_mermaid(data.get("mermaid_flowchart", "graph LR; A[Start] --> B[End]"))

            st.markdown('<div class="section-head">🕸️ Knowledge Graph</div>', unsafe_allow_html=True)
            render_knowledge_graph(
                data.get("entities", []),
                data.get("relationships", [])
            )

        with tab_refs:
            st.markdown('<div class="section-head">📚 Reference Health Check</div>', unsafe_allow_html=True)
            render_references(data.get("references", []))

        with tab_audio:
            st.markdown('<div class="section-head">🎧 Audio Abstract</div>', unsafe_allow_html=True)
            text_to_speak = data.get("abstract_summary", "No abstract available.")
            st.markdown(f'<div style="font-size:0.83rem;color:var(--muted);margin-bottom:12px">{text_to_speak}</div>',
                        unsafe_allow_html=True)
            if st.button("🔊 Generate Audio Summary", use_container_width=True):
                render_audio(text_to_speak)

            st.markdown('<div class="section-head">📋 Key Contributions Read-Aloud</div>', unsafe_allow_html=True)
            contrib_text = ". ".join(data.get("key_contributions", []))
            if st.button("🔊 Read Contributions", use_container_width=True):
                render_audio(contrib_text)

        with tab_advanced:
            st.markdown('<div class="section-head">🧠 Comparative Radar</div>', unsafe_allow_html=True)
            categories = ["Evidence", "Novelty", "Reproducibility", "Recency", "Methodology"]
            refs = data.get("references", [])
            now = datetime.now().year
            recency = int(sum(1 for r in refs if now - r["year"] <= 5) / max(len(refs),1) * 100)
            values = [
                data["evidence_strength_score"],
                data["novelty_score"],
                data["reproducibility_score"],
                recency,
                min(100, len(data.get("methodology_breakdown",{}).get("labels",[])) * 18),
            ]
            fig = go.Figure(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor="rgba(91,138,240,0.15)",
                line=dict(color="#5b8af0", width=2),
                marker=dict(color="#5b8af0"),
            ))
            fig.update_layout(
                polar=dict(
                    bgcolor="rgba(17,20,32,1)",
                    radialaxis=dict(visible=True, range=[0,100], gridcolor="#252a40",
                                   tickfont=dict(color="#64748b", size=9)),
                    angularaxis=dict(gridcolor="#252a40", tickfont=dict(color="#e2e8f0", size=10)),
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=40,r=40,t=20,b=20),
                height=300,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            st.markdown('<div class="section-head">📈 Evidence vs Novelty Scatter</div>', unsafe_allow_html=True)
            scatter_data = pd.DataFrame({
                "Claim": [c["text"][:35]+"…" for c in data.get("claims", [])],
                "Evidence": [{"Strong":90,"Moderate":55,"Weak":20}.get(c["strength"],50)
                             + random.randint(-5,5) for c in data.get("claims", [])],
                "Strength": [c["strength"] for c in data.get("claims", [])],
            })
            if not scatter_data.empty:
                fig2 = px.bar(scatter_data, x="Claim", y="Evidence",
                              color="Strength",
                              color_discrete_map={"Strong":"#34d399","Moderate":"#f59e0b","Weak":"#f87171"})
                fig2.update_layout(
                    height=220,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(17,20,32,1)",
                    font_color="#e2e8f0",
                    margin=dict(l=0,r=0,t=0,b=0),
                    xaxis=dict(gridcolor="#252a40", tickfont=dict(size=9)),
                    yaxis=dict(gridcolor="#252a40", range=[0,100]),
                    legend=dict(bgcolor="rgba(0,0,0,0)"),
                    showlegend=True,
                )
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
