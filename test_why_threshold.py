"""Test different min-char thresholds for 'why' open questions."""
import json
import quality_check as qc

# 'Why' questions specifically — these require a real reason, not just a word
WHY_QUESTIONS = {
    'lingerie-swim':   ['q53', 'q63', 'q70', 'q71', 'q75', 'q76'],
    'sport-loungewear':['q56', 'q66', 'q73', 'q74', 'q78', 'q79'],
}

with open(r'C:\Users\ajulve\Downloads\selmark_respuestas_2026-06-12 (1).json', encoding='utf-8') as f:
    data = json.load(f)
completed = [r for r in data if r.get('status') == 'complete']

def count_short_why(min_chars):
    affected_respondents = set()
    examples = []
    for row in completed:
        survey  = row.get('survey_id', '')
        answers = row.get('answers', {}) or {}
        rid     = row['respondent_id']
        for qid in WHY_QUESTIONS.get(survey, []):
            val = answers.get(qid)
            if val and isinstance(val, str):
                clean = val.strip()
                if 0 < len(clean) < min_chars:
                    affected_respondents.add(rid)
                    if len(examples) < 40:
                        examples.append((rid[:20], qid, clean))
    return len(affected_respondents), examples

print(f'{"Threshold":>10}  {"Respondents affected":>22}  {"% of 167":>10}')
print('-' * 50)
for t in [10, 15, 20, 25, 30]:
    n, _ = count_short_why(t)
    print(f'{t:>10}  {n:>22}  {100*n//167:>9}%')

print()
print('=== Examples at threshold=20 (answers between 3-19 chars) ===')
_, examples = count_short_why(20)
for rid, qid, val in examples:
    print(f'  {rid}  {qid}: "{val}"')
