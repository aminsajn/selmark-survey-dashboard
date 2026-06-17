"""Compare verdicts: old rule (1 attr block) vs new rule (2 attr blocks required)."""
import json
import quality_check as qc
from collections import Counter

with open(r'C:\Users\ajulve\Downloads\selmark_respuestas_2026-06-12 (1).json', encoding='utf-8') as f:
    data = json.load(f)
completed = [r for r in data if r.get('status') == 'complete']

# Current (new) results
new_results = {r['respondent_id']: r for r in [qc.assess_response(row) for row in completed]}

# Simulate OLD rule: flag each attribute block independently
def assess_old(row):
    import quality_check as qc2
    answers   = row.get('answers', {}) or {}
    survey_id = row.get('survey_id', '')
    rid       = row.get('respondent_id') or row.get('id', '')
    duration  = qc2.duration_minutes(row)
    flags = []

    if duration is not None:
        if duration < qc2.MIN_MINUTES_ELIMINATE:
            flags.append(('ELIMINATE', 'short_time', '%.1fm' % duration))
        elif duration > qc2.MAX_MINUTES_REVIEW:
            flags.append(('INFO', 'very_long_time', '%.1fm' % duration))

    for issue in qc2.check_age_cp(answers):
        flags.append(('ELIMINATE', 'invalid_demographics', issue))

    blocks = qc2.SCALE_BLOCKS.get(survey_id, {})
    ls_sl = []
    for block_id, item_ids in blocks.get('lifestyle', {}).items():
        vals = qc2.get_flat_scale_values(answers, item_ids)
        if qc2.is_straight_line(vals, threshold=1.0):
            ls_sl.append((block_id, qc2.modal_value(vals)))
    if ls_sl:
        uniform_values = [v for _, v in ls_sl]
        same_value_count = Counter(uniform_values).most_common(1)[0][1]
        if len(ls_sl) == 4 or (len(ls_sl) >= qc2.SL_LIFESTYLE_BLOCKS_MIN and same_value_count >= qc2.SL_LIFESTYLE_BLOCKS_MIN):
            flags.append(('REVIEW', 'straight_line_lifestyle', '%d/4 blocks' % len(ls_sl)))

    # OLD: flag each attribute block independently
    for block_id, item_ids in blocks.get('attributes', {}).items():
        vals = qc2.get_flat_scale_values(answers, item_ids)
        if vals and qc2.is_straight_line(vals, threshold=qc2.SL_ATTR_THRESHOLD):
            mv   = qc2.modal_value(vals)
            same = sum(1 for v in vals if v == mv)
            flags.append(('REVIEW', 'straight_line_attributes', '%s: %d/%d=%s' % (block_id, same, len(vals), mv)))

    all_blocks = {}
    all_blocks.update(blocks.get('lifestyle', {}))
    all_blocks.update(blocks.get('attributes', {}))
    for block_id, item_ids in all_blocks.items():
        vals = qc2.get_flat_scale_values(answers, item_ids)
        if qc2.is_seesaw(vals):
            flags.append(('REVIEW', 'seesaw_pattern', block_id))

    open_qmap = qc2.OPEN_QUESTIONS_S1 if survey_id == 'lingerie-swim' else qc2.OPEN_QUESTIONS_S2
    for qid, reason in qc2.check_open_quality(answers, open_qmap):
        sev = 'ELIMINATE' if reason == 'empty' else 'REVIEW'
        flags.append((sev, 'poor_open_text', '%s: %s' % (qid, reason)))
    for qa, qb, snippet in qc2.check_copy_paste(answers, open_qmap):
        flags.append(('REVIEW', 'copy_paste', '%s==%s' % (qa, qb)))

    short_why = qc2.check_short_why(answers, survey_id)
    if short_why:
        flags.append(('REVIEW', 'short_why_answers', '%d bad' % len(short_why)))

    for issue in qc2.check_conditional_logic(answers, survey_id):
        flags.append(('REVIEW', 'conditional_logic', issue))

    severities   = [f[0] for f in flags]
    review_count = severities.count('REVIEW')
    if 'ELIMINATE' in severities:
        verdict = 'ELIMINATE'
    elif review_count >= 4:
        verdict = 'ELIMINATE'
    elif review_count > 0:
        verdict = 'REVIEW'
    else:
        verdict = 'OK'

    return verdict, flags

old_results = {row['respondent_id']: assess_old(row) for row in completed}

# Find respondents that changed verdict
print('=== Respondents that moved OUT of ELIMINATE with new rule ===\n')
moved_out = []
for rid, (old_v, old_flags) in old_results.items():
    new_v = new_results[rid]['verdict']
    if old_v == 'ELIMINATE' and new_v != 'ELIMINATE':
        moved_out.append((rid, new_v, old_flags, new_results[rid]['flag_summary']))

print(f'Total moved out of ELIMINATE: {len(moved_out)}\n')
for rid, new_v, old_flags, new_summary in moved_out:
    old_flag_str = '; '.join('%s:%s' % (r,d) for _,r,d in old_flags)
    print(f'  {rid[:36]}')
    print(f'    Old verdict: ELIMINATE  ->  New verdict: {new_v}')
    print(f'    Old flags: {old_flag_str[:120]}')
    print(f'    New flags: {new_summary[:120]}')
    print()
