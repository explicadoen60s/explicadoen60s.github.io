# explicadoen60s: producción automática de vídeos

Cuenta @explicadoen60s (TikTok, Instagram, YouTube «explicadoen60s_shorts»). Vídeos verticales de ~60-75 s que explican cómo funcionan las cosas, en castellano de España. El dueño revisa y aprueba desde el panel: https://explicadoen60s.github.io/

## Cómo fluye un vídeo (`produccion/estado.json`)
| estado | quién lo mueve | qué significa |
|---|---|---|
| `propuesto` | **Claude** (pasada diaria) | guion propuesto, esperando al usuario |
| `aprobado` | usuario (panel) | la acción «Generar voces» crea `escenas/<id>.mp3` con la voz del dueño (Qwen3-TTS, `produccion/voz.py`) |
| `voz` | GitHub | hay voz; **Claude** debe escribir la escena 3D |
| `escena` | **Claude** | escena escrita y revisada; al hacer push se lanza «Renderizar vídeos» |
| `revision` | GitHub | vídeo en el release `videos`; el usuario lo ve en el panel |
| `rehacer` | usuario | ha pedido cambios en `nota`: **Claude** corrige la escena y vuelve a `escena` |
| `programado` / `rechazado` | usuario | terminado |

Claude **nunca** aprueba vídeos ni los programa: eso lo hace el usuario en el panel.

## Pasada diaria de Claude (por este orden)
Trabajas como **la oficina**: los nueve puestos de la sección «La oficina» (más abajo). Cada paso lo firma el puesto que lo hace, y lo revisan sus compañeros. **Los acuerdos vigentes** (`oficina.json` → `acuerdos`, `estado: "vigente"`) son normas que los propios agentes se han comprometido a cumplir en la jornada: aplica los de cada puesto cuando hagas su parte (guion, cámara, gráficos, sonido, montaje, títulos) igual que las leyes del Manual.
1. `git pull`. Lee `produccion/estado.json`. Ejecuta `python3 produccion/auditoria.py` y después `python3 produccion/oficina.py`, y lee `produccion/oficina_datos.json` (qué tiene cada puesto entre manos, compuertas, segundas partes, evidencia del Manual) y las **leyes** de `produccion/oficina.json` → `manual`.
2. **`rehacer`**: lee `nota`, corrige `escenas/<id>_scene.py` / `_ov.py`, revísalo (ver «Revisar antes de entregar» y «Revisión cruzada de escenas») y ponlo en `escena`. Borra `nota` (el panel guarda el historial en `rehacer_notas`).
3. **`voz`** (todos los que haya, hasta 8 por pasada, los más antiguos primero): escribe `escenas/<id>_scene.py` y `escenas/<id>_ov.py`, revísalos (incluida la «Revisión cruzada de escenas») y pon `escena`. Haz un commit y un push por vídeo, para que el render empiece cuanto antes (cada push lanza el render de todos los que están en `escena`).
3c. **Jornada de respaldo:** si en `oficina.json` → `jornadas` no hay ninguna `"estado": "hecha"` de hoy (normalmente porque falta la clave de la API en GitHub), celebra la jornada con los agentes de Claude Code (ver «Jornada diaria» en «La oficina») antes del paso 4. Solo en la pasada de la mañana.
3a. **Reunión de respaldo:** si es lunes por la tarde (pasada de las 19:56) y en `oficina.json` → `reuniones` no hay acta de esta semana, celebra la reunión semanal (protocolo en «La oficina») después de entregar las escenas.
3b. **Encargos de la oficina** (`produccion/oficina.json` → `encargos` con `estado` distinto de `"hecho"`): hazlos (ver «Encargos»).
4. **Guiones con `nota_guion`** (el usuario pidió «otra versión» desde el panel): reescribe `guion`/`texto`/`titulo` según la nota, pásalo otra vez por la «Revisión cruzada de guiones», deja el estado en `propuesto` y borra `nota_guion`.
5. **Tendencias** (`produccion/tendencias.json`, lo enseña el panel en «Tendencias»): lee las señales de `programador/tendencias_raw.json` (Google Trends España, Wikipedia, YouTube España, shorts de «cómo funciona» de la semana, competencia) y escribe el análisis completo. Formato: `{actualizado, resumen, tendencias:[…], descartadas:[{tema, motivo}]}`. Cada tendencia lleva `id`, `tema`, `tipo` (`actualidad` | `evergreen` | `nicho`), `puntuacion` (0-100), `por_que` (con cifras de las señales), `senales:[{fuente, dato, url?}]`, `urgencia`, `angulo`, `titulo`, `gancho`, `primer_segundo`, `cifras:[…]`, `formato`, `estructura:[…]`, `reglas:{cotidiano, primer_segundo, ensenar}` (0-10), `potencial`, `por_que_funcionaria`, `competencia`, `riesgos`, `mejor_hora` y `hashtags`. Entre 6 y 10 tendencias, ordenadas por puntuación. Descarta, explicando el motivo, famosos, política, sucesos con víctimas, apuestas, armas y lo que ya está en `produccion/escenas/`. Comprueba con búsqueda web las cifras que propongas; si no puedes, márcalas «(comprobar)».
6. **Comunidad** (`produccion/comunidad_analisis.json`): con `programador/comunidad.json`, escribe `{actualizado, resumen, respuestas:{<id del comentario>: "respuesta sugerida"}, ideas:[{tema, idea, menciones, ejemplos:[…]}]}`. Las respuestas sugeridas van en tuteo, son cortas y cercanas, y no prometen fechas. Las ideas son los temas que piden los seguidores.
7. **Propuestas**: que haya siempre unos **8** vídeos entre `propuesto`, `aprobado`, `voz` y `escena`. Añade los que falten como `propuesto`. **Empieza por el banco de ideas** (`produccion/ideas.json`, las de `prioridad: "alta"` primero): cada idea que conviertas en guion se marca `estado: "usada"` con `guion: <id>`. **De cada tres propuestas, al menos una es de la serie «Lo que esconde tu ciudad»** (ver «Línea editorial»). Después, usa las mejores tendencias y las `segundas_partes` de `oficina_datos.json`. Si el guion sale de una idea o de una tendencia, pon `idea: <id>` o `tendencia: <tema>` en la entrada. **Cada guion nuevo pasa por la «Revisión cruzada de guiones»** (con `revisiones`, `seo` y predicciones) antes de quedarse en `propuesto`.
7a. **Mejora diaria** (obligatoria en cada pasada): ver «Mejora diaria» en «La oficina».
7b. **Cierre de la oficina**: vuelve a ejecutar `python3 produccion/oficina.py` y súbelo junto con `produccion/oficina.json` (actividad, predicciones, encargos y Manual al día). Si alguna ley tiene evidencia `en_contra` en `oficina_datos.json`, deja un `aviso` en `actividad`.
8. Si una entrada tiene `error`, intenta resolverlo. Si no puedes (falta un secreto, por ejemplo), déjalo anotado en `error` en palabras sencillas.

