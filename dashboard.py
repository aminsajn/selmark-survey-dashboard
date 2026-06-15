"""
Selmark Survey — Quota Dashboard
Run locally:   streamlit run dashboard.py
Production:    deploy to Streamlit Community Cloud, add Supabase secrets
"""

import streamlit as st
import json, os
from pathlib import Path
from datetime import datetime
import quality_check as qc
from collections import defaultdict

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title='Selmark Survey — Quota Progress',
    page_icon='📊',
    layout='wide',
)

# ── PASSWORD GATE ─────────────────────────────────────────────────────────────
PASSWORD = st.secrets.get("DASHBOARD_PASSWORD", "")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title('📊 Selmark Survey — Quota Progress')
    pwd = st.text_input('Password', type='password')
    if st.button('Enter'):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error('Incorrect password.')
    st.stop()

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
TOTAL_TARGET = 1200
AGE_QUOTAS = {
    '18–30': {'pct': 0.20, 'min': 18, 'max': 30, 'target': int(1200 * 0.20)},
    '31–45': {'pct': 0.50, 'min': 31, 'max': 45, 'target': int(1200 * 0.50)},
    '46+':   {'pct': 0.30, 'min': 46, 'max': 99, 'target': int(1200 * 0.30)},
}
GEO_QUOTAS = {
    'Madrid / Barcelona': {'pct': 0.50, 'target': 600, 'prefixes': {'28', '08'}},
    'Rest of Spain':      {'pct': 0.50, 'target': 600, 'prefixes': None},
}
REFRESH_SECONDS = 60

# ── DATA LOADING ──────────────────────────────────────────────────────────────
def load_from_supabase():
    """Load responses from Supabase (production)."""
    from supabase import create_client
    url = st.secrets['SUPABASE_URL']
    key = st.secrets['SUPABASE_KEY']
    client = create_client(url, key)
    resp = client.table('survey_responses').select('*').eq('status', 'complete').execute()
    return resp.data

def load_from_file():
    """Load responses from local JSON (development/testing)."""
    candidates = sorted(
        Path(r'C:\Users\ajulve\Downloads').glob('selmark_respuestas*.json'),
        key=lambda p: p.stat().st_mtime, reverse=True
    )
    if not candidates:
        return []
    with open(candidates[0], encoding='utf-8') as f:
        data = json.load(f)
    return [r for r in data if r.get('status') == 'complete']

@st.cache_data(ttl=REFRESH_SECONDS)
def get_data():
    try:
        rows = load_from_supabase()
        source = 'Supabase (live)'
    except Exception:
        rows = load_from_file()
        source = 'Local file (development)'
    return rows, source

# ── QC + QUOTA LOGIC ─────────────────────────────────────────────────────────
def age_group(val):
    try:
        age = int(val)
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
    return 'Madrid / Barcelona' if cp[:2] in {'28', '08'} else 'Rest of Spain'

def compute_quotas(rows):
    results = [qc.assess_response(r) for r in rows]
    valid   = [r for r, res in zip(rows, results) if res['verdict'] in ('OK', 'REVIEW')]

    age_counts = defaultdict(int)
    geo_counts = defaultdict(int)

    for r in valid:
        answers = r.get('answers', {}) or {}
        ag = age_group(answers.get('q2'))
        gg = geo_group(answers.get('q1'))
        if ag: age_counts[ag] += 1
        if gg: geo_counts[gg] += 1

    return len(valid), len(rows), age_counts, geo_counts, results

# ── HELPERS ───────────────────────────────────────────────────────────────────
def progress_color(pct):
    if pct >= 100: return '🟢'
    if pct >= 60:  return '🟡'
    return '🔴'

def render_quota_row(label, have, target):
    pct  = min(100, int(100 * have / target)) if target else 0
    icon = progress_color(pct)
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    col1.write(f'{icon} **{label}**')
    col2.metric('Have', have)
    col3.metric('Target', target)
    col4.metric('Still needed', max(0, target - have))
    st.progress(pct / 100)

# ── LAYOUT ────────────────────────────────────────────────────────────────────
st.title('📊 Selmark Survey — Quota Progress')

rows, source = get_data()

if not rows:
    st.error('No data found.')
    st.stop()

n_valid, n_total, age_counts, geo_counts, results = compute_quotas(rows)
n_review  = sum(1 for r in results if r['verdict'] == 'REVIEW')
n_elim    = sum(1 for r in results if r['verdict'] == 'ELIMINATE')
last_update = datetime.now().strftime('%d %b %Y  %H:%M')

st.caption(f'Source: {source}  |  Last updated: {last_update}  |  Auto-refresh every {REFRESH_SECONDS}s')

# ── TOP METRICS ───────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric('Total responses', n_total)
c2.metric('✅ Valid (OK)', n_valid)
c3.metric('🎯 Still needed', max(0, TOTAL_TARGET - n_valid))

overall_pct = min(100, int(100 * n_valid / TOTAL_TARGET))
st.write(f'**Overall progress: {n_valid} / {TOTAL_TARGET} valid completes ({overall_pct}%)**')
st.progress(overall_pct / 100)

st.divider()

# ── QUOTA BREAKDOWN ───────────────────────────────────────────────────────────
col_age, col_geo = st.columns(2)

with col_age:
    st.subheader('Age quotas')
    for label, cfg in AGE_QUOTAS.items():
        render_quota_row(label, age_counts[label], cfg['target'])

with col_geo:
    st.subheader('Geographic quotas')
    for label, cfg in GEO_QUOTAS.items():
        render_quota_row(label, geo_counts[label], cfg['target'])

st.divider()

# ── SURVEY SPLIT ─────────────────────────────────────────────────────────────
st.subheader('By survey')
s1 = sum(1 for r, res in zip(rows, results)
         if res['verdict'] in ('OK', 'REVIEW') and r.get('survey_id') == 'lingerie-swim')
s2 = sum(1 for r, res in zip(rows, results)
         if res['verdict'] in ('OK', 'REVIEW') and r.get('survey_id') == 'sport-loungewear')

cs1, cs2 = st.columns(2)
cs1.metric('Lingerie & Swim (S1)', s1)
cs2.metric('Sport & Loungewear (S2)', s2)

# ── AUTO-REFRESH ─────────────────────────────────────────────────────────────
st.caption(f'Page refreshes automatically every {REFRESH_SECONDS} seconds.')
st.markdown(
    f'<meta http-equiv="refresh" content="{REFRESH_SECONDS}">',
    unsafe_allow_html=True,
)
