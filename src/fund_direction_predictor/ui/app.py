from typing import cast

import streamlit as st

from fund_direction_predictor.settings import load_config


config = load_config()
project = cast(dict[str, object], config["project"])
scope = cast(dict[str, object], config["v1_scope"])
fund_universe = cast(dict[str, object], config["fund_universe"])

st.set_page_config(page_title="Fund Direction Predictor", layout="wide")

st.title(str(project["display_name"]))
st.caption("Stage-one bootstrap dashboard placeholder")

col1, col2, col3 = st.columns(3)
col1.metric("Stage", str(project["stage"]))
col2.metric("Horizons", ", ".join(str(item) for item in cast(list[object], project["prediction_horizons"])))
col3.metric("Universe Target", str(fund_universe["pool_size_target"]))

st.subheader("Current V1 Scope")
st.write(f"Target universe: {scope['target_universe']}")
st.write(f"Primary target type: {scope['primary_target_type']}")

st.subheader("Core Benchmarks")
st.write(", ".join(str(item) for item in cast(list[object], fund_universe["core_benchmarks"])))

st.subheader("Configuration Snapshot")
st.json(config)
