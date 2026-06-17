/* ============================================================
   SURVEY 1 — Lencería & Baño
   Question screen definitions
   ============================================================ */

window.SURVEY_ID = 'lingerie-swim';

window.SCREENS = [

  // ── INTRO ─────────────────────────────────────────────────
  {
    id: 'intro', type: 'intro',
    title: 'Encuesta sobre Lencería y Baño',
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
      id:'lifestyle_a', num:'6–8', type:'scale_block', required:true,
      text:'Indica tu grado de acuerdo con cada afirmación.',
      sub:'Escala del 1 (totalmente en desacuerdo) al 5 (totalmente de acuerdo).',
      rows:[
        { id:'q6',  text:'Me cuesta cambiar de marca de ropa, suelo elegir la que llevo años usando.' },
        { id:'q7',  text:'Compro siempre en los mismos supermercados.' },
        { id:'q8',  text:'Prefiero planes tranquilos con gente de confianza a experiencias nuevas o desconocidas.' },
      ],
    }],
  },
  {
    id: 'ls_b', section: 'Estilo de vida',
    questions: [{
      id:'lifestyle_b', num:'9–11', type:'scale_block', required:true,
      text:'Indica tu grado de acuerdo con cada afirmación.',
      sub:'Escala del 1 (totalmente en desacuerdo) al 5 (totalmente de acuerdo).',
      rows:[
        { id:'q9',  text:'Busco marcas de ropa que mejoren la percepción que los demás tienen sobre mí.' },
        { id:'q10', text:'Elijo restaurantes por su reputación y nivel, no solo por el precio.' },
        { id:'q11', text:'Invierto en cultura, viajes o experiencias que me aporten y me distingan de los demás.' },
      ],
    }],
  },
  {
    id: 'ls_c', section: 'Estilo de vida',
    questions: [{
      id:'lifestyle_c', num:'12–14', type:'scale_block', required:true,
      text:'Indica tu grado de acuerdo con cada afirmación.',
      sub:'Escala del 1 (totalmente en desacuerdo) al 5 (totalmente de acuerdo).',
      rows:[
        { id:'q12', text:'No tengo un estilo definido, me adapto según el momento y el contexto.' },
        { id:'q13', text:'Me gusta probar restaurantes o estilos de cocina que no conozco.' },
        { id:'q14', text:'Me adapto fácilmente a situaciones y contextos muy distintos.' },
      ],
    }],
  },
  {
    id: 'ls_d', section: 'Estilo de vida',
    questions: [{
      id:'lifestyle_d', num:'15–17', type:'scale_block', required:true,
      text:'Indica tu grado de acuerdo con cada afirmación.',
      sub:'Escala del 1 (totalmente en desacuerdo) al 5 (totalmente de acuerdo).',
      rows:[
        { id:'q15', text:'Valoro más el origen, la proximidad y el impacto de lo que como que el propio precio.' },
        { id:'q16', text:'Prefiero hacer cosas que me aporten, antes que planes sin más.' },
        { id:'q17', text:'Prefiero que me regalen una experiencia a un anillo.' },
      ],
    }],
  },

  // ── FRECUENCIA DE COMPRA ──────────────────────────────────
  {
    id: 'fc1', section: 'Compra',
    questions: [
      { id:'q18', num:18, text:'¿Cuándo fue tu última compra de lencería?', type:'open', required:true, placeholder:'Ej: hace 3 meses, el mes pasado...' },
      { id:'q19', num:19, text:'¿Cuándo fue tu última compra de baño?', type:'open', required:true, placeholder:'Ej: el verano pasado, hace un año...' },
    ],
  },
  {
    id: 'fc2', section: 'Compra',
    questions: [{
      id:'q20', num:20, type:'single', required:true,
      text:'¿Con qué frecuencia sueles comprar ropa?',
      options:['Cada semana','Una vez al mes','Cada 2 – 3 meses','Cada 6 meses','Solo cuando lo necesito o se rompe'],
    }],
  },
  {
    id: 'fc3', section: 'Compra',
    questions: [{ id:'q21', num:21, text:'¿Cuándo fue tu última compra de moda?', type:'open', required:true, placeholder:'Ej: este mes, hace 2 meses...' }],
  },

  // ── SHARE OF WALLET ───────────────────────────────────────
  {
    id: 'sw1', section: 'Gasto',
    questions: [
      { id:'q22', num:22, text:'¿Cuánto sueles gastarte en lencería en cada compra?', type:'open', required:true, placeholder:'Ej: 30 €, entre 20 y 50 €...' },
      { id:'q23', num:23, text:'¿Cuánto sueles gastarte en baño en cada compra?', type:'open', required:true, placeholder:'Ej: 50 €, unos 80 €...' },
    ],
  },
  {
    id: 'tm1', section: 'Gasto',
    questions: [{ id:'q24', num:24, text:'¿Cuál es la marca más cara en la que has comprado en el último año?', type:'open', required:true, placeholder:'Nombre de la marca' }],
  },
  {
    id: 'tm2', section: 'Gasto',
    questions: [{
      id:'q25', num:25, type:'single', required:true,
      text:'¿Cuánto gastas aproximadamente al mes en ropa?',
      options:['Menos de 200 €','200 – 500 €','500 – 1.000 €','1.000 – 2.000 €','Más de 2.000 €'],
    }],
  },
  {
    id: 'tm3', section: 'Gasto',
    questions: [{
      id:'q26', num:26, type:'dichotomy', required:true,
      text:'¿Qué prefieres? Elige una opción en cada fila.',
      pairs:[
        { id:'d1', a:'Playa',          b:'Montaña' },
        { id:'d2', a:'Colores neutros', b:'Colores vividos' },
        { id:'d3', a:'Con estampado',   b:'Sin estampado' },
        { id:'d4', a:'Con diseño',      b:'Básico' },
        { id:'d5', a:'Producto duradero',b:'Estar a la moda' },
      ],
    }],
  },

  // ── COMPRA DE BAÑO ────────────────────────────────────────
  {
    id: 'cb1', section: 'Compra',
    questions: [
      { id:'q27', num:27, text:'¿Cuántos bañadores tienes en el armario?', type:'open', required:true, placeholder:'Número aproximado' },
      { id:'q28', num:28, text:'¿Cuántos bañadores usas por temporada?', type:'open', required:true, placeholder:'Número aproximado' },
    ],
  },
  {
    id: 'cb2', section: 'Compra',
    questions: [
      { id:'q29', num:29, type:'single', required:true,
        text:'¿Te compras bañadores o bikinis nuevos para verano?',
        options:['Sí','No'],
      },
      { id:'q30', num:30, type:'single', required:true,
        text:'¿Aprovechas las rebajas post verano para comprar ropa de baño para el verano que viene?',
        options:['Sí','No'],
      },
    ],
  },

  // ── MISIÓN DE COMPRA ──────────────────────────────────────
  {
    id: 'mc1', section: 'Compra',
    questions: [{
      id:'q31', num:31, type:'multi', required:true,
      text:'En los últimos 12 meses, ¿por qué motivos has comprado ropa? Marca todas las que apliquen.',
      options:['Se me ha gastado o roto','Me apetece darme un capricho','La vi y me encantó','Quiero probar algo diferente o renovar mi estilo','Mi cuerpo o mi vida ha cambiado y necesito ropa acorde'],
    }],
  },
  {
    id: 'oc1', section: 'Compra',
    questions: [{
      id:'q32', num:32, type:'multi', required:true,
      text:'¿En qué momento o situación sueles comprar ropa? Marca todas las que apliquen.',
      options:['En el día a día, compro sin necesitar una razón concreta','Una fecha o evento social próximo (boda, cena, reunión, etc.)','Un viaje o escapada planificada','Una etapa vital nueva: maternidad, postparto, postcirugía, cambio de peso','Ver algo en redes o en tienda que me llama la atención','En las rebajas o una promoción concreta'],
    }],
  },

  // ── MORFOLOGÍA ────────────────────────────────────────────
  {
    id: 'mo1', section: 'Tallas',
    questions: [
      { id:'q33', num:33, text:'¿Qué talla tienes de pantalón?', type:'open', required:true, placeholder:'Ej: 38, S, M...' },
      { id:'q34', num:34, text:'¿Qué talla tienes de camiseta?', type:'open', required:true, placeholder:'Ej: M, L, 40...' },
      { id:'q35', num:35, text:'¿Qué talla tienes de sujetador?', type:'open', required:true, placeholder:'Ej: 90B, 95C...' },
    ],
  },
  {
    id: 'mo2', section: 'Tallas',
    questions: [{
      id:'q36', num:36, type:'single', required:true,
      text:'¿Te cuesta encontrar tu talla en la mayoría de las marcas?',
      options:['Nunca, siempre encuentro','A veces, depende de la marca','A menudo','Siempre es un problema'],
    }],
  },
  {
    id: 'mo3', section: 'Tallas',
    condition: (a) => a.q36 && a.q36 !== 'Nunca, siempre encuentro',
    questions: [{
      id:'q37', num:37, type:'multi', required:false,
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
      id:'q38', num:38, type:'multi', required:true,
      text:'¿Cuáles son los factores que MÁS valoras? Marca todos los que apliquen.',
      options:['Comodidad y fit perfecto','Calidad del tejido y acabados','Tallaje amplio','Relación calidad-precio','Exclusivo y diferente','Diseño y estética','Sentirse atractiva','Durabilidad tras lavados','Asesoramiento personalizado','Que sea una marca reconocida','Que esté de moda o sea tendencia'],
    }],
  },
  {
    id: 'ba1', section: 'Compra',
    questions: [{
      id:'q39', num:39, type:'multi', required:true,
      text:'¿Qué factores te han hecho que decidas NO comprar algo? Marca todas las que apliquen.',
      options:['Dificultad para encontrar talla','Precio percibido elevado','Tirantes o aros que clavan o molestan','Miedo a comprar online sin probar','Proceso de devolución complicado','Poca confianza en la durabilidad','Probador incómodo','No encontrar mi línea (lactancia, postcirugía…)','Falta de asesoramiento',{ value:'otras_barrera', label:'Otras', open:true }],
    }],
  },

  // ── CANAL ─────────────────────────────────────────────────
  {
    id: 'ca1', section: 'Canal',
    questions: [{
      id:'q40', num:40, type:'multi', required:true,
      text:'¿En qué tipo de establecimiento físico compras lencería habitualmente? Marca todos los que apliquen.',
      options:['Tienda monomarca de lencería o baño','Grandes almacenes (El Corte Inglés)','Tienda multimarca especializada en lencería','Corsetería o mercería tradicional','Marcas de moda generalista','Outlet físico'],
    }],
  },
  {
    id: 'ca2', section: 'Canal',
    questions: [{
      id:'q41', num:41, type:'multi', required:true,
      text:'¿En qué tipo de establecimiento físico compras baño habitualmente? Marca todos los que apliquen.',
      options:['Tienda monomarca de lencería o baño','Grandes almacenes (El Corte Inglés)','Tienda multimarca especializada en lencería','Corsetería o mercería tradicional','Marcas de moda generalista','Outlet físico'],
    }],
  },
  {
    id: 'ca3', section: 'Canal',
    questions: [{
      id:'q42', num:42, type:'single', required:true,
      text:'¿Compras lencería/baño por internet?',
      options:['Sí, habitualmente','Sí, ocasionalmente','Lo he intentado, pero prefiero tienda física','No, nunca compro lencería/baño online'],
    }],
  },
  {
    id: 'ca4', section: 'Canal',
    condition: (a) => a.q42 && (a.q42.startsWith('Sí')),
    questions: [{
      id:'q43', num:43, type:'multi', required:true,
      text:'Si compras lencería online, ¿a través de qué canal? Marca todos los que apliquen.',
      options:['Ecommerce propio de la marca','Marketplace (Amazon, Zalando, Asos…)','Social commerce (Instagram Shop, TikTok Shop)','App móvil de la marca','Outlet o venta flash online (Privalia, Veepee…)'],
    }],
  },
  {
    id: 'ca5', section: 'Canal',
    condition: (a) => a.q42 && (a.q42.startsWith('Sí')),
    questions: [{
      id:'q44', num:44, type:'multi', required:true,
      text:'Si compras baño online, ¿a través de qué canal? Marca todos los que apliquen.',
      options:['Ecommerce propio de la marca','Marketplace (Amazon, Zalando, Asos…)','Social commerce (Instagram Shop, TikTok Shop)','App móvil de la marca','Outlet o venta flash online (Privalia, Veepee…)'],
    }],
  },
  {
    id: 'ca6', section: 'Canal',
    questions: [{
      id:'q45', num:45, type:'multi', required:true,
      text:'De lo siguiente, ¿qué valoras más cuando compras lencería/baño en cualquier canal? Marca todas las que apliquen.',
      options:['Poder medirme y que me asesoren','Probadores cómodos y privados','Guía de tallas fiable online','Devolución fácil y gratuita','Variedad de tallas incluyendo las mías','Precio competitivo'],
    }],
  },
  {
    id: 'ca7', section: 'Canal',
    questions: [
      { id:'q46', num:46, text:'¿Qué es lo que más valoras en tu experiencia de compra de lencería en el canal que usas habitualmente?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
      { id:'q47', num:47, text:'¿Qué es lo que más valoras en tu experiencia de compra de baño en el canal que usas habitualmente?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
    ],
  },
  {
    id: 'ca8', section: 'Canal',
    condition: (a) => a.q42 && (a.q42.startsWith('Sí')),
    questions: [{
      id:'q48', num:48, type:'multi', required:false,
      text:'Si compras lencería/baño online, ¿qué aspectos de la experiencia digital valoras más? Marca todos los que apliquen.',
      options:['Web fácil de navegar y filtrar por talla','Fotos de alta calidad con diferentes cuerpos','Guía de tallas fiable y específica por modelo','Chat o asesoramiento online en tiempo real','Opción de recoger en tienda','Devolución gratuita garantizada','Privacidad en el packaging del envío'],
    }],
  },

  // ── MARCA – LENCERÍA (top of mind primero, sin marcas) ─────
  {
    id: 'ma1', section: 'Marca',
    questions: [{ id:'q49', num:49, text:'Cuando piensas en lencería, ¿cuál es la primera marca que se te viene a la cabeza? Escribe solo una marca.', type:'open', required:true, placeholder:'Nombre de la marca' }],
  },
  {
    id: 'ma2', section: 'Marca',
    questions: [{ id:'q50', num:50, text:'¿Y qué otras marcas de lencería recuerdas? Escribe las marcas que recuerdes.', type:'open', required:true, placeholder:'Escribe las marcas separadas por comas' }],
  },
  {
    id: 'ma3', section: 'Marca',
    questions: [{
      id:'q51', num:51, type:'multi', required:true,
      text:'¿En cuál de las siguientes marcas compras lencería?',
      options:['Ysabel Mora','Janira','Selmark','Triumph','Women Secret','Intimissimi','Calvin Klein','Énfasis','Chantelle','Gisela','Admas','Selene','Playtex',{ value:'otras_marcas', label:'Otras', open:true }],
    }],
  },
  {
    id: 'ma4', section: 'Marca',
    questions: [
      { id:'q53', num:53, text:'¿Cuál es tu marca favorita de lencería y por qué?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
    ],
  },
  {
    id: 'ma5', section: 'Marca',
    questions: [{
      id:'atrib_func_lenc', num:'54', type:'scale_block', required:true,
      text:'Valora del 1 al 5 cada atributo funcional.',
      sub:'1 = poco importante, 5 = muy importante.',
      rows:[
        { id:'q54_1', text:'Buen ajuste y sujeción' },
        { id:'q54_2', text:'Duración de la prenda' },
        { id:'q54_3', text:'Variedad de tallas' },
        { id:'q54_4', text:'Cómoda' },
        { id:'q54_5', text:'Buena relación calidad-precio' },
        { id:'q54_6', text:'Suavidad del tejido' },
      ],
    }],
  },
  {
    id: 'ma6', section: 'Marca',
    questions: [{
      id:'atrib_emoc_lenc', num:'55', type:'scale_block', required:true,
      text:'Valora del 1 al 5 cada atributo emocional.',
      sub:'1 = poco importante, 5 = muy importante.',
      rows:[
        { id:'q55_1', text:'Estética' },
        { id:'q55_2', text:'Moderna' },
        { id:'q55_3', text:'Que refleje mi personalidad' },
        { id:'q55_4', text:'Que destaque' },
        { id:'q55_5', text:'Identificación con la marca' },
        { id:'q55_6', text:'Diseño' },
        { id:'q55_7', text:'Marca especialista' },
      ],
    }],
  },

  // ── COMUNICACIÓN – LENCERÍA ───────────────────────────────
  {
    id: 'co1', section: 'Comunicación',
    questions: [{
      id:'q56', num:56, type:'ranking', required:false,
      text:'¿En cuáles de los siguientes lugares has visto lencería? Ordénalos por frecuencia de uso (haz clic en el primero que más usas, luego el segundo, etc.).',
      options:['Instagram','TikTok','YouTube','Escaparate de tienda','Revistas de moda','Ecommerce propio de la marca','Email marketing o newsletter','Publicidad exterior','Televisión','Cartelera','Valla publicitaria','Mupis','Marquesina'],
    }],
  },
  {
    id: 'co2', section: 'Comunicación',
    questions: [{
      id:'q57', num:57, type:'single', required:true,
      text:'¿Conoces a alguna influencer que promocione lencería?',
      options:[
        { value:'si', label:'Sí' },
        { value:'no', label:'No' },
      ],
    }, {
      id:'q57_quien', num:'', type:'open', required:false,
      text:'¿Cuál? Escribe su nombre.',
      condition: (a) => a.q57 === 'si',
      placeholder:'Nombre de la influencer',
    }],
  },
  {
    id: 'co3', section: 'Comunicación',
    questions: [{ id:'q58', num:58, text:'¿Qué opinión tienes de Pilar Rubio?', type:'open', required:true, placeholder:'Escribe tu respuesta...' }],
  },

  // ── MARCA – BAÑO (top of mind primero) ───────────────────
  {
    id: 'mb1', section: 'Marca',
    questions: [{ id:'q59', num:59, text:'Cuando piensas en baño, ¿cuál es la primera marca que te viene a la cabeza? Escribe solo una marca.', type:'open', required:true, placeholder:'Nombre de la marca' }],
  },
  {
    id: 'mb2', section: 'Marca',
    questions: [{ id:'q60', num:60, text:'¿Y qué otras marcas de baño recuerdas? Escribe las marcas que recuerdes.', type:'open', required:true, placeholder:'Escribe las marcas separadas por comas' }],
  },
  {
    id: 'mb3', section: 'Marca',
    questions: [{
      id:'q61', num:61, type:'multi', required:true,
      text:'¿En cuál de las siguientes marcas compras ropa de baño?',
      options:['Selmark','Énfasis','Ysabel Mora','Gisela','Dolores Cortés','Chantelle','Banana Moon','Calzedonia','Oysho','H&M','Zara','Red Point','Basmar','Maryan Mehlhorn',{ value:'otras_marcas', label:'Otras', open:true }],
    }],
  },
  {
    id: 'mb4', section: 'Marca',
    questions: [
      { id:'q63', num:63, text:'¿Cuál es tu marca favorita de baño y por qué?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
    ],
  },
  {
    id: 'mb5', section: 'Marca',
    questions: [{
      id:'q64', num:64, type:'multi', required:true,
      text:'¿Qué atributos valoras a la hora de comprar baño? Marca todos los que consideres.',
      options:['Calidad del tejido','Ajuste y fit del bañador','Durabilidad','Comodidad','Variedad de tallas','No transparenta al mojarse','Secado rápido','Sujeción','Buena relación calidad-precio','Elegante','Clásica','Cómoda','De moda','Sexy','Moderna','Accesible o cercana','Especialista','Para mi cuerpo o mi edad'],
    }],
  },

  // ── COMUNICACIÓN – BAÑO ───────────────────────────────────
  {
    id: 'co4', section: 'Comunicación',
    questions: [{
      id:'q65', num:65, type:'ranking', required:false,
      text:'¿En cuáles de los siguientes lugares has visto ropa de baño? Ordénalos por frecuencia de uso.',
      options:['Instagram','TikTok','YouTube','Escaparate de tienda','Revistas de moda','Ecommerce propio de la marca','Email marketing o newsletter','Publicidad exterior','Televisión','Cartelera','Valla publicitaria','Mupis','Marquesina'],
    }],
  },
  {
    id: 'co5', section: 'Comunicación',
    questions: [{
      id:'q66', num:66, type:'single', required:true,
      text:'¿Conoces a alguna influencer que promocione ropa de baño?',
      options:[
        { value:'si', label:'Sí' },
        { value:'no', label:'No' },
      ],
    }, {
      id:'q66_quien', num:'', type:'open', required:false,
      text:'¿Cuál? Escribe su nombre.',
      condition: (a) => a.q66 === 'si',
      placeholder:'Nombre de la influencer',
    }],
  },

  // ── PRODUCTO – LENCERÍA ───────────────────────────────────
  {
    id: 'pr1', section: 'Producto',
    questions: [{
      id:'q67', num:67, type:'color_pick', required:true,
      text:'Elige tres colores que más te gusten para lencería.',
      sub:'Ajusta cada selector para elegir el color exacto que tienes en mente.',
    }],
  },
  {
    id: 'pr2', section: 'Producto',
    questions: [{
      id:'q68', num:68, type:'color_combos', required:true,
      text:'Crea 3 o más combinaciones de colores que más te gusten.',
      sub:'Selecciona un color de la paleta y añádelo a la combinación activa.',
    }],
  },
  {
    id: 'pr3', section: 'Producto',
    questions: [{
      id:'q69_select', num:69, type:'product_select', required:true,
      text:'¿Cuál te gusta más?',
      sub:'Haz clic en el producto que más te guste.',
      category: 'lingerie',
      intro: 'A continuación verás una selección de productos de lencería. Observa cada uno con atención.',
    }],
  },
  {
    id: 'pr4', section: 'Producto',
    questions: [
      { id:'q70', num:70, text:'¿Por qué es la que más te gusta?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
      { id:'q71', num:71, text:'¿Por qué las otras te han gustado menos?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
    ],
  },

  // ── PRODUCTO – BAÑO ───────────────────────────────────────
  {
    id: 'pr5', section: 'Producto',
    questions: [{
      id:'q72', num:72, type:'color_pick', required:true,
      text:'Elige tres colores que más te gusten para baño.',
      sub:'Ajusta cada selector para elegir el color exacto que tienes en mente.',
    }],
  },
  {
    id: 'pr6', section: 'Producto',
    questions: [{
      id:'q73', num:73, type:'color_combos', required:true,
      text:'Crea 3 o más combinaciones de colores que más te gusten.',
      sub:'Selecciona un color de la paleta y añádelo a la combinación activa.',
    }],
  },
  {
    id: 'pr7', section: 'Producto',
    questions: [{
      id:'q74_select', num:74, type:'product_select', required:true,
      text:'¿Cuál te gusta más?',
      sub:'Haz clic en el producto que más te guste.',
      category: 'swim',
      intro: 'A continuación verás una selección de productos de baño. Observa cada uno con atención.',
    }],
  },
  {
    id: 'pr8', section: 'Producto',
    questions: [
      { id:'q75', num:75, text:'¿Por qué es la que más te gusta?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
      { id:'q76', num:76, text:'¿Por qué las otras te han gustado menos?', type:'open', required:true, placeholder:'Escribe tu respuesta...' },
    ],
  },

  // ── GRACIAS ───────────────────────────────────────────────
  {
    id: 'thanks', type: 'thanks',
    title: 'Gracias por participar',
    paragraphs: ['Tus respuestas han sido registradas con éxito. Tu opinión es muy valiosa para nosotros.'],
  },
];
