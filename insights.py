"""
Selmark Consumer Insights — Dashboard local
streamlit run insights.py --server.port 8503
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collections import Counter
import traceback, os, re, base64, hmac
import unicodedata
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(
    page_title='Selmark · Consumer Insights',
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded',
)

# ── LOGIN ─────────────────────────────────────────────────────────────────────
def check_password():
    if st.session_state.get('authenticated'):
        return True
    st.markdown("""
    <style>
    .login-box { max-width:380px; margin:120px auto; padding:40px; background:#fff;
                 border-radius:10px; border:1px solid #D4E4F0; box-shadow:0 4px 24px rgba(0,0,0,.08) }
    .login-title { font-family:Montserrat,sans-serif; font-size:1.4rem; font-weight:700;
                   color:#1B2B3B; text-align:center; margin-bottom:6px }
    .login-sub { font-size:.75rem; letter-spacing:.12em; text-transform:uppercase;
                 color:#6A8BA4; text-align:center; margin-bottom:28px }
    </style>
    <div class="login-box">
      <div class="login-title">Consumer Insights</div>
      <div class="login-sub">Selmark · Minsait</div>
    </div>
    """, unsafe_allow_html=True)
    with st.form('login', clear_on_submit=True):
        pwd = st.text_input('Contraseña', type='password', placeholder='Introduce la contraseña')
        if st.form_submit_button('Entrar', use_container_width=True):
            if hmac.compare_digest(pwd, 'SelmarkMinsait2026'):
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error('Contraseña incorrecta')
    return False

if not check_password():
    st.stop()

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Montserrat:wght@300;400;600;700&display=swap');

#MainMenu, footer, header { visibility: hidden }
[data-testid="stToolbar"] { display: none }
.block-container { padding: 0 2rem 2rem !important; max-width: 1500px }

/* Fondo general clarito azulado */
.stApp { background: #F3F7FB; color: #1A2A3A }
html, body, [class*="css"] { font-family: 'Inter', sans-serif }

/* Sidebar navy */
[data-testid="stSidebar"] { background: #1B2B3B !important; border-right: none !important }
[data-testid="stSidebar"] * { color: #CBD8E6 !important }
[data-testid="stSidebar"] label { color: #7FAFD4 !important; font-size: .7rem !important; letter-spacing: .1em; text-transform: uppercase }
[data-testid="stSidebar"] [data-baseweb="select"] { background: #243444 !important; border: 1px solid #3A5068 !important; border-radius: 4px !important }
[data-testid="stSidebar"] [data-baseweb="select"] * { background: #243444 !important; color: #CBD8E6 !important }
[data-testid="stSidebar"] hr { border-color: #2E4460 !important }
[data-testid="stSidebar"] .stRadio label { color: #CBD8E6 !important; font-size: .82rem !important }
[data-testid="stSidebar"] [data-baseweb="radio"] { gap: 6px }

/* Header top bar */
.top-bar {
    background: transparent;
    padding: 14px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0 -2rem 1.5rem -2rem;
    border-bottom: 1px solid #D4E4F0;
}
.top-bar img { height: 48px; width: auto; display: block; object-fit: contain; }
.top-center {
    font-family: 'Montserrat', sans-serif;
    font-size: .72rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: #1B2B3B;
    font-weight: 600;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid #D4E4F0;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-size: .72rem;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #6A8BA4;
    padding: 11px 22px;
    border: none;
    border-bottom: 3px solid transparent;
    background: transparent !important;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    color: #1B2B3B !important;
    border-bottom: 3px solid #2E86AB !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem }

/* Sección */
.section-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #1B2B3B;
    letter-spacing: .02em;
    margin-bottom: 4px;
}
.section-rule { width: 36px; height: 3px; background: #2E86AB; border-radius: 2px; margin: 6px 0 18px 0 }

/* Metric cards */
.kpi-row { display: flex; gap: 14px; margin-bottom: 1.8rem; flex-wrap: wrap }
.kpi-card {
    background: #fff;
    border: 1px solid #D4E4F0;
    border-top: 3px solid #2E86AB;
    border-radius: 6px;
    padding: 18px 22px;
    flex: 1;
    min-width: 140px;
}
.kpi-label { font-size: .64rem; letter-spacing: .12em; text-transform: uppercase; color: #6A8BA4; margin-bottom: 7px }
.kpi-value { font-family: 'Montserrat', sans-serif; font-size: 1.9rem; font-weight: 600; color: #1B2B3B; line-height: 1 }
.kpi-sub { font-size: .68rem; color: #2E86AB; margin-top: 5px }

/* Chart cards */
.chart-card { background: #fff; border: 1px solid #D4E4F0; border-radius: 6px; padding: 18px; margin-bottom: 16px }
.chart-label { font-size: .64rem; letter-spacing: .1em; text-transform: uppercase; color: #6A8BA4; margin-bottom: 10px }
hr { border: none; border-top: 1px solid #D4E4F0; margin: 1.6rem 0 }

/* Expander */
[data-testid="stExpander"] { border: 1px solid #D4E4F0 !important; border-radius: 6px !important; background: #fff !important }

/* Cluster chips */
.cluster-chip {
    display: inline-block;
    background: #E8F1F8;
    color: #1B2B3B;
    border-radius: 3px;
    padding: 3px 10px;
    font-size: .72rem;
    margin: 3px 2px;
    border: 1px solid #C0D8EC;
}

/* Producto brand badge */
.badge-s  { background:#1B2B3B; color:#fff; padding:3px 10px; border-radius:3px; font-size:.62rem; letter-spacing:.1em; text-transform:uppercase; font-weight:600 }
.badge-a  { background:#2E86AB; color:#fff; padding:3px 10px; border-radius:3px; font-size:.62rem; letter-spacing:.1em; text-transform:uppercase; font-weight:600 }
.badge-b  { background:#D4E4F0; color:#1B2B3B; padding:3px 10px; border-radius:3px; font-size:.62rem; letter-spacing:.1em; text-transform:uppercase; font-weight:600 }

/* Imágenes de producto — tamaño uniforme */
.prod-img-container {
    width: 140px;
    height: 186px;
    overflow: hidden;
    border-radius: 6px 6px 0 0;
    border: 1px solid #D4E4F0;
    border-bottom: none;
    background: #F8FAFC;
    margin: 0 auto;
}
.prod-img-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center top;
    display: block;
}

/* Buyer persona cards */
.persona-card {
    border-radius: 8px;
    padding: 18px 20px;
    margin-bottom: 12px;
    border: 1px solid #D4E4F0;
}
.persona-title { font-family:'Montserrat',sans-serif; font-size:1rem; font-weight:700; margin-bottom:4px }
.persona-n { font-size:.7rem; opacity:.7; margin-bottom:10px }
.persona-tag { display:inline-block; background:rgba(255,255,255,.25); border-radius:3px; padding:2px 8px; font-size:.65rem; margin:2px 2px; border:1px solid rgba(255,255,255,.4) }
</style>
""", unsafe_allow_html=True)

# ── PALETA ───────────────────────────────────────────────────────────────────
P     = ['#2E86AB','#1B4F72','#5DADE2','#85C1E9','#1A5276','#2980B9','#7FB3D3','#154360']
# Colores distintos para radar (no todos azules)
RADAR_C = ['#E74C3C','#2E86AB','#27AE60','#F39C12','#8E44AD','#16A085','#D35400','#2C3E50']
# Colores por buyer persona
PERSONA_C = {
    'La Aspiracional':          '#8E44AD',
    'La Tradicional Fiel':      '#E74C3C',
    'La Hogareña Práctica':     '#F39C12',
    'La Exploradora Comprometida': '#27AE60',
}
PAPER = '#FFFFFF'
BG    = '#F3F7FB'
FONT  = '#1A2A3A'
GRID  = '#EAF2F8'
AGES  = ['18–30','31–45','46+']

# CCAA centroides para mapa
CCAA_COORDS = {
    'Comunidad de Madrid':  (40.42,-3.70), 'Cataluña':          (41.80, 1.70),
    'Andalucía':            (37.50,-4.50), 'C. Valenciana':     (39.50,-0.50),
    'Castilla y León':      (41.50,-4.20), 'Castilla-La Mancha':(39.50,-3.00),
    'Galicia':              (42.70,-7.80), 'País Vasco':        (43.00,-2.70),
    'Aragón':               (41.50,-0.90), 'Extremadura':       (39.00,-6.20),
    'Murcia':               (37.90,-1.50), 'Asturias':          (43.30,-6.00),
    'Navarra':              (42.70,-1.60), 'Canarias':          (28.30,-15.60),
    'Cantabria':            (43.20,-4.00), 'La Rioja':          (42.30,-2.50),
    'Baleares':             (39.50, 2.90), 'Ceuta':             (35.90,-5.30),
    'Melilla':              (35.30,-2.90),
}

IMG_BASE = os.path.dirname(os.path.abspath(__file__))

PROD_IMG = {
    'lt1_s':'img/products/lenc_p10_Image74.jpg','lt1_a':'img/products/lenc_p11_Image80.jpg','lt1_b':'img/products/lenc_p11_Image82.jpg',
    'lt2_s':'img/products/lenc_p10_Image75.jpg','lt2_a':'img/products/lenc_p11_Image79.jpg','lt2_b':'img/products/lenc_p11_Image83.jpg',
    'lt3_s':'img/products/lenc_p10_Image76.jpg','lt3_a':'img/products/lenc_p11_Image81.jpg','lt3_b':'img/products/lenc_p11_Image84.jpg',
    'st1_s':'img/products/lenc_p12_Image87.jpg','st1_a':'img/products/lenc_p12_Image90.jpg','st1_b':'img/products/lenc_p13_Image96.jpg',
    'st2_s':'img/products/lenc_p12_Image88.jpg','st2_a':'img/products/lenc_p12_Image91.jpg','st2_b':'img/products/lenc_p13_Image97.jpg',
    'st3_s':'img/products/lenc_p12_Image89.jpg','st3_a':'img/products/lenc_p12_Image92.jpg','st3_b':'img/products/lenc_p13_Image95.jpg',
    'spt1_s':'img/products/sport_p11_Image78.jpg','spt1_a':'img/products/sport_p11_Image81.jpg','spt1_b':'img/products/sport_p11_Image84.jpg',
    'spt2_s':'img/products/sport_p11_Image79.jpg','spt2_a':'img/products/sport_p11_Image82.jpg','spt2_b':'img/products/sport_p11_Image85.jpg',
    'spt3_s':'img/products/sport_p11_Image80.jpg','spt3_a':'img/products/sport_p11_Image83.jpg','spt3_b':'img/products/sport_p11_Image86.jpg',
    'lw1_s':'img/products/sport_p12_Image89.jpg','lw1_a':'img/products/sport_p13_Image94.jpg','lw1_b':'img/products/sport_p13_Image97.jpg',
    'lw2_s':'img/products/sport_p12_Image90.jpg','lw2_a':'img/products/sport_p13_Image95.jpg','lw2_b':'img/products/sport_p13_Image98.jpg',
    'lw3_s':'img/products/sport_p12_Image91.jpg','lw3_a':'img/products/sport_p13_Image96.jpg','lw3_b':'img/products/sport_p13_Image99.jpg',
}

# Palabras sin significado en respuestas abiertas (ES)
NO_MEANING = {
    'no sé','no se','ns','ns/nc','n/s','n/c','no','nada','ninguna','ninguno',
    'sin respuesta','no contesta','nc','na','no sabe','no lo sé','no lo se',
    'no contestar','nada en especial','no aplica','n/a','—','--','-','.',',',
    'depende','no tengo','no recuerdo','no me acuerdo','no lo recuerdo',
    'pues no sé','pues nada','no lo sabe','algo','no nada','no mucho',
    'pues no','ya','ok','bien','si','sí','no especifica',
}
STOPWORDS_ES = {
    # artículos / preposiciones / conjunciones
    'de','la','el','en','y','a','que','los','las','un','una','con','por','para','se',
    'del','al','es','no','mas','su','sus','lo','le','como','pero','si','me','te',
    'mi','tu','nos','son','ha','han','hay','era','ser','estar','esto','esta','estos',
    'estas','ese','esa','esos','esas','muy','tambien','solo','porque','cuando',
    'todo','toda','todos','todas','bien','tener','tiene','tengo','hace','hacer',
    'cada','entre','desde','hasta','sobre','bajo','dado','ve','vi','va','van',
    'fue','han','haber','he','les','os','ya','asi','donde','quien','cual','cuales',
    'tanto','tan','tal','luego','aunque','mas','pues','algo','creo',
    # verbos sin contenido semántico en contexto de producto
    'es','parece','parecen','me','el','la','lo','le','les',
    # formas de "gustar" que solos no aportan
    'gusta','gustan','gusto','gustado','gustaba','gustar',
    # formas de "parecer"
    'parece','parecen','parecio','parecia',
    # otras muy frecuentes sin valor
    'forma','tiene','tienen','creo','pienso','veo','ver','queda','quedan',
    'siento','hace','hacen','da','dan','permite','permite',
}

def clean_text(v):
    """Normaliza y limpia texto libre. Elimina acentos para mejor matching."""
    if not isinstance(v, str): return ''
    try: v = v.encode('latin1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError): pass
    v = v.lower().strip()
    # quitar acentos para normalizar stopwords
    v = unicodedata.normalize('NFD', v)
    v = ''.join(c for c in v if unicodedata.category(c) != 'Mn')
    v = re.sub(r'[^\w\s]', ' ', v)
    v = re.sub(r'\s+', ' ', v).strip()
    return v

def is_meaningful(v):
    t = clean_text(v)
    if not t or len(t) < 3: return False
    if t in NO_MEANING: return False
    if any(t == nm or t.startswith(nm+' ') or t.endswith(' '+nm) for nm in NO_MEANING if len(nm) > 3):
        return False
    return True

def img_path(code):
    rel = PROD_IMG.get(code,'')
    if not rel: return None
    p = os.path.join(IMG_BASE, rel.replace('/', os.sep))
    return p if os.path.exists(p) else None

def prod_brand(code):
    if code.endswith('_s'): return 'Selmark',         '#1B2B3B', 'badge-s'
    if code.endswith('_a'): return 'Comp. aspiracional','#2E86AB', 'badge-a'
    if code.endswith('_b'): return 'Comp. accesible',  '#6A8BA4', 'badge-b'
    return 'Desconocido','#999',''

# ── GRÁFICOS ─────────────────────────────────────────────────────────────────
PC = {'modeBarButtonsToRemove': ['zoom2d','pan2d','select2d','lasso2d','zoomIn2d','zoomOut2d','autoScale2d','resetScale2d','hoverClosestCartesian','hoverCompareCartesian','toggleSpikelines'], 'displaylogo': False, 'displayModeBar': True}

def lay(title='', h=None):
    d = dict(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color=FONT, size=11),
        margin=dict(t=46 if title else 22, b=22, l=8, r=36),
        showlegend=False,
    )
    if title:
        d['title'] = dict(text=f'<b>{title}</b>', font=dict(size=12, color='#1B2B3B'), x=0, pad=dict(b=6))
    if h: d['height'] = h
    return d

def gradient_colors(vals):
    mn, mx = min(vals), max(vals)
    if mx == mn: mx = mn + 1
    out = []
    for v in vals:
        n = (v - mn) / (mx - mn)
        r = int(0x7F + (0x2E-0x7F)*n); g = int(0xB3 + (0x86-0xB3)*n); b = int(0xD3 + (0xAB-0xD3)*n)
        out.append(f'rgb({r},{g},{b})')
    return out

def hbar(y_vals, x_vals, color=None, title='', h=300, gradient=False):
    xv = [float(v) for v in x_vals]
    cols = gradient_colors(xv) if gradient else (color or P[0])
    mx = max(xv) if xv else 1
    fig = go.Figure(go.Bar(
        y=list(y_vals), x=xv, orientation='h',
        marker=dict(color=cols, line=dict(width=0)),
        text=[str(int(v)) if v == int(v) else f'{v:.1f}' for v in xv],
        textposition='outside', textfont=dict(size=10, color=FONT),
    ))
    fig.update_layout(**lay(title, h),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[0, mx*1.22]),
        yaxis=dict(showgrid=False, tickfont=dict(size=10), autorange='reversed'),
    )
    return fig

def vbar(x_vals, y_vals, colors=None, title='', h=300):
    yv = [float(v) for v in y_vals]
    fig = go.Figure(go.Bar(
        x=list(x_vals), y=yv,
        marker=dict(color=colors or P[:len(x_vals)], line=dict(width=0)),
        text=[str(int(v)) if v == int(v) else f'{v:.1f}' for v in yv],
        textposition='outside', textfont=dict(size=10, color=FONT),
    ))
    fig.update_layout(**lay(title, h),
        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, showticklabels=False),
    )
    return fig