## Las 3 reglas que deciden si un vídeo funciona (obligatorias)
Las sacó el usuario de un creador que publicó el mismo tipo de vídeo con dos resultados: unos 60 mil frente a 10,5 millones de visualizaciones.
1. **De qué hablas: algo que el espectador tiene en la mano o usa todos los días.** Mejor la pantalla del móvil, «que estás tocando ahora mismo», que un gadget que no todo el mundo tiene. Prioriza temas universales y conéctalos con el espectador en la primera frase («ahora mismo», «tu», «cada mañana»).
2. **El primer segundo: el objeto ya en acción, en primer plano y moviéndose.** Nada de planos generales quietos ni objetos en reposo. Ejemplo bueno: un dedo gigante tocando la pantalla. Ejemplo malo: un móvil quieto en un bolsillo. Ahí es donde la gente decide si pasa el vídeo.
3. **No lo cuentes, enséñalo.** Nada de metáforas que haya que imaginar («hay un detective en tu bolsillo»). Muestra el mecanismo real con algo que cambie en pantalla: «tu dedo se lleva electricidad y un número baja de 100 a 62». Usa contadores, medidores, cifras que suben o bajan, flechas de corriente o de fuerza y etiquetas pequeñas en mayúsculas sobre las piezas (CRISTAL, CABLES…).

Formato visual de referencia:
- Subtítulos en frase arriba: la frase se escribe palabra a palabra, la palabra que suena en blanco, las anteriores en gris y las palabras clave en un recuadro azul. En `_ov.py`, pon `SUB_ESTILO = "frase"` en todas las escenas nuevas. Los marcadores (`badge`) bajan solos para no pisar el subtítulo.
- Primeros planos, cámara cerca del mecanismo y fondos oscuros o neutros que hagan resaltar el objeto.

## Línea editorial (sale de las estadísticas, 11-nov-2026)
Los tres vídeos que hicieron crecer TikTok de 77 a 441 seguidores en 4 días fueron el tanque de tormentas de Madrid (50 mil vistas, 51 veces lo normal), la rueda de avión (40 mil) y el wifi en forma de donut (37 mil). En YouTube, «¿Y si construyes un pozo?» (17,7 mil, 12 veces lo normal). Lo que menos funciona: acertijos de probabilidad (cumpleaños, puertas) y temas abstractos (tarjeta, código de barras), con menos de 160 vistas.
- **Fórmula del gancho:** una cifra enorme y exacta, comparada con algo del espectador. «Casi 6 veces la presión de tu coche», «400.000 m³ bajo tus pies». Desde el 12-nov la cifra no se dice al principio: el título y la primera frase la plantean como pregunta («¿Cuánta agua cabe bajo Madrid?») y se descubre más tarde (ver «Juego de la cifra»). La comparación con algo del espectador sigue yendo al principio.
- **Serie «Lo que esconde tu ciudad»:** grandes obras reales de España (depósitos, ríos desviados, autovías enterradas, túneles, canales), formato C, numerada en el título («… parte 2»). Pide en el pie que comenten su ciudad; esas respuestas van al banco de ideas.
- **Segundas partes:** cuando un vídeo supera 10 veces la mediana de su red, propón una segunda parte (otro aspecto del mismo objeto) en la siguiente pasada, con «(parte 2)» en el título.
- **Evita:** acertijos, probabilidad, objetos que no todo el mundo tiene y temas sin una cifra que se pueda enseñar.
- **Instagram** no se trabaja aparte por ahora: recibe los mismos vídeos.

