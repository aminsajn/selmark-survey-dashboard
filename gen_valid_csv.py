"""Generate selmark_valid_responses.csv with all valid responses, ordered columns and readable names."""
import json, csv, sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import quality_check as qc

with open(r'C:\Users\ajulve\Downloads\selmark_respuestas_full.json', encoding='utf-8') as f:
    data = json.load(f)

completed = [r for r in data if r.get('status') == 'complete']
results   = [qc.assess_response(r) for r in completed]
valid     = [(r, res) for r, res in zip(completed, results) if res['verdict'] in ('OK', 'REVIEW')]

# ── Column order ──────────────────────────────────────────────────────────────
COLUMN_ORDER = {
    'lingerie-swim': [
        'q1','q2','q3','q4',
        'q6','q7','q8','q9','q10','q11','q12','q13','q14','q15','q16','q17',
        'q18','q19','q20','q21','q22','q23','q24','q25',
        'q26_d1','q26_d2','q26_d3','q26_d4','q26_d5',
        'q27','q28','q29','q30','q31','q32',
        'q33','q34','q35','q36','q37','q37_open_otro_talla','q38','q39','q39_open_otras_barrera',
        'q40','q41','q42','q43','q44','q45','q46','q47','q48',
        'q49','q50','q51','q51_open_otras_marcas','q53',
        'q54_1','q54_2','q54_3','q54_4','q54_5','q54_6',
        'q55_1','q55_2','q55_3','q55_4','q55_5','q55_6','q55_7',
        'q56','q57','q57_quien','q58',
        'q59','q60','q61','q61_open_otras_marcas','q63','q64','q65','q66','q66_quien',
        'q67','q68','q69_select','q70','q71',
        'q72','q73','q74_select','q75','q76',
        'producto_mostrado',
    ],
    'sport-loungewear': [
        'q1','q2','q3','q4',
        'q5','q6','q7','q8','q9','q10','q11','q12','q13','q14','q15','q16',
        'q17','q18','q19','q20','q21','q22','q23','q24',
        'q25_d1','q25_d2','q25_d3','q25_d4','q25_d5',
        'q26','q27','q28','q29','q30','q31','q32','q33','q34',
        'q35','q36','q37','q38','q39','q40','q41','q41_open_otro_talla',
        'q42','q43','q43_open_otras_barrera','q44','q45','q46','q47','q48','q49','q50','q51',
        'q52','q53','q54','q54_open_otras_marcas','q56',
        'q57_1','q57_2','q57_3','q57_4','q57_5','q57_6',
        'q57_7','q57_8','q57_9','q57_10','q57_11','q57_12',
        'q58_1','q58_2','q58_3','q58_4','q58_5','q58_6','q58_7',
        'q59','q60','q60_quien','q61',
        'q62','q63','q64','q64_open_otras_marcas','q66','q67','q68','q69','q69_quien',
        'q70','q71','q72_select','q73','q74',
        'q75','q76','q77_select','q78','q79',
        'producto_mostrado',
    ],
}

# ── Readable column names ─────────────────────────────────────────────────────
QUESTION_LABELS = {
    # Shared / sociodemographic
    'q1': 'Codigo_postal',
    'q2': 'Edad',
    'q3': 'Renta_anual_hogar',
    'q4': 'Situacion_familiar',
    # Lingerie-swim lifestyle
    'q6_ls':  'LS_cuesta_cambiar_marca',
    'q7_ls':  'LS_siempre_mismo_supermercado',
    'q8_ls':  'LS_prefiere_planes_tranquilos',
    'q9_ls':  'LS_busca_marcas_por_percepcion',
    'q10_ls': 'LS_elige_restaurante_por_reputacion',
    'q11_ls': 'LS_invierte_en_cultura_viajes',
    'q12_ls': 'LS_sin_estilo_definido',
    'q13_ls': 'LS_prueba_restaurantes_nuevos',
    'q14_ls': 'LS_se_adapta_facilmente',
    'q15_ls': 'LS_valora_origen_impacto',
    'q16_ls': 'LS_prefiere_actividades_con_aporte',
    'q17_ls': 'LS_prefiere_experiencia_a_anillo',
    # Sport-loungewear lifestyle (q5-q16)
    'q5_sl':  'LS_cuesta_cambiar_marca',
    'q6_sl':  'LS_siempre_mismo_supermercado',
    'q7_sl':  'LS_prefiere_planes_tranquilos',
    'q8_sl':  'LS_busca_marcas_por_percepcion',
    'q9_sl':  'LS_elige_restaurante_por_reputacion',
    'q10_sl': 'LS_invierte_en_cultura_viajes',
    'q11_sl': 'LS_sin_estilo_definido',
    'q12_sl': 'LS_prueba_restaurantes_nuevos',
    'q13_sl': 'LS_se_adapta_facilmente',
    'q14_sl': 'LS_valora_origen_impacto',
    'q15_sl': 'LS_prefiere_actividades_con_aporte',
    'q16_sl': 'LS_prefiere_experiencia_a_anillo',
}

