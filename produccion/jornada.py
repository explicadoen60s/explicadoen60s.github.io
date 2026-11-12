#!/usr/bin/env python3
"""Jornada de la oficina: nueve agentes independientes que se escriben, se responden y mejoran.

Cada agente es una llamada separada a Claude con su propia ficha (.claude/agents/<id>.md) y los
mismos datos del día. No comparten contexto: lo único que saben unos de otros es lo que se escriben.

  Ronda 1  cada agente analiza, revisa guiones, apuesta y escribe mensajes a sus compañeros.
  Ronda 2  cada agente lee su bandeja y responde: acepta, rechaza o matiza, y se compromete.
  Aplicar  compromisos -> acuerdos vigentes; aprendizajes -> su ficha; hipótesis -> Manual;
           un experimento nuevo; revisiones y SEO -> estado.json; cambios de guion del director
           (solo si pasan las compuertas); diario y registro de la jornada.

Uso:
  python3 produccion/jornada.py                    jornada completa con la API (ANTHROPIC_API_KEY)
  python3 produccion/jornada.py --guardar R.json   ... y guarda las respuestas para reaplicarlas
  python3 produccion/jornada.py --aplicar R.json   solo aplica respuestas guardadas (tras un conflicto)
  python3 produccion/jornada.py --preparar DIR 1   escribe los encargos de la ronda 1 (para agentes de Claude Code)
  python3 produccion/jornada.py --preparar DIR 2   ronda 2, a partir de DIR/r1_<rol>.json
  python3 produccion/jornada.py --aplicar-dir DIR  aplica DIR/r1_*.json y DIR/r2_*.json
  JORNADA_SIMULADA=1 ...                           respuestas de prueba, sin llamar a nadie
"""
import concurrent.futures as cf
import json, os, re, subprocess, sys, time, unicodedata
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *r: os.path.join(RAIZ, *r)
sys.path.insert(0, P("produccion"))
import oficina as OF  # noqa: E402  (compuertas, rasgos, cálculos)

MODELO = os.environ.get("JORNADA_MODELO", "claude-opus-5-5")
ESFUERZO = os.environ.get("JORNADA_ESFUERZO", "medium")
PRECIO = {"in": 4.0, "cache_w": 5.0, "cache_r": 0.20, "out": 20.0}  # $/millón de tokens (Opus 5.5)
ROLES = ["director", "fotografia", "sonido", "editor", "motion", "estratega", "social", "paid", "seo"]
REVISAN_GUION = {"estratega", "seo", "motion", "sonido"}
AHORA = datetime.now(timezone.utc)
HOY = AHORA.astimezone().strftime("%Y-%m-%d")
CAMPOS_FILTRO = {"formato", "juego", "comentario", "serie", "titulo_pregunta", "titulo_cifra", "duracion", "tendencia",
                 "idea", "cotidiano", "ensenar", "primer_segundo", "gancho", "rehacer", "palabras", "parte2"}