## Juego de la cifra (obligatorio en todos los guiones nuevos desde el 12-nov-2026)
Datos que lo justifican: 264.714 vistas en TikTok y solo 66 comentarios en toda la cuenta (uno cada 4.000 vistas), y 1 seguidor por cada 600 vistas. El único vídeo que preguntaba algo al espectador (la ruleta) se llevó 258 de los 520 compartidos. La gente mira, pero no participa: el juego le da un motivo para comentar y para quedarse hasta el final.
- **Pregunta en las dos primeras frases:** después del gancho con el objeto en acción, una pregunta con número y la invitación a escribirlo. Ejemplo: «¿Cuánta agua cabe bajo Madrid? Escribe tu número antes de que acabe.» La cifra es la del gancho (fórmula de la cifra enorme): **el gancho no la dice**, la plantea.
- **La cifra se descubre** en el momento del dato sorprendente, en mitad o en el último tercio del vídeo; nunca en los primeros 15 segundos.
- **Cierre:** «¿Te has acercado? Y si quieres que explique algo, pídelo en comentarios: lo más pedido será un vídeo. Sígueme para más.» (puede variar la redacción, no la idea; no prometas fechas).
- **El pie del post** (`texto`) repite el reto: «¿Cuál era tu número? 👇».
- **Campo `juego`** en la entrada de `estado.json`: `{"pregunta": "¿Cuánta agua cabe bajo Madrid?", "valor": 400000, "unidad": "m³ BAJO MADRID", "dec": 0, "pregunta_en": "<primeras palabras de la frase de la pregunta>", "revela_en": "<primeras palabras de la frase que dice la cifra>"}`. La unidad va en mayúsculas y corta (cabe en una línea).
- **Vídeos pedidos por seguidores:** si el guion responde a un comentario (de `programador/comunidad.json` o del análisis de comunidad), añade `comentario: {"autor": "usuario", "texto": "la pregunta tal cual, corta"}` y empieza el guion respondiendo a esa persona («Me preguntas cómo…»). Solo comentarios reales; nunca te inventes uno.
- **En la escena** (`_ov.py`): `C.cifra_juego(ctx, t, valor, unidad, T(pregunta_en), T(revela_en), T("sígueme"), dec=dec)` y, en `sfx_events`, `E += C.sfx_cifra(T(pregunta_en), T(revela_en))`. La tarjeta sale grande con «?», a los 2,6 s se encoge a una esquina (`mini=(x, y)`; elige un hueco que no tape el mecanismo), vuelve al centro en la revelación y la cifra sube contando. Coloca `grande=(x, y)` donde no tape el objeto del primer segundo. Si hay `comentario`: `C.comentario(ctx, t, autor, texto, 0.0, T(<segunda frase>))` en el primer segundo, sobre el objeto que ya se mueve (nunca en lugar de él).
- **El panel** mide comentarios y seguidores por cada mil vistas, y compara los vídeos con juego frente a los demás (Estadísticas → General).

## Guiones (propuestas)
Campos de cada entrada nueva en `estado.json`:
- `id`: corto, ASCII y único, por ejemplo `piscina`.
- `formato`: `A`, `B` o `C`.
- `titulo`: hasta 100 caracteres, con emoji.
- `guion`: solo el texto que se locuta.
- `texto`: el pie del post, 1-2 frases que terminen en pregunta o 👇.
- `tags`: 5 temas sin `#`.
- `estado: "propuesto"` y `creado` (la fecha).
- `reglas`: tu nota de 0 a 10 para cada una de las 3 reglas, con una frase que lo justifique: `{"cotidiano": 9, "cotidiano_nota": "…", "primer_segundo": 8, "primer_segundo_nota": "qué se verá en el primer segundo", "ensenar": 9, "ensenar_nota": "qué cifras cambian en pantalla"}`. El panel lo enseña como un semáforo.
- `ganchos`: 3 primeras frases alternativas; la primera es la que va en `guion`. El usuario elige una en el panel.
- `juego` (siempre) y `comentario` (si responde a un seguidor): ver «Juego de la cifra».

