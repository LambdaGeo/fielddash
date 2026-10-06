# Configuration

A project is a single YAML file. Only `source` is required; everything else has a default. `fielddash init` writes a commented starting point.

```yaml
title: "My Field Survey"
subtitle: "Research team, institution..."

source:
  type: epicollect
  project: ${PROJECT_MY_SURVEY}
  credentials: MY_SURVEY

fields:                       # alias -> question
  neighborhood: "5401ce"
  waste_dest: "48c35e"
types:
  neighborhood: category
ignore: [created_by, "3401cb"]
filters: [created_at, neighborhood]
highlights:
  - {field: waste_dest, by: neighborhood, title: "Waste destination by neighborhood"}
sections:
  - {title: "Profile", fields: [age, gender]}
map: {field: location, popup: [neighborhood]}
extensions: [pages]
timezone: America/Fortaleza
cache_minutes: 5
```

## Keys

| Key | Default | Description |
|-----|---------|-------------|
| `title` | file name | Page title. |
| `subtitle` | empty | Line shown under the title. |
| `source` | required | Where schema and responses come from. See [Data sources](sources.md). |
| `fields` | none | Aliases: short name → question. |
| `types` | none | Force the type of a question. |
| `ignore` | none | Hide questions from the dashboard and the data export. |
| `filters` | none | Filters opened by default in the sidebar. |
| `highlights` | none | Curated charts for the **Highlights** page. |
| `sections` | form groups | Tabs of the **Questions** page. |
| `map` | first location question | Which location question to map and what to show in popups. |
| `extensions` | none | Python files or folders with project-specific pages or sources. |
| `timezone` | `America/Fortaleza` | IANA time zone dates are converted to. `fielddash init` writes `UTC`. |
| `cache_minutes` | `5` | How long loaded data is cached. |

Unknown keys are rejected with an error, so typos do not pass silently.

## Referring to a question

Everywhere a question is expected (`fields`, `types`, `ignore`, `filters`, `highlights`, `sections`, `map`) you can use its alias, its full `ref`, a unique `ref` suffix of at least six characters, its column name or its question text. `fielddash fields project.yaml` lists them. A key matching more than one question is an error (ambiguous). A key matching none does not stop the app: an alias or type pointing nowhere is listed in the schema warnings, a highlight shows an error box in its slot, and an unknown filter is skipped.

## `source`

Values may reference variables as `${NAME}`. They are read from the environment, a `.env` file (current directory and project folder) or Streamlit secrets, in that order. A variable that is not defined stops loading with a clear message. Substitution applies to `source` only.

Relative paths (`schema`, `data`, `extensions`) are resolved from the folder of the YAML file.

## `fields`

```yaml
fields:
  neighborhood: "5401ce"          # ref suffix
  age: "Idade"                    # question text
```

Aliases make the rest of the file readable and survive form edits, because the key behind the alias is the stable `ref`.

## `types`

```yaml
types:
  neighborhood: category          # free text treated as a category
```

Accepts any Epicollect type name plus `category`. Typical use: a text question whose answers repeat (neighborhood, school) becomes filterable and chartable as a category. See [type handling](how-it-works.md#what-each-question-type-becomes).

## `ignore`

```yaml
ignore: [created_by, "3401cb"]
```

Ignored questions disappear from filters, charts, the map popups and the **Data** table and downloads. Use it for personal data: names, phone numbers, collector e-mails. See [Privacy](privacy.md).

## `filters`

```yaml
filters: [created_at, neighborhood, age]
```

Opens these filters in the sidebar. Only categorical, multiple-choice, numeric and date questions can be filters; others are skipped. Visitors can add more filters from the sidebar with *Add filter*. Active filters are summarised under the title.

## `highlights`

```yaml
highlights:
  - {field: waste_dest}
  - {field: collection_freq, by: neighborhood, title: "Collection frequency by neighborhood"}
```

| Key | Description |
|-----|-------------|
| `field` | Question to chart. |
| `by` | Optional categorical question to cross with (stacked bars, % within group). Ignored if it is not categorical. |
| `title` | Optional; default is the question label, or `label × by-label`. |

Highlights are drawn two per row. The **Highlights** page is hidden when the list is empty.

## `sections`

```yaml
sections:
  - {title: "Profile", fields: [age, gender, ethnicity]}
  - {title: "Waste", fields: [waste_dest, recycling]}
```

Each section becomes a tab on the **Questions** page. Without `sections`, tabs follow the form's own groups, and questions outside any group go under "Questionnaire". Locations, media and unsupported types are never listed there.

## `map`

```yaml
map: {field: location, popup: [neighborhood, age]}
```

`field` picks the location question (default: the first one in the form). `popup` lists questions shown when a point is clicked. The map offers *Points* and *Heatmap* modes. Responses without coordinates are counted in a caption.

## `extensions`

```yaml
extensions: [pages, extra/my_source.py]
```

Files, or folders whose `*.py` files are all loaded (names starting with `_` are skipped), each imported once. See [Extending](extending.md).

## `timezone` and `cache_minutes`

Dates arrive in UTC and are shown in `timezone`. Loaded data is cached for `cache_minutes` and the cache is shared by all visitors, so Epicollect receives at most one set of requests per project in that interval. It is also dropped when the YAML file changes, and the sidebar's *↻ Refresh data* button clears it.

!!! note "Older Portuguese keys"
    Early versions used `titulo`, `fonte`, `campos`, `ignorar`, `tipos`, `filtros`, `destaques`, `secoes`, `mapa`, `extensoes`, `fuso`, `cache_minutos` and, under `fonte`, `tipo`, `projeto`, `credenciais`, `dados`. They still load, with a deprecation warning, but new projects should use the English names above.