# ───────────────────────── utilidades ─────────────────────────
def leer(ruta, defecto=None):
    try:
        with open(P(ruta), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return defecto


def escribir(ruta, datos):
    with open(P(ruta), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
        f.write("\n")


def norm(t):
    t = unicodedata.normalize("NFD", (t or "").lower())
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", "".join(c for c in t if unicodedata.category(c) != "Mn"))).strip()


def ficha(rol):
    """Cuerpo de la ficha del agente (sin el bloque YAML de cabecera)."""
    t = open(P(".claude", "agents", f"{rol}.md"), encoding="utf-8").read()
    return re.sub(r"^---.*?---\s*", "", t, flags=re.S)


def nid(prefijo, n):
    return f"{prefijo}{AHORA.strftime('%y%m%d')}{n:03d}"


# ───────────────────────── contexto común del día ─────────────────────────
def contexto():
    """Lo que todos ven igual. Mismo texto para los nueve: se cachea una vez por jornada."""
    subprocess.run([sys.executable, P("produccion", "oficina.py")], check=False, capture_output=True)
    est = leer("produccion/estado.json", {"videos": []})["videos"]
    ofi = leer("produccion/oficina.json", {})
    dat = leer("produccion/oficina_datos.json", {})
    aud = (leer("produccion/auditoria.json", {}) or {}).get("videos", {})
    ideas = (leer("produccion/ideas.json", {}) or {}).get("ideas", [])
    tend = leer("produccion/tendencias.json", {}) or {}
    com = leer("produccion/comunidad_analisis.json", {}) or {}
    M = dat.get("mejora") or {}
    clave_tec = ("cam_cada", "cam_inicio_dist", "ov_contadores", "sfx_variedad", "voz_ritmo", "duracion")
    recientes = []
    for v in (dat.get("videos") or [])[:30]:
        recientes.append({k: v.get(k) for k in ("id", "titulo", "formato", "rel", "rel_red", "com_mil", "comp_mil", "juego",
                                                 "serie", "publicado", *clave_tec) if v.get(k) is not None})
    propuestos = [{k: v.get(k) for k in ("id", "formato", "titulo", "guion", "texto", "tags", "juego", "reglas", "ganchos",
                                         "comentario", "revisiones", "seo", "idea", "tendencia") if v.get(k) is not None}
                  for v in est if v.get("estado") == "propuesto"]
    en_marcha = [{"id": v["id"], "titulo": v.get("titulo"), "estado": v.get("estado"), "nota": v.get("nota"),
                  "medidas": {k: (aud.get(v["id"]) or {}).get(k) for k in clave_tec if (aud.get(v["id"]) or {}).get(k) is not None},
                  "mejorar": [x["texto"] for x in (M.get("recomendaciones") or {}).get(v["id"], []) if x["tipo"] == "mejorar"][:4]}
                 for v in est if v.get("estado") in ("aprobado", "voz", "rehacer", "escena", "revision")]
    manual = [{"id": m["id"], "estado": m.get("estado"), "por": m.get("por"), "texto": m["texto"],
               "evidencia": (dat.get("manual") or {}).get(m["id"], {}).get("veredicto")} for m in ofi.get("manual", [])
              if m.get("estado") != "descartada"]
    canal = ofi.get("canal", [])[-40:]
    doc = {
        "fecha": HOY,
        "puestos": {r: {k: (dat.get("puestos") or {}).get(r, {}).get(k) for k in ("ahora", "kpi", "foco")} for r in ROLES},
        "reputacion": dat.get("reputacion"),
        "hallazgos_tecnicos": [{k: h[k] for k in ("rol", "texto", "metrica", "umbral", "direccion", "ratio", "fuerza")} for h in (M.get("hallazgos") or [])[:12]],
        "como_son_los_mejores_videos": M.get("referencia"),
        "manual_vivo": manual,
        "experimentos": [{**x, "evaluacion": (M.get("experimentos") or {}).get(x["id"])} for x in ofi.get("experimentos", [])[-6:]],
        "acuerdos_vigentes": [a for a in ofi.get("acuerdos", []) if a.get("estado") == "vigente"][-30:],
        "videos_recientes": recientes,
        "guiones_propuestos": propuestos,
        "videos_en_marcha": en_marcha,
        "encargos_pendientes": [e for e in ofi.get("encargos", []) if e.get("estado") != "hecho"],
        "ideas_banco": [{"id": i["id"], "texto": i["texto"], "prioridad": i.get("prioridad")} for i in ideas if i.get("estado") != "usada"][:12],
        "ideas_de_seguidores": (com.get("ideas") or [])[:6],
        "tendencias": [{k: t.get(k) for k in ("tema", "puntuacion", "angulo")} for t in (tend.get("tendencias") or [])[:6]],
        "segundas_partes": dat.get("segundas_partes"),
        "candidatos_promocion": dat.get("paid_candidatos"),
        "ultima_reunion": (ofi.get("reuniones") or [{}])[-1].get("resumen"),
        "canal_reciente": canal,
    }
    return json.dumps(doc, ensure_ascii=False, sort_keys=True), {"propuestos": [p["id"] for p in propuestos], "canal": canal}


COMUN = """Eres uno de los nueve trabajadores de la oficina que produce los vídeos de @explicadoen60s (TikTok, Instagram y YouTube: vídeos verticales de 60-75 s que explican cómo funcionan las cosas, en castellano de España, con escenas 3D, voz y gráficos).

Hoy es una jornada de trabajo. Trabajas solo, con tu ficha y los datos de abajo. A tus compañeros solo los conoces por lo que te escriben en el canal: si necesitas algo de alguien, o crees que algo suyo se puede hacer mejor, escríbele un mensaje concreto. Lo que acuerdéis se convierte en una norma que la producción cumple desde mañana, así que pide cosas que se puedan aplicar y medir.

Reglas de la casa:
- Datos antes que opiniones. Cita la cifra (vistas frente a lo normal «×», medidas técnicas de la auditoría, KPI de cada puesto).
- Nada de críticas sin propuesta: cada objeción lleva el arreglo exacto.
- Sé breve y concreto. Nada de saludos ni relleno. Español de España, tuteo.
- No te inventes datos, comentarios ni vídeos. Si un dato no está, dilo.
- Las 3 reglas que deciden si un vídeo funciona: algo que el espectador usa cada día; el objeto en acción y en primer plano en el primer segundo; enséñalo con cifras que cambian en pantalla, no con metáforas.

IDs de tus compañeros: director, fotografia, sonido, editor, motion, estratega, social, paid, seo (o "todos").

DATOS DEL DÍA (JSON):
"""

ESQ_R1 = {
    "type": "object", "additionalProperties": False,
    "required": ["resumen", "analisis", "revisiones", "predicciones", "mensajes", "aprendizajes", "hipotesis", "experimento", "seo"],
    "properties": {
        "resumen": {"type": "string", "description": "Lo más importante que ves hoy desde tu puesto, 1-2 frases con cifra."},
        "analisis": {"type": "array", "description": "Autopsia de vídeos publicados que te digan algo (máx. 3).", "items": {
            "type": "object", "additionalProperties": False, "required": ["video", "texto"],
            "properties": {"video": {"type": "string"}, "texto": {"type": "string"}}}},
        "revisiones": {"type": "array", "description": "Solo si revisas guiones: una por guion propuesto que no hayas revisado ya.", "items": {
            "type": "object", "additionalProperties": False, "required": ["video", "veredicto", "nota", "propuesta"],
            "properties": {"video": {"type": "string"}, "veredicto": {"type": "string", "enum": ["ok", "cambios"]},
                           "nota": {"type": "string"}, "propuesta": {"type": "string"}}}},
        "predicciones": {"type": "array", "description": "Cuántas veces lo normal hará cada guion propuesto sin predicción tuya (0,2-20).", "items": {
            "type": "object", "additionalProperties": False, "required": ["video", "rel", "nota"],
            "properties": {"video": {"type": "string"}, "rel": {"type": "number"}, "nota": {"type": "string"}}}},
        "mensajes": {"type": "array", "description": "1-3 mensajes a compañeros: peticiones, propuestas, avisos o preguntas concretas.", "items": {
            "type": "object", "additionalProperties": False, "required": ["para", "tipo", "asunto", "texto", "video"],
            "properties": {"para": {"type": "string", "enum": ROLES + ["todos"]},
                           "tipo": {"type": "string", "enum": ["peticion", "propuesta", "aviso", "pregunta", "dato"]},
                           "asunto": {"type": "string"}, "texto": {"type": "string"}, "video": {"type": "string"}}}},
        "aprendizajes": {"type": "array", "description": "0-2 lecciones nuevas para tu ficha, con umbral o cifra.", "items": {"type": "string"}},
        "hipotesis": {"type": "array", "description": "0-2 reglas que crees que deberían probarse con los datos.", "items": {
            "type": "object", "additionalProperties": False, "required": ["texto", "campo", "operador", "valor"],
            "properties": {"texto": {"type": "string"}, "campo": {"type": "string", "description": "campo medible o vacío"},
                           "operador": {"type": "string", "enum": ["igual", "mayor", "menor", ""]}, "valor": {"type": "string"}}}},
        "experimento": {"type": "object", "additionalProperties": False, "required": ["proponer", "cambio", "hipotesis", "metrica"],
                        "properties": {"proponer": {"type": "boolean"}, "cambio": {"type": "string"},
                                       "hipotesis": {"type": "string"}, "metrica": {"type": "string"}}},
        "seo": {"type": "array", "description": "Solo el puesto seo: títulos por red de los guiones propuestos sin ellos.", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["video", "tiktok_titulo", "tiktok_texto", "instagram_texto", "youtube_titulo", "youtube_texto", "tags"],
            "properties": {"video": {"type": "string"}, "tiktok_titulo": {"type": "string"}, "tiktok_texto": {"type": "string"},
                           "instagram_texto": {"type": "string"}, "youtube_titulo": {"type": "string"},
                           "youtube_texto": {"type": "string"}, "tags": {"type": "array", "items": {"type": "string"}}}}},
    },
}
ESQ_R2 = {
    "type": "object", "additionalProperties": False, "required": ["respuestas", "aprendizajes", "cambios_guion"],
    "properties": {
        "respuestas": {"type": "array", "description": "Una por cada mensaje de tu bandeja.", "items": {
            "type": "object", "additionalProperties": False, "required": ["mensaje", "decision", "texto", "compromiso"],
            "properties": {"mensaje": {"type": "string"},
                           "decision": {"type": "string", "enum": ["acepto", "matizo", "rechazo", "respondo"]},
                           "texto": {"type": "string"},
                           "compromiso": {"type": "string", "description": "Si aceptas o matizas: la norma exacta que aplicarás desde mañana. Vacío si no."}}}},
        "aprendizajes": {"type": "array", "items": {"type": "string"}},
        "cambios_guion": {"type": "array", "description": "Solo el director: guion corregido por las revisiones.", "items": {
            "type": "object", "additionalProperties": False, "required": ["video", "guion", "titulo", "texto", "respuesta"],
            "properties": {"video": {"type": "string"}, "guion": {"type": "string"}, "titulo": {"type": "string"},
                           "texto": {"type": "string"}, "respuesta": {"type": "string"}}}},
    },
}


def encargo_r1(rol, info):
    tareas = ["Analiza los datos desde tu puesto y escribe tu resumen.",
              "Escribe de 1 a 3 mensajes a compañeros concretos: lo que necesitas de ellos o lo que harían mejor, con la cifra que lo justifica."]
    if rol in REVISAN_GUION and info["propuestos"]:
        tareas.append(f"Revisa los guiones propuestos ({', '.join(info['propuestos'])}) desde tu puesto: veredicto, nota y arreglo exacto.")
    if info["propuestos"]:
        tareas.append(f"Apuesta cuántas veces lo normal hará cada guion propuesto ({', '.join(info['propuestos'])}).")
    if rol == "seo":
        tareas.append("Escribe títulos y pies por red de los guiones propuestos que no tengan «seo».")
    tareas.append("Si los datos lo justifican: aprendizajes para tu ficha, hipótesis medibles y un experimento.")
    tareas.append("Lo que no te toque, déjalo como lista vacía.")
    return f"Jornada del {HOY}. Eres «{rol}».\n" + "\n".join(f"- {t}" for t in tareas)


def bandeja(rol, msgs):
    return [m for m in msgs if m["para"] in (rol, "todos") and m["de"] != rol]


def encargo_r2(rol, msgs, revs_para_director):
    b = bandeja(rol, msgs)
    txt = f"Jornada del {HOY}, segunda ronda. Eres «{rol}». Esta es tu bandeja de hoy:\n"
    txt += json.dumps(b, ensure_ascii=False, indent=1) if b else "(vacía)"
    txt += ("\n\nResponde a cada mensaje: «acepto» o «matizo» con un compromiso exacto que aplicarás desde mañana, "
            "«rechazo» con el motivo y la alternativa, o «respondo» si es una pregunta o un dato.")
    if rol == "director" and revs_para_director:
        txt += ("\n\nRevisiones de tus guiones de hoy:\n" + json.dumps(revs_para_director, ensure_ascii=False, indent=1) +
                "\n\nSi alguna mejora el guion, devuélvelo corregido en «cambios_guion» (guion completo, 205-245 palabras, "
                "con el juego de la cifra intacto) y explica en «respuesta» qué aplicas y qué no.")
    return txt


# ───────────────────────── llamadas ─────────────────────────
class Gasto:
    def __init__(self):
        self.t = {"in": 0, "cache_w": 0, "cache_r": 0, "out": 0}
        self.llamadas = 0

    def suma(self, u):
        self.llamadas += 1
        self.t["in"] += getattr(u, "input_tokens", 0) or 0
        self.t["cache_w"] += getattr(u, "cache_creation_input_tokens", 0) or 0
        self.t["cache_r"] += getattr(u, "cache_read_input_tokens", 0) or 0
        self.t["out"] += getattr(u, "output_tokens", 0) or 0

    def euros(self):
        usd = sum(self.t[k] * PRECIO[k] for k in self.t) / 1e6
        return round(usd * 0.93, 3)


def llamar(cliente, gasto, rol, ctx, encargo, esquema):
    if os.environ.get("JORNADA_SIMULADA"):
        return simulada(rol, encargo, esquema)
    import anthropic
    params = dict(
        model=MODELO, max_tokens=16000,
        system=[{"type": "text", "text": COMUN + ctx, "cache_control": {"type": "ephemeral", "ttl": "1h"}},
                {"type": "text", "text": "TU FICHA:\n" + ficha(rol)}],
        messages=[{"role": "user", "content": encargo}],
        output_config={"effort": ESFUERZO, "format": {"type": "json_schema", "schema": esquema}},
    )
    for intento in range(3):
        try:
            try:
                r = cliente.beta.messages.create(betas=["server-side-fallback-2026-07-01"], fallbacks="default", **params)
            except anthropic.BadRequestError as e:
                if "fallback" not in str(e).lower():
                    raise
                r = cliente.messages.create(**params)  # la cuenta no admite el respaldo: sin él
            gasto.suma(r.usage)
            if r.stop_reason == "refusal":
                raise RuntimeError(f"{rol}: el modelo rechazó la petición")
            if r.stop_reason == "max_tokens":
                raise RuntimeError(f"{rol}: respuesta cortada")
            texto = next(b.text for b in r.content if b.type == "text")
            return json.loads(texto)
        except (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError) as e:
            if intento == 2:
                raise
            time.sleep(20 * (intento + 1))
        except json.JSONDecodeError as e:
            if intento == 2:
                raise RuntimeError(f"{rol}: JSON no válido") from e


def simulada(rol, encargo, esquema):
    """Respuestas de prueba coherentes, para probar la jornada y el panel sin gastar."""
    otros = [r for r in ROLES if r != rol]
    k = ROLES.index(rol)
    if esquema is ESQ_R1:
        props = re.findall(r"propuestos? \(([^)]*)\)", encargo)
        ids = props[0].split(", ") if props else []
        return {"resumen": f"[prueba] {rol}: los vídeos con cámara más viva rinden 2,6× lo normal.",
                "analisis": [{"video": "tormentas", "texto": f"[prueba] {rol} ve que tormentas funcionó por la cifra comparada con Madrid."}],
                "revisiones": [{"video": i, "veredicto": "cambios" if k % 2 else "ok", "nota": f"[prueba] nota de {rol}",
                                "propuesta": f"[prueba] arreglo de {rol}" if k % 2 else ""} for i in ids] if rol in REVISAN_GUION else [],
                "predicciones": [{"video": i, "rel": round(0.8 + k * 0.2, 1), "nota": f"[prueba] {rol}"} for i in ids],
                "mensajes": [{"para": otros[(k * 2) % 8], "tipo": ["peticion", "propuesta", "aviso", "pregunta"][k % 4],
                              "asunto": f"[prueba] asunto de {rol}", "texto": f"[prueba] {rol} pide algo concreto con una cifra.", "video": ""}],
                "aprendizajes": [f"[prueba] lección de {rol} (cambio de plano < 3 s: 2,6×)"] if k % 3 == 0 else [],
                "hipotesis": [{"texto": f"[prueba] hipótesis de {rol}", "campo": "cam_cada", "operador": "menor", "valor": "3"}] if k == 1 else [],
                "experimento": {"proponer": k == 4, "cambio": "[prueba] 5 contadores por vídeo", "hipotesis": "más contadores, más retención", "metrica": "ov_contadores"},
                "seo": [{"video": i, "tiktok_titulo": "[prueba] título TikTok 🔧", "tiktok_texto": "¿Cuál era tu número? 👇",
                         "instagram_texto": "[prueba] pie IG", "youtube_titulo": "[prueba] Cómo funciona", "youtube_texto": "#shorts",
                         "tags": ["comofunciona"]} for i in ids] if rol == "seo" else []}
    ids = re.findall(r'"id": "([^"]+)"', encargo)
    return {"respuestas": [{"mensaje": i, "decision": ["acepto", "matizo", "rechazo", "respondo"][(k + n) % 4],
                            "texto": f"[prueba] respuesta de {rol}",
                            "compromiso": f"[prueba] {rol} se compromete a algo medible" if (k + n) % 4 < 2 else ""} for n, i in enumerate(ids)],
            "aprendizajes": [], "cambios_guion": []}


def jornada():
    sin_clave = not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("JORNADA_SIMULADA")
    if sin_clave:
        return {"sin_clave": True}
    cliente = None
    if not os.environ.get("JORNADA_SIMULADA"):
        import anthropic
        cliente = anthropic.Anthropic(max_retries=3)
    ctx, info = contexto()
    gasto, errores = Gasto(), []

    def ronda(encargos, esquema):
        out = {}
        orden = list(encargos)
        # la primera llamada escribe la caché; las demás la leen
        primero = orden[0]
        try:
            out[primero] = llamar(cliente, gasto, primero, ctx, encargos[primero], esquema)
        except Exception as e:  # noqa: BLE001 - un agente que falla no para la jornada
            errores.append(f"{primero}: {e}")
        with cf.ThreadPoolExecutor(max_workers=4) as ex:
            fut = {ex.submit(llamar, cliente, gasto, r, ctx, encargos[r], esquema): r for r in orden[1:]}
            for f in cf.as_completed(fut):
                try:
                    out[fut[f]] = f.result()
                except Exception as e:  # noqa: BLE001
                    errores.append(f"{fut[f]}: {e}")
        return out

    r1 = ronda({r: encargo_r1(r, info) for r in ROLES}, ESQ_R1)
    msgs = numerar(r1)
    revs = [dict(rol=r, **x) for r, d in r1.items() for x in d.get("revisiones", []) if x.get("veredicto") == "cambios"]
    enc2 = {r: encargo_r2(r, msgs, revs) for r in ROLES if bandeja(r, msgs) or (r == "director" and revs)}
    r2 = ronda(enc2, ESQ_R2) if enc2 else {}
    return {"r1": r1, "r2": r2, "errores": errores, "tokens": gasto.t, "llamadas": gasto.llamadas, "euros": gasto.euros(),
            "modelo": "simulación" if os.environ.get("JORNADA_SIMULADA") else MODELO}


def numerar(r1):
    msgs, n = [], 0
    for rol in ROLES:
        for m in (r1.get(rol) or {}).get("mensajes", []):
            n += 1
            msgs.append({"id": nid("c", n), "de": rol, **m})
    return msgs


# ───────────────────────── aplicar ─────────────────────────
def filtro_de(h):
    campo = (h.get("campo") or "").strip()
    met = set(((leer("produccion/auditoria.json", {}) or {}).get("metricas") or {}).keys())
    if campo not in CAMPOS_FILTRO | met or h.get("operador") not in ("igual", "mayor", "menor"):
        return None
    v = (h.get("valor") or "").strip()
    if v.lower() in ("true", "sí", "si"):
        v = True
    elif v.lower() == "false" or v.lower() == "no":
        v = False
    else:
        try:
            v = float(v.replace(",", "."))
            v = int(v) if v.is_integer() else v
        except ValueError:
            pass
    return {"campo": campo, h["operador"]: v}


def aprender(rol, lecciones):
    """Añade lecciones a «Lo que he aprendido» de la ficha (máx. 10, sin repetir)."""
    if not lecciones:
        return 0
    ruta = P(".claude", "agents", f"{rol}.md")
    t = open(ruta, encoding="utf-8").read()
    cab, _, cuerpo = t.partition("## Lo que he aprendido")
    previas = [l[2:].strip() for l in cuerpo.splitlines() if l.startswith("- ")]
    vistos = {norm(x)[:60] for x in previas}
    nuevas = [f"{l.strip()} ({HOY})" for l in lecciones if l.strip() and norm(l)[:60] not in vistos]
    if not nuevas:
        return 0
    todas = (previas + nuevas)[-10:]
    t = cab + "## Lo que he aprendido\n<!-- Lo amplían las jornadas y las reuniones: máximo 10 puntos, los más recientes. -->\n" + "\n".join(f"- {x}" for x in todas) + "\n"
    open(ruta, "w", encoding="utf-8").write(t)
    return len(nuevas)


def aplicar(res):
    est_doc = leer("produccion/estado.json", {"videos": []})
    ofi = leer("produccion/oficina.json", {})
    for k in ("canal", "acuerdos", "jornadas", "actividad", "manual", "experimentos", "diario"):
        ofi.setdefault(k, [])
    ofi.setdefault("predicciones", {})
    ahora = datetime.now(timezone.utc).isoformat(timespec="seconds")

    if res.get("sin_clave"):
        ofi["jornadas"] = [j for j in ofi["jornadas"] if not (j.get("fecha", "").startswith(HOY) and j.get("estado") == "sin_clave")]
        ofi["jornadas"].append({"fecha": ahora, "estado": "sin_clave"})
        ofi["jornadas"] = ofi["jornadas"][-30:]
        escribir("produccion/oficina.json", ofi)
        return {"sin_clave": True}

    r1, r2 = res.get("r1", {}), res.get("r2", {})
    vid = {v["id"]: v for v in est_doc["videos"]}
    peso = {r: ((leer("produccion/oficina_datos.json", {}) or {}).get("reputacion") or {}).get(r, {}).get("peso", 1) for r in ROLES}
    cuenta = {"mensajes": 0, "respuestas": 0, "acuerdos": 0, "aprendizajes": 0, "hipotesis": 0, "revisiones": 0, "guiones": 0, "seo": 0}
    cambios, aprendido = [], []

    # 1) canal: mensajes de la ronda 1 con sus respuestas de la ronda 2
    msgs = numerar(r1)
    resp = {}
    for rol, d in r2.items():
        for x in d.get("respuestas", []):
            resp.setdefault(x["mensaje"], []).append({"de": rol, **x, "fecha": ahora})
    for m in msgs:
        ofi["canal"].append({"id": m["id"], "fecha": ahora, "jornada": HOY, "de": m["de"], "para": m["para"], "tipo": m["tipo"],
                             "asunto": m["asunto"], "texto": m["texto"], "video": m.get("video") or "",
                             "respuestas": [{k: x[k] for k in ("de", "decision", "texto", "compromiso", "fecha")} for x in resp.get(m["id"], [])]})
        cuenta["mensajes"] += 1
        for x in resp.get(m["id"], []):
            cuenta["respuestas"] += 1
            if x["decision"] in ("acepto", "matizo") and x.get("compromiso", "").strip():
                ofi["acuerdos"].append({"id": "a" + m["id"][1:] + x["de"][:3], "rol": x["de"], "pedido_por": m["de"],
                                        "texto": x["compromiso"].strip(), "desde": HOY, "origen": m["id"], "estado": "vigente"})
                cuenta["acuerdos"] += 1
                cambios.append({"rol": x["de"], "texto": f"Acuerdo con {m['de']}: {x['compromiso'].strip()}"})
    ofi["canal"] = ofi["canal"][-400:]
    vig = [a for a in ofi["acuerdos"] if a.get("estado") == "vigente"]
    if len(vig) > 40:  # los más antiguos caducan: la oficina no puede cumplir cien normas a la vez
        for a in vig[:-40]:
            a["estado"] = "caducado"
    ofi["acuerdos"] = ofi["acuerdos"][-150:]

    for rol in ROLES:
        d1, d2 = r1.get(rol) or {}, r2.get(rol) or {}
        # 2) autopsias y resumen
        for a in d1.get("analisis", [])[:3]:
            ofi["actividad"].append({"fecha": ahora, "rol": rol, "tipo": "analisis", "video": a.get("video"), "texto": a["texto"]})
        # 3) revisiones de guiones propuestos
        for x in d1.get("revisiones", []):
            v = vid.get(x.get("video"))
            if not v or v.get("estado") != "propuesto":
                continue
            v.setdefault("revisiones", [])
            v["revisiones"] = [r for r in v["revisiones"] if not (r.get("rol") == rol and r.get("fase") == "guion" and r.get("jornada") == HOY)]
            v["revisiones"].append({"rol": rol, "fase": "guion", "veredicto": x["veredicto"], "nota": x["nota"],
                                    "propuesta": x.get("propuesta", ""), "jornada": HOY, "agente": True})
            cuenta["revisiones"] += 1
        # 4) predicciones
        for x in d1.get("predicciones", []):
            if x.get("video") in vid and isinstance(x.get("rel"), (int, float)) and 0.1 <= x["rel"] <= 50:
                p = ofi["predicciones"].setdefault(x["video"], {"fecha": ahora, "roles": {}})
                p["roles"][rol] = {"rel": round(float(x["rel"]), 2), "nota": x.get("nota", "")}
        # 5) aprendizajes a la ficha
        n = aprender(rol, (d1.get("aprendizajes") or []) + (d2.get("aprendizajes") or []))
        cuenta["aprendizajes"] += n
        aprendido += [f"{rol}: {l}" for l in ((d1.get("aprendizajes") or []) + (d2.get("aprendizajes") or []))[:n]]
        # 6) hipótesis al Manual (sin repetir)
        textos = {norm(m["texto"])[:50] for m in ofi["manual"]}
        for h in d1.get("hipotesis", [])[:2]:
            if norm(h["texto"])[:50] in textos:
                continue
            f = filtro_de(h)
            if f and any(m.get("filtro") == f for m in ofi["manual"]):
                continue
            ofi["manual"].append({"id": "m" + AHORA.strftime("%y%m%d") + rol[:3] + str(len(ofi["manual"])), "texto": h["texto"],
                                  "estado": "hipotesis", "por": rol, "creada": HOY, "origen": f"Jornada del {HOY}", **({"filtro": f} if f else {})})
            cuenta["hipotesis"] += 1
        # 7) SEO por red
        for s in d1.get("seo", []) if rol == "seo" else []:
            v = vid.get(s.get("video"))
            if v and v.get("estado") == "propuesto":
                v["seo"] = {"tiktok": {"titulo": s["tiktok_titulo"][:100], "texto": s["tiktok_texto"], "tags": s["tags"][:5]},
                            "instagram": {"titulo": v.get("titulo"), "texto": s["instagram_texto"], "tags": s["tags"][:5]},
                            "youtube": {"titulo": s["youtube_titulo"][:100], "texto": s["youtube_texto"], "tags": s["tags"][:5]}}
                cuenta["seo"] += 1

    # 8) cambios de guion del director, solo si pasan las compuertas
    for c in (r2.get("director") or {}).get("cambios_guion", []):
        v = vid.get(c.get("video"))
        if not v or v.get("estado") != "propuesto":
            continue
        prueba = {**v, "guion": c["guion"], "titulo": c["titulo"] or v.get("titulo"), "texto": c["texto"] or v.get("texto")}
        errores = [x for x in OF.compuertas(prueba) if x["nivel"] == "error"]
        hoy_revs = [r for r in v.get("revisiones", []) if r.get("jornada") == HOY and r.get("veredicto") == "cambios"]
        if errores:
            for r in hoy_revs:
                r["respuesta"] = f"Director: no aplicado, el guion corregido no pasa las compuertas ({errores[0]['texto']})."
            continue
        v.update({"guion": prueba["guion"], "titulo": prueba["titulo"], "texto": prueba["texto"]})
        if v.get("ganchos"):
            v["ganchos"][0] = re.split(r"(?<=[.?!…])\s", prueba["guion"], maxsplit=1)[0]
        for r in hoy_revs:
            r["aplicada"] = True
            r["respuesta"] = "Director: " + c.get("respuesta", "")
        cuenta["guiones"] += 1
        cambios.append({"rol": "director", "texto": f"Guion de «{v.get('titulo')}» corregido con las revisiones: {c.get('respuesta', '')}"})

    # 9) un experimento nuevo como mucho (el de quien más acierta), si hay hueco
    activos = [x for x in ofi["experimentos"] if x.get("estado") == "activo"]
    props = sorted([(peso.get(r, 1), r, (r1.get(r) or {}).get("experimento") or {}) for r in ROLES], reverse=True)
    for _, rol, e in props:
        if len(activos) >= 3 or not e.get("proponer") or not e.get("cambio", "").strip():
            continue
        if any(norm(x.get("cambio"))[:40] == norm(e["cambio"])[:40] for x in ofi["experimentos"]):
            continue
        x = {"id": "x" + AHORA.strftime("%y%m%d") + rol[:3], "rol": rol, "cambio": e["cambio"], "hipotesis": e.get("hipotesis", ""),
             "desde": HOY, "videos": [], "estado": "activo", **({"metrica": e["metrica"]} if e.get("metrica") else {})}
        ofi["experimentos"].append(x)
        activos.append(x)
        cambios.append({"rol": rol, "texto": f"Abre el experimento: {e['cambio']}"})
        break

    # 10) diario y registro de la jornada
    frases = [d.get("resumen") for r in ROLES if (d := r1.get(r)) and d.get("resumen")]
    ofi["diario"].append({"fecha": ahora, "autor": "jornada",
                          "resumen": f"{cuenta['mensajes']} mensajes, {cuenta['acuerdos']} acuerdos, {cuenta['revisiones']} revisiones y {cuenta['aprendizajes']} lecciones nuevas.",
                          "aprendido": aprendido[:10] or frases[:4], "cambios": cambios[:14],
                          "experimentos": [x["id"] for x in activos]})
    ofi["diario"] = ofi["diario"][-60:]
    ofi["jornadas"] = [j for j in ofi["jornadas"] if not (j.get("fecha", "").startswith(HOY) and j.get("estado") == "sin_clave")]
    ofi["jornadas"].append({"fecha": ahora, "estado": "hecha" if r1 else "fallida", "modelo": res.get("modelo"), "llamadas": res.get("llamadas"),
                            "tokens": res.get("tokens"), "euros": res.get("euros"), "errores": res.get("errores", [])[:9],
                            "resumenes": {r: (r1.get(r) or {}).get("resumen", "") for r in ROLES}, **cuenta})
    ofi["jornadas"] = ofi["jornadas"][-30:]
    ofi["actividad"].append({"fecha": ahora, "rol": "director", "tipo": "reunion",
                             "texto": f"Jornada del {HOY}: {cuenta['mensajes']} mensajes entre puestos, {cuenta['acuerdos']} acuerdos nuevos, "
                                      f"{cuenta['guiones']} guiones mejorados y {cuenta['aprendizajes']} lecciones a las fichas."})
    ofi["actividad"] = ofi["actividad"][-300:]
    escribir("produccion/estado.json", est_doc)
    escribir("produccion/oficina.json", ofi)
    subprocess.run([sys.executable, P("produccion", "oficina.py")], check=False, capture_output=True)
    return cuenta


# ───────────────────────── modo «agentes de Claude Code» ─────────────────────────
def preparar(dirr, ronda):
    os.makedirs(dirr, exist_ok=True)
    ctx, info = contexto()
    open(os.path.join(dirr, "contexto.txt"), "w", encoding="utf-8").write(COMUN + ctx)
    if ronda == 1:
        for r in ROLES:
            open(os.path.join(dirr, f"encargo1_{r}.txt"), "w", encoding="utf-8").write(
                encargo_r1(r, info) + f"\n\nLee {dirr}/contexto.txt (datos del día) y tu ficha. Devuelve SOLO un JSON con este esquema:\n" + json.dumps(ESQ_R1, ensure_ascii=False))
    else:
        r1 = {r: json.load(open(os.path.join(dirr, f"r1_{r}.json"), encoding="utf-8")) for r in ROLES if os.path.exists(os.path.join(dirr, f"r1_{r}.json"))}
        msgs = numerar(r1)
        revs = [dict(rol=r, **x) for r, d in r1.items() for x in d.get("revisiones", []) if x.get("veredicto") == "cambios"]
        for r in ROLES:
            if bandeja(r, msgs) or (r == "director" and revs):
                open(os.path.join(dirr, f"encargo2_{r}.txt"), "w", encoding="utf-8").write(
                    encargo_r2(r, msgs, revs) + f"\n\nDevuelve SOLO un JSON con este esquema:\n" + json.dumps(ESQ_R2, ensure_ascii=False))
    print("\n".join(sorted(f for f in os.listdir(dirr) if f.startswith(f"encargo{ronda}_"))))


def aplicar_dir(dirr):
    carga = lambda pre: {r: json.load(open(os.path.join(dirr, f"{pre}_{r}.json"), encoding="utf-8"))
                         for r in ROLES if os.path.exists(os.path.join(dirr, f"{pre}_{r}.json"))}
    return aplicar({"r1": carga("r1"), "r2": carga("r2"), "modelo": "agentes de Claude Code", "errores": [], "llamadas": None})


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--aplicar"]:
        print(aplicar(json.load(open(a[1], encoding="utf-8"))))
    elif a[:1] == ["--preparar"]:
        preparar(a[1], int(a[2]) if len(a) > 2 else 1)
    elif a[:1] == ["--aplicar-dir"]:
        print(aplicar_dir(a[1]))
    else:
        res = jornada()
        if a[:1] == ["--guardar"]:
            json.dump(res, open(a[1], "w", encoding="utf-8"), ensure_ascii=False)
        print(json.dumps(aplicar(res), ensure_ascii=False))
        if res.get("sin_clave"):
            print("Sin ANTHROPIC_API_KEY: la jornada la hará la pasada diaria con los agentes de Claude Code.")
