// ============================================================
//  NETLIFY SERVERLESS FUNCTION — admin-data
//  Esta función corre en el servidor de Netlify, nunca en
//  el navegador del usuario. La service_role key NUNCA se
//  expone al cliente.
//
//  Variables de entorno necesarias en Netlify:
//    SUPABASE_URL          → tu Project URL de Supabase
//    SUPABASE_SERVICE_KEY  → Settings > API > service_role (secret)
//    ADMIN_PASSWORD        → contraseña para el panel admin
// ============================================================

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json',
};

exports.handler = async (event) => {

  // Preflight CORS
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers: CORS_HEADERS, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers: CORS_HEADERS,
             body: JSON.stringify({ error: 'Método no permitido' }) };
  }

  // Parse body
  let body;
  try { body = JSON.parse(event.body || '{}'); }
  catch (e) {
    return { statusCode: 400, headers: CORS_HEADERS,
             body: JSON.stringify({ error: 'JSON inválido' }) };
  }

  // ── Verificar contraseña (server-side) ───────────────────
  const adminPwd = process.env.ADMIN_PASSWORD;
  if (!adminPwd || body.password !== adminPwd) {
    // Pequeño delay para dificultar ataques de fuerza bruta
    await new Promise(r => setTimeout(r, 500));
    return { statusCode: 401, headers: CORS_HEADERS,
             body: JSON.stringify({ error: 'Contraseña incorrecta' }) };
  }

  const SUPABASE_URL  = process.env.SUPABASE_URL;
  const SERVICE_KEY   = process.env.SUPABASE_SERVICE_KEY;

  if (!SUPABASE_URL || !SERVICE_KEY) {
    return { statusCode: 500, headers: CORS_HEADERS,
             body: JSON.stringify({ error: 'Función no configurada — añade las variables de entorno en Netlify' }) };
  }

  try {
    // ── Construir query Supabase REST API ─────────────────
    let url = `${SUPABASE_URL}/rest/v1/survey_responses?select=*&order=created_at.desc&limit=2000`;
    if (body.surveyFilter) url += `&survey_id=eq.${encodeURIComponent(body.surveyFilter)}`;
    if (body.statusFilter)  url += `&status=eq.${encodeURIComponent(body.statusFilter)}`;

    const response = await fetch(url, {
      headers: {
        'apikey':        SERVICE_KEY,
        'Authorization': `Bearer ${SERVICE_KEY}`,
        'Content-Type':  'application/json',
      },
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`Supabase error ${response.status}: ${errText}`);
    }

    const data = await response.json();
    return { statusCode: 200, headers: CORS_HEADERS,
             body: JSON.stringify({ data }) };

  } catch (e) {
    return { statusCode: 500, headers: CORS_HEADERS,
             body: JSON.stringify({ error: e.message }) };
  }
};
