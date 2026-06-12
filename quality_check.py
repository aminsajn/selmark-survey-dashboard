"""
Selmark Surveys -- Quality Control Script
==========================================
Usage:
    python quality_check.py responses.json
    python quality_check.py responses.json --output report.csv
    python quality_check.py responses.json --only-flagged

Reads a JSON export from Supabase (array of survey_responses rows).
Outputs a CSV report with verdict: ELIMINATE / REVIEW / OK and detailed reasons.
"""

import json
import sys
import csv
import re
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import Counter


# ── CONFIG ────────────────────────────────────────────────────────────────────

MIN_MINUTES_ELIMINATE = 8
MAX_MINUTES_REVIEW    = 30   # flag for manual review if > 30 min

# Lifestyle: 4 blocks x 3 items. Flag only if >= this many blocks are all-equal.
# (3 items is too few to reliably flag a single block)
SL_LIFESTYLE_BLOCKS_MIN = 3

# Attributes: flag if >= 85% of items in a block share the same value
SL_ATTR_THRESHOLD = 0.85

OPEN_MIN_CHARS = 3

# Spanish postal codes
CP_PATTERN = re.compile(r'^\d{5}$')
CP_MIN, CP_MAX = 1000, 52999   # as int

# Scale block definitions per survey
# Items are stored as FLAT keys in answers (not nested objects)
SCALE_BLOCKS = {
    'lingerie-swim': {
        'lifestyle': {
            'lifestyle_a': ['q6',  'q7',  'q8'],
            'lifestyle_b': ['q9',  'q10', 'q11'],
            'lifestyle_c': ['q12', 'q13', 'q14'],
            'lifestyle_d': ['q15', 'q16', 'q17'],
        },
        'attributes': {
            'atrib_func_lenc': ['q54_1','q54_2','q54_3','q54_4','q54_5','q54_6'],
            'atrib_emoc_lenc': ['q55_1','q55_2','q55_3','q55_4','q55_5','q55_6','q55_7'],
        },
    },
    'sport-loungewear': {
        'lifestyle': {
            'lifestyle_a': ['q5',  'q6',  'q7'],
            'lifestyle_b': ['q8',  'q9',  'q10'],
            'lifestyle_c': ['q11', 'q12', 'q13'],
            'lifestyle_d': ['q14', 'q15', 'q16'],
        },
        'attributes': {
            'atrib_func_sport': [
                'q57_1','q57_2','q57_3','q57_4','q57_5','q57_6',
                'q57_7','q57_8','q57_9','q57_10','q57_11','q57_12',
            ],
            'atrib_emoc_sport': [
                'q58_1','q58_2','q58_3','q58_4','q58_5','q58_6','q58_7',
            ],
        },
    },
}

# Open questions to check for quality — paired questions about similar topics
# (q46/q47, q49/q50, q73/q74, q78/q79) are intentionally similar so we
# do NOT flag them as copy-paste; only cross-topic duplicates are flagged.
OPEN_QUESTIONS_S1 = {
    'q46': 'lenceria_canal', 'q47': 'bano_canal',
    'q53': 'marca_fav_lenc', 'q58': 'pilar_rubio',
    'q63': 'marca_fav_bano',
    'q70': 'producto_lenc_like', 'q71': 'producto_lenc_dislike',
    'q75': 'producto_bano_like', 'q76': 'producto_bano_dislike',
}
OPEN_QUESTIONS_S2 = {
    'q49': 'deporte_canal', 'q50': 'homewear_canal',
    'q56': 'marca_fav_deporte', 'q61': 'pilar_rubio',
    'q66': 'marca_fav_homewear',
    'q73': 'producto_sport_like', 'q74': 'producto_sport_dislike',
    'q78': 'producto_lounge_like', 'q79': 'producto_lounge_dislike',
}

