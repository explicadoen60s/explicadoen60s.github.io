#!/usr/bin/env python3
# Montaje: fotogramas 3D + subtítulo de UNA palabra + etiquetas/marcadores puntuales + voz + efectos.
# Uso: python3 comp.py <nombre> [t0 t1]  (con t0 t1 hace una prueba parcial)
import subprocess, os, sys, json, math, re, glob, importlib, wave
import numpy as np, cairo

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
ESTILO_ACTUAL = "palabra"
YL = (1.0, 0.82, 0.16); RED = (0.93, 0.2, 0.22); GREEN = (0.25, 0.85, 0.45)

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def back(x):
    x = max(0.0, min(1.0, x)); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def text_path(ctx, s, size, italic=False):
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    e = ctx.text_extents(s); return e

def outlined(ctx, s, cx, cy, size, fill=(1, 1, 1), stroke=10, italic=False, scale=1.0, rot=0.0, alpha=1.0, shadow=True):
    if abs(scale) < 1e-3 or alpha <= 0: return   # escala 0 = matriz no invertible en cairo
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot); ctx.scale(scale, scale)
    e = text_path(ctx, s, size, italic)
    x = -e.x_advance / 2; y = size * 0.35
    if shadow:
        ctx.move_to(x + 4, y + 6); ctx.text_path(s); ctx.set_source_rgba(0, 0, 0, 0.35 * alpha); ctx.set_line_width(stroke); ctx.stroke_preserve(); ctx.fill()
    ctx.move_to(x, y); ctx.text_path(s)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_source_rgba(0, 0, 0, alpha); ctx.set_line_width(stroke); ctx.stroke_preserve()
    ctx.set_source_rgba(*fill, alpha); ctx.fill()
    ctx.restore()

def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); ctx.close_path()

def badge(ctx, s, cx, cy, p, col=(1, 1, 1), size=70, sub=None):
    if p <= 0: return
    sc = back(p)
    if sc < 1e-3: return
    ctx.save(); ctx.translate(cx, cy); ctx.scale(sc, sc)
    # ✗ y ✓ no están en Poppins: se dibujan como trazos para no depender de fuentes de respaldo
    icon = None
    if s[:1] in "✗✓✕✔✘": icon = "ok" if s[0] in "✓✔" else "no"; s = s[1:].lstrip()
    iw = size * 0.78 if icon else 0
    e = text_path(ctx, s, size); w = e.x_advance + 56 + iw; h = size * 1.45
    rrect(ctx, -w / 2 + 4, -h / 2 + 7, w, h, 22); ctx.set_source_rgba(0, 0, 0, 0.25); ctx.fill()
    rrect(ctx, -w / 2, -h / 2, w, h, 22); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.92); ctx.fill_preserve()
    ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, 0.18); ctx.stroke()
    x0 = -(e.x_advance + iw) / 2
    if icon:
        r = size * 0.27; cx0 = x0 + r; ctx.set_source_rgb(*col); ctx.set_line_width(size * 0.13); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        if icon == "no":
            ctx.move_to(cx0 - r, -r); ctx.line_to(cx0 + r, r); ctx.move_to(cx0 + r, -r); ctx.line_to(cx0 - r, r)
        else:
            ctx.move_to(cx0 - r, 0.05 * r); ctx.line_to(cx0 - 0.25 * r, 0.8 * r); ctx.line_to(cx0 + r, -0.85 * r)
        ctx.stroke()
    ctx.move_to(x0 + iw, size * 0.36); ctx.text_path(s); ctx.set_source_rgb(*col); ctx.fill()
    ctx.restore()

def callout(ctx, s, cx, cy, p, size=64):
    if p <= 0: return
    lines = s.split("\n")
    for k, l in enumerate(lines):
        outlined(ctx, l, cx, cy + (k - (len(lines) - 1) / 2) * size * 0.95, size, fill=YL, stroke=12, italic=True,
                 scale=back(p), rot=-0.07)

