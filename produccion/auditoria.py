#!/usr/bin/env python3
"""Auditoría técnica de cada vídeo: voz (mp3) + escena 3D (_scene.py) + capa 2D y sonido (_ov.py).

Uso: python3 produccion/auditoria.py   -> actualiza produccion/auditoria.json

No renderiza nada: mide lo que se puede medir sin Blender, para que la oficina cruce esas
medidas con las vistas (oficina.py) y descubra qué potenciar y qué corregir en cada puesto.
Solo vuelve a medir los vídeos cuyos archivos han cambiado (huella sha1). Necesita ffmpeg.
"""
import hashlib, json, math, os, re, subprocess, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESC = os.path.join(RAIZ, "produccion", "escenas")
SALIDA = os.path.join(RAIZ, "produccion", "auditoria.json")
VERSION = 5  # súbela si cambian las medidas: obliga a medir todo otra vez

# Qué mide cada cosa, a qué puesto pertenece y en qué sentido se espera que ayude.
# «mejor»: "mas" | "menos" | None (que lo decidan los datos).
METRICAS = {
    "voz_ritmo":        {"nombre": "Ritmo de la voz", "unidad": "palabras/s", "rol": "sonido", "mejor": None},
    "voz_silencio":     {"nombre": "Silencio en la voz", "unidad": "%", "rol": "sonido", "mejor": None},
    "voz_pausas_min":   {"nombre": "Pausas por minuto", "unidad": "/min", "rol": "sonido", "mejor": None},
    "voz_pausa_max":    {"nombre": "Pausa más larga", "unidad": "s", "rol": "sonido", "mejor": "menos"},
    "voz_arranque":     {"nombre": "Tarda en empezar a hablar", "unidad": "s", "rol": "sonido", "mejor": "menos"},
    "voz_lufs":         {"nombre": "Volumen de la voz", "unidad": "LUFS", "rol": "sonido", "mejor": None},
    "voz_expresividad": {"nombre": "Expresividad (rango dinámico)", "unidad": "LU", "rol": "sonido", "mejor": "mas"},
    "voz_gancho":       {"nombre": "Energía del gancho frente al resto", "unidad": "dB", "rol": "sonido", "mejor": "mas"},
    "duracion":         {"nombre": "Duración", "unidad": "s", "rol": "editor", "mejor": None},
    "cam_claves":       {"nombre": "Claves de cámara", "unidad": "", "rol": "fotografia", "mejor": "mas"},
    "cam_cada":         {"nombre": "Un movimiento de cámara cada", "unidad": "s", "rol": "fotografia", "mejor": "menos"},
    "cam_inicio_dist":  {"nombre": "Distancia de cámara en el primer segundo", "unidad": "m", "rol": "fotografia", "mejor": "menos"},
    "cam_lente_max":    {"nombre": "Lente más larga (primeros planos)", "unidad": "mm", "rol": "fotografia", "mejor": None},
    "obj_piezas":       {"nombre": "Piezas 3D", "unidad": "", "rol": "fotografia", "mejor": None},
    "obj_animaciones":  {"nombre": "Animaciones en la escena", "unidad": "", "rol": "motion", "mejor": "mas"},
    "obj_cortes":       {"nombre": "Cortes que enseñan el interior", "unidad": "", "rol": "fotografia", "mejor": None},
    "ov_etiquetas":     {"nombre": "Etiquetas sobre las piezas", "unidad": "", "rol": "motion", "mejor": None},
    "ov_contadores":    {"nombre": "Contadores y medidores", "unidad": "", "rol": "motion", "mejor": "mas"},
    "ov_graficos_min":  {"nombre": "Gráficos por minuto", "unidad": "/min", "rol": "motion", "mejor": None},
    "ov_palabras_clave":{"nombre": "Palabras clave resaltadas", "unidad": "", "rol": "editor", "mejor": None},
    "sfx_min":          {"nombre": "Efectos de sonido por minuto", "unidad": "/min", "rol": "sonido", "mejor": None},
    "sfx_variedad":     {"nombre": "Tipos de efecto distintos", "unidad": "", "rol": "sonido", "mejor": "mas"},
}
BANDERAS = {
    "juego_en_escena": ("Juego de la cifra en pantalla", "motion"),
    "comentario_en_escena": ("Comentario de un seguidor en pantalla", "social"),
    "sub_frase": ("Subtítulos en frase", "editor"),
}


