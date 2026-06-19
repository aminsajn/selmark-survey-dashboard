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
    page_icon=None,
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
                 border-radius:10px; border:1px solid #E5E7EB; box-shadow:0 4px 24px rgba(0,0,0,.08) }
    .login-title { font-family:Montserrat,sans-serif; font-size:1.4rem; font-weight:700;
                   color:#111827; text-align:center; margin-bottom:6px }
    .login-sub { font-size:.75rem; letter-spacing:.12em; text-transform:uppercase;
                 color:#6B7280; text-align:center; margin-bottom:28px }
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
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

#MainMenu, footer, header { visibility: hidden }
[data-testid="stToolbar"] { display: none }
.block-container { padding: 0 2.5rem 3rem !important; max-width: 1440px }

/* Fondo blanco limpio */
.stApp { background: #F8F9FA; color: #111827 }
html, body, [class*="css"] { font-family: 'Inter', sans-serif }

/* Sidebar — fondo gris claro */
[data-testid="stSidebar"] { background: #EBEBED !important; border-right: 1px solid #D8D8DB !important }
[data-testid="stSidebar"] * { color: #111827 !important; font-family: 'Inter', sans-serif !important }

/* Labels de filtros */
[data-testid="stSidebar"] label {
    color: #6B7280 !important;
    font-size: .65rem !important;
    letter-spacing: .1em;
    text-transform: uppercase;
    font-weight: 600 !important;
    margin-bottom: 4px !important;
}

/* Selectbox */
[data-testid="stSidebar"] [data-baseweb="select"] {
    background: #F5F5F7 !important;
    border: 1px solid #C8C8CC !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] * {
    background: #F5F5F7 !important;
    color: #111827 !important;
    font-size: .84rem !important;
}
[data-testid="stSidebar"] [data-baseweb="select"]:focus-within {
    border-color: #0F6FEC !important;
}

/* Radio buttons */
[data-testid="stSidebar"] .stRadio > div { gap: 0 !important }
[data-testid="stSidebar"] [data-baseweb="radio"] {
    padding: 7px 10px !important;
    border-radius: 5px !important;
    margin-bottom: 2px !important;
    transition: background .12s !important;
}
[data-testid="stSidebar"] [data-baseweb="radio"]:hover { background: #DCDCDF !important }
[data-testid="stSidebar"] .stRadio label {
    color: #374151 !important;
    font-size: .85rem !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    font-weight: 400 !important;
}

/* Barra de separación */
[data-testid="stSidebar"] hr { border-color: #D0D0D3 !important; margin: 0 !important }

/* Botón de colapsar — oscuro para contrastar con el sidebar claro */
[data-testid="stSidebarCollapsedControl"] {
    background: #1C1C1E !important;
    border-right: none !important;
}
[data-testid="stSidebarCollapsedControl"] button {
    color: #9CA3AF !important;
    background: transparent !important;
}
[data-testid="stSidebarCollapsedControl"] button:hover {
    color: #F9FAFB !important;
    background: #2C2C2E !important;
}
[data-testid="collapsedControl"] {
    background: #1C1C1E !important;
}
[data-testid="collapsedControl"] button {
    color: #9CA3AF !important;
}

/* Header */
.top-bar {
    background: #ffffff;
    padding: 16px 36px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0 -2.5rem 2rem -2.5rem;
    border-bottom: 1px solid #E5E7EB;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.top-bar img { height: 44px; width: auto; display: block; object-fit: contain; }
.top-center {
    font-size: .7rem;
    letter-spacing: .16em;
    text-transform: uppercase;
    color: #6B7280;
    font-weight: 500;
}

/* Tabs — estilo texto limpio */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid #E5E7EB;
    background: transparent;
    padding: 0 2px;
}
.stTabs [data-baseweb="tab"] {
    font-size: .78rem;
    letter-spacing: .04em;
    color: #6B7280;
    padding: 10px 18px;
    border: none;
    border-bottom: 2px solid transparent;
    background: transparent !important;
    font-weight: 500;
    transition: color .15s;
}
.stTabs [aria-selected="true"] {
    color: #111827 !important;
    border-bottom: 2px solid #0F6FEC !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.8rem }

/* Secciones */
.section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #111827;
    letter-spacing: -.01em;
    margin-bottom: 2px;
}
.section-rule { width: 28px; height: 2px; background: #0F6FEC; border-radius: 2px; margin: 5px 0 16px 0 }

/* KPI cards — sin borde de color, solo sombra */
.kpi-row { display: flex; gap: 12px; margin-bottom: 2rem; flex-wrap: wrap }
.kpi-card {
    background: #ffffff;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 20px 24px;
    flex: 1;
    min-width: 140px;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
    transition: box-shadow .15s;
}
.kpi-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,.08) }
.kpi-label { font-size: .65rem; letter-spacing: .08em; text-transform: uppercase; color: #9CA3AF; margin-bottom: 8px; font-weight: 500 }
.kpi-value { font-size: 2rem; font-weight: 700; color: #111827; line-height: 1; letter-spacing: -.02em }
.kpi-sub { font-size: .7rem; color: #0F6FEC; margin-top: 6px; font-weight: 500 }

/* Etiquetas de gráfico */
.chart-label { font-size: .65rem; letter-spacing: .06em; text-transform: uppercase; color: #9CA3AF; margin-bottom: 8px; font-weight: 500 }
hr { border: none; border-top: 1px solid #F3F4F6; margin: 2rem 0 }

/* Expander */
[data-testid="stExpander"] { border: 1px solid #E5E7EB !important; border-radius: 8px !important; background: #ffffff !important; box-shadow: 0 1px 3px rgba(0,0,0,.04) !important }

/* Cluster chips */
.cluster-chip {
    display: inline-block;
    background: #EFF6FF;
    color: #1D4ED8;
    border-radius: 4px;
    padding: 3px 10px;
    font-size: .7rem;
    margin: 3px 2px;
    font-weight: 500;
}

/* Badges de producto */
.badge-s  { background:#1E3A8A; color:#fff; padding:3px 10px; border-radius:4px; font-size:.62rem; letter-spacing:.06em; text-transform:uppercase; font-weight:600 }
.badge-a  { background:#3B82F6; color:#fff; padding:3px 10px; border-radius:4px; font-size:.62rem; letter-spacing:.06em; text-transform:uppercase; font-weight:600 }
.badge-b  { background:#BAE6FD; color:#0C4A6E; padding:3px 10px; border-radius:4px; font-size:.62rem; letter-spacing:.06em; text-transform:uppercase; font-weight:600 }

/* Imágenes de producto */
.prod-img-container {
    width: 140px;
    height: 186px;
    overflow: hidden;
    border-radius: 8px 8px 0 0;
    border: 1px solid #E5E7EB;
    border-bottom: none;
    background: #F9FAFB;
    margin: 0 auto;
}
.prod-img-container img {
    width: 100%; height: 100%;
    object-fit: cover; object-position: center top; display: block;
}

/* Buyer persona cards — transparente con borde de color */
.persona-card {
    border-radius: 12px;
    padding: 22px 22px 18px;
    margin-bottom: 12px;
    background: #FFFFFF !important;
    border-width: 2px;
    border-style: solid;
    box-shadow: 0 2px 12px rgba(0,0,0,.06);
}
.persona-title { font-size:.95rem; font-weight:700; margin-bottom:4px; letter-spacing:-.01em }
.persona-n { font-size:.68rem; color:#6B7280; margin-bottom:10px }
.persona-desc { font-size:.74rem; color:#374151; margin-bottom:12px; line-height:1.45 }
.persona-tag { display:inline-block; border-width:1px; border-style:solid; border-radius:4px; padding:2px 8px; font-size:.62rem; margin:2px 2px; font-weight:500; background:transparent }
</style>
""", unsafe_allow_html=True)

# ── PALETA ───────────────────────────────────────────────────────────────────
ACCENT = '#0F6FEC'
P      = ['#0F6FEC','#3B82F6','#60A5FA','#93C5FD','#1D4ED8','#2563EB','#BFDBFE','#DBEAFE']
RADAR_C = ['#EF4444','#0F6FEC','#10B981','#F59E0B','#8B5CF6','#06B6D4','#F97316','#374151']
PERSONA_C = {
    'La Aspiracional':             '#8B5CF6',
    'La Tradicional Fiel':         '#EF4444',
    'La Hogareña Práctica':        '#F59E0B',
    'La Exploradora Comprometida': '#10B981',
}
PAPER = '#FFFFFF'
BG    = '#F8F9FA'
FONT  = '#111827'
GRID  = '#F3F4F6'
AGES  = ['18–30','31–45','46+']
# Colores diferenciados para los 3 grupos de edad (no tres azules)
AGE_COLORS = {'18–30': '#0F6FEC', '31–45': '#F59E0B', '46+': '#10B981'}

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
    # ruido / respuestas sin sentido
    'nose','nose nada','jsjsjsjsjjs','jsjsjjsjsjjs','jsjsjsjjsjsjjs','jajajaja','jaja','jeje',
    'jejeje','jajajajaja','hhhh','hhhhh','hahaha','xd','xdd','xddd','lol','lmao',
    'asdf','qwerty','aaa','aaaa','aaaaa','bbb','cccc','dddd','eeee','fff','gggg',
    'hhjff','hhhh','hjhjh','jjjj','kkkk','llll','mmmm','nnnn','pppp','qqqq',
    'sdfs','sdf','sdfsd','asdfg','qweqwe','123','1234','12345','000','111','222',
    'blah','blablabla','bla bla','blabla','nope','nop','nan','none','null',
    'no se que poner','no sé qué poner','no tengo opinion','no tengo nada',
    'sin comentarios','sin nada','da igual','igual','lo mismo','igual da',
    'no lo se','no lo sé nada','pff','pfff','buf','bufffff','meh',
    '...','….',',,','???','!!!','no procede','np','sd','st',
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
    # detectar cadenas de caracteres repetidos (jsjsjsjs, aaaaaaa, etc.)
    if len(t) >= 4:
        unique_chars = set(t.replace(' ',''))
        if len(unique_chars) <= 2 and len(t) >= 6: return False
        # patrón bicarácter repetido (jsjs, ahahah…)
        if re.match(r'^(.{1,2})\1{3,}$', t.replace(' ','')): return False
    return True

def img_path(code):
    rel = PROD_IMG.get(code,'')
    if not rel: return None
    p = os.path.join(IMG_BASE, rel.replace('/', os.sep))
    return p if os.path.exists(p) else None

def prod_brand(code):
    if code.endswith('_s'): return 'Selmark',          '#1E3A8A', 'badge-s'
    if code.endswith('_a'): return 'Comp. aspiracional','#3B82F6', 'badge-a'
    if code.endswith('_b'): return 'Comp. accesible',  '#BAE6FD', 'badge-b'
    return 'Desconocido','#999',''

# ── GRÁFICOS ─────────────────────────────────────────────────────────────────
PC = {'modeBarButtonsToRemove': ['zoom2d','pan2d','select2d','lasso2d','zoomIn2d','zoomOut2d','autoScale2d','resetScale2d','hoverClosestCartesian','hoverCompareCartesian','toggleSpikelines'], 'displaylogo': False, 'displayModeBar': True}

def lay(title='', h=None, showlegend=False, legend=None):
    d = dict(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color=FONT, size=11),
        margin=dict(t=46 if title else 22, b=22, l=8, r=36),
        showlegend=showlegend,
    )
    if legend: d['legend'] = legend
    if title:
        d['title'] = dict(text=f'<b>{title}</b>', font=dict(size=12, color=FONT), x=0, pad=dict(b=6))
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
        colorscale=[[0,'#F3F4F6'],[0.5,'#60A5FA'],[1,'#1D4ED8']],
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
        pct_bar = f'<div style="height:4px;background:#F3F4F6;border-radius:2px;margin:6px 0 8px">' \
                  f'<div style="height:4px;background:#0F6FEC;border-radius:2px;width:{pct:.0f}%"></div></div>'
        ejemplos = ' · '.join(f'<i>"{s[:60]}"</i>' for s in cl['samples'][:2])
        st.markdown(
            f'<div style="background:#fff;border:1px solid #E5E7EB;border-left:4px solid #0F6FEC;'
            f'border-radius:0 6px 6px 0;padding:12px 16px;margin-bottom:10px">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">'
            f'<span style="font-weight:600;font-size:.85rem;color:#111827">{lbl}</span>'
            f'<span style="font-size:.75rem;color:#0F6FEC;font-weight:600">{cl["count"]} respuestas &nbsp;({pct:.0f}%)</span>'
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
            pct_bar = (f'<div style="height:4px;background:#F3F4F6;border-radius:2px;margin:5px 0 7px">'
                       f'<div style="height:4px;background:#0F6FEC;border-radius:2px;width:{min(pct*3,100):.0f}%"></div></div>')
            ejemplo = f'<i>"{r["samples"][0][:80]}"</i>' if r['samples'] else ''
            st.markdown(
                f'<div style="background:#fff;border:1px solid #E5E7EB;border-left:4px solid #1D4ED8;'
                f'border-radius:0 6px 6px 0;padding:10px 14px;margin-bottom:8px">'
                f'<div style="display:flex;justify-content:space-between;align-items:center">'
                f'<span style="font-weight:700;font-size:.9rem;color:#111827">{r["brand"]}</span>'
                f'<span style="font-size:.72rem;color:#0F6FEC;font-weight:600">{r["count"]} menciones</span>'
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
                        colorscale=[[0,'#EBF5FB'],[0.15,'#93C5FD'],[0.5,'#0F6FEC'],[1,'#111827']],
                        showscale=True, sizemode='diameter',
                        colorbar=dict(thickness=10, len=0.5, title=dict(text='n', font=dict(size=9)))),
            hovertext=texts, hoverinfo='text', customdata=names,
        ))
        fig.update_geos(scope='europe', center=dict(lat=40.4, lon=-3.7),
                        projection_scale=5.5, showland=True, landcolor='#F0F4F8',
                        showcoastlines=True, coastlinecolor='#B0C8D8',
                        showocean=True, oceancolor='#F3F4F6', showframe=False)
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
        [0.6,  '#0F6FEC'],   # alto
        [1.0,  '#111827'],   # máximo
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
  <text x="4" y="36" font-family="Georgia,serif" font-size="30" font-weight="700" fill="#111827" letter-spacing="-0.5">selmark</text>
  <text x="64" y="48" font-family="Arial,sans-serif" font-size="8" font-weight="400" fill="#6B7280" letter-spacing="3">LINGERIE</text>
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
<div style="padding:28px 20px 20px">
  <div style="font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;color:#9CA3AF;margin-bottom:8px">Research 2025</div>
  <div style="font-size:1.25rem;font-weight:700;color:#111827;letter-spacing:-.02em;line-height:1.2">Consumer<br>Insights</div>
  <div style="width:24px;height:2px;background:#0F6FEC;border-radius:2px;margin-top:12px"></div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="padding:0 20px 6px">
  <div style="font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:#9CA3AF;margin-bottom:10px;font-weight:600">Colección</div>
</div>
""", unsafe_allow_html=True)

survey_sel = st.sidebar.radio('', ['Lencería & Baño', 'Deporte & Homewear'],
                               label_visibility='collapsed')
is_s1  = survey_sel == 'Lencería & Baño'
df_all = enrich(s1_raw if is_s1 else s2_raw)

st.sidebar.markdown("""
<div style="height:1px;background:#D0D0D3;margin:18px 0 20px"></div>
<div style="padding:0 20px 8px">
  <div style="font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:#9CA3AF;margin-bottom:14px;font-weight:600">Filtros</div>
</div>
""", unsafe_allow_html=True)

age_opts = ['Todos los grupos'] + AGES
age_f    = st.sidebar.selectbox('Grupo de edad', age_opts)

ccaa_opts = ['Todas las CCAA'] + sorted(df_all['CCAA'].dropna().unique().tolist())
geo_f     = st.sidebar.selectbox('Comunidad autónoma', ccaa_opts)

persona_opts = ['Todos los perfiles'] + list(PERSONA_NAMES.values())
tipo_f       = st.sidebar.selectbox('Perfil de compradora', persona_opts)

mask = pd.Series(True, index=df_all.index)
if age_f  != 'Todos los grupos':   mask &= df_all['Grupo_edad']    == age_f
if geo_f  != 'Todas las CCAA':     mask &= df_all['CCAA']          == geo_f
if tipo_f != 'Todos los perfiles': mask &= df_all['Buyer_persona'] == tipo_f
df = df_all[mask].copy()

n_active = sum([age_f != 'Todos los grupos', geo_f != 'Todas las CCAA', tipo_f != 'Todos los perfiles'])
filter_tag = f'<span style="background:#0F6FEC;color:#fff;font-size:.58rem;padding:1px 6px;border-radius:10px;margin-left:6px;font-weight:600">{n_active}</span>' if n_active else ''

st.sidebar.markdown(f"""
<div style="height:1px;background:#D0D0D3;margin:24px 0 0"></div>
<div style="padding:18px 20px 12px">
  <div style="font-size:2rem;font-weight:700;color:#111827;letter-spacing:-.03em;line-height:1">{len(df):,}</div>
  <div style="font-size:.65rem;color:#9CA3AF;margin-top:4px">encuestadas seleccionadas</div>
  {'<div style="margin-top:10px;font-size:.65rem;color:#0F6FEC;font-weight:500">' + str(n_active) + ' filtro' + ('s' if n_active!=1 else '') + ' activo' + ('s' if n_active!=1 else '') + '</div>' if n_active else ''}
</div>
<div style="padding:0 20px 32px">
  <div style="font-size:.58rem;color:#C4C4C8;letter-spacing:.04em">Selmark · Minsait Analytics</div>
</div>
""", unsafe_allow_html=True)

lbl = 'Lencería & Baño' if is_s1 else 'Deporte & Homewear'

tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8 = st.tabs(['  Perfil  ','  Lifestyle  ','  Compra  ','  Marcas  ','  Producto  ','  Color  ','  Canales & Influencers  ','  Estrategia  '])

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
                '<p style="font-size:.82rem;color:#6B7280;max-width:800px;margin-bottom:1.4rem">'
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
                    col_hex = PERSONA_C.get(pname,'#0F6FEC')
                    _pd = PERSONA_DESCS.get(pname, ('', []))
                    desc, tags = _pd[0], _pd[1]
                    tag_html = ''.join(
                        f'<span class="persona-tag" style="color:{col_hex};border-color:{col_hex}20">{t}</span>'
                        for t in tags)
                    st.markdown(
                        f'<div class="persona-card" style="border-color:{col_hex}">'
                        f'<div class="persona-title" style="color:{col_hex}">{pname}</div>'
                        f'<div class="persona-n">{n} encuestadas · {pct_p:.0f}%</div>'
                        f'<div class="persona-desc">{desc}</div>'
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

            # ── Perfil socioeconómico por buyer persona ──────────────────
            hr()
            section('Perfil socioeconómico × buyer persona')
            renta_short_p = {
                'Menos de 20.000 €':'<20K€','20.000 – 35.000 € (medio-bajo)':'20–35K€',
                '35.000 – 55.000 € (medio)':'35–55K€','55.000 – 75.000 € (medio-alto)':'55–75K€',
                'Más de 75.000 € (alto)':'>75K€',
            }
            renta_ord_p = ['<20K€','20–35K€','35–55K€','55–75K€','>75K€']
            df['_renta_bp'] = df['Renta_anual_hogar'].map(renta_short_p)

            c1, c2 = st.columns(2, gap='large')
            with c1:
                # Distribución de renta por persona — % apilado
                cross_rp = pd.crosstab(df['Buyer_persona'], df['_renta_bp'])
                cross_rp = cross_rp.reindex(
                    index=[p for p in p_order if p in cross_rp.index],
                    columns=[r for r in renta_ord_p if r in cross_rp.columns]).fillna(0)
                pct_rp = (cross_rp.div(cross_rp.sum(axis=1).replace(0,1), axis=0)*100).round(1)
                if not pct_rp.empty:
                    renta_colors_p = ['#DBEAFE','#93C5FD','#3B82F6','#1D4ED8','#1E3A8A']
                    fig_rp = go.Figure()
                    for i, renta in enumerate(pct_rp.columns):
                        fig_rp.add_trace(go.Bar(
                            name=renta, x=pct_rp.index.tolist(), y=pct_rp[renta].tolist(),
                            marker=dict(color=renta_colors_p[i % len(renta_colors_p)], line=dict(width=0)),
                        ))
                    fig_rp.update_layout(**lay('Distribución de renta por buyer persona (%)', 320,
                        showlegend=True, legend=dict(orientation='h', y=1.08, x=0, font=dict(size=10))),
                        barmode='stack',
                        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
                        yaxis=dict(showgrid=True, gridcolor=GRID, ticksuffix='%'),
                    )
                    st.plotly_chart(fig_rp, use_container_width=True, config=PC)

            with c2:
                # Edad media y renta media por persona
                edad_renta = []
                for pname in p_order:
                    sub_p = df[df['Buyer_persona'] == pname]
                    edad_m = sub_p['Edad'].mean() if 'Edad' in sub_p.columns else np.nan
                    # renta numérica aproximada
                    renta_map_n = {'<20K€':10,'20–35K€':27,'35–55K€':45,'55–75K€':65,'>75K€':85}
                    renta_num = sub_p['_renta_bp'].map(renta_map_n).mean()
                    edad_renta.append({'Perfil': pname.replace('La ',''), 'Edad media': round(edad_m,1),
                                       'Renta media (K€)': round(renta_num,1)})
                df_er = pd.DataFrame(edad_renta)
                if not df_er.empty:
                    fig_er = go.Figure()
                    for _, row in df_er.iterrows():
                        col_p = PERSONA_C.get('La ' + row['Perfil'], P[0])
                        fig_er.add_trace(go.Scatter(
                            x=[row['Edad media']], y=[row['Renta media (K€)']],
                            mode='markers+text',
                            marker=dict(color=col_p, size=18, line=dict(width=2, color='white')),
                            text=[row['Perfil']], textposition='top center',
                            textfont=dict(size=9, color=FONT),
                            name=row['Perfil'],
                        ))
                    fig_er.update_layout(**lay('Edad media vs. Renta media por buyer persona', 320),
                        xaxis=dict(title='Edad media', showgrid=True, gridcolor=GRID, tickfont=dict(size=10)),
                        yaxis=dict(title='Renta media (K€)', showgrid=True, gridcolor=GRID, tickfont=dict(size=10)),
                    )
                    st.plotly_chart(fig_er, use_container_width=True, config=PC)

            df.drop(columns=['_renta_bp'], inplace=True, errors='ignore')

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
                        if lb == 'Baño':
                            item = item.replace(
                                'Tienda multimarca especializada en lencería',
                                'Tienda multimarca especializada en baño')
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

        # Motivos y barreras — opciones cerradas → frecuencia de respuesta
        hr()
        section('Motivos y barreras de compra')
        st.markdown('<p style="font-size:.82rem;color:#6B7280;max-width:900px;margin-bottom:1rem">'
                    'Opciones de respuesta cerrada. Se muestra cuántas encuestadas seleccionaron cada opción '
                    '(una encuestada puede marcar varias).</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2, gap='large')

        def freq_closed_opts(series, title, color):
            from collections import Counter as _C
            cts = _C()
            n_resp = 0
            for val in series.dropna():
                opts = [o.strip() for o in str(val).split('|') if o.strip()]
                if opts:
                    n_resp += 1
                    for o in opts:
                        cts[o] += 1
            if not cts: return
            items = sorted(cts.items(), key=lambda x: x[1], reverse=True)
            labels, vals = zip(*items)
            pcts = [v/n_resp*100 for v in vals]
            labels_r = list(labels)[::-1]; pcts_r = list(pcts)[::-1]; vals_r = list(vals)[::-1]
            h = max(300, len(labels_r) * 32 + 80)
            fig = go.Figure(go.Bar(
                y=labels_r, x=vals_r, orientation='h',
                marker=dict(color=color, line=dict(width=0)),
                text=[f'{p:.0f}%' for p in pcts_r],
                textposition='outside', textfont=dict(size=10, color=FONT),
            ))
            fig.update_layout(**lay(title, h),
                xaxis=dict(showgrid=False, showticklabels=False,
                           range=[0, max(vals_r)*1.35] if vals_r else [0,10], zeroline=False),
                yaxis=dict(showgrid=False, tickfont=dict(size=10)),
            )
            st.plotly_chart(fig, use_container_width=True, config=PC)

        with c1:
            if 'Motivos_compra_ropa' in df.columns:
                freq_closed_opts(df['Motivos_compra_ropa'], 'Motivos de compra (% de encuestadas)', P[0])
        with c2:
            if 'Factores_frenan_compra' in df.columns:
                freq_closed_opts(df['Factores_frenan_compra'], 'Barreras de compra (% de encuestadas)', '#EF4444')

        # ── HOMEWEAR — LIFESTYLE EN CASA ────────────────────────────
        if not is_s1:
            hr()
            section('Homewear · Perfil de uso en casa')
            st.markdown('<p style="font-size:.82rem;color:#6B7280;max-width:900px;margin-bottom:1rem">'
                        'Análisis del contexto de uso de ropa de casa: oficina vs. teletrabajo, '
                        'si se reserva ropa exclusiva para casa, qué tipo de prendas prefiere y '
                        'comportamiento con los recados.</p>', unsafe_allow_html=True)

            hw_cols1 = st.columns(3, gap='large')

            # Teletrabajo vs oficina
            with hw_cols1[0]:
                if 'Dic_Teletrabajo_vs_Oficina' in df.columns:
                    vc_tw = df['Dic_Teletrabajo_vs_Oficina'].value_counts()
                    if not vc_tw.empty:
                        fig_tw = go.Figure(go.Bar(
                            x=list(vc_tw.index), y=list(vc_tw.values),
                            marker=dict(color=[P[0], P[3]], line=dict(width=0)),
                            text=list(vc_tw.values), textposition='outside',
                            textfont=dict(size=11, color=FONT),
                        ))
                        fig_tw.update_layout(**lay('Entorno de trabajo', 260),
                            xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                            yaxis=dict(showgrid=False, showticklabels=False),
                        )
                        st.plotly_chart(fig_tw, use_container_width=True, config=PC)

            # Ropa exclusiva para casa
            with hw_cols1[1]:
                if 'Ropa_exclusiva_para_casa' in df.columns:
                    vc_re = df['Ropa_exclusiva_para_casa'].value_counts()
                    if not vc_re.empty:
                        fig_re = go.Figure(go.Bar(
                            x=list(vc_re.index), y=list(vc_re.values),
                            marker=dict(color=[P[0], '#E5E7EB'], line=dict(width=0)),
                            text=list(vc_re.values), textposition='outside',
                            textfont=dict(size=11, color=FONT),
                        ))
                        fig_re.update_layout(**lay('¿Ropa exclusiva para casa?', 260),
                            xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                            yaxis=dict(showgrid=False, showticklabels=False),
                        )
                        st.plotly_chart(fig_re, use_container_width=True, config=PC)

            # Le molesta cambiarse para recados
            with hw_cols1[2]:
                if 'Molesta_cambiarse_recados' in df.columns:
                    vc_mc = df['Molesta_cambiarse_recados'].value_counts()
                    if not vc_mc.empty:
                        fig_mc = go.Figure(go.Bar(
                            x=list(vc_mc.index), y=list(vc_mc.values),
                            marker=dict(color=[P[0], '#E5E7EB'], line=dict(width=0)),
                            text=list(vc_mc.values), textposition='outside',
                            textfont=dict(size=11, color=FONT),
                        ))
                        fig_mc.update_layout(**lay('¿Le molesta cambiarse para recados?', 260),
                            xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                            yaxis=dict(showgrid=False, showticklabels=False),
                        )
                        st.plotly_chart(fig_mc, use_container_width=True, config=PC)

            hw_cols2 = st.columns(2, gap='large')

            # Durabilidad buscada
            with hw_cols2[0]:
                if 'Duracion_buscada' in df.columns:
                    vc_dur = df['Duracion_buscada'].value_counts()
                    if not vc_dur.empty:
                        labels_r = list(vc_dur.index)[::-1]
                        vals_r   = list(vc_dur.values)[::-1]
                        fig_dur = go.Figure(go.Bar(
                            y=labels_r, x=vals_r, orientation='h',
                            marker=dict(color=P[0], line=dict(width=0)),
                            text=vals_r, textposition='outside',
                            textfont=dict(size=10, color=FONT),
                        ))
                        fig_dur.update_layout(**lay('Durabilidad buscada en homewear', 260),
                            xaxis=dict(showgrid=False, showticklabels=False,
                                       range=[0, max(vals_r)*1.3] if vals_r else [0,10], zeroline=False),
                            yaxis=dict(showgrid=False, tickfont=dict(size=10)),
                        )
                        st.plotly_chart(fig_dur, use_container_width=True, config=PC)

            # Tipo de prendas para casa (texto abierto → frecuencia normalizada)
            with hw_cols2[1]:
                if 'Tipo_prendas_para_casa' in df.columns:
                    from collections import Counter as _C
                    tipo_cts = _C()
                    for val in df['Tipo_prendas_para_casa'].dropna():
                        t = clean_text(val)
                        if t and len(t) > 2:
                            # normalizar variantes comunes
                            t = t.replace('chandal','chándal').replace('chandalc','chándal')
                            tipo_cts[t.title()] += 1
                    if tipo_cts:
                        top_tipo = tipo_cts.most_common(10)
                        labels_r = [x[0] for x in top_tipo][::-1]
                        vals_r   = [x[1] for x in top_tipo][::-1]
                        fig_tipo = go.Figure(go.Bar(
                            y=labels_r, x=vals_r, orientation='h',
                            marker=dict(color=P[2], line=dict(width=0)),
                            text=vals_r, textposition='outside',
                            textfont=dict(size=10, color=FONT),
                        ))
                        fig_tipo.update_layout(**lay('Tipo de prenda preferida en casa', 300),
                            xaxis=dict(showgrid=False, showticklabels=False,
                                       range=[0, max(vals_r)*1.3] if vals_r else [0,10], zeroline=False),
                            yaxis=dict(showgrid=False, tickfont=dict(size=10)),
                        )
                        st.plotly_chart(fig_tipo, use_container_width=True, config=PC)

            # Cruce: Teletrabajo × Ropa exclusiva para casa × Grupo de edad
            if all(c in df.columns for c in ['Dic_Teletrabajo_vs_Oficina','Ropa_exclusiva_para_casa']):
                hr()
                st.markdown('<div class="chart-label">Perfil de uso — cruce entorno laboral × ropa exclusiva para casa</div>',
                            unsafe_allow_html=True)
                cross_hw = pd.crosstab(df['Dic_Teletrabajo_vs_Oficina'],
                                       df['Ropa_exclusiva_para_casa'])
                pct_hw = cross_hw.div(cross_hw.sum(axis=1).replace(0,1), axis=0) * 100
                fig_hw_cross = go.Figure()
                for col_name in pct_hw.columns:
                    fig_hw_cross.add_trace(go.Bar(
                        name=str(col_name),
                        x=pct_hw.index.tolist(),
                        y=pct_hw[col_name].tolist(),
                        marker=dict(color=P[0] if str(col_name).startswith('S') else '#E5E7EB',
                                    line=dict(width=0)),
                        text=[f'{v:.0f}%' for v in pct_hw[col_name]],
                        textposition='inside', textfont=dict(size=11),
                    ))
                fig_hw_cross.update_layout(**lay('', 260,
                    showlegend=True, legend=dict(orientation='h', y=1.06, x=0, font=dict(size=10))),
                    barmode='stack',
                    xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                    yaxis=dict(showgrid=True, gridcolor=GRID, ticksuffix='%'),
                )
                st.plotly_chart(fig_hw_cross, use_container_width=True, config=PC)

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
            fig.add_hline(y=pct_media, line_dash='dot', line_color='#6B7280', line_width=1.5,
                          annotation_text=f'Media {pct_media:.0f}%', annotation_position='top right',
                          annotation_font=dict(size=9, color='#6B7280'))
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

        st.markdown('<div style="font-size:.68rem;color:#6B7280;margin-top:4px">'
                    '🔴 >25% · 🟠 15–25% · 🟡 8–15% · 🟢 <8% de dificultad · Solo tallas con n≥10 respuestas · '
                    'Línea punteada = media de la muestra</div>', unsafe_allow_html=True)

        # ── DISTRIBUCIÓN DE TALLAS — ¿cuántas son tallas grandes? ───
        hr()
        section('Distribución de tallas · Peso real de tallas grandes')
        st.markdown('<p style="font-size:.82rem;color:#6B7280;max-width:800px;margin-bottom:.8rem">'
                    'Tamaño real de las clientas: quién tiene tallas "difíciles" de encontrar y qué peso '
                    'representa en la base de consumidoras.</p>', unsafe_allow_html=True)
        TALLAS_GRANDES_PANT = {'44','46','48','50','52','54','56','XL','XXL','XXXL','3XL','4XL'}
        TALLAS_GRANDES_CAM  = {'XL','XXL','XXXL','3XL','4XL','46','48','50'}
        TALLAS_GRANDES_SUJ  = {'E','F','G','H','90','95','100','105'}  # contornos o copas grandes

        talla_grande_cols = [
            ('Talla_pantalon',  TALLAS_GRANDES_PANT, 'Pantalón — tallas grandes (≥44/XL)'),
            ('Talla_camiseta',  TALLAS_GRANDES_CAM,  'Camiseta — tallas grandes (≥XL)'),
            ('Talla_sujetador', TALLAS_GRANDES_SUJ,  'Sujetador — copa/contorno grande'),
        ]
        tg_cols_ui = st.columns(len(talla_grande_cols))
        for col_obj, (tcol, tg_set, tlabel) in zip(tg_cols_ui, talla_grande_cols):
            if tcol not in df.columns: continue
            def norm_t(v):
                v2 = str(v).strip().upper()
                # extraer número si viene como "42 (M)" etc.
                m = re.search(r'\d{2,3}', v2)
                num = m.group(0) if m else ''
                return v2, num
            _skip = {'0','NO USO','NINGUNA','NO LLEVO','NAN','NONE',''}
            total_v = df[tcol].dropna().apply(lambda x: str(x).strip())
            total_v = total_v[~total_v.str.upper().isin(_skip)]
            grandes = total_v[total_v.apply(lambda x: any(
                g.upper() in str(x).upper() for g in tg_set))]
            n_g = len(grandes); n_t = len(total_v) or 1; pct_g = n_g/n_t*100
            # distribución completa de tallas
            vc_t = total_v.apply(lambda x: str(x).strip().upper()).value_counts().head(12)
            with col_obj:
                st.markdown(
                    f'<div style="background:#F8F9FA;border:1px solid #E5E7EB;border-radius:8px;'
                    f'padding:14px;margin-bottom:12px;text-align:center">'
                    f'<div style="font-size:.65rem;color:#6B7280;text-transform:uppercase;letter-spacing:.1em">{tlabel}</div>'
                    f'<div style="font-size:2rem;font-weight:700;color:#1E3A8A;line-height:1.1">{pct_g:.0f}%</div>'
                    f'<div style="font-size:.7rem;color:#6B7280">{n_g} de {n_t} encuestadas</div>'
                    f'</div>',
                    unsafe_allow_html=True)
                if not vc_t.empty:
                    fig_t2 = go.Figure(go.Bar(
                        x=list(vc_t.index), y=list(vc_t.values),
                        marker=dict(
                            color=['#EF4444' if any(g in str(k) for g in tg_set) else '#93C5FD'
                                   for k in vc_t.index],
                            line=dict(width=0)),
                        text=list(vc_t.values), textposition='outside',
                        textfont=dict(size=9, color=FONT),
                    ))
                    fig_t2.update_layout(**lay(f'Distribución {tlabel.split("—")[0].strip()}', 260),
                        xaxis=dict(showgrid=False, tickfont=dict(size=9)),
                        yaxis=dict(showgrid=False, showticklabels=False),
                    )
                    st.plotly_chart(fig_t2, use_container_width=True, config=PC)

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
            # ordenar descendente
            func_sorted = func_means.sort_values(ascending=True)
            func_labels_sorted = [func_lab_avail[func_avail.index(c)] for c in func_sorted.index]
            fig_func = go.Figure(go.Bar(
                x=[float(v) for v in func_sorted], y=func_labels_sorted, orientation='h',
                marker=dict(color=gradient_colors([float(v) for v in func_sorted]), line=dict(width=0)),
                text=[f'{v:.2f}' for v in func_sorted], textposition='outside', textfont=dict(size=10,color=FONT),
            ))
            fig_func.update_layout(**lay('Atributos funcionales — valoración media (1–5)', 380),
                xaxis=dict(range=[0,5.5],showgrid=False,showticklabels=False,zeroline=False),
                yaxis=dict(showgrid=False,tickfont=dict(size=11)),
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
            emoc_sorted = emoc_means.sort_values(ascending=True)
            emoc_labels_sorted = [emoc_lab_avail[emoc_avail.index(c)] for c in emoc_sorted.index]
            fig_emoc = go.Figure(go.Bar(
                x=[float(v) for v in emoc_sorted], y=emoc_labels_sorted, orientation='h',
                marker=dict(color=gradient_colors([float(v) for v in emoc_sorted]), line=dict(width=0)),
                text=[f'{v:.2f}' for v in emoc_sorted], textposition='outside', textfont=dict(size=10,color=FONT),
            ))
            fig_emoc.update_layout(**lay('Atributos emocionales — valoración media (1–5)', 340),
                xaxis=dict(range=[0,5.5],showgrid=False,showticklabels=False,zeroline=False),
                yaxis=dict(showgrid=False,tickfont=dict(size=11)),
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
                    badge_color = '#0F6FEC' if row['Tipo']=='Funcional' else '#E74C3C'
                    pct = (row['Media']-1)/4*100
                    st.markdown(
                        f'<div style="margin-bottom:14px">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">'
                        f'<span style="font-size:.88rem;font-weight:600;color:{FONT}">{row["Atributo"]}</span>'
                        f'<span style="font-size:.7rem;background:{badge_color};color:#fff;padding:2px 8px;border-radius:3px">{row["Tipo"]}</span>'
                        f'</div>'
                        f'<div style="display:flex;align-items:center;gap:10px">'
                        f'<div style="flex:1;background:#F3F4F6;border-radius:4px;height:10px">'
                        f'<div style="width:{pct:.0f}%;background:{badge_color};border-radius:4px;height:10px"></div></div>'
                        f'<span style="font-size:.85rem;font-weight:700;color:{badge_color};min-width:28px">{row["Media"]:.2f}</span>'
                        f'</div></div>',
                        unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="chart-label">Lo menos valorado</div>', unsafe_allow_html=True)
                for _, row in bot3.iterrows():
                    badge_color = '#0F6FEC' if row['Tipo']=='Funcional' else '#E74C3C'
                    pct = (row['Media']-1)/4*100
                    st.markdown(
                        f'<div style="margin-bottom:14px">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">'
                        f'<span style="font-size:.88rem;font-weight:600;color:{FONT}">{row["Atributo"]}</span>'
                        f'<span style="font-size:.7rem;background:{badge_color};color:#fff;padding:2px 8px;border-radius:3px">{row["Tipo"]}</span>'
                        f'</div>'
                        f'<div style="display:flex;align-items:center;gap:10px">'
                        f'<div style="flex:1;background:#F3F4F6;border-radius:4px;height:10px">'
                        f'<div style="width:{pct:.0f}%;background:#B0C8D8;border-radius:4px;height:10px"></div></div>'
                        f'<span style="font-size:.85rem;font-weight:700;color:#6B7280;min-width:28px">{row["Media"]:.2f}</span>'
                        f'</div></div>',
                        unsafe_allow_html=True)

            # Ranking completo — dos trazas para que la leyenda funcione
            st.markdown('<br>', unsafe_allow_html=True)
            rank_func = ranking[ranking['Tipo']=='Funcional']
            rank_emoc = ranking[ranking['Tipo']=='Emocional']
            fig_rank = go.Figure()
            fig_rank.add_trace(go.Bar(
                name='Funcional',
                x=[float(v) for v in rank_func['Media']], y=list(rank_func['Atributo']),
                orientation='h',
                marker=dict(color='#0F6FEC', line=dict(width=0)),
                text=[f'{v:.2f}' for v in rank_func['Media']],
                textposition='outside', textfont=dict(size=10, color=FONT),
            ))
            fig_rank.add_trace(go.Bar(
                name='Emocional',
                x=[float(v) for v in rank_emoc['Media']], y=list(rank_emoc['Atributo']),
                orientation='h',
                marker=dict(color='#E74C3C', line=dict(width=0)),
                text=[f'{v:.2f}' for v in rank_emoc['Media']],
                textposition='outside', textfont=dict(size=10, color=FONT),
            ))
            fig_rank.update_layout(**lay('Todos los atributos — ranking completo', 420,
                showlegend=True, legend=dict(orientation='h', y=1.06, x=0, font=dict(size=10))),
                xaxis=dict(range=[0,5.5], showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, tickfont=dict(size=10), autorange='reversed'),
                barmode='overlay',
            )
            st.plotly_chart(fig_rank, use_container_width=True, config=PC)

        # ── ANÁLISIS ACTIVIDAD DEPORTIVA (solo S2) ──────────────────
        if not is_s1:
            hr()
            section('Actividad deportiva · Quién, qué y cuánto')

            def norm_num(v):
                try:
                    s = str(v).split('-')[0].split('a')[0].strip()
                    s = re.sub(r'[^\d.]','',s)
                    return float(s) if s else np.nan
                except: return np.nan

            # Frecuencia semanal
            c1, c2 = st.columns(2, gap='large')
            with c1:
                veces_num = df['Veces_deporte_semana'].map(norm_num).dropna()
                if len(veces_num) > 10:
                    buckets_v = pd.cut(veces_num,
                                       bins=[-0.1,0,1,2,3,5,100],
                                       labels=['0 (no practica)','1 vez','2 veces','3 veces','4–5 veces','6+ veces'])
                    vc_v = buckets_v.value_counts().reindex(
                        ['0 (no practica)','1 vez','2 veces','3 veces','4–5 veces','6+ veces']).dropna()
                    st.plotly_chart(hbar(list(vc_v.index), list(vc_v.values),
                                         gradient=True, title='Frecuencia semanal de deporte', h=280),
                                    use_container_width=True, config=PC)

            with c2:
                # Tipo de deporte — normalización básica
                DEPORTE_NORM = {
                    'pilates':'Pilates','pilate':'Pilates','pilatis':'Pilates',
                    'yoga':'Yoga',
                    'running':'Running','correr':'Running','carrera':'Running','run':'Running',
                    'natacion':'Natación','natación':'Natación','nadar':'Natación',
                    'gimnasio':'Gimnasio','gym':'Gimnasio','musculacion':'Gimnasio',
                    'senderismo':'Senderismo','trekking':'Senderismo','hiking':'Senderismo',
                    'ciclismo':'Ciclismo','bici':'Ciclismo','bicicleta':'Ciclismo','spinning':'Ciclismo',
                    'padel':'Pádel','pádel':'Pádel','paddle':'Pádel',
                    'tenis':'Tenis',
                    'crossfit':'CrossFit','cross fit':'CrossFit',
                    'baile':'Baile/Danza','zumba':'Baile/Danza','danza':'Baile/Danza',
                    'futbol':'Fútbol','fútbol':'Fútbol','football':'Fútbol',
                    'calistenia':'Calistenia',
                    'ninguno':'— ninguno —','ninguna':'— ninguno —','no hago':'— ninguno —','no practico':'— ninguno —',
                }
                dep_cts = Counter()
                for val in df['Deporte_que_realiza'].dropna():
                    parts = re.split(r'[,;y/]', str(val).lower())
                    for part in parts:
                        part = part.strip()
                        matched = False
                        for key, label in DEPORTE_NORM.items():
                            if key in part:
                                dep_cts[label] += 1; matched = True; break
                        if not matched and len(part) > 3 and is_meaningful(part):
                            dep_cts[part.title()] += 1

                dep_cts.pop('— ninguno —', None)
                if dep_cts:
                    top_dep = pd.DataFrame(dep_cts.most_common(12), columns=['Deporte','N'])
                    st.plotly_chart(hbar(list(top_dep['Deporte']), list(top_dep['N']),
                                         gradient=True, title='Tipos de deporte practicado', h=380),
                                    use_container_width=True, config=PC)

            # Deporte × edad: ¿quién practica qué?
            hr()
            st.markdown('<div class="chart-label">Deporte más practicado por grupo de edad</div>',
                        unsafe_allow_html=True)

            dep_records = []
            for _, row in df.iterrows():
                ge = row.get('Grupo_edad')
                dep_str = str(row.get('Deporte_que_realiza',''))
                if not ge or not dep_str: continue
                parts = re.split(r'[,;y/]', dep_str.lower())
                for part in parts:
                    part = part.strip()
                    for key, label in DEPORTE_NORM.items():
                        if key in part and label != '— ninguno —':
                            dep_records.append({'GE': ge, 'Deporte': label}); break

            if dep_records:
                dep_df = pd.DataFrame(dep_records)
                top6_dep = dep_df['Deporte'].value_counts().head(7).index.tolist()
                dep_age_cts = {}
                for age in AGES:
                    sub_a = dep_df[dep_df['GE'] == age]
                    n_age = (df['Grupo_edad'] == age).sum() or 1
                    dep_age_cts[age] = {d: sub_a[sub_a['Deporte']==d].shape[0]/n_age*100
                                        for d in top6_dep}

                # Barras agrupadas verticales: X=deporte, grupo=edad
                fig_dep_cross = go.Figure()
                age_colors = AGE_COLORS
                for age in AGES:
                    fig_dep_cross.add_trace(go.Bar(
                        name=age,
                        x=top6_dep,
                        y=[round(dep_age_cts[age].get(d, 0), 1) for d in top6_dep],
                        marker=dict(color=age_colors.get(age, P[2]), line=dict(width=0)),
                        text=[f'{dep_age_cts[age].get(d,0):.0f}%' for d in top6_dep],
                        textposition='outside', textfont=dict(size=9),
                    ))
                fig_dep_cross.update_layout(**lay('% de practicantes por deporte y grupo de edad', 360,
                    showlegend=True, legend=dict(orientation='h', y=1.06, x=0, font=dict(size=10))),
                    barmode='group',
                    xaxis=dict(showgrid=False, tickfont=dict(size=10)),
                    yaxis=dict(showgrid=True, gridcolor=GRID, ticksuffix='%',
                               range=[0, max(v for ac in dep_age_cts.values() for v in ac.values())*1.3 or 10]),
                )
                st.plotly_chart(fig_dep_cross, use_container_width=True, config=PC)

            # Frecuencia de compra deportiva libre
            hr()
            section('Dónde y cada cuánto compran ropa deportiva')
            c1, c2 = st.columns(2, gap='large')
            with c1:
                if 'Frecuencia_lugar_compra_deportiva' in df.columns:
                    # extraer lugar
                    LUGAR_NORM = {
                        'decathlon':'Decathlon','dekathlon':'Decathlon',
                        'amazon':'Amazon','zara':'Zara','corte ingles':'El Corte Inglés',
                        'corte inglés':'El Corte Inglés','el corte':'El Corte Inglés',
                        'nike':'Nike (tienda)','adidas':'Adidas (tienda)',
                        'online':'Online (sin especificar)','internet':'Online (sin especificar)',
                        'tienda':'Tienda física','multimarca':'Multimarca',
                        'outlet':'Outlet',
                    }
                    lugar_cts = Counter()
                    otros_raw = []
                    for val in df['Frecuencia_lugar_compra_deportiva'].dropna():
                        s = str(val).lower()
                        matched = False
                        for key, label in LUGAR_NORM.items():
                            if key in s: lugar_cts[label] += 1; matched = True; break
                        if not matched and is_meaningful(s) and len(s) > 3:
                            try: clean = val.encode('latin1').decode('utf-8')
                            except: clean = val
                            otros_raw.append(str(clean).strip())
                    # contar "otros" normalizados como entidades propias
                    otros_norm = Counter()
                    for raw in otros_raw:
                        key_r = raw.lower().strip()
                        if len(key_r) > 3: otros_norm[raw.title()] += 1
                    top_otros = [f'{k} ({v})' for k, v in otros_norm.most_common(3)]
                    if top_otros: lugar_cts[f'Otro: {", ".join(top_otros[:2])}…'] = len(otros_raw)
                    if lugar_cts:
                        top_lug = pd.DataFrame(lugar_cts.most_common(9), columns=['Lugar','N'])
                        st.plotly_chart(hbar(list(top_lug['Lugar']), list(top_lug['N']),
                                             gradient=True, title='Lugar habitual de compra deportiva', h=320),
                                        use_container_width=True, config=PC)
            with c2:
                if 'Frecuencia_lugar_compra_deportiva' in df.columns:
                    # extraer frecuencia temporal
                    FREQ_NORM = {
                        'temporada':'Cada temporada','año':'Una vez al año','anual':'Una vez al año',
                        '6 mes':'Cada 6 meses','seis mes':'Cada 6 meses','semestre':'Cada 6 meses',
                        '3 mes':'Cada 3 meses','tres mes':'Cada 3 meses','trimestre':'Cada 3 meses',
                        '2 mes':'Cada 2 meses','dos mes':'Cada 2 meses',
                        'mes':'Mensual','mensual':'Mensual',
                        'necesita':'Cuando necesita','estropea':'Cuando se estropea','gasta':'Cuando se gasta',
                        'rebajas':'En rebajas',
                    }
                    freq_cts = Counter()
                    for val in df['Frecuencia_lugar_compra_deportiva'].dropna():
                        s = str(val).lower()
                        for key, label in FREQ_NORM.items():
                            if key in s: freq_cts[label] += 1; break
                    if freq_cts:
                        top_frq = pd.DataFrame(freq_cts.most_common(8), columns=['Frecuencia','N'])
                        st.plotly_chart(hbar(list(top_frq['Frecuencia']), list(top_frq['N']),
                                             color=P[2], title='Frecuencia de compra deportiva', h=300),
                                        use_container_width=True, config=PC)

            # Prendas en armario × gasto (proxy nivel de engagement)
            if 'Prendas_deportivas_armario' in df.columns:
                hr()
                section('Prendas deportivas en armario × nivel económico')
                PRENDAS_NORM = {
                    '1':'1–3 prendas','2':'1–3 prendas','3':'1–3 prendas',
                    '4':'4–6 prendas','5':'4–6 prendas','6':'4–6 prendas',
                    '7':'7–10 prendas','8':'7–10 prendas','9':'7–10 prendas','10':'7–10 prendas',
                }
                def bucket_prendas(v):
                    try:
                        n = int(float(str(v).strip()))
                        if n <= 3: return '1–3 prendas'
                        if n <= 6: return '4–6 prendas'
                        if n <= 10: return '7–10 prendas'
                        return '10+ prendas'
                    except: return None

                df['_prendas_b'] = df['Prendas_deportivas_armario'].map(bucket_prendas)
                renta_short2 = {
                    'Menos de 20.000 €':'<20K€','20.000 – 35.000 € (medio-bajo)':'20–35K€',
                    '35.000 – 55.000 € (medio)':'35–55K€','55.000 – 75.000 € (medio-alto)':'55–75K€',
                    'Más de 75.000 € (alto)':'>75K€',
                }
                df['_renta_s'] = df['Renta_anual_hogar'].map(renta_short2)
                renta_ord2 = ['<20K€','20–35K€','35–55K€','55–75K€','>75K€']
                prenda_ord = ['1–3 prendas','4–6 prendas','7–10 prendas','10+ prendas']
                cross_p = pd.crosstab(df['_prendas_b'], df['_renta_s'])
                cross_p = cross_p.reindex(index=[p for p in prenda_ord if p in cross_p.index],
                                           columns=[r for r in renta_ord2 if r in cross_p.columns]).fillna(0)
                pct_p = (cross_p.div(cross_p.sum(axis=1).replace(0,1), axis=0) * 100).round(1)
                if not pct_p.empty:
                    fig_p = go.Figure()
                    renta_colors = [P[4],P[0],P[1],P[2],P[3]]
                    for i, renta in enumerate(pct_p.columns):
                        fig_p.add_trace(go.Bar(
                            name=renta, x=pct_p.index.tolist(), y=pct_p[renta].tolist(),
                            marker=dict(color=renta_colors[i % len(renta_colors)], line=dict(width=0)),
                        ))
                    fig_p.update_layout(**lay('Nº prendas deportivas en armario por nivel de renta (%)', 320,
                        showlegend=True, legend=dict(orientation='h', y=1.08, x=0, font=dict(size=10))),
                        barmode='stack',
                        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
                        yaxis=dict(showgrid=True, gridcolor=GRID, ticksuffix='%'),
                    )
                    st.plotly_chart(fig_p, use_container_width=True, config=PC)
                df.drop(columns=['_prendas_b','_renta_s'], inplace=True, errors='ignore')

        # ── MODELOS EN ARMARIO × NIVEL SOCIOECONÓMICO (S1: bañadores) ─
        if is_s1 and 'Banadores_en_armario' in df.columns:
            hr()
            section('Bañadores en armario × nivel socioeconómico')

            def bucket_ban(v):
                try:
                    n = int(float(str(v).strip()))
                    if n <= 1: return '1'
                    if n <= 3: return '2–3'
                    if n <= 5: return '4–5'
                    return '6+'
                except: return None

            df['_ban_b'] = df['Banadores_en_armario'].map(bucket_ban)
            renta_short3 = {
                'Menos de 20.000 €':'<20K€','20.000 – 35.000 € (medio-bajo)':'20–35K€',
                '35.000 – 55.000 € (medio)':'35–55K€','55.000 – 75.000 € (medio-alto)':'55–75K€',
                'Más de 75.000 € (alto)':'>75K€',
            }
            df['_renta_s2'] = df['Renta_anual_hogar'].map(renta_short3)
            ban_ord = ['1','2–3','4–5','6+']
            renta_ord3 = ['<20K€','20–35K€','35–55K€','55–75K€','>75K€']
            cross_b = pd.crosstab(df['_ban_b'], df['_renta_s2'])
            cross_b = cross_b.reindex(index=[b for b in ban_ord if b in cross_b.index],
                                       columns=[r for r in renta_ord3 if r in cross_b.columns]).fillna(0)
            pct_b = (cross_b.div(cross_b.sum(axis=0).replace(0,1), axis=1) * 100).round(1)

            c1, c2 = st.columns(2, gap='large')
            with c1:
                if not cross_b.empty:
                    fig_bh = go.Figure()
                    for i, renta in enumerate(cross_b.columns):
                        fig_bh.add_trace(go.Bar(
                            name=renta, x=cross_b.index.tolist(), y=cross_b[renta].tolist(),
                            marker=dict(color=[P[4],P[0],P[1],P[2],P[3]][i % 5], line=dict(width=0)),
                        ))
                    fig_bh.update_layout(**lay('Bañadores en armario por nivel de renta (nº)', 320,
                        showlegend=True, legend=dict(orientation='h', y=1.08, x=0, font=dict(size=10))),
                        barmode='group',
                        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                        yaxis=dict(showgrid=True, gridcolor=GRID),
                    )
                    st.plotly_chart(fig_bh, use_container_width=True, config=PC)
            with c2:
                # Bañadores usados en temporada vs en armario
                if 'Banadores_usados_temporada' in df.columns:
                    def bucket_uso(v):
                        try:
                            n = int(float(str(v).strip()))
                            if n <= 1: return '1'
                            if n <= 2: return '2'
                            if n <= 3: return '3'
                            return '4+'
                        except: return None
                    uso_vc = df['Banadores_usados_temporada'].map(bucket_uso).value_counts().reindex(
                        ['1','2','3','4+']).dropna()
                    if not uso_vc.empty:
                        st.plotly_chart(vbar(list(uso_vc.index), list(uso_vc.values),
                                             colors=P[:len(uso_vc)],
                                             title='Bañadores usados por temporada', h=320),
                                        use_container_width=True, config=PC)
            df.drop(columns=['_ban_b','_renta_s2'], inplace=True, errors='ignore')

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
                tb = top_mentions(s, 20)  # top 20 para encontrar Selmark aunque esté abajo
                if not tb.empty:
                    # Posicionar Selmark: buscar en el ranking completo
                    all_brands = top_mentions(s, 50)
                    selmark_row = all_brands[all_brands['Marca'].str.lower() == 'selmark']
                    if not selmark_row.empty:
                        selmark_pos = selmark_row.index[0] + 1
                        selmark_n   = int(selmark_row['Menciones'].iloc[0])
                        selmark_pct = selmark_n / len(df) * 100
                        st.markdown(
                            f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;'
                            f'padding:12px 16px;margin-bottom:12px;display:flex;align-items:center;gap:16px">'
                            f'<span style="font-size:1.6rem;font-weight:700;color:#1E3A8A">#{selmark_pos}</span>'
                            f'<div><div style="font-size:.75rem;font-weight:600;color:#1E3A8A">Posición de Selmark en mención espontánea — {lb}</div>'
                            f'<div style="font-size:.7rem;color:#6B7280">{selmark_n} menciones · {selmark_pct:.1f}% de las encuestadas</div></div>'
                            f'</div>',
                            unsafe_allow_html=True)
                    else:
                        st.markdown(
                            '<div style="background:#FEF3C7;border:1px solid #FDE68A;border-radius:8px;'
                            'padding:12px 16px;margin-bottom:12px;font-size:.78rem;color:#92400E">'
                            f'⚠️ Selmark no aparece en la mención espontánea — {lb}.</div>',
                            unsafe_allow_html=True)

                    # Colorear barra de Selmark en el gráfico top 15
                    tb15 = tb.head(15)
                    bar_colors = ['#EF4444' if str(m).lower() == 'selmark' else P[0]
                                  for m in tb15['Marca']]
                    brands_r = list(tb15['Marca'])[::-1]
                    vals_r   = list(tb15['Menciones'])[::-1]
                    cols_r   = bar_colors[::-1]
                    h_brand  = max(340, len(brands_r)*30 + 80)
                    fig_brand = go.Figure(go.Bar(
                        y=brands_r, x=vals_r, orientation='h',
                        marker=dict(color=cols_r, line=dict(width=0)),
                        text=vals_r, textposition='outside',
                        textfont=dict(size=10, color=FONT),
                    ))
                    fig_brand.update_layout(**lay(f'Notoriedad espontánea — {lb}', h_brand),
                        xaxis=dict(showgrid=False, showticklabels=False,
                                   range=[0, max(vals_r)*1.3] if vals_r else [0,10], zeroline=False),
                        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
                    )
                    st.plotly_chart(fig_brand, use_container_width=True, config=PC)

                if usa in df.columns:
                    tu = top_mentions(df[usa], 10)
                    if not tu.empty:
                        tu_colors = ['#EF4444' if str(m).lower() == 'selmark' else P[2]
                                     for m in tu['Marca']]
                        tu_r = list(tu['Marca'])[::-1]; tv_r = list(tu['Menciones'])[::-1]
                        tc_r = tu_colors[::-1]
                        fig_uso = go.Figure(go.Bar(
                            y=tu_r, x=tv_r, orientation='h',
                            marker=dict(color=tc_r, line=dict(width=0)),
                            text=tv_r, textposition='outside',
                            textfont=dict(size=10, color=FONT),
                        ))
                        fig_uso.update_layout(**lay(f'Dónde compra — {lb}', max(300, len(tu_r)*30+80)),
                            xaxis=dict(showgrid=False, showticklabels=False,
                                       range=[0, max(tv_r)*1.3] if tv_r else [0,10], zeroline=False),
                            yaxis=dict(showgrid=False, tickfont=dict(size=10)),
                        )
                        st.plotly_chart(fig_uso, use_container_width=True, config=PC)

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

        # ── MARCAS MÁS RECONOCIDAS POR CCAA ─────────────────────────
        hr()
        section('Penetración de marca por Comunidad Autónoma')
        st.markdown(
            '<p style="font-size:.82rem;color:#6B7280;max-width:900px;margin-bottom:1rem">'
            'Notoriedad espontánea (top of mind + otras menciones) por CCAA. '
            'Útil para detectar zonas de baja penetración y oportunidades de expansión.</p>',
            unsafe_allow_html=True)

        tom_cols_ccaa = [bc[0][0], bc[0][1]] if len(bc) > 0 else []
        if tom_cols_ccaa and 'CCAA' in df.columns:
            all_ccaa_available = sorted(df['CCAA'].dropna().unique().tolist())
            all_tom_cols = []
            for tom_c, otras_c, usa_c, lb_m in bc:
                if tom_c in df.columns: all_tom_cols.append(tom_c)
                if otras_c in df.columns: all_tom_cols.append(otras_c)

            # Calcular menciones para TODAS las CCAA (no solo top 7)
            ccaa_brand_data_all = {}
            for ccaa in all_ccaa_available:
                sub = df[df['CCAA'] == ccaa]
                cts = Counter()
                for col in all_tom_cols:
                    if col in sub.columns:
                        for val in sub[col].dropna():
                            for item in str(val).split('|'):
                                item = item.strip().title()
                                if item and item.lower() not in NO_MEANING and len(item) > 2:
                                    cts[item] += 1
                ccaa_brand_data_all[ccaa] = cts

            global_cts_all = Counter()
            for cts in ccaa_brand_data_all.values(): global_cts_all.update(cts)
            all_marcas_ranked = [m for m, _ in global_cts_all.most_common(20)]

            # Filtros interactivos
            col_f1, col_f2 = st.columns(2, gap='large')
            with col_f1:
                ccaa_options = ['Todas las CCAA'] + all_ccaa_available
                ccaa_sel = st.selectbox('Comunidad Autónoma', ccaa_options, key='ccaa_marca')
            with col_f2:
                marca_options = ['Todas las marcas'] + all_marcas_ranked[:15]
                marca_sel = st.multiselect('Marcas a mostrar', all_marcas_ranked[:15],
                                           default=all_marcas_ranked[:8], key='marca_ccaa_filter')

            ccaa_list_filtered = all_ccaa_available if ccaa_sel == 'Todas las CCAA' else [ccaa_sel]
            # solo CCAA con muestra suficiente
            ccaa_list_filtered = [c for c in ccaa_list_filtered if len(df[df['CCAA']==c]) >= 5]
            top_marcas_sel = marca_sel if marca_sel else all_marcas_ranked[:8]

            if top_marcas_sel and ccaa_list_filtered:
                heat_data = []
                for marca in top_marcas_sel:
                    row_vals = []
                    for ccaa in ccaa_list_filtered:
                        n_ccaa = len(df[df['CCAA'] == ccaa])
                        cnt = ccaa_brand_data_all[ccaa].get(marca, 0)
                        row_vals.append(round(cnt / n_ccaa * 100 if n_ccaa > 0 else 0, 1))
                    heat_data.append(row_vals)

                h_hm = max(320, len(top_marcas_sel) * 36 + 80)
                fig_hm = go.Figure(go.Heatmap(
                    z=heat_data,
                    x=ccaa_list_filtered,
                    y=top_marcas_sel,
                    colorscale=[[0,'#F8FAFF'],[0.4,'#93C5FD'],[1,'#1E3A8A']],
                    text=[[f'{v:.0f}%' for v in row] for row in heat_data],
                    texttemplate='%{text}',
                    textfont=dict(size=9),
                    showscale=True,
                    colorbar=dict(title='%', ticksuffix='%', thickness=10,
                                  len=0.8, tickfont=dict(size=9)),
                ))
                fig_hm.update_layout(**lay('% de mención espontánea por marca y CCAA', h_hm),
                    xaxis=dict(showgrid=False, tickfont=dict(size=9), tickangle=-25),
                    yaxis=dict(showgrid=False, tickfont=dict(size=10), autorange='reversed'),
                )
                st.plotly_chart(fig_hm, use_container_width=True, config=PC)

                # Tabla — marca líder por CCAA
                hr()
                ccaa_leader = {}
                for ccaa in all_ccaa_available:
                    cts_c = ccaa_brand_data_all.get(ccaa, Counter())
                    if cts_c:
                        leader, score = cts_c.most_common(1)[0]
                        n_ccaa = len(df[df['CCAA']==ccaa]) or 1
                        ccaa_leader[ccaa] = {'marca': leader, 'pct': round(score/n_ccaa*100, 1)}

                if ccaa_leader:
                    st.markdown('<div class="chart-label">Marca más mencionada por CCAA</div>',
                                unsafe_allow_html=True)
                    df_leader = pd.DataFrame([
                        {'CCAA': c, 'Marca líder': v['marca'], '% mención': f"{v['pct']:.1f}%",
                         'n encuestadas': len(df[df['CCAA']==c])}
                        for c, v in ccaa_leader.items()
                    ]).sort_values('CCAA')
                    st.dataframe(df_leader, use_container_width=True, hide_index=True)

                with st.expander('Ver tabla de datos completa'):
                    df_heat = pd.DataFrame(heat_data, index=top_marcas_sel, columns=ccaa_list_filtered)
                    df_heat.index.name = 'Marca'
                    st.dataframe(df_heat.style.format('{:.1f}%').background_gradient(
                        cmap='Blues', axis=None), use_container_width=True)

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

            st.markdown(f'<div style="font-family:Montserrat,sans-serif;font-size:1.15rem;font-weight:600;color:#111827;margin:1.2rem 0 .4rem">— {lbl}</div>', unsafe_allow_html=True)

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
                ('_s','Selmark',          '#1E3A8A','#FFFFFF'),
                ('_a','Comp. aspiracional','#3B82F6','#FFFFFF'),
                ('_b','Comp. accesible',  '#BAE6FD','#0C4A6E'),
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
                st.markdown(f'<div style="font-size:.7rem;font-weight:600;color:#0F6FEC;margin:12px 0 8px;text-transform:uppercase;letter-spacing:.1em">Tríada {t_num}</div>', unsafe_allow_html=True)
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
                        bg_c = {'_s':'#1E3A8A','_a':'#3B82F6','_b':'#BAE6FD'}[suf]
                        fg_c = '#FFFFFF' if suf != '_b' else '#0C4A6E'
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
            bnames  = {'_s':'Selmark','_a':'Aspiracional','_b':'Accesible'}
            bcols   = {'_s':'#1E3A8A','_a':'#3B82F6','_b':'#BAE6FD'}
            ftcols  = {'_s':'#FFFFFF','_a':'#FFFFFF','_b':'#0C4A6E'}
            for suf in ('_s','_a','_b'):
                ys = [prod_brand_pcts(df[df[scol]==s],pc).get(suf,0) for s in segs]
                fig_seg.add_trace(go.Bar(
                    name=bnames[suf], x=segs, y=ys,
                    marker=dict(color=bcols[suf], line=dict(width=0)),
                    text=[f'{v:.0f}%' for v in ys],
                    textposition='inside', textfont=dict(size=10, color=ftcols[suf]),
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

            # ─ Nubes de palabras por marca ────────────────────────────────
            hr()
            section(f'¿Por qué eligen cada producto? — {lbl}')
            st.markdown('<p style="font-size:.82rem;color:#6B7280;margin-bottom:1rem">'
                        'Nube de palabras con los motivos de elección por tipo de marca. '
                        'El tamaño refleja la frecuencia de cada término.</p>',
                        unsafe_allow_html=True)

            def make_wordcloud_img(texts, color):
                try:
                    from wordcloud import WordCloud
                    import matplotlib
                    matplotlib.use('Agg')
                    import matplotlib.pyplot as plt
                    import io, base64
                    combined = ' '.join(
                        clean_text(t) for t in texts if is_meaningful(t))
                    if not combined.strip(): return None
                    _SW = {
                        # artículos, prep, pronombres
                        'que','de','la','el','lo','me','es','se','un','una','en','por',
                        'con','al','del','mas','le','no','si','y','a','mi','su','te','ya',
                        'muy','para','como','pero','los','las','son','hay','tan','bien',
                        'les','nos','os','ellas','ellos','esta','este','esto','eso','esa',
                        'ese','unos','unas','ante','bajo','desde','entre','hacia','hasta',
                        'segun','sin','sobre','tras','o','e','u',
                        # verbos comunes sin valor semántico
                        'parece','porque','gusta','gustan','gosto','me','tiene','tienen',
                        'ser','estar','ver','hace','hacen','creo','pone','ponen','da','dan',
                        'veo','quiero','quiere','quieren','puede','pueden','es','son',
                        'ha','han','he','hemos','habia','habian','hay','hubo','fue','fueron',
                        'era','eran','si','no','ni','aunque','cuando','donde','mientras',
                        'ademas','tambien','asi','ahi','aqui','alla','todo','toda','todos',
                        'todas','algo','nada','cada','otro','otra','otros','otras','mismo',
                        'misma','mismo','mas','menos','mucho','mucha','muchos','muchas',
                        'poco','poca','pocos','pocas','bastante','demasiado','algo','nada',
                        'numero','color','tipo','cosa','cosas','forma','vez','veces',
                    }
                    wc = WordCloud(
                        width=500, height=280, background_color='white',
                        color_func=lambda *a, **kw: color,
                        max_words=50, min_font_size=10,
                        collocations=False,
                        stopwords=_SW,
                    ).generate(combined)
                    fig, ax = plt.subplots(figsize=(5, 2.8), facecolor='none')
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis('off')
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight',
                                transparent=True, dpi=120)
                    plt.close(fig)
                    buf.seek(0)
                    return base64.b64encode(buf.read()).decode()
                except Exception:
                    return None

            def brand_mask(suffix):
                codes = [c for c in raw_cts if c.endswith(suffix)]
                return df[pc].apply(lambda v: any(
                    str(v).endswith(c) or (':' in str(v) and str(v).split(':',1)[1].strip()==c)
                    for c in codes))

            wc_configs = [
                ('_s', 'Selmark',           '#1E3A8A', wc_pos),
                ('_a', 'Comp. aspiracional', '#3B82F6', wc_pos),
                ('_b', 'Comp. accesible',   '#60A5FA', wc_pos),
            ]

            # Función para extraer top keywords (sustantivos/adjetivos)
            def top_keywords(texts, n=6):
                from collections import Counter as _C
                _SW2 = {
                    'que','de','la','el','lo','me','es','se','un','una','en','por',
                    'con','al','del','mas','le','no','si','y','a','mi','su','te','ya',
                    'muy','para','como','pero','los','las','son','hay','tan','bien',
                    'parece','porque','gusta','tiene','ser','estar','ver','hace',
                    'creo','pone','da','veo','quiero','puede','ha','han','he','fue',
                    'era','aunque','cuando','donde','mientras','ademas','tambien',
                    'asi','todo','toda','todos','todas','algo','nada','cada','otro',
                    'otra','mismo','misma','mucho','muchos','poco','pocos','bastante',
                    'numero','color','tipo','cosa','forma','vez','veces','mas','menos',
                    'este','esta','esto','ese','esa','eso','ni','o','e','u',
                }
                words = []
                for t in texts:
                    if is_meaningful(t):
                        for w in clean_text(t).split():
                            if w not in _SW2 and len(w) > 3:
                                words.append(w)
                top = _C(words).most_common(n)
                return [w for w, _ in top]

            wc_cols = st.columns(3)
            wc_keyword_data = {}
            for col_obj, (suf, bname, color, txt_col) in zip(wc_cols, wc_configs):
                with col_obj:
                    st.markdown(f'<div style="font-size:.72rem;font-weight:600;color:{color};'
                                f'text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px">'
                                f'{bname}</div>', unsafe_allow_html=True)
                    mask = brand_mask(suf)
                    if mask.sum() > 5 and txt_col in df.columns:
                        texts = df[mask][txt_col].dropna().tolist()
                        img64 = make_wordcloud_img(texts, color)
                        if img64:
                            st.markdown(
                                f'<img src="data:image/png;base64,{img64}" '
                                f'style="width:100%;border-radius:8px;border:1px solid #E5E7EB">',
                                unsafe_allow_html=True)
                        else:
                            st.info('Sin suficientes respuestas.')
                        wc_keyword_data[suf] = (bname, color, texts)
                    else:
                        st.info('Pocas respuestas.')

            # Motivos clave por marca — resumen compacto
            neg_texts_all = df[wc_neg].dropna().tolist() if wc_neg in df.columns else []
            st.markdown('<br>', unsafe_allow_html=True)
            motivo_cols3 = st.columns(3)
            for col_obj, (suf, bname, color, txt_col) in zip(motivo_cols3, wc_configs):
                with col_obj:
                    if suf not in wc_keyword_data: continue
                    _, col_hex, pos_texts = wc_keyword_data[suf]
                    kw_pos = top_keywords(pos_texts, 5)
                    st.markdown(
                        f'<div style="border-left:3px solid {col_hex};padding:10px 14px;'
                        f'background:#F9FAFB;border-radius:0 6px 6px 0">'
                        f'<div style="font-size:.65rem;font-weight:700;color:{col_hex};'
                        f'text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px">'
                        f'{bname} — eligen por</div>'
                        + ''.join(f'<div style="font-size:.75rem;color:#374151;margin:3px 0">'
                                  f'· {w.capitalize()}</div>' for w in kw_pos)
                        + '</div>',
                        unsafe_allow_html=True)

            # Por qué los otros no gustan — resumen
            if neg_texts_all:
                neg_kw = top_keywords(neg_texts_all, 6)
                st.markdown(
                    f'<div style="margin-top:10px;border-left:3px solid #9CA3AF;padding:10px 14px;'
                    f'background:#F9FAFB;border-radius:0 6px 6px 0">'
                    f'<div style="font-size:.65rem;font-weight:700;color:#6B7280;'
                    f'text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px">'
                    f'Por qué los otros no convencen</div>'
                    + ''.join(f'<div style="font-size:.75rem;color:#374151;margin:3px 0">'
                              f'· {w.capitalize()}</div>' for w in neg_kw)
                    + '</div>',
                    unsafe_allow_html=True)

            # Respuestas abiertas completas (expandible)
            c1, c2 = st.columns(2)
            with c1:
                if wc_pos in df.columns:
                    texts = [v for v in df[wc_pos].dropna() if is_meaningful(v)]
                    if texts:
                        with st.expander(f'Ver respuestas — por qué gusta más ({len(texts)})'):
                            for t in texts[:80]:
                                st.markdown(f'<p style="font-size:.8rem;color:#2A3A4A;border-left:3px solid #0F6FEC;padding-left:10px;margin:4px 0">{t}</p>', unsafe_allow_html=True)
            with c2:
                if wc_neg in df.columns:
                    texts = [v for v in df[wc_neg].dropna() if is_meaningful(v)]
                    if texts:
                        with st.expander(f'Ver respuestas — por qué gustan menos ({len(texts)})'):
                            for t in texts[:80]:
                                st.markdown(f'<p style="font-size:.8rem;color:#2A3A4A;border-left:3px solid #93C5FD;padding-left:10px;margin:4px 0">{t}</p>', unsafe_allow_html=True)
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
                    f'<div style="font-size:.6rem;color:#6B7280">{hex_c}</div>'
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
                        f'<div style="font-size:.62rem;color:#6B7280">{cnt} encuestadas</div>'
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
                        color_h = PERSONA_C.get(persona, '#0F6FEC')
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

        # ── COLORES POR RANGO DE EDAD ─────────────────────────────────
        for col_fav_age, _col_combo_age, label_age in (color_pairs if len(color_pairs) else []):
            if col_fav_age not in df.columns or 'Grupo_edad' not in df.columns:
                continue
            section(f'Colores por rango de edad — {label_age}')
            age_col_data = {}
            for age in AGES:
                sub_age = df[df['Grupo_edad'] == age]
                age_col_data[age] = parse_hex_colors(sub_age[col_fav_age])

            # Agrupar por tono (12 categorías de color)
            def hex_to_hue_category(hex_c):
                try:
                    h = hex_c.lstrip('#')
                    r,g,b = tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
                    import colorsys as _cs
                    hue, sat, val = _cs.rgb_to_hsv(r, g, b)
                    if sat < 0.12: return '⬜ Blanco/Crema' if val > 0.85 else ('⬛ Negro/Gris oscuro' if val < 0.35 else '🔲 Gris medio')
                    h_deg = hue * 360
                    if h_deg < 20: return '🔴 Rojo'
                    if h_deg < 40: return '🟠 Naranja'
                    if h_deg < 65: return '🟡 Amarillo'
                    if h_deg < 150: return '🟢 Verde'
                    if h_deg < 195: return '🩵 Azul claro/Turquesa'
                    if h_deg < 255: return '🔵 Azul'
                    if h_deg < 290: return '🟣 Morado/Violeta'
                    if h_deg < 330: return '🩷 Rosa/Fucsia'
                    return '🔴 Rojo'
                except: return 'Otro'

            cat_colors = ['🔴 Rojo','🟠 Naranja','🟡 Amarillo','🟢 Verde',
                          '🩵 Azul claro/Turquesa','🔵 Azul','🟣 Morado/Violeta','🩷 Rosa/Fucsia',
                          '⬜ Blanco/Crema','🔲 Gris medio','⬛ Negro/Gris oscuro']

            # Para cada categoría de color, usar 3 tonalidades (claro→oscuro por edad)
            # (light=18-30, medium=31-45, dark=46+)
            CAT_SHADES = {
                '🔴 Rojo':                   ('#FFBBBB', '#EF4444', '#B91C1C'),
                '🟠 Naranja':                ('#FED7AA', '#F97316', '#C2410C'),
                '🟡 Amarillo':               ('#FEF08A', '#EAB308', '#A16207'),
                '🟢 Verde':                  ('#BBF7D0', '#22C55E', '#15803D'),
                '🩵 Azul claro/Turquesa':    ('#CFFAFE', '#06B6D4', '#0E7490'),
                '🔵 Azul':                   ('#BFDBFE', '#3B82F6', '#1E3A8A'),
                '🟣 Morado/Violeta':         ('#E9D5FF', '#A855F7', '#6B21A8'),
                '🩷 Rosa/Fucsia':            ('#FBCFE8', '#EC4899', '#9D174D'),
                '⬜ Blanco/Crema':           ('#F9FAFB', '#D1D5DB', '#6B7280'),
                '🔲 Gris medio':             ('#E5E7EB', '#9CA3AF', '#4B5563'),
                '⬛ Negro/Gris oscuro':      ('#9CA3AF', '#374151', '#111827'),
            }
            age_shade_idx = {'18–30': 0, '31–45': 1, '46+': 2}
            fig_age_col = go.Figure()
            for age in AGES:
                if not age_col_data.get(age): continue
                cat_cts = Counter(hex_to_hue_category(h) for h in age_col_data[age])
                total_age = sum(cat_cts.values()) or 1
                vals = [cat_cts.get(c, 0) / total_age * 100 for c in cat_colors]
                sidx = age_shade_idx.get(age, 0)
                marker_colors = [CAT_SHADES.get(c, ('#aaa','#777','#444'))[sidx] for c in cat_colors]
                # Para el grupo más claro (18-30), añadir borde visible en blancos/grises claros
                line_colors = ['#9CA3AF' if sidx == 0 and c in ('⬜ Blanco/Crema',) else 'rgba(0,0,0,0)'
                               for c in cat_colors]
                fig_age_col.add_trace(go.Bar(
                    name=age, x=cat_colors, y=vals,
                    marker=dict(color=marker_colors,
                                line=dict(color=line_colors, width=1)),
                ))
            fig_age_col.update_layout(**lay(f'Preferencia de tono de color por grupo de edad — {label_age}', 340,
                showlegend=True, legend=dict(orientation='h', y=1.08, x=0, font=dict(size=10))),
                barmode='group',
                xaxis=dict(showgrid=False, tickfont=dict(size=9), tickangle=-20),
                yaxis=dict(showgrid=True, gridcolor=GRID, ticksuffix='%'),
            )
            st.plotly_chart(fig_age_col, use_container_width=True, config=PC)

            # Swatches top 8 por grupo de edad
            age_sw_cols = st.columns(len(AGES))
            for age, col_obj in zip(AGES, age_sw_cols):
                with col_obj:
                    top_age_cols = Counter(age_col_data.get(age, [])).most_common(8)
                    st.markdown(f'<div style="font-size:.7rem;font-weight:600;color:#0F6FEC;margin-bottom:6px">{age}</div>',
                                unsafe_allow_html=True)
                    if top_age_cols:
                        sw = '<div style="display:flex;flex-wrap:wrap;gap:4px">'
                        for hx, cnt in top_age_cols:
                            sw += (f'<div title="{hx} ({cnt}×)" style="width:32px;height:32px;background:{hx};'
                                   f'border-radius:5px;border:1px solid rgba(0,0,0,.1)"></div>')
                        sw += '</div>'
                        st.markdown(sw, unsafe_allow_html=True)
            hr()

    except Exception as e:
        st.error(f'Error Color: {e}'); st.code(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════════
# TAB 7 — CANALES & INFLUENCERS
# ═══════════════════════════════════════════════════════════════════
with tab7:
    try:
        section('Canales de visibilidad · Análisis cruzado por edad')

        # columnas de canales según encuesta
        if is_s1:
            vis_cols = [('Visibilidad_lenceria_canales','Lencería'),('Visibilidad_bano_canales','Baño')]
            inf_sino = [('Influencer_lenceria_sino','Lencería'),('Influencer_bano_sino','Baño')]
            inf_nom  = [('Influencer_lenceria_nombre','Lencería'),('Influencer_bano_nombre','Baño')]
        else:
            vis_cols = [('Visibilidad_deporte_canales','Deporte'),('Visibilidad_homewear_canales','Homewear')]
            inf_sino = [('Influencer_deporte_sino','Deporte'),('Influencer_homewear_sino','Homewear')]
            inf_nom  = [('Influencer_deporte_nombre','Deporte'),('Influencer_homewear_nombre','Homewear')]

        def parse_canal_rank(series, top_n=1):
            """Extrae el canal en posición top_n de respuestas ordenadas '1.Canal | 2.Canal …'."""
            cts = Counter()
            for val in series.dropna():
                parts = str(val).split('|')
                for part in parts:
                    part = part.strip()
                    m = re.match(r'^(\d+)\.(.*)', part)
                    if m:
                        rank = int(m.group(1))
                        canal = m.group(2).strip()
                        if rank <= top_n and canal and len(canal) > 2:
                            cts[canal] += 1
                    elif not re.match(r'^\d+\.', part) and len(part) > 2:
                        # respuesta sin orden numérico — contar como 1ª posición
                        cts[part] += 1
                        break
            return cts

        # ── Canal 1ª posición total y por edad ─────────────────────────
        for vis_col, label_v in vis_cols:
            if vis_col not in df.columns: continue
            section(f'Canal de visibilidad principal — {label_v}')

            # Total
            cts_total = parse_canal_rank(df[vis_col], top_n=1)
            top_canales = [c for c, _ in sorted(cts_total.items(), key=lambda x: -x[1])[:10]]

            c1, c2 = st.columns([1, 1], gap='large')
            with c1:
                if cts_total:
                    top_df = pd.DataFrame(cts_total.most_common(10), columns=['Canal','N'])
                    st.plotly_chart(hbar(list(top_df['Canal']), list(top_df['N']),
                                         gradient=True, title=f'Top canales 1ª posición — {label_v}', h=360),
                                    use_container_width=True, config=PC)

            with c2:
                # Canal por edad (% de cada grupo que menciona ese canal en 1ª pos)
                age_canal = {}
                for age in AGES:
                    sub_a = df[df['Grupo_edad'] == age]
                    age_canal[age] = parse_canal_rank(sub_a[vis_col], top_n=1)

                if top_canales and any(age_canal.values()):
                    fig_ca = go.Figure()
                    _AGE_SOFT = {'18–30': '#93C5FD', '31–45': '#C4B5FD', '46+': '#FDE68A'}
                    for age in AGES:
                        n_age = (df['Grupo_edad'] == age).sum() or 1
                        vals_ca = [age_canal.get(age,Counter()).get(c,0)/n_age*100 for c in top_canales[:8]]
                        fig_ca.add_trace(go.Bar(
                            name=age, x=top_canales[:8], y=vals_ca,
                            marker=dict(color=_AGE_SOFT.get(age, P[2]), line=dict(width=0)),
                        ))
                    fig_ca.update_layout(**lay(f'Canal 1ª posición — % por grupo de edad', 360,
                        showlegend=True, legend=dict(orientation='h', y=1.08, x=0, font=dict(size=10))),
                        barmode='group',
                        xaxis=dict(showgrid=False, tickfont=dict(size=9), tickangle=-20),
                        yaxis=dict(showgrid=True, gridcolor=GRID, ticksuffix='%'),
                    )
                    st.plotly_chart(fig_ca, use_container_width=True, config=PC)

            # Todos los canales ordenados (no solo 1ª posición) — con score ponderado
            with st.expander(f'Ver ranking ponderado de todos los canales — {label_v}'):
                scores = Counter()
                for val in df[vis_col].dropna():
                    parts = str(val).split('|')
                    n_total = len(parts)
                    for part in parts:
                        part = part.strip()
                        m = re.match(r'^(\d+)\.(.*)', part)
                        if m:
                            rank = int(m.group(1))
                            canal = m.group(2).strip()
                            if canal and len(canal) > 2:
                                # score inverso: 1ª posición vale más
                                weight = max(1, n_total - rank + 1)
                                scores[canal] += weight
                if scores:
                    top_sc = pd.DataFrame(scores.most_common(12), columns=['Canal','Score ponderado'])
                    st.plotly_chart(hbar(list(top_sc['Canal']), list(top_sc['Score ponderado']),
                                         color=P[2], title='Score de canal ponderado por posición (más posición 1 = más peso)', h=360),
                                    use_container_width=True, config=PC)

            hr()

        # ── INFLUENCERS ─────────────────────────────────────────────────
        section('Influencers de referencia mencionados')

        def norm_influencer(v):
            v = str(v).strip().lower()
            # normalización básica de nombres frecuentes
            MAP_INF = {
                'dulceida':'Dulceida','dulce vida':'Dulceida',
                'laura escanes':'Laura Escanes','escanes':'Laura Escanes',
                'pilar rubio':'Pilar Rubio',
                'georgina':'Georgina Rodríguez','georgina rodriguez':'Georgina Rodríguez',
                'lola indigo':'Lola Índigo','lola índigo':'Lola Índigo','miriam':'Lola Índigo',
                'maria pombo':'María Pombo','pombo':'María Pombo',
                'violeta':'Violeta by Mango','violeta by mango':'Violeta by Mango',
                'marta diaz':'Marta Díaz','marta díaz':'Marta Díaz',
                'blanca suarez':'Blanca Suárez','blanca suárez':'Blanca Suárez',
                'sofia suescun':'Sofía Suescun','sofia':'Sofía Suescun',
                'carlota maranon':'Carlota Marañón','carlota':'Carlota Marañón',
                'irina shayk':'Irina Shayk','irina shiek':'Irina Shayk','irina':'Irina Shayk',
                'emily ratajkowski':'Emily Ratajkowski','emili':'Emily Ratajkowski',
                'kim kardashian':'Kim Kardashian','kim k':'Kim Kardashian',
                'kendall jenner':'Kendall Jenner','kendall':'Kendall Jenner',
                'ninguna':'— ninguna —','no':'— ninguna —','no tengo':'— ninguna —',
                'no sigo':'— ninguna —','no uso':'— ninguna —',
            }
            for key, label in MAP_INF.items():
                if key in v: return label
            if not is_meaningful(v) or len(v) < 3: return None
            return v.title()

        inf_records = []
        for nom_col, label_n in inf_nom:
            if nom_col not in df.columns: continue
            for _, row in df.iterrows():
                val = row.get(nom_col, '')
                ge  = row.get('Grupo_edad', '')
                norm = norm_influencer(str(val))
                if norm and norm != '— ninguna —' and ge in AGES:
                    inf_records.append({'Influencer': norm, 'GE': ge, 'Categoria': label_n})

        if inf_records:
            inf_df = pd.DataFrame(inf_records)

            # ── Por categoría de producto ──────────────────────────────
            cats_inf = inf_df['Categoria'].unique().tolist()
            for cat_inf in cats_inf:
                sub_cat = inf_df[inf_df['Categoria'] == cat_inf]
                top_inf_cat = sub_cat['Influencer'].value_counts().head(12)
                if top_inf_cat.empty: continue

                st.markdown(f'<div style="font-size:.75rem;font-weight:600;color:#0F6FEC;'
                            f'text-transform:uppercase;letter-spacing:.1em;margin:12px 0 6px">'
                            f'— {cat_inf}</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2, gap='large')
                with c1:
                    st.plotly_chart(hbar(list(top_inf_cat.index), list(top_inf_cat.values),
                                         gradient=True, title=f'Top influencers — {cat_inf}', h=380),
                                    use_container_width=True, config=PC)
                with c2:
                    top8 = top_inf_cat.head(8).index.tolist()
                    sub_cross = sub_cat[sub_cat['Influencer'].isin(top8)]
                    inf_cross_c = pd.crosstab(sub_cross['Influencer'], sub_cross['GE'])
                    inf_cross_c = inf_cross_c.reindex(columns=[a for a in AGES if a in inf_cross_c.columns]).fillna(0)
                    inf_pct_c = inf_cross_c.div(inf_cross_c.sum(axis=1).replace(0,1), axis=0) * 100
                    fig_inf_age = go.Figure()
                    AGE_COLORS_SOFT = {'18–30': '#93C5FD', '31–45': '#C4B5FD', '46+': '#FDE68A'}
                    for age in inf_pct_c.columns:
                        fig_inf_age.add_trace(go.Bar(
                            name=age, y=inf_pct_c.index.tolist(), x=inf_pct_c[age].tolist(),
                            orientation='h',
                            marker=dict(color=AGE_COLORS_SOFT.get(age, P[2]), line=dict(width=0)),
                        ))
                    fig_inf_age.update_layout(**lay(f'Distribución de edad por influencer — {cat_inf}', 380,
                        showlegend=True, legend=dict(orientation='h', y=1.08, x=0, font=dict(size=10))),
                        barmode='stack',
                        xaxis=dict(showgrid=False, ticksuffix='%', range=[0,105]),
                        yaxis=dict(showgrid=False, tickfont=dict(size=10), autorange='reversed'),
                    )
                    st.plotly_chart(fig_inf_age, use_container_width=True, config=PC)

        # ── PILAR RUBIO ────────────────────────────────────────────────
        hr()
        section('Opinión sobre Pilar Rubio · Por grupo de edad')

        st.markdown(
            '<p style="font-size:.82rem;color:#6B7280;max-width:800px;margin-bottom:1rem">'
            'Análisis de sentimiento de las respuestas abiertas sobre Pilar Rubio, '
            'cruzado por grupo de edad.</p>',
            unsafe_allow_html=True)

        if 'Opinion_Pilar_Rubio' in df.columns:
            # Clasificar opinión en positiva / negativa / neutral / no la conoce
            POSITIVAS = {'bien','buena','bueno','guapa','moderna','bonita','elegante',
                         'natural','simpática','graciosa','talentos','profesional',
                         'encanta','gusta','favorita','perfecta','increíble','increible',
                         'top','crack','genial','fantastica','fantástica','estupenda'}
            NEGATIVAS = {'mal','mala','malo','gorda','fea','antipática','aburrida',
                         'no me gusta','horrible','pésima','pesima','floja','regular',
                         'insoportable','no me convence','no me agrada','fatal'}
            NO_CONOCE = {'no sé quién es','no la conozco','no sé','no se quien','no se quién',
                         'no la conozco','desconocida','no la sigo','nunca la he visto',
                         'nose kien','nose quien','no kien'}

            def classify_rubio(v):
                if not isinstance(v, str): return 'Sin respuesta'
                t = clean_text(v)
                if any(nc in t for nc in NO_CONOCE): return 'No la conoce'
                if not is_meaningful(v): return 'Sin respuesta'
                # buscar palabras clave
                words = set(t.split())
                pos_score = sum(1 for w in words if any(p in w for p in POSITIVAS))
                neg_score = sum(1 for w in words if any(n in w for n in NEGATIVAS))
                if pos_score > neg_score: return 'Positiva'
                if neg_score > pos_score: return 'Negativa'
                return 'Neutral'

            df['_rubio_sent'] = df['Opinion_Pilar_Rubio'].apply(classify_rubio)

            sent_order = ['Positiva','Neutral','Negativa','No la conoce','Sin respuesta']
            sent_colors = {'Positiva': '#6EE7B7', 'Neutral': '#CBD5E1',
                           'Negativa': '#FCA5A5', 'No la conoce': '#FDE68A', 'Sin respuesta': '#F3F4F6'}

            c1, c2 = st.columns(2, gap='large')
            with c1:
                sent_total = (df['_rubio_sent'].value_counts()
                              .drop('Sin respuesta', errors='ignore')
                              .sort_values(ascending=True))
                fig_rt = go.Figure(go.Bar(
                    y=list(sent_total.index), x=list(sent_total.values), orientation='h',
                    marker=dict(color=[sent_colors.get(s, '#ccc') for s in sent_total.index],
                                line=dict(width=0)),
                    text=list(sent_total.values), textposition='outside',
                    textfont=dict(size=10, color=FONT),
                ))
                fig_rt.update_layout(**lay('Sentimiento total sobre Pilar Rubio', 260),
                    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False,
                               range=[0, max(sent_total.values)*1.3] if len(sent_total) else [0,10]),
                    yaxis=dict(showgrid=False, tickfont=dict(size=11)),
                )
                st.plotly_chart(fig_rt, use_container_width=True, config=PC)

            with c2:
                sent_cross = pd.crosstab(df['Grupo_edad'], df['_rubio_sent'])
                sent_cross = sent_cross.reindex(AGES).fillna(0)
                sent_pct = sent_cross.div(sent_cross.sum(axis=1).replace(0,1), axis=0) * 100
                fig_rage = go.Figure()
                for sent in [s for s in sent_order if s in sent_pct.columns]:
                    fig_rage.add_trace(go.Bar(
                        name=sent, x=AGES,
                        y=[float(sent_pct.loc[a, sent]) if a in sent_pct.index else 0 for a in AGES],
                        marker=dict(color=sent_colors.get(sent, '#ccc'), line=dict(width=0)),
                    ))
                fig_rage.update_layout(**lay('Sentimiento por grupo de edad (%)', 260,
                    showlegend=True, legend=dict(orientation='h', y=1.08, x=0, font=dict(size=10))),
                    barmode='stack',
                    xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                    yaxis=dict(showgrid=True, gridcolor=GRID, ticksuffix='%'),
                )
                st.plotly_chart(fig_rage, use_container_width=True, config=PC)

            # ── Text Mining — términos más frecuentes en opiniones ──────
            hr()
            rubio_texts = []
            for val in df['Opinion_Pilar_Rubio'].dropna():
                try: val = val.encode('latin1').decode('utf-8')
                except: pass
                if is_meaningful(val) and classify_rubio(val) != '❓ No la conoce':
                    rubio_texts.append(clean_text(val))

            if len(rubio_texts) >= 20:
                show_text_mining(
                    pd.Series(rubio_texts),
                    'Temas en las opiniones sobre Pilar Rubio')

            # ── Palabras más frecuentes por sentimiento ─────────────────
            st.markdown('<div class="chart-label" style="margin-top:16px">Palabras más frecuentes por tipo de opinión</div>',
                        unsafe_allow_html=True)
            sent_cols_ui = st.columns(4)
            sent_show = ['✅ Positiva','❌ Negativa','➖ Neutral','❓ No la conoce']
            for col_obj, sent in zip(sent_cols_ui, sent_show):
                with col_obj:
                    s_color = sent_colors.get(sent, '#999')
                    st.markdown(f'<div style="font-size:.68rem;font-weight:600;color:{s_color};margin-bottom:6px">{sent}</div>',
                                unsafe_allow_html=True)
                    sub_s = df[df['_rubio_sent'] == sent]['Opinion_Pilar_Rubio'].dropna()
                    sub_s = sub_s[sub_s.apply(is_meaningful)]
                    if len(sub_s) < 3:
                        st.markdown('<div style="font-size:.7rem;color:#aaa">Sin datos suficientes</div>',
                                    unsafe_allow_html=True)
                        continue
                    words_s = Counter()
                    for val in sub_s:
                        try: val = val.encode('latin1').decode('utf-8')
                        except: pass
                        for w in clean_text(val).split():
                            if w not in STOPWORDS_ES and len(w) > 3:
                                words_s[w] += 1
                    for word, cnt in words_s.most_common(8):
                        st.markdown(
                            f'<div style="display:flex;justify-content:space-between;align-items:center;'
                            f'padding:2px 0;border-bottom:1px solid #F3F4F6">'
                            f'<span style="font-size:.78rem;color:{FONT}">{word}</span>'
                            f'<span style="font-size:.68rem;font-weight:600;color:{s_color};'
                            f'background:{s_color}18;padding:1px 6px;border-radius:3px">{cnt}</span>'
                            f'</div>',
                            unsafe_allow_html=True)

            # Muestra de respuestas representativas
            with st.expander('Ver respuestas reales por sentimiento'):
                for sent in ['✅ Positiva','❌ Negativa','❓ No la conoce','➖ Neutral']:
                    sub_s = df[df['_rubio_sent'] == sent]['Opinion_Pilar_Rubio'].dropna()
                    sub_s = sub_s[sub_s.apply(is_meaningful)]
                    s_color = sent_colors.get(sent, '#999')
                    st.markdown(f'<div style="font-size:.7rem;font-weight:600;color:{s_color};'
                                f'margin:10px 0 4px">{sent} ({len(sub_s)} respuestas)</div>',
                                unsafe_allow_html=True)
                    sample = sub_s.sample(min(6, len(sub_s)), random_state=42) if len(sub_s) > 0 else []
                    for resp in sample:
                        try: resp = resp.encode('latin1').decode('utf-8')
                        except: pass
                        st.markdown(f'<p style="font-size:.8rem;color:#374151;border-left:3px solid '
                                    f'{s_color};padding-left:10px;margin:3px 0">'
                                    f'{resp}</p>', unsafe_allow_html=True)

            df.drop(columns=['_rubio_sent'], inplace=True, errors='ignore')

    except Exception as e:
        st.error(f'Error Canales & Influencers: {e}'); st.code(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════════
# TAB 8 — ANÁLISIS ESTRATÉGICO
# ═══════════════════════════════════════════════════════════════════
with tab8:
    try:
        st.markdown(
            '<p style="font-size:.85rem;color:#6B7280;max-width:960px;margin-bottom:1.5rem">'
            'Análisis cruzados orientados a decisión: oportunidades de expansión física, '
            'segmentos de alto potencial y gaps de cobertura de Selmark.</p>',
            unsafe_allow_html=True)

        # ── 1. ZONAS DE EXPANSIÓN FÍSICA ────────────────────────────────────
        section('Oportunidad de expansión física por CCAA')
        st.markdown(
            '<p style="font-size:.82rem;color:#6B7280;max-width:900px;margin-bottom:1rem">'
            'CCAA donde las encuestadas compran lencería/baño en tienda física pero '
            '<strong>no mencionan Selmark</strong> espontáneamente. Son zonas con demanda '
            'física probada y baja notoriedad de Selmark → mayor potencial de expansión.</p>',
            unsafe_allow_html=True)

        if is_s1:
            fis_cols  = ['Canal_fisico_lenceria','Canal_fisico_bano']
            tom_cols_e = ['Top_of_mind_lenceria','Otras_marcas_lenceria',
                          'Top_of_mind_bano','Otras_marcas_bano']
        else:
            fis_cols  = ['Canal_fisico_deportiva','Canal_fisico_homewear']
            tom_cols_e = ['Top_of_mind_deporte','Otras_marcas_deporte',
                          'Top_of_mind_homewear','Otras_marcas_homewear']

        # Quién compra físicamente
        buys_physical = df[fis_cols].apply(
            lambda col: col.dropna().str.lower().str.contains('tienda|almacen|física|corte|mercer|outlet|corseter',
                                                               regex=True, na=False)
        ).any(axis=1)

        # Quién menciona Selmark
        def mentions_sel(row):
            for c in tom_cols_e:
                if c in row.index and pd.notna(row[c]) and 'selmark' in str(row[c]).lower():
                    return True
            return False
        mentions_selmark_mask = df.apply(mentions_sel, axis=1)

        df_phys_no_sel = df[buys_physical & ~mentions_selmark_mask]
        df_phys_sel    = df[buys_physical & mentions_selmark_mask]

        ccaa_opp = df_phys_no_sel['CCAA'].value_counts()
        ccaa_kno = df_phys_sel['CCAA'].value_counts()

        if not ccaa_opp.empty:
            c1, c2 = st.columns(2, gap='large')
            with c1:
                labels_r = list(ccaa_opp.index[:12])[::-1]
                vals_r   = list(ccaa_opp.values[:12])[::-1]
                pct_r    = [round(v / max(df[df['CCAA']==l].shape[0],1)*100, 1) for l,v in zip(labels_r, vals_r)]
                fig_opp = go.Figure(go.Bar(
                    y=labels_r, x=vals_r, orientation='h',
                    marker=dict(color='#F97316', line=dict(width=0)),
                    text=[f'{p:.0f}%' for p in pct_r],
                    textposition='outside', textfont=dict(size=10, color=FONT),
                ))
                fig_opp.update_layout(**lay('Compran físicamente, NO mencionan Selmark (nº encuestadas)', 380),
                    xaxis=dict(showgrid=False, showticklabels=False,
                               range=[0, max(vals_r)*1.35] if vals_r else [0,10], zeroline=False),
                    yaxis=dict(showgrid=False, tickfont=dict(size=10)),
                )
                st.plotly_chart(fig_opp, use_container_width=True, config=PC)

            with c2:
                # Perfil de edad en zonas de oportunidad
                age_opp = df_phys_no_sel['Grupo_edad'].value_counts().reindex(AGES).fillna(0)
                age_all = df[buys_physical]['Grupo_edad'].value_counts().reindex(AGES).fillna(0)
                idx_pct = (age_opp / max(int(age_opp.sum()), 1) * 100).round(1)
                base_pct= (age_all / max(int(age_all.sum()), 1) * 100).round(1)
                fig_age_opp = go.Figure()
                fig_age_opp.add_trace(go.Bar(
                    name='Sin Selmark', x=AGES, y=list(idx_pct),
                    marker=dict(color='#F97316', line=dict(width=0)),
                    text=[f'{v:.0f}%' for v in idx_pct], textposition='outside',
                    textfont=dict(size=10),
                ))
                fig_age_opp.add_trace(go.Bar(
                    name='Base compradores físicos', x=AGES, y=list(base_pct),
                    marker=dict(color='#CBD5E1', line=dict(width=0)),
                    text=[f'{v:.0f}%' for v in base_pct], textposition='outside',
                    textfont=dict(size=10),
                ))
                fig_age_opp.update_layout(**lay('Perfil de edad · zona de oportunidad vs. base', 300,
                    showlegend=True, legend=dict(orientation='h', y=1.08, x=0, font=dict(size=10))),
                    barmode='group',
                    xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                    yaxis=dict(showgrid=True, gridcolor=GRID, ticksuffix='%'),
                )
                st.plotly_chart(fig_age_opp, use_container_width=True, config=PC)

            # ── CCAA donde SÍ mencionan Selmark y compran físicamente → dónde abrir tienda
            hr()
            section('CCAA prioritarias para abrir tienda Selmark')
            st.markdown(
                '<p style="font-size:.82rem;color:#6B7280;max-width:900px;margin-bottom:1rem">'
                'Zonas donde las encuestadas <strong>compran en tienda física</strong> '
                'y <strong>sí mencionan Selmark</strong> espontáneamente. '
                'Son las CCAA con mayor receptividad a una tienda Selmark: la marca ya existe '
                'en la mente del consumidor y el hábito de compra física también.</p>',
                unsafe_allow_html=True)

            ccaa_sel_phys = df_phys_sel['CCAA'].value_counts()
            if not ccaa_sel_phys.empty:
                c1b, c2b = st.columns(2, gap='large')
                with c1b:
                    labels_sp = list(ccaa_sel_phys.index[:12])[::-1]
                    vals_sp   = list(ccaa_sel_phys.values[:12])[::-1]
                    # penetración: % de compradores físicos de esa CCAA que mencionan Selmark
                    pen_sp = []
                    for ccaa_n in labels_sp:
                        n_phys_ccaa = df[buys_physical & (df['CCAA']==ccaa_n)].shape[0] or 1
                        n_sel_ccaa  = df_phys_sel[df_phys_sel['CCAA']==ccaa_n].shape[0]
                        pen_sp.append(round(n_sel_ccaa/n_phys_ccaa*100, 1))

                    fig_sp = go.Figure(go.Bar(
                        y=labels_sp, x=vals_sp, orientation='h',
                        marker=dict(color='#1E3A8A', line=dict(width=0)),
                        text=[f'{p:.0f}%' for p in pen_sp],
                        textposition='outside', textfont=dict(size=10, color=FONT),
                    ))
                    fig_sp.update_layout(**lay('Nº encuestadas: compran físicamente + mencionan Selmark', 380),
                        xaxis=dict(showgrid=False, showticklabels=False,
                                   range=[0, max(vals_sp)*1.4] if vals_sp else [0,10], zeroline=False),
                        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
                    )
                    st.plotly_chart(fig_sp, use_container_width=True, config=PC)

                with c2b:
                    # Perfil de edad del segmento Selmark-físico
                    age_sp = df_phys_sel['Grupo_edad'].value_counts().reindex(AGES).fillna(0)
                    pct_sp = (age_sp / max(int(age_sp.sum()), 1) * 100).round(1)
                    fig_age_sp = go.Figure(go.Bar(
                        x=AGES, y=list(pct_sp),
                        marker=dict(color=[AGE_COLORS.get(a, P[0]) for a in AGES],
                                    line=dict(width=0)),
                        text=[f'{v:.0f}%' for v in pct_sp],
                        textposition='outside', textfont=dict(size=11, color=FONT),
                    ))
                    fig_age_sp.update_layout(**lay('Perfil de edad · compradoras físicas que mencionan Selmark', 280),
                        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                        yaxis=dict(showgrid=True, gridcolor=GRID, ticksuffix='%'),
                    )
                    st.plotly_chart(fig_age_sp, use_container_width=True, config=PC)

                # Insight boxes lado a lado
                top_sel_ccaa = ccaa_sel_phys.index[0] if len(ccaa_sel_phys) else '—'
                n_sel_top    = int(ccaa_sel_phys.iloc[0]) if len(ccaa_sel_phys) else 0
                top_opp_ccaa = ccaa_opp.index[0] if len(ccaa_opp) else '—'
                pct_46_opp   = (df_phys_no_sel['Grupo_edad']=='46+').sum() / max(len(df_phys_no_sel),1) * 100
                ins1, ins2 = st.columns(2, gap='large')
                with ins1:
                    st.markdown(
                        f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:14px 18px">'
                        f'<div style="font-size:.65rem;font-weight:700;color:#1E40AF;text-transform:uppercase;'
                        f'letter-spacing:.08em;margin-bottom:5px">Prioridad 1 — Abrir tienda</div>'
                        f'<p style="font-size:.8rem;color:#1E3A8A;margin:0">'
                        f'<strong>{top_sel_ccaa}</strong> concentra el mayor número de consumidoras '
                        f'que compran físicamente y ya conocen Selmark ({n_sel_top} encuestadas). '
                        f'Apertura de tienda con alta probabilidad de conversión inmediata.</p></div>',
                        unsafe_allow_html=True)
                with ins2:
                    st.markdown(
                        f'<div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;padding:14px 18px">'
                        f'<div style="font-size:.65rem;font-weight:700;color:#9A3412;text-transform:uppercase;'
                        f'letter-spacing:.08em;margin-bottom:5px">Prioridad 2 — Construir notoriedad</div>'
                        f'<p style="font-size:.8rem;color:#7C2D12;margin:0">'
                        f'<strong>{top_opp_ccaa}</strong> tiene alta demanda física pero baja mención de Selmark. '
                        f'El {pct_46_opp:.0f}% son 46+, el segmento de mayor fidelidad. '
                        f'Requiere inversión en notoriedad antes de apertura.</p></div>',
                        unsafe_allow_html=True)
            else:
                st.info('No hay encuestadas que compren físicamente y mencionen Selmark con los filtros actuales.')

        hr()

        # ── 2. DEPORTE × SELMARK ────────────────────────────────────────────
        section('Perfil deportivo · Oportunidad para la línea sport de Selmark')
        st.markdown(
            '<p style="font-size:.82rem;color:#6B7280;max-width:900px;margin-bottom:1rem">'
            'Análisis de hábitos deportivos de la muestra: qué deporte practican, '
            'con qué frecuencia y qué perfil de edad tiene cada deporte. '
            'Útil para orientar la propuesta de valor de la línea deportiva.</p>',
            unsafe_allow_html=True)

        dep_col = 'Deporte_que_realiza' if 'Deporte_que_realiza' in df.columns else None
        frec_col = 'Veces_deporte_semana' if 'Veces_deporte_semana' in df.columns else None

        if dep_col:
            # Normalizar y contar deportes
            dep_cts = Counter()
            dep_rows = []
            for idx_r, row in df.iterrows():
                val = row.get(dep_col, '')
                if pd.isna(val): continue
                for dep in str(val).split('|'):
                    dep = dep.strip().title()
                    dep_norm = {
                        'Running': 'Running/Correr', 'Correr': 'Running/Correr',
                        'Gimnasio': 'Gimnasio', 'Yoga': 'Yoga',
                        'Natacion': 'Natación', 'Natación': 'Natación',
                        'Pilates': 'Pilates', 'Caminar': 'Caminar/Senderismo',
                        'Senderismo': 'Caminar/Senderismo', 'Ciclismo': 'Ciclismo',
                        'Padel': 'Pádel', 'Pádel': 'Pádel', 'Tenis': 'Tenis',
                        'Ninguno': None,
                    }.get(dep, dep if dep and dep != 'Nan' else None)
                    if dep_norm:
                        dep_cts[dep_norm] += 1
                        dep_rows.append({'Deporte': dep_norm, 'GE': row.get('Grupo_edad','')})

            dep_df = pd.DataFrame(dep_rows)
            top_deps = [d for d,_ in dep_cts.most_common(8)]

            c1, c2 = st.columns(2, gap='large')
            with c1:
                top_items = dep_cts.most_common(10)
                labels_r = [x[0] for x in top_items][::-1]
                vals_r   = [x[1] for x in top_items][::-1]
                n_enc    = len(df) or 1
                pct_dep  = [round(v/n_enc*100,1) for v in vals_r]
                fig_dep = go.Figure(go.Bar(
                    y=labels_r, x=vals_r, orientation='h',
                    marker=dict(color=P[0], line=dict(width=0)),
                    text=[f'{p:.0f}%' for p in pct_dep],
                    textposition='outside', textfont=dict(size=10, color=FONT),
                ))
                fig_dep.update_layout(**lay('Deportes más practicados (% encuestadas)', 360),
                    xaxis=dict(showgrid=False, showticklabels=False,
                               range=[0, max(vals_r)*1.35] if vals_r else [0,10], zeroline=False),
                    yaxis=dict(showgrid=False, tickfont=dict(size=10)),
                )
                st.plotly_chart(fig_dep, use_container_width=True, config=PC)

            with c2:
                if frec_col:
                    # Normalizar frecuencia numérica
                    def norm_frec(v):
                        m = re.search(r'(\d+)', str(v))
                        return int(m.group(1)) if m else None
                    df['_frec_num'] = df[frec_col].apply(norm_frec)
                    frec_age = df.groupby('Grupo_edad')['_frec_num'].mean().reindex(AGES)
                    fig_frec = go.Figure(go.Bar(
                        x=AGES, y=list(frec_age.values),
                        marker=dict(color=[AGE_COLORS.get(a, P[0]) for a in AGES],
                                    line=dict(width=0)),
                        text=[f'{v:.1f}x/sem' if pd.notna(v) else '' for v in frec_age],
                        textposition='outside', textfont=dict(size=11, color=FONT),
                    ))
                    fig_frec.update_layout(**lay('Frecuencia media de deporte por grupo de edad (veces/semana)', 280),
                        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                        yaxis=dict(showgrid=True, gridcolor=GRID, tickfont=dict(size=10)),
                    )
                    st.plotly_chart(fig_frec, use_container_width=True, config=PC)
                    df.drop(columns=['_frec_num'], inplace=True, errors='ignore')

            # Deporte × grupo de edad — barras agrupadas
            if not dep_df.empty and top_deps:
                dep_age_pcts = {}
                for age in AGES:
                    n_age = (df['Grupo_edad'] == age).sum() or 1
                    sub_a = dep_df[dep_df['GE'] == age]
                    dep_age_pcts[age] = {d: sub_a[sub_a['Deporte']==d].shape[0]/n_age*100
                                         for d in top_deps}

                fig_da = go.Figure()
                for age in AGES:
                    fig_da.add_trace(go.Bar(
                        name=age, x=top_deps,
                        y=[round(dep_age_pcts[age].get(d,0),1) for d in top_deps],
                        marker=dict(color=AGE_COLORS.get(age, P[2]), line=dict(width=0)),
                        text=[f'{dep_age_pcts[age].get(d,0):.0f}%' for d in top_deps],
                        textposition='outside', textfont=dict(size=9),
                    ))
                fig_da.update_layout(**lay('% practicantes por deporte y grupo de edad', 380,
                    showlegend=True, legend=dict(orientation='h', y=1.06, x=0, font=dict(size=10))),
                    barmode='group',
                    xaxis=dict(showgrid=False, tickfont=dict(size=10), tickangle=-20),
                    yaxis=dict(showgrid=True, gridcolor=GRID, ticksuffix='%'),
                )
                st.plotly_chart(fig_da, use_container_width=True, config=PC)

            # Insight box deporte
            top_dep_name = dep_cts.most_common(1)[0][0] if dep_cts else '—'
            pct_young_dep = (dep_df[dep_df['GE']=='18–30'].shape[0] /
                             max((df['Grupo_edad']=='18–30').sum(), 1) * 100) if not dep_df.empty else 0
            pct_mid_dep   = (dep_df[dep_df['GE']=='31–45'].shape[0] /
                             max((df['Grupo_edad']=='31–45').sum(), 1) * 100) if not dep_df.empty else 0
            st.markdown(
                f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;'
                f'padding:16px 20px;margin-top:8px">'
                f'<div style="font-size:.75rem;font-weight:700;color:#1E40AF;margin-bottom:6px;'
                f'text-transform:uppercase;letter-spacing:.08em">Insight estratégico</div>'
                f'<p style="font-size:.82rem;color:#1E3A8A;margin:0">'
                f'El deporte más practicado es <strong>{top_dep_name}</strong>. '
                f'El grupo 18-30 tiene una tasa de práctica deportiva del {pct_young_dep:.0f}% '
                f'y el grupo 31-45 del {pct_mid_dep:.0f}%. '
                f'La línea sport de Selmark tiene mayor potencial de penetración en el segmento '
                f'31-45 que combina alta actividad deportiva con mayor poder adquisitivo.'
                f'</p></div>',
                unsafe_allow_html=True)

    except Exception as e:
        st.error(f'Error Estrategia: {e}'); st.code(traceback.format_exc())
