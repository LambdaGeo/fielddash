import shutil
from pathlib import Path

import pytest
import streamlit
from streamlit.testing.v1 import AppTest

from conftest import EXAMPLE
from fielddash.cli import main
from fielddash.core.config import load_config
from fielddash.core.loader import bootstrap, load_dataset


def _plotly_stub(fig, *args, **kwargs):
    fig.to_json()


def test_init_epicollect_creates_files_and_valid_config(tmp_path, monkeypatch):
    target = tmp_path / "my-survey"
    assert main(["init", str(target)]) == 0
    assert {p.name for p in target.iterdir()} == {"project.yaml", ".gitignore", ".env.example"}
    assert "MY_SURVEY_CLIENT_ID" in (target / ".env.example").read_text()

    monkeypatch.setenv("PROJECT_MY_SURVEY", "some-slug")
    config = load_config(target / "project.yaml")
    assert config.title == "My Survey"
    assert config.source["type"] == "epicollect"
    assert config.source["project"] == "some-slug"
    assert config.source["credentials"] == "MY_SURVEY"


def test_init_json_ignores_data_folder(tmp_path):
    main(["init", str(tmp_path), "--source", "json"])
    assert (tmp_path / "data").is_dir()
    assert "data/" in (tmp_path / ".gitignore").read_text().splitlines()
    assert not (tmp_path / ".env.example").exists()


def test_init_does_not_overwrite_without_force(tmp_path):
    (tmp_path / "project.yaml").write_text("mine")
    main(["init", str(tmp_path)])
    assert (tmp_path / "project.yaml").read_text() == "mine"
    main(["init", str(tmp_path), "--force"])
    assert (tmp_path / "project.yaml").read_text() != "mine"


def test_init_title_with_quotes_stays_valid_yaml(tmp_path, monkeypatch):
    main(["init", str(tmp_path), "--name", 'Pesquisa "A" 2024'])
    monkeypatch.setenv("PROJECT_PESQUISA_A_2024", "x")
    assert load_config(tmp_path / "project.yaml").title == 'Pesquisa "A" 2024'


def test_generated_json_project_loads_example_data(tmp_path):
    main(["init", str(tmp_path), "--source", "json"])
    shutil.copy(EXAMPLE / "form.json", tmp_path / "data" / "form.json")
    shutil.copy(EXAMPLE / "responses.json", tmp_path / "data" / "entries.json")
    config = load_config(tmp_path / "project.yaml")
    bootstrap(config)
    assert len(load_dataset(config).df) == 18


@pytest.mark.parametrize("pin", [None, "secret123"])
def test_generated_deploy_app_runs(tmp_path, monkeypatch, pin):
    main(["init", str(tmp_path), "--source", "json", "--deploy", "--name", "field-test"])
    shutil.copy(EXAMPLE / "form.json", tmp_path / "data" / "form.json")
    shutil.copy(EXAMPLE / "responses.json", tmp_path / "data" / "entries.json")
    monkeypatch.setattr(streamlit, "plotly_chart", _plotly_stub)
    if pin:
        monkeypatch.setenv("FIELD_ACCESS_PIN", pin)
    assert (tmp_path / "requirements.txt").read_text().split() == ["fielddash"]
    script = tmp_path / "streamlit_app.py"
    monkeypatch.setattr("sys.argv", [str(script)])
    at = AppTest.from_file(str(script), default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    if pin:
        assert len(at.title) == 0
        at.text_input[0].input(pin)
        at.button[0].click().run()
        assert not at.exception, at.exception
    assert at.title[0].value == "Field Test"
