"""Fetch ALL complete responses from Supabase and save to JSON."""
import os, json
from pathlib import Path

env_path = Path(__file__).parent / '.env'
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

from supabase import create_client
client = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

all_rows, offset, page_size = [], 0, 1000
while True:
    batch = (
        client.table('survey_responses')
        .select('*')
        .eq('status', 'complete')
        .range(offset, offset + page_size - 1)
        .execute()
    ).data or []
    all_rows.extend(batch)
    print(f"  offset={offset}: {len(batch)} rows (total: {len(all_rows)})")
    if len(batch) < page_size:
        break
    offset += page_size

out = Path(r'C:\Users\ajulve\Downloads\selmark_respuestas_full.json')
out.write_text(json.dumps(all_rows, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"\nSaved {len(all_rows)} rows -> {out}")