# Pure "why" questions + channel-experience questions where "no se"/"nada" is never valid.
# Brand-favourite questions (q53/q63/q56/q66) are excluded: "ninguna" is valid there.
WHY_ONLY_QUESTIONS = {
    'lingerie-swim':    ['q70', 'q71', 'q75', 'q76', 'q46', 'q47'],
    'sport-loungewear': ['q73', 'q74', 'q78', 'q79', 'q49', 'q50'],
}
WHY_SHORT_CHARS = 8    # answers <= this length count as lazy
WHY_SHORT_MIN   = 3    # flag if >= this many "why" answers are bad

# Phrases that are semantically empty — valid only for brand-favourite questions
NON_ANSWER_PHRASES = {
    'no se', 'no sé', 'ns', 'n/s', 'nada', 'ninguna', 'ninguno', 'ningún',
    'no tengo', 'no lo se', 'no lo sé', 'no sé decir', 'ni idea', 'sin idea',
    'no idea', 'nothing', 'idk', 'no aplica', 'n/a', 'na', 'no',
    'nose', 'nse', 'sin respuesta', 'no tengo idea', 'no tengo favorita',
    'no tengo marca', 'no tengo ninguna', 'no conozco', 'no la conozco',
}

# Pairs that are naturally similar — skip copy-paste check for these
ALLOWED_SAME_PAIRS = {
    frozenset(['q46', 'q47']),   # lenceria vs bano canal
    frozenset(['q49', 'q50']),   # deporte vs homewear canal
    frozenset(['q70', 'q75']),   # por que gusta prod lenc vs bano
    frozenset(['q71', 'q76']),   # por que no gusta prod lenc vs bano
    frozenset(['q73', 'q78']),   # por que gusta prod sport vs lounge
    frozenset(['q74', 'q79']),   # por que no gusta prod sport vs lounge
}


# ── HELPERS ───────────────────────────────────────────────────────────────────

