#!/usr/bin/env python3
import argparse
import hashlib
import os
import shutil
import sqlite3
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# Pure-Python Base58 (Bitcoin alphabet) encoder
# ──────────────────────────────────────────────────────────────
ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def b58encode(b: bytes) -> str:
    num = int.from_bytes(b, 'big')
    encoded = ''
    while num > 0:
        num, rem = divmod(num, 58)
        encoded = ALPHABET[rem] + encoded
    # preserve leading zeros
    pad = len(b) - len(b.lstrip(b'\0'))
    return '1' * pad + encoded

# ──────────────────────────────────────────────────────────────
# Compute CIDv1 (raw codec + sha2-256 multihash + Base58btc)
# ──────────────────────────────────────────────────────────────
def compute_cid_v1(path: str) -> str:
    data = open(path, 'rb').read()
    digest = hashlib.sha256(data).digest()
    # raw multicodec = 0x55; multihash prefix = 0x12 (sha2-256) + 0x20 (length)
    prefix = b'\x55' + b'\x12\x20'
    cid_bytes = prefix + digest
    return 'b' + b58encode(cid_bytes)

# ──────────────────────────────────────────────────────────────
# Validate slug against [a-z0-9-]+
# ──────────────────────────────────────────────────────────────
def validate_slug(slug: str) -> str:
    import re
    if not re.fullmatch(r'[a-z0-9\-]+', slug):
        raise ValueError(f"Invalid slug '{slug}'. Must match [a-z0-9-]+")
    return slug

# ──────────────────────────────────────────────────────────────
# Main ingestion logic
# ──────────────────────────────────────────────────────────────
def ingest_paper(args):
    # Ensure blobs directory
    os.makedirs(args.blobs_dir, exist_ok=True)

    # Compute CID for the file
    cid = compute_cid_v1(args.file)
    ext = os.path.splitext(args.file)[1]
    blob_dst = os.path.join(args.blobs_dir, f"{cid}{ext}")
    shutil.copyfile(args.file, blob_dst)
    print(f"✔ Blob stored at: {blob_dst}")

    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # Open SQLite
    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL2;")
    conn.execute("PRAGMA foreign_keys=ON;")

    # Upsert paper metadata
    slug = validate_slug(args.slug)
    try:
        conn.execute("""
            INSERT INTO paper(
              slug, title, abstract, published_at,
              latest_version_cid, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            slug, args.title, args.abstract or '',
            args.published_at or now,
            cid, now, now
        ))
        print(f"✔ Inserted new paper '{slug}'")
    except sqlite3.IntegrityError:
        conn.execute("""
            UPDATE paper SET
              title=?, abstract=?, published_at=?,
              latest_version_cid=?, updated_at=?
            WHERE slug=?
        """, (
            args.title, args.abstract or '',
            args.published_at or now,
            cid, now, slug
        ))
        print(f"✔ Updated existing paper '{slug}'")

    # Link authors (repeatable)
    for auth in args.author:
        did, name, orcid = (auth.split(',') + [None, None])[:3]
        conn.execute("""
            INSERT OR IGNORE INTO paper_author
              (paper_slug, did, name, orcid)
            VALUES (?, ?, ?, ?)
        """, (slug, did, name or '', orcid))
        print(f"  • Author linked: {did}")

    # Determine next version number
    row = conn.execute("""
        SELECT COALESCE(MAX(version_number), 0) AS mx
          FROM paper_version WHERE paper_slug=?
    """, (slug,)).fetchone()
    ver = row["mx"] + 1

    # Insert new version
    conn.execute("""
        INSERT INTO paper_version(
          paper_slug, version_number, body_cid, uploaded_at, notes
        ) VALUES (?, ?, ?, ?, ?)
    """, (slug, ver, cid, now, args.notes or ''))
    print(f"✔ Inserted paper_version v{ver} (CID: {cid})")

    conn.commit()
    conn.close()
    print("✅ Ingestion complete.")

# ──────────────────────────────────────────────────────────────
# CLI definition
# ──────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description="Ingest a PDF/Markdown as a paper into SQLite"
    )
    p.add_argument("--db", default="scholar.db",
                   help="SQLite database file (default: scholar.db)")
    p.add_argument("--blobs-dir", default="blobs",
                   help="Directory to store blob files")
    p.add_argument("--file", required=True,
                   help="Path to PDF or Markdown file")
    p.add_argument("--slug", required=True,
                   help="Paper slug (lowercase, alphanum + hyphens)")
    p.add_argument("--title", required=True,
                   help="Paper title")
    p.add_argument("--abstract", help="Abstract text")
    p.add_argument("--published-at", help="ISO timestamp (default=now)")
    p.add_argument("--notes", help="Version notes (optional)")
    p.add_argument("--author", action="append", required=True,
                   help="Author entry as 'did,name,orcid' (repeatable)")
    args = p.parse_args()
    ingest_paper(args)

if __name__ == "__main__":
    main()
