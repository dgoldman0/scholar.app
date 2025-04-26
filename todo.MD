# Scholar.App – Asset Support Roll‑out Checklist

**Patch Version:** 1.0.3  **Date:** 26 Apr 2025
This living checklist tracks every deliverable required to add **supplementary‑file (paperAsset)** support across the entire Scholar.App stack.

---

## 1 Schema & Spec

| # | Area | Deliverable | Owner | Status |
|---|------|-------------|-------|--------|
| 1.1 | Lexicon (JSON) | New `paperAsset` definition | ✨Core Team | ✅ **Done** |
| 1.2 | Lexicon (records) | `createPaperAsset`, `putPaperAsset` operations | ✨Core Team | ✅ **Done** |
| 1.3 | Bump lexicon rev → **1.0.3** | ✨Core Team | ✅ **Done** |
| 1.4 | Update public lexicon repo & tag | Ops | ⬜ Pending |

## 2 Backend Storage

| # | Area | Deliverable | Owner | Status |
|---|------|-------------|-------|--------|
| 2.1 | SQLite | `paper_asset` table + FK + index | DB Team | ✅ **Done** |
| 2.2 | Migration script (`scholar_schema.sql`) | DB Team | ✅ **Done** |
| 2.3 | WAL2 performance test w/ asset inserts | DB Team | ⬜ Pending |

## 3 Code & Tooling

| # | Component | Deliverable | Owner | Status |
|---|-----------|-------------|-------|--------|
| 3.1 | CLI – **ingest_paper.py** | Add `--asset` flag + ingestion logic | SDK Team | ✅ **Done** |
| 3.2 | CLI – unit tests for multi‑asset ingest | SDK Team | ⬜ Pending |
| 3.3 | Blob helper | Local copy ↔ CID calc (no IPFS) | SDK Team | ✅ **Done** |
| 3.4 | IPFS pinning service (dev mode) | SDK Team | ⬜ Pending |
| 3.5 | PDS record handlers (`createPaperAsset`) | PDS Team | ⬜ Pending |
| 3.6 | PDS blob store wiring for assets | PDS Team | ⬜ Pending |

## 4 Documentation / UX

| # | Artifact | Deliverable | Owner | Status |
|---|----------|-------------|-------|--------|
| 4.1 | **HTML docs** | Add collapsible `paperAsset` section | Docs | ✅ **Done** |
| 4.2 | Markdown change‑spec (this file) | Docs | ✅ **Done** |
| 4.3 | API Reference update | Docs | ⬜ Pending |
| 4.4 | UI mockups (asset gallery) | Design | ⬜ Pending |

## 5 Testing & QA

| # | Area | Deliverable | Owner | Status |
|---|------|-------------|-------|--------|
| 5.1 | SQLite regression suite | Inserts/updates/edge cases | QA | ✅ **Done** |
| 5.2 | CLI end‑to‑end w/ assets | QA | ⬜ Pending |
| 5.3 | PDS federation test (asset replication) | QA | ⬜ Pending |

## 6 Deployment

| # | Task | Owner | Status |
|---|------|-------|--------|
| 6.1 | Stage migration on dev DBs | DevOps | ⬜ Pending |
| 6.2 | Roll to staging PDS | DevOps | ⬜ Pending |
| 6.3 | Roll to prod PDS (with back‑fill) | DevOps | ⬜ Pending |

---

### Legend
* ✅ **Done** – coded, merged, verified.  
* ⬜ Pending – not started or in progress.  
* 🔶 Blocked – requires upstream dependency.

---

## Immediate Next Actions (Week 18‑19 / 2025)
1. **SDK Team:** finish CLI unit tests (3.2).  
2. **PDS Team:** endpoint + blob store wiring (3.5 & 3.6).  
3. **DevOps:** prepare dev DB migration (6.1).  
4. **Docs:** publish API reference update (4.3).

---

_Last updated: 26 Apr 2025 – 16:24 UTC