Formatos (mezclarlos; uno de cada tres, más o menos):
- **A · «Así funciona»**: un objeto cotidiano en corte (*cutaway*); se ve el mecanismo por dentro y se explica paso a paso. Ejemplos: `cisterna`, `semaforo`, `airbag`.
- **B · «Si tuvieras que inventar…»**: construir el objeto pieza a pieza, cada pieza resuelve un problema. Ejemplos: `termo`, `mechero`, `cremallera`.
- **C · «¿Y si construyes…?»**: construcción grande en corte bajo tierra o en sección. Cada paso crea un problema («pero…») y el siguiente lo soluciona («así que…»). Ejemplos de temas: piscina, rascacielos, túnel bajo un río, pozo, presa.

Reglas del guion:
- **Longitud:** 205-245 palabras (≈60-72 s: la voz va a unas 3,4 palabras por segundo). Escribe con gancho: preguntas, exclamaciones (¡…!) y puntos suspensivos antes de los datos sorprendentes; la puntuación da la entonación.
- **Estilo:** tuteo, vocabulario de España, frases de 6-12 palabras, sin relleno. Números en letra.
- **Estructura:** gancho en la primera frase (dato chocante o pregunta), conectado con el espectador (regla 1); un dato sorprendente en mitad del vídeo; cierre con la frase del juego de la cifra (ver arriba) y «Sígueme para más.».
- **Cifras que se puedan enseñar:** cada guion debe tener al menos 2 números que cambian y que la escena pueda mostrar como contador o medidor (regla 3).
- **Datos:** comprueba con búsqueda web cada dato técnico, cifra o récord antes de proponerlo.
- **Temas:** no repitas nada que ya esté en `estado.json` ni en `produccion/escenas/`. Nada de casinos ni apuestas, nada de marcas reales en pantalla.

## Escenas 3D (`escenas/<id>_scene.py` + `<id>_ov.py`)
Motor en `produccion/motor/`. Copia los patrones de las escenas existentes: es la mejor documentación.
- **Render:** Blender 5 (`bpy`) con Workbench, estilo 3D estilizado con colores planos y sombras suaves. 1080×1920, 30 fps.
- **Funciones de `lib3d`:**
  - Primitivas: `box`, `cyl`, `sph`, `torus`, `rounded_slab`, `text3d`, `bar_obj`/`bar_set`, `set_color`.
  - Animación: `seg(t,a,b)` (0→1 suavizado), `keyed(t,[(t,v),…])`, `mix`.
  - Cámara: `cam_state(t, CAM, drift)` con claves Catmull-Rom `(t, (pos), (target), lens)` y `apply_cam`.
  - Rendimiento: `join_static(dinamicos)` une todo lo estático para ir más rápido. **Todo lo que se mueve, cambia de color o tiene modificadores (booleanas, solidify) va en la lista de dinámicos**; si no, se pierde.
  - Cortes: modificador SOLIDIFY (interior más claro con `material_offset`) + BOOLEAN DIFFERENCE con un cubo cortador oculto.
  - `run(nombre, build, pose, anchors)` renderiza; `anchors` devuelve puntos 3D proyectados a pantalla para colocar etiquetas.
- **`_ov.py` (capa 2D):** `SUB_Y`, `KEYWORDS` (palabras del subtítulo en amarillo), `overlay(ctx,t,A,C)` y `sfx_events(C)`. Ayudas: `C.badge`, `C.callout`, `C.s_whoosh`, `C.s_pop`, `C.s_thud`, `C.s_clank`, `C.s_win`, `C.s_fail`… El subtítulo de una palabra lo pone `comp.py` solo.
- **Sincronizar con la voz:** `produccion/producir.sh <id>` alinea la voz y crea `trabajo/<id>/<id>_words.json`. Con `python3 trabajo/<id>/phr.py <id>`, ejecutado dentro de esa carpeta, se ven las frases con sus tiempos. Cada acción visual debe coincidir con lo que dice la voz en ese momento.

Calidad que exige el usuario:
- Escenas realistas y con sentido común; el objeto se reconoce a la primera.
- Vídeo continuo, sin imágenes fijas; algo se mueve siempre.
- Un único estilo; texto en pantalla solo para palabras clave o cifras, **sin repetir lo que dice el subtítulo**.
- La cámara nunca atraviesa objetos y lo importante siempre está dentro del encuadre. Respeta las zonas seguras: los 150 px de arriba, los 420 px de abajo y los 140 px de la derecha quedan libres de cosas importantes.
- El primer segundo ya muestra el objeto en acción, en primer plano y moviéndose (regla 2); nada de pantallas vacías ni planos quietos.
- Lo que la voz explica se ve: contadores, medidores y flechas en lugar de metáforas (regla 3).
- No repitas siempre los mismos elementos de un vídeo a otro.

