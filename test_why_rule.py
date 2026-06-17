"""Test: flag if 3+ 'why' questions have answers <= 8 chars."""
import json
import quality_check as qc

WHY_QUESTIONS = {
    'lingerie-swim':   ['q53', 'q63', 'q70', 'q71', 'q75', 'q76'],
    'sport-loungewear':['q56', 'q66', 'q73', 'q74', 'q78', 'q79'],
}
THRESHOLD = 8   # chars
MIN_SHORT = 3   # how many short answers to trigger flag

with open(r'C:\Users\ajulve\Downloads\selmark_respuestas_2026-06-12 (1).json', encoding='utf-8') as f:
    data = json.load(f)
completed = [r for r in data if r.get('status') == 'complete']

flagged = []
for row in completed:
    survey  = row.get('survey_id', '')
    answers = row.get('answers', {}) or {}
    rid     = row['respondent_id']
    short = []
    for qid in WHY_QUESTIONS.get(survey, []):
        val = answers.get(qid)
        if val and isinstance(val, str) and 0 < len(val.strip()) <= THRESHOLD:
            short.append((qid, val.strip()))
    if len(short) >= MIN_SHORT:
        flagged.append((rid, row.get('survey_id',''), short))

print(f'Respondents with 3+ why-answers <= {THRESHOLD} chars: {len(flagged)} ({100*len(flagged)//len(completed)}%)')
print()

# Simulate impact on verdicts by patching the rule into assess_response
import importlib, copy

# Quick simulation: add 1 REVIEW flag to those respondents and recalc
results_base = {r['respondent_id']: r for r in [qc.assess_response(row) for row in completed]}
flagged_ids  = {rid for rid, _, _ in flagged}

new_verdicts = {'OK': 0, 'REVIEW': 0, 'ELIMINATE': 0}
newly_eliminated = []
for row in completed:
    rid = row['respondent_id']
    res = results_base[rid]
    if rid not in flagged_ids:
        new_verdicts[res['verdict']] += 1
        continue
    # Add 1 REVIEW flag and recalculate verdict
    flags_detail = res['flags_detail']
    n_review = flags_detail.count('REVIEW:') + 1   # +1 new
    n_elim   = flags_detail.count('ELIMINATE:')
    if n_elim > 0 or n_review >= 4:
        new_verdict = 'ELIMINATE'
    elif n_review > 0:
        new_verdict = 'REVIEW'
    else:
        new_verdict = 'OK'
    new_verdicts[new_verdict] += 1
    if new_verdict == 'ELIMINATE' and res['verdict'] != 'ELIMINATE':
        newly_eliminated.append((rid, qc.duration_minutes(row), res['flag_summary']))

total = len(completed)
print(f'=== Verdicts with new rule ===')
print(f'OK:        {new_verdicts["OK"]:3d}  ({100*new_verdicts["OK"]//total}%)')
print(f'REVIEW:    {new_verdicts["REVIEW"]:3d}  ({100*new_verdicts["REVIEW"]//total}%)')
print(f'ELIMINATE: {new_verdicts["ELIMINATE"]:3d}  ({100*new_verdicts["ELIMINATE"]//total}%)')
print(f'\nNewly pushed to ELIMINATE by this rule alone: {len(newly_eliminated)}')
for rid, dur, flags in newly_eliminated:
    print(f'  {rid[:36]}  {dur:.1f}m  {flags[:100]}')

print(f'\n--- All flagged respondents (3+ short why-answers) ---')
for rid, survey, short in flagged:
    res = results_base[rid]
    print(f'  {rid[:36]}  {res["verdict"]:8s}  short: {short}')
