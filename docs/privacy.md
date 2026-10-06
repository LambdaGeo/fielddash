# Privacy and data protection

Field surveys often record people at their homes: who they are, what they earn, where they live. A dashboard makes that data easy to read, and, once deployed, easy to leak. This page lists what to check before the link leaves your team. It is practical guidance, not legal advice; confirm your obligations (for example LGPD in Brazil or GDPR in the EU) and your ethics approval with your institution.

## What the dashboard exposes

- Every answer in the form, unless you `ignore` it.
- **Locations.** The map plots each response. Coordinates with 4 decimal places point to within about 11 metres, which in a household survey is the house.
- **Collectors.** The Overview page counts responses per collector from `created_by`, which on Epicollect is typically the collector's e-mail.
- **A full copy of the data.** The **Data** page offers CSV and Excel downloads of the filtered responses to anyone who can open the app.
- Combinations. Age, gender, ethnicity and neighborhood may each look harmless, but together they can identify a person in a small community.

## Checklist before publishing

- [ ] **Restrict access.** Set `FIELD_ACCESS_PIN` and call `fielddash.require_access()` ([Deployment](deployment.md#restricting-access)), or host behind real authentication.
- [ ] **Ignore personal fields.** List names, phone numbers, consent forms, addresses, ZIP codes and `created_by` under `ignore`.
- [ ] **Keep real data out of Git.** `fielddash init` git-ignores `.env`, `token.json`, `.streamlit/secrets.toml` and, for `json` projects, `data/`. Check `git status` before committing.
- [ ] **Reduce coordinate precision** in any data you publish as an example: 3 decimals is about 110 m, 2 decimals about 1 km. Dropping the location question from the public version is safer still.
- [ ] **Do not publish real data as a package or example.** Anything in the repository stays in its history even after deletion. Use anonymized or synthetic data for examples.
- [ ] **Rotate leaked credentials.** If a client secret was ever committed or shared, generate a new one in Epicollect and revoke the old.

## Sensitive categories

Ethnicity, health, income, sexual orientation, religion and similar answers are treated as sensitive by most data-protection laws. If your form collects them, keep the dashboard private, minimize what is shown (use `ignore`), and decide who really needs the **Data** download.

## The bundled example

`examples/waste/` contains anonymized survey data meant for demonstration. Even so, it carries location points and demographic answers; treat any real survey you adapt it from with the same care as above.