# Per-survey readable labels (qID -> label)
LABELS = {
    'lingerie-swim': {
        'q1':'Codigo_postal', 'q2':'Edad', 'q3':'Renta_anual_hogar', 'q4':'Situacion_familiar',
        'q6':'LS_cuesta_cambiar_marca', 'q7':'LS_mismo_supermercado', 'q8':'LS_planes_tranquilos',
        'q9':'LS_marcas_por_percepcion', 'q10':'LS_restaurante_reputacion', 'q11':'LS_cultura_viajes',
        'q12':'LS_sin_estilo', 'q13':'LS_restaurantes_nuevos', 'q14':'LS_se_adapta',
        'q15':'LS_origen_impacto', 'q16':'LS_actividades_aporte', 'q17':'LS_experiencia_vs_anillo',
        'q18':'Ultima_compra_lenceria', 'q19':'Ultima_compra_bano',
        'q20':'Frecuencia_compra_ropa', 'q21':'Ultima_compra_moda',
        'q22':'Gasto_lenceria_por_compra', 'q23':'Gasto_bano_por_compra',
        'q24':'Marca_mas_cara_ultimo_ano', 'q25':'Gasto_mensual_ropa',
        'q26_d1':'Dic_Playa_vs_Montana', 'q26_d2':'Dic_Colores_neutros_vs_vividos',
        'q26_d3':'Dic_Con_vs_Sin_estampado', 'q26_d4':'Dic_Con_diseno_vs_Basico',
        'q26_d5':'Dic_Duradero_vs_Moda',
        'q27':'Banadores_en_armario', 'q28':'Banadores_usados_temporada',
        'q29':'Compra_banadores_nuevos_verano', 'q30':'Aprovecha_rebajas_post_verano',
        'q31':'Motivos_compra_ropa', 'q32':'Momentos_compra_ropa',
        'q33':'Talla_pantalon', 'q34':'Talla_camiseta', 'q35':'Talla_sujetador',
        'q36':'Dificultad_encontrar_talla', 'q37':'Motivo_dificultad_talla',
        'q38':'Factores_valorados_compra', 'q39':'Factores_frenan_compra',
        'q40':'Canal_fisico_lenceria', 'q41':'Canal_fisico_bano',
        'q42':'Compra_lenceria_bano_online', 'q43':'Canal_online_lenceria',
        'q44':'Canal_online_bano', 'q45':'Que_valora_al_comprar',
        'q46':'Experiencia_compra_lenceria', 'q47':'Experiencia_compra_bano',
        'q48':'Experiencia_digital_lenceria_bano',
        'q49':'Top_of_mind_lenceria', 'q50':'Otras_marcas_lenceria',
        'q37_open_otro_talla':'Talla_otro_especificar', 'q39_open_otras_barrera':'Barrera_compra_otra_especificar',
        'q51':'Marcas_donde_compra_lenceria', 'q51_open_otras_marcas':'Marcas_lenceria_otras_especificar',
        'q53':'Marca_favorita_lenceria_motivo',
        'q54_1':'Func_lenc_Ajuste_sujecion', 'q54_2':'Func_lenc_Duracion',
        'q54_3':'Func_lenc_Variedad_tallas', 'q54_4':'Func_lenc_Comodidad',
        'q54_5':'Func_lenc_Calidad_precio', 'q54_6':'Func_lenc_Suavidad_tejido',
        'q55_1':'Emoc_lenc_Estetica', 'q55_2':'Emoc_lenc_Moderna',
        'q55_3':'Emoc_lenc_Refleja_personalidad', 'q55_4':'Emoc_lenc_Destaca',
        'q55_5':'Emoc_lenc_Identificacion_marca', 'q55_6':'Emoc_lenc_Diseno',
        'q55_7':'Emoc_lenc_Marca_especialista',
        'q56':'Visibilidad_lenceria_canales', 'q57':'Influencer_lenceria_sino',
        'q57_quien':'Influencer_lenceria_nombre', 'q58':'Opinion_Pilar_Rubio',
        'q59':'Top_of_mind_bano', 'q60':'Otras_marcas_bano',
        'q61':'Marcas_donde_compra_bano', 'q61_open_otras_marcas':'Marcas_bano_otras_especificar',
        'q63':'Marca_favorita_bano_motivo',
        'q64':'Atributos_valorados_bano',
        'q65':'Visibilidad_bano_canales', 'q66':'Influencer_bano_sino',
        'q66_quien':'Influencer_bano_nombre',
        'q67':'Colores_favoritos_lenceria', 'q68':'Combinaciones_colores_lenceria',
        'q69_select':'Producto_lenceria_elegido', 'q70':'Por_que_gusta_mas_lenc',
        'q71':'Por_que_otros_gustan_menos_lenc',
        'q72':'Colores_favoritos_bano', 'q73':'Combinaciones_colores_bano',
        'q74_select':'Producto_bano_elegido', 'q75':'Por_que_gusta_mas_bano',
        'q76':'Por_que_otros_gustan_menos_bano',
        'producto_mostrado':'Triada_producto_mostrada',
    },
    'sport-loungewear': {
        'q1':'Codigo_postal', 'q2':'Edad', 'q3':'Renta_anual_hogar', 'q4':'Situacion_familiar',
        'q5':'LS_cuesta_cambiar_marca', 'q6':'LS_mismo_supermercado', 'q7':'LS_planes_tranquilos',
        'q8':'LS_marcas_por_percepcion', 'q9':'LS_restaurante_reputacion', 'q10':'LS_cultura_viajes',
        'q11':'LS_sin_estilo', 'q12':'LS_restaurantes_nuevos', 'q13':'LS_se_adapta',
        'q14':'LS_origen_impacto', 'q15':'LS_actividades_aporte', 'q16':'LS_experiencia_vs_anillo',
        'q17':'Ultima_compra_ropa_deportiva', 'q18':'Ultima_compra_homewear',
        'q19':'Frecuencia_compra_ropa', 'q20':'Ultima_compra_moda',
        'q21':'Gasto_ropa_deportiva_por_compra', 'q22':'Gasto_homewear_por_compra',
        'q23':'Marca_mas_cara_ultimo_ano', 'q24':'Gasto_mensual_ropa',
        'q25_d1':'Dic_Gimnasio_vs_Aire_libre', 'q25_d2':'Dic_Colores_neutros_vs_vividos',
        'q25_d3':'Dic_Ajustado_vs_Suelto', 'q25_d4':'Dic_Con_diseno_vs_Basico',
        'q25_d5':'Dic_Teletrabajo_vs_Oficina',
        'q26':'Veces_deporte_semana', 'q27':'Deporte_que_realiza',
        'q28':'Frecuencia_lugar_compra_deportiva',
        'q29':'Compra_ropa_deportiva_cada_temporada', 'q30':'Prendas_deportivas_armario',
        'q31':'Duracion_buscada', 'q32':'Ropa_exclusiva_para_casa',
        'q33':'Tipo_prendas_para_casa', 'q34':'Molesta_cambiarse_recados',
        'q35':'Motivos_compra_ropa', 'q36':'Momentos_compra_ropa',
        'q37':'Talla_pantalon', 'q38':'Talla_camiseta', 'q39':'Talla_sujetador',
        'q40':'Dificultad_encontrar_talla', 'q41':'Motivo_dificultad_talla',
        'q41_open_otro_talla':'Talla_otro_especificar',
        'q42':'Factores_valorados_compra', 'q43':'Factores_frenan_compra',
        'q43_open_otras_barrera':'Barrera_compra_otra_especificar',
        'q44':'Canal_fisico_deportiva', 'q45':'Canal_fisico_homewear',
        'q46':'Compra_deporte_homewear_online',
        'q47':'Canal_online_deportiva', 'q48':'Canal_online_homewear',
        'q49':'Experiencia_compra_deportiva', 'q50':'Experiencia_compra_homewear',
        'q51':'Experiencia_digital_deporte_homewear',
        'q52':'Top_of_mind_deporte', 'q53':'Otras_marcas_deporte',
        'q54':'Marcas_donde_compra_deporte', 'q54_open_otras_marcas':'Marcas_deporte_otras_especificar',
        'q56':'Marca_favorita_deporte_motivo',
        'q57_1':'Func_sport_Sujecion', 'q57_2':'Func_sport_Transpirabilidad',
        'q57_3':'Func_sport_Compresion', 'q57_4':'Func_sport_Calidad_precio',
        'q57_5':'Func_sport_Secado_rapido', 'q57_6':'Func_sport_Variedad_tallas',
        'q57_7':'Func_sport_Libertad_movimiento', 'q57_8':'Func_sport_Suavidad_tejido',
        'q57_9':'Func_sport_Comodidad', 'q57_10':'Func_sport_Resistencia_durabilidad',
        'q57_11':'Func_sport_Bolsillos_practicos', 'q57_12':'Func_sport_Versatilidad',
        'q58_1':'Emoc_sport_Estetica', 'q58_2':'Emoc_sport_Moderna',
        'q58_3':'Emoc_sport_Refleja_personalidad', 'q58_4':'Emoc_sport_Destaca',
        'q58_5':'Emoc_sport_Identificacion_marca', 'q58_6':'Emoc_sport_Diseno',
        'q58_7':'Emoc_sport_Marca_especialista',
        'q59':'Visibilidad_deporte_canales',
        'q60':'Influencer_deporte_sino', 'q60_quien':'Influencer_deporte_nombre',
        'q61':'Opinion_Pilar_Rubio',
        'q62':'Top_of_mind_homewear', 'q63':'Otras_marcas_homewear',
        'q64':'Marcas_donde_compra_homewear', 'q64_open_otras_marcas':'Marcas_homewear_otras_especificar',
        'q66':'Marca_favorita_homewear_motivo',
        'q67':'Atributos_valorados_homewear',
        'q68':'Visibilidad_homewear_canales',
        'q69':'Influencer_homewear_sino', 'q69_quien':'Influencer_homewear_nombre',
        'q70':'Colores_favoritos_deporte', 'q71':'Combinaciones_colores_deporte',
        'q72_select':'Producto_deporte_elegido', 'q73':'Por_que_gusta_mas_deporte',
        'q74':'Por_que_otros_gustan_menos_deporte',
        'q75':'Colores_favoritos_homewear', 'q76':'Combinaciones_colores_homewear',
        'q77_select':'Producto_homewear_elegido', 'q78':'Por_que_gusta_mas_homewear',
        'q79':'Por_que_otros_gustan_menos_homewear',
        'producto_mostrado':'Triada_producto_mostrada',
    },
}