## Revisar antes de entregar (obligatorio)
1. Instala si falta: `pip install --break-system-packages bpy==5.2.3 numpy pycairo`, `ffmpeg`, y las fuentes de `produccion/fuentes/` en `~/.fonts`.
2. Vista previa barata: `RANGO="0 <N> 15" produccion/producir.sh <id>` (un fotograma de cada 15), donde N = duración × 30.
3. Hoja de contactos de `produccion/trabajo/<id>/frames/<id>_prev/*.png` con ffmpeg (`tile`) y **mírala con Read**. Comprueba que se ve lo que dice la voz en cada momento, que nada se sale del encuadre, que la cámara no atraviesa nada y que los cortes muestran el interior.
4. Corrige y repite hasta que esté bien. Solo entonces: `estado: "escena"`, commit y push. `produccion/trabajo/` no se sube (está en `.gitignore`).

## La oficina (desde el 12-nov-2026)
La producción la lleva un equipo de nueve puestos que **se revisan entre ellos, se proponen mejoras y aprenden de las estadísticas**. El usuario lo ve todo en el panel → «Oficina». Las fichas de cada puesto (misión, qué comprueba, cómo responde y «Lo que he aprendido») están en `.claude/agents/<id>.md`, y sus datos en `produccion/oficina.json` → `equipo`.

| id | puesto | revisa a | le revisan |
|---|---|---|---|
| `director` | Director / Guionista (decide si no hay acuerdo) | estratega, editor | estratega, seo, motion |
| `fotografia` | Videógrafo / Camarógrafo (cámara 3D, regla 2) | motion, director | editor, motion |
| `sonido` | Técnico de sonido (voz, ritmo, sfx) | director, editor | editor |
| `editor` | Editor de vídeo / Montador (sincronía, bucle) | fotografia, sonido, director | director, sonido |
| `motion` | Motion graphics (regla 3, `_ov.py`) | director, fotografia | fotografia |
| `estratega` | Estratega de contenidos | director | social, paid |
| `social` | Social Media / Community Manager | estratega, director | seo |
| `paid` | Paid Media (Traffic Manager) | estratega | estratega |
| `seo` | SEO para vídeo | director, social | director |

**Archivos**
- `produccion/oficina.json`: lo escriben Claude, la jornada y el panel. `equipo`, `actividad` (registro; añade al final y deja como mucho las 300 últimas), `manual`, `reuniones`, `predicciones`, `encargos`, `paid`, `experimentos`, `diario`, `canal`, `acuerdos`, `jornadas`. Cambia solo lo tuyo y conserva el resto.
- `produccion/auditoria.json`: **no se edita a mano**. Medidas técnicas de cada vídeo (`python3 produccion/auditoria.py`; solo vuelve a medir lo que cambia). Sirven también como campos de `filtro` en el Manual (`cam_cada`, `ov_contadores`, `sfx_variedad`, `voz_ritmo`…).
- `produccion/oficina_datos.json`: **no se edita a mano**. Lo calcula `python3 produccion/oficina.py` (el flujo «Oficina» lo ejecuta solo después de cada recogida de estadísticas y en cada push): número y foco de cada puesto, compuertas, evidencia del Manual, señales automáticas, `mejora` (hallazgos técnicos, recomendaciones por vídeo, experimentos y cómo son los mejores vídeos), reputación, candidatos a promoción y segundas partes.
- Entrada de `actividad`: `{"fecha": ISO, "rol": "<id>", "para": "<id>"?, "tipo": "revision|propuesta|mejora|analisis|reunion|aviso|encargo|prediccion", "video": "<id>"?, "texto": "una o dos frases", "estado": "aplicada|rechazada"?}`.

