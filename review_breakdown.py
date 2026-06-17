"""Break down the 58 REVIEW cases by what's actually wrong."""
import json
import quality_check as qc
from collections import Counter

with open(r'C:\Users\ajulve\Downloads\selmark_respuestas_2026-06-12 (1).json', encoding='utf-8') as f:
    data = json.load(f)
completed = [r for r in data if r.get('status') == 'complete']
results   = {r['respondent_id']: r for r in [qc.assess_response(row) for row in completed]}

reviews = [r for r in results.values() if r['verdict'] == 'REVIEW']

# Categorise each REVIEW by which rules fired
def get_rules(r):
    return set(seg.split(':')[0].strip() for seg in r['flag_summary'].split('; ') if seg != 'OK')

# Count how many have ONLY attribute SL (no other issue)
only_attr_sl, only_why, only_copy, mixed, only_lifestyle_sl = [], [], [], [], []

for r in reviews:
    rules = get_rules(r)
    attr_sl   = any('straight_line_attributes' in rule for rule in rules)
    life_sl   = any('straight_line_lifestyle'  in rule for rule in rules)
    why       = 'short_why_answers'  in rules
    copy      = 'copy_paste'         in rules
    poor_text = 'poor_open_text'     in rules
    long_time = 'very_long_time'     in rules

    real_issues = {r for r in rules if r not in ('very_long_time', 'no_duration')}

    if real_issues == {'straight_line_attributes'}:
        only_attr_sl.append(r)
    elif real_issues == {'straight_line_lifestyle'}:
        only_lifestyle_sl.append(r)
    elif real_issues == {'short_why_answers'}:
        only_why.append(r)
    elif real_issues == {'copy_paste'}:
        only_copy.append(r)
    else:
        mixed.append(r)

print(f'Total REVIEW: {len(reviews)}')
print()
print(f'  Only straight-lining in ATTRIBUTES:  {len(only_attr_sl):2d}  — scale data unreliable, rest of survey OK')
print(f'  Only straight-lining in LIFESTYLE:   {len(only_lifestyle_sl):2d}  — lifestyle data unreliable, rest OK')
print(f'  Only short/empty why-answers:        {len(only_why):2d}  — open text weak, scales OK')
print(f'  Only copy-paste in open text:        {len(only_copy):2d}  — open text weak, scales OK')
print(f'  Mixed (2+ different issues):         {len(mixed):2d}  — more problematic')
print()

print('=== Only attribute SL (borderline — scales useless but rest valid) ===')
for r in only_attr_sl:
    print(f'  {r["respondent_id"][:36]}  {r["duration_min"]:>6}m  {r["flag_summary"][:90]}')

print()
print('=== Mixed issues (2+ problems) ===')
for r in mixed:
    print(f'  {r["respondent_id"][:36]}  {r["duration_min"]:>6}m  {r["flag_summary"][:100]}')
