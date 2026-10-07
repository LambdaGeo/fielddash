import re
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

from fielddash.core.env import getenv

_ENV = re.compile(r"\$\{([A-Za-z0-9_]+)\}")


def _expand(value):
    if isinstance(value, str):
        def replace(match):
            name = match.group(1)
            value = getenv(name)
            if value is None:
                raise KeyError(f"Variable not defined in .env or Streamlit secrets: {name}")
            return value
        return _ENV.sub(replace, value)
    if isinstance(value, list):
        return [_expand(v) for v in value]
    if isinstance(value, dict):
        return {k: _expand(v) for k, v in value.items()}
    return value


# Portuguese keys from earlier versions: still accepted (with a FutureWarning), use English keys.
LEGACY_KEYS = {
    "titulo": "title",
    "subtitulo": "subtitle",
    "fonte": "source",
    "campos": "fields",
    "ignorar": "ignore",
    "tipos": "types",
    "filtros": "filters",
    "destaques": "highlights",
    "secoes": "sections",
    "mapa": "map",
    "extensoes": "extensions",
    "fuso": "timezone",
    "cache_minutos": "cache_minutes",
}

LEGACY_SOURCE_KEYS = {
    "tipo": "type",
    "projeto": "project",
    "credenciais": "credentials",
    "dados": "data",
}


@dataclass
class Config:
    path: Path
    title: str
    source: dict
    subtitle: str = ""
    fields: dict = field(default_factory=dict)       # alias -> ref / column / question
    ignore: list = field(default_factory=list)
    types: dict = field(default_factory=dict)        # field -> forced type (e.g. neighborhood: category)
    filters: list = field(default_factory=list)
    highlights: list = field(default_factory=list)
    sections: list = field(default_factory=list)
    map: dict = field(default_factory=dict)
    extensions: list = field(default_factory=list)   # .py files or directories with project pages/sources
    timezone: str = "America/Fortaleza"
    cache_minutes: int = 5

    @property
    def base_dir(self) -> Path:
        return self.path.parent

    def resolve(self, relative: str) -> Path:
        return (self.base_dir / relative).resolve()


def load_config(path) -> Config:
    path = Path(path).resolve()
    # .env in current directory and in project directory
    load_dotenv(Path.cwd() / ".env")
    load_dotenv(path.parent / ".env")
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    normalized, legacy = {}, []
    for key, value in raw.items():
        canonical = LEGACY_KEYS.get(key, key)
        if canonical != key:
            legacy.append(f"{key} -> {canonical}")
        normalized[canonical] = value

    source = {}
    for key, value in _expand(normalized.get("source") or {}).items():
        canonical = LEGACY_SOURCE_KEYS.get(key, key)
        if canonical != key:
            legacy.append(f"source.{key} -> source.{canonical}")
        source[canonical] = value
    normalized["source"] = source

    if legacy:
        warnings.warn(f"{path.name}: Portuguese config keys are deprecated, rename: {', '.join(legacy)}", FutureWarning, stacklevel=2)

    if "type" not in source:
        raise ValueError(f"{path.name}: 'source.type' is required")

    known = Config.__dataclass_fields__.keys() - {"path"}
    unknown = set(normalized) - known
    if unknown:
        raise ValueError(f"{path.name}: unknown keys: {', '.join(sorted(unknown))}")

    normalized.setdefault("title", path.stem)
    return Config(path=path, **{k: v for k, v in normalized.items() if v is not None})
