# Scholar.App

*Decentralized open-access publishing for the next era of scholarship.*

Scholar.App provides an open, federated infrastructure for publishing, reviewing, and preserving academic papers, using the AT Protocol (the federation layer behind Bluesky) and decentralized content-addressed storage.

Papers, versions, reviews, and citations are stored as **AT Protocol records**. Full-text PDFs and supplementary files are stored as **blobs**, retrievable via IPFS or any compatible blob store. Scholar.App ensures your research remains verifiable, portable, and free.

---

## ✨ Why Scholar.App?

| Problem in Traditional Academia | Scholar.App Approach |
| -------------------------------- | ---------------------- |
| Expensive paywalled journals | Open, portable, permissionless publication |
| Opaque peer review | Transparent peer-review records linked to papers |
| Link rot and PDF rot | CIDs ensure immutable, accessible content |
| Slow and siloed publishing cycles | Native support for paper versioning and dynamic updates |


---

## 1. Core Components

| Record | Purpose |
|--------|---------|
| `paper` | Canonical metadata about a scholarly work |
| `paperVersion` | Immutable version snapshots (full text blobs) |
| `paperAsset` | Supplementary files (figures, data, LaTeX, media) |
| `citation` | Formal record of cited works |
| `review` / `reviewAssignment` | Structured peer review tracking |
| `subject` | Academic subject taxonomy |
| `profile`, `reviewer`, `institution` | Scholarly identity records |

---

## 2. System Architecture

```
┌───────────────┐      createRecord        ┌───────────────┐
│  Client / UI  │ ───────────────────────▶ │  PDS Server   │
└───────────────┘                          │ (AT Protocol) │
      ▲   ▲                                └──────┬────────┘
      │   │  blob fetch (CID)                     │
REST / WS   ─────────────────────────────────────▶│
      │   │                                       ▼
      ▼   ▼                                ┌───────────────┐
     SQLite (records)   Blob store / IPFS  │  Peers / IPLD │
```

- **SQLite**: Fast, transactional local database (WAL2 journaling).
- **Blob store**: Content-addressed files (optionally pinned via IPFS).
- **AT Protocol**: Decentralized identity and record storage (via PDS).

---

## 3. Local Development

```bash
# Clone the repository
$ git clone https://github.com/scholar-app/scholar-app.git
$ cd scholar-app

# (Optional) Set up virtual environment
$ python -m venv .venv && source .venv/bin/activate

# Install requirements
$ pip install -r requirements.txt

# Initialize SQLite schema
$ sqlite3 scholar.db < schema/scholar_schema.sql

# Ingest a paper
$ python tools/ingest_paper.py \
    --file sample_paper.pdf \
    --slug quantum-graphs-study \
    --title "A Study of Quantum Graphs" \
    --author "did:example:1234,Alice Quantum" \
    --notes "v1 initial upload"

# Query the database
$ sqlite3 scholar.db "SELECT slug, title FROM paper;"
```

> **Tip:** You can also attach supplementary files using `--asset path,mimeType,description`.

---

## 4. Repository Layout

```
lexicon/                 # AT Protocol JSON schema (v1.0.3)
schema/                  # SQLite DDL and migrations
tools/
  ingest_paper.py        # CLI for paper ingestion
docs/
  lexicon.html           # Full collapsible documentation
  CHANGELOG.md
pds/                     # (Coming soon) AT Protocol server glue
```

---

## 5. Roadmap

- **Q2 2025**: Full `paperAsset` support; reader UI prototype.
- **Q3 2025**: Federated PDS deployments; citation graph indexing.
- **Q4 2025**: Open peer review incentives; reputation tracking.

Contributions welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines.

---

## 6. License

Scholar.App source code is released under the **MIT License**.

Sample papers and test data are released under **CC-BY 4.0** unless otherwise noted.

---

## Contact

- Project chat: `#scholar-app` on Bluesky Dev Slack
- Maintainers: @aliceq, @bobsmith
- Issues: Open a GitHub issue or start a discussion.

---

*Version: 1.0.3*

