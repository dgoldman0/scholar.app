# 📜 Scholar.App System Change Requirements
**Topic**: Supplementary Files ("Assets") Support  
**Date**: April 27, 2025  
**Version**: Patch for v1.0.2 Schema and System

---

## 1. Lexicon Changes (JSON Schema)

### 1.1 Add New Record: `paperAsset`

```jsonc
"paperAsset": {
  "type": "object",
  "description": "Supplementary file associated with a paper version",
  "properties": {
    "paperSlug":     { "type": "string" },
    "versionNumber": { "type": "integer" },
    "assetCid":      { "type": "string" },
    "mimeType":      { "type": "string" },
    "filename":      { "type": "string" },
    "description":   { "type": "string" },
    "createdAt":     { "type": "string", "format": "date-time" }
  },
  "required": [
    "paperSlug", "versionNumber",
    "assetCid", "mimeType", "filename", "createdAt"
  ]
}
```

### 1.2 Add New Records Map Entry

```jsonc
"createPaperAsset": {
  "encoding": "application/json",
  "schema": "#/defs/paperAsset"
},
"putPaperAsset": {
  "encoding": "application/json",
  "schema": "#/defs/paperAsset"
}
```

---

## 2. SQLite Schema Changes

### 2.1 Add Table `paper_asset`

Append to `scholar_schema.sql`:

```sql
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
```

---

## 3. HTML Lexicon Documentation Changes

### 3.1 Add New Section Under “Record Definitions”

```html
<h3>📂 Paper Asset (<code>scholar.app.paperAsset</code>)</h3>
<p>Represents a supplementary file associated with a specific version of a paper (e.g., datasets, images, LaTeX sources).</p>
<ul>
  <li><span class="type">paperSlug</span> (string): The associated paper's slug.</li>
  <li><span class="type">versionNumber</span> (integer): The version number of the paper this asset belongs to.</li>
  <li><span class="type">assetCid</span> (string): Content ID (CID) of the supplementary file.</li>
  <li><span class="type">mimeType</span> (string): MIME type of the file (e.g., image/png, application/zip).</li>
  <li><span class="type">filename</span> (string): Original filename of the uploaded file.</li>
  <li><span class="type">description</span> (string, optional): Description of the file’s contents or purpose.</li>
  <li><span class="type">createdAt</span> (datetime): Timestamp of when the asset was added.</li>
</ul>
<h4>Example:</h4>
<pre>{
  "paperSlug": "quantum-graphs-study",
  "versionNumber": 1,
  "assetCid": "bafybeifilecid12345xyz",
  "mimeType": "image/png",
  "filename": "figure1.png",
  "description": "Main figure for section 2",
  "createdAt": "2025-05-01T12:00:00Z"
}</pre>
```

---

## 4. CLI Changes (`ingest_paper.py`)

### 4.1 Add `--asset` Argument

```python
p.add_argument(
  "--asset", action="append",
  help="Supplementary file as 'path,mimeType,description?' (repeatable)"
)
```

### 4.2 Add Logic to Handle Assets After Inserting `paper_version`

```python
for asset in args.asset or []:
    parts = asset.split(',', 2)
    if len(parts) < 2:
        raise ValueError("Asset must be 'path,mimeType,description?'")
    path, mime = parts[0], parts[1]
    desc = parts[2] if len(parts) == 3 else ''
    a_cid = compute_cid_v1(path)
    ext = os.path.splitext(path)[1]
    dst = os.path.join(args.blobs_dir, f"{a_cid}{ext}")
    shutil.copyfile(path, dst)
    print(f"  • Asset stored: {dst}")
    conn.execute("""
        INSERT INTO paper_asset (
            paper_slug, version_number,
            asset_cid, mime_type, filename, description, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
       slug, next_ver,
       a_cid, mime, os.path.basename(path), desc, now
    ))
    print(f"  • Asset linked: {a_cid}")
```

---

## 5. Optional (Recommended) Future Steps

| Optional Change | Purpose |
|-----------------|---------|
| Write a `getPaperAssets` API endpoint | Allow clients to fetch all supplementary files linked to a paper version |
| Add download functionality in the UI | Clicking a figure or dataset link fetches and displays it |
| Attach licensing metadata per asset | Support CC licenses, attribution requirements, etc. |

---

# 📋 Summary Checklist

| Component | Change |
|-----------|--------|
| Lexicon (JSON Schema) | Add `paperAsset` |
| Lexicon (Records) | Add `createPaperAsset`, `putPaperAsset` |
| SQLite Schema | Add `paper_asset` table |
| HTML Documentation | Add new collapsible section for assets |
| CLI Tool | Accept `--asset`, handle ingestion |

