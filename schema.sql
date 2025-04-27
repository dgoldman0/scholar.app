/* ===========================================================
   Scholar.App SQLite schema  –  v1.0.3   (2025-04-27)
   =========================================================== */

/* ── GLOBAL PRAGMAS ───────────────────────────────────────── */
PRAGMA journal_mode = WAL2;      -- dual-log write-ahead
PRAGMA synchronous   = NORMAL;   -- safe + fast for WAL2
PRAGMA foreign_keys  = ON;       -- enforce FK constraints
PRAGMA temp_store    = MEMORY;   -- temp b-trees stay off-disk
/* 50 MiB page-cache (negative ⇒ kibibytes) */
PRAGMA cache_size    = -50000;   

/* Helper: ISO-8601 UTC timestamp default
   ─────────────────────────────────────────
   strftime('%Y-%m-%dT%H:%M:%fZ','now')
*/

/* ===========================================================
   1.  ORGANISATIONS & PEOPLE
   =========================================================== */

CREATE TABLE institution (
  slug         TEXT PRIMARY KEY
               CHECK (slug GLOB '[a-z0-9-]*'),
  name         TEXT    NOT NULL,
  type         TEXT    NOT NULL
               CHECK (type IN ('university','lab','club',
                                'publisher','organization')),
  website      TEXT,
  location     TEXT,
  description  TEXT,
  logo_cid     TEXT,
  created_at   TEXT    NOT NULL
               DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at   TEXT
);

CREATE TABLE profile (
  did              TEXT PRIMARY KEY,
  handle           TEXT    NOT NULL
                    CHECK (handle GLOB '[a-z0-9-]*'),
  name             TEXT,
  affiliation_slug TEXT
                    REFERENCES institution(slug)
                    ON DELETE SET NULL,
  orcid            TEXT,
  bio              TEXT,
  created_at       TEXT    NOT NULL
                    DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at       TEXT
);

/* ===========================================================
   2.  PAPER & VERSIONING
   =========================================================== */

CREATE TABLE paper (
  slug               TEXT PRIMARY KEY
                      CHECK (slug GLOB '[a-z0-9-]*'),
  title              TEXT    NOT NULL,
  abstract           TEXT,
  published_at       TEXT,
  latest_version_cid TEXT    NOT NULL,
  citations_count    INTEGER NOT NULL DEFAULT 0,
  created_at         TEXT    NOT NULL
                      DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at         TEXT    NOT NULL
);

CREATE TABLE paper_author (
  paper_slug  TEXT NOT NULL
              REFERENCES paper(slug) ON DELETE CASCADE,
  did         TEXT NOT NULL,
  name        TEXT NOT NULL,
  orcid       TEXT,
  PRIMARY KEY (paper_slug, did)
);

/* ----- Immutable versions ----- */
CREATE TABLE paper_version (
  paper_slug     TEXT NOT NULL
                 REFERENCES paper(slug) ON DELETE CASCADE,
  version_number INTEGER NOT NULL,
  body_cid       TEXT    NOT NULL,
  uploaded_at    TEXT    NOT NULL,
  notes          TEXT,
  PRIMARY KEY (paper_slug, version_number)
);

CREATE TABLE paper_version_author (
  paper_slug     TEXT NOT NULL,
  version_number INTEGER NOT NULL,
  author_did     TEXT NOT NULL,
  PRIMARY KEY (paper_slug, version_number, author_did),
  FOREIGN KEY (paper_slug, version_number)
      REFERENCES paper_version(paper_slug, version_number)
      ON DELETE CASCADE
);

/* ===========================================================
   3.  CITATION SYSTEM
   =========================================================== */

