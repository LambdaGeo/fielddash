"""Optional PIN gate for dashboards shared with a field team (Streamlit).

    import fielddash
    fielddash.require_access()      # no-op unless FIELD_ACCESS_PIN is set (env, .env or Streamlit secrets)
    fielddash.dashboard("project.yaml", configure_page=False)

Team members enter the code on a login screen or open a link ending in `?token=<code>`.
"""
import hmac

import streamlit as st

from fielddash.core.env import getenv

PIN_VARS = ("FIELD_ACCESS_PIN", "FIELD_ACCESS_TOKEN", "ACCESS_PIN")
URL_PARAMS = ("token", "pin", "key")


def required_pin():
    """The configured access code, or None when the dashboard is open to everyone."""
    for name in PIN_VARS:
        value = getenv(name)
        if value:
            return str(value).strip()
    return None


def _matches(given, expected) -> bool:
    return hmac.compare_digest(str(given).strip().encode(), str(expected).encode())


def _url_token():
    for name in URL_PARAMS:
        value = st.query_params.get(name)
        if value:
            return value
    return None


def _sidebar_logout():
    st.sidebar.caption("🟢 Access granted (field team)")
    if st.sidebar.button("End session", key="logout_btn"):
        st.session_state["authenticated"] = False
        for name in URL_PARAMS:  # otherwise the link would log the user straight back in
            if name in st.query_params:
                del st.query_params[name]
        st.rerun()


def require_access() -> None:
    """Stops the script on a login screen unless the visitor has the access code."""
    pin = required_pin()
    if not pin:
        return

    token = _url_token()
    if st.session_state.get("authenticated") or (token and _matches(token, pin)):
        st.session_state["authenticated"] = True
        _sidebar_logout()
        return

    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown("## 🔐 Restricted area — field team")
        st.info("This dashboard contains field-work data. Enter the access code provided by the research coordination.")
        with st.form("login_form"):
            entered = st.text_input("Access code / PIN:", type="password")
            if st.form_submit_button("Enter dashboard"):
                if entered and _matches(entered, pin):
                    st.session_state["authenticated"] = True
                    st.rerun()
                st.error("Wrong access code. Check with the responsible team.")
    st.stop()
