"""Count respondents with non-answer phrases in open text questions."""
import json, re
import quality_check as qc

# Phrases that are semantically empty regardless of question
NON_ANSWER_PHRASES = {
    'no se', 'no sé', 'ns', 'n/s', 'nada', 'ninguna', 'ninguno', 'ningún',
    'no tengo', 'no lo se', 'no lo sé', 'no sé decir', 'ni idea', 'sin idea',
    'no idea', 'nothing', 'idk', 'no aplica', 'n/a', 'na', 'no', 'no sé quien',
    'no la conozco', 'no conozco', 'nose', 'nse', 'no tengo idea', 'sin respuesta',
    'no tengo favorita', 'no tengo marca', 'no tengo ninguna',
}

def is_non_answer(text):
    if not text or not isinstance(text, str):
        return False
    clean = text.strip().lower().rstrip('.,!?')
    return clean in NON_ANSWER_PHRASES

ALL_OPEN_S1 = ['q46','q47','q53','q58','q63','q70','q71','q75','q76']
ALL_OPEN_S2 = ['q49','q50','q56','q61','q66','q73','q74','q78','q79']

with open(r'C:\Users\ajulve\Downloads\selmark_respuestas_2026-06-12 (1).json', encoding='utf-8') as f:
    data = json.load(f)
completed = [r for r in data if r.get('status') == 'complete']

print('=== Respondents with non-answer phrases (exact match) ===\n')
affected = []
for row in completed:
    survey  = row.get('survey_id', '')
    answers = row.get('answers', {}) or {}
    rid     = row['respondent_id']
    open_qs = ALL_OPEN_S1 if survey == 'lingerie-swim' else ALL_OPEN_S2
    hits = []
    for qid in open_qs:
        val = answers.get(qid)
        if is_non_answer(str(val) if val else ''):
            hits.append((qid, str(val).strip()))
    if hits:
        res = qc.assess_response(row)
        affected.append((rid, res['verdict'], hits))

print(f'Respondents with at least 1 non-answer: {len(affected)} ({100*len(affected)//len(completed)}%)')

# Group by number of non-answers
from collections import Counter
dist = Counter(len(h) for _, _, h in affected)
print('Distribution:')
for k in sorted(dist):
    print(f'  {k} non-answer(s): {dist[k]} respondents')

print()
print('--- 3+ non-answers (strong signal) ---')
for rid, verdict, hits in affected:
    if len(hits) >= 3:
        print(f'  {rid[:36]}  {verdict:8s}  {hits}')
