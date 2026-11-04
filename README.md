# Firehose

A daily digest of what I published in the open: public GitHub repositories, public Hugging Face models and datasets, and my [blog](https://blog.danielrosehill.com). Each day's entry groups the work by project and subject rather than by platform, and links back to the original source.

Replaces [Project-Flow](https://github.com/danielrosehill/Project-Flow), the manually kept journal this idea started as. For the full map of my repositories, see [Start Here](https://github.com/danielrosehill/Start-Here).

## Entries

<!-- entries:begin -->
### Latest

- [2026-11-04](2026/11/2026-11-04.md): A playbook for improving a personal ASR model through daily use, a new bulk-LLM plugin, and renames that consolidate the eval, diagram and RTL plugins.

### By month

- [2026-11](2026/11/README.md) (1 days)
<!-- entries:end -->

## How it works

Entries live at `YYYY/MM/YYYY-MM-DD.md`, one per day. A day runs midnight to midnight Israel time (`Asia/Jerusalem`).

1. `scripts/collect.py [--date YYYY-MM-DD]` prints the day's activity as JSON. Standard library only. Set `GH_TOKEN` or be logged in to `gh`.
2. An agent turns that JSON into the entry, using the `write-entry` skill in the private `firehose-author` plugin.
3. `scripts/update_index.py` rebuilds the lists above and each month's `README.md`.

Forks, private repositories, gated Hugging Face items and this repository are left out. YouTube and anything else not listed above are out of scope.
