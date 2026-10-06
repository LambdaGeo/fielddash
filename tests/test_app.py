from pathlib import Path

import pytest
import streamlit
from streamlit.testing.v1 import AppTest

import fielddash
from conftest import EXAMPLE

APP = str(Path(fielddash.__file__).resolve().parent / "app.py")
CONFIG = str(EXAMPLE / "project.yaml")


def _plotly_stub(fig, *args, **kwargs):
    # AppTest (Streamlit 1.39) does not serialize plotly widgets natively;
    # serializing the figure still verifies that the chart was created without error.
    fig.to_json()


def run(monkeypatch, page=None):
    monkeypatch.setenv("FIELDDASH_CONFIG", CONFIG)
    monkeypatch.setattr(streamlit, "plotly_chart", _plotly_stub)
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    if page:
        at.sidebar.radio(key="page").set_value(page).run()
    assert not at.exception, at.exception
    return at


@pytest.mark.parametrize("page", ["Overview", "Highlights", "Questions", "Recycling", "Data"])
def test_pages_render(monkeypatch, page):
    run(monkeypatch, page)


def test_cross_and_filter(monkeypatch):
    at = run(monkeypatch, "Questions")
    at.selectbox(key="cross_by").select_index(3).run()      # cross with a question
    assert not at.exception, at.exception
    bairro = next(m for m in at.sidebar.multiselect if m.label == "Bairro")
    bairro.select(bairro.options[0]).run()
    assert not at.exception, at.exception
    assert "Filters: Bairro" in at.caption[0].value


def test_dashboard_function_in_user_script(monkeypatch):
    monkeypatch.setattr(streamlit, "plotly_chart", _plotly_stub)
    script = Path(__file__).parent / "fixtures" / "streamlit_app.py"
    monkeypatch.setattr("sys.argv", [str(script)])
    at = AppTest.from_file(str(script), default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    assert at.title[0].value == "Diagnóstico de Resíduos – Itaqui-Bacanga"


def test_root_streamlit_app_public(monkeypatch):
    monkeypatch.setattr(streamlit, "plotly_chart", _plotly_stub)
    monkeypatch.setenv("FIELDDASH_CONFIG", CONFIG)
    root_script = Path(__file__).parent.parent / "streamlit_app.py"
    monkeypatch.setattr("sys.argv", [str(root_script)])
    at = AppTest.from_file(str(root_script), default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    assert at.title[0].value == "Diagnóstico de Resíduos – Itaqui-Bacanga"


def test_root_streamlit_app_with_pin_protection(monkeypatch):
    monkeypatch.setattr(streamlit, "plotly_chart", _plotly_stub)
    monkeypatch.setenv("FIELDDASH_CONFIG", CONFIG)
    monkeypatch.setenv("FIELD_ACCESS_PIN", "secret123")
    root_script = Path(__file__).parent.parent / "streamlit_app.py"
    monkeypatch.setattr("sys.argv", [str(root_script)])

    # 1. Unauthenticated run stops at login prompt
    at = AppTest.from_file(str(root_script), default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    assert len(at.title) == 0  # didn't load dashboard title

    # 2. Enter correct PIN and submit
    at.text_input[0].input("secret123")
    at.button[0].click().run()
    assert not at.exception, at.exception
    assert at.title[0].value == "Diagnóstico de Resíduos – Itaqui-Bacanga"