def radar_fig(cats, vals_dict, title='', h=400):
    fig = go.Figure()
    cats_c = cats + [cats[0]]
    for i, (name, vals) in enumerate(vals_dict.items()):
        v = [float(x) if not pd.isna(x) else 0 for x in vals] + [float(vals[0]) if not pd.isna(vals[0]) else 0]
        col = PERSONA_C.get(name, RADAR_C[i % len(RADAR_C)])
        r,g,b = int(col[1:3],16), int(col[3:5],16), int(col[5:7],16)
        fig.add_trace(go.Scatterpolar(
            r=v, theta=cats_c, name=name,
            line=dict(color=col, width=2),
            fill='toself', fillcolor=f'rgba({r},{g},{b},0.08)',
        ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[1,5], tickfont=dict(size=9),
                            gridcolor=GRID, linecolor=GRID),
            angularaxis=dict(tickfont=dict(size=9, family='Inter'), gridcolor=GRID),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=11, color=FONT),
        showlegend=len(vals_dict) > 1,
        legend=dict(orientation='h', y=-0.18, font=dict(size=10)),
        margin=dict(t=50, b=70, l=40, r=40),
        height=h,
    )
    if title:
        fig.update_layout(title=dict(text=f'<b>{title}</b>', font=dict(size=12,color='#4A7A9B'), x=0))
    return fig

def heatmap_fig(data_df, title='', h=320):
    z = [[float(v) if not pd.isna(v) else 0 for v in row] for row in data_df.values]
    fig = go.Figure(go.Heatmap(
        z=z, x=list(data_df.columns), y=list(data_df.index),
        colorscale=[[0,'#EAF2F8'],[0.5,'#7FB3D3'],[1,'#1B4F72']],
        showscale=False,
        text=[[f'{v:.1f}' for v in row] for row in z],
        texttemplate='%{text}',
        textfont=dict(size=10, color=FONT),
    ))
    fig.update_layout(**lay(title, h),
        xaxis=dict(tickfont=dict(size=10), side='bottom'),
        yaxis=dict(tickfont=dict(size=10), autorange='reversed'),
    )
    return fig

def group_mean(df, cols, grp_col, groups):
    num = df[cols].apply(pd.to_numeric, errors='coerce')
    rows = {ag: num[df[grp_col] == ag].mean() for ag in groups}
    return pd.DataFrame(rows).T

def top_mentions(series, n=12):
    cts = Counter()
    for val in series.dropna():
        for item in str(val).split('|'):
            item = item.strip().title()
            if item and item.lower() not in NO_MEANING and len(item) > 2:
                cts[item] += 1
    return pd.DataFrame(cts.most_common(n), columns=['Marca','Menciones'])

def section(txt):
    st.markdown(f'<div class="section-title">{txt}</div><div class="section-rule"></div>',
                unsafe_allow_html=True)

def hr():
    st.markdown('<hr>', unsafe_allow_html=True)

