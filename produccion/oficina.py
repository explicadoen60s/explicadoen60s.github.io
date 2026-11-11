#!/usr/bin/env python3
"""La oficina de explicadoen60s: la parte que se calcula sin Claude.

Uso:
  python3 produccion/oficina.py               -> recalcula produccion/oficina_datos.json
  python3 produccion/oficina.py comprobar     -> compuertas de todos los guiones «propuesto»
  python3 produccion/oficina.py comprobar ID  -> compuertas de un guion (sale con 1 si falla)

Lee estado.json, oficina.json, ideas.json, tendencias.json, comunidad_analisis.json y
programador/estadisticas.json + comunidad.json. Solo escribe oficina_datos.json
(lo enseña el panel en «Oficina»). No necesita red ni secretos.
"""
import json, math, os, re, sys, unicodedata
from datetime import datetime, timezone, timedelta

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *r: os.path.join(RAIZ, *r)
AHORA = datetime.now(timezone.utc)
REDES = ["tiktok", "instagram", "youtube"]
MADURO_H = 48          # horas para que un vídeo cuente en el análisis
MIN_N = 3              # vídeos mínimos a cada lado para dar una regla por buena


def leer(ruta, defecto):
    try:
        with open(P(ruta), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return defecto


def fecha(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def norm(t):
    """Igual que norm() del panel (estadisticas.js) para casar títulos."""
    t = unicodedata.normalize("NFD", (t or "").lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-z0-9 ]", "", t)
    return re.sub(r"\s+", " ", t).strip()[:60]


def mediana(a):
    s = sorted(x for x in a if x is not None and math.isfinite(x))
    if not s:
        return None
    m = len(s) // 2
    return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2


def r2(x, d=2):
    return None if x is None else round(x, d)


# ───────────────────────── Compuertas (comprobaciones automáticas) ─────────────────────────
NUM_PAL = re.compile(r"\b(\d+[\d.,]*|cero|uno|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|"
                     r"quince|veinte|treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa|cien|ciento|"
                     r"doscientos|trescientos|quinientos|mil|millón|millones|mitad|doble|triple)\b", re.I)
PROHIBIDO = re.compile(r"\b(casino|apuesta|apuestas|ruleta|loter[ií]a|póker|poker|pistola|rifle|arma|armas|"
                       r"atentado|asesinato|partido pol[ií]tico)\b", re.I)


def compuertas(v):
    """Lista de (nivel, puesto, texto). nivel: ok | aviso | error. Error = no puede pasar a revisión."""
    out = []
    add = lambda n, rol, t: out.append({"nivel": n, "rol": rol, "texto": t})
    g = v.get("guion") or ""
    pal = len(g.split())
    if 205 <= pal <= 245:
        add("ok", "sonido", f"{pal} palabras (≈{round(pal / 3.4)} s)")
    elif 190 <= pal <= 260:
        add("aviso", "sonido", f"{pal} palabras: fuera de 205-245 (≈{round(pal / 3.4)} s)")
    else:
        add("error", "sonido", f"{pal} palabras: tiene que estar entre 205 y 245")
    nums = len(NUM_PAL.findall(g))
    add("ok" if nums >= 4 else "aviso" if nums >= 2 else "error", "motion",
        f"{nums} cifras en el guion (mínimo 2 que se puedan enseñar)")
    j = v.get("juego")
    if not isinstance(j, dict):
        add("error", "director", "Falta el campo «juego» (juego de la cifra, obligatorio)")
    else:
        falta = [k for k in ("pregunta", "valor", "unidad", "pregunta_en", "revela_en") if j.get(k) in (None, "")]
        if falta:
            add("error", "director", "Al juego le falta: " + ", ".join(falta))
        else:
            pos_p = g.find(str(j["pregunta_en"])[:25])
            pos_r = g.find(str(j["revela_en"])[:25])
            if pos_p < 0 or pos_r < 0:
                add("error", "editor", "«pregunta_en» o «revela_en» no aparecen tal cual en el guion")
            elif pos_r / max(1, len(g)) < 0.25:
                add("aviso", "editor", "La cifra se revela demasiado pronto (debe ser pasado el primer cuarto)")
            else:
                add("ok", "editor", "Juego de la cifra bien colocado")
    reg = v.get("reglas") or {}
    for k, rol, nom in (("cotidiano", "estratega", "tema cotidiano"), ("primer_segundo", "fotografia", "primer segundo"),
                        ("ensenar", "motion", "enséñalo")):
        n = reg.get(k)
        if n is None:
            add("error", rol, f"Falta la nota de la regla «{nom}»")
        elif n < 7:
            add("error", rol, f"Regla «{nom}» con {n}/10: tiene que llegar a 7")
        else:
            add("ok", rol, f"Regla «{nom}»: {n}/10")
    if len(v.get("ganchos") or []) < 3:
        add("aviso", "director", "Faltan ganchos alternativos (se piden 3)")
    t = (v.get("titulo") or "")
    if len(t) > 100:
        add("error", "seo", f"Título de {len(t)} caracteres (máximo 100)")
    if not re.search(r"[\U0001F300-\U0001FAFF☀-➿]", t):
        add("aviso", "seo", "El título no lleva emoji")
    tx = (v.get("texto") or "").strip()
    if not tx.endswith(("?", "👇")):
        add("aviso", "social", "El pie no termina en pregunta ni en 👇")
    if len(v.get("tags") or []) != 5:
        add("aviso", "seo", f"{len(v.get('tags') or [])} temas en «tags» (se piden 5)")
    if PROHIBIDO.search(g + " " + t):
        add("error", "estratega", "Tema vetado por la línea editorial (apuestas, armas, sucesos…)")
    if not re.search(r"sígueme", g, re.I):
        add("aviso", "social", "El cierre no dice «Sígueme»")
    return out


def cmd_comprobar(ids):
    est = leer("produccion/estado.json", {"videos": []})["videos"]
    sel = [v for v in est if (v["id"] in ids if ids else v.get("estado") == "propuesto")]
    if ids and not sel:
        print("No encuentro:", ", ".join(ids))
        return 2
    malo = False
    for v in sel:
        c = compuertas(v)
        errs = [x for x in c if x["nivel"] == "error"]
        malo |= bool(errs)
        print(f"\n{'✗' if errs else '✓'} {v['id']} · {v.get('titulo', '')}")
        for x in c:
            if x["nivel"] != "ok":
                print(f"   [{x['nivel']}] {x['rol']}: {x['texto']}")
    return 1 if malo else 0


# ───────────────────────── Datos de cada vídeo ─────────────────────────
def rasgos(v, rel_videos):
    """Rasgos de un vídeo que sirven para comprobar reglas del Manual."""
    t = v.get("titulo") or ""
    return {
        "id": v["id"], "titulo": t, "formato": v.get("formato"), "juego": bool(v.get("juego")),
        "comentario": bool(v.get("comentario")), "serie": "esconde tu ciudad" in t.lower() or v.get("serie") == "ciudad",
        "parte2": bool(re.search(r"parte\s*2|\(parte", t, re.I)),
        "titulo_pregunta": "¿" in t or "?" in t, "titulo_cifra": bool(re.search(r"\d", t)),
        "duracion": v.get("duracion"), "gancho": v.get("gancho_elegido"), "rehacer": v.get("rehacer_n", 0),
        "palabras": len((v.get("guion") or "").split()), "tendencia": bool(v.get("tendencia")), "idea": bool(v.get("idea")),
        "cotidiano": (v.get("reglas") or {}).get("cotidiano"), "ensenar": (v.get("reglas") or {}).get("ensenar"),
        "primer_segundo": (v.get("reglas") or {}).get("primer_segundo"),
        **rel_videos,
    }


def indice(est, cal):
    """Texto normalizado -> id del vídeo. TikTok e Instagram guardan como «título» el pie del post."""
    idx = {}
    for v in est:
        for t in (v.get("titulo"), v.get("texto")):
            if norm(t):
                idx.setdefault(norm(t)[:40], v["id"])
    for p in cal:
        vid = re.sub(r"-(tiktok|instagram|youtube)$", "", p.get("id") or "")
        for t in (p.get("titulo"), p.get("texto")):
            if norm(t) and vid:
                idx.setdefault(norm(t)[:40], vid)
    return idx


def buscar(idx, texto):
    n = norm(texto)[:40]
    if not n:
        return None
    if n in idx:
        return idx[n]
    if len(n) >= 20:
        for k, v in idx.items():
            if len(k) >= 20 and (k.startswith(n) or n.startswith(k)):
                return v
    return None


def unir(est, st, cal=(), aud=None):
    """Une cada vídeo de estado.json con sus publicaciones en las 3 redes (por título, pie o calendario)."""
    idx = indice(est, cal)
    medianas, inter_med = {}, {}
    pubs = []
    for r in REDES:
        vs = [x for x in (st.get("videos") or {}).get(r, []) if (x.get("vistas") or 0) > 0]
        medianas[r] = mediana([x["vistas"] for x in vs]) or 1
        ints = []
        fechas = [(fecha(x.get("fecha")), x["vistas"]) for x in vs]

        def normal(f0):
            """«Lo normal» para un vídeo: mediana de su red entre los publicados ±5 días (la cuenta crece rápido)."""
            if not f0:
                return medianas[r]
            cerca = [vv for ff, vv in fechas if ff and abs((ff - f0).total_seconds()) <= 5 * 86400]
            return (mediana(cerca) if len(cerca) >= 5 else None) or medianas[r]
        for x in vs:
            i = ((x.get("likes") or 0) + 2 * (x.get("comentarios") or 0) + 3 * (x.get("compartidos") or 0) + 2 * (x.get("guardados") or 0)) / x["vistas"]
            ints.append(i)
            f = fecha(x.get("fecha"))
            pubs.append({"red": r, "id": x.get("id"), "titulo": x.get("titulo"), "url": x.get("url"), "fecha": x.get("fecha"),
                         "vistas": x["vistas"], "comentarios": x.get("comentarios") or 0, "compartidos": x.get("compartidos") or 0,
                         "guardados": x.get("guardados") or 0, "likes": x.get("likes") or 0, "inter": i,
                         "rel": x["vistas"] / normal(f), "horas": (AHORA - f).total_seconds() / 3600 if f else None,
                         "video": buscar(idx, x.get("titulo"))})
        inter_med[r] = mediana(ints)
    vids = []
    for v in est:
        ps = [p for p in pubs if p["video"] == v["id"]]
        mad = [p for p in ps if p["horas"] is not None and p["horas"] >= MADURO_H]
        rel = mediana([p["rel"] for p in mad])
        V = sum(p["vistas"] for p in ps)
        tec = {k: x for k, x in ((aud or {}).get(v["id"]) or {}).items() if k != "huella"}
        vids.append(rasgos(v, {
            **tec,
            "estado": v.get("estado"), "creado": v.get("creado"),
            "rel": r2(rel), "maduro": bool(mad), "vistas": V,
            "rel_red": {p["red"]: r2(p["rel"]) for p in ps},
            "com_mil": r2(sum(p["comentarios"] for p in ps) / V * 1000) if V else None,
            "comp_mil": r2(sum(p["compartidos"] for p in ps) / V * 1000) if V else None,
            "publicado": min((p["fecha"] for p in ps if p["fecha"]), default=None),
        }))
    return vids, pubs, medianas, inter_med


# ───────────────────────── Manual vivo: evidencia de cada regla ─────────────────────────
def cumple(x, f):
    """f = {"campo": "...", "igual"|"distinto"|"menor"|"mayor"|"contiene": valor}  (o lista = todas)."""
    if isinstance(f, list):
        return all(cumple(x, g) for g in f)
    val = x.get(f.get("campo"))
    if "igual" in f:
        return val == f["igual"]
    if "distinto" in f:
        return val != f["distinto"]
    if val is None:
        return False
    if "menor" in f:
        return val < f["menor"]
    if "mayor" in f:
        return val > f["mayor"]
    if "contiene" in f:
        return str(f["contiene"]).lower() in str(val).lower()
    return False


def evidencia(maduros, filtro):
    si = [v["rel"] for v in maduros if cumple(v, filtro)]
    no = [v["rel"] for v in maduros if not cumple(v, filtro)]
    ms, mn = mediana(si), mediana(no)
    ratio = (ms / mn) if ms and mn else None
    if len(si) < MIN_N or len(no) < MIN_N or ratio is None:
        ver = "faltan_datos"
    elif ratio >= 1.2:
        ver = "a_favor"
    elif ratio <= 0.85:
        ver = "en_contra"
    else:
        ver = "sin_efecto"
    return {"n_si": len(si), "n_no": len(no), "med_si": r2(ms), "med_no": r2(mn), "ratio": r2(ratio), "veredicto": ver}


SENALES = [  # rasgos que se prueban solos cada hora para dar ideas de reglas a la reunión
    ("Formato A «Así funciona»", {"campo": "formato", "igual": "A"}),
    ("Formato B «Si tuvieras que inventar…»", {"campo": "formato", "igual": "B"}),
    ("Formato C «¿Y si construyes…?»", {"campo": "formato", "igual": "C"}),
    ("Con juego de la cifra", {"campo": "juego", "igual": True}),
    ("Responde a un comentario", {"campo": "comentario", "igual": True}),
    ("Serie «Lo que esconde tu ciudad»", {"campo": "serie", "igual": True}),
    ("Título en forma de pregunta", {"campo": "titulo_pregunta", "igual": True}),
    ("Título con una cifra", {"campo": "titulo_cifra", "igual": True}),
    ("Vídeo de menos de 65 s", {"campo": "duracion", "menor": 65}),
    ("Sale de una tendencia", {"campo": "tendencia", "igual": True}),
    ("Sale del banco de ideas", {"campo": "idea", "igual": True}),
    ("Se eligió el 1.er gancho", {"campo": "gancho", "igual": 0}),
    ("Regla «cotidiano» con 9 o más", {"campo": "cotidiano", "mayor": 8}),
    ("Necesitó correcciones", {"campo": "rehacer", "mayor": 0}),
]


# ───────────────────────── Mejora continua: qué tienen los vídeos que funcionan ─────────────────────────
MIN_LADO = 4   # vídeos mínimos a cada lado de la mediana para dar un hallazgo


def fmt_num(x, u=""):
    if x is None:
        return "—"
    if float(x).is_integer() and abs(x) >= 1:
        x = int(x)
        return f"{x}" + (f" {u}" if u and u != "%" else u)
    t = (f"{x:.0f}" if abs(x) >= 20 else f"{x:.1f}" if abs(x) >= 2 else f"{x:.2f}").replace(".", ",")
    return t + (f" {u}" if u and u not in ("%",) else u)


def hallazgos(maduros, metricas, banderas):
    """Para cada medida técnica: ¿rinden más los vídeos por encima o por debajo de la mediana?"""
    out = []
    for k, m in metricas.items():
        xs = [v[k] for v in maduros if isinstance(v.get(k), (int, float))]
        if len(xs) < 2 * MIN_LADO:
            continue
        med = mediana(xs)
        if med is None or len(set(xs)) < 3:
            continue
        e = evidencia([v for v in maduros if isinstance(v.get(k), (int, float))], {"campo": k, "mayor": med})
        if e["n_si"] < MIN_LADO or e["n_no"] < MIN_LADO or e["ratio"] is None:
            continue
        if e["ratio"] >= 1.2:
            dire = "mas"
        elif e["ratio"] <= 0.85:
            dire = "menos"
        else:
            continue
        fuerza = abs(math.log(e["ratio"])) * math.sqrt(min(e["n_si"], e["n_no"]))
        lado = "más de" if dire == "mas" else "menos de"
        mejor = e["med_si"] if dire == "mas" else e["med_no"]
        peor = e["med_no"] if dire == "mas" else e["med_si"]
        sorpresa = m.get("mejor") and m["mejor"] != dire
        out.append({"metrica": k, "nombre": m["nombre"], "rol": m["rol"], "unidad": m.get("unidad", ""), "umbral": r2(med),
                    "direccion": dire, "ratio": r2(max(e["ratio"], 1 / e["ratio"])), "n_si": e["n_si"], "n_no": e["n_no"],
                    "fuerza": r2(fuerza), "sorpresa": bool(sorpresa),
                    "texto": f"{m['nombre']}: los vídeos con {lado} {fmt_num(med, m.get('unidad', ''))} rinden "
                             f"{fmt_num(mejor)}× lo normal, frente a {fmt_num(peor)}× los demás"
                             + (" (al revés de lo que se esperaba)" if sorpresa else "") + "."})
    for k, (nom, rol) in banderas.items():
        e = evidencia(maduros, {"campo": k, "igual": True})
        if e["veredicto"] in ("a_favor", "en_contra"):
            dire = "mas" if e["veredicto"] == "a_favor" else "menos"
            out.append({"metrica": k, "nombre": nom, "rol": rol, "unidad": "", "umbral": None, "direccion": dire,
                        "ratio": r2(max(e["ratio"], 1 / e["ratio"])), "n_si": e["n_si"], "n_no": e["n_no"],
                        "fuerza": r2(abs(math.log(e["ratio"])) * math.sqrt(min(e["n_si"], e["n_no"]))), "sorpresa": False,
                        "texto": f"{nom}: {'rinde' if dire == 'mas' else 'no rinde'} ({fmt_num(e['med_si'])}× frente a {fmt_num(e['med_no'])}×)."})
    out.sort(key=lambda h: -h["fuerza"])
    return out


def recomendaciones(vids, hall, metricas):
    """Qué mejorar en los vídeos en marcha y recién publicados, y qué potenciar del mejor de la semana."""
    rec = {}
    vivos = [v for v in vids if v.get("estado") in ("propuesto", "aprobado", "voz", "escena", "rehacer", "revision")
             or (v.get("publicado") and fecha(v["publicado"]) and fecha(v["publicado"]) > AHORA - timedelta(days=7))]
    for v in vivos:
        items = []
        for h in hall:
            x = v.get(h["metrica"])
            if h["umbral"] is None or not isinstance(x, (int, float)):
                continue
            malo = x <= h["umbral"] if h["direccion"] == "mas" else x > h["umbral"]
            u = h["unidad"]
            if malo:
                items.append({"rol": h["rol"], "tipo": "mejorar", "metrica": h["metrica"],
                              "texto": f"{h['nombre']}: {fmt_num(x, u)}. Los que funcionan van {'por encima' if h['direccion'] == 'mas' else 'por debajo'} de {fmt_num(h['umbral'], u)} ({fmt_num(h['ratio'])}× más vistas)."})
            else:
                items.append({"rol": h["rol"], "tipo": "potenciar", "metrica": h["metrica"],
                              "texto": f"{h['nombre']}: {fmt_num(x, u)}, en el lado bueno. Mantenlo."})
        if items:
            rec[v["id"]] = items[:8]
    return rec


def evaluar_experimentos(exps, por_id):
    """Un experimento compara sus vídeos con lo normal (1×) cuando ya llevan 48 h publicados."""
    out = {}
    for x in exps or []:
        vs = [por_id[i] for i in x.get("videos", []) if i in por_id]
        mad = [v["rel"] for v in vs if v.get("maduro") and v.get("rel") is not None]
        if not mad:
            out[x["id"]] = {"maduros": 0, "total": len(vs), "veredicto": "esperando"}
            continue
        m = mediana(mad)
        ver = "esperando" if len(mad) < 2 else "ganado" if m >= 1.2 else "perdido" if m < 0.85 else "neutro"
        out[x["id"]] = {"maduros": len(mad), "total": len(vs), "mediana": r2(m), "veredicto": ver}
    return out


# ───────────────────────── Predicciones y reputación ─────────────────────────
def puntuar(predicciones, por_id, equipo):
    rep = {e["id"]: {"n": 0, "ok": 0, "err": []} for e in equipo}
    res = {}
    for vid, p in (predicciones or {}).items():
        v = por_id.get(vid)
        if not v or v.get("rel") is None or not v.get("maduro"):
            continue
        real = v["rel"]
        fila = {}
        for rol, q in (p.get("roles") or {}).items():
            pred = q.get("rel") if isinstance(q, dict) else q
            if not isinstance(pred, (int, float)) or pred <= 0:
                continue
            ok = (pred >= 1) == (real >= 1)
            e = abs(math.log2(pred / max(real, 0.01)))
            fila[rol] = {"pred": pred, "ok": ok, "error": r2(e)}
            rep.setdefault(rol, {"n": 0, "ok": 0, "err": []})
            rep[rol]["n"] += 1
            rep[rol]["ok"] += ok
            rep[rol]["err"].append(e)
        if fila:
            res[vid] = {"real": real, "roles": fila}
    out = {}
    for rol, r in rep.items():
        acc = (r["ok"] + 1) / (r["n"] + 2)            # con un empujón hacia el 50 % mientras hay pocos datos
        out[rol] = {"n": r["n"], "aciertos": r["ok"], "acierto": r2(r["ok"] / r["n"]) if r["n"] else None,
                    "error_medio": r2(sum(r["err"]) / len(r["err"])) if r["err"] else None,
                    "peso": r2(max(0.5, min(2.0, 2 * acc)))}
    return out, res


# ───────────────────────── Puestos: qué tienen entre manos y su número ─────────────────────────
def puestos(est, vids, pubs, medianas, inter_med, ofi, ideas, tend, com, coman, paid_cand, segundas):
    por = lambda *e: [v for v in est if v.get("estado") in e]
    recientes = [v for v in vids if v["maduro"] and v.get("publicado") and fecha(v["publicado"]) > AHORA - timedelta(days=14)]
    progs = [v for v in est if v.get("estado") == "programado"]
    encargos = [e for e in ofi.get("encargos", []) if e.get("estado") != "hecho"]
    enc = lambda rol: [e for e in encargos if e.get("rol") in (rol, None, "", "todos")]
    sin_seo = [v for v in por("propuesto", "aprobado", "voz", "escena", "revision") if not v.get("seo")]
    voz, reh, esc, rev = por("voz"), por("rehacer"), por("escena", "renderizando"), por("revision")
    pend_ideas = [i for i in ideas if i.get("estado") != "usada"]
    tend_ed = fecha(tend.get("actualizado"))
    coms = com.get("comentarios") or []
    resp = coman.get("respuestas") or {}
    tt = [p for p in pubs if p["red"] == "tiktok" and p["horas"] and p["horas"] <= 24 * 14]
    V = sum(p["vistas"] for p in tt) or 0
    durs = [v.get("duracion") for v in progs[-20:] if v.get("duracion")]
    ens = [(v.get("reglas") or {}).get("ensenar") for v in est[-20:] if (v.get("reglas") or {}).get("ensenar") is not None]
    hechos = [v for v in est if v.get("estado") in ("programado", "rechazado") and (v.get("creado") or "") >= "2026-11-12"]
    sin_rehacer = [v for v in progs if (v.get("creado") or "") >= "2026-11-12"]
    paid_lz = [p for p in ofi.get("paid", []) if p.get("estado") == "lanzado"]

    def k(nombre, valor, fmt="num", meta=None, pie=""):
        return {"nombre": nombre, "valor": valor, "fmt": fmt, "meta": meta, "pie": pie}

    rel_rec = [v["rel"] for v in recientes]
    return {
        "director": {"ahora": f"{len(por('propuesto'))} guiones esperando tu visto bueno" + (f" · {len([v for v in est if v.get('nota_guion')])} por reescribir" if any(v.get('nota_guion') for v in est) else ""),
                     "pendiente": len([v for v in est if v.get("nota_guion")]) + len(enc("director")),
                     "kpi": k("Mediana de los últimos 14 días", r2(mediana(rel_rec)), "x", 1.5, f"{len(rel_rec)} vídeos maduros, frente a lo normal")},
        "fotografia": {"ahora": f"{len(voz)} escenas por plantear · {len(reh)} correcciones" if voz or reh else "Al día: sin escenas pendientes",
                       "pendiente": len(voz) + len(reh),
                       "kpi": k("Vídeos sin pedir cambios", r2(len([v for v in sin_rehacer if not v.get('rehacer_n')]) / len(sin_rehacer)) if sin_rehacer else None, "pct", 0.8, "desde el 12-nov")},
        "sonido": {"ahora": f"{len(por('aprobado'))} voces generándose · {len(voz)} mezclas por hacer",
                   "pendiente": len(voz),
                   "kpi": k("Duración media", r2(sum(durs) / len(durs), 1) if durs else None, "s", 70, f"{len([d for d in durs if 55 <= d <= 75])}/{len(durs)} entre 55 y 75 s")},
        "editor": {"ahora": f"{len(esc)} en render · {len(rev)} esperando tu revisión",
                   "pendiente": len(rev),
                   "kpi": k("Compartidos por 1.000 vistas", r2(sum(p["compartidos"] for p in tt) / V * 1000) if V else None, "dec", 3, "TikTok, últimos 14 días")},
        "motion": {"ahora": f"{len(voz) + len(reh)} capas de gráficos por montar" if voz or reh else "Al día",
                   "pendiente": len(voz) + len(reh),
                   "kpi": k("Nota media de «enséñalo»", r2(sum(ens) / len(ens), 1) if ens else None, "dec", 9, "últimos 20 guiones")},
        "estratega": {"ahora": f"{len(pend_ideas)} ideas en el banco · tendencias {'de hoy' if tend_ed and AHORA - tend_ed < timedelta(hours=30) else 'sin actualizar'}" + (f" · {len(segundas)} segundas partes por proponer" if segundas else ""),
                      "pendiente": len(segundas) + len(enc("estratega")),
                      "kpi": k("Vídeos por encima de lo normal", r2(len([x for x in rel_rec if x >= 1]) / len(rel_rec)) if rel_rec else None, "pct", 0.5, "últimos 14 días")},
        "social": {"ahora": f"{len(coms)} comentarios leídos · {len(resp)} respuestas sugeridas",
                   "pendiente": max(0, len([c for c in coms if c.get("id") not in resp])),
                   "kpi": k("Comentarios por 1.000 vistas", r2(sum(p["comentarios"] for p in tt) / V * 1000) if V else None, "dec", 1, "TikTok, últimos 14 días")},
        "paid": {"ahora": f"{len(paid_cand)} vídeos candidatos a promocionar" if paid_cand else "Ningún vídeo despega ahora mismo: no gastes",
                 "pendiente": len([c for c in paid_cand if not c.get("decidido")]),
                 "kpi": k("Promociones lanzadas", len(paid_lz), "num", None, f"{sum(p.get('gasto') or 0 for p in paid_lz):g} € invertidos")},
        "seo": {"ahora": f"{len(sin_seo)} vídeos sin título por red" if sin_seo else "Títulos por red al día",
                "pendiente": len(sin_seo),
                "kpi": k("YouTube frente a lo normal", r2(mediana([p["rel"] for p in pubs if p["red"] == "youtube" and p["horas"] and 48 <= p["horas"] <= 24 * 14])), "x", 1.2, "la red que más vive de la búsqueda, últimos 14 días")},
    }


# ───────────────────────── Principal ─────────────────────────
def calcular():
    est = leer("produccion/estado.json", {"videos": []})["videos"]
    ofi = leer("produccion/oficina.json", {})
    st = leer("programador/estadisticas.json", {})
    ideas = leer("produccion/ideas.json", {"ideas": []}).get("ideas", [])
    tend = leer("produccion/tendencias.json", {})
    com = leer("programador/comunidad.json", {})
    coman = leer("produccion/comunidad_analisis.json", {})
    cal = leer("programador/calendario.json", {"posts": []}).get("posts", [])
    aud = leer("produccion/auditoria.json", {})
    equipo = ofi.get("equipo", [])

    vids, pubs, medianas, inter_med = unir(est, st, cal, aud.get("videos"))
    por_id = {v["id"]: v for v in vids}
    maduros = [v for v in vids if v["maduro"] and v["rel"] is not None]

    manual = {}
    for m in ofi.get("manual", []):
        if m.get("filtro"):
            manual[m["id"]] = evidencia(maduros, m["filtro"])
    senales = []
    for nom, f in SENALES:
        e = evidencia(maduros, f)
        if e["veredicto"] in ("a_favor", "en_contra"):
            senales.append({"senal": nom, "filtro": f, **e})
    senales.sort(key=lambda s: -abs(math.log(s["ratio"])))

    rep, pred_res = puntuar(ofi.get("predicciones"), por_id, equipo)

    # Paid Media: vídeos de los últimos 5 días que ya van muy por encima de lo normal
    decid = {(p.get("red"), p.get("id")): p for p in ofi.get("paid", [])}
    paid_cand = []
    for p in pubs:
        if p["horas"] is None or p["horas"] > 24 * 5 or p["horas"] < 6 or p["red"] == "youtube":
            continue
        if p["rel"] >= 3 and p["vistas"] >= 500 and (inter_med.get(p["red"]) is None or p["inter"] >= 0.8 * inter_med[p["red"]]):
            pres = 20 if p["rel"] >= 10 else 10 if p["rel"] >= 5 else 5
            d = decid.get((p["red"], p["id"]))
            paid_cand.append({"red": p["red"], "id": p["id"], "video": p["video"], "titulo": p["titulo"], "url": p["url"],
                              "vistas": p["vistas"], "rel": r2(p["rel"]), "inter": r2(p["inter"], 4), "horas": round(p["horas"]),
                              "presupuesto": pres, "objetivo": "seguidores" if p["red"] == "tiktok" else "visitas al perfil",
                              "decidido": (d or {}).get("estado")})
    paid_cand.sort(key=lambda c: -c["rel"])
    # resultados de lo que ya se promocionó
    paid_res = []
    for d in ofi.get("paid", []):
        if d.get("estado") != "lanzado":
            continue
        p = next((x for x in pubs if x["red"] == d.get("red") and x["id"] == d.get("id")), None)
        if p:
            antes = d.get("vistas_al_lanzar") or 0
            paid_res.append({"red": d["red"], "id": d["id"], "titulo": p["titulo"], "gasto": d.get("gasto"), "vistas_al_lanzar": antes,
                             "vistas": p["vistas"], "ganadas": p["vistas"] - antes,
                             "coste_mil": r2(d["gasto"] / ((p["vistas"] - antes) / 1000)) if d.get("gasto") and p["vistas"] > antes else None})

    # Estratega: vídeos que piden segunda parte (más de 10 veces lo normal en alguna red)
    ya = " ".join(norm(v.get("titulo")) for v in est)
    segundas = []
    for p in pubs:
        if p["rel"] >= 10 and p["video"]:
            base = next((v for v in est if v["id"] == p["video"]), {})
            if f"{p['video']}2" in {v["id"] for v in est} or "parte 2" in norm(base.get("titulo")):
                continue
            segundas.append({"video": p["video"], "red": p["red"], "titulo": p["titulo"], "rel": r2(p["rel"]), "vistas": p["vistas"]})
    vistos, segundas_u = set(), []
    for s in sorted(segundas, key=lambda s: -s["rel"]):
        if s["video"] not in vistos:
            vistos.add(s["video"])
            segundas_u.append(s)

    hall = hallazgos(maduros, aud.get("metricas") or {}, {k: (b["nombre"], b["rol"]) for k, b in (aud.get("banderas") or {}).items()})
    recs = recomendaciones(vids, hall, aud.get("metricas") or {})
    exps = evaluar_experimentos(ofi.get("experimentos"), por_id)
    # foco de cada puesto: su hallazgo más fuerte
    foco = {}
    for h in hall:
        foco.setdefault(h["rol"], h)
    # referencia técnica: mediana de cada medida en el mejor cuarto de vídeos frente al resto
    ref = {}
    if len(maduros) >= 8:
        corte = sorted(v["rel"] for v in maduros)[int(len(maduros) * 0.75)]
        top = [v for v in maduros if v["rel"] >= corte]
        resto = [v for v in maduros if v["rel"] < corte]
        for k in (aud.get("metricas") or {}):
            a = mediana([v[k] for v in top if isinstance(v.get(k), (int, float))])
            b = mediana([v[k] for v in resto if isinstance(v.get(k), (int, float))])
            if a is not None and b is not None:
                ref[k] = {"top": r2(a), "resto": r2(b)}

    comp = {v["id"]: compuertas(v) for v in est if v.get("estado") in ("propuesto", "aprobado", "voz", "escena", "rehacer")}

    pst = puestos(est, vids, pubs, medianas, inter_med, ofi, ideas, tend, com, coman, paid_cand, segundas_u)
    for rol, h in foco.items():
        if rol in pst:
            pst[rol]["foco"] = h["texto"]
    datos = {
        "medianas": {r: r2(medianas[r], 0) for r in REDES},
        "maduros": len(maduros),
        "puestos": pst,
        "manual": manual,
        "senales": senales,
        "reputacion": rep,
        "predicciones": pred_res,
        "paid_candidatos": paid_cand[:10],
        "paid_resultados": paid_res,
        "segundas_partes": segundas_u[:6],
        "compuertas": comp,
        "mejora": {"hallazgos": hall[:14], "recomendaciones": recs, "experimentos": exps, "foco": foco,
                   "referencia": ref, "metricas": aud.get("metricas") or {}, "medidos": len(aud.get("videos") or {})},
        "videos": sorted([v for v in vids if v["vistas"]], key=lambda v: v.get("publicado") or "", reverse=True)[:60],
    }
    ruta = P("produccion/oficina_datos.json")
    viejo = leer("produccion/oficina_datos.json", {})
    sello = lambda d: json.dumps({k: v for k, v in d.items() if k != "actualizado"}, sort_keys=True, ensure_ascii=False)
    if viejo and sello(viejo) == sello(datos):
        print("oficina_datos.json sin cambios")
        return
    datos = {"actualizado": AHORA.isoformat(timespec="seconds"), **datos}
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"oficina_datos.json: {len(maduros)} vídeos maduros, {len(senales)} señales, {len(paid_cand)} candidatos a promoción, "
          f"{len(segundas_u)} segundas partes, {len(pred_res)} predicciones puntuadas")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "comprobar":
        sys.exit(cmd_comprobar(sys.argv[2:]))
    calcular()