def arrow_dim(ctx, x0, x1, y, col, p, lw=9):
    if p <= 0: return
    xm = (x0 + x1) / 2; hw = (x1 - x0) / 2 * ease(p)
    a, b = xm - hw, xm + hw
    for st, c in ((lw + 8, (0, 0, 0)), (lw, col)):
        ctx.set_line_width(st); ctx.set_source_rgb(*c); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(a, y); ctx.line_to(b, y); ctx.stroke()
        for xx, d in ((a, 1), (b, -1)):
            ctx.move_to(xx + d * 26, y - 20); ctx.line_to(xx, y); ctx.line_to(xx + d * 26, y + 20); ctx.stroke()
        for xx in (a, b):
            ctx.move_to(xx, y - 34); ctx.line_to(xx, y + 34); ctx.stroke()

def clean(w):
    w = re.sub(r"^[¿¡\"“(]+|[.,:;?!…\"”)]+$", "", w)
    return w[:1].upper() + w[1:] if w else w

# ---------------- audio: efectos sintéticos ----------------
SR = 44100
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def s_whoosh(dur=0.55):
    n = int(dur * SR); x = np.random.randn(n); t = np.arange(n) / n
    # ruido filtrado por un paso-bajo variable (sube y baja)
    out = np.zeros(n); y = 0
    for i in range(n):
        a = 0.02 + 0.25 * math.sin(math.pi * t[i]) ** 2; y += a * (x[i] - y); out[i] = y
    return out * np.sin(np.pi * t) ** 1.5 * 2.2
def s_pop():
    n = int(0.12 * SR); t = np.arange(n) / SR; f = 900 * np.exp(-t * 25) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.03) * 0.8
def s_coin():
    n = int(0.45 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2637 * t) * 0.6 + np.sin(2 * np.pi * 3951 * t) * 0.4) * env(n, 0.001, 0.09) * 0.5
def s_thud():
    n = int(0.3 * SR); t = np.arange(n) / SR; f = 140 * np.exp(-t * 12) + 50
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.08) * 1.0
def s_clank():
    n = int(0.6 * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((310, 0.5), (787, 0.35), (1290, 0.25), (2210, 0.15)))
    return x * env(n, 0.001, 0.12) * 0.8 + np.random.randn(n) * env(n, 0.001, 0.02) * 0.4
def s_win():
    out = np.zeros(int(0.9 * SR))
    for k, f in enumerate((784, 988, 1175, 1568)):
        n = int(0.35 * SR); t = np.arange(n) / SR; a = int(k * 0.1 * SR)
        tone = (np.sign(np.sin(2 * np.pi * f * t)) * 0.25 + np.sin(2 * np.pi * f * t) * 0.5) * env(n, 0.002, 0.12)
        out[a:a + n] += tone[:len(out) - a]
    return out * 0.45
def s_fail():
    n = int(0.5 * SR); t = np.arange(n) / SR; f = 420 - 250 * t / 0.5
    return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * env(n, 0.005, 0.25) * 0.18
def s_bleep(f):
    n = int(0.09 * SR); t = np.arange(n) / SR; return np.sign(np.sin(2 * np.pi * f * t)) * env(n, 0.002, 0.04) * 0.12
def s_buzz(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 120 * t) * 0.5 + np.sign(np.sin(2 * np.pi * 240 * t)) * 0.15
    return x * np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.1) * 0.12

def build_sfx(dur, events, path):
    out = np.zeros(int((dur + 2) * SR))
    for t, snd, g in events:
        a = int(t * SR); x = snd * g; b = min(len(out), a + len(x)); out[a:b] += x[:b - a]
    out = np.clip(out, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767 * 0.8).astype(np.int16).tobytes())