# ── TEXT MINING ──────────────────────────────────────────────────────────────
def text_mining(series, n_clusters=6, n_terms=5, title=''):
    """Agrupa respuestas abiertas con TF-IDF + KMeans."""
    texts = [clean_text(v) for v in series.dropna() if is_meaningful(v)]
    if len(texts) < n_clusters * 2:
        return None, None

    try:
        vec = TfidfVectorizer(
            max_features=300,
            stop_words=list(STOPWORDS_ES),
            min_df=2,
            ngram_range=(1,2),
        )
        X = vec.fit_transform(texts)
        n_k = min(n_clusters, len(texts)//3)
        km = KMeans(n_clusters=n_k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        terms = vec.get_feature_names_out()
        clusters = []
        for i in range(n_k):
            center = km.cluster_centers_[i]
            top_idx = center.argsort()[::-1][:n_terms]
            top_t = [terms[j] for j in top_idx if center[j] > 0]
            count = int((labels == i).sum())
            sample_texts = [texts[j] for j in range(len(texts)) if labels[j] == i][:3]
            clusters.append({'id':i, 'terms':top_t, 'count':count, 'samples':sample_texts})
        clusters.sort(key=lambda c: c['count'], reverse=True)
        return clusters, len(texts)
    except Exception:
        return None, None

def cluster_label(terms):
    """Convierte los términos clave de un cluster en un nombre legible."""
    if not terms: return 'Otros'
    # Capitalizar y limpiar: eliminar bigramas redundantes si ya está el unigrama
    unique = []
    seen_words = set()
    for t in terms:
        words = t.split()
        if len(words) == 1:
            if t not in seen_words:
                unique.append(t.capitalize())
                seen_words.add(t)
        else:
            # bigrama: incluir solo si aporta algo nuevo
            if not any(w in seen_words for w in words):
                unique.append(t.capitalize())
                seen_words.update(words)
    return ' · '.join(unique[:3]) if unique else terms[0].capitalize()

def show_text_mining(series, title=''):
    clusters, total = text_mining(series, n_clusters=6)
    if not clusters:
        words = Counter()
        for v in series.dropna():
            if is_meaningful(v):
                for w in clean_text(v).split():
                    if w not in STOPWORDS_ES and len(w) > 3:
                        words[w] += 1
        if words:
            top = words.most_common(15)
            st.plotly_chart(hbar([t[0].capitalize() for t in top],
                                  [t[1] for t in top], gradient=True, title=title, h=350),
                            use_container_width=True, config=PC)
        return

    st.markdown(
        f'<div class="chart-label">{title} — {total} respuestas válidas · '
        f'agrupadas automáticamente en {len(clusters)} motivos principales</div>',
        unsafe_allow_html=True)

    for i, cl in enumerate(clusters):
        lbl   = cluster_label(cl['terms'])
        pct   = cl['count'] / total * 100
        chips = ' '.join(f'<span class="cluster-chip">{t}</span>' for t in cl['terms'])
        pct_bar = f'<div style="height:4px;background:#EAF2F8;border-radius:2px;margin:6px 0 8px">' \
                  f'<div style="height:4px;background:#2E86AB;border-radius:2px;width:{pct:.0f}%"></div></div>'
        ejemplos = ' · '.join(f'<i>"{s[:60]}"</i>' for s in cl['samples'][:2])
        st.markdown(
            f'<div style="background:#fff;border:1px solid #D4E4F0;border-left:4px solid #2E86AB;'
            f'border-radius:0 6px 6px 0;padding:12px 16px;margin-bottom:10px">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">'
            f'<span style="font-weight:600;font-size:.85rem;color:#1B2B3B">{lbl}</span>'
            f'<span style="font-size:.75rem;color:#2E86AB;font-weight:600">{cl["count"]} respuestas &nbsp;({pct:.0f}%)</span>'
            f'</div>'
            f'{pct_bar}'
            f'<div style="margin-bottom:6px">{chips}</div>'
            f'<div style="font-size:.7rem;color:#7A9AB4">{ejemplos}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── ANÁLISIS DE MARCA POR NOMBRE ──────────────────────────────────────────────
BRANDS_LENC = [
    'intimissimi','calzedonia','calcedonia','women secret','woman secret','womens secret',
    'calvin klein','primark','zara','h&m','oysho','cortefiel','triumph','selmark',
    'etam','livy','victoria secret','victorias secret','lidl','alcampo','el corte ingles',
    'tezenis','wonderbra','marks spencer','bershka','pull bear',
]
BRANDS_BANO = [
    'calzedonia','calcedonia','oysho','zara','primark','h&m','decathlon','lidl',
    'alcampo','el corte ingles','shein','mango','stradivarius','bershka',
    'speedo','arena','adidas','nike','women secret','woman secret',
]
BRANDS_SPORT = [
    'nike','adidas','decathlon','zara','primark','h&m','oysho','under armour',
    'puma','lululemon','mango','shein','lidl','alcampo','el corte ingles',
    'columbia','the north face','reebok','new balance','asics',
]
BRANDS_HOME = [
    'zara','h&m','primark','oysho','mango','shein','stradivarius','bershka',
    'alcampo','lidl','el corte ingles','calzedonia','women secret','woman secret',
    'sfera','cortefiel',
]

def brand_grouped_analysis(motivo_series, brand_list, min_count=4):
    """
    Agrupa respuestas de 'motivo' según qué marca mencionan.
    Devuelve lista de {brand, count, top_words, samples}.
    """
    results = []
    for brand in brand_list:
        mask = motivo_series.dropna().apply(
            lambda v: brand in clean_text(v)
        )
        matching = motivo_series.dropna()[mask]
        if len(matching) < min_count:
            continue
        # extraer palabras clave (excluyendo la propia marca y stopwords)
        brand_words = set(brand.split())
        words = Counter()
        for v in matching:
            for w in clean_text(v).split():
                if w not in STOPWORDS_ES and w not in brand_words and len(w) > 3:
                    words[w] += 1
        top_w = [w for w,_ in words.most_common(6)]
        samples = [v for v in matching.tolist()[:3] if is_meaningful(v)]
        results.append({
            'brand': brand.title(),
            'count': len(matching),
            'top_words': top_w,
            'samples': samples,
        })
    results.sort(key=lambda r: r['count'], reverse=True)
    return results

def show_brand_analysis(motivo_series, brand_list, title=''):
    """Muestra análisis agrupado por marca con sus atributos principales."""
    results = brand_grouped_analysis(motivo_series, brand_list)
    if not results:
        show_text_mining(motivo_series, title)
        return

    total = motivo_series.dropna().apply(is_meaningful).sum()
    st.markdown(f'<div class="chart-label">{title} — {total} respuestas · agrupadas por marca mencionada</div>',
                unsafe_allow_html=True)

    c1, c2 = st.columns([2,3], gap='large')
    with c1:
        st.plotly_chart(
            hbar([r['brand'] for r in results[:10]],
                 [r['count'] for r in results[:10]],
                 gradient=True, h=max(280, len(results[:10])*46)),
            use_container_width=True, config=PC)
    with c2:
        for r in results[:8]:
            pct = r['count'] / total * 100 if total else 0
            chips = ' '.join(f'<span class="cluster-chip">{w}</span>' for w in r['top_words'])
            pct_bar = (f'<div style="height:4px;background:#EAF2F8;border-radius:2px;margin:5px 0 7px">'
                       f'<div style="height:4px;background:#2E86AB;border-radius:2px;width:{min(pct*3,100):.0f}%"></div></div>')
            ejemplo = f'<i>"{r["samples"][0][:80]}"</i>' if r['samples'] else ''
            st.markdown(
                f'<div style="background:#fff;border:1px solid #D4E4F0;border-left:4px solid #1B4F72;'
                f'border-radius:0 6px 6px 0;padding:10px 14px;margin-bottom:8px">'
                f'<div style="display:flex;justify-content:space-between;align-items:center">'
                f'<span style="font-weight:700;font-size:.9rem;color:#1B2B3B">{r["brand"]}</span>'
                f'<span style="font-size:.72rem;color:#2E86AB;font-weight:600">{r["count"]} menciones</span>'
                f'</div>'
                f'{pct_bar}'
                f'<div style="margin-bottom:5px">{chips if chips else "<span style=\'color:#aaa;font-size:.7rem\'>sin atributos frecuentes</span>"}</div>'
                f'<div style="font-size:.7rem;color:#7A9AB4">{ejemplo}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

# ── DATOS ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    s1 = pd.read_csv(os.path.join(base, 'data', 'selmark_S1_lenceria_bano.csv'),
                     encoding='utf-8-sig', dtype=str)
    s2 = pd.read_csv(os.path.join(base, 'data', 'selmark_S2_deporte_homewear.csv'),
                     encoding='utf-8-sig', dtype=str)
    for d in [s1, s2]:
        d['Edad']         = pd.to_numeric(d['Edad'],         errors='coerce')
        d['Duracion_min'] = pd.to_numeric(d['Duracion_min'], errors='coerce')
        def fix_enc(v):
            if not isinstance(v, str): return v
            try: return v.encode('latin1').decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError): return v
        for c in d.select_dtypes(include='object').columns:
            d[c] = d[c].apply(fix_enc)
    return s1, s2

s1_raw, s2_raw = load_data()

CP_CCAA = {
    '01':'País Vasco','02':'Castilla-La Mancha','03':'C. Valenciana','04':'Andalucía',
    '05':'Castilla y León','06':'Extremadura','07':'Baleares','08':'Cataluña',
    '09':'Castilla y León','10':'Extremadura','11':'Andalucía','12':'C. Valenciana',
    '13':'Castilla-La Mancha','14':'Andalucía','15':'Galicia','16':'Castilla-La Mancha',
    '17':'Cataluña','18':'Andalucía','19':'Castilla-La Mancha','20':'País Vasco',
    '21':'Andalucía','22':'Aragón','23':'Andalucía','24':'Castilla y León',
    '25':'Cataluña','26':'La Rioja','27':'Galicia','28':'Comunidad de Madrid',
    '29':'Andalucía','30':'Murcia','31':'Navarra','32':'Galicia','33':'Asturias',
    '34':'Castilla y León','35':'Canarias','36':'Galicia','37':'Castilla y León',
    '38':'Canarias','39':'Cantabria','40':'Castilla y León','41':'Andalucía',
    '42':'Castilla y León','43':'Cataluña','44':'Aragón','45':'Castilla-La Mancha',
    '46':'C. Valenciana','47':'Castilla y León','48':'País Vasco','49':'Castilla y León',
    '50':'Aragón','51':'Ceuta','52':'Melilla',
}

LS_COLS = [
    'LS_cuesta_cambiar_marca','LS_mismo_supermercado','LS_planes_tranquilos',
    'LS_marcas_por_percepcion','LS_restaurante_reputacion','LS_cultura_viajes',
    'LS_sin_estilo','LS_restaurantes_nuevos','LS_se_adapta',
    'LS_origen_impacto','LS_actividades_aporte','LS_experiencia_vs_anillo',
]
# Nombres de buyer persona por cluster (validados con k=4 sobre datos reales)
# 0=Tradicional Fiel, 1=Hogareña Práctica, 2=Exploradora, 3=Aspiracional
PERSONA_NAMES = {
    0: 'La Tradicional Fiel',
    1: 'La Hogareña Práctica',
    2: 'La Exploradora Comprometida',
    3: 'La Aspiracional',
}
PERSONA_DESCS = {
    'La Aspiracional':
        ('Orientada a imagen y marcas de calidad. Le importa la reputación, viaja y consume cultura. '
         'Mayor grupo — consumidora activa de moda.',
         ['calidad y reputación','cultura y viajes','marcas por imagen','restaurantes de referencia']),
    'La Tradicional Fiel':
        ('Leal a sus marcas de siempre. Prefiere planes tranquilos y rutinas conocidas. '
         'No busca novedades — compra lo que ya conoce.',
         ['fidelidad de marca','rutinas fijas','planes tranquilos','poco exploratoria']),
    'La Hogareña Práctica':
        ('Disfruta de lo cotidiano y del hogar. Sin aspiraciones de status pero con valores experienciales. '
         'Pragmática y tranquila.',
         ['planes tranquilos','rutina','experiencial','sin interés en imagen']),
    'La Exploradora Comprometida':
        ('Le gusta probar cosas nuevas, se adapta fácil. Preocupada por el impacto social y medioambiental. '
         'La más moderna y ética.',
         ['exploratoria','flexible','comprometida socialmente','valora experiencias']),
}

@st.cache_data
def compute_personas(df_in):
    """KMeans k=4 sobre LS_ cols → buyer personas tipo Sinus."""
    ls_avail = [c for c in LS_COLS if c in df_in.columns]
    if len(ls_avail) < 4 or len(df_in) < 20:
        return pd.Series(['Sin clasificar']*len(df_in), index=df_in.index)
    ls_num = df_in[ls_avail].apply(pd.to_numeric, errors='coerce').fillna(3)
    X = StandardScaler().fit_transform(ls_num)
    km = KMeans(n_clusters=4, random_state=42, n_init=20)
    labels = km.fit_predict(X)
    # Asignar nombre por perfil del centroide
    centers = pd.DataFrame(km.cluster_centers_, columns=ls_avail)
    # Nombre basado en características dominantes
    name_map = {}
    for i in range(4):
        row = centers.iloc[i]
        if (row.get('LS_planes_tranquilos',0) > 0.3 and
                row.get('LS_cuesta_cambiar_marca',0) > 0.3):
            name_map[i] = 'La Tradicional Fiel'
        elif (row.get('LS_restaurantes_nuevos',0) > 0.3 and
                row.get('LS_se_adapta',0) > 0.2):
            name_map[i] = 'La Exploradora Comprometida'
        elif (row.get('LS_marcas_por_percepcion',0) > 0.1 and
                row.get('LS_restaurante_reputacion',0) > 0.1):
            name_map[i] = 'La Aspiracional'
        else:
            name_map[i] = 'La Hogareña Práctica'
    # Si hay duplicados, resolver por segunda opción
    used = set()
    all_names = ['La Aspiracional','La Tradicional Fiel','La Hogareña Práctica','La Exploradora Comprometida']
    for i in range(4):
        if name_map[i] in used:
            for alt in all_names:
                if alt not in used:
                    name_map[i] = alt; break
        used.add(name_map[i])
    return pd.Series([name_map[l] for l in labels], index=df_in.index)

def enrich(df):
    df = df.copy()
    def ag(a): return None if pd.isna(a) else '18–30' if a<=30 else '31–45' if a<=45 else '46+'
    def ccaa(cp):
        if not isinstance(cp,str): return 'Desconocido'
        cp = cp.strip().zfill(5)
        return CP_CCAA.get(cp[:2], 'Desconocido')
    df['Grupo_edad']  = df['Edad'].apply(ag)
    df['CCAA']        = df['Codigo_postal'].apply(ccaa)
    df['Zona_agr']    = df['CCAA']
    df['Buyer_persona'] = compute_personas(df)
    return df

SPAIN_GEOJSON_URL = 'https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-communities.geojson'

@st.cache_data
def load_spain_geojson():
    import urllib.request, json
    try:
        with urllib.request.urlopen(SPAIN_GEOJSON_URL, timeout=8) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

# Mapeo nombre GeoJSON → nombre CCAA interno
GEOJSON_NAME_MAP = {
    'Andalucía': 'Andalucía',
    'Aragón': 'Aragón',
    'Asturias, Principality of': 'Asturias',
    'Principado de Asturias': 'Asturias',
    'Balearic Islands': 'Islas Baleares',
    'Illes Balears': 'Islas Baleares',
    'Islas Baleares': 'Islas Baleares',
    'Canary Islands': 'Islas Canarias',
    'Canarias': 'Islas Canarias',
    'Cantabria': 'Cantabria',
    'Castilla y León': 'Castilla y León',
    'Castilla-La Mancha': 'Castilla-La Mancha',
    'Cataluña': 'Cataluña',
    'Catalunya': 'Cataluña',
    'Ceuta': 'Ceuta',
    'Comunidad de Madrid': 'Comunidad de Madrid',
    'Madrid': 'Comunidad de Madrid',
    'Comunidad Foral de Navarra': 'Navarra',
    'Navarra': 'Navarra',
    'Comunitat Valenciana': 'C. Valenciana',
    'C. Valenciana': 'C. Valenciana',
    'Extremadura': 'Extremadura',
    'Galicia': 'Galicia',
    'La Rioja': 'La Rioja',
    'Melilla': 'Melilla',
    'País Vasco': 'País Vasco',
    'Basque Country': 'País Vasco',
    'Región de Murcia': 'Murcia',
    'Murcia': 'Murcia',
}

def spain_map_fig(df, selected_ccaa=None):
    """Mapa coroplético de España por CCAA coloreado por nº encuestadas."""
    geojson = load_spain_geojson()
    ccaa_counts = df['CCAA'].value_counts().to_dict()

    if geojson is None:
        # Fallback: burbujas si no hay internet
        lats, lons, names, sizes, colors, texts = [], [], [], [], [], []
        for ccaa, (lat, lon) in CCAA_COORDS.items():
            n = ccaa_counts.get(ccaa, 0)
            lats.append(lat); lons.append(lon); names.append(ccaa)
            sizes.append(max(10, n/3) if n > 0 else 6); colors.append(n)
            texts.append(f'<b>{ccaa}</b><br>{n} encuestadas')
        fig = go.Figure(go.Scattergeo(
            lat=lats, lon=lons, mode='markers',
            marker=dict(size=sizes, color=colors,
                        colorscale=[[0,'#EBF5FB'],[0.15,'#85C1E9'],[0.5,'#2E86AB'],[1,'#1B2B3B']],
                        showscale=True, sizemode='diameter',
                        colorbar=dict(thickness=10, len=0.5, title=dict(text='n', font=dict(size=9)))),
            hovertext=texts, hoverinfo='text', customdata=names,
        ))
        fig.update_geos(scope='europe', center=dict(lat=40.4, lon=-3.7),
                        projection_scale=5.5, showland=True, landcolor='#F0F4F8',
                        showcoastlines=True, coastlinecolor='#B0C8D8',
                        showocean=True, oceancolor='#EAF2F8', showframe=False)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=5,b=5,l=0,r=0), height=420)
        return fig

    # Construir listas para choropleth con ids de features
    feature_ids, feature_names, feature_counts, hover_texts = [], [], [], []
    for feat in geojson['features']:
        props = feat.get('properties', {})
        raw_name = props.get('name') or props.get('NAME') or props.get('cartodb_id','')
        ccaa_name = GEOJSON_NAME_MAP.get(raw_name, raw_name)
        n = ccaa_counts.get(ccaa_name, 0)
        feat_id = feat.get('id') or props.get('cartodb_id') or raw_name
        feat['id'] = str(feat_id)
        feature_ids.append(str(feat_id))
        feature_names.append(ccaa_name)
        feature_counts.append(n)
        pct = round(n / len(df) * 100, 1) if len(df) > 0 else 0
        if n > 0:
            hover_texts.append(f'<b>{ccaa_name}</b><br>{n} encuestadas ({pct}%)')
        else:
            hover_texts.append(f'<b>{ccaa_name}</b><br>Sin datos en esta muestra')

    zmax = max(feature_counts) if max(feature_counts) > 0 else 1

    # Colorscale: gris claro para 0, azul progresivo para > 0
    colorscale = [
        [0.0,  '#E8EDF2'],   # sin datos → gris azulado claro
        [0.01, '#C5DCF0'],   # muy pocos
        [0.25, '#5DADE2'],   # medio
        [0.6,  '#2E86AB'],   # alto
        [1.0,  '#1B2B3B'],   # máximo
    ]

    fig = go.Figure(go.Choropleth(
        geojson=geojson,
        locations=feature_ids,
        z=feature_counts,
        colorscale=colorscale,
        zmin=0,
        zmax=zmax,
        marker_line_color='white',
        marker_line_width=1.5,
        colorbar=dict(
            title=dict(text='Encuestadas', font=dict(size=10, color=FONT)),
            thickness=14, len=0.65, x=1.0, xanchor='left',
            tickfont=dict(size=9, color=FONT),
            bgcolor='rgba(255,255,255,0.8)',
        ),
        hovertext=hover_texts,
        hoverinfo='text',
        customdata=feature_names,
    ))
    # fitbounds ajusta automáticamente el zoom a España
    fig.update_geos(
        fitbounds='locations',
        visible=False,
        bgcolor='rgba(0,0,0,0)',
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        geo=dict(bgcolor='rgba(0,0,0,0)', showframe=False, showcoastlines=False),
        margin=dict(t=5, b=5, l=0, r=10),
        height=450,
        dragmode='select',
    )
    # Resaltar CCAA seleccionada con borde rojo
    if selected_ccaa and selected_ccaa in feature_names:
        sel_idx = feature_names.index(selected_ccaa)
        fig.add_trace(go.Choropleth(
            geojson=geojson,
            locations=[feature_ids[sel_idx]],
            z=[zmax],
            colorscale=[[0,'#E74C3C'],[1,'#E74C3C']],
            showscale=False,
            marker_line_color='#C0392B',
            marker_line_width=2.5,
            hoverinfo='skip',
        ))
    return fig

