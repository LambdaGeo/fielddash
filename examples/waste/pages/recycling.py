"""Example of a project-specific page, loaded through `extensions` in the config."""
import streamlit as st

from fielddash.core.registry import page
from fielddash.ui.charts import render_field


@page("Recycling", order=40, available=lambda ctx: ctx.dataset.find("separa_reciclagem") is not None)
def render(ctx):
    ds, df = ctx.dataset, ctx.df
    answers = df[ds.field("separa_reciclagem").column].dropna()
    share = f"{(answers == 'Sim').mean():.0%}" if len(answers) else "—"
    st.metric("Separate waste for recycling", share, help=f"{len(answers)} answers")
    st.markdown("**Separation by neighborhood**")
    render_field(ds, df, ds.field("separa_reciclagem"), by=ds.field("bairro"))
