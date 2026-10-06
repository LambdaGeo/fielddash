# How it works

## The problem with Epicollect exports

Epicollect names each column of an export `{index}_{question}`, where `index` counts every entry of the form (groups included, `readme` blocks excluded) and the question keeps only ASCII letters, digits and spaces, cut to 20 characters. Inserting a question shifts the index of everything after it, and renaming one changes the name. Any tool that refers to `14_Renda_familiar_me` is one form edit away from breaking.

## The approach

Every question in the form schema has a stable `ref`. fielddash works like this:

1. The **source** returns the form schema and the raw responses ([Data sources](sources.md)).
2. The schema is parsed into a list of fields (ref, label, type, options, group) and the expected export column of each one is computed.
3. Each field is **reconciled** with the columns actually present in the data. If the expected column is missing (an outdated local schema, renumbered questions), fielddash looks for a column whose name matches the question text, ignoring the index. It never matches by position. Every adjustment, and every mismatch it cannot resolve, becomes a warning.
4. Your `fields` (aliases), `types` and `ignore` are applied.
5. The data is **normalized** into typed columns and the pages render from that.

Warnings appear in the app under the title (*⚠ n warning(s) about the form schema*) and at the end of `fielddash fields`.

## How a field key is resolved

When the YAML or a custom page refers to a question, fielddash tries, in order:

1. the alias;
2. the full `ref` or the column name;
3. the question text, ignoring case;
4. a `ref` ending with the key (keys of at least six characters).

The first step that matches **exactly one** field wins. A step matching several fields is an error (ambiguous key), so a short suffix that happens to match twice is reported rather than guessed.

## What each question type becomes

| Epicollect types | Handled as | Filter | Visualization |
|------------------|-----------|--------|---------------|
| `radio`, `dropdown`, `searchsingle`, `category` | categorical | multi-select | Horizontal bars with count and %, in form order. Crossed with another category: stacked bars, % within group. Beyond 8 groups the rest is folded into "Other". |
| `checkbox`, `searchmultiple` | multiple choice | multi-select (any of the chosen) | Bars with % of respondents; the sum may exceed 100%. |
| `integer`, `decimal` | numeric | range slider | Distribution of values with mean and median; box plot when crossed with a category. |
| `date`, `datetime` | date | date range | Entries per day, week or month, chosen from the time span. |
| `location` | location | none | Map with points or heatmap. |
| `text`, `textarea`, `phone`, `barcode`, `time` | text | none | Table of open answers (hidden by default on **Questions**). |
| `photo`, `audio`, `video` | media | none | None. |
| anything else | other | none | A note that there is no automatic visualization. |

Two system fields exist in every project: `created_at` (*Collection date*) and `created_by` (*Collector*).

## Normalization

- Empty strings become missing values.
- Categorical answers keep the form's option order; answers not among the options are appended alphabetically. Extra whitespace is collapsed.
- For text forced to `category` (no predefined options), spellings that differ only in case or spacing (`"foo bar"`, `"Foo  Bar"`, `"FooBar"`) are merged into the most frequent one.
- Multiple-choice answers become lists.
- Locations are split into latitude and longitude columns.
- Dates are parsed as UTC and converted to `timezone`.
