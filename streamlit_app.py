
import os, sys
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# Ensure we can import from src/ (src layout)
REPO_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.join(REPO_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from srf_carboncapture.models.srf_net_income import srf_net_income
from srf_carboncapture.models.trees import QuercusRobur, AlnusGlutinosa, PopulusTremula, AcerPseudoplatanus

st.set_page_config(page_title="SRF Net Income Explorer", layout="wide")

st.title("Short Rotation Forestry – Net Income Explorer")
st.caption("Interactively explore net revenue over time for mixed-species woodlands and biochar processing.")

# --- Sidebar: global settings ---
with st.sidebar:
    st.header("Simulation Settings")
    years_max = st.slider("Simulation horizon (years)", min_value=10, max_value=200, value=150, step=10)
    st.markdown("---")
    st.write("**Run controls**")
    run_sim = st.button("Run simulation", type="primary")

# --- Inputs: core parameters ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("Forest & Land")
    wood_area = st.number_input("Wood area [hectares]", min_value=0.01, max_value=10_000.0, value=1.0, step=0.1)
    tree_area = st.number_input("Tree area [hectares per tree]", min_value=0.00001, max_value=0.01, value=0.000225, step=0.000005, format="%.6f")
    yearly_rotation = st.slider("Yearly rotation [years]", min_value=5, max_value=60, value=20, step=1)
    land_per_biochar_tonne = st.number_input("Land used per biochar tonne [ha/t]", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
    land_value_per_ha = st.number_input("Land value [£/ha]", min_value=0.0, max_value=100_000.0, value=0.0, step=100.0)

with col2:
    st.subheader("Economics")
    carbon_credit_per_co2_tonne = st.number_input("Carbon credit [£ per tCO₂e]", min_value=0.0, max_value=1_000.0, value=30.0, step=1.0)
    pyroloysis_processing_cost_per_biochar_tonne = st.number_input("Pyrolysis processing cost [£/t biochar]", min_value=0.0, max_value=10_000.0, value=50.0, step=10.0)
    carbon_resale_per_biochar_tonne = st.number_input("Carbon resale price [£/t biochar]", min_value=0.0, max_value=10_000.0, value=800.0, step=10.0)

st.markdown("---")

# --- Tree species selection & enforced percentages ---
st.subheader("Tree species mix (percent cover)")

# Available species (extendable)
available_species = [
    ("Quercus robur (Oak)", QuercusRobur),
    ("Acer pseudoplatanus (Sycamore)", AcerPseudoplatanus),
    ("Alnus glutinosa (Alder)", AlnusGlutinosa),
    ("Populus tremula (Aspen)", PopulusTremula),
]

# Defaults from the model
default_enabled = {
    QuercusRobur: True,
    AcerPseudoplatanus: True,
    AlnusGlutinosa: True,
    PopulusTremula: True,
}

# Select which species to include
enabled = []
cols = st.columns(len(available_species))
for i, (label, cls) in enumerate(available_species):
    with cols[i]:
        enabled_flag = st.checkbox(label, value=default_enabled.get(cls, False), key=f"enable_{cls.__name__}")
        if enabled_flag:
            enabled.append(cls)

if not enabled:
    st.warning("Select at least one species to proceed.")
    st.stop()

st.caption("Adjust percentages below. The last selected species is auto-filled to ensure the total is exactly 100%.")

# Percent sliders for all but the last species
raw_percents = {}
remaining = 100.0
for i, cls in enumerate(enabled):
    is_last = (i == len(enabled)-1)
    label = next(lbl for lbl, c in available_species if c is cls)
    if is_last:
        # auto-fill with remaining (>=0)
        pct_val = max(0.0, round(remaining, 2))
        raw_percents[cls] = pct_val
        st.write(f"**{label}**: {pct_val:.2f}% (auto-filled)")
    else:
        # slider limited by what remains to avoid going over 100
        max_here = max(0.0, remaining)
        pct_val = st.slider(f"{label} [%]", min_value=0.0, max_value=float(max(0.0, min(100.0, max_here))), value=float(min(25.0, max_here)), step=0.5, key=f"pct_{cls.__name__}")
        raw_percents[cls] = pct_val
        remaining -= pct_val

total_pct = sum(raw_percents.values())
if abs(total_pct - 100.0) > 1e-6:
    st.error(f"Percentages do not sum to 100% (current total = {total_pct:.2f}%). Please adjust.")
    st.stop()

# Convert to fractions
tree_percentages = {cls: pct/100.0 for cls, pct in raw_percents.items()}

# --- Run the simulation and plot ---
if run_sim:
    # Monkeypatch the years horizon by temporarily wrapping srf_net_income
    # We'll call srf_net_income and simply slice years to requested horizon if needed.
    costs, years = srf_net_income(
        wood_area=wood_area,
        tree_percentages=tree_percentages,
        tree_area=tree_area,
        yearly_rotation=yearly_rotation,
        carbon_credit_per_co2_tonne=carbon_credit_per_co2_tonne,
        pyroloysis_processing_cost_per_biochar_tonne=pyroloysis_processing_cost_per_biochar_tonne,
        carbon_resale_per_biochar_tonne=carbon_resale_per_biochar_tonne,
        land_per_biochar_tonne=land_per_biochar_tonne,
        land_value_per_ha=land_value_per_ha
    )
    # Ensure arrays
    years = np.asarray(years)
    costs = np.asarray(costs, dtype=float)

    # Crop to requested horizon if needed
    mask = (years >= 0) & (years <= years_max)
    years = years[mask]
    costs = costs[mask]

    # Plot with matplotlib (single plot, no style/colors set)
    fig, ax = plt.subplots()
    ax.plot(years, costs)
    ax.set_xlabel("Year")
    ax.set_ylabel("Net revenue [£/year]")
    ax.set_title("Net revenue vs year")

    st.pyplot(fig, clear_figure=True)

    # Summary stats
    st.markdown("### Summary")
    st.write(f"Total net revenue over {int(years[-1])} years: **£{float(np.trapz(costs, years)):.0f}** (area under curve)")
    st.write(f"Average annual net revenue: **£{float(costs.mean()):.2f}/year**")
else:
    st.info("Set your inputs and click **Run simulation**.")