DICHOTOMY_PAIRS = {
    'lingerie-swim': {
        'q26': { 'd1':['Playa','Montana'], 'd2':['Colores neutros','Colores vividos'],
                 'd3':['Con estampado','Sin estampado'], 'd4':['Con diseno','Basico'],
                 'd5':['Producto duradero','Estar a la moda'],
                 # column aliases used in COLUMN_ORDER
                 'q26_d1': 'd1', 'q26_d2': 'd2', 'q26_d3': 'd3', 'q26_d4': 'd4', 'q26_d5': 'd5' },
    },
    'sport-loungewear': {
        'q25': { 'd1':['Gimnasio','Deporte al aire libre'], 'd2':['Colores neutros','Colores vividos'],
                 'd3':['Ajustado','Suelto'], 'd4':['Con diseno','Basico'],
                 'd5':['Teletrabajo en casa','Ir a la oficina'],
                 'q25_d1': 'd1', 'q25_d2': 'd2', 'q25_d3': 'd3', 'q25_d4': 'd4', 'q25_d5': 'd5' },
    },
}

def clean(text):
    """Remove newlines and extra whitespace from text."""
    if not isinstance(text, str): return text
    return ' '.join(text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ').split())

def get_val(col, answers, survey_id, product_shown):
    # Dichotomy columns e.g. q26_d1, q25_d3
    m = re.match(r'^(q\d+)_(d\d+)$', col)
    if m:
        qid, did = m.group(1), m.group(2)
        survey_dic = DICHOTOMY_PAIRS.get(survey_id) or {}
        pairs = (survey_dic.get(qid) or {}).get(did)
        raw = answers.get(qid)
        val = raw.get(did) if isinstance(raw, dict) else None
        if pairs and val:
            return pairs[0] if val == 'a' else pairs[1] if val == 'b' else val
        return ''
    if col == 'producto_mostrado':
        ps = product_shown or {}
        parts = []
        for k in ps:
            if not k.endswith('_triad'):
                parts.append(f"{k}:triada{ps.get(k+'_triad','?')}")
        return ' | '.join(parts)
    val = answers.get(col)
    if val is None: return ''
    if isinstance(val, list):
        if val and isinstance(val[0], dict) and 'hex' in val[0]:
            # Color picker — use hex as the value (name field also contains hex)
            return ' | '.join(c.get('hex', '') for c in val if c and c.get('hex'))
        if val and isinstance(val[0], dict) and 'colors' in val[0]:
            return ' | '.join(f"Combo{i+1}:{'+'.join(c.get('colors',[]))}" for i,c in enumerate(val))
        return ' | '.join(clean(str(v)) for v in val)
    if isinstance(val, dict):
        entries = list(val.items())
        if entries and isinstance(entries[0][1], (int, float)):
            return ' | '.join(f"{v}.{k}" for k,v in sorted(entries, key=lambda x: x[1]))
        if col.endswith('_select'):
            return ' | '.join(f"{k}:{v}" for k,v in entries)
        return json.dumps(val, ensure_ascii=False)
    return clean(str(val))

# ── Generate one CSV per survey ───────────────────────────────────────────────
meta_cols = ['ID_respuesta','Encuesta','ID_respondente','Fecha_inicio','Fecha_fin','Estado','QC_veredicto','Duracion_min']

for sid, filename in [
    ('lingerie-swim',    r'C:\Users\ajulve\Downloads\selmark_S1_lenceria_bano.csv'),
    ('sport-loungewear', r'C:\Users\ajulve\Downloads\selmark_S2_deporte_homewear.csv'),
]:
    survey_valid = [(r, res) for r, res in valid if r.get('survey_id') == sid]
    col_ids    = COLUMN_ORDER[sid]
    col_labels = [LABELS[sid].get(c, c) for c in col_ids]

    # Safety net: add any keys not in predefined order
    seen = set(col_ids)
    for r, _ in survey_valid:
        for k in (r.get('answers') or {}).keys():
            if k not in seen:
                seen.add(k)
                col_ids    = col_ids + [k]
                col_labels = col_labels + [k]

    header = meta_cols + col_labels
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row, res in survey_valid:
            answers       = row.get('answers') or {}
            product_shown = row.get('product_shown') or {}
            line = [
                row.get('id',''), sid, row.get('respondent_id',''),
                row.get('created_at',''), row.get('completed_at',''),
                row.get('status',''), res['verdict'], res['duration_min'],
            ]
            for qid in col_ids:
                line.append(get_val(qid, answers, sid, product_shown))
            writer.writerow(line)
    print(f'Saved: {filename}  ({len(survey_valid)} rows x {len(header)} cols)')
