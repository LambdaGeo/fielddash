# Extending

fielddash has two extension points, both plain Python files listed under `extensions` in the project YAML:

```yaml
extensions: [pages, extra/my_source.py]    # files, or folders (every *.py not starting with "_")
```

!!! note
    Extensions are imported once per server process. Restart the app after editing one.

## Custom pages

A page is a function decorated with `@page`. It receives a `PageContext`.

```python
import streamlit as st

from fielddash.core.registry import page
from fielddash.ui.charts import render_field


@page("Recycling", order=40, available=lambda ctx: ctx.dataset.find("separa_reciclagem") is not None)
def render(ctx):
    ds, df = ctx.dataset, ctx.df
    answers = df[ds.field("separa_reciclagem").column].dropna()
    share = f"{(answers == 'Sim').mean():.0%}" if len(answers) else "—"
    st.metric("Separate waste for recycling", share, help=f"{len(answers)} answers")
    st.markdown("**Separation by neighborhood**")
    render_field(ds, df, ds.field("separa_reciclagem"), by=ds.field("bairro"))
```

This is `examples/waste/pages/recycling.py` from the repository.

`@page(name, order=100, available=None)`:

| Argument | Description |
|----------|-------------|
| `name` | Label in the sidebar navigation. |
| `order` | Position. Built-in pages use Overview 10, Highlights 20, Questions 30, Data 90. |
| `available` | Optional `ctx -> bool`. When it returns false the page is hidden, for example because the project has no such question. |

### `PageContext`

| Attribute | Description |
|-----------|-------------|
| `ctx.config` | The parsed project configuration. |
| `ctx.dataset` | Schema plus the complete data. |
| `ctx.df` | The data **after the visitor's sidebar filters**. Use this, not `dataset.df`, for anything shown. |
| `ctx.filters` | Labels of the active filters. |

### `Dataset`

| Member | Description |
|--------|-------------|
| `ds.field(key)` | The `Field` for an alias, ref, ref suffix, column or question text. Raises `KeyError` if missing or ambiguous. |
| `ds.find(key)` | Same, but returns `None` when missing. Use it in `available`. |
| `ds.of_kind(*kinds)` | Fields of the given kinds: `categorical`, `multi`, `numeric`, `date`, `location`, `text`, `media`, `other`. |
| `ds.fields`, `ds.df`, `ds.warnings` | All fields, the full data and the schema warnings. |

A `Field` has `ref`, `column` (the column of `df`), `label`, `type`, `kind`, `options`, `group`, `alias` and `system`. A location field also has `lat` and `lon`, the names of its two numeric columns.

### Building blocks

| Import | Use |
|--------|-----|
| `fielddash.ui.charts.render_field(ds, df, field, by=None, key="")` | The chart chosen for the question's type, optionally crossed with a categorical `by`. |
| `fielddash.ui.charts.timeline(df, field, key)` | Entries per day, week or month for a date field. |
| `fielddash.ui.maps.render_map(ds, df, config_map, key="map", height=460)` | The points/heatmap map. |

Pass a distinct `key` when you draw the same chart twice on a page.

## Custom data sources

A source returns the form schema and the responses. Subclass `DataSource`, register it with `@source`, and select it with `source.type`:

```python
# extra/my_source.py
from fielddash.core.registry import source
from fielddash.sources.base import DataSource


@source("my_system")
class MySystemSource(DataSource):
    def fetch_schema(self) -> dict:
        """Epicollect form JSON, or a project export."""
        ...

    def fetch_entries(self) -> list:
        """One dict per response, keyed by export column name."""
        ...
```

```yaml
source:
  type: my_system
  anything: you_need                # arrives in self.options
extensions: [extra/my_source.py]
```

Inside the class, `self.options` is the `source:` mapping (variables already substituted) and `self.config.resolve("relative/path")` resolves a path against the YAML's folder.

The responses must follow Epicollect's JSON export shape, because the schema parser computes the expected column of each question from it:

- keys are column names such as `4_Idade`, plus `created_at` and `created_by`;
- a location answer is a dict with `latitude` and `longitude`;
- a multiple-choice answer is a list (a comma-separated string is also accepted).

A source for another system is therefore mostly a translation step into this shape. The built-in `json` source ([`fielddash/sources/json_file.py`](https://github.com/LambdaGeo/fielddash/blob/main/fielddash/sources/json_file.py)) is the smallest complete example.