def huella(*rutas):
    h = hashlib.sha1(str(VERSION).encode())
    for r in rutas:
        if os.path.exists(r):
            with open(r, "rb") as f:
                h.update(f.read())
    return h.hexdigest()[:16]


def ff(args):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args, "-f", "null", "-"], capture_output=True, text=True)
    return p.stderr


def duracion(mp3):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp3], capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return None


def media_db(mp3, extra=()):
    m = re.search(r"mean_volume: (-?[\d.]+) dB", ff([*extra, "-i", mp3, "-af", "volumedetect"]))
    return float(m.group(1)) if m else None


def medir_voz(mp3, palabras):
    d = duracion(mp3)
    if not d:
        return {}
    s = ff(["-i", mp3, "-af", "silencedetect=noise=-35dB:d=0.25"])
    ini = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", s)]
    fin = [(float(a), float(b)) for a, b in re.findall(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", s)]
    sil = sum(b for _, b in fin)
    arranque = next((e for (e, b), st in zip(fin, ini) if st <= 0.05), 0.0)
    internas = [b for (e, b), st in zip(fin, ini) if st > 0.05 and e < d - 0.05]
    e = ff(["-i", mp3, "-af", "ebur128"]).split("Summary:")[-1]
    lufs = re.search(r"I:\s+(-?[\d.]+) LUFS", e)
    lra = re.search(r"LRA:\s+([\d.]+) LU", e)
    g, todo = media_db(mp3, ("-t", "3")), media_db(mp3)
    return {
        "duracion": round(d, 1),
        "voz_ritmo": round(palabras / max(d - sil, 1), 2) if palabras else None,
        "voz_silencio": round(sil / d * 100, 1),
        "voz_pausas_min": round(len(internas) / d * 60, 1),
        "voz_pausa_max": round(max(internas), 2) if internas else 0.0,
        "voz_arranque": round(arranque, 2),
        "voz_lufs": float(lufs.group(1)) if lufs else None,
        "voz_expresividad": float(lra.group(1)) if lra else None,
        "voz_gancho": round(g - todo, 1) if g is not None and todo is not None else None,
    }


def bloque(src, nombre):
    """Cuerpo de una función def nombre(...) hasta la siguiente def de primer nivel."""
    m = re.search(rf"^def {nombre}\b.*?(?=^def |^if __name__|\Z)", src, re.S | re.M)
    return m.group(0) if m else ""


def medir_escena(src, dur):
    cam = bloque(src, "CAM")
    if not cam:  # CAM = [ ... ] a nivel de módulo
        m = re.search(r"^CAM\s*=\s*\[", src, re.M)
        if m:
            i, n = m.end(), 1
            while i < len(src) and n:
                n += {"[": 1, "]": -1}.get(src[i], 0)
                i += 1
            cam = src[m.start():i]
    if not cam:  # otras escenas: CAMS(), cams(k), camera(t)
        cam = "\n".join(bloque(src, n) for n in ("CAMS", "cams", "camera", "cam_keys"))
    # estilos: add(t, V_(...)) · (t,) + orb(...) · (t, (pos), (objetivo), lente)
    claves = len(re.findall(r"^\s*add\(", cam, re.M)) or len(re.findall(
        r"\(\s*(?:[\d.]+|T\([^)]*\)(?:\s*[+-]\s*[\d.]+)?|DUR(?:\s*[+-]\s*[\d.]+)?)\s*,\s*(?:\)|\()", cam))
    dist = None
    try:
        if m := re.search(r"add\(\s*0(?:\.0)?\s*,\s*V_\(\s*\(.*?\)\s*,\s*\(([-\d.\s,]+)\)", cam):
            dist = math.sqrt(sum(float(x) ** 2 for x in m.group(1).split(",") if x.strip()))
        elif m := re.search(r"\(0(?:\.0)?,\)\s*\+\s*orb\(\s*(?:\([^)]*\)|\w+)\s*,\s*([\d.]+)", cam):
            dist = float(m.group(1))
        elif m := re.search(r"\(0(?:\.0)?\s*,\s*\(([-\d.\s,]+)\)\s*,\s*\(([-\d.\s,]+)\)", cam):
            p, q = ([float(x) for x in g.split(",") if x.strip()] for g in m.groups())
            dist = math.dist(p, q)
    except ValueError:
        dist = None
    dist = round(dist, 1) if dist is not None else None
    claves = claves or None  # 0 = no se ha sabido leer: mejor sin dato que un dato falso
    lentes = [int(x) for x in re.findall(r",\s*(\d{2,3})\)", cam) if 14 <= int(x) <= 200] or [35]
    build, pose = bloque(src, "build"), bloque(src, "pose")
    return {
        "cam_claves": claves,
        "cam_cada": round(dur / claves, 2) if claves and dur and claves >= 3 else None,
        "cam_inicio_dist": dist,
        "cam_lente_max": max(lentes),
        "obj_piezas": len(re.findall(r"\b(box|cyl|sph|torus|rounded_slab|text3d|bar_obj|bx)\(", build or src)),
        "obj_animaciones": len(re.findall(r"\b(keyed|seg|mix)\(", pose or src)),
        "obj_cortes": len(re.findall(r"BOOLEAN", src)),
    }


def medir_ov(src, dur):
    ov = bloque(src, "overlay")
    sfx = bloque(src, "sfx_events")
    etiquetas = len(re.findall(r"\blabel\(", ov))
    badges = len(re.findall(r"\bbadge\(", ov))
    # contador = una cifra que cambia en pantalla: badge/label con texto calculado (f"…{v}…" o "…%d…")
    contadores = len(re.findall(r"\b(?:badge|label)\(\s*(?:C\s*,\s*)?ctx\s*,\s*(?:t\s*,[^,]*,[^,]*,\s*)?(?:f[\"'][^\"']*\{|[\"'][^\"']*%[\d.]*[dfs]|miles\(|str\(|fmt)", ov)) + len(re.findall(r"cifra_juego\(", ov))
    kw = re.search(r"KEYWORDS\s*=\s*\{(.*?)\}", src, re.S)
    tipos = re.findall(r"C\.s_([a-z_]+)\(", sfx)
    return {
        "ov_etiquetas": etiquetas,
        "ov_contadores": contadores,
        "ov_graficos_min": round((etiquetas + badges + contadores) / dur * 60, 1) if dur else None,
        "ov_palabras_clave": len(re.findall(r'"[^"]+"', kw.group(1))) if kw else 0,
        "sfx_min": round(len(tipos) / dur * 60, 1) if dur and tipos else 0,
        "sfx_variedad": len(set(tipos)),
        "juego_en_escena": "cifra_juego(" in src,
        "comentario_en_escena": "C.comentario(" in src,
        "sub_frase": bool(re.search(r'SUB_ESTILO\s*=\s*"frase"', src)),
    }


def main():
    try:
        viejo = json.load(open(SALIDA, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        viejo = {}
    previos = viejo.get("videos", {})
    est = {v["id"]: v for v in json.load(open(os.path.join(RAIZ, "produccion", "estado.json"), encoding="utf-8"))["videos"]}
    ids = sorted({f.split(".")[0].replace("_scene", "").replace("_ov", "") for f in os.listdir(ESC)
                  if f.endswith((".mp3", "_scene.py", "_ov.py")) and not f.startswith("_")})
    hay_ff = subprocess.run(["which", "ffmpeg"], capture_output=True).returncode == 0
    out, medidos = {}, 0
    for i in ids:
        mp3, sc, ov, txt = (os.path.join(ESC, f"{i}{s}") for s in (".mp3", "_scene.py", "_ov.py", ".txt"))
        h = huella(mp3, sc, ov)
        if previos.get(i, {}).get("huella") == h:
            out[i] = previos[i]
            continue
        texto = open(txt, encoding="utf-8").read() if os.path.exists(txt) else (est.get(i, {}).get("guion") or "")
        m = {"huella": h}
        if os.path.exists(mp3) and hay_ff:
            m.update(medir_voz(mp3, len(texto.split())))
        dur = m.get("duracion") or est.get(i, {}).get("duracion")
        if os.path.exists(sc):
            m.update(medir_escena(open(sc, encoding="utf-8").read(), dur))
        if os.path.exists(ov):
            m.update(medir_ov(open(ov, encoding="utf-8").read(), dur))
        out[i] = {k: v for k, v in m.items() if v is not None}
        medidos += 1
    if not hay_ff:
        print("Aviso: sin ffmpeg no se mide la voz", file=sys.stderr)
    datos = {"version": VERSION, "metricas": METRICAS, "banderas": {k: {"nombre": n, "rol": r} for k, (n, r) in BANDERAS.items()}, "videos": out}
    if json.dumps(datos, sort_keys=True) == json.dumps({k: viejo.get(k) for k in datos}, sort_keys=True):
        print("auditoria.json sin cambios")
        return
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"auditoria.json: {len(out)} vídeos ({medidos} medidos de nuevo)")


if __name__ == "__main__":
    main()
