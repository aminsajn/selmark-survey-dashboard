"""
Diagnostic: count ALL rows in Supabase (with pagination) and cross-reference
with the 1664 IDs that Cint says are complete.

Run: python check_supabase_count.py
Requires SUPABASE_URL and SUPABASE_KEY in environment or .env file.
"""

import os, sys
from pathlib import Path

# Load .env if present
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

url = os.environ.get('SUPABASE_URL', '')
key = os.environ.get('SUPABASE_KEY', '')

if not url or not key:
    print("ERROR: SUPABASE_URL / SUPABASE_KEY not set.")
    print("Set them in a .env file or environment variables.")
    sys.exit(1)

from supabase import create_client
client = create_client(url, key)

# ── 1. Count ALL rows with pagination ────────────────────────────────────────
print("Fetching all rows from Supabase (paginated)...")
all_rows = []
page_size = 1000
offset = 0
while True:
    resp = (
        client.table('survey_responses')
        .select('id, respondent_id, status, survey_id, created_at')
        .range(offset, offset + page_size - 1)
        .execute()
    )
    batch = resp.data or []
    all_rows.extend(batch)
    print(f"  Fetched page offset={offset}: {len(batch)} rows (total so far: {len(all_rows)})")
    if len(batch) < page_size:
        break
    offset += page_size

print(f"\nTotal rows in Supabase (all statuses): {len(all_rows)}")

status_counts = {}
for r in all_rows:
    s = r.get('status', 'unknown')
    status_counts[s] = status_counts.get(s, 0) + 1
for s, c in sorted(status_counts.items(), key=lambda x: -x[1]):
    print(f"  status={s!r}: {c}")

complete_rows = [r for r in all_rows if r.get('status') == 'complete']
print(f"\nComplete rows: {len(complete_rows)}")

supabase_respondent_ids = {str(r['respondent_id']).strip() for r in complete_rows}

# ── 2. Load Cint IDs from Excel ──────────────────────────────────────────────
cint_path = Path(r'C:\Users\ajulve\Downloads\Cint Completes.xlsx')
if not cint_path.exists():
    print("\nCint Completes.xlsx not found — skipping cross-reference.")
    sys.exit(0)

import openpyxl
wb = openpyxl.load_workbook(cint_path)
ws = wb.active
rows_xl = list(ws.iter_rows(values_only=True))
cint_ids = {str(r[0]).strip() for r in rows_xl[1:] if r[0]}
print(f"\nCint IDs total: {len(cint_ids)}")

# ── 3. Cross-reference ────────────────────────────────────────────────────────
in_both       = cint_ids & supabase_respondent_ids
in_cint_only  = cint_ids - supabase_respondent_ids
in_supa_only  = supabase_respondent_ids - cint_ids

print(f"\nCross-reference:")
print(f"  In BOTH (Cint + Supabase):        {len(in_both)}")
print(f"  In Cint ONLY (missing in Supa):   {len(in_cint_only)}")
print(f"  In Supabase ONLY (not in Cint):   {len(in_supa_only)}")

if in_cint_only:
    print(f"\nFirst 10 IDs in Cint but missing from Supabase:")
    for rid in sorted(in_cint_only)[:10]:
        print(f"  {rid}")

if in_supa_only:
    print(f"\nFirst 10 IDs in Supabase but NOT in Cint:")
    for rid in sorted(in_supa_only)[:10]:
        print(f"  {rid}")
