"""
Quota progress report for Cint.
Generates two files:
  - quota_summary.csv   : progress per quota cell vs target
  - valid_ids.csv       : list of valid respondent IDs with their quota segments

Usage:
    python quota_report.py responses.json
"""

import json, csv, sys, argparse
from pathlib import Path
from collections import defaultdict
import quality_check as qc

# ── QUOTA TARGETS (out of 1200 valid completes) ───────────────────────────────
TOTAL_TARGET = 1200

AGE_QUOTAS = {
    '18-30': {'pct': 0.20, 'min': 18, 'max': 30},
    '31-45': {'pct': 0.50, 'min': 31, 'max': 45},
    '46+':   {'pct': 0.30, 'min': 46, 'max': 99},
}

GEO_QUOTAS = {
    'Madrid/Barcelona': {'pct': 0.50},
    'Rest of Spain':    {'pct': 0.50},
}

MAD_BCN_PREFIXES = {'28', '08'}  # Madrid=28xxx, Barcelona=08xxx


def age_group(age_raw):
    try:
        age = int(age_raw)
    except (TypeError, ValueError):
        return None
    for label, cfg in AGE_QUOTAS.items():
        if cfg['min'] <= age <= cfg['max']:
            return label
    return None


def geo_group(cp_raw):
    if not cp_raw:
        return None
    cp = str(cp_raw).strip().zfill(5)
    return 'Madrid/Barcelona' if cp[:2] in MAD_BCN_PREFIXES else 'Rest of Spain'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='JSON export from Supabase')
    args = parser.parse_args()

    input_path = Path(args.input)
    with open(input_path, encoding='utf-8') as f:
        data = json.load(f)

    completed = [r for r in data if r.get('status') == 'complete']
    results   = [qc.assess_response(r) for r in completed]
    res_map   = {r['respondent_id']: r for r in results}

    # Only count OK responses as valid for quota purposes
    valid = [r for r in completed if res_map[r['respondent_id']]['verdict'] == 'OK']

    # Count per quota cell
    age_counts = defaultdict(int)
    geo_counts = defaultdict(int)
    cell_counts = defaultdict(int)  # (age_group, geo_group)

    valid_rows = []
    for r in valid:
        answers = r.get('answers', {}) or {}
        ag = age_group(answers.get('q2'))
        gg = geo_group(answers.get('q1'))
        age_counts[ag or 'unknown'] += 1
        geo_counts[gg or 'unknown'] += 1
        if ag and gg:
            cell_counts[(ag, gg)] += 1
        valid_rows.append({
            'respondent_id': r['respondent_id'],
            'survey_id':     r.get('survey_id', ''),
            'age':           answers.get('q2', ''),
            'postal_code':   answers.get('q1', ''),
            'age_group':     ag or 'unknown',
            'geo_group':     gg or 'unknown',
            'verdict':       res_map[r['respondent_id']]['verdict'],
        })

    total_valid = len(valid)

    # ── SUMMARY ──────────────────────────────────────────────────────────────
    print(f'\n=== QUOTA PROGRESS REPORT ===')
    print(f'Total responses: {len(completed)}  |  Valid (OK): {total_valid}  |  Target: {TOTAL_TARGET}')
    print(f'Overall progress: {total_valid}/{TOTAL_TARGET} ({100*total_valid//TOTAL_TARGET}%)\n')

    print(f'{"Quota":<22} {"Target N":>8} {"Have":>6} {"Need":>6} {"Progress":>10}')
    print('-' * 56)

    summary_rows = []
    for label, cfg in AGE_QUOTAS.items():
        target_n = int(TOTAL_TARGET * cfg['pct'])
        have     = age_counts[label]
        need     = max(0, target_n - have)
        pct      = 100 * have // target_n if target_n else 0
        print(f'  Age {label:<17} {target_n:>8} {have:>6} {need:>6} {pct:>9}%')
        summary_rows.append({'quota_type':'age','segment':label,'target':target_n,'have':have,'need':need,'pct_done':pct})

    print()
    for label, cfg in GEO_QUOTAS.items():
        target_n = int(TOTAL_TARGET * cfg['pct'])
        have     = geo_counts[label]
        need     = max(0, target_n - have)
        pct      = 100 * have // target_n if target_n else 0
        print(f'  Geo {label:<18} {target_n:>8} {have:>6} {need:>6} {pct:>9}%')
        summary_rows.append({'quota_type':'geo','segment':label,'target':target_n,'have':have,'need':need,'pct_done':pct})

    if age_counts.get('unknown') or geo_counts.get('unknown'):
        print(f'\n  WARNING: {age_counts["unknown"]} unknown age / {geo_counts["unknown"]} unknown geo — check demographics')

    # ── WRITE FILES ──────────────────────────────────────────────────────────
    stem     = input_path.stem
    out_dir  = input_path.parent

    summary_path = out_dir / f'{stem}_quota_summary.csv'
    ids_path     = out_dir / f'{stem}_valid_ids.csv'

    with open(summary_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=['quota_type','segment','target','have','need','pct_done'])
        w.writeheader(); w.writerows(summary_rows)

    with open(ids_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=['respondent_id','survey_id','age','postal_code','age_group','geo_group','verdict'])
        w.writeheader(); w.writerows(valid_rows)

    print(f'\nFiles saved:')
    print(f'  {summary_path}')
    print(f'  {ids_path}')


if __name__ == '__main__':
    main()