CREATE TABLE citation (
  id                   INTEGER PRIMARY KEY AUTOINCREMENT,
  citing_version_cid   TEXT    NOT NULL,

  /* One-of target fields (exactly one must be non-NULL) */
  target_paper_slug    TEXT,
  target_paper_version INTEGER,
  target_doi           TEXT,
  target_url           TEXT,
  target_raw_bibtex    TEXT,

  context              TEXT,
  label                TEXT,
  created_at           TEXT    NOT NULL
                    DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

/* -- maintain paper.citations_count automatically -- */
CREATE TRIGGER trg_citation_insert
AFTER INSERT ON citation
WHEN NEW.target_paper_slug IS NOT NULL
BEGIN
  UPDATE paper
     SET citations_count = citations_count + 1
   WHERE slug = NEW.target_paper_slug;
END;

CREATE TRIGGER trg_citation_delete
AFTER DELETE ON citation
WHEN OLD.target_paper_slug IS NOT NULL
BEGIN
  UPDATE paper
     SET citations_count = MAX(citations_count - 1, 0)
   WHERE slug = OLD.target_paper_slug;
END;

/* ===========================================================
   4.  REVIEW WORKFLOW
   =========================================================== */

CREATE TABLE review (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  paper_slug     TEXT    NOT NULL,
  version_number INTEGER NOT NULL,
  reviewer_did   TEXT    NOT NULL,
  decision       TEXT    NOT NULL
                  CHECK (decision IN ('accept','revise','reject')),
  comments       TEXT    NOT NULL,
  rating         REAL,
  created_at     TEXT    NOT NULL
                  DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  FOREIGN KEY (paper_slug, version_number)
      REFERENCES paper_version(paper_slug, version_number)
      ON DELETE CASCADE
);

CREATE TABLE review_assignment (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  paper_slug       TEXT    NOT NULL,
  version_number   INTEGER NOT NULL,
  reviewer_did     TEXT    NOT NULL,
  assigned_by_did  TEXT    NOT NULL,
  assigned_at      TEXT    NOT NULL
                  DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  due_date         TEXT,
  FOREIGN KEY (paper_slug, version_number)
      REFERENCES paper_version(paper_slug, version_number)
      ON DELETE CASCADE
);

/* ===========================================================
   5.  SUBJECT TAXONOMY
   =========================================================== */

CREATE TABLE subject (
  slug         TEXT PRIMARY KEY
               CHECK (slug GLOB '[a-z0-9-]*'),
  name         TEXT NOT NULL,
  description  TEXT,
  parent_slug  TEXT
               REFERENCES subject(slug)
               ON DELETE SET NULL,
  created_at   TEXT
               DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE paper_subject (
  paper_slug   TEXT NOT NULL
               REFERENCES paper(slug) ON DELETE CASCADE,
  subject_slug TEXT NOT NULL
               REFERENCES subject(slug) ON DELETE CASCADE,
  assigned_at  TEXT
               DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  PRIMARY KEY (paper_slug, subject_slug)
);

/* ===========================================================
   6.  REVIEWER REGISTRY
   =========================================================== */

CREATE TABLE reviewer (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  reviewer_did     TEXT,   -- NULL = bot
  name             TEXT    NOT NULL,
  type             TEXT    NOT NULL
                  CHECK (type IN ('human','automated','editorial')),
  affiliation_slug TEXT
                  REFERENCES institution(slug) ON DELETE SET NULL,
  endpoint         TEXT,
  created_at       TEXT    NOT NULL
                  DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at       TEXT
);

CREATE TABLE reviewer_expertise (
  reviewer_id  INTEGER NOT NULL
               REFERENCES reviewer(id) ON DELETE CASCADE,
  subject_slug TEXT    NOT NULL
               REFERENCES subject(slug) ON DELETE CASCADE,
  PRIMARY KEY (reviewer_id, subject_slug)
);

CREATE TABLE paper_asset (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  paper_slug     TEXT    NOT NULL
                   REFERENCES paper(slug) ON DELETE CASCADE,
  version_number INTEGER NOT NULL,
  asset_cid      TEXT    NOT NULL,
  mime_type      TEXT    NOT NULL,
  filename       TEXT    NOT NULL,
  description    TEXT,
  created_at     TEXT    NOT NULL
                   DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  FOREIGN KEY (paper_slug, version_number)
    REFERENCES paper_version(paper_slug, version_number)
    ON DELETE CASCADE
);

CREATE INDEX idx_paper_asset_version
  ON paper_asset(paper_slug, version_number);

/* ===========================================================
   7.  FULL-TEXT SEARCH  (title & abstract)
   =========================================================== */

CREATE VIRTUAL TABLE fts_paper
USING fts5(slug UNINDEXED, title, abstract);

CREATE TRIGGER fts_paper_after_insert
AFTER INSERT ON paper
BEGIN
  INSERT INTO fts_paper(rowid, slug, title, abstract)
  VALUES (NEW.rowid, NEW.slug, NEW.title, NEW.abstract);
END;

CREATE TRIGGER fts_paper_after_update
AFTER UPDATE OF title, abstract ON paper
BEGIN
  UPDATE fts_paper
     SET title   = NEW.title,
         abstract= NEW.abstract
   WHERE rowid = OLD.rowid;
END;

CREATE TRIGGER fts_paper_after_delete
AFTER DELETE ON paper
BEGIN
  DELETE FROM fts_paper WHERE rowid = OLD.rowid;
END;

/* ===========================================================
   8.  INDEXES  (query-path tuned)
   =========================================================== */

/* 8.1 Profiles & Institutions */
CREATE INDEX IF NOT EXISTS idx_profile_affiliation
          ON profile(affiliation_slug);

/* 8.2 Papers */
CREATE UNIQUE INDEX IF NOT EXISTS idx_paper_latest_cid
                    ON paper(latest_version_cid);

/* 8.3 Authorship */
CREATE INDEX IF NOT EXISTS idx_paper_author_did
          ON paper_author(did);

CREATE INDEX IF NOT EXISTS idx_version_author_did
          ON paper_version_author(author_did);

/* 8.4 Paper versions */
CREATE INDEX IF NOT EXISTS idx_paper_version_time
          ON paper_version(paper_slug, uploaded_at DESC);

/* 8.5 Citations (partial where majority of rows have NULL) */
CREATE INDEX IF NOT EXISTS idx_citation_target_paper
          ON citation(target_paper_slug, target_paper_version)
       WHERE target_paper_slug IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_citation_target_doi
          ON citation(target_doi)
       WHERE target_doi IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_citation_target_url
          ON citation(target_url)
       WHERE target_url IS NOT NULL;

/* 8.6 Reviews */
CREATE INDEX IF NOT EXISTS idx_review_paper
          ON review(paper_slug, version_number);

CREATE INDEX IF NOT EXISTS idx_review_reviewer
          ON review(reviewer_did);

CREATE INDEX IF NOT EXISTS idx_review_assignment_reviewer
          ON review_assignment(reviewer_did, due_date);

CREATE INDEX IF NOT EXISTS idx_review_assignment_paper
          ON review_assignment(paper_slug, version_number);

/* 8.7 Subjects & expertise */
CREATE INDEX IF NOT EXISTS idx_paper_subject_subject
          ON paper_subject(subject_slug);

CREATE INDEX IF NOT EXISTS idx_reviewer_expertise_subject
          ON reviewer_expertise(subject_slug);

/* 8.8 Assets */
CREATE UNIQUE INDEX IF NOT EXISTS idx_paper_asset_cid
                    ON paper_asset(asset_cid);

/* 8.9 Misc handy indexes from v1.0.2 */
CREATE INDEX IF NOT EXISTS idx_paper_version_uploaded
          ON paper_version(uploaded_at);

CREATE INDEX IF NOT EXISTS idx_citation_citing
          ON citation(citing_version_cid);