# ---------------- juego de la cifra ----------------
# «¿Cuánto crees?»: al principio sale una tarjeta con «?» (el espectador escribe su número en comentarios);
# se encoge a una esquina mientras dura la explicación y, en el dato sorprendente, la cifra real sube y se descubre.
def miles(v, dec=0):
    if dec: return f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{int(round(v)):,}".replace(",", ".")

def s_tick():
    n = int(0.03 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * 2400 * t) * env(n, 0.001, 0.008) * 0.35

def _tarjeta_cifra(ctx, cx, cy, sc, cab, num, unidad, num_col, pie=None, alpha=1.0):
    if sc < 1e-3 or alpha <= 0: return
    ctx.save(); ctx.translate(cx, cy); ctx.scale(sc, sc)
    ys = {"cab": 66, "num": 222}; y = 222
    if unidad: y += 62; ys["uni"] = y
    if pie: y += 58; ys["pie"] = y
    h = y + 40
    anchos = [text_path(ctx, num, 150).x_advance, text_path(ctx, cab, 44).x_advance]
    if unidad: anchos.append(text_path(ctx, unidad, 50).x_advance)
    if pie: anchos.append(text_path(ctx, pie, 36).x_advance)
    w = max(500, max(anchos) + 110); top = -h / 2
    rrect(ctx, -w / 2 + 6, top + 10, w, h, 34); ctx.set_source_rgba(0, 0, 0, 0.3 * alpha); ctx.fill()
    rrect(ctx, -w / 2, top, w, h, 34); ctx.set_source_rgba(0.09, 0.11, 0.16, 0.94 * alpha); ctx.fill_preserve()
    ctx.set_line_width(5); ctx.set_source_rgba(*YL, 0.85 * alpha); ctx.stroke()
    for clave, txt, size, col in (("cab", cab, 44, (1, 1, 1, 0.8)), ("num", num, 150, (*num_col, 1)), ("uni", unidad, 50, (1, 1, 1, 0.75)), ("pie", pie, 36, (*YL, 1))):
        if clave not in ys: continue
        e = text_path(ctx, txt, size); ctx.move_to(-e.x_advance / 2, top + ys[clave]); ctx.text_path(txt)
        ctx.set_source_rgba(*col[:3], col[3] * alpha); ctx.fill()
    ctx.restore()

def cifra_juego(ctx, t, valor, unidad, t_preg, t_rev, t_fin, dec=0, cab="¿CUÁNTO CREES?", grande=(W / 2, H * 0.33),
                mini=(W * 0.21, H * 0.205), t_mini=None, dur_rev=1.1):
    """t_preg: cuando la voz hace la pregunta; t_rev: cuando dice la cifra; t_fin: cuando desaparece.
    t_mini (por defecto t_preg+2,6 s): cuando la tarjeta se encoge a la esquina para dejar ver la escena."""
    if t < t_preg or t > t_fin: return
    t_mini = t_preg + 2.6 if t_mini is None else t_mini
    a = min(1.0, (t_fin - t) / 0.3)
    if t < t_rev - 0.5:
        p = back((t - t_preg) / 0.35); m = ease((t - t_mini) / 0.45) if t > t_mini else 0.0
        cx = grande[0] + (mini[0] - grande[0]) * m; cy = grande[1] + (mini[1] - grande[1]) * m
        q = "?"
        rot = 0.05 * math.sin(t * 5.5)   # se balancea: algo se mueve siempre
        ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot * (1 - m)); ctx.translate(-cx, -cy)
        _tarjeta_cifra(ctx, cx, cy, p * (1 - 0.45 * m), cab if m < 0.5 else "TU NÚMERO", q, unidad, YL,
                       pie="ESCRÍBELO EN COMENTARIOS" if m < 0.5 else None, alpha=a)
        ctx.restore(); return
    # vuelve al centro y la cifra sube
    g = ease((t - (t_rev - 0.5)) / 0.45)
    cx = mini[0] + (grande[0] - mini[0]) * g; cy = mini[1] + (grande[1] - mini[1]) * g
    k = ease((t - t_rev) / dur_rev) if t > t_rev else 0.0
    v = valor * k; listo = t >= t_rev + dur_rev
    pop = 1 + 0.12 * math.sin(min(1, (t - t_rev - dur_rev) / 0.3) * math.pi) if listo and t < t_rev + dur_rev + 0.3 else 1
    _tarjeta_cifra(ctx, cx, cy, (0.55 + 0.45 * g) * pop, "¿TE HAS ACERCADO?" if listo else cab, miles(v, dec) if t >= t_rev else "?", unidad,
                   GREEN if listo else ((1, 1, 1) if t >= t_rev else YL), alpha=a)

