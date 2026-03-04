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
    "ORIO AL SERIO": "P", "BOLOGNA": "P", "VENEZIA TESSERA": "P",
    "TORINO CASELLE": "P", "GENOVA": "P", "CATANIA": "P", "PALERMO": "P",
    "BARI": "P", "NAPOLI": "P", "LAMEZIA TERME": "P", "FIRENZE": "P",
    "VERONA VILLAFRANCA": "P", "TREVISO": "P", "RIMINI": "P",
    "RONCHI DEI LEGIONARI": "P", "ALGHERO": "P", "CAGLIARI": "P",
    "OLBIA": "P", "PESCARA": "P", "PERUGIA": "P", "ANCONA FALCONARA": "P",
    "COMISO": "P", "LAMPEDUSA": "P", "PANTELLERIA": "P",
    "REGGIO CALABRIA": "P", "GROTTAGLIE": "P", "BRESCIA MONTICHIARI": "P",
    "PARMA": "P", "CUNEO": "P", "FORLI": "P", "BRINDISI": "P",
    "ROMA URBE": "P", "SALERNO": "P",
    "RTCC BRINDISI": "S", "HEADQUARTERS": "S", "ACADEMY": "S"
}
