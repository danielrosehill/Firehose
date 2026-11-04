# Firehose entry format

Approved by Daniel 2026-11-04 on the sample `2026/11/2026-11-03.json`. Live at `https://blog.danielrosehill.com/firehose/`.

An entry lists the public projects created on one day (midnight to midnight, `Asia/Jerusalem`). A day with no created projects gets no entry.

## Pipeline

Everything is scripted except the intro. An agent's only writing task is that one paragraph.

1. `scripts/assemble.py --from YYYY-MM-DD --to YYYY-MM-DD` lists public repos, models and datasets, groups them by creation day and writes `YYYY/MM/YYYY-MM-DD.json` with no `intro`. Names, types and descriptions come from metadata. Existing days are skipped unless `--force`. If a source fails it aborts and writes nothing.
2. `with-secrets python3 scripts/write_intros.py` fills each missing `intro`, one call per day, through OpenRouter on `deepseek/deepseek-v4.1-flash`, and prints measured cost.
3. `scripts/render_entry.py <json>...` validates, sorts the projects, sets the templated `summary` and writes the `.md`.
4. `scripts/update_index.py` rebuilds the month and root indexes, each month's `wrap-up.md` (the days concatenated section by section, no AI) `data.json` and `stats.json`, which the blog reads at build time.

Never edit a `.md`, `data.json` or `stats.json` by hand. To correct an entry, edit its `.json` and rerun steps 3 and 4.

## JSON schema

```json
{
  "date": "2026-11-03",
  "summary": "Public projects created on 3 November 2026: 4 repos, 2 datasets and 2 models.",
  "intro": "Two or three plain sentences saying what was created and across which areas.",
  "scope": "created",
  "projects": [
    {
      "name": "Network Forensics Plugin",
      "url": "https://github.com/danielrosehill/Network-Forensics-Plugin",
      "network": "GitHub",
      "section": "repos",
      "type": "Agent plugin",
      "description": "One line saying what it is."
    }
  ]
}
```

| Field | Source and allowed values |
| --- | --- |
| `summary` | Templated by `render_entry.py`. Used as the page description and on the indexes |
| `intro` | The only AI-written field: two or three sentences, 60 words at most |
| `name` | Normalised from the machine name by `assemble.py`: spaces for hyphens and underscores, words capitalised, known casing kept (`ChatGPT`, `GGUF`, `MCP`, `IP`, `ASR`; list in `CASING`). `render_entry.py` rejects a name containing `-` or `_` |
| `network` | `GitHub`, `Hugging Face` |
| `section` | `repos` (GitHub Repositories), `datasets` (Datasets), `models` (AI Models) |
| `type` for `repos` | `Agent plugin`, `MCP server`, `Application`, `Tool`, `Website`, `Documentation`, `Prompt collection`, `Evaluation`, `Other` |
| `type` for `datasets` | `Training dataset`, `Evaluation dataset`, `Audio dataset`, `Reference dataset`, `Other` |
| `type` for `models` | `Fine-tuned model`, `Quantised model`, `Other` |
| `description` | The GitHub description, or else the first paragraph of the README or model card, cut to 200 characters. Falls back to `No description published.` |

`type` is a rule-based guess from names, tags and descriptions, so expect the odd miss. Sections render in the order above, and a section with no projects has no header. Each section opens with a count ("4 repos created"). Projects sort alphabetically by `name` within a section.

Forks, private repositories, gated Hugging Face items and this repository are left out. A project that later stops being public is removed from its entry.

## Reads

- Blog: `/firehose/` (with a month-by-month chart), `/firehose/YYYY/MM/`, `/firehose/YYYY/MM/wrap-up/`, `/firehose/YYYY/MM/DD/`
- RSS: `https://blog.danielrosehill.com/firehose/rss.xml` (latest 50 days)
- JSON Feed 1.1: `https://blog.danielrosehill.com/firehose/feed.json` (every day, projects under `_firehose`)
- Raw, `data.json` in this repo: `entries`, the full record of every day
- Raw, `stats.json` in this repo: counts only, for charts and tables. `totals`, `by_month` and `by_day`, each with `repos`, `datasets`, `models` and `total`. Days with nothing created are absent from `by_day`

## Planned

- **Repos updated** (raised by Daniel 2026-11-04, left for later): list existing repos that changed on the day. Measured for 2025-11-04 to 2026-11-04 on GitHub: at least 1,166 repo-days, 3,798 commits, 369 repos, median 3 a day, peak 59. The GraphQL `contributionsCollection.commitContributionsByRepository` query gives per-repo daily counts cheaply, in windows of a week or less because it caps at 100 repos. Proposed shape: a single `Updated` section at the bottom, plain one-line items, sweeps collapsed, data refreshes dropped. `collect.py` is kept for this.