def sfx_cifra(t_preg, t_rev, dur_rev=1.1):
    E = [(t_preg, s_pop(), 0.5)]
    n = 14
    for i in range(n): E.append((t_rev + dur_rev * (1 - (1 - i / n) ** 0.5), s_tick(), 0.5))
    E.append((t_rev + dur_rev, s_win(), 0.45))
    return E

# ---------------- comentario en pantalla (vídeos que pidió un seguidor) ----------------
def comentario(ctx, t, autor, texto, a, b, cx=W / 2, cy=H * 0.33):
    p = win_simple(t, a, b)
    if p <= 0: return
    ctx.save(); sc = back(min(1, (t - a) / 0.35)); ctx.translate(cx, cy); ctx.scale(sc, sc)
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(46)
    palabras, lineas, l = texto.split(), [], ""
    for w in palabras:
        if l and ctx.text_extents(l + " " + w).x_advance > 640: lineas.append(l); l = w
        else: l = (l + " " + w).strip()
    if l: lineas.append(l)
    lineas = lineas[:3]
    w = max([ctx.text_extents(x).x_advance for x in lineas] + [380]) + 190; h = 110 + 58 * len(lineas)
    rrect(ctx, -w / 2 + 5, -h / 2 + 9, w, h, 30); ctx.set_source_rgba(0, 0, 0, 0.3 * p); ctx.fill()
    rrect(ctx, -w / 2, -h / 2, w, h, 30); ctx.set_source_rgba(1, 1, 1, 0.97 * p); ctx.fill()
    ax, ay = -w / 2 + 70, -h / 2 + 70
    ctx.arc(ax, ay, 38, 0, math.tau); ctx.set_source_rgba(0.2, 0.55, 1.0, p); ctx.fill()
    ini = (autor.lstrip("@")[:1] or "?").upper(); e = text_path(ctx, ini, 40)
    ctx.move_to(ax - e.x_advance / 2, ay + 14); ctx.text_path(ini); ctx.set_source_rgba(1, 1, 1, p); ctx.fill()
    cab = "Respuesta a @" + autor.lstrip("@"); text_path(ctx, cab, 32)
    ctx.move_to(ax + 60, -h / 2 + 62); ctx.text_path(cab); ctx.set_source_rgba(0.45, 0.47, 0.52, p); ctx.fill()
    for i, x in enumerate(lineas):
        text_path(ctx, x, 46); ctx.move_to(ax + 60, -h / 2 + 122 + i * 58); ctx.text_path(x); ctx.set_source_rgba(0.08, 0.09, 0.12, p); ctx.fill()
    ctx.restore()

def win_simple(t, a, b, fi=0.2, fo=0.25):
    if t < a or t > b: return 0.0
    return min(1.0, (t - a) / fi, (b - t) / fo)

# ---------------- estilo «maqueta de día» (referencia @conrazon_es) ----------------
AMARILLO_ROT = (1.0, 0.80, 0.12)

