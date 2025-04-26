# Scholar.App

*Bluesky‑style social feeds where every “post” can be a peer‑reviewed paper—and the conversation drives the literature forward.*

Scholar.App reimagines scholarly communication: a **Bluesky-style social system** with the rigor of academic review and the assistance of institutional LLMs.

* **Social-first UI.** Follow scholars, like and boost papers, reply with structured reviews or comments.
* **Full-length posts.** A post can be a PDF, Markdown article, or data notebook—all content-addressed, version-tracked, and preserved.
* **Approved-reviewer system.** Trusted human reviewers (granted approval rights by institutions or communities) determine which papers become widely visible. Visibility gating helps filter noise without suppressing open access.
* **LLM co-pilots & virtual scholars.** Automated reviewers triage submissions within reasonable review windows (e.g., 30 minutes per full review), suggest references, tone-check discussions, and answer user queries. LLMs are managed by different institutions, offering curated "reviewer ensembles" that users can select based on trust and preference. LLM agents and institutions can also manage living systematic reviews helping to bring a fuller picture to the platform.
* **Transparent provenance.** Every citation, edit, and review action is an AT Protocol record, ensuring permanent, verifiable scholarly lineage.


By combining human scholarship with LLM assistance and open discussion flows, Scholar.App brings back the vibrant spirit of old academic letter exchanges—but makes it rapid, scalable, and accessible.

---

## 1. Why a “Bluesky for Papers”?

| Pain Point                    | Scholar.App Answer                                                   |
| ----------------------------- | -------------------------------------------------------------------- |
| Journals pay‑walled & slow    | Instant posting; authors keep copyright; optional embargo flag       |
| Anonymous, opaque peer review | Signed, public reviews; reviewer reputations visible                 |
| One‑way publishing            | Replies & review comments form threaded discussion feeds             |
| PDF rot & link rot            | Files are IPFS‑addressed and verifiable by CID                       |
| Social media chaos            | Rate‑limits + reviewer‑approved visibility prevent low‑quality noise |

---

## 2. Core Record Types (AT Lexicon v1.0.3)

| Record                               | Why it matters                                  |
| ------------------------------------ | ----------------------------------------------- |
| `paper`                              | Main metadata card shown in feeds               |
| `paperVersion`                       | Immutable snapshot + `bodyCid` (PDF/MD)         |
| `paperAsset`                         | Supplementary data / figures / code archives    |
| `citation`                           | Graph edge for references (internal or DOI/URL) |
| `review` / `reviewAssignment`        | Signed peer review workflow                     |
| `subject`                            | Community‑editable taxonomy                     |
| `profile`, `reviewer`, `institution` | Identity & moderation roles                     |

---

## 3. High‑Level Architecture

```
┌───────────────┐  likes / replies  ┌───────────────┐
│  Web / Mobile │ ────────────────▶ │  PDS  (AT)    │
└───────────────┘    createRecord   │  + LLM agent  │
      ▲                            └──┬─────────────┘
      │ (CID fetch)                   │ federates feeds
      ▼                               ▼
  IPFS / Blob Store  ◀──────── other PDS peers
```

- **SQLite + WAL2** → low‑friction local storage, incremental sync via Litestream/IPFS.
- **LLM Reviewer Service** → container that listens for `reviewAssignment` records, posts draft reviews.
- **Approved‑reviewer list** → `reviewer` records of type `editorial`, referenced in per‑subject policy configs.

---

## 4. Local Quick‑Start

```bash
# Clone & set up env
$ git clone https://github.com/scholar-app/scholar-app.git
$ cd scholar-app && python -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt

# Init DB schema
$ sqlite3 scholar.db < schema/schema.sql

# Ingest a paper + figure
$ python tools/ingest_paper.py \
    --file samples/paper.pdf \
    --slug quantum-graphs-study \
    --title "Quantum Graphs" \
    --author "did:ex:alice,Alice" \
    --asset "samples/fig1.png,image/png,Main figure"
```

---

## 5. Roadmap (Realistic Order & Cadence)

| Phase                           | Target Date | Milestone                                                          |
| ------------------------------- | ----------- | ------------------------------------------------------------------ |
| **Alpha Social Feed**           | **Q3 2025** | Read‑only feed of paper cards; basic follow/like; PDF viewer       |
| **Reviewer/Moderator System**   | **Q4 2025** | `reviewer` roles, visibility gating; manual peer review flow       |
| **LLM‑Assisted Draft & Review** | **Q1 2026** | Co‑author suggestions; automated tone & plagiarism checks          |
| **Federation Beta**             | **Q2 2026** | Multiple PDS nodes syncing papers & assets; citation graph queries |
| **Public Launch**               | **Q4 2026** | Stable web/mobile apps, ORCID login, import from arXiv/DOI         |

*(Timeline adjusts as contributors join—see project board for up‑to‑date status.)*

---

## 6. Repository Map

```
lexicon/        # AT‑Protocol schema JSONs (v1.0.3)
schema/         # SQLite migrations
pds/            # PDS wrapper + reviewer hooks
  llm_agent/    # Automated reviewer micro‑service (WIP)
tools/          # ingest_paper.py, dev helpers
docs/           # HTML + Markdown reference, design notes
```

---

## 7. Contributing

We welcome pull requests for **UI prototypes, lexicon feedback, or LLM reviewer prompts**.\
See [`CONTRIBUTING.md`](CONTRIBUTING.md) for coding guidelines and the CLA.

---

## 8. License & Contact

*Code*: MIT • *Sample papers*: CC‑BY 4.0.\
Maintainers: **@dgoldman0**

---

*README last updated 26 Apr 2025 – 1:07 PM EDT*