def parse_dt(s):
    if not s:
        return None
    # Handle timezone offset like +00:00 or -03:00
    s = re.sub(r'([+-]\d{2}):(\d{2})$', r'\1\2', s)  # +00:00 -> +0000
    s = s.rstrip('Z')
    for fmt in ('%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%dT%H:%M:%S.%f',   '%Y-%m-%dT%H:%M:%S'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None


def duration_minutes(row):
    # Prefer pre-computed field if present
    dur_seg = row.get('_duracion_seg')
    if dur_seg is not None:
        try:
            return float(dur_seg) / 60
        except (TypeError, ValueError):
            pass
    t0 = parse_dt(row.get('created_at'))
    t1 = parse_dt(row.get('completed_at'))
    if t0 and t1:
        # Strip tz if one has it and the other doesn't
        if t0.tzinfo and not t1.tzinfo:
            t1 = t1.replace(tzinfo=timezone.utc)
        if t1.tzinfo and not t0.tzinfo:
            t0 = t0.replace(tzinfo=timezone.utc)
        return (t1 - t0).total_seconds() / 60
    return None


def get_flat_scale_values(answers, item_ids):
    """Read scale values stored as flat keys in answers dict."""
    vals = []
    for iid in item_ids:
        v = answers.get(iid)
        if v is not None:
            try:
                vals.append(int(v))
            except (ValueError, TypeError):
                pass
    return vals


def is_straight_line(values, threshold=1.0):
    if len(values) < 2:
        return False
    most_common = Counter(values).most_common(1)[0][1]
    return most_common / len(values) >= threshold


def modal_value(values):
    if not values:
        return None
    return Counter(values).most_common(1)[0][0]


def is_seesaw(values, min_items=4):
    """True if values strictly alternate between two distinct extremes."""
    if len(values) < min_items:
        return False
    unique = set(values)
    if len(unique) != 2:
        return False
    a, b = sorted(unique)
    if b - a < 2:
        return False
    for i in range(1, len(values)):
        if values[i] == values[i - 1]:
            return False
    return True


def text_quality(text):
    if not text or not isinstance(text, str):
        return True, 'empty'
    clean = text.strip()
    if len(clean) < OPEN_MIN_CHARS:
        return True, 'too short (%d chars)' % len(clean)
    if re.fullmatch(r'[\d\s\W]+', clean):
        return True, 'only numbers/symbols'
    if len(set(clean.lower().replace(' ', ''))) <= 2:
        return True, 'single char repeated'
    alphachars = re.sub(r'[^a-z\xe1\xe9\xed\xf3\xfa\xfc\xf1a-zA-Z]', '', clean.lower())
    if len(alphachars) > 5 and not re.search(r'[aeiou\xe1\xe9\xed\xf3\xfa]', alphachars):
        return True, 'no vowels (possible mashing)'
    return False, ''


def check_open_quality(answers, open_qmap):
    """Check each important open question for poor-quality text."""
    issues = []
    for qid in open_qmap:
        val = answers.get(qid)
        if val is None:
            continue
        poor, reason = text_quality(str(val))
        if poor:
            issues.append((qid, reason))
    return issues


def check_copy_paste(answers, open_qmap):
    """Flag cross-topic identical answers (skip naturally similar pairs)."""
    texts = {}
    for qid in open_qmap:
        val = answers.get(qid)
        if val and isinstance(val, str) and len(val.strip()) > 8:
            texts[qid] = val.strip().lower()
    pairs = []
    qids = list(texts.keys())
    for i in range(len(qids)):
        for j in range(i + 1, len(qids)):
            qi, qj = qids[i], qids[j]
            if frozenset([qi, qj]) in ALLOWED_SAME_PAIRS:
                continue
            if texts[qi] == texts[qj]:
                pairs.append((qi, qj, texts[qi][:50]))
    return pairs


def check_age_cp(answers):
    issues = []
    raw_age = answers.get('q2')
    if raw_age is not None:
        try:
            age = int(raw_age)
            if age < 16 or age > 99:
                issues.append('age out of range (%s)' % age)
        except (ValueError, TypeError):
            issues.append('age not a number (%r)' % raw_age)
    raw_cp = answers.get('q1')
    if raw_cp is not None:
        cp = str(raw_cp).strip()
        if not CP_PATTERN.match(cp):
            issues.append('postal code not 5 digits (%r)' % cp)
        else:
            try:
                if not (CP_MIN <= int(cp) <= CP_MAX):
                    issues.append('postal code out of range (%s)' % cp)
            except ValueError:
                pass
    return issues


def is_non_answer(text):
    """True if text is a semantically empty phrase (no se, nada, ninguna, etc.)."""
    if not text or not isinstance(text, str):
        return False
    clean = text.strip().lower().rstrip('.,!? ')
    return clean in NON_ANSWER_PHRASES


def check_short_why(answers, survey_id):
    """Flag if >= WHY_SHORT_MIN 'why' answers are either too short OR a non-answer phrase."""
    bad = []
    for qid in WHY_ONLY_QUESTIONS.get(survey_id, []):
        val = answers.get(qid)
        if not val or not isinstance(val, str):
            continue
        clean = val.strip()
        if 0 < len(clean) <= WHY_SHORT_CHARS or is_non_answer(clean):
            bad.append('%s="%s"' % (qid, clean[:30]))
    return bad if len(bad) >= WHY_SHORT_MIN else []


def check_conditional_logic(answers, survey_id):
    issues = []
    if survey_id == 'lingerie-swim':
        q36 = answers.get('q36', '')
        if q36 == 'Nunca, siempre encuentro' and answers.get('q37'):
            issues.append('q37 present but q36=Nunca (impossible skip-logic path)')
        q42 = answers.get('q42', '')
        buys_online = isinstance(q42, str) and q42.startswith('S')
        for cq in ['q43', 'q44']:
            if buys_online and not answers.get(cq):
                issues.append('%s missing despite q42=%r' % (cq, q42))
    elif survey_id == 'sport-loungewear':
        q40 = answers.get('q40', '')
        if q40 == 'Nunca, siempre encuentro' and answers.get('q41'):
            issues.append('q41 present but q40=Nunca (impossible skip-logic path)')
        if answers.get('q29') == 'No' and not answers.get('q31'):
            issues.append('q31 missing despite q29=No')
        q46 = answers.get('q46', '')
        buys_online = isinstance(q46, str) and q46.startswith('S')
        for cq in ['q47', 'q48']:
            if buys_online and not answers.get(cq):
                issues.append('%s missing despite q46=%r' % (cq, q46))
    return issues


# ── MAIN QC FUNCTION ──────────────────────────────────────────────────────────

def assess_response(row):
    answers   = row.get('answers', {}) or {}
    survey_id = row.get('survey_id', '')
    rid       = row.get('respondent_id') or row.get('id', '')
    duration  = duration_minutes(row)

    flags = []  # (severity, rule, detail)

    # 1. DURATION
    if duration is not None:
        if duration < MIN_MINUTES_ELIMINATE:
            flags.append(('ELIMINATE', 'short_time',
                          '%.1fm < %dm' % (duration, MIN_MINUTES_ELIMINATE)))
        elif duration > MAX_MINUTES_REVIEW:
            # INFO only — long duration alone does not affect verdict.
            # Other rules (SL, text quality, etc.) already evaluate the answers themselves.
            flags.append(('INFO', 'very_long_time',
                          '%.1fm > %dm (check answers manually if other flags present)' % (duration, MAX_MINUTES_REVIEW)))
    else:
        flags.append(('INFO', 'no_duration', 'timestamps missing'))

    # 2. DEMOGRAPHICS
    for issue in check_age_cp(answers):
        flags.append(('ELIMINATE', 'invalid_demographics', issue))

    # 3. STRAIGHT-LINING
    blocks = SCALE_BLOCKS.get(survey_id, {})

    # Lifestyle (3 items/block): flag only when uniform blocks share the same value.
    # Rationale: [5,5,5] + [3,3,3] + [4,4,4] = different attitudes per theme → OK.
    #            [5,5,5] + [5,5,5] + [5,5,5] = no differentiation at all → suspicious.
    # Rule: flag if ALL 4 blocks are uniform (any values), OR if 3+ blocks are
    # uniform AND those 3+ share the same modal value.
    ls_sl = []
    for block_id, item_ids in blocks.get('lifestyle', {}).items():
        vals = get_flat_scale_values(answers, item_ids)
        if is_straight_line(vals, threshold=1.0):
            ls_sl.append((block_id, modal_value(vals)))
    if ls_sl:
        uniform_values = [v for _, v in ls_sl]
        same_value_count = Counter(uniform_values).most_common(1)[0][1] if uniform_values else 0
        flag_lifestyle = (
            len(ls_sl) == 4  # all 4 blocks uniform (any values)
            or (len(ls_sl) >= SL_LIFESTYLE_BLOCKS_MIN and same_value_count >= SL_LIFESTYLE_BLOCKS_MIN)
        )
        if flag_lifestyle:
            detail = ', '.join('%s=%s' % (b, v) for b, v in ls_sl)
            flags.append(('REVIEW', 'straight_line_lifestyle',
                          '%d/4 blocks all-equal: %s' % (len(ls_sl), detail)))

    # Attributes: flag only if BOTH functional AND emotional blocks are SL.
    # A single block all-equal can be genuine; two blocks together is a clear pattern.
    attr_sl_hits = []
    for block_id, item_ids in blocks.get('attributes', {}).items():
        vals = get_flat_scale_values(answers, item_ids)
        if vals and is_straight_line(vals, threshold=SL_ATTR_THRESHOLD):
            mv   = modal_value(vals)
            same = sum(1 for v in vals if v == mv)
            attr_sl_hits.append('%s: %d/%d = %s' % (block_id, same, len(vals), mv))
    if len(attr_sl_hits) >= 2:
        flags.append(('REVIEW', 'straight_line_attributes',
                      '; '.join(attr_sl_hits)))

    # 4. SEESAW (alternating extremes within a block)
    all_blocks = {}
    all_blocks.update(blocks.get('lifestyle', {}))
    all_blocks.update(blocks.get('attributes', {}))
    for block_id, item_ids in all_blocks.items():
        vals = get_flat_scale_values(answers, item_ids)
        if is_seesaw(vals):
            flags.append(('REVIEW', 'seesaw_pattern',
                          '%s: %s' % (block_id, vals)))

    # 5. OPEN TEXT QUALITY
    open_qmap = OPEN_QUESTIONS_S1 if survey_id == 'lingerie-swim' else OPEN_QUESTIONS_S2
    for qid, reason in check_open_quality(answers, open_qmap):
        sev = 'ELIMINATE' if reason == 'empty' else 'REVIEW'
        flags.append((sev, 'poor_open_text', '%s: %s' % (qid, reason)))
    for qa, qb, snippet in check_copy_paste(answers, open_qmap):
        flags.append(('REVIEW', 'copy_paste',
                      '%s==%s ("%s...")' % (qa, qb, snippet[:40])))

    # 6. SHORT WHY ANSWERS
    short_why = check_short_why(answers, survey_id)
    if short_why:
        flags.append(('REVIEW', 'short_why_answers',
                      '%d/4 why-answers <= %d chars: %s' % (
                          len(short_why), WHY_SHORT_CHARS, ', '.join(short_why))))

    # 7. CONDITIONAL LOGIC
    for issue in check_conditional_logic(answers, survey_id):
        flags.append(('REVIEW', 'conditional_logic', issue))

    # VERDICT — INFO flags are informational only and never affect verdict.
    # ELIMINATE if: any ELIMINATE flag, OR 3+ REVIEW flags
    severities   = [f[0] for f in flags]
    review_count = severities.count('REVIEW')
    if 'ELIMINATE' in severities:
        verdict = 'ELIMINATE'
    elif review_count >= 3:
        verdict = 'ELIMINATE'
    elif review_count > 0:
        verdict = 'REVIEW'
    else:
        verdict = 'OK'

    return {
        'respondent_id': rid,
        'survey_id':     survey_id,
        'duration_min':  ('%.1f' % duration) if duration is not None else 'N/A',
        'verdict':       verdict,
        'n_flags':       len(flags),
        'flag_summary':  '; '.join('%s: %s' % (r, d) for _, r, d in flags) if flags else 'OK',
        'flags_detail':  ' | '.join('%s:%s:%s' % f for f in flags) if flags else '',
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Selmark survey quality check')
    parser.add_argument('input', help='JSON export from Supabase')
    parser.add_argument('--output', default=None, help='Output CSV path')
    parser.add_argument('--only-flagged', action='store_true',
                        help='Only include ELIMINATE/REVIEW in CSV')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print('ERROR: file not found: %s' % input_path)
        sys.exit(1)

    with open(input_path, encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        print('ERROR: expected a JSON array')
        sys.exit(1)

    completed = [r for r in data if r.get('status') == 'complete']
    print('Loaded %d rows -- %d completed' % (len(data), len(completed)))

    results = [assess_response(r) for r in completed]
    total   = len(results)
    verdicts = [r['verdict'] for r in results]
    n_ok     = verdicts.count('OK')
    n_review = verdicts.count('REVIEW')
    n_elim   = verdicts.count('ELIMINATE')

    print('\nResults:')
    print('  OK:        %3d  (%d%%)' % (n_ok,    100 * n_ok    // total))
    print('  REVIEW:    %3d  (%d%%)' % (n_review, 100 * n_review // total))
    print('  ELIMINATE: %3d  (%d%%)' % (n_elim,   100 * n_elim   // total))

    if n_elim:
        print('\n--- ELIMINATE ---')
        for r in results:
            if r['verdict'] == 'ELIMINATE':
                print('  %-38s  %6sm  %s' % (
                    r['respondent_id'][:36], r['duration_min'],
                    r['flag_summary'][:100]))

    if n_review:
        print('\n--- REVIEW ---')
        for r in results:
            if r['verdict'] == 'REVIEW':
                print('  %-38s  %6sm  %s' % (
                    r['respondent_id'][:36], r['duration_min'],
                    r['flag_summary'][:100]))

    out_rows = [r for r in results if r['verdict'] != 'OK'] if args.only_flagged else results
    out_path = args.output or str(
        input_path.with_name(input_path.stem + '_qc_report.csv'))
    fieldnames = ['respondent_id','survey_id','duration_min','verdict',
                  'n_flags','flag_summary','flags_detail']
    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)
    print('\nReport saved to: %s' % out_path)


if __name__ == '__main__':
    main()