def rotulo(ctx, t, texto, a, b, cx=W / 2, cy=H * 0.60, size=92, rot=-0.07):
    """Nombre de la pieza en grande: amarillo, cursiva, mayúsculas, con contorno. Sale cuando la voz lo dice."""
    if t < a or t > b: return
    p = back(min(1, (t - a) / 0.3)); al = min(1.0, (b - t) / 0.2)
    lineas = _partir(texto.upper(), 2)
    for i, l in enumerate(lineas):
        outlined(ctx, l, cx, cy + (i - (len(lineas) - 1) / 2) * size * 0.92, size, fill=AMARILLO_ROT, stroke=14, italic=True,
                 scale=p, rot=rot, alpha=al)

def _partir(txt, maxl):
    w = txt.split()
    if len(w) < 2 or len(txt) < 13 or maxl < 2: return [txt]
    mejor = min(range(1, len(w)), key=lambda i: abs(len(" ".join(w[:i])) - len(" ".join(w[i:]))))
    return [" ".join(w[:mejor]), " ".join(w[mejor:])]

def pastilla(ctx, t, valor, unidad, a, b, cx, cy, desde=None, dec=0, dur=0.7, size=70):
    """Contador pequeño en una pastilla oscura («9 litros», «120 °C»). Con `desde`, el número cuenta hasta `valor`."""
    if t < a or t > b: return
    al = min(1.0, (t - a) / 0.15, (b - t) / 0.2); sc = back(min(1, (t - a) / 0.3))
    if sc < 1e-3 or al <= 0: return   # escala 0 = matriz no invertible en cairo
    v = valor if desde is None else desde + (valor - desde) * ease(min(1, (t - a) / dur))
    num = miles(v, dec)
    ctx.save(); ctx.translate(cx, cy); ctx.scale(sc, sc)
    e1 = text_path(ctx, num, size); e2 = text_path(ctx, unidad, size * 0.42) if unidad else None
    w = e1.x_advance + (e2.x_advance + 14 if e2 else 0) + 56; h = size * 1.25
    rrect(ctx, -w / 2 + 3, -h / 2 + 6, w, h, h * 0.32); ctx.set_source_rgba(0, 0, 0, 0.25 * al); ctx.fill()
    rrect(ctx, -w / 2, -h / 2, w, h, h * 0.32); ctx.set_source_rgba(0.17, 0.18, 0.21, 0.92 * al); ctx.fill()
    x = -w / 2 + 28; text_path(ctx, num, size); ctx.move_to(x, size * 0.36); ctx.text_path(num); ctx.set_source_rgba(1, 1, 1, al); ctx.fill()
    if e2:
        text_path(ctx, unidad, size * 0.42); ctx.move_to(x + e1.x_advance + 12, size * 0.36); ctx.text_path(unidad); ctx.set_source_rgba(0.82, 0.85, 0.9, al); ctx.fill()
    ctx.restore()

def chispa(ctx, t, cx, cy, a, r=60, n=7, col=(1, 1, 1)):
    """Rayitas de «clic» o golpe (cierre que encaja, botón que se pulsa)."""
    u = (t - a) / 0.35
    if u < 0 or u > 1: return
    ctx.save(); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(n):
        ang = -math.pi / 2 + (i - (n - 1) / 2) * 0.32
        r0, r1 = r * (0.6 + 0.6 * u), r * (1.0 + 0.7 * u)
        ctx.move_to(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0); ctx.line_to(cx + math.cos(ang) * r1, cy + math.sin(ang) * r1)
        ctx.set_line_width(7); ctx.set_source_rgba(0, 0, 0, 0.35 * (1 - u)); ctx.stroke_preserve()
        ctx.set_line_width(4); ctx.set_source_rgba(*col, 1 - u); ctx.stroke()
    ctx.restore()

