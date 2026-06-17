// ============================================================
//  CONFIGURACIÓN SELMARK SURVEYS
//  Edita este archivo antes de desplegar en Netlify
// ============================================================

const CONFIG = {

  // ----------------------------------------------------------
  // SUPABASE  →  crea cuenta gratis en https://supabase.com
  //   1. Nuevo proyecto
  //   2. Settings > API  →  copia Project URL y anon key
  //   3. SQL Editor  →  ejecuta el script de creación de tabla
  //      (ver instrucciones al final de este archivo)
  // ----------------------------------------------------------
  supabase: {
    url:     'https://ytmcbkgrnaytbxzkcwyc.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl0bWNia2dybmF5dGJ4emtjd3ljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA0NzQxNjEsImV4cCI6MjA5NjA1MDE2MX0.UFne_7Kz_CrOciODsrh1S4Yqpzqit_kXx2JBqtzvWok',
  },

  // ----------------------------------------------------------
  // CINT – URLs de redirección
  //   Reemplaza con las URLs reales que te proporcione Cint.
  //   {RID} se sustituye automáticamente por el respondent_id.
  // ----------------------------------------------------------
  cint: {
    complete:   'https://notch.insights.supply/cb?token=c08a1f86-b7ad-409b-b6a3-53f9d4457083&RID=',
    screenout:  'https://samplicio.us/s/ClientCallBack.aspx?RIS=20&RID=',
    duplicate:  'https://samplicio.us/s/ClientCallBack.aspx?RIS=30&RID=',
    quotaFull:  'https://samplicio.us/s/ClientCallBack.aspx?RIS=40&RID=',
  },

  // ----------------------------------------------------------
  // IMÁGENES DE PRODUCTO
  //   Coloca las imágenes en la carpeta img/products/
  //   Nombre sugerido: lenc-selmark-1.jpg, bano-comp-asp-2.jpg, etc.
  //   Cada bloque tiene 3 imágenes; se muestra 1 aleatoria por bloque.
  //
  //   Estructura:  survey1 → { lingerie, swim }  cada uno con block1/2/3
  //                survey2 → { sport, lounge }   cada uno con block1/2/3
  // ----------------------------------------------------------
  // Imágenes organizadas en TRÍADAS: cada tríada contiene 1 Selmark + 1 comp. aspiracional + 1 comp. baja.
  // La posición (1ª, 2ª, 3ª columna del PDF) determina la tríada.
  // Cada respondente ve aleatoriamente UNA tríada completa (3 imágenes en orden aleatorio).
  products: {
    'lingerie-swim': {
      lingerie: {
        // Tríada 1: columna izquierda del PDF
        // Tríada 2: columna central
        // Tríada 3: columna derecha
        triads: [
          [
            { id: 'lt1_s', src: 'img/products/lenc_p10_Image74.jpg', label: 'Producto A' },  // Selmark izq
            { id: 'lt1_a', src: 'img/products/lenc_p11_Image80.jpg', label: 'Producto B' },  // Asp izq (bra+shorts, modelo curvy)
            { id: 'lt1_b', src: 'img/products/lenc_p11_Image82.jpg', label: 'Producto C' },  // Baja izq
          ],
          [
            { id: 'lt2_s', src: 'img/products/lenc_p10_Image75.jpg', label: 'Producto A' },  // Selmark centro
            { id: 'lt2_a', src: 'img/products/lenc_p11_Image79.jpg', label: 'Producto B' },  // Asp centro (bra+briefs, modelo slim)
            { id: 'lt2_b', src: 'img/products/lenc_p11_Image83.jpg', label: 'Producto C' },  // Baja centro
          ],
          [
            { id: 'lt3_s', src: 'img/products/lenc_p10_Image76.jpg', label: 'Producto A' },  // Selmark dcha
            { id: 'lt3_a', src: 'img/products/lenc_p11_Image81.jpg', label: 'Producto B' },  // Asp dcha (lace bra)
            { id: 'lt3_b', src: 'img/products/lenc_p11_Image84.jpg', label: 'Producto C' },  // Baja dcha
          ],
        ],
      },
      swim: {
        triads: [
          [
            { id: 'st1_s', src: 'img/products/lenc_p12_Image87.jpg', label: 'Producto A' },  // Selmark izq (bikini rosa)
            { id: 'st1_a', src: 'img/products/lenc_p12_Image90.jpg', label: 'Producto B' },  // Asp izq (halter floral rosa)
            { id: 'st1_b', src: 'img/products/lenc_p13_Image96.jpg', label: 'Producto C' },  // Baja izq (bikini naranja)
          ],
          [
            { id: 'st2_s', src: 'img/products/lenc_p12_Image88.jpg', label: 'Producto A' },  // Selmark centro (bikini cebra)
            { id: 'st2_a', src: 'img/products/lenc_p12_Image91.jpg', label: 'Producto B' },  // Asp centro (bikini cebra marrón)
            { id: 'st2_b', src: 'img/products/lenc_p13_Image97.jpg', label: 'Producto C' },  // Baja centro (bikini amarillo)
          ],
          [
            { id: 'st3_s', src: 'img/products/lenc_p12_Image89.jpg', label: 'Producto A' },  // Selmark dcha (bikini floral azul)
            { id: 'st3_a', src: 'img/products/lenc_p12_Image92.jpg', label: 'Producto B' },  // Asp dcha (bañador verde)
            { id: 'st3_b', src: 'img/products/lenc_p13_Image95.jpg', label: 'Producto C' },  // Baja dcha (bañador rosa zip)
          ],
        ],
      },
    },
    'sport-loungewear': {
      sport: {
        triads: [
          [
            { id: 'spt1_s', src: 'img/products/sport_p11_Image78.jpg', label: 'Producto A' }, // Selmark 1
            { id: 'spt1_a', src: 'img/products/sport_p11_Image81.jpg', label: 'Producto B' }, // Asp 1
            { id: 'spt1_b', src: 'img/products/sport_p11_Image84.jpg', label: 'Producto C' }, // Baja 1
          ],
          [
            { id: 'spt2_s', src: 'img/products/sport_p11_Image79.jpg', label: 'Producto A' }, // Selmark 2
            { id: 'spt2_a', src: 'img/products/sport_p11_Image82.jpg', label: 'Producto B' }, // Asp 2
            { id: 'spt2_b', src: 'img/products/sport_p11_Image85.jpg', label: 'Producto C' }, // Baja 2
          ],
          [
            { id: 'spt3_s', src: 'img/products/sport_p11_Image80.jpg', label: 'Producto A' }, // Selmark 3
            { id: 'spt3_a', src: 'img/products/sport_p11_Image83.jpg', label: 'Producto B' }, // Asp 3
            { id: 'spt3_b', src: 'img/products/sport_p11_Image86.jpg', label: 'Producto C' }, // Baja 3
          ],
        ],
      },
      lounge: {
        triads: [
          [
            { id: 'lw1_s', src: 'img/products/sport_p12_Image89.jpg', label: 'Producto A' }, // Selmark 1
            { id: 'lw1_a', src: 'img/products/sport_p13_Image94.jpg', label: 'Producto B' }, // Asp 1
            { id: 'lw1_b', src: 'img/products/sport_p13_Image97.jpg', label: 'Producto C' }, // Baja 1
          ],
          [
            { id: 'lw2_s', src: 'img/products/sport_p12_Image90.jpg', label: 'Producto A' }, // Selmark 2
            { id: 'lw2_a', src: 'img/products/sport_p13_Image95.jpg', label: 'Producto B' }, // Asp 2
            { id: 'lw2_b', src: 'img/products/sport_p13_Image98.jpg', label: 'Producto C' }, // Baja 2
          ],
          [
            { id: 'lw3_s', src: 'img/products/sport_p12_Image91.jpg', label: 'Producto A' }, // Selmark 3
            { id: 'lw3_a', src: 'img/products/sport_p13_Image96.jpg', label: 'Producto B' }, // Asp 3
            { id: 'lw3_b', src: 'img/products/sport_p13_Image99.jpg', label: 'Producto C' }, // Baja 3
          ],
        ],
      },
    },
  },
};

// ----------------------------------------------------------
// SQL para crear la tabla en Supabase
// Copia y ejecuta en: Supabase > SQL Editor > New Query
// ----------------------------------------------------------
/*
create table survey_responses (
  id              uuid default gen_random_uuid() primary key,
  survey_id       text not null,
  respondent_id   text,
  session_id      text not null,
  created_at      timestamptz default now(),
  completed_at    timestamptz,
  status          text default 'in_progress',
  answers         jsonb default '{}',
  product_shown   jsonb default '{}'
);

-- Índices para consultas rápidas en el admin
create index on survey_responses (survey_id);
create index on survey_responses (status);
create index on survey_responses (created_at);

-- Política: insertar desde el navegador (anon key)
alter table survey_responses enable row level security;
create policy "insert_public" on survey_responses for insert with check (true);
create policy "update_own" on survey_responses for update using (true);
-- Para el admin (usa service_role key en admin.html para leer):
create policy "select_all" on survey_responses for select using (true);
*/
