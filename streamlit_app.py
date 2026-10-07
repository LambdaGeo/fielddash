"""Entry point for publishing the example on Streamlit Community Cloud.

- Access restricted to the field team via PIN/token (`FIELD_ACCESS_PIN` in Streamlit Secrets).
- Project chosen by `FIELDDASH_CONFIG` (secret or env var), a local `projects/` folder,
  or the bundled example with anonymized data.
"""
from pathlib import Path

import streamlit as st

import fielddash
from fielddash.core.env import getenv

st.set_page_config(page_title="fielddash", page_icon="📊", layout="wide")


def _resolve_target() -> str:
    target = getenv("FIELDDASH_CONFIG")
    if target and Path(target).exists():
        return target

    projects = Path("projects")
    if projects.is_dir() and (list(projects.glob("*.yaml")) or list(projects.glob("*/*.yaml"))):
        return "projects"

    example = Path("examples/waste/project.yaml")  # safe fallback: anonymized data
    return str(example) if example.exists() else "."


fielddash.require_access()
fielddash.dashboard(_resolve_target(), configure_page=False)