**Revisión cruzada de guiones (todo guion nuevo o reescrito)**
1. `director` lo escribe aplicando las reglas de este archivo y las **leyes** del Manual.
2. **Compuertas:** `python3 produccion/oficina.py comprobar <id>` tiene que salir sin errores (longitud, juego de la cifra bien colocado, ≥2 cifras, reglas ≥7, título ≤100 con emoji, temas vetados). Si falla, corrígelo antes de seguir.
3. **Revisan** `estratega`, `seo`, `motion` y `sonido`, cada uno **por separado**: los guiones que ya existen los revisa la jornada diaria; los que escribas en la pasada, lánzalos tú con la herramienta Agent (`subagent_type` = el id del puesto, uno por revisor, en paralelo, con todos los guiones nuevos en un solo encargo) y guarda lo que devuelvan, sin reescribirlo, en la entrada de `estado.json`: `revisiones: [{"rol", "fase": "guion", "veredicto": "ok|cambios", "nota", "propuesta", "aplicada": true|false, "respuesta"}]`. **No vale criticar sin proponer** un arreglo concreto. Revisiones de verdad: si todo está bien, di por qué en una frase; si algo falla, dilo.
4. `director` aplica o rechaza cada propuesta y lo explica en `respuesta` (una frase). Como mucho **2 rondas**; después decide `director`.
5. `seo` escribe `seo: {"tiktok": {"titulo", "texto", "tags"}, "instagram": {…}, "youtube": {…}}`. TikTok: título = gancho con la pregunta del juego (≤100, emoji). Instagram: pie algo más descriptivo y 5 hashtags. YouTube: título buscable ≤70 caracteres con «cómo funciona…» o la pregunta, y `#shorts` en el pie. `tags` sin `#`. El panel usa estos textos al programar cada red.
6. **Predicciones:** los nueve puestos apuestan cuántas veces lo normal hará el vídeo (0,2-20) con una frase. Guárdalo en `oficina.json` → `predicciones["<id>"] = {"fecha", "roles": {"<rol>": {"rel": 1.4, "nota": "…"}}}`. Apuestas honestas y distintas según el puesto: el script las puntúa cuando el vídeo lleva 48 h publicado y el que acierta pesa más en las votaciones.
7. Deja en `actividad` una línea por cada revisión con cambios (`tipo: "revision"`, `para: "director"`) y por cada mejora aplicada (`tipo: "mejora"`).

**Revisión cruzada de escenas (al escribir o corregir `_scene.py`/`_ov.py`)**
Con la hoja de contactos de «Revisar antes de entregar», mira el vídeo con los ojos de cada puesto y corrige antes de entregar:
- `fotografia`: primer fotograma en acción y en primer plano, cámara sin atravesar nada, encuadre y zonas seguras.
- `motion`: cada cifra se ve cambiar, etiquetas cortas que no tapan el mecanismo, `cifra_juego` en un hueco libre.
- `editor`: cada acción cae en su palabra (`phr.py`), algo cambia cada 2 s, el final enlaza con el principio.
- `sonido`: `sfx_events` sin pisar las cifras dichas en voz, duración dentro de lo previsto.

**Auditor técnico antes de entregar:** cuando la escena esté escrita, ejecuta `python3 produccion/auditoria.py && python3 produccion/oficina.py` y mira `oficina_datos.json` → `mejora.recomendaciones["<id>"]`. Cada punto `mejorar` es una medida (ritmo de cámara, contadores, tipos de efecto, distancia en el primer segundo…) que está en el lado que peor funciona: corrígelo si encaja con lo que cuenta la voz, y repite la hoja de contactos. Si decides no hacerlo, explica por qué en `revisiones`. Usa `mejora.referencia` (cómo son tus mejores vídeos) como objetivo al plantear cada escena nueva.

Añade sus conclusiones a `revisiones` con `"fase": "escena"` (solo las que pidieron cambios, con lo que se cambió) y una línea en `actividad`. Si el vídeo vuelve de `rehacer`, el puesto responsable del fallo (según la `nota`) escribe en `actividad` qué ha aprendido, y si es una lección general, la añade a «Lo que he aprendido» de su ficha.

**Jornada diaria** (la independencia de la oficina)
Cada día los nueve puestos trabajan como **agentes separados**: cada uno con su ficha (`.claude/agents/<id>.md`) y los mismos datos, sin ver lo que piensan los demás salvo lo que se escriben. Lo hace `produccion/jornada.py`:
- **Ronda 1:** cada agente analiza, revisa los guiones propuestos (estratega, seo, motion, sonido), apuesta por cada guion, propone hipótesis y experimentos, y escribe de 1 a 3 mensajes concretos a compañeros.
- **Ronda 2:** cada agente lee su bandeja y responde: `acepto`/`matizo` con un **compromiso** exacto, `rechazo` con motivo, o `respondo`. El director corrige sus guiones con las revisiones (solo se aplica si pasa las compuertas).
- **Aplicar:** mensajes y respuestas → `oficina.json` → `canal`; compromisos → `acuerdos` vigentes (como mucho 40; los más antiguos caducan); lecciones → «Lo que he aprendido» de cada ficha; hipótesis → Manual; como mucho un experimento nuevo; revisiones, predicciones y `seo` → `estado.json`; entrada en `diario` y registro en `jornadas` (tokens y coste).
- **Quién la lanza:** el flujo «Jornada de la oficina» de GitHub, cada día a las 07:17 (Madrid), con la API de Claude (secreto `ANTHROPIC_API_KEY`). Si no hay clave, deja `"estado": "sin_clave"` y la hace la pasada de la mañana con los agentes de Claude Code:
  1. `python3 produccion/jornada.py --preparar produccion/trabajo/jornada 1`
  2. Lanza en paralelo los nueve agentes (Agent, `subagent_type` = id) con el texto de `produccion/trabajo/jornada/encargo1_<id>.txt`. Guarda el JSON que devuelve cada uno, tal cual, en `produccion/trabajo/jornada/r1_<id>.json`.
  3. `python3 produccion/jornada.py --preparar produccion/trabajo/jornada 2` y lanza los agentes que tengan `encargo2_<id>.txt`; guarda sus respuestas en `r2_<id>.json`.
  4. `python3 produccion/jornada.py --aplicar-dir produccion/trabajo/jornada`, commit «Oficina: jornada <fecha>» y push.
