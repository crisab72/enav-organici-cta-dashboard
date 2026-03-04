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

CATL = {"A": "ACC", "P": "Aeroporto", "S": "Speciale"}


# ---------------------------------
# Funzioni dati
# ---------------------------------
@st.cache_data(show_spinner=False)
def gA(imp: str, year: int):
    d = AGG.get(imp, {}).get(str(year), {})
    return {
        "hc": int(d.get("hc", 0) or 0),
        "ent": int(d.get("ent", 0) or 0),
        "usc": int(d.get("usc", 0) or 0),
        "ces": int(d.get("ces", 0) or 0),
    }


def gF(imp: str, year: int):
    return int(FTE.get(imp, {}).get(str(year), 0) or 0)


# ---------------------------------
# Sidebar
# ---------------------------------
with st.sidebar:
    st.title("✈ ENAV — Organici CTA")

    view = st.segmented_control(
        "Vista",
        ["Overview", "Persone", "Flussi", "Confronto", "Simulatore"],
        default="Overview"
    )

    year = st.select_slider("Anno", options=YRS, value=YRS[0])

    cat = st.radio(
        "Categoria",
        ["Tutti", "ACC", "Aeroporto", "Speciale"],
        horizontal=True
    )


# ---------------------------------
# Filtraggio impianti
# ---------------------------------
all_imps = sorted(set(CAT) | set(FTE.keys()) | set(AGG.keys()))

if cat != "Tutti":
    inv = {v: k for k, v in CATL.items()}
    ccode = inv.get(cat)
    imps = [i for i in all_imps if CAT.get(i) == ccode]
else:
    imps = all_imps


# ---------------------------------
# KPI
# ---------------------------------
hc_tot = sum(gA(i, year)["hc"] for i in imps)
fte_tot = sum(gF(i, year) for i in imps)
cv = round(hc_tot / fte_tot * 100) if fte_tot else None
crit = sum(
    1 for i in imps
    if gF(i, year) > 0 and (gA(i, year)["hc"] - gF(i, year)) < -5
)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Impianti", len(imps))
k2.metric(f"HC Organico {year}", hc_tot)
k3.metric(f"FTE Fabbisogno {year}", fte_tot)
k4.metric("Delta HC-FTE", hc_tot - fte_tot if fte_tot else None)
k5.metric("Copertura %", f"{cv}%" if cv is not None else "n/d")
k6.metric("Carenza critica", crit)


# ---------------------------------
# Vista: Overview
# ---------------------------------
if view == "Overview":
    rows = []

    for imp in imps:
        a = gA(imp, year)
        f = gF(imp, year)

        rows.append({
            "Impianto": imp,
            "Cat.": CATL.get(CAT.get(imp, ""), ""),
            "HC": a["hc"],
            "FTE": f if f else np.nan,
            "Delta HC-FTE": (a["hc"] - f) if f else np.nan,
            "Copertura %": round(a["hc"] / f * 100) if f else np.nan,
            "+Entrate": a["ent"],
            "-Uscite": a["usc"],
            "-Cessaz.": a["ces"],
        })

    df = pd.DataFrame(rows).sort_values("Delta HC-FTE")
    st.dataframe(df, use_container_width=True)


# ---------------------------------
# Vista: Persone
# ---------------------------------
elif view == "Persone":
    if not PER:
        st.info("Aggiungi data/per.json per abilitare la vista Persone.")
    else:
        df = pd.DataFrame(PER)
        st.dataframe(
            df[["mat", "cog", "nom", "qua", "ora", "sa", "d60", "abi"]].head(400),
            use_container_width=True
        )


# ---------------------------------
# Vista: Flussi
# ---------------------------------
elif view == "Flussi":
    rows = []

    for imp in imps:
        a = gA(imp, year)
        f = gF(imp, year)

        mn = a["ent"] - a["usc"]
        bl = mn - a["ces"]

        rows.append({
            "Impianto": imp,
            "HC": a["hc"],
            "FTE": f,
            "Delta": a["hc"] - f,
            "Entrate": a["ent"],
            "Uscite": a["usc"],
            "Cessazioni": a["ces"],
            "Mob.netta": mn,
            "Bilancio netto": bl,
        })

    st.dataframe(
        pd.DataFrame(rows).sort_values("Cessazioni", ascending=False),
        use_container_width=True
    )


# ---------------------------------
# Vista: Confronto
# ---------------------------------
elif view == "Confronto":
    sel = st.multiselect("Impianti (max 5)", imps, max_selections=5)

    if len(sel) < 2:
        st.info("Seleziona almeno 2 impianti")
    else:
        r = []

        for imp in sel:
            for y in YRS:
                a = gA(imp, y)
                f = gF(imp, y)
                r.append({
                    "Impianto": imp,
                    "Anno": y,
                    "HC": a["hc"],
                    "FTE": f,
                    "Delta": a["hc"] - f,
                })

        cdf = pd.DataFrame(r)

        col1, col2 = st.columns(2)

        col1.plotly_chart(
            px.line(cdf, x="Anno", y="Delta", color="Impianto", markers=True),
            use_container_width=True
        )

        melted = cdf.melt(id_vars=["Impianto", "Anno"], value_vars=["HC", "FTE"])

        col2.plotly_chart(
            px.line(
                melted, x="Anno", y="value",
                color="Impianto", line_dash="variable"
            ),
            use_container_width=True
        )

        st.dataframe(
            cdf.pivot(index="Anno", columns="Impianto", values="Delta"),
            use_container_width=True
        )


# ---------------------------------
# Vista: Simulatore
# ---------------------------------
elif view == "Simulatore":
    imp = st.selectbox("Impianto", imps)

    cols = st.columns(4)
    inputs = {}

    for i, y in enumerate(YRS):
        with cols[i]:
            ass = st.slider(f"{y} · Ass.", 0, 50, 0)
            mob = st.slider(f"{y} · Mob.", -20, 20, 0)
            pid = st.slider(f"{y} · Perd.", 0, 15, 0)
            inputs[y] = {"ass": ass, "mob": mob, "pid": pid}

    hc_base = [gA(imp, y)["hc"] for y in YRS]
    fte = [gF(imp, y) for y in YRS]

    cum = 0
    hc_sim = []

    for y in YRS:
        x = inputs[y]
        cum += x["ass"] + x["mob"] - x["pid"]
        hc_sim.append(gA(imp, y)["hc"] + cum)

    sdf = pd.DataFrame({
        "Anno": YRS,
        "FTE": fte,
        "HC base": hc_base,
        "HC simulato": hc_sim,
    })

    st.plotly_chart(
        px.line(
            sdf.melt(id_vars="Anno", value_vars=["FTE", "HC base", "HC simulato"]),
            x="Anno", y="value", color="variable", markers=True
        ),
        use_container_width=True
    )

    sdf["Delta HC-FTE"] = sdf["HC simulato"] - sdf["FTE"]

    st.dataframe(sdf, use_container_width=True)
