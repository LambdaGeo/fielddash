"""fielddash: schema-driven dashboards for field data collection (Epicollect5)."""

__version__ = "0.1.1"


def dashboard(target=".", *, configure_page: bool = True):
    """Renders the dashboard for a project (.yaml) or directory of projects in a Streamlit script."""
    from fielddash.web import dashboard as _dashboard  # imports streamlit only when called

    return _dashboard(target, configure_page=configure_page)


def require_access():
    """Optional PIN gate: stops the Streamlit script on a login screen unless FIELD_ACCESS_PIN matches."""
    from fielddash.access import require_access as _require_access  # imports streamlit only when called

    return _require_access()