- **Nunca escribas tú los mensajes, respuestas o revisiones de un agente**: solo los agentes hablan por sí mismos. Si uno falla, sigue sin él y apúntalo.
- `canal`: `{"id", "fecha", "jornada", "de", "para", "tipo": "peticion|propuesta|aviso|pregunta|dato", "asunto", "texto", "video", "respuestas": [{"de", "decision", "texto", "compromiso", "fecha"}]}`. `acuerdos`: `{"id", "rol" (quien se compromete), "pedido_por", "texto", "desde", "origen", "estado": "vigente|caducado|retirado"}`. El usuario puede retirar un acuerdo desde el panel.

**Mejora diaria** (en cada pasada, después de entregar escenas y guiones)
La oficina se mejora sola cada día con tres fuentes: `produccion/auditoria.json` (lo calcula `produccion/auditoria.py`: voz, escena 3D, capa 2D y sonido de cada vídeo, sin renderizar), las estadísticas y lo que pasó en la pasada.
1. **Autopsia:** para cada vídeo que haya cumplido 48 h publicado desde la última entrada del `diario`, los puestos implicados escriben una línea en `actividad` (`tipo: "analisis"`, `video`): qué funcionó y qué no, con la cifra (vistas frente a lo normal) y la medida técnica que lo explica (`mejora.recomendaciones`).
2. **Hallazgos:** lee `mejora.hallazgos` (qué medidas separan los vídeos que funcionan de los que no; «lo normal» es la mediana de su red en los días cercanos, así que el crecimiento de la cuenta no engaña). El puesto dueño de cada hallazgo con `fuerza` ≥ 1,5 lo aplica desde ya en lo que escriba. Si es nuevo o más preciso que lo que tiene, lo apunta en «Lo que he aprendido» de su ficha (`.claude/agents/<rol>.md`) con el umbral («cambio de plano cada menos de 3 s: 2,6× más vistas»), como mucho 10 puntos.
3. **Experimentos** (`oficina.json` → `experimentos`, 1-3 activos a la vez): `{"id", "rol", "cambio": "qué se hace distinto, concreto", "hipotesis": "qué se espera y por qué", "metrica": "<medida de auditoria.json>"?, "desde": fecha, "videos": [ids], "estado": "activo|ganado|perdido|neutro", "conclusion"?}`. Si hay menos de 2 activos, abre uno con el hallazgo más fuerte que no se esté aplicando ya o con una idea propia de un puesto (voz, cámara, gráficos, sonido, guion, título). Cada vídeo de esta pasada que aplique un experimento se añade a sus `videos`. `oficina_datos.json` → `mejora.experimentos` lo juzga solo cuando hay datos: con 3 o más vídeos maduros, ciérralo (`estado`, `conclusion`). Si ha ganado, va a la ficha del puesto y al Manual como `propuesta` (con `filtro` si tiene `metrica`). Si ha perdido, se apunta para no repetirlo.
4. **Voz:** si los hallazgos de `sonido` tocan el ritmo, las pausas o la energía del gancho, se corrige donde se puede: en el guion (puntuación, frases más cortas, «…» antes de los datos) y, si hiciera falta un cambio de la voz en sí (velocidad, tono), se propone al usuario en `actividad` (`tipo: "aviso"`), porque la voz la genera `produccion/voz.py`.
5. **Diario** (`oficina.json` → `diario`, deja como mucho 60): `{"fecha", "resumen": "una frase", "aprendido": ["…"], "cambios": [{"rol", "texto"}], "experimentos": [ids]}`. Es lo que el usuario lee en el panel → Oficina → Mejora diaria y en la pizarra del mundo 3D.

**Encargos** (`oficina.json` → `encargos`): el usuario los deja desde el panel, para un puesto (`rol`) o para `"todos"`. Hazlos en la pasada, como el puesto indicado: un tema → idea o guion; una pregunta → análisis con datos; un cambio de proceso → cámbialo (ficha, este archivo o el Manual). Escribe `respuesta` (qué has hecho, en dos frases como mucho), `estado: "hecho"` y `hecho: <fecha>`, y una línea en `actividad` (`tipo: "encargo"`). Si el encargo es `tipo: "reunion"`, celebra una reunión extraordinaria (protocolo de abajo, con `tipo: "extraordinaria"` y el encargo como tema).