# ── HEADER TOP BAR ────────────────────────────────────────────────────────────
import os as _os

def _logo_b64(fname):
    path = _os.path.join(IMG_BASE, 'img', fname)
    if _os.path.exists(path):
        import mimetypes
        mime = mimetypes.guess_type(path)[0] or 'image/png'
        with open(path, 'rb') as f:
            return f'<img src="data:{mime};base64,{base64.b64encode(f.read()).decode()}" style="height:52px;width:160px;object-fit:contain;object-position:left center;display:block;" />'
    return None

_sel_img = _logo_b64('logo_selmark.png') or _logo_b64('logo_selmark.jpg') or _logo_b64('logo_selmark.svg')
_min_img = _logo_b64('logo_minsait.png') or _logo_b64('logo_minsait.jpg') or _logo_b64('logo_minsait.svg')

# Fallback SVG logos if files not found
_sel_html = _sel_img or '''<svg width="160" height="52" viewBox="0 0 160 52" xmlns="http://www.w3.org/2000/svg">
  <text x="4" y="36" font-family="Georgia,serif" font-size="30" font-weight="700" fill="#1B2B3B" letter-spacing="-0.5">selmark</text>
  <text x="64" y="48" font-family="Arial,sans-serif" font-size="8" font-weight="400" fill="#6A8BA4" letter-spacing="3">LINGERIE</text>
</svg>'''

_min_html = _min_img or '''<svg width="160" height="52" viewBox="0 0 160 52" xmlns="http://www.w3.org/2000/svg">
  <text x="2" y="36" font-family="Arial,sans-serif" font-size="18" fill="#5C1A3A">✕</text>
  <text x="24" y="36" font-family="Arial Black,sans-serif" font-size="22" font-weight="900" fill="#5C1A3A" letter-spacing="1">MINSAIT</text>
</svg>'''

