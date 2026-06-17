import pandas as pd, warnings, traceback
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

warnings.filterwarnings('ignore')

s1 = pd.read_csv(r'C:\Users\ajulve\Downloads\selmark_S1_lenceria_bano.csv', encoding='utf-8-sig', dtype=str)

def fix(v):
    if not isinstance(v, str): return v
    try: return v.encode('latin1').decode('utf-8')
    except: return v

s1['Edad'] = pd.to_numeric(s1['Edad'], errors='coerce')
s1['Duracion_min'] = pd.to_numeric(s1['Duracion_min'], errors='coerce')
for col in s1.select_dtypes(include='object').columns:
    s1[col] = s1[col].apply(fix)

def age_group(age):
    if pd.isna(age): return None
    if age <= 30: return '18-30'
    if age <= 45: return '31-45'
    return '46+'

def geo_group(cp):
    if not isinstance(cp, str): return 'Desconocido'
    cp = cp.strip().zfill(5)
    if cp[:2] == '28': return 'Madrid'
    if cp[:2] == '08': return 'Barcelona'
    return 'Resto de Espana'

s1['Grupo_edad'] = s1['Edad'].apply(age_group)
s1['Zona'] = s1['Codigo_postal'].apply(geo_group)
s1['Zona_agrupada'] = s1['Zona'].apply(
    lambda z: 'Madrid / Barcelona' if z in ('Madrid','Barcelona') else 'Resto de Espana')
df = s1.copy()

P = ['#C17A7A','#BFA17A','#8C6672','#D4A99A','#7A8C7A','#9A8C6A','#C4A8C0','#6A7A8C']
PAPER = '#FFFFFF'
LAYOUT_BASE = dict(paper_bgcolor=PAPER, plot_bgcolor=PAPER,
    font=dict(family='Inter, sans-serif', color='#1A1616', size=11),
    margin=dict(t=40, b=30, l=10, r=10), coloraxis_showscale=False)

AGE_LABELS = ['18-30','31-45','46+']

# ---- TAB 2 ----
print('=== TAB 2 ===')
ls_cols = [c for c in df.columns if c.startswith('LS_')]
ls_labels = [c.replace('LS_','').replace('_',' ').capitalize() for c in ls_cols]
try:
    ls_age = df.groupby('Grupo_edad')[ls_cols].apply(
        lambda x: x.apply(pd.to_numeric, errors='coerce').mean()
    ).reindex(AGE_LABELS)
    ls_age.columns = ls_labels
    fig = px.imshow(ls_age.T.round(2), text_auto='.1f',
                    color_continuous_scale=[[0,'#FAF6F1'],[0.5,'#E8C4BE'],[1,'#C17A7A']], aspect='auto')
    print('Lifestyle heatmap: OK, shape', ls_age.shape)
except Exception as e:
    print('Lifestyle heatmap FAIL:')
    traceback.print_exc()

# ---- TAB 3 ----
print('=== TAB 3 ===')
try:
    freq = df['Frecuencia_compra_ropa'].value_counts().head(8)
    print('Frecuencia OK:', len(freq), 'values')
    spend_pairs = [('Gasto_lenceria_por_compra','Lenceria'),('Gasto_bano_por_compra','Bano')]
    for sc, label in spend_pairs:
        sp = df[sc].value_counts().head(7)
        print(f'Gasto {label} OK:', len(sp), 'values')
    fisico = [('Canal_fisico_lenceria','Lenceria'),('Canal_fisico_bano','Bano')]
    for cc, label in fisico:
        counts = Counter()
        for val in df[cc].dropna():
            for item in str(val).split('|'):
                item = item.strip()
                if item and len(item) > 1: counts[item] += 1
        print(f'Canal fisico {label} OK:', len(counts), 'values')
    print('TAB3: OK')
except Exception as e:
    print('TAB3 FAIL:')
    traceback.print_exc()

# ---- TAB 4 ----
print('=== TAB 4 ===')

def top_mentions(series, n=12):
    counts = Counter()
    for val in series.dropna():
        for item in str(val).split('|'):
            item = item.strip()
            if item and item.lower() not in ('nan','ninguna','ninguno','no','ns','n/a',''):
                counts[item.title()] += 1
    return pd.DataFrame(counts.most_common(n), columns=['Marca','Menciones'])

