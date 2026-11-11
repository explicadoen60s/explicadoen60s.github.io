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
1. `git pull`. Lee `produccion/estado.json`.
2. **`rehacer`**: lee `nota`, corrige `escenas/<id>_scene.py` / `_ov.py`, revísalo (ver «Revisar antes de entregar») y ponlo en `escena`. Borra `nota`.
3. **`voz`** (todos los que haya, hasta 8 por pasada, los más antiguos primero): escribe `escenas/<id>_scene.py` y `escenas/<id>_ov.py`, revísalos y pon `escena`. Haz un commit y un push por vídeo, para que el render empiece cuanto antes (cada push lanza el render de todos los que están en `escena`).
4. **Guiones con `nota_guion`** (el usuario pidió «otra versión» desde el panel): reescribe `guion`/`texto`/`titulo` según la nota, deja el estado en `propuesto` y borra `nota_guion`.
5. **Tendencias** (`produccion/tendencias.json`, lo enseña el panel en «Tendencias»): lee las señales de `programador/tendencias_raw.json` (Google Trends España, Wikipedia, YouTube España, shorts de «cómo funciona» de la semana, competencia) y escribe el análisis completo. Formato: `{actualizado, resumen, tendencias:[…], descartadas:[{tema, motivo}]}`. Cada tendencia lleva `id`, `tema`, `tipo` (`actualidad` | `evergreen` | `nicho`), `puntuacion` (0-100), `por_que` (con cifras de las señales), `senales:[{fuente, dato, url?}]`, `urgencia`, `angulo`, `titulo`, `gancho`, `primer_segundo`, `cifras:[…]`, `formato`, `estructura:[…]`, `reglas:{cotidiano, primer_segundo, ensenar}` (0-10), `potencial`, `por_que_funcionaria`, `competencia`, `riesgos`, `mejor_hora` y `hashtags`. Entre 6 y 10 tendencias, ordenadas por puntuación. Descarta, explicando el motivo, famosos, política, sucesos con víctimas, apuestas, armas y lo que ya está en `produccion/escenas/`. Comprueba con búsqueda web las cifras que propongas; si no puedes, márcalas «(comprobar)».
6. **Comunidad** (`produccion/comunidad_analisis.json`): con `programador/comunidad.json`, escribe `{actualizado, resumen, respuestas:{<id del comentario>: "respuesta sugerida"}, ideas:[{tema, idea, menciones, ejemplos:[…]}]}`. Las respuestas sugeridas van en tuteo, son cortas y cercanas, y no prometen fechas. Las ideas son los temas que piden los seguidores.
7. **Propuestas**: que haya siempre unos **8** vídeos entre `propuesto`, `aprobado`, `voz` y `escena`. Añade los que falten como `propuesto`. **Empieza por el banco de ideas** (`produccion/ideas.json`, las de `prioridad: "alta"` primero): cada idea que conviertas en guion se marca `estado: "usada"` con `guion: <id>`. **De cada tres propuestas, al menos una es de la serie «Lo que esconde tu ciudad»** (ver «Línea editorial»). Después, usa las mejores tendencias. Si el guion sale de una idea o de una tendencia, pon `idea: <id>` o `tendencia: <tema>` en la entrada.
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

## Publicación (no la toques salvo que se pida)
- `programador/` + `.github/workflows/publicar.yml` publican cada 10 min lo que está en `programador/calendario.json`.
- El panel (`docs/index.html`) añade publicaciones al aprobar un vídeo.
- Vídeos: release `videos`. `<id>.mp4` va a Instagram y YouTube; `<id>_tiktok.mp4` (con música) va a TikTok.
- Horario: TikTok 10, 13, 16, 18 y 21 h; Instagram 10 y 18 h; YouTube 12 y 16 h (hora de Madrid).

## Commits
Autor `explicadoen60s <explicadoen60s.cxn@gmail.com>`. Mensajes en español.
