"""Project scaffolding for `fielddash init`."""
import json
import re
from pathlib import Path

PROJECT_EPICOLLECT = """\
# fielddash project. Run `fielddash fields project.yaml` to list the form fields,
# then fill in `fields`, `filters` and `highlights`. Only `source` is required.

title: @@TITLE@@
subtitle: ""

source:
  type: epicollect
  project: ${PROJECT_@@PREFIX@@}        # project slug (from the Epicollect5 project URL)
  credentials: @@PREFIX@@               # @@PREFIX@@_CLIENT_ID / @@PREFIX@@_CLIENT_SECRET; remove for public projects
  # form_ref: ${FORM_@@PREFIX@@_REF}    # optional (default: first form)

@@BODY@@"""

PROJECT_JSON = """\
# fielddash project reading files saved on disk (offline use, testing, schema inspection).
# Put the Epicollect5 form schema and the entries in data/ (git-ignored: they may hold personal data).

title: @@TITLE@@
subtitle: ""

source:
  type: json
  schema: data/form.json
  data: data/entries.json               # optional: omit for an empty dataset

@@BODY@@"""

BODY = """\
# Aliases: short name -> ref suffix, column or question text (see `fielddash fields`)
fields: {}
#  neighborhood: "5401ce"

# types:                                # force a type, e.g. treat free text as category
#   neighborhood: category

# ignore: [created_by]                  # hide fields (collector e-mail, personal data, ...)

filters: [created_at]

# highlights:
#   - {field: neighborhood}

# map: {field: location}

# extensions: [pages]                   # .py files or folders with custom pages

timezone: UTC                           # e.g. America/Fortaleza
cache_minutes: 5
"""

ENV_EXAMPLE = """\
# Copy to `.env` and fill in (never commit it). Credentials: Epicollect5 project > Apps.
PROJECT_@@PREFIX@@=
@@PREFIX@@_CLIENT_ID=
@@PREFIX@@_CLIENT_SECRET=
"""

GITIGNORE = """\
.env
token.json
.streamlit/secrets.toml
__pycache__/
.venv/
"""

STREAMLIT_APP = """\
\"\"\"Streamlit entry point (e.g. Streamlit Community Cloud).\"\"\"
import streamlit as st

import fielddash

st.set_page_config(page_title=@@TITLE@@, page_icon="📊", layout="wide")
fielddash.require_access()  # optional PIN: set FIELD_ACCESS_PIN in Streamlit secrets
fielddash.dashboard("project.yaml", configure_page=False)
"""

REQUIREMENTS = """\
fielddash
"""

SECRETS_EXAMPLE = """\
# Streamlit Community Cloud: paste into Settings > Secrets.
# Locally: copy to .streamlit/secrets.toml (git-ignored).

# Restrict the app to the field team. Without it the dashboard is open to anyone with the link.
FIELD_ACCESS_PIN = "choose-a-code"
@@CREDENTIALS@@"""

SECRETS_CREDENTIALS = """
# Epicollect5
PROJECT_@@PREFIX@@ = ""
@@PREFIX@@_CLIENT_ID = ""
@@PREFIX@@_CLIENT_SECRET = ""
"""


def env_prefix(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper() or "PROJECT"


def display_title(name: str) -> str:
    return re.sub(r"[-_\s]+", " ", name).strip().title() or "Field survey"


def render(template: str, **values) -> str:
    for key, value in values.items():
        template = template.replace(f"@@{key}@@", value)
    return template


def files(name: str, source: str = "epicollect", deploy: bool = False) -> dict:
    """Relative path -> content for a new project."""
    prefix, title = env_prefix(name), json.dumps(display_title(name), ensure_ascii=False)
    epicollect = source == "epicollect"
    project = PROJECT_EPICOLLECT if epicollect else PROJECT_JSON
    out = {"project.yaml": render(project, TITLE=title, PREFIX=prefix, BODY=BODY)}
    out[".gitignore"] = GITIGNORE if epicollect else GITIGNORE + "data/\n"
    if epicollect:
        out[".env.example"] = render(ENV_EXAMPLE, PREFIX=prefix)
    if deploy:
        out["streamlit_app.py"] = render(STREAMLIT_APP, TITLE=title)
        out["requirements.txt"] = REQUIREMENTS
        credentials = render(SECRETS_CREDENTIALS, PREFIX=prefix) if epicollect else ""
        out[".streamlit/secrets.toml.example"] = render(SECRETS_EXAMPLE, CREDENTIALS=credentials)
    return out


def init_project(directory, name=None, source="epicollect", deploy=False, force=False):
    """Writes the project files into `directory`. Returns (created, skipped) relative paths."""
    root = Path(directory).resolve()
    created, skipped = [], []
    for relative, content in files(name or root.name, source, deploy).items():
        target = root / relative
        if target.exists() and not force:
            skipped.append(relative)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        created.append(relative)
    if source == "json":
        (root / "data").mkdir(exist_ok=True)
    return created, skipped
