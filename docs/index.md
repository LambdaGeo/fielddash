# fielddash

Schema-driven dashboards for **field data collection**. Point it at an [Epicollect5](https://five.epicollect.net) project, write a short YAML file, and get filters, charts, a map and a data table generated from the form itself.

## Why it exists

Epicollect exports name each column after the question's position and text (for example `12_Neighborhood`). Add, remove or reorder a question and the numbers shift, so a dashboard built on column names breaks in the middle of fieldwork.

fielddash identifies every question by its stable Epicollect `ref` and resolves the column at runtime. Editing the form does not break the dashboard, and starting a new survey takes one YAML file. [How it works →](how-it-works.md)

## What you get

| Page | Content |
|------|---------|
| **Overview** | Summary indicators, map of survey locations, submissions over time, responses per collector. |
| **Highlights** | The charts you curate in the YAML (`highlights`). Hidden when none are configured. |
| **Questions** | Every question grouped by section, with search, a free-text toggle and cross-tabulation by any categorical question. |
| **Data** | Searchable table with CSV and Excel download. |

The input type of each question (`radio`, `checkbox`, `integer`, `location`, ...) decides its filter, chart and map representation automatically.

## Quick start

```bash
mkdir my-survey && cd my-survey
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install fielddash
fielddash init .
cp .env.example .env              # project slug and Epicollect credentials
fielddash fields project.yaml     # list the form's questions
fielddash run project.yaml
```

## Where next

- [Getting started](getting-started.md): the full first-run walkthrough.
- [Configuration](configuration.md): every key of the project YAML.
- [Deployment](deployment.md): Streamlit Community Cloud, your own server, access control.
- [Privacy and data protection](privacy.md): read before publishing a dashboard with real survey data.
- [Extending](extending.md): project-specific pages and new data sources.
