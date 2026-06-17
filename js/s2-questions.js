/* ============================================================
   SURVEY 2 — Ropa Deportiva & Homewear/Loungewear
   Question screen definitions
   ============================================================ */

window.SURVEY_ID = 'sport-loungewear';

window.SCREENS = [

  // ── INTRO ─────────────────────────────────────────────────
  {
    id: 'intro', type: 'intro',
    title: 'Encuesta sobre Ropa Deportiva y Homewear',
    definition: 'Cuando hablamos de <strong>homewear / loungewear</strong>, nos referimos a prendas cómodas y versátiles que pueden usarse tanto en casa como para salir de manera informal. Incluye desde conjuntos cómodos tipo chándal o punto (<em>in &amp; out</em>) hasta accesorios pensados para exterior, como gorros o bufandas.',
    paragraphs: [
      'Esta encuesta es completamente anónima. Tus respuestas nos ayudarán a mejorar nuestros productos y servicios.',
      'No hay respuestas correctas ni incorrectas. Responde con honestidad y según tu experiencia personal.',
    ],
    duration: '15–20 min',
  },

  // ── PEOPLE ────────────────────────────────────────────────
  {
    id: 'p1', section: 'Sobre ti',
    questions: [
      { id:'q1', num:1, text:'¿Código postal?', type:'text', required:true, placeholder:'Ej: 28001' },
      { id:'q2', num:2, text:'¿Qué edad tienes?', type:'number', required:true, placeholder:'Ej: 34', min:16, max:99 },
    ],
  },
  {
    id: 'p2', section: 'Sobre ti',
    questions: [{
      id:'q3', num:3, type:'single', required:true,
      text:'¿Cuál es la renta anual aproximada de tu hogar (suma de todos los ingresos)?',
      options:['Menos de 20.000 €','20.000 – 35.000 € (medio-bajo)','35.000 – 55.000 € (medio)','55.000 – 75.000 € (medio-alto)','Más de 75.000 € (alto)'],
    }],
  },
  {
    id: 'p3', section: 'Sobre ti',
    questions: [{
      id:'q4', num:4, type:'single', required:true,
      text:'¿Cuál es tu situación familiar actual?',
      options:['Vivo sin pareja, sin hijos','Vivo sin pareja, sin hijos, en casa de mis padres','Vivo sin pareja, con hijos en el hogar','Vivo sin pareja, con hijos fuera del hogar','Vivo con pareja, sin hijos','Vivo con pareja, con hijos en el hogar','Vivo con pareja, con hijos fuera del hogar'],
    }],
  },

  // ── LIFESTYLE ─────────────────────────────────────────────
  {
    id: 'ls_a', section: 'Estilo de vida',
    questions: [{
      id:'lifestyle_a', num:'5–7', type:'scale_block', required:true,
      text:'Indica tu grado de acuerdo con cada afirmación.',
      sub:'Escala del 1 (totalmente en desacuerdo) al 5 (totalmente de acuerdo).',
      rows:[
        { id:'q5', text:'Me cuesta cambiar de marca de ropa, suelo elegir la que llevo años usando.' },
        { id:'q6', text:'Compro siempre en los mismos supermercados.' },
        { id:'q7', text:'Prefiero planes tranquilos con gente de confianza a experiencias nuevas o desconocidas.' },
      ],
    }],
  },
  {
    id: 'ls_b', section: 'Estilo de vida',
    questions: [{
      id:'lifestyle_b', num:'8–10', type:'scale_block', required:true,
      text:'Indica tu grado de acuerdo con cada afirmación.',
      sub:'Escala del 1 (totalmente en desacuerdo) al 5 (totalmente de acuerdo).',
      rows:[
        { id:'q8',  text:'Busco marcas de ropa que mejoren la percepción que los demás tienen sobre mí.' },
        { id:'q9',  text:'Elijo restaurantes por su reputación y nivel, no solo por el precio.' },
        { id:'q10', text:'Invierto en cultura, viajes o experiencias que me aporten y me distingan de los demás.' },
      ],
    }],
  },
  {
    id: 'ls_c', section: 'Estilo de vida',
    questions: [{
      id:'lifestyle_c', num:'11–13', type:'scale_block', required:true,
      text:'Indica tu grado de acuerdo con cada afirmación.',
      sub:'Escala del 1 (totalmente en desacuerdo) al 5 (totalmente de acuerdo).',
      rows:[
        { id:'q11', text:'No tengo un estilo definido, me adapto según el momento y el contexto.' },
        { id:'q12', text:'Me gusta probar restaurantes o estilos de cocina que no conozco.' },
        { id:'q13', text:'Me adapto fácilmente a situaciones y contextos muy distintos.' },
      ],
    }],
  },
  {
    id: 'ls_d', section: 'Estilo de vida',
    questions: [{
      id:'lifestyle_d', num:'14–16', type:'scale_block', required:true,
      text:'Indica tu grado de acuerdo con cada afirmación.',
      sub:'Escala del 1 (totalmente en desacuerdo) al 5 (totalmente de acuerdo).',
      rows:[
        { id:'q14', text:'Valoro más el origen, la proximidad y el impacto de lo que como que el propio precio.' },
        { id:'q15', text:'Prefiero hacer cosas que me aporten, antes que planes sin más.' },
        { id:'q16', text:'Prefiero que me regalen una experiencia a un anillo.' },
      ],
    }],
  },

  // ── FRECUENCIA DE COMPRA ──────────────────────────────────
  {
    id: 'fc1', section: 'Compra',
    questions: [
      { id:'q17', num:17, text:'¿Cuándo fue tu última compra de ropa de deporte?', type:'open', required:true, placeholder:'Ej: hace 2 meses, el mes pasado...' },
      { id:'q18', num:18, text:'¿Cuándo fue tu última compra de homewear/loungewear?', type:'open', required:true, placeholder:'Ej: hace 6 meses, este año...' },
    ],
  },
  {
    id: 'fc2', section: 'Compra',
    questions: [{
      id:'q19', num:19, type:'single', required:true,
      text:'¿Con qué frecuencia sueles comprar ropa?',
      options:['Cada semana','Una vez al mes','Cada 2 – 3 meses','Cada 6 meses','Solo cuando lo necesito o se rompe'],
    }],
  },
  {
    id: 'fc3', section: 'Compra',
    questions: [{ id:'q20', num:20, text:'¿Cuándo fue tu última compra de moda?', type:'open', required:true, placeholder:'Ej: este mes, hace 2 meses...' }],
  },

  // ── SHARE OF WALLET ───────────────────────────────────────
  {
    id: 'sw1', section: 'Gasto',
    questions: [
      { id:'q21', num:21, text:'¿Cuánto sueles gastarte en ropa de deporte?', type:'open', required:true, placeholder:'Ej: 50 €, entre 30 y 80 €...' },
      { id:'q22', num:22, text:'¿Cuánto sueles gastarte en ropa homewear/loungewear?', type:'open', required:true, placeholder:'Ej: 30 €, unos 60 €...' },
    ],
  },
  {
    id: 'tm1', section: 'Gasto',
    questions: [{ id:'q23', num:23, text:'¿Cuál es la marca más cara en la que has comprado en el último año?', type:'open', required:true, placeholder:'Nombre de la marca' }],
  },
  {
    id: 'tm2', section: 'Gasto',
    questions: [{
      id:'q24', num:24, type:'single', required:true,
      text:'¿Cuánto gastas aproximadamente al mes en ropa?',
      options:['Menos de 200 €','200 – 500 €','500 – 1.000 €','1.000 – 2.000 €','Más de 2.000 €'],
    }],
  },
  {
    id: 'tm3', section: 'Gasto',
    questions: [{
      id:'q25', num:25, type:'dichotomy', required:true,
      text:'¿Qué prefieres? Elige una opción en cada fila.',
      pairs:[
        { id:'d1', a:'Gimnasio',          b:'Deporte al aire libre' },
        { id:'d2', a:'Colores neutros',    b:'Colores vividos' },
        { id:'d3', a:'Ajustado',           b:'Suelto / ligero' },
        { id:'d4', a:'Con diseño',         b:'Básico' },
        { id:'d5', a:'Teletrabajo en casa',b:'Ir a la oficina' },
      ],
    }],
  },

  // ── COMPRA EN DEPORTE ─────────────────────────────────────
  {
    id: 'cd1', section: 'Compra',
    questions: [
      { id:'q26', num:26, text:'¿Cuántas veces haces deporte a la semana?', type:'open', required:true, placeholder:'Ej: 3 veces' },
      { id:'q27', num:27, text:'¿Qué deporte realizas?', type:'open', required:true, placeholder:'Ej: running, yoga, natación...' },
      { id:'q28', num:28, text:'¿Cada cuánto tiempo compras ropa deportiva? ¿Dónde?', type:'open', required:true, placeholder:'Ej: cada temporada, en Decathlon...' },
    ],
  },
  {
    id: 'cd2', section: 'Compra',
    questions: [
      { id:'q29', num:29, type:'single', required:true,
        text:'¿Compras ropa deportiva cada temporada?',
        options:['Sí','No'],
      },
      { id:'q30', num:30, text:'¿Cuántas prendas distintas tienes para hacer deporte en tu armario?', type:'open', required:true, placeholder:'Número aproximado de conjuntos u outfits' },
    ],
  },
  {
    id: 'cd3', section: 'Compra',
    condition: (a) => a.q29 === 'No',
    questions: [{
      id:'q31', num:31, type:'single', required:true,
      text:'Si no compras por temporadas, ¿buscas una prenda que dure?',
      options:['Sí, 1 año','Sí, 2 años','Sí, +3 años','Para toda la vida','Hasta que venga otra que me guste más'],
    }],
  },

  // ── COMPRA EN HOMEWEAR ────────────────────────────────────
  {
    id: 'ch1', section: 'Compra',
    questions: [
      { id:'q32', num:32, type:'single', required:true,
        text:'¿Te compras ropa para usar exclusivamente en casa?',
        options:['Sí','No'],
      },
      { id:'q33', num:33, text:'Si compras ropa cómoda para casa, ¿qué tipo de prendas usas?', type:'open', required:false, placeholder:'Ej: pijama, chándal, camisón...', condition: (a) => a.q32 === 'Sí' },
    ],
  },
  {
    id: 'ch2', section: 'Compra',
    questions: [{
      id:'q34', num:34, type:'single', required:true,
      text:'¿Te molesta tener que cambiarte para ir a hacer algún recado cerca de casa (comprar el pan, pasear al perro…)?',
      options:['Sí','No'],
    }],
  },

  // ── MISIÓN Y OCASIÓN DE COMPRA ────────────────────────────
  {
    id: 'mc1', section: 'Compra',
    questions: [{
      id:'q35', num:35, type:'multi', required:true,
      text:'En los últimos 12 meses, ¿por qué motivos has comprado ropa? Marca todas las que apliquen.',
      options:['Se me ha gastado o roto','Me apetece un capricho','La vi y me encantó','Quiero probar algo diferente o renovar mi estilo','Mi cuerpo o mi vida ha cambiado y necesito ropa acorde'],
    }],
  },
  {
    id: 'oc1', section: 'Compra',
    questions: [{
      id:'q36', num:36, type:'multi', required:true,
      text:'¿En qué situación o momento sueles comprar ropa? Marca todas las que apliquen.',
      options:['En el día a día, compro sin necesitar una razón concreta','Una fecha o evento social próximo (boda, cena, reunión, etc.)','Un viaje o escapada planificada','Una etapa vital nueva: maternidad, postparto, postcirugía, cambio de peso','Ver algo en redes o en tienda que me llama la atención','En las rebajas o una promoción concreta'],
    }],
  },

  // ── MORFOLOGÍA ────────────────────────────────────────────
  {
    id: 'mo1', section: 'Tallas',
    questions: [
      { id:'q37', num:37, text:'¿Qué talla tienes de pantalón?', type:'open', required:true, placeholder:'Ej: 38, S, M...' },
      { id:'q38', num:38, text:'¿Qué talla tienes de camiseta?', type:'open', required:true, placeholder:'Ej: M, L, 40...' },
      { id:'q39', num:39, text:'¿Qué talla tienes de sujetador?', type:'open', required:true, placeholder:'Ej: 90B, 95C...' },
    ],
  },
  {
    id: 'mo2', section: 'Tallas',
    questions: [{
      id:'q40', num:40, type:'single', required:true,
      text:'¿Te cuesta encontrar tu talla en la mayoría de las marcas?',
      options:['Nunca, siempre encuentro','A veces, depende de la marca','A menudo','Siempre es un problema'],
    }],
  },
  {
    id: 'mo3', section: 'Tallas',
    condition: (a) => a.q40 && a.q40 !== 'Nunca, siempre encuentro',
    questions: [{
      id:'q41', num:41, type:'multi', required:false,
      text:'Si te cuesta encontrar tu talla, ¿cuál es el motivo principal? Marca todos los que apliquen.',
      options:[
        'Copa grande para mi contorno',
        'Copa pequeña para mi contorno',
        'Contorno entre dos tallas',
        'Asimetría de pecho',
        'Espalda ancha u hombros anchos',
        { value:'otro_talla', label:'Otro', open:true },
      ],
    }],
  },

  // ── DRIVERS ───────────────────────────────────────────────
  {
    id: 'dr1', section: 'Compra',
    questions: [{
      id:'q42', num:42, type:'multi', required:true,
      text:'¿Cuáles son los factores que más valoras? Marca todos los que apliquen.',
      options:['Comodidad y fit perfecto','Calidad del tejido y acabados','Tallaje amplio','Relación calidad-precio','Exclusivo y diferente','Diseño y estética','Sentirse atractiva','Durabilidad tras lavados','Asesoramiento personalizado','Que sea una marca reconocida','Que esté de moda o sea tendencia'],
    }],
  },
  {
    id: 'ba1', section: 'Compra',
    questions: [{
      id:'q43', num:43, type:'multi', required:true,
      text:'¿Qué factores te han hecho que decidas NO comprar algo? Marca todas las que apliquen.',
      options:['Dificultad para encontrar talla','Precio percibido elevado','Tirantes o aros que clavan o molestan','Miedo a comprar online sin probar','Proceso de devolución complicado','Poca confianza en la durabilidad','Probador incómodo','No encontrar mi línea (lactancia, postcirugía…)','Falta de asesoramiento',{ value:'otras_barrera', label:'Otras', open:true }],
    }],
  },

  // ── CANAL ─────────────────────────────────────────────────
  {
    id: 'ca1', section: 'Canal',
    questions: [{
      id:'q44', num:44, type:'multi', required:true,
      text:'¿En qué tipo de establecimiento físico compras ropa deportiva habitualmente? Marca todos los que apliquen.',
      options:['Tienda monomarca de ropa deportiva/homewear (Nike, Lululemon, Decathlon…)','Grandes almacenes (El Corte Inglés)','Moda generalista con sección sport (Oysho, H&M Sport, Zara Sport)','Outlet físico','Mercería o corsetería tradicional'],
    }],
  },
  {
    id: 'ca2', section: 'Canal',
    questions: [{
      id:'q45', num:45, type:'multi', required:true,
      text:'¿En qué tipo de establecimiento físico compras homewear habitualmente? Marca todos los que apliquen.',
      options:['Tienda monomarca especializada en ropa deportiva o homewear (Lululemon, Decathlon…)','Grandes almacenes (El Corte Inglés)','Tienda de moda generalista con sección home/lounge (Oysho, Primark, H&M…)','Tienda de lencería e íntimo (Women\'Secret, Intimissimi…)','Outlet físico'],
    }],
  },
  {
    id: 'ca3', section: 'Canal',
    questions: [{
      id:'q46', num:46, type:'single', required:true,
      text:'¿Compras ropa deportiva/homewear por internet?',
      options:['Sí, habitualmente','Sí, ocasionalmente','Lo he intentado, pero prefiero tienda física','No, nunca compro ropa deportiva/homewear online'],
    }],
  },
  {
    id: 'ca4', section: 'Canal',
    condition: (a) => a.q46 && a.q46.startsWith('Sí'),
    questions: [{
      id:'q47', num:47, type:'multi', required:true,
      text:'Si compras ropa deportiva online, ¿a través de qué canal? Marca todos los que apliquen.',
      options:['Ecommerce propio de la marca','Marketplace especializado','Marketplace generalista','Social commerce (Instagram Shop, TikTok Shop)','App móvil de la marca','Outlet o venta flash online (Privalia, Veepee…)'],
    }],
  },
  {
    id: 'ca5', section: 'Canal',
    condition: (a) => a.q46 && a.q46.startsWith('Sí'),
    questions: [{
      id:'q48', num:48, type:'multi', required:true,
      text:'Si compras homewear/loungewear online, ¿a través de qué canal? Marca todos los que apliquen.',
      options:['Ecommerce propio de la marca','Marketplace especializado','Marketplace generalista','Social commerce (Instagram Shop, TikTok Shop)','App móvil de la marca','Outlet o venta flash online (Privalia, Veepee…)'],
    }],
  },
  {
    id: 'ca6', section: 'Canal',
    questions: [
      { id:'q49', num:49, text:'¿Qué es lo que más valoras en tu experiencia de compra de ropa deportiva en el canal que usas habitualmente?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
      { id:'q50', num:50, text:'¿Qué es lo que más valoras en tu experiencia de compra de homewear en el canal que usas habitualmente?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
    ],
  },
  {
    id: 'ca7', section: 'Canal',
    condition: (a) => a.q46 && a.q46.startsWith('Sí'),
    questions: [{
      id:'q51', num:51, type:'multi', required:false,
      text:'Si compras ropa deportiva/homewear online, ¿qué aspectos de la experiencia digital valoras más?',
      options:['Web fácil de navegar y filtrar por talla','Fotos de alta calidad con diferentes cuerpos','Guía de tallas fiable y específica por modelo','Chat o asesoramiento online en tiempo real','Opción de recoger en tienda','Devolución gratuita garantizada','Privacidad en el packaging del envío'],
    }],
  },

  // ── MARCA – DEPORTE ───────────────────────────────────────
  {
    id: 'md1', section: 'Marca',
    questions: [{ id:'q52', num:52, text:'Cuando piensas en ropa deportiva, ¿cuál es la primera marca que te viene a la cabeza? Escribe solo una marca.', type:'open', required:true, placeholder:'Nombre de la marca' }],
  },
  {
    id: 'md2', section: 'Marca',
    questions: [{ id:'q53', num:53, text:'¿Y qué otras marcas de ropa deportiva recuerdas? Escribe las marcas que recuerdes.', type:'open', required:true, placeholder:'Escribe las marcas separadas por comas' }],
  },
  {
    id: 'md3', section: 'Marca',
    questions: [{
      id:'q54', num:54, type:'multi', required:true,
      text:'¿En cuál de las siguientes marcas compras deporte?',
      options:['Nike','Adidas','Selmark','Puma','Anita','Oysho','Triumph','H&M','Born Living Yoga','Black Limba','Énfasis','Alo','Calvin Klein',{ value:'otras_marcas', label:'Otras', open:true }],
    }],
  },
  {
    id: 'md4', section: 'Marca',
    questions: [
      { id:'q56', num:56, text:'¿Cuál es tu marca favorita de deporte y por qué?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
    ],
  },
  {
    id: 'md5', section: 'Marca',
    questions: [{
      id:'atrib_func_sport', num:'57', type:'scale_block', required:true,
      text:'Valora del 1 al 5 cada atributo funcional.',
      sub:'1 = poco importante, 5 = muy importante.',
      rows:[
        { id:'q57_1',  text:'Sujeción' },
        { id:'q57_2',  text:'Transpirabilidad' },
        { id:'q57_3',  text:'Compresión' },
        { id:'q57_4',  text:'Buena relación calidad-precio' },
        { id:'q57_5',  text:'Secado rápido' },
        { id:'q57_6',  text:'Variedad de tallas' },
        { id:'q57_7',  text:'Libertad de movimiento' },
        { id:'q57_8',  text:'Suavidad del tejido' },
        { id:'q57_9',  text:'Comodidad' },
        { id:'q57_10', text:'Resistencia y durabilidad' },
        { id:'q57_11', text:'Bolsillo o elementos prácticos' },
        { id:'q57_12', text:'Versatilidad' },
      ],
    }],
  },
  {
    id: 'md6', section: 'Marca',
    questions: [{
      id:'atrib_emoc_sport', num:'58', type:'scale_block', required:true,
      text:'Valora del 1 al 5 cada atributo emocional.',
      sub:'1 = poco importante, 5 = muy importante.',
      rows:[
        { id:'q58_1', text:'Estética' },
        { id:'q58_2', text:'Moderna' },
        { id:'q58_3', text:'Que refleje mi personalidad' },
        { id:'q58_4', text:'Que destaque' },
        { id:'q58_5', text:'Identificación con la marca' },
        { id:'q58_6', text:'Diseño' },
        { id:'q58_7', text:'Marca especialista' },
      ],
    }],
  },

  // ── COMUNICACIÓN – DEPORTE ────────────────────────────────
  {
    id: 'co1', section: 'Comunicación',
    questions: [{
      id:'q59', num:59, type:'ranking', required:false,
      text:'¿En cuáles de los siguientes lugares has visto ropa de deporte? Ordénalos por frecuencia de uso.',
      options:['Instagram','TikTok','YouTube','Escaparate de tienda','Revistas de moda','Ecommerce propio de la marca','Email marketing o newsletter','Publicidad exterior','Televisión','Cartelera','Valla publicitaria','Mupis','Marquesina'],
    }],
  },
  {
    id: 'co2', section: 'Comunicación',
    questions: [{
      id:'q60', num:60, type:'single', required:true,
      text:'¿Conoces a alguna influencer que promocione ropa deportiva?',
      options:[
        { value:'si', label:'Sí' },
        { value:'no', label:'No' },
      ],
    }, {
      id:'q60_quien', num:'', type:'open', required:false,
      text:'¿Cuál? Escribe su nombre.',
      condition: (a) => a.q60 === 'si',
      placeholder:'Nombre de la influencer',
    }],
  },
  {
    id: 'co3', section: 'Comunicación',
    questions: [{ id:'q61', num:61, text:'¿Qué opinión tienes de Pilar Rubio?', type:'open', required:true, placeholder:'Escribe tu respuesta...' }],
  },

  // ── MARCA – HOMEWEAR ─────────────────────────────────────
  {
    id: 'mh1', section: 'Marca',
    questions: [{ id:'q62', num:62, text:'Cuando piensas en homewear, ¿cuál es la primera marca que te viene a la cabeza? Escribe solo una marca.', type:'open', required:true, placeholder:'Nombre de la marca' }],
  },
  {
    id: 'mh2', section: 'Marca',
    questions: [{ id:'q63', num:63, text:'¿Y qué otras marcas de homewear recuerdas? Escribe las marcas que recuerdes.', type:'open', required:true, placeholder:'Escribe las marcas separadas por comas' }],
  },
  {
    id: 'mh3', section: 'Marca',
    questions: [{
      id:'q64', num:64, type:'multi', required:true,
      text:'¿En cuál de las siguientes marcas compras homewear?',
      options:['Punto Blanco','Massana','Selmark','Admas','Ysabel Mora','Triumph','Janira','Zara','Calvin Klein','Women Secret','H&M','El Corte Inglés',{ value:'otras_marcas', label:'Otras', open:true }],
    }],
  },
  {
    id: 'mh4', section: 'Marca',
    questions: [
      { id:'q66', num:66, text:'¿Cuál es tu marca favorita de homewear y por qué?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
    ],
  },
  {
    id: 'mh5', section: 'Marca',
    questions: [{
      id:'q67', num:67, type:'multi', required:true,
      text:'¿Qué atributos valoras a la hora de comprar homewear? Marca todos los que consideres.',
      options:['Suavidad del tejido','Durabilidad tras lavados','Tallas inclusivas','Facilidad de movimiento','No encoge','No transparenta','Cómoda','Cálida','Bonita','Estética','Para regalo','Familiar','Moderna','Clásica accesible','Para mi edad'],
    }],
  },

  // ── COMUNICACIÓN – HOMEWEAR ───────────────────────────────
  {
    id: 'co4', section: 'Comunicación',
    questions: [{
      id:'q68', num:68, type:'ranking', required:false,
      text:'¿En cuáles de los siguientes lugares has visto ropa de homewear? Ordénalos por frecuencia de uso.',
      options:['Instagram','TikTok','YouTube','Escaparate de tienda','Revistas de moda','Ecommerce propio de la marca','Email marketing o newsletter','Publicidad exterior','Televisión','Cartelera','Valla publicitaria','Mupis','Marquesina'],
    }],
  },
  {
    id: 'co5', section: 'Comunicación',
    questions: [{
      id:'q69', num:69, type:'single', required:true,
      text:'¿Conoces a alguna influencer que promocione ropa de homewear?',
      options:[
        { value:'si', label:'Sí' },
        { value:'no', label:'No' },
      ],
    }, {
      id:'q69_quien', num:'', type:'open', required:false,
      text:'¿Cuál? Escribe su nombre.',
      condition: (a) => a.q69 === 'si',
      placeholder:'Nombre de la influencer',
    }],
  },

  // ── PRODUCTO – DEPORTE ────────────────────────────────────
  {
    id: 'pr1', section: 'Producto',
    questions: [{
      id:'q70', num:70, type:'color_pick', required:true,
      text:'Elige tres colores que más te gusten en ropa deportiva.',
      sub:'Ajusta cada selector para elegir el color exacto que tienes en mente.',
    }],
  },
  {
    id: 'pr2', section: 'Producto',
    questions: [{
      id:'q71', num:71, type:'color_combos', required:true,
      text:'Crea 3 o más combinaciones de colores que más te gusten.',
      sub:'Selecciona un color de la paleta y añádelo a la combinación activa.',
    }],
  },
  {
    id: 'pr3', section: 'Producto',
    questions: [{
      id:'q72_select', num:72, type:'product_select', required:true,
      text:'¿Cuál te gusta más?',
      sub:'Haz clic en el producto que más te guste.',
      category: 'sport',
      intro: 'A continuación verás una selección de productos de ropa deportiva. Observa cada uno con atención.',
    }],
  },
  {
    id: 'pr4', section: 'Producto',
    questions: [
      { id:'q73', num:73, text:'¿Por qué es la que más te gusta?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
      { id:'q74', num:74, text:'¿Por qué las otras te han gustado menos?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
    ],
  },

  // ── PRODUCTO – HOMEWEAR ───────────────────────────────────
  {
    id: 'pr5', section: 'Producto',
    questions: [{
      id:'q75', num:75, type:'color_pick', required:true,
      text:'Elige tres colores que más te gusten en ropa homewear/loungewear.',
      sub:'Ajusta cada selector para elegir el color exacto que tienes en mente.',
    }],
  },
  {
    id: 'pr6', section: 'Producto',
    questions: [{
      id:'q76', num:76, type:'color_combos', required:true,
      text:'Crea 3 o más combinaciones de colores que más te gusten.',
      sub:'Selecciona un color de la paleta y añádelo a la combinación activa.',
    }],
  },
  {
    id: 'pr7', section: 'Producto',
    questions: [{
      id:'q77_select', num:77, type:'product_select', required:true,
      text:'¿Cuál te gusta más?',
      sub:'Haz clic en el producto que más te guste.',
      category: 'lounge',
      intro: 'A continuación verás una selección de productos de homewear. Observa cada uno con atención.',
    }],
  },
  {
    id: 'pr8', section: 'Producto',
    questions: [
      { id:'q78', num:78, text:'¿Por qué es la que más te gusta?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
      { id:'q79', num:79, text:'¿Por qué las otras te han gustado menos?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
    ],
  },

  // ── GRACIAS ───────────────────────────────────────────────
  {
    id: 'thanks', type: 'thanks',
    title: 'Gracias por participar',
    paragraphs: ['Tus respuestas han sido registradas con éxito. Tu opinión es muy valiosa para nosotros.'],
  },
];
