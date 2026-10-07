# Data sources

A source provides two things: the form schema and the list of responses. Everything else (parsing, reconciliation, normalization, pages) is shared. Choose one with `source.type`.

## `epicollect`

Reads straight from the Epicollect5 API every time the cache expires, so schema changes are picked up without redeploying.

```yaml
source:
  type: epicollect
  project: ${PROJECT_MY_SURVEY}     # project slug
  credentials: MY_SURVEY            # MY_SURVEY_CLIENT_ID / MY_SURVEY_CLIENT_SECRET
  form_ref: ${FORM_MY_SURVEY_REF}   # optional: default is the first form
  schema: form.json                 # optional: local fallback if the project API fails
```

| Key | Description |
|-----|-------------|
| `project` | Project slug (required). |
| `credentials` | Prefix of the variables holding the OAuth client id and secret. Omit it for a **public** project. |
| `form_ref` | Which form to use in projects with several forms. |
| `schema` | Path to a saved form JSON, used only if fetching the schema from Epicollect fails. |

Credentials are created in the project's administration area on Epicollect5 (*Apps*) and read from `<PREFIX>_CLIENT_ID` and `<PREFIX>_CLIENT_SECRET` in the environment, `.env` or Streamlit secrets.

### Requests and rate limits

Responses are fetched 1000 per page. Epicollect limits token requests per IP, so fielddash is careful:

- Tokens last about two hours. They are kept in memory and in `~/.cache/fielddash/tokens.json` (or under `$XDG_CACHE_HOME`), created readable only by you, so restarting the app does not request a new one.
- If Epicollect answers 429 to a token request, fielddash records the block and makes no further attempt until it expires (15 minutes when no `Retry-After` is given), to avoid extending it. The app shows the time when retrying is allowed.
- Data requests that get a 429 are retried up to twice when the wait is 60 seconds or less.

## `json`

Reads the schema and responses from files. Useful offline, in tests, for archived surveys, or to inspect a form.

```yaml
source:
  type: json
  schema: data/form.json
  data: data/entries.json           # optional: without it the dataset is empty
```

- `schema` is either the form JSON or the full project export.
- `data` is a list of responses in the Epicollect JSON export format. A file shaped like an API response (`{"data": {"entries": [...]}}`) works as well.
- Paths are relative to the YAML file.

!!! warning "Not for the cloud"
    `fielddash init --source json` puts `data/` in `.gitignore` on purpose, because responses may hold personal data. A deployment from Git therefore will not contain it. Use `epicollect` for apps on Streamlit Community Cloud.

## Other sources

KoboToolbox, CSV or any system you can map to Epicollect's response format can be added without changing fielddash: see [Extending](extending.md#custom-data-sources).