st.markdown(f"""
<div class="top-bar">
  <div style="display:flex;align-items:center;width:160px">{_sel_html}</div>
  <div class="top-center">Consumer Insights · Research 2025</div>
  <div style="display:flex;align-items:center;justify-content:flex-end;width:160px">{_min_html}</div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="text-align:center;padding:8px 0 16px">
  <div style="font-family:Montserrat,sans-serif;font-size:1.2rem;font-weight:700;letter-spacing:.15em;color:#fff">SELMARK</div>
  <div style="font-size:.6rem;letter-spacing:.2em;text-transform:uppercase;color:#7FAFD4">Consumer Intelligence</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown('---')

survey_sel = st.sidebar.radio('Encuesta', ['Lencería & Baño', 'Deporte & Homewear'])
is_s1      = survey_sel == 'Lencería & Baño'
df_all     = enrich(s1_raw if is_s1 else s2_raw)

st.sidebar.markdown('<br>', unsafe_allow_html=True)
st.sidebar.markdown('**Filtros**')

age_opts = ['Todos los grupos'] + AGES
age_f    = st.sidebar.selectbox('Edad', age_opts)

ccaa_opts = ['Todas las CCAA'] + sorted(df_all['CCAA'].dropna().unique().tolist())
geo_f     = st.sidebar.selectbox('Comunidad autónoma', ccaa_opts)

persona_opts = ['Todos los perfiles'] + list(PERSONA_NAMES.values())
tipo_f       = st.sidebar.selectbox('Buyer persona', persona_opts)

mask = pd.Series(True, index=df_all.index)
if age_f  != 'Todos los grupos':   mask &= df_all['Grupo_edad']    == age_f
if geo_f  != 'Todas las CCAA':     mask &= df_all['CCAA']          == geo_f
if tipo_f != 'Todos los perfiles': mask &= df_all['Buyer_persona'] == tipo_f
df = df_all[mask].copy()

st.sidebar.markdown('---')
st.sidebar.markdown(
    f'<div style="text-align:center;padding:8px">'
    f'<div style="font-family:Montserrat,sans-serif;font-size:2rem;font-weight:700;color:#fff">{len(df):,}</div>'
    f'<div style="font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:#7FAFD4">respuestas</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── KPIs ──────────────────────────────────────────────────────────────────────
lbl      = 'Lencería & Baño' if is_s1 else 'Deporte & Homewear'
e_m      = df['Edad'].mean()
top_ccaa = df['CCAA'].value_counts().index[0] if len(df) else '—'
pct_top  = df['CCAA'].value_counts().iloc[0]/len(df)*100 if len(df) else 0
d_m      = df['Duracion_min'].mean()
comp_pct = (df['Grupo_edad']=='31–45').sum()/len(df)*100 if len(df) else 0

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-label">Muestra</div>
    <div class="kpi-value">{len(df):,}</div>
    <div class="kpi-sub">{survey_sel}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Edad media</div>
    <div class="kpi-value">{e_m:.1f}</div>
    <div class="kpi-sub">años</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">CCAA principal</div>
    <div class="kpi-value" style="font-size:1.3rem">{top_ccaa}</div>
    <div class="kpi-sub">{pct_top:.0f}% de la muestra</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Duración media</div>
    <div class="kpi-value">{d_m:.1f}'</div>
    <div class="kpi-sub">minutos</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Segmento principal</div>
    <div class="kpi-value">{comp_pct:.0f}%</div>
    <div class="kpi-sub">31–45 años</div>
  </div>
</div>
""", unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs(['  Perfil  ','  Lifestyle  ','  Compra  ','  Marcas  ','  Producto  ','  Color  '])

# ═══════════════════════════════════════════════════════════════════
# TAB 1 — PERFIL
# ═══════════════════════════════════════════════════════════════════
with tab1:
    try:
        section('Perfil demográfico')
        c1, c2 = st.columns(2, gap='large')

        df_geo = df
        hr()
        c1, c2 = st.columns(2, gap='large')
        with c1:
            age_v = df_geo['Grupo_edad'].value_counts().reindex(AGES).fillna(0)
            st.plotly_chart(vbar(AGES, [float(age_v[a]) for a in AGES],
                                 colors=P[:3], title='Distribución por edad', h=280),
                            use_container_width=True, config=PC)

            ccaa_v = df_geo['CCAA'].value_counts().head(10)
            st.plotly_chart(hbar(list(ccaa_v.index), list(ccaa_v.values),
                                  gradient=True, title='Top CCAA por muestra', h=340),
                            use_container_width=True, config=PC)

        with c2:
            renta_order = ['Menos de 20.000 €','20.000 – 35.000 € (medio-bajo)',
                           '35.000 – 55.000 € (medio)','55.000 – 75.000 € (medio-alto)',
                           'Más de 75.000 € (alto)']
            renta_short = {'Menos de 20.000 €':'< 20K €','20.000 – 35.000 € (medio-bajo)':'20–35K €',
                           '35.000 – 55.000 € (medio)':'35–55K €','55.000 – 75.000 € (medio-alto)':'55–75K €',
                           'Más de 75.000 € (alto)':'> 75K €'}
            rc = df_geo['Renta_anual_hogar'].value_counts()
            rl = [renta_short.get(r,r) for r in renta_order if r in rc]
            rv = [int(rc[r]) for r in renta_order if r in rc]
            if rl:
                st.plotly_chart(hbar(rl, rv, gradient=True, title='Renta anual del hogar', h=280),
                                use_container_width=True, config=PC)

            bp_v = df_geo['Buyer_persona'].value_counts()
            bp_colors = [PERSONA_C.get(p, P[0]) for p in bp_v.index]
            fig_bp = go.Figure(go.Bar(
                x=list(bp_v.index), y=list(bp_v.values),
                marker=dict(color=bp_colors, line=dict(width=0)),
                text=list(bp_v.values), textposition='outside',
                textfont=dict(size=10, color=FONT),
            ))
            fig_bp.update_layout(**lay('Buyer personas', 280),
                xaxis=dict(showgrid=False, tickfont=dict(size=9)),
                yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, showticklabels=False),
            )
            st.plotly_chart(fig_bp, use_container_width=True, config=PC)

        hr()
        section('Cruce edad × comunidad autónoma')
        if len(df_geo) > 10:
            top_ccaa_list = df_geo['CCAA'].value_counts().head(8).index.tolist()
            df_top = df_geo[df_geo['CCAA'].isin(top_ccaa_list)]
            cross = pd.crosstab(df_top['Grupo_edad'], df_top['CCAA']).reindex(AGES).fillna(0)
            cp = (cross.div(cross.sum(axis=1).replace(0,1), axis=0)*100).round(1)
            st.plotly_chart(heatmap_fig(cp, '% por CCAA dentro de cada grupo de edad (top 8 CCAA)', h=260),
                            use_container_width=True, config=PC)

    except Exception as e:
        st.error(f'Error Perfil: {e}'); st.code(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════════
# TAB 2 — LIFESTYLE + BUYER PERSONAS
# ═══════════════════════════════════════════════════════════════════
with tab2:
    try:
        ls_cols = [c for c in df.columns if c.startswith('LS_')]
        ls_lbls = [c.replace('LS_','').replace('_',' ').capitalize() for c in ls_cols]

        if not ls_cols:
            st.info('Sin datos de lifestyle.')
        else:
            ls_num = df[ls_cols].apply(pd.to_numeric, errors='coerce')

            # ── Buyer Personas ──────────────────────────────────────────
            section('Buyer Personas · Metodología Sinus')
            st.markdown(
                '<p style="font-size:.82rem;color:#6A8BA4;max-width:800px;margin-bottom:1.4rem">'
                'Las 4 buyer personas se derivan automáticamente de las 12 dimensiones de lifestyle '
                '(metodología Sinus) mediante clustering. Representan arquetipos de consumidora, '
                'no segmentos demográficos.</p>',
                unsafe_allow_html=True)

            # Tarjetas de persona
            p_order = ['La Aspiracional','La Tradicional Fiel',
                       'La Hogareña Práctica','La Exploradora Comprometida']
            bp_v = df['Buyer_persona'].value_counts()
            p_cols = st.columns(4)
            for col_obj, pname in zip(p_cols, p_order):
                with col_obj:
                    n = int(bp_v.get(pname, 0))
                    pct_p = n/len(df)*100 if len(df) else 0
                    col_hex = PERSONA_C.get(pname,'#2E86AB')
                    _pd = PERSONA_DESCS.get(pname, ('', []))
                    desc, tags = _pd[0], _pd[1]
                    tag_html = ''.join(f'<span class="persona-tag">{t}</span>' for t in tags)
                    st.markdown(
                        f'<div class="persona-card" style="background:{col_hex};color:#fff">'
                        f'<div class="persona-title">{pname}</div>'
                        f'<div class="persona-n">{n} encuestadas · {pct_p:.0f}%</div>'
                        f'<div style="font-size:.75rem;opacity:.85;margin-bottom:10px;line-height:1.4">{desc}</div>'
                        f'<div>{tag_html}</div>'
                        f'</div>',
                        unsafe_allow_html=True)

            hr()
            # ── Radar por persona ───────────────────────────────────────
            section('Perfil de lifestyle por buyer persona')
            means_total = [float(v) for v in ls_num.mean().values]
            vd_persona = {pname: [float(v) for v in ls_num[df['Buyer_persona']==pname].mean().values]
                          for pname in p_order if (df['Buyer_persona']==pname).sum()>4}
            c1, c2 = st.columns([3,2], gap='large')
            with c1:
                st.plotly_chart(radar_fig(ls_lbls, vd_persona,
                                          'Perfil de las 4 buyer personas', h=460),
                                use_container_width=True, config=PC)
            with c2:
                gm_p = group_mean(df, ls_cols, 'Buyer_persona', p_order)
                gm_p.columns = ls_lbls
                st.plotly_chart(heatmap_fig(gm_p.T.round(2),
                                            'Media por dimensión y buyer persona', h=460),
                                use_container_width=True, config=PC)

            hr()
            # ── Desglose adicional ──────────────────────────────────────
            section('Desglose por edad y CCAA')
            c1, c2 = st.columns(2, gap='large')
            with c1:
                vd_age = {ag:[float(v) for v in ls_num[df['Grupo_edad']==ag].mean().values]
                          for ag in AGES if (df['Grupo_edad']==ag).sum()>4}
                if vd_age:
                    st.plotly_chart(radar_fig(ls_lbls, vd_age, 'Por grupo de edad', h=400),
                                    use_container_width=True, config=PC)
            with c2:
                top4_ccaa = df['CCAA'].value_counts().head(4).index.tolist()
                vd_ccaa = {z:[float(v) for v in ls_num[df['CCAA']==z].mean().values]
                           for z in top4_ccaa if (df['CCAA']==z).sum()>4}
                if vd_ccaa:
                    st.plotly_chart(radar_fig(ls_lbls, vd_ccaa, 'Por CCAA (top 4)', h=400),
                                    use_container_width=True, config=PC)

    except Exception as e:
        st.error(f'Error Lifestyle: {e}'); st.code(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════════
# TAB 3 — COMPRA
# ═══════════════════════════════════════════════════════════════════
with tab3:
    try:
        section('Comportamiento de compra')

        if is_s1:
            spend_pairs = [('Gasto_lenceria_por_compra','Lencería'),('Gasto_bano_por_compra','Baño')]
            ch_fis = [('Canal_fisico_lenceria','Lencería'),('Canal_fisico_bano','Baño')]
            ch_onl = [('Canal_online_lenceria','Lencería'),('Canal_online_bano','Baño')]
        else:
            spend_pairs = [('Gasto_ropa_deportiva_por_compra','Deportiva'),('Gasto_homewear_por_compra','Homewear')]
            ch_fis = [('Canal_fisico_deportiva','Deportiva'),('Canal_fisico_homewear','Homewear')]
            ch_onl = [('Canal_online_deportiva','Deportiva'),('Canal_online_homewear','Homewear')]

        c1, c2 = st.columns(2, gap='large')
        with c1:
            fr = df['Frecuencia_compra_ropa'].value_counts().head(8)
            if not fr.empty:
                st.plotly_chart(hbar(list(fr.index), list(fr.values), gradient=True,
                                     title='Frecuencia de compra de ropa', h=310),
                                use_container_width=True, config=PC)
        with c2:
            def bucket_gasto(v):
                try:
                    n = float(str(v).replace('€','').replace(',','.').strip())
                    if n <= 30:  return 'Hasta 30 €'
                    if n <= 60:  return '31 – 60 €'
                    if n <= 100: return '61 – 100 €'
                    return 'Más de 100 €'
                except: return None
            bucket_order = ['Hasta 30 €','31 – 60 €','61 – 100 €','Más de 100 €']
            for i, (sc, lb) in enumerate(spend_pairs):
                if sc not in df.columns: continue
                buckets = df[sc].apply(bucket_gasto).dropna()
                sp = buckets.value_counts().reindex(bucket_order).dropna()
                if not sp.empty:
                    st.plotly_chart(hbar(list(sp.index), list(sp.values),
                                         gradient=True, title=f'Gasto por compra — {lb}', h=240),
                                    use_container_width=True, config=PC)

        hr()
        section('Canales de compra')
        c1, c2 = st.columns(2, gap='large')
        with c1:
            for i, (cc, lb) in enumerate(ch_fis):
                if cc not in df.columns: continue
                cts = Counter()
                for val in df[cc].dropna():
                    for item in str(val).split('|'):
                        item = item.strip()
                        if len(item)>1: cts[item]+=1
                top = pd.DataFrame(cts.most_common(8), columns=['Canal','N'])
                if not top.empty:
                    st.plotly_chart(hbar(list(top['Canal']), list(top['N']),
                                         gradient=True, title=f'Canal físico — {lb}', h=300),
                                    use_container_width=True, config=PC)
        with c2:
            for i, (cc, lb) in enumerate(ch_onl):
                if cc not in df.columns: continue
                cts = Counter()
                for val in df[cc].dropna():
                    for item in str(val).split('|'):
                        item = item.strip()
                        if len(item)>1: cts[item]+=1
                top = pd.DataFrame(cts.most_common(8), columns=['Canal','N'])
                if not top.empty:
                    st.plotly_chart(hbar(list(top['Canal']), list(top['N']),
                                         color=P[2], title=f'Canal online — {lb}', h=300),
                                    use_container_width=True, config=PC)

        # Motivos de compra — text mining
        hr()
        section('Motivos y barreras de compra — Text Mining')
        c1, c2 = st.columns(2, gap='large')
        with c1:
            if 'Motivos_compra_ropa' in df.columns:
                show_text_mining(df['Motivos_compra_ropa'], 'Motivos de compra')
        with c2:
            if 'Factores_frenan_compra' in df.columns:
                show_text_mining(df['Factores_frenan_compra'], 'Barreras de compra')

        # ── TALLAS ──────────────────────────────────────────────────
        hr()
        section('Análisis de tallas')
        c1, c2 = st.columns(2, gap='large')
        with c1:
            dif = df['Dificultad_encontrar_talla'].value_counts() if 'Dificultad_encontrar_talla' in df.columns else pd.Series()
            if not dif.empty:
                order = ['Nunca, siempre encuentro','A veces, depende de la marca','A menudo','Siempre es un problema']
                dif = dif.reindex([o for o in order if o in dif.index]).dropna()
                colors_dif = ['#27AE60','#F39C12','#E67E22','#E74C3C'][:len(dif)]
                fig_dif = go.Figure(go.Bar(
                    x=list(dif.values), y=list(dif.index), orientation='h',
                    marker=dict(color=colors_dif, line=dict(width=0)),
                    text=list(dif.values), textposition='outside', textfont=dict(size=10,color=FONT),
                ))
                fig_dif.update_layout(**lay('Dificultad para encontrar talla', 280),
                    xaxis=dict(showgrid=False,showticklabels=False,zeroline=False),
                    yaxis=dict(showgrid=False,tickfont=dict(size=10),autorange='reversed'),
                )
                st.plotly_chart(fig_dif, use_container_width=True, config=PC)

        with c2:
            if 'Motivo_dificultad_talla' in df.columns:
                mot = Counter()
                for val in df['Motivo_dificultad_talla'].dropna():
                    for item in str(val).split('|'):
                        item = item.strip()
                        if item and item != 'otro_talla' and len(item) > 3:
                            mot[item] += 1
                if mot:
                    top_mot = pd.DataFrame(mot.most_common(8), columns=['Motivo','N'])
                    st.plotly_chart(hbar(list(top_mot['Motivo']), list(top_mot['N']),
                                         gradient=True, title='Motivos de dificultad con la talla', h=280),
                                    use_container_width=True, config=PC)

        # ── Tallas con mayor dificultad ──────────────────────────────
        hr()
        section('¿Qué tallas no se encuentran?')
        st.markdown('<div class="chart-label">Tallas de personas que declaran dificultad frecuente (A menudo · Siempre es un problema)</div>',
                    unsafe_allow_html=True)

        hard_vals = ['A menudo','Siempre es un problema']

        def norm_talla(v):
            if not isinstance(v, str): return None
            v = v.strip().upper()
            if v in ('XS','S','M','L','XL','XXL','XXXL'): return v
            try:
                n = int(float(v))
                return str(n) if n > 0 else None
            except: return v if len(v) <= 5 else None

        def talla_insight_chart(df_all_t, df_hard_t, tc, tlabel):
            """Para cada talla: % de las que la tienen que tienen dificultad."""
            if tc not in df_all_t.columns or 'Dificultad_encontrar_talla' not in df_all_t.columns:
                return None
            tdf = df_all_t[[tc,'Dificultad_encontrar_talla']].copy()
            tdf['talla_n'] = tdf[tc].apply(norm_talla)
            tdf['hard'] = tdf['Dificultad_encontrar_talla'].isin(hard_vals)
            tdf = tdf.dropna(subset=['talla_n'])
            total_by_talla = tdf.groupby('talla_n').size()
            hard_by_talla  = tdf[tdf['hard']].groupby('talla_n').size()
            pct = (hard_by_talla / total_by_talla * 100).dropna()
            # Solo tallas con al menos 10 respuestas para evitar ruido
            valid = total_by_talla[total_by_talla >= 10].index
            pct = pct[pct.index.isin(valid)].sort_values(ascending=False).head(12)
            if pct.empty: return None
            colors = ['#E74C3C' if v >= 25 else '#E67E22' if v >= 15 else '#F39C12' if v >= 8 else '#27AE60'
                      for v in pct.values]
            fig = go.Figure(go.Bar(
                x=list(pct.index), y=list(pct.values),
                marker=dict(color=colors, line=dict(width=0)),
                text=[f'{v:.0f}%' for v in pct.values],
                textposition='outside', textfont=dict(size=11, color=FONT),
                customdata=[int(total_by_talla.get(t,0)) for t in pct.index],
                hovertemplate='<b>Talla %{x}</b><br>%{y:.1f}% tienen dificultad<br>n=%{customdata}<extra></extra>',
            ))
            fig.update_layout(**lay(f'{tlabel} — % con dificultad frecuente por talla', 320),
                xaxis=dict(showgrid=False, tickfont=dict(size=12, color=FONT)),
                yaxis=dict(range=[0, min(100, pct.max()*1.3)], showgrid=True, gridcolor=GRID,
                           zeroline=False, ticksuffix='%', showticklabels=False),
            )
            # Línea de referencia: media general
            pct_media = df_all_t['Dificultad_encontrar_talla'].isin(hard_vals).mean()*100
            fig.add_hline(y=pct_media, line_dash='dot', line_color='#6A8BA4', line_width=1.5,
                          annotation_text=f'Media {pct_media:.0f}%', annotation_position='top right',
                          annotation_font=dict(size=9, color='#6A8BA4'))
            return fig

        talla_cols_list = [('Talla_pantalon','Pantalón'), ('Talla_camiseta','Camiseta'), ('Talla_sujetador','Sujetador/top')]
        cols_t = st.columns(len(talla_cols_list), gap='large')
        for col_obj, (tc, tlabel) in zip(cols_t, talla_cols_list):
            fig_t = talla_insight_chart(df, df[df['Dificultad_encontrar_talla'].isin(hard_vals)], tc, tlabel)
            with col_obj:
                if fig_t:
                    st.plotly_chart(fig_t, use_container_width=True, config=PC)
                else:
                    st.info(f'Sin datos suficientes — {tlabel}')

        st.markdown('<div style="font-size:.68rem;color:#6A8BA4;margin-top:4px">'
                    '🔴 >25% · 🟠 15–25% · 🟡 8–15% · 🟢 <8% de dificultad · Solo tallas con n≥10 respuestas · '
                    'Línea punteada = media de la muestra</div>', unsafe_allow_html=True)

        # ── ATRIBUTOS FUNCIONALES Y EMOCIONALES ─────────────────────
        hr()
        section('Atributos valorados')
        if is_s1:
            func_cols = ['Func_lenc_Ajuste_sujecion','Func_lenc_Duracion','Func_lenc_Variedad_tallas',
                         'Func_lenc_Comodidad','Func_lenc_Calidad_precio','Func_lenc_Suavidad_tejido']
            func_labels = ['Ajuste/Sujeción','Duración','Variedad tallas','Comodidad','Calidad/precio','Suavidad tejido']
            emoc_cols = ['Emoc_lenc_Estetica','Emoc_lenc_Moderna','Emoc_lenc_Refleja_personalidad',
                         'Emoc_lenc_Destaca','Emoc_lenc_Identificacion_marca','Emoc_lenc_Diseno','Emoc_lenc_Marca_especialista']
            emoc_labels = ['Estética','Moderna','Refleja personalidad','Destaca','Identificación marca','Diseño','Marca especialista']
        else:
            func_cols = ['Func_sport_Sujecion','Func_sport_Transpirabilidad','Func_sport_Compresion',
                         'Func_sport_Calidad_precio','Func_sport_Secado_rapido','Func_sport_Variedad_tallas',
                         'Func_sport_Libertad_movimiento','Func_sport_Suavidad_tejido','Func_sport_Comodidad',
                         'Func_sport_Resistencia_durabilidad','Func_sport_Bolsillos_practicos','Func_sport_Versatilidad']
            func_labels = ['Sujeción','Transpirabilidad','Compresión','Calidad/precio','Secado rápido',
                           'Variedad tallas','Libertad movimiento','Suavidad tejido','Comodidad',
                           'Resistencia','Bolsillos','Versatilidad']
            emoc_cols = ['Emoc_sport_Estetica','Emoc_sport_Moderna','Emoc_sport_Refleja_personalidad',
                         'Emoc_sport_Destaca','Emoc_sport_Identificacion_marca','Emoc_sport_Diseno','Emoc_sport_Marca_especialista']
            emoc_labels = ['Estética','Moderna','Refleja personalidad','Destaca','Identificación marca','Diseño','Marca especialista']

        func_avail = [c for c in func_cols if c in df.columns]
        emoc_avail = [c for c in emoc_cols if c in df.columns]
        func_lab_avail = [func_labels[func_cols.index(c)] for c in func_avail]
        emoc_lab_avail = [emoc_labels[emoc_cols.index(c)] for c in emoc_avail]
        personas_present = [p for p in list(PERSONA_NAMES.values()) if p in df['Buyer_persona'].values]

        attr_tabs = st.tabs(['Funcional — media','Funcional — por perfil','Emocional — media','Emocional — por perfil','Funcional vs Emocional'])

        with attr_tabs[0]:
            func_means = df[func_avail].apply(pd.to_numeric, errors='coerce').mean()
            fig_func = go.Figure(go.Bar(
                x=[float(v) for v in func_means], y=func_lab_avail, orientation='h',
                marker=dict(color=gradient_colors([float(v) for v in func_means]), line=dict(width=0)),
                text=[f'{v:.2f}' for v in func_means], textposition='outside', textfont=dict(size=10,color=FONT),
            ))
            fig_func.update_layout(**lay('Atributos funcionales — valoración media (1–5)', 380),
                xaxis=dict(range=[0,5.5],showgrid=False,showticklabels=False,zeroline=False),
                yaxis=dict(showgrid=False,tickfont=dict(size=11),autorange='reversed'),
            )
            st.plotly_chart(fig_func, use_container_width=True, config=PC)

        with attr_tabs[1]:
            if len(func_avail) >= 3 and len(personas_present) >= 2:
                vals_dict = {p: df[df['Buyer_persona']==p][func_avail].apply(pd.to_numeric,errors='coerce').mean().tolist()
                             for p in personas_present}
                st.plotly_chart(radar_fig(func_lab_avail, vals_dict, title='Atributos funcionales por buyer persona', h=420),
                                use_container_width=True, config=PC)

        with attr_tabs[2]:
            emoc_means = df[emoc_avail].apply(pd.to_numeric, errors='coerce').mean()
            fig_emoc = go.Figure(go.Bar(
                x=[float(v) for v in emoc_means], y=emoc_lab_avail, orientation='h',
                marker=dict(color=gradient_colors([float(v) for v in emoc_means]), line=dict(width=0)),
                text=[f'{v:.2f}' for v in emoc_means], textposition='outside', textfont=dict(size=10,color=FONT),
            ))
            fig_emoc.update_layout(**lay('Atributos emocionales — valoración media (1–5)', 340),
                xaxis=dict(range=[0,5.5],showgrid=False,showticklabels=False,zeroline=False),
                yaxis=dict(showgrid=False,tickfont=dict(size=11),autorange='reversed'),
            )
            st.plotly_chart(fig_emoc, use_container_width=True, config=PC)

        with attr_tabs[3]:
            if len(emoc_avail) >= 3 and len(personas_present) >= 2:
                vals_dict_e = {p: df[df['Buyer_persona']==p][emoc_avail].apply(pd.to_numeric,errors='coerce').mean().tolist()
                               for p in personas_present}
                st.plotly_chart(radar_fig(emoc_lab_avail, vals_dict_e, title='Atributos emocionales por buyer persona', h=380),
                                use_container_width=True, config=PC)

        with attr_tabs[4]:
            # Ranking: qué atributos destacan y cuáles flojean
            all_cols   = func_avail + emoc_avail
            all_labels = func_lab_avail + emoc_lab_avail
            all_types  = ['Funcional']*len(func_avail) + ['Emocional']*len(emoc_avail)
            all_means  = df[all_cols].apply(pd.to_numeric, errors='coerce').mean()

            ranking = pd.DataFrame({
                'Atributo': all_labels,
                'Tipo': all_types,
                'Media': [float(all_means[c]) for c in all_cols],
            }).sort_values('Media', ascending=False)

            n = len(ranking)
            top3 = ranking.head(3)
            bot3 = ranking.tail(3).iloc[::-1]

            c1, c2 = st.columns(2, gap='large')
            with c1:
                st.markdown('<div class="chart-label">Lo más valorado</div>', unsafe_allow_html=True)
                for _, row in top3.iterrows():
                    badge_color = '#2E86AB' if row['Tipo']=='Funcional' else '#E74C3C'
                    pct = (row['Media']-1)/4*100
                    st.markdown(
                        f'<div style="margin-bottom:14px">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">'
                        f'<span style="font-size:.88rem;font-weight:600;color:{FONT}">{row["Atributo"]}</span>'
                        f'<span style="font-size:.7rem;background:{badge_color};color:#fff;padding:2px 8px;border-radius:3px">{row["Tipo"]}</span>'
                        f'</div>'
                        f'<div style="display:flex;align-items:center;gap:10px">'
                        f'<div style="flex:1;background:#EAF2F8;border-radius:4px;height:10px">'
                        f'<div style="width:{pct:.0f}%;background:{badge_color};border-radius:4px;height:10px"></div></div>'
                        f'<span style="font-size:.85rem;font-weight:700;color:{badge_color};min-width:28px">{row["Media"]:.2f}</span>'
                        f'</div></div>',
                        unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="chart-label">Lo menos valorado</div>', unsafe_allow_html=True)
                for _, row in bot3.iterrows():
                    badge_color = '#2E86AB' if row['Tipo']=='Funcional' else '#E74C3C'
                    pct = (row['Media']-1)/4*100
                    st.markdown(
                        f'<div style="margin-bottom:14px">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">'
                        f'<span style="font-size:.88rem;font-weight:600;color:{FONT}">{row["Atributo"]}</span>'
                        f'<span style="font-size:.7rem;background:{badge_color};color:#fff;padding:2px 8px;border-radius:3px">{row["Tipo"]}</span>'
                        f'</div>'
                        f'<div style="display:flex;align-items:center;gap:10px">'
                        f'<div style="flex:1;background:#EAF2F8;border-radius:4px;height:10px">'
                        f'<div style="width:{pct:.0f}%;background:#B0C8D8;border-radius:4px;height:10px"></div></div>'
                        f'<span style="font-size:.85rem;font-weight:700;color:#6A8BA4;min-width:28px">{row["Media"]:.2f}</span>'
                        f'</div></div>',
                        unsafe_allow_html=True)

            # Ranking completo
            st.markdown('<br>', unsafe_allow_html=True)
            fig_rank = go.Figure(go.Bar(
                x=[float(v) for v in ranking['Media']],
                y=list(ranking['Atributo']),
                orientation='h',
                marker=dict(
                    color=['#2E86AB' if t=='Funcional' else '#E74C3C' for t in ranking['Tipo']],
                    line=dict(width=0)
                ),
                text=[f'{v:.2f}' for v in ranking['Media']],
                textposition='outside', textfont=dict(size=10, color=FONT),
            ))
            fig_rank.update_layout(**lay('Todos los atributos — ranking completo', 420),
                xaxis=dict(range=[0,5.5], showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, tickfont=dict(size=10), autorange='reversed'),
            )
            fig_rank.update_layout(showlegend=True,
                legend=dict(orientation='h', y=1.06, x=0,
                            font=dict(size=10),
                            itemsizing='constant'))
            st.plotly_chart(fig_rank, use_container_width=True, config=PC)

    except Exception as e:
        st.error(f'Error Compra: {e}'); st.code(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════════
# TAB 4 — MARCAS
# ═══════════════════════════════════════════════════════════════════
with tab4:
    try:
        section('Análisis de marca y percepción')

        if is_s1:
            bc = [('Top_of_mind_lenceria','Otras_marcas_lenceria','Marcas_donde_compra_lenceria','Lencería'),
                  ('Top_of_mind_bano','Otras_marcas_bano','Marcas_donde_compra_bano','Baño')]
            fc = [c for c in df.columns if c.startswith('Func_lenc')]
            ec = [c for c in df.columns if c.startswith('Emoc_lenc')]
            fl = [c.replace('Func_lenc_','').replace('_',' ') for c in fc]
            el = [c.replace('Emoc_lenc_','').replace('_',' ') for c in ec]
            motivo_cols = [('Marca_favorita_lenceria_motivo','Lencería'),('Marca_favorita_bano_motivo','Baño')]
        else:
            bc = [('Top_of_mind_deporte','Otras_marcas_deporte','Marcas_donde_compra_deporte','Deporte'),
                  ('Top_of_mind_homewear','Otras_marcas_homewear','Marcas_donde_compra_homewear','Homewear')]
            fc = [c for c in df.columns if c.startswith('Func_sport')]
            ec = [c for c in df.columns if c.startswith('Emoc_sport')]
            fl = [c.replace('Func_sport_','').replace('_',' ') for c in fc]
            el = [c.replace('Emoc_sport_','').replace('_',' ') for c in ec]
            motivo_cols = [('Marca_favorita_deporte_motivo','Deporte'),('Marca_favorita_homewear_motivo','Homewear')]

        c1, c2 = st.columns(2, gap='large')
        for col_obj, (tom, otras, usa, lb) in zip([c1,c2], bc):
            with col_obj:
                s = pd.concat([df[tom] if tom in df.columns else pd.Series(dtype=str),
                               df[otras] if otras in df.columns else pd.Series(dtype=str)],
                              ignore_index=True)
                tb = top_mentions(s, 12)
                if not tb.empty:
                    st.plotly_chart(hbar(list(tb['Marca']), list(tb['Menciones']),
                                         gradient=True, title=f'Notoriedad espontánea — {lb}', h=400),
                                    use_container_width=True, config=PC)
                if usa in df.columns:
                    tu = top_mentions(df[usa], 10)
                    if not tu.empty:
                        st.plotly_chart(hbar(list(tu['Marca']), list(tu['Menciones']),
                                             color=P[2], title=f'Dónde compra — {lb}', h=340),
                                        use_container_width=True, config=PC)

        hr()
        section('Atributos — Funcionales y emocionales')
        desglose = st.radio('Desglosar atributos por',
                            ['Total','Grupo de edad','Tipo de persona','CCAA (top 4)'],
                            horizontal=True, key='attr_br')

        def seg_vals(num_df):
            if desglose == 'Total':
                return {'Total': [float(v) for v in num_df.mean().values]}
            elif desglose == 'Grupo de edad':
                return {ag:[float(v) for v in num_df[df['Grupo_edad']==ag].mean().values]
                        for ag in AGES if (df['Grupo_edad']==ag).sum()>4}
            elif desglose == 'Tipo de persona':
                tipos = df['Buyer_persona'].value_counts().index.tolist()[:3]
                return {t:[float(v) for v in num_df[df['Buyer_persona']==t].mean().values]
                        for t in tipos if (df['Buyer_persona']==t).sum()>4}
            else:
                top4 = df['CCAA'].value_counts().head(4).index.tolist()
                return {z:[float(v) for v in num_df[df['CCAA']==z].mean().values]
                        for z in top4 if (df['CCAA']==z).sum()>4}

        c1, c2 = st.columns(2, gap='large')
        with c1:
            if fc:
                fn = df[fc].apply(pd.to_numeric, errors='coerce')
                vd = seg_vals(fn)
                if vd:
                    st.plotly_chart(radar_fig(fl, vd, 'Atributos funcionales'), use_container_width=True, config=PC)
        with c2:
            if ec:
                en = df[ec].apply(pd.to_numeric, errors='coerce')
                vd = seg_vals(en)
                if vd:
                    st.plotly_chart(radar_fig(el, vd, 'Atributos emocionales'), use_container_width=True, config=PC)

        if fc and len(df) > 10:
            hr()
            gm = group_mean(df, fc, 'Grupo_edad', AGES)
            gm.columns = fl
            st.plotly_chart(heatmap_fig(gm.T.round(2), 'Atributos funcionales por grupo de edad', h=360),
                            use_container_width=True, config=PC)

        # Análisis por marca: qué dicen de cada una
        hr()
        section('¿Qué valoran de cada marca?')
        if is_s1:
            brand_lists = [(motivo_cols[0][0], BRANDS_LENC, 'Lencería'),
                           (motivo_cols[1][0], BRANDS_BANO, 'Baño')]
        else:
            brand_lists = [(motivo_cols[0][0], BRANDS_SPORT, 'Deporte'),
                           (motivo_cols[1][0], BRANDS_HOME, 'Homewear')]
        for mc, blist, lb in brand_lists:
            if mc in df.columns and df[mc].dropna().apply(is_meaningful).sum() > 10:
                show_brand_analysis(df[mc], blist, f'{lb} — por qué eligen cada marca')

    except Exception as e:
        st.error(f'Error Marcas: {e}'); st.code(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════════
# TAB 5 — PRODUCTO
# ═══════════════════════════════════════════════════════════════════
with tab5:
    try:
        section('Test de producto · Preferencia por marca')

        # prefijos correctos por categoría para buscar imágenes
        if is_s1:
            prod_pairs = [
                ('Producto_lenceria_elegido','Por_que_gusta_mas_lenc','Por_que_otros_gustan_menos_lenc','Lencería',['lt']),
                ('Producto_bano_elegido','Por_que_gusta_mas_bano','Por_que_otros_gustan_menos_bano','Baño',['st']),
            ]
        else:
            prod_pairs = [
                ('Producto_deporte_elegido','Por_que_gusta_mas_deporte','Por_que_otros_gustan_menos_deporte','Deporte',['spt']),
                ('Producto_homewear_elegido','Por_que_gusta_mas_homewear','Por_que_otros_gustan_menos_homewear','Homewear',['lw']),
            ]

        for pc, wc_pos, wc_neg, lbl, img_prefixes in prod_pairs:
            if pc not in df.columns: continue

            st.markdown(f'<div style="font-family:Montserrat,sans-serif;font-size:1.15rem;font-weight:600;color:#1B2B3B;margin:1.2rem 0 .4rem">— {lbl}</div>', unsafe_allow_html=True)

            raw_cts = Counter()
            for val in df[pc].dropna():
                code = str(val).strip()
                if ':' in code: code = code.split(':',1)[1].strip()
                if code and code!='nan': raw_cts[code] += 1

            brand_cts = Counter({'_s':0,'_a':0,'_b':0})
            for code, n in raw_cts.items():
                for suf in ('_s','_a','_b'):
                    if code.endswith(suf): brand_cts[suf]+=n; break

            total_v = sum(brand_cts.values()) or 1

            # ─ Tarjetas resumen por tipo de marca ─────────────────────────
            brand_order = [
                ('_s','Selmark',          '#1B2B3B','#FFFFFF'),
                ('_a','Comp. aspiracional','#2E86AB','#FFFFFF'),
                ('_b','Comp. accesible',  '#EAF2F8','#1B2B3B'),
            ]
            cols3 = st.columns(3)
            for col_obj,(suf,bname,bg,fg) in zip(cols3, brand_order):
                with col_obj:
                    v = brand_cts[suf]; pv = v/total_v*100
                    st.markdown(
                        f'<div style="background:{bg};color:{fg};border-radius:6px;padding:20px;text-align:center">'
                        f'<div style="font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;opacity:.7;margin-bottom:8px">{bname}</div>'
                        f'<div style="font-family:Montserrat,sans-serif;font-size:2.8rem;font-weight:700;line-height:1">{pv:.0f}%</div>'
                        f'<div style="font-size:.7rem;opacity:.7;margin-top:4px">{v} votos</div>'
                        f'</div>', unsafe_allow_html=True)

            hr()
            # ─ Grid de imágenes por tríada ────────────────────────────────
            st.markdown('<div class="chart-label">Productos por tríada</div>', unsafe_allow_html=True)
            triads = set()
            for code in raw_cts:
                m = re.search(r'(\d+)', code)
                if m: triads.add(int(m.group(1)))

            for t_num in sorted(triads):
                st.markdown(f'<div style="font-size:.7rem;font-weight:600;color:#2E86AB;margin:12px 0 8px;text-transform:uppercase;letter-spacing:.1em">Tríada {t_num}</div>', unsafe_allow_html=True)
                img_cols = st.columns(3)
                triad_prods = []
                for suf in ('_s','_a','_b'):
                    for pre in img_prefixes:
                        cand = f'{pre}{t_num}{suf}'
                        if cand in PROD_IMG:
                            triad_prods.append((cand, suf)); break

                for col_obj,(code,suf) in zip(img_cols, triad_prods):
                    with col_obj:
                        bname,bcol,badge_cls = prod_brand(code)
                        votes = raw_cts.get(code,0)
                        pct_v = votes/total_v*100
                        pimg  = img_path(code)
                        if pimg:
                            import base64
                            with open(pimg,'rb') as f: b64 = base64.b64encode(f.read()).decode()
                            ext = pimg.split('.')[-1].lower()
                            mime = 'image/jpeg' if ext in ('jpg','jpeg') else 'image/png'
                            st.markdown(
                                f'<div class="prod-img-container">'
                                f'<img src="data:{mime};base64,{b64}" />'
                                f'</div>',
                                unsafe_allow_html=True)
                        bg_c = {'_s':'#1B2B3B','_a':'#2E86AB','_b':'#EAF2F8'}[suf]
                        fg_c = '#FFFFFF' if suf != '_b' else '#1B2B3B'
                        st.markdown(
                            f'<div style="background:{bg_c};color:{fg_c};border-radius:4px;'
                            f'padding:8px 12px;text-align:center;margin-top:4px">'
                            f'<div style="font-size:.58rem;letter-spacing:.12em;text-transform:uppercase;opacity:.8">{bname}</div>'
                            f'<div style="font-family:Montserrat,sans-serif;font-size:1.8rem;font-weight:700">{pct_v:.0f}%</div>'
                            f'<div style="font-size:.65rem;opacity:.7">{votes} votos</div>'
                            f'</div>', unsafe_allow_html=True)

            hr()
            # ─ Por grupo de edad ──────────────────────────────────────────
            section('Preferencia por segmento')
            seg_type = st.radio('Ver por', ['Grupo de edad','Tipo de persona','CCAA (top 5)'],
                                horizontal=True, key=f'prod_seg_{lbl}')

            def prod_brand_pcts(sub_df, pc_col):
                ac = Counter({'_s':0,'_a':0,'_b':0})
                for val in sub_df[pc_col].dropna():
                    code = str(val).strip()
                    if ':' in code: code = code.split(':',1)[1].strip()
                    for suf in ('_s','_a','_b'):
                        if code.endswith(suf): ac[suf]+=1
                n = sum(ac.values()) or 1
                return {suf: ac[suf]/n*100 for suf in ('_s','_a','_b')}

            if seg_type == 'Grupo de edad':
                segs = AGES; scol = 'Grupo_edad'
            elif seg_type == 'Tipo de persona':
                segs = df['Buyer_persona'].value_counts().index.tolist()[:4]; scol = 'Buyer_persona'
            else:
                segs = df['CCAA'].value_counts().head(5).index.tolist(); scol = 'CCAA'

            fig_seg = go.Figure()
            bnames = {'_s':'Selmark','_a':'Aspiracional','_b':'Accesible'}
            bcols  = {'_s':P[1],'_a':P[0],'_b':P[3]}
            for suf in ('_s','_a','_b'):
                ys = [prod_brand_pcts(df[df[scol]==s],pc).get(suf,0) for s in segs]
                fig_seg.add_trace(go.Bar(
                    name=bnames[suf], x=segs, y=ys,
                    marker=dict(color=bcols[suf], line=dict(width=0)),
                    text=[f'{v:.0f}%' for v in ys],
                    textposition='inside', textfont=dict(size=10,color='#fff'),
                ))
            fig_seg.update_layout(**lay(f'% elección por {seg_type.lower()} — {lbl}', 310),
                barmode='group',
                legend=dict(orientation='h', y=-0.22, font=dict(size=11)),
                xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False,
                           ticksuffix='%', tickfont=dict(size=10)),
            )
            fig_seg.update_layout(showlegend=True)
            st.plotly_chart(fig_seg, use_container_width=True, config=PC)

            # ─ Text mining motivos ────────────────────────────────────────
            hr()
            section(f'¿Por qué eligen cada producto? — {lbl}')

            # Mining por tipo de marca
            brand_tab = st.tabs(['✦ Selmark','✦ Comp. aspiracional','✦ Comp. accesible',
                                  '✦ Por qué los otros gustan menos'])
            with brand_tab[0]:
                sel_codes = [c for c in raw_cts if c.endswith('_s')]
                sel_mask  = df[pc].apply(lambda v: any(
                    str(v).endswith(c) or (':'in str(v) and str(v).split(':',1)[1].strip()==c)
                    for c in sel_codes))
                if sel_mask.sum() > 5 and wc_pos in df.columns:
                    show_text_mining(df[sel_mask][wc_pos], 'Razones al elegir Selmark')
                else:
                    st.info('Pocas respuestas en este segmento.')

            with brand_tab[1]:
                asc_codes = [c for c in raw_cts if c.endswith('_a')]
                asc_mask  = df[pc].apply(lambda v: any(
                    str(v).endswith(c) or (':'in str(v) and str(v).split(':',1)[1].strip()==c)
                    for c in asc_codes))
                if asc_mask.sum() > 5 and wc_pos in df.columns:
                    show_text_mining(df[asc_mask][wc_pos], 'Razones al elegir Comp. aspiracional')
                else:
                    st.info('Pocas respuestas en este segmento.')

            with brand_tab[2]:
                low_codes = [c for c in raw_cts if c.endswith('_b')]
                low_mask  = df[pc].apply(lambda v: any(
                    str(v).endswith(c) or (':'in str(v) and str(v).split(':',1)[1].strip()==c)
                    for c in low_codes))
                if low_mask.sum() > 5 and wc_pos in df.columns:
                    show_text_mining(df[low_mask][wc_pos], 'Razones al elegir Comp. accesible')
                else:
                    st.info('Pocas respuestas en este segmento.')

            with brand_tab[3]:
                if wc_neg in df.columns:
                    show_text_mining(df[wc_neg], 'Razones de rechazo a los otros productos')

            # Respuestas abiertas completas (expandible)
            c1, c2 = st.columns(2)
            with c1:
                if wc_pos in df.columns:
                    texts = [v for v in df[wc_pos].dropna() if is_meaningful(v)]
                    if texts:
                        with st.expander(f'Ver respuestas — por qué gusta más ({len(texts)})'):
                            for t in texts[:80]:
                                st.markdown(f'<p style="font-size:.8rem;color:#2A3A4A;border-left:3px solid #2E86AB;padding-left:10px;margin:4px 0">{t}</p>', unsafe_allow_html=True)
            with c2:
                if wc_neg in df.columns:
                    texts = [v for v in df[wc_neg].dropna() if is_meaningful(v)]
                    if texts:
                        with st.expander(f'Ver respuestas — por qué gustan menos ({len(texts)})'):
                            for t in texts[:80]:
                                st.markdown(f'<p style="font-size:.8rem;color:#2A3A4A;border-left:3px solid #85C1E9;padding-left:10px;margin:4px 0">{t}</p>', unsafe_allow_html=True)
            hr()

    except Exception as e:
        st.error(f'Error Producto: {e}'); st.code(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════════
# TAB 6 — ESTUDIO CROMÁTICO
# ═══════════════════════════════════════════════════════════════════
with tab6:
    try:
        if is_s1:
            color_pairs = [
                ('Colores_favoritos_lenceria', 'Combinaciones_colores_lenceria', 'Lencería'),
                ('Colores_favoritos_bano',     'Combinaciones_colores_bano',     'Baño'),
            ]
        else:
            color_pairs = [
                ('Colores_favoritos_deporte',  'Combinaciones_colores_deporte',  'Deporte'),
                ('Colores_favoritos_homewear', 'Combinaciones_colores_homewear', 'Homewear'),
            ]

        def parse_hex_colors(series):
            """Extrae todos los hex codes de una serie de strings tipo '#ff0000 | #00ff00'."""
            colors = []
            for val in series.dropna():
                for part in str(val).split('|'):
                    part = part.strip()
                    if part.startswith('#') and len(part) in (7,):
                        colors.append(part.upper())
            return colors

        def parse_combos(series):
            """Extrae combinaciones como listas de hex codes."""
            combos = []
            for val in series.dropna():
                for combo_str in str(val).split('|'):
                    combo_str = combo_str.strip()
                    # formato: Combo1:#rrggbb+#rrggbb+#rrggbb
                    if ':' in combo_str:
                        hex_part = combo_str.split(':',1)[1]
                    else:
                        hex_part = combo_str
                    cols = [c.strip().upper() for c in hex_part.split('+') if c.strip().startswith('#')]
                    if len(cols) >= 2:
                        combos.append(cols)
            return combos

        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2],16) for i in (0,2,4))

        def color_swatch(hex_code, size=36, label=''):
            r,g,b = hex_to_rgb(hex_code)
            lum = 0.299*r + 0.587*g + 0.114*b
            txt_color = '#111' if lum > 140 else '#fff'
            return (f'<div style="display:inline-block;width:{size}px;height:{size}px;'
                    f'background:{hex_code};border-radius:50%;border:2px solid rgba(0,0,0,.12);'
                    f'margin:3px;title="{hex_code}""></div>')

        for col_fav, col_combo, label in color_pairs:
            if col_fav not in df.columns:
                continue
            section(f'Estudio cromático — {label}')

            all_colors = parse_hex_colors(df[col_fav])
            if not all_colors:
                st.info('Sin datos de color.')
                continue

            from collections import Counter as _Counter
            import colorsys as _colorsys
            color_counts = _Counter(all_colors)
            top_colors_raw = color_counts.most_common(20)

            # Ordenar por tono HSL (recorre el espectro: rojo→amarillo→verde→azul→morado)
            def _hue_key(hex_cnt):
                h = hex_cnt[0]
                r,g,b = hex_to_rgb(h)
                hue,sat,val = _colorsys.rgb_to_hsv(r/255,g/255,b/255)
                # Neutros (baja saturación) van al final
                return (0 if sat < 0.12 else 1, hue)

            top_colors = sorted(top_colors_raw, key=_hue_key)

            # ── Paleta de colores más frecuentes (ordenada por tono) ──
            st.markdown('<div class="chart-label">Colores más elegidos · ordenados por tono</div>', unsafe_allow_html=True)
            swatches_html = '<div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:20px">'
            for hex_c, cnt in top_colors:
                r,g,b = hex_to_rgb(hex_c)
                lum = 0.299*r + 0.587*g + 0.114*b
                txt = '#111' if lum > 140 else '#fff'
                swatches_html += (
                    f'<div style="text-align:center">'
                    f'<div style="width:56px;height:56px;background:{hex_c};border-radius:8px;'
                    f'border:1px solid rgba(0,0,0,.1);margin:0 auto 4px"></div>'
                    f'<div style="font-size:.6rem;color:#6A8BA4">{hex_c}</div>'
                    f'<div style="font-size:.65rem;font-weight:600;color:{FONT}">{cnt}×</div>'
                    f'</div>'
                )
            swatches_html += '</div>'
            st.markdown(swatches_html, unsafe_allow_html=True)

            # ── Gráfico de barras top colores (orden por frecuencia para el bar chart) ──
            top_by_freq = sorted(top_colors, key=lambda x: -x[1])[:12]
            top_hex = [h for h,_ in top_by_freq]
            top_cnt = [c for _,c in top_by_freq]
            fig_col = go.Figure(go.Bar(
                x=top_hex, y=top_cnt,
                marker=dict(color=top_hex, line=dict(width=0)),
                text=top_cnt, textposition='outside', textfont=dict(size=10, color=FONT),
            ))
            fig_col.update_layout(**lay('Frecuencia de color', 280),
                xaxis=dict(showgrid=False, tickfont=dict(size=9, color=FONT)),
                yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, showticklabels=False),
            )
            st.plotly_chart(fig_col, use_container_width=True, config=PC)

            # ── Combinaciones más frecuentes ──
            if col_combo in df.columns:
                st.markdown('<div class="chart-label" style="margin-top:16px">Combinaciones más elegidas</div>',
                            unsafe_allow_html=True)
                combos = parse_combos(df[col_combo])
                # Contar combos por su representación canónica
                combo_strs = ['|'.join(c) for c in combos]
                combo_counts = _Counter(combo_strs).most_common(12)

                combo_html = '<div style="display:flex;flex-wrap:wrap;gap:14px;margin-bottom:20px">'
                for combo_key, cnt in combo_counts:
                    hexes = combo_key.split('|')
                    strips = ''.join(
                        f'<div style="flex:1;height:52px;background:{h};min-width:0"></div>'
                        for h in hexes
                    )
                    combo_html += (
                        f'<div style="text-align:center;width:120px">'
                        f'<div style="display:flex;border-radius:6px;overflow:hidden;'
                        f'border:1px solid rgba(0,0,0,.1);margin-bottom:4px">{strips}</div>'
                        f'<div style="font-size:.62rem;color:#6A8BA4">{cnt} encuestadas</div>'
                        f'</div>'
                    )
                combo_html += '</div>'
                st.markdown(combo_html, unsafe_allow_html=True)

            # ── Por buyer persona ──
            with st.expander(f'Ver colores por buyer persona — {label}'):
                p_cols_ui = st.columns(4)
                for idx, persona in enumerate(list(PERSONA_NAMES.values())):
                    sub_p = df[df['Buyer_persona'] == persona]
                    p_colors = parse_hex_colors(sub_p[col_fav]) if len(sub_p) else []
                    top_p = _Counter(p_colors).most_common(8) if p_colors else []
                    with p_cols_ui[idx % 4]:
                        color_h = PERSONA_C.get(persona, '#2E86AB')
                        st.markdown(f'<div style="font-size:.7rem;font-weight:600;color:{color_h};'
                                    f'margin-bottom:6px">{persona}</div>', unsafe_allow_html=True)
                        if top_p:
                            sw = '<div style="display:flex;flex-wrap:wrap;gap:4px">'
                            for hx, _ in top_p:
                                sw += f'<div style="width:28px;height:28px;background:{hx};border-radius:4px;border:1px solid rgba(0,0,0,.1)" title="{hx}"></div>'
                            sw += '</div>'
                            st.markdown(sw, unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="font-size:.7rem;color:#aaa">Sin datos</div>',
                                        unsafe_allow_html=True)

            hr()

    except Exception as e:
        st.error(f'Error Color: {e}'); st.code(traceback.format_exc())