brand_cats = [
    ('Top_of_mind_lenceria','Otras_marcas_lenceria','Marcas_donde_compra_lenceria','Lenceria'),
    ('Top_of_mind_bano','Otras_marcas_bano','Marcas_donde_compra_bano','Bano'),
]
try:
    for tom, otras, usa, label in brand_cats:
        tom_s = df[tom] if tom in df.columns else pd.Series(dtype=str)
        otras_s = df[otras] if otras in df.columns else pd.Series(dtype=str)
        all_b = pd.concat([tom_s, otras_s], ignore_index=True)
        top_b = top_mentions(all_b, 12)
        fig = go.Figure(go.Bar(
            y=list(top_b['Marca']), x=list(top_b['Menciones']), orientation='h',
            marker=dict(color=list(top_b['Menciones']),
                        colorscale=[[0,'#E8C4BE'],[1,'#C17A7A']], line=dict(width=0)),
            text=list(top_b['Menciones'].astype(str)),
            textposition='outside', textfont=dict(size=10),
        ))
        fig.update_layout(**LAYOUT_BASE,
                          title=dict(text=f'Notoriedad {label}', font=dict(size=12), x=0),
                          xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                          yaxis=dict(tickfont=dict(size=10), autorange='reversed', showgrid=False),
                          showlegend=False, height=400)
        print(f'Brand {label}: OK')
except Exception as e:
    print('TAB4 brand FAIL:')
    traceback.print_exc()

# Func/emoc radar
func_cols = [c for c in df.columns if c.startswith('Func_lenc')]
func_labels_list = [c.replace('Func_lenc_','').replace('_',' ') for c in func_cols]
emoc_cols = [c for c in df.columns if c.startswith('Emoc_lenc')]
emoc_labels_list = [c.replace('Emoc_lenc_','').replace('_',' ') for c in emoc_cols]
try:
    func_df = df[func_cols].apply(pd.to_numeric, errors='coerce')
    vals = {'Total': func_df.mean().values}
    print('Func radar Total:', vals['Total'])
    for ag in AGE_LABELS:
        v = func_df[df['Grupo_edad']==ag].mean().values
        print(f'Func radar {ag}: OK shape {v.shape}')
    print('TAB4 radar: OK')
except Exception as e:
    print('TAB4 radar FAIL:')
    traceback.print_exc()

# Func heatmap
try:
    fa = df.groupby('Grupo_edad')[func_cols].apply(
        lambda x: x.apply(pd.to_numeric, errors='coerce').mean()
    ).reindex(AGE_LABELS)
    fa.columns = func_labels_list
    fig_hm = px.imshow(fa.T.round(2), text_auto='.1f',
                       color_continuous_scale=[[0,'#FAF6F1'],[0.5,'#E8C4BE'],[1,'#C17A7A']], aspect='auto')
    print('TAB4 func heatmap: OK shape', fa.shape)
except Exception as e:
    print('TAB4 func heatmap FAIL:')
    traceback.print_exc()

# ---- TAB 5 ----
print('=== TAB 5 ===')
try:
    counts = Counter()
    for val in df['Producto_lenceria_elegido'].dropna():
        for item in str(val).split('|'):
            item = item.strip()
            if ':' in item:
                prod = item.split(':')[1].strip()
                if prod: counts[prod] += 1
    top = pd.DataFrame(counts.most_common(10), columns=['Producto','Votos'])
    print('Product counts:', top.head(3).to_dict('records'))

    prod_age = []
    for ag in AGE_LABELS:
        sub = df[df['Grupo_edad']==ag]['Producto_lenceria_elegido'].dropna()
        sc2 = Counter()
        for val in sub:
            for item in str(val).split('|'):
                item = item.strip()
                if ':' in item:
                    p2 = item.split(':')[1].strip()
                    if p2: sc2[p2] += 1
        for p2, n in sc2.most_common(1):
            prod_age.append({'Edad': ag, 'Prod': p2[:20], 'N': n})
    print('Prod by age:', prod_age)

    if prod_age:
        pad = pd.DataFrame(prod_age)
        fig2 = go.Figure()
        for i, row in pad.iterrows():
            fig2.add_trace(go.Bar(
                name=row['Edad'], x=[row['Edad']], y=[row['N']],
                text=[row['Prod']], textposition='inside',
                marker=dict(color=P[i % len(P)], line=dict(width=0)),
                textfont=dict(size=9),
            ))
        fig2.update_layout(**LAYOUT_BASE, showlegend=False, height=320)
    print('TAB5: OK')
except Exception as e:
    print('TAB5 FAIL:')
    traceback.print_exc()

print('\nDone.')
