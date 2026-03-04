import json
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------
# Configurazione Streamlit
# ---------------------------------
st.set_page_config(
    page_title="ENAV · Organici CTA",
    page_icon="✈",
    layout="wide"
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


# ---------------------------------
# Helper per caricare i JSON
# ---------------------------------
def load_json(path: Path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


# ---------------------------------
# Caricamento dati
# ---------------------------------
FTE = load_json(DATA_DIR / "fte.json", {})
AGG = load_json(DATA_DIR / "agg.json", {})
PER = load_json(DATA_DIR / "per.json", [])

YRS = [2026, 2027, 2028, 2029]

CAT = {
    "ACC ROMA": "A", "ACC MILANO": "A", "ACC PADOVA": "A", "ACC BRINDISI": "A",
    "FIUMICINO": "P", "CIAMPINO": "P", "LINATE": "P", "MALPENSA": "P",
