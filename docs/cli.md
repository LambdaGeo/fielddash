# Command line

```text
fielddash init   [DIRECTORY] [--name NAME] [--source {epicollect,json}] [--deploy] [--force]
fielddash fields PROJECT
fielddash run    [PROJECT] [STREAMLIT OPTIONS]
```

## `fielddash init`

Creates a new project folder (default: the current directory).

| Option | Description |
|--------|-------------|
| `DIRECTORY` | Folder to create or use. |
| `--name NAME` | Project name, used for the title and the variable names (`MY_SURVEY_CLIENT_ID`). Default: the folder name. |
| `--source` | `epicollect` (default) or `json` (offline, reads `data/`). |
| `--deploy` | Also write `streamlit_app.py` and `.streamlit/secrets.toml.example`. |
| `--force` | Overwrite files that already exist. Without it they are skipped and listed. |

Always written: `project.yaml`, `requirements.txt` and `.gitignore`. For `epicollect` also `.env.example`. It ends by printing the next steps: environment, credentials, `fielddash fields`, `fielddash run`.

## `fielddash fields`

Loads the project and prints every question: the last six characters of its `ref`, alias, type, export column and question text, followed by schema warnings. Use it to decide aliases, filters and highlights.

## `fielddash run`

Starts the dashboard in Streamlit. `PROJECT` is a `.yaml` file or a folder of projects (default: the current directory); with a folder, a selector appears in the sidebar. Any other option is passed to Streamlit:

```bash
fielddash run project.yaml --server.port 8600
```
