#!/usr/bin/env python3
"""
ingest_paper.py  –  Scholar.App CLI (schema v1.0.3, 2025-04-27)

•   Adds support for supplemental assets → paper_asset
•   Records per-version authors → paper_version_author
•   Auto-detects MIME types
•   Minor UX niceties (better errors, final summary)
"""
import argparse
import hashlib
import mimetypes
import os
import re
import shutil
import sqlite3
from datetime import datetime
from typing import List, Tuple

# ──────────────────────────────────────────────────────────────
# Pure-Python Base58 (Bitcoin alphabet) encoder
# ──────────────────────────────────────────────────────────────
_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def _b58encode(raw: bytes) -> str:
    n = int.from_bytes(raw, 'big')
    out = ''
    while n:
        n, r = divmod(n, 58)
        out = _ALPHABET[r] + out
    # preserve leading 0x00
    pad = len(raw) - len(raw.lstrip(b'\0'))
    return '1' * pad + out


# ──────────────────────────────────────────────────────────────
# Compute CIDv1  (raw codec 0x55 + sha2-256 multihash)
# ──────────────────────────────────────────────────────────────
def compute_cid_v1(path: str) -> str:
    with open(path, 'rb') as fh:
        digest = hashlib.sha256(fh.read()).digest()
    prefix = b'\x55' + b'\x12\x20'          # raw + sha2-256 + 32-byte length
    return 'b' + _b58encode(prefix + digest)


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────
def validate_slug(slug: str) -> str:
    if not re.fullmatch(r'[a-z0-9\-]+', slug):
        raise ValueError(f"Invalid slug '{slug}'. Must match [a-z0-9-]+")
    return slug


def detect_mime(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or 'application/octet-stream'


def parse_author(arg: str) -> Tuple[str, str, str]:
    did, name, orcid = (arg.split(',') + [None, None])[:3]
    return did.strip(), (name or '').strip(), (orcid or '').strip()


def parse_asset(arg: str) -> Tuple[str, str]:
    """Return (path, description). Syntax:  path[,description]"""
    if ',' in arg:
        path, desc = arg.split(',', 1)
        return path.strip(), desc.strip()
    return arg.strip(), ''


# ──────────────────────────────────────────────────────────────
# Ingestion routine
# ──────────────────────────────────────────────────────────────
def ingest_paper(args):
    os.makedirs(args.blobs_dir, exist_ok=True)
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # ▸ 1.  Body blob → CID
    body_cid = compute_cid_v1(args.file)
    body_ext = os.path.splitext(args.file)[1]
    body_blob = os.path.join(args.blobs_dir, f'{body_cid}{body_ext}')
    shutil.copyfile(args.file, body_blob)
    print(f'✔ Body stored @ {body_blob}')

    # ▸ 2.  DB connect
    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL2')
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA temp_store=MEMORY')
    conn.execute('PRAGMA cache_size=-50000')

    slug = validate_slug(args.slug)

    # ▸ 3.  Upsert paper
    try:
        conn.execute("""
            INSERT INTO paper(
              slug, title, abstract, published_at,
              latest_version_cid, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (slug, args.title, args.abstract or '',
              args.published_at or now, body_cid, now, now))
        print(f'✔ Paper created  ({slug})')
    except sqlite3.IntegrityError:
        conn.execute("""
            UPDATE paper SET
              title            = ?,
              abstract         = ?,
              published_at     = ?,
              latest_version_cid = ?,
              updated_at       = ?
            WHERE slug        = ?
        """, (args.title, args.abstract or '',
              args.published_at or now, body_cid, now, slug))
        print(f'✔ Paper updated  ({slug})')

    # ▸ 4.  Paper-level authors
    authors = [parse_author(a) for a in args.author]
    for did, name, orcid in authors:
        conn.execute("""
            INSERT OR IGNORE INTO paper_author
              (paper_slug, did, name, orcid)
            VALUES (?, ?, ?, ?)
        """, (slug, did, name, orcid))

    # ▸ 5.  New version #
    ver = conn.execute("""
        SELECT COALESCE(MAX(version_number), 0) + 1 AS next
          FROM paper_version
         WHERE paper_slug = ?
    """, (slug,)).fetchone()['next']

    conn.execute("""
        INSERT INTO paper_version(
          paper_slug, version_number, body_cid, uploaded_at, notes
        ) VALUES (?, ?, ?, ?, ?)
    """, (slug, ver, body_cid, now, args.notes or ''))
    print(f'✔ Version v{ver} inserted (CID {body_cid})')

    # ▸ 6.  Version-author links
    for did, *_ in authors:
        conn.execute("""
            INSERT OR IGNORE INTO paper_version_author
              (paper_slug, version_number, author_did)
            VALUES (?, ?, ?)
        """, (slug, ver, did))

    # ▸ 7.  Supplemental assets
    assets: List[Tuple[str, str]] = [parse_asset(a) for a in (args.asset or [])]
    for path, desc in assets:
        asset_cid = compute_cid_v1(path)
        ext = os.path.splitext(path)[1]
        dst = os.path.join(args.blobs_dir, f'{asset_cid}{ext}')
        shutil.copyfile(path, dst)

        conn.execute("""
            INSERT OR IGNORE INTO paper_asset(
              paper_slug, version_number, asset_cid,
              mime_type, filename, description
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (slug, ver, asset_cid, detect_mime(path),
              os.path.basename(path), desc))
        print(f'  • Asset added: {os.path.basename(path)}  → CID {asset_cid}')

    conn.commit()
    conn.close()
    print(f'✅ Ingestion complete: {slug} v{ver} ({len(assets)} asset(s))')


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        prog='ingest_paper',
        description='Ingest a PDF/Markdown paper (and optional assets) into the Scholar.App SQLite DB.'
    )
    p.add_argument('--db', default='scholar.db',
                   help='SQLite database file (default: scholar.db)')
    p.add_argument('--blobs-dir', default='blobs',
                   help='Directory where blob files are stored')
    p.add_argument('--file', required=True,
                   help='Path to the main PDF or Markdown file')
    p.add_argument('--slug', required=True,
                   help='Paper slug (lowercase a-z, 0-9, hyphens)')
    p.add_argument('--title', required=True, help='Paper title')
    p.add_argument('--abstract', help='Abstract (optional)')
    p.add_argument('--published-at',
                   help='ISO-8601 timestamp (defaults to now)')
    p.add_argument('--notes', help='Version notes (optional)')
    p.add_argument('--author', action='append', required=True,
                   metavar='DID[,name,orcid]',
                   help='Repeatable. Example: "did:plc:abc123,Jane Doe,0000-0002-1825-0097"')
    p.add_argument('--asset', action='append',
                   metavar='PATH[,description]',
                   help='Repeatable supplemental asset')
    args = p.parse_args()
    ingest_paper(args)


if __name__ == '__main__':
    main()
