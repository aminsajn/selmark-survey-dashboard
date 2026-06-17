import json, sys, importlib
import quality_check as qc

# Patch threshold to 10 min
qc.MIN_MINUTES_ELIMINATE = 10

with open(r'C:\Users\ajulve\Downloads\selmark_respuestas_2026-06-12 (1).json', encoding='utf-8') as f:
    data = json.load(f)

completed = [r for r in data if r.get('status') == 'complete']
results   = [qc.assess_response(r) for r in completed]
verdicts  = [r['verdict'] for r in results]
total     = len(results)

n_ok   = verdicts.count('OK')
n_rev  = verdicts.count('REVIEW')
n_elim = verdicts.count('ELIMINATE')
print(f'--- Threshold 10 min ---')
print(f'OK:        {n_ok:3d}  ({100*n_ok//total}%)')
print(f'REVIEW:    {n_rev:3d}  ({100*n_rev//total}%)')
print(f'ELIMINATE: {n_elim:3d}  ({100*n_elim//total}%)')
print()

# Show respondents 8-10 min specifically (affected by the change)
print('Respondents in the 8-10 min range (newly ELIMINATE if threshold raised):')
for r in completed:
    d = qc.duration_minutes(r)
    if d is not None and 8 <= d < 10:
        res = qc.assess_response(r)
        print(f'  {r["respondent_id"][:36]}  {d:.1f}m  {res["verdict"]}  {res["flag_summary"][:90]}')
