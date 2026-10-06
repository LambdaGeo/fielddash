# Deployment

## Inside your own Streamlit script

```python
# streamlit_app.py
import fielddash

fielddash.dashboard("project.yaml")        # a project file...
fielddash.dashboard("projects/")           # ...or a folder: selector in the sidebar
```

`dashboard(target=".", *, configure_page=True)` takes a `.yaml` file or a folder. In a folder it lists `*.yaml` and `*/*.yaml`. Relative paths are looked up from the current directory and then from the script's folder. Pass `configure_page=False` if your script already called `st.set_page_config`.

## Streamlit Community Cloud

1. Create the project with the deploy files and try it locally:
   ```bash
   pip install fielddash
   fielddash init my-survey --deploy
   cd my-survey
   cp .env.example .env          # fill in, then edit project.yaml
   streamlit run streamlit_app.py
   ```
2. Push the folder to a GitHub repository. `.env` and `.streamlit/secrets.toml` are git-ignored, so credentials never reach the repository.
3. On [share.streamlit.io](https://share.streamlit.io) choose *Create app*, pick the repository and branch, and set `streamlit_app.py` as the main file.
4. Under *Advanced settings → Secrets* (later: *Settings → Secrets*) paste the content of `.streamlit/secrets.toml.example`, filled in:
   ```toml
   FIELD_ACCESS_PIN = "choose-a-code"
   PROJECT_MY_SURVEY = "project-slug"
   MY_SURVEY_CLIENT_ID = "..."
   MY_SURVEY_CLIENT_SECRET = "..."
   ```
5. Deploy, then share the app link, or `https://<your-app>.streamlit.app/?token=<code>` to skip the login screen.

fielddash reads variables from the environment (including `.env`) first and from Streamlit secrets next, so the same `project.yaml` works locally and in the cloud. The data cache is shared by all visitors.

!!! warning "Without a PIN the app is public"
    Anyone with the link sees the data, and the **Data** page lets them download all of it. Read [Privacy and data protection](privacy.md) before publishing real survey data.

## Restricting access

```python
import fielddash

fielddash.require_access()                 # before fielddash.dashboard(...)
fielddash.dashboard("project.yaml", configure_page=False)
```

`fielddash init --deploy` already generates this. When `FIELD_ACCESS_PIN` is set (environment, `.env` or Streamlit secrets; `FIELD_ACCESS_TOKEN` and `ACCESS_PIN` also work), visitors see a login screen and must enter the code, or open a link ending in `?token=<code>` (`pin` and `key` are accepted as parameter names too). The sidebar then shows an *End session* button. When the variable is not set the call does nothing.

This is a single shared code meant to keep a field dashboard away from casual visitors. It has no individual accounts and no limit on attempts, and a code in a URL can end up in browser history and server logs. For sensitive data put real authentication in front of the app (for example your institution's single sign-on on a self-hosted server).

## Self-hosted server

```bash
fielddash run projects/ --server.port 8501 --server.headless true
```

Run it as a service (for example systemd) behind a reverse proxy such as Nginx with HTTPS. Extra options after the project are passed to Streamlit.
