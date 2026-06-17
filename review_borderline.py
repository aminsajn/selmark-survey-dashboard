"""Print full answers for respondents in the 8-10 min range for manual inspection."""
import json
import quality_check as qc

with open(r'C:\Users\ajulve\Downloads\selmark_respuestas_2026-06-12 (1).json', encoding='utf-8') as f:
    data = json.load(f)

completed = [r for r in data if r.get('status') == 'complete']

# Count with 9-min threshold
qc.MIN_MINUTES_ELIMINATE = 9
results9 = [qc.assess_response(r) for r in completed]
v9 = [r['verdict'] for r in results9]
print(f'=== Threshold 9 min ===')
print(f'OK: {v9.count("OK")}  REVIEW: {v9.count("REVIEW")}  ELIMINATE: {v9.count("ELIMINATE")}')
print()

# Respondents 8-10 min (newly affected range)
borderline = [(r, qc.duration_minutes(r)) for r in completed
              if qc.duration_minutes(r) is not None and 8 <= qc.duration_minutes(r) < 10]
borderline.sort(key=lambda x: x[1])

print(f'Respondents 8-10 min: {len(borderline)}\n')
print('=' * 100)

OPEN_S1 = ['q46','q47','q53','q58','q63','q70','q71','q75','q76']
OPEN_S2 = ['q49','q50','q56','q61','q66','q73','q74','q78','q79']

for row, dur in borderline:
    rid     = row['respondent_id']
    survey  = row.get('survey_id','')
    answers = row.get('answers', {}) or {}
    res     = qc.assess_response(row)

    print(f'\n--- {rid}  ({dur:.1f} min)  survey={survey}  verdict@9min={res["verdict"]} ---')
    if res['flag_summary'] != 'OK':
        print(f'    Flags: {res["flag_summary"]}')

    # Demographics
    age = answers.get('q2','?')
    cp  = answers.get('q1','?')
    print(f'    Age={age}  CP={cp}')

    # Open text answers
    open_qs = OPEN_S1 if survey == 'lingerie-swim' else OPEN_S2
    for qid in open_qs:
        val = answers.get(qid)
        if val:
            print(f'    [{qid}] {str(val)[:120]}')

    # Lifestyle scale summary (show values per block)
    blocks = qc.SCALE_BLOCKS.get(survey, {})
    ls_summary = []
    for bname, items in blocks.get('lifestyle', {}).items():
        vals = qc.get_flat_scale_values(answers, items)
        ls_summary.append(f'{bname}={vals}')
    if ls_summary:
        print(f'    Lifestyle: {" | ".join(ls_summary)}')

    # Attribute scale summary
    for bname, items in blocks.get('attributes', {}).items():
        vals = qc.get_flat_scale_values(answers, items)
        print(f'    {bname}: {vals}')
