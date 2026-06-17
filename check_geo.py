"""Verify geographic segmentation from postal codes in actual data."""
import json
from collections import Counter

with open(r'C:\Users\ajulve\Downloads\selmark_respuestas_2026-06-12 (1).json', encoding='utf-8') as f:
    data = json.load(f)

prefixes = Counter()
madrid, barcelona, other = [], [], []

for r in data:
    cp = str((r.get('answers') or {}).get('q1', '')).strip().zfill(5)
    if not cp or cp == '00000': continue
    prefix = cp[:2]
    prefixes[prefix] += 1
    if prefix == '28':   madrid.append(cp)
    elif prefix == '08': barcelona.append(cp)
    else:                other.append(cp)

print(f'Madrid    (28xxx): {len(madrid)} responses')
print(f'Barcelona (08xxx): {len(barcelona)} responses')
print(f'Rest of Spain:     {len(other)} responses')
print()
print('All prefixes found:', dict(prefixes.most_common()))
print()
print('Sample Madrid CPs:',    madrid[:5])
print('Sample Barcelona CPs:', barcelona[:5])
print('Sample Other CPs:',     other[:8])
