# Getting started

## Install

```bash
pip install fielddash
```

Python 3.10 or newer. For development, clone the repository and run `pip install -e ".[dev]"`.

## Try the bundled example

The repository ships an example with anonymized household survey data (solid waste, Itaqui-Bacanga, São Luís, MA) that works offline:

```bash
git clone https://github.com/LambdaGeo/fielddash && cd fielddash
fielddash run examples/waste/project.yaml
```

It also shows a project-specific page (`Recycling`); see [Extending](extending.md).

## Start your own project

```bash
fielddash init my-survey
cd my-survey
```

This creates:

| File | Purpose |
|------|---------|
| `project.yaml` | The dashboard configuration, with every option documented in comments. |
| `.env.example` | Names of the variables you need (project slug, client id and secret). |
| `.gitignore` | Keeps `.env`, `token.json` and `.streamlit/secrets.toml` out of Git. |

Useful variants:

```bash
fielddash init my-survey --deploy         # + streamlit_app.py, requirements.txt, secrets example
fielddash init my-survey --source json    # offline project reading data/ (git-ignored)
```

Existing files are never overwritten unless you pass `--force`.

## Connect to Epicollect5

Copy `.env.example` to `.env` and fill it in. The client id and secret are generated under *Apps* in your project's administration area on Epicollect5:

```bash
PROJECT_MY_SURVEY=project-slug
MY_SURVEY_CLIENT_ID=...
MY_SURVEY_CLIENT_SECRET=...
```

For a **public** project no credentials are needed: remove the `credentials` line from `project.yaml`. Details in [Data sources](sources.md).

## Find your questions

```bash
fielddash fields project.yaml
```

prints every question of the form with the keys you can use in the YAML. Example, from the bundled project:

```text
ref (suffix)  alias        type      column                question
created_at                 datetime  created_at            Collection date
created_by                 category  created_by            Collector
f27864        localizacao  location  3_Localizao_do_ponto  Localização do ponto da entrevista
83aec3        idade        radio     4_Idade               Idade
5401ce        bairro       category  11_Bairro             Bairro
```

The first column shows the last six characters of the question's `ref`. Any unique ref suffix of at least six characters identifies the question, and so do its alias, full ref, column name or question text. See [how fields are resolved](how-it-works.md#how-a-field-key-is-resolved).

Warnings about the form (a column in the data without a question, a question without data) are listed below the table with a ⚠.

## Configure and run

Give questions short aliases, choose filters and highlights in `project.yaml`:

```yaml
fields:
  neighborhood: "5401ce"
  waste_dest: "48c35e"
filters: [created_at, neighborhood]
highlights:
  - {field: waste_dest, by: neighborhood}
```

then:

```bash
fielddash run project.yaml
```

`fielddash run folder/` finds every `.yaml` in the folder and adds a project selector to the sidebar. Extra options go straight to Streamlit, for example `--server.port 8600`.

Every key is described in [Configuration](configuration.md). To put the dashboard online, continue with [Deployment](deployment.md).