def subtitulo_centro(ctx, t, ws, kws, y):
    """Una palabra en el centro de la pantalla, encima del mecanismo: blanca, o amarilla si es palabra clave."""
    for i, (ta, tb, w) in enumerate(ws):
        nxt = ws[i + 1][0] if i + 1 < len(ws) else tb + 0.5
        end = nxt if nxt - tb < 0.35 else tb + 0.25
        if ta - 0.03 <= t < end:
            s = clean(w); kw = s.lower() in kws
            outlined(ctx, s[:1].upper() + s[1:], W / 2, y, 66, fill=(AMARILLO_ROT if kw else (1, 1, 1)), stroke=10,
                     scale=0.85 + 0.15 * min(1, (t - ta + 0.03) / 0.08))
            return

# ---------------- subtítulo en frases (estilo «karaoke») ----------------
# La frase se escribe palabra a palabra arriba; la palabra que suena va en blanco y las anteriores en gris.
# Las palabras clave llevan un recuadro azul. Fondo oscuro suave para que se lea sobre cualquier escena.
def frases(ws):
    # corta por signos de puntuación o pausas; las frases largas se parten por la mitad (nunca quedan palabras sueltas)
    bloques, cur = [], []
    for i, (ta, tb, w) in enumerate(ws):
        if cur and ta - cur[-1][1] > 0.6: bloques.append(cur); cur = []
        cur.append((ta, tb, w))
        if re.search(r"[.,;:?!…]$", w): bloques.append(cur); cur = []
    if cur: bloques.append(cur)
    out = []
    for b in bloques:
        while len(b) > 8:
            n = max(3, (len(b) + 1) // 2 if len(b) <= 16 else 8); out.append(b[:n]); b = b[n:]
        out.append(b)
    return out

def subtitulo_frase(ctx, t, FR, kws, y0):
    for k, fr in enumerate(FR):
        ini = fr[0][0] - 0.05
        fin = FR[k + 1][0][0] - 0.05 if k + 1 < len(FR) else fr[-1][1] + 0.6
        if not (ini <= t < fin): continue
        size = 70; ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(size)
        esp = ctx.text_extents(" ").x_advance * 1.1
        toks = [(ta, tb, re.sub(r"^[\"“(]+|[\"”)]+$", "", w)) for ta, tb, w in fr]
        lineas, linea, ancho = [], [], 0
        for tok in toks:
            wd = ctx.text_extents(tok[2]).x_advance
            if linea and ancho + esp + wd > 880: lineas.append((linea, ancho)); linea, ancho = [], 0
            ancho += (esp if linea else 0) + wd; linea.append((tok, wd))
        if linea: lineas.append((linea, ancho))
        lh = size * 1.22; alto = lh * len(lineas)
        vis = [tok for tok in toks if tok[0] - 0.03 <= t]
        if not vis: return
        a = min(1, (t - ini) / 0.12)
        anch = max(an for _, an in lineas)
        rrect(ctx, W / 2 - anch / 2 - 30, y0 - 18, anch + 60, alto + 30, 26); ctx.set_source_rgba(0.04, 0.06, 0.14, 0.58 * a); ctx.fill()
        for j, (linea, an) in enumerate(lineas):
            x = W / 2 - an / 2; y = y0 + j * lh + size * 0.88
            for (ta, tb, w), wd in linea:
                if ta - 0.03 > t: x += wd + esp; continue
                actual = ta - 0.03 <= t < max(tb, ta + 0.18)
                limpio = re.sub(r"[.,;:?!…¿¡]", "", w).lower()
                if limpio in kws:
                    rrect(ctx, x - 9, y - size * 0.86, wd + 18, size * 1.12, 8)
                    ctx.set_source_rgba(0.2, 0.55, 1.0, 0.95); ctx.set_line_width(3.5); ctx.stroke()
                    for cx, cy in ((x - 9, y - size * 0.86), (x + wd + 9, y + size * 0.26)):
                        ctx.arc(cx, cy, 5, 0, 7); ctx.set_source_rgb(1, 1, 1); ctx.fill()
                ctx.move_to(x, y); ctx.text_path(w)
                ctx.set_source_rgba(1, 1, 1, 1 if (actual or limpio in kws) else 0.62); ctx.fill()
                x += wd + esp
        return

# ---------------- montaje ----------------
def main(name, t0=None, t1=None):
    spec = importlib.import_module(f"{name}_ov")
    words = json.load(open(os.path.join(HERE, f"{name}_words.json")))
    dur = words["dur"]; ws = words["words"]
    frames_dir = os.path.join(HERE, "frames", name)
    anc = {}
    for f in glob.glob(os.path.join(HERE, "frames", f"anchors_{name}_*_1.json")):
        anc.update({int(k): v for k, v in json.load(open(f)).items()})
    n_total = int(math.ceil((dur + 0.4) * FPS))
    f0 = int(t0 * FPS) if t0 is not None else 0; f1 = int(t1 * FPS) if t1 is not None else n_total
    vout = os.path.join(HERE, f"{name}_video.mp4" if t0 is None else f"{name}_part.mp4")
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-start_number", str(f0), "-framerate", str(FPS), "-i", os.path.join(frames_dir, "%05d.png"),
                            "-frames:v", str(f1 - f0), "-vf", f"scale={W}:{H}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "bgra", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    last_anchor = None
    global ESTILO_ACTUAL
    estilo = getattr(spec, "SUB_ESTILO", "palabra"); FR = frases(ws); ESTILO_ACTUAL = estilo
    kws = {k.lower() for k in spec.KEYWORDS}
    for f in range(f0, f1):
        raw = dec.stdout.read(W * H * 4)
        if len(raw) < W * H * 4: break
        t = f / FPS
        buf = bytearray(raw)
        surf = cairo.ImageSurface.create_for_data(buf, cairo.FORMAT_ARGB32, W, H, W * 4); ctx = cairo.Context(surf)
        a = anc.get(f, last_anchor); last_anchor = a
        A = (lambda k: (a[k][0] * W, a[k][1] * H)) if a else (lambda k: (W / 2, H / 2))
        spec.overlay(ctx, t, A, sys.modules[__name__])
        if estilo == "centro":
            subtitulo_centro(ctx, t, ws, kws, H * getattr(spec, "SUB_Y", 0.50))
            surf.flush(); enc.stdin.write(bytes(buf)); continue
        if estilo == "frase":
            subtitulo_frase(ctx, t, FR, kws, H * getattr(spec, "SUB_Y_FRASE", 0.12))
            surf.flush(); enc.stdin.write(bytes(buf)); continue
        # subtítulo: una sola palabra
        cur = None
        for i, (ta, tb, w) in enumerate(ws):
            nxt = ws[i + 1][0] if i + 1 < len(ws) else tb + 0.5
            end = nxt if nxt - tb < 0.35 else tb + 0.25
            if ta - 0.03 <= t < end: cur = (ta, w); break
        if cur:
            ta, w = cur; s = clean(w); kw = s.lower() in spec.KEYWORDS
            p = min(1, (t - ta + 0.03) / 0.09)
            outlined(ctx, s, W / 2, H * spec.SUB_Y, 84, fill=(YL if kw else (1, 1, 1)), stroke=13, scale=0.82 + 0.18 * p)
        surf.flush(); enc.stdin.write(bytes(buf))
    enc.stdin.close(); enc.wait(); dec.wait()
    if t0 is not None: print("ok", vout); return
    sfx = os.path.join(HERE, f"{name}_sfx.wav")
    build_sfx(dur, spec.sfx_events(sys.modules[__name__]), sfx)
    final = os.path.join(HERE, f"{name}_final.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vout, "-i", os.path.join(HERE, f"{name}_voz.wav"), "-i", sfx, "-filter_complex",
                    "[1:a]apad[v];[v][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[m]", "-map", "0:v", "-map", "[m]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], check=True)
    print("ok", final)

if __name__ == "__main__":
    sys.path.insert(0, HERE)
    if len(sys.argv) > 2: main(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))
    else: main(sys.argv[1])