**Manual vivo** (`oficina.json` → `manual`): `{"id", "texto", "estado": "ley|hipotesis|propuesta|descartada", "por": "<rol>", "creada", "origen", "filtro"?}`.
- Las **leyes** son obligatorias en guiones y escenas, igual que este archivo.
- Las reglas que se pueden medir llevan `filtro` (`{"campo": …, "igual"|"menor"|"mayor"|"contiene": valor}`, o una lista de varios; campos: `formato`, `juego`, `comentario`, `serie`, `titulo_pregunta`, `titulo_cifra`, `duracion`, `tendencia`, `idea`, `cotidiano`, `ensenar`, `primer_segundo`, `gancho`, `rehacer`). El script compara cada hora los vídeos que la cumplen con los que no y deja el veredicto en `oficina_datos.json` → `manual`.
- Claude puede crear `hipotesis` cuando quiera. **Nunca crea una `ley` directamente**: si una hipótesis tiene veredicto `a_favor` con 3 o más vídeos a cada lado, pásala a `propuesta` y lo decide el usuario en el panel.
- Cuando el usuario convierte una regla en ley (`decidida`, `decidida_por`) y cambia cómo se escriben guiones o escenas, añádela como un punto en «Línea editorial» con «(Manual, <fecha>)». Si una ley pasa a `descartada` o `hipotesis`, quita ese punto.

**Promoción** (`paid`): Claude nunca gasta ni lanza anuncios. `oficina.py` calcula los candidatos (3 veces lo normal o más en sus primeros 5 días) y el usuario marca en el panel lo que lanza. En las reuniones, `paid` comenta el coste por 1.000 vistas de lo lanzado y si conviene repetir.

**Reunión semanal** (lunes 11:37, tarea programada «Reunión semanal de la oficina», o un encargo `tipo: "reunion"`)
1. `git pull` y `python3 produccion/oficina.py`.
2. Lanza **los nueve agentes** de `.claude/agents/` en paralelo (herramienta Agent, `subagent_type` = el id). A cada uno dale el mismo encargo: «Reunión semanal de la oficina del <fecha>. Lee produccion/oficina_datos.json, programador/estadisticas.json, produccion/estado.json, produccion/ideas.json, produccion/tendencias.json, produccion/comunidad_analisis.json y produccion/oficina.json (manual, reuniones anteriores, paid). Devuelve solo tu JSON de reunión.» Si un agente falla, sigue con los demás y apúntalo en el acta.
3. **Votación** (haces de moderador): cada puesto vota como mucho 3 ideas de otros, según su ficha y su regla de oro. `puntos = media(I, C, F) × (0,75 + 0,25 × peso de quien la propone) + 0,3 × suma de los pesos de quienes la votan`, con los pesos de `oficina_datos.json` → `reputacion` (1 si no hay). Redondea a un decimal.
4. Las **3 ideas con más puntos** pasan a `produccion/ideas.json` con `prioridad: "alta"`, `origen: "reunión <fecha>"` y `notas` con el porqué; márcalas `elegida: true` en el acta.
5. **Mejoras entre compañeros:** el puesto que la recibe la acepta o la rechaza con un motivo (`estado`, `respuesta`). Si una aceptada es una lección general, añádela a «Lo que he aprendido» de su ficha (como mucho 10 puntos: sustituye el menos útil). Si cambia el proceso, cámbialo aquí.
6. **Manual:** las `regla` que propongan los puestos y las `senales` nuevas de `oficina_datos.json` entran como `hipotesis` (con `filtro` si se puede medir). Las hipótesis `a_favor` pasan a `propuesta`. Las leyes `en_contra` se comentan en `decisiones`.
7. Guarda el acta en `oficina.json` → `reuniones`: `{"fecha", "tipo": "semanal|extraordinaria", "resumen": "una o dos frases", "repaso": [{"rol", "texto"}], "ideas": [{"rol", "idea", "por_que", "ice": {"i", "c", "f"}, "votos": [roles], "puntos", "elegida"}], "mejoras": [{"de", "para", "texto", "estado": "aceptada|rechazada", "respuesta"}], "decisiones": […], "reglas": […]}`. Una línea en `actividad` (`tipo: "reunion"`) y otra por cada mejora aceptada (`tipo: "mejora"`).
8. Commit «Oficina: reunión semanal <fecha>» y push. Resumen de dos líneas al usuario.

## Publicación (no la toques salvo que se pida)
- `programador/` + `.github/workflows/publicar.yml` publican cada 10 min lo que está en `programador/calendario.json`.
- El panel (`docs/index.html`) añade publicaciones al aprobar un vídeo.
- Vídeos: release `videos`. `<id>.mp4` va a Instagram y YouTube; `<id>_tiktok.mp4` (con música) va a TikTok.
- Horario: TikTok 10, 13, 16, 18 y 21 h; Instagram 10 y 18 h; YouTube 12 y 16 h (hora de Madrid).

## Commits
Autor `explicadoen60s <explicadoen60s.cxn@gmail.com>`. Mensajes en español.
