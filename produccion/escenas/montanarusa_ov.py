# Capa 2D de «¿Y si construyes una montaña rusa?»
# También define el recorrido (vía), el movimiento del tren, la forma del rizo y los medidores (los usa la escena 3D).
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("montanarusa")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"vagón", "montaña", "rusa", "energía", "motor", "cadena", "treinta", "metros", "rompe", "atrás", "dientes", "clac",
            "seguros", "gravedad", "noventa", "kilómetros", "volando", "ruedas", "encima", "lados", "debajo", "rizo", "redondo",
            "seis", "peso", "círculos", "lágrima", "abierta", "cerrada", "cuatro", "parar", "imanes", "aletas", "corrientes",
            "frenan", "tocarlo", "electricidad"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def sg(t, a, b): return ss((t - a) / max(b - a, 1e-4))
def mix(a, b, u): return a + (b - a) * u
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]

K = dict(sube=T("subes"), construir=T("construir"), vamos=T("vamos a levantarla"), primero=T("primero"), motor=T("el tren no"),
         cadena=T("así que lo subes"), treinta=T("treinta"), pero1=T("pero si la cadena"), rompe=T("se rompe"), atras=T("el tren caería"),
         dientes=T("así que pones unos dientes"), clac1=T("clac"), seguros=T("son los seguros"), arriba=T("arriba lo"),
         grav=T("la gravedad"), bajada=T("en la bajada"), noventa=T("noventa"), curvas=T("pero en las curvas"),
         volando=T("el vagón saldría"), ruedas=T("así que pones ruedas"), encima=T("encima"), lados=T("por los lados"),
         debajo=T("por debajo"), rizo=T("ahora el"), redondo=T("si lo haces"), aplasta=T("abajo la fuerza"), seis=T("hasta seis"),
         curioso=T("y aquí viene"), circulos=T("por eso los rizos"), lagrima=T("tienen forma"), abajo2=T("abajo la curva"),
         arriba2=T("arriba cerrada"), cuatro=T("así la fuerza"), parar=T("pero al final"), chirr=T("sin chirridos"),
         imanes=T("así que pones imanes"), aletas=T("aletas"), pasar=T("al pasar"), corrientes=T("aparecen corrientes"),
         sintocar=T("sin tocarlo"), elec=T("ni siquiera"), sig=T("sígueme"))
k = K

# ---------------- recorrido ----------------
CX = 66.0                 # centro del rizo
R0 = 10.0                 # radio del rizo redondo
BRAKE_LEN = 60.0
MAIN_CP = [(-56, 1.5), (-44, 1.5), (-33, 1.5), (-28.5, 2.4), (-25, 5.0), (-4, 24.0), (-0.5, 28.2), (4, 29.6), (8, 28.6), (10.5, 25.0),
           (20, 6.5), (23, 2.6), (27, 1.5), (31, 2.4), (36, 6.2), (41, 7.8), (46, 6.2), (51, 2.4), (55, 1.5), (60, 1.5), (CX, 1.5)]

def _cr(p0, p1, p2, p3, u):
    return tuple(0.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (-a + 3 * b - 3 * c + d) * u ** 3)
                 for a, b, c, d in zip(p0, p1, p2, p3))

def _main():
    P = MAIN_CP; out = []
    for i in range(len(P) - 1):
        p0 = P[max(0, i - 1)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(len(P) - 1, i + 2)]
        L = math.dist(p1, p2); n = max(2, int(L / 0.5))
        for j in range(n):
            x, z = _cr(p0, p1, p2, p3, j / n); out.append((x, 0.0, z))
    out.append((P[-1][0], 0.0, P[-1][1]))
    return out
MAIN = _main()

def loop_pts(m, N=96):
    a = mix(R0, 5.5, m); b = mix(0.0, 3.2, m); out = []
    for i in range(N + 1):
        f = 2 * math.pi * i / N
        kk = 1 - m * (1 - (0.75 + 0.25 * math.cos(f / 2) ** 2))
        c = 1 - math.cos(f)
        out.append((CX + R0 * math.sin(f) * kk, 4.0 * i / N, 1.5 + a * c + b * c * c))
    return out

BRAKE = [(CX + BRAKE_LEN * i / 30, 4.0, 1.5) for i in range(31)]

def _cum(pts):
    c = [0.0]
    for p, q in zip(pts, pts[1:]): c.append(c[-1] + math.dist(p, q))
    return c

def _idx_x(pts, x):
    return min(range(len(pts)), key=lambda i: abs(pts[i][0] - x))

_PC = {}
def path(m):
    m = round(m, 4)
    if m in _PC: return _PC[m]
    lp = loop_pts(m)
    pts = MAIN + lp[1:] + BRAKE[1:]
    cum = _cum(pts)
    nm = len(MAIN); nl = len(lp)
    L = [0.0, cum[_idx_x(MAIN, -33)], cum[_idx_x(MAIN, 4)], cum[_idx_x(MAIN, 27)], cum[_idx_x(MAIN, 41)], cum[nm - 1],
         cum[nm - 1 + (nl - 1) // 2], cum[nm - 1 + nl - 1], cum[-1]]
    r = (pts, cum, L)
    if len(_PC) > 400: _PC.clear()
    _PC[m] = r
    return r

def v2d(v, m):
    _, _, L = path(m)
    v = max(0.0, min(8.0, v)); i = min(7, int(v)); f = v - i
    return L[i] + (L[i + 1] - L[i]) * f

def point(d, m):
    pts, cum, _ = path(m)
    d = max(0.0, min(cum[-1], d))
    lo, hi = 0, len(cum) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if cum[mid] <= d: lo = mid
        else: hi = mid
    u = (d - cum[lo]) / max(cum[hi] - cum[lo], 1e-6)
    return tuple(mix(a, b, u) for a, b in zip(pts[lo], pts[hi]))

def frame(d, m):
    """punto, tangente, lateral y normal (hacia el lado del tren) de la vía"""
    p = point(d, m); a = point(d - 0.6, m); b = point(d + 0.6, m)
    t = [b[i] - a[i] for i in range(3)]; l = math.sqrt(sum(x * x for x in t)) or 1; t = [x / l for x in t]
    h = math.hypot(t[0], t[2]) or 1
    n = [-t[2] / h, 0.0, t[0] / h]
    lat = [n[1] * t[2] - n[2] * t[1], n[2] * t[0] - n[0] * t[2], n[0] * t[1] - n[1] * t[0]]
    l = math.sqrt(sum(x * x for x in lat)) or 1; lat = [x / l for x in lat]
    n = [t[1] * lat[2] - t[2] * lat[1], t[2] * lat[0] - t[0] * lat[2], t[0] * lat[1] - t[1] * lat[0]]
    return p, t, lat, n

# ---------------- tiempos ----------------
def morph(t):
    return keyed(t, [(0, 1.0), (k["rizo"] - 0.2, 1.0), (k["rizo"] - 0.1, 0.0), (k["circulos"], 0.0), (k["lagrima"] + 0.9, 1.0)])

def train_v(t):
    """posición de la cabeza del tren en «hitos» (0 estación … 2 cima … 5 entrada del rizo … 7 salida … 8 fin)"""
    return keyed(t, [(0, 2.18), (1.9, 3.0), (3.6, 3.95), (k["vamos"] - 0.1, 4.55), (k["vamos"] - 0.05, 0.66),
                     (k["cadena"], 0.66), (k["pero1"] - 0.1, 1.82), (k["rompe"] + 0.4, 1.84), (k["dientes"] - 0.25, 1.42),
                     (k["clac1"] - 0.2, 1.42), (k["arriba"] - 0.3, 1.75), (k["arriba"] + 0.8, 2.03), (k["grav"], 2.05),
                     (k["bajada"], 2.3), (k["noventa"] + 0.8, 3.0), (k["curvas"], 3.55), (k["volando"] + 0.2, 4.0),
                     (k["ruedas"], 4.08), (k["rizo"], 4.1), (k["redondo"], 4.85), (k["aplasta"], 4.96), (k["seis"] + 0.6, 5.06),
                     (k["curioso"] + 0.9, 7.0), (k["cuatro"] - 0.25, 7.0), (k["cuatro"] - 0.2, 4.86), (k["cuatro"], 4.92),
                     (k["cuatro"] + 1.1, 5.06), (k["parar"] - 0.2, 7.0), (k["chirr"], 7.2), (k["imanes"] - 0.3, 7.41),
                     (k["aletas"], 7.45), (k["pasar"], 7.47), (k["sintocar"] + 0.3, 7.9), (DUR + 2, 7.9)])
PAD_V = 7.25; MAG_V = 7.45; MAG_N = 14; MAG_STEP = 2.2

def reveal(t):
    return keyed(t, [(0, 5.0), (k["vamos"] - 0.1, 5.0), (k["vamos"] - 0.05, 0.0), (k["vamos"] + 0.05, 0.0), (k["primero"] + 0.2, 1.0),
                     (k["cadena"], 1.0), (k["treinta"] + 0.6, 2.0), (k["arriba"], 2.0), (k["grav"], 3.0), (k["noventa"], 3.0),
                     (k["curvas"] - 0.1, 5.0), (k["rizo"] - 0.05, 5.0), (k["redondo"] - 0.1, 7.0), (k["parar"] - 0.2, 7.0),
                     (k["parar"] + 0.7, 8.0), (k["sig"], 8.0), (k["sig"] + 0.01, 8.0)])

def speed(t):
    if t < 5: return keyed(t, [(0, 45), (1.9, 88), (3.6, 52), (4.8, 60)])
    if t < 40: return keyed(t, [(k["grav"], 3), (k["bajada"], 30), (k["noventa"] + 0.8, 88), (k["curvas"], 86)])
    return keyed(t, [(k["parar"], 62), (k["chirr"], 58), (k["imanes"] - 0.3, 50), (k["pasar"], 48), (k["sintocar"] + 0.3, 0)])

def gforce(t):
    return keyed(t, [(0, 1), (k["aplasta"] - 0.1, 1.2), (k["seis"] + 0.3, 6.0), (k["seis"] + 1.0, 6.0), (k["curioso"] + 0.3, 1.6),
                     (k["curioso"] + 0.9, 1.0), (k["cuatro"], 1.0), (k["cuatro"] + 1.0, 4.0), (k["cuatro"] + 1.9, 4.0),
                     (k["cuatro"] + 2.5, 1.0)])

def rollback_flag(t): return k["rompe"] + 0.3 <= t < k["dientes"] - 0.2
def chain_broken(t): return k["rompe"] + 0.2 <= t < k["dientes"]
def flyoff(t):
    if t >= k["ruedas"] or t < k["curvas"]: return 0.0
    return keyed(t, [(k["volando"] - 0.1, 0.0), (k["volando"] + 0.6, 1.7), (k["ruedas"], 1.9)])

def head_pos(t):
    m = morph(t); return frame(v2d(train_v(t), m), m)[0]

# ---------------- dibujo ----------------
def gauge(ctx, x, y, r, p, val, vmax, unit, col):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); s = 0.6 + 0.4 * ss(p); ctx.scale(s, s)
    a0, a1 = math.radians(150), math.radians(390)
    ctx.set_source_rgba(0.08, 0.09, 0.12, 0.9 * p); ctx.arc(0, 0, r * 1.1, 0, math.tau); ctx.fill()
    ctx.set_line_width(18); ctx.set_source_rgba(1, 1, 1, 0.15 * p); ctx.arc(0, 0, r * 0.86, a0, a1); ctx.stroke()
    u = max(0.0, min(1.0, val / vmax))
    if u > 0.002:
        ctx.set_source_rgba(*col, p); ctx.arc(0, 0, r * 0.86, a0, a0 + (a1 - a0) * u); ctx.stroke()
    for i in range(10):
        a = a0 + (a1 - a0) * i / 9
        ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, 0.7 * p)
        ctx.move_to(r * 0.66 * math.cos(a), r * 0.66 * math.sin(a)); ctx.line_to(r * 0.72 * math.cos(a), r * 0.72 * math.sin(a)); ctx.stroke()
    ctx.select_font_face("Poppins", 0, 1); ctx.set_font_size(r * 0.58)
    s_ = str(int(round(val))); e = ctx.text_extents(s_)
    ctx.move_to(-e.x_advance / 2, r * 0.16); ctx.set_source_rgba(1, 1, 1, p); ctx.text_path(s_); ctx.fill()
    ctx.set_font_size(r * 0.24); e = ctx.text_extents(unit)
    ctx.move_to(-e.x_advance / 2, r * 0.56); ctx.set_source_rgba(*col, p); ctx.text_path(unit); ctx.fill()
    ctx.restore()

def gbar(ctx, x, y0, y1, p, g, col):
    """medidor vertical «veces tu peso» 1…6"""
    if p <= 0: return
    ctx.save(); w = 70
    ctx.set_source_rgba(0.08, 0.09, 0.12, 0.88 * p); ctx.rectangle(x - w / 2 - 14, y1 - 30, w + 28, y0 - y1 + 60); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.15 * p); ctx.rectangle(x - w / 2, y1, w, y0 - y1); ctx.fill()
    u = max(0.0, min(1.0, (g - 0) / 6.5))
    ctx.set_source_rgba(*col, p); ctx.rectangle(x - w / 2, y0 - (y0 - y1) * u, w, (y0 - y1) * u); ctx.fill()
    ctx.select_font_face("Poppins", 0, 1); ctx.set_font_size(30)
    for i in range(1, 7):
        yy = y0 - (y0 - y1) * i / 6.5
        ctx.set_source_rgba(1, 1, 1, 0.8 * p); ctx.set_line_width(4); ctx.move_to(x + w / 2, yy); ctx.line_to(x + w / 2 + 16, yy); ctx.stroke()
        ctx.move_to(x + w / 2 + 22, yy + 11); ctx.text_path(str(i)); ctx.fill()
    ctx.restore()

def cross(ctx, x, y, r, p, col=(0.93, 0.2, 0.22)):
    if p <= 0: return
    ctx.save(); ctx.set_line_cap(1)
    for lw, c in ((26, (0, 0, 0)), (15, col)):
        ctx.set_line_width(lw); ctx.set_source_rgba(*c, p)
        ctx.arc(x, y, r, 0, math.tau); ctx.stroke()
        ctx.move_to(x - r * 0.7, y - r * 0.7); ctx.line_to(x + r * 0.7, y + r * 0.7); ctx.stroke()
    ctx.restore()

def bolt(ctx, x, y, s, p):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    pts = [(0.15, -1), (-0.55, 0.15), (-0.05, 0.15), (-0.2, 1), (0.55, -0.2), (0.05, -0.2)]
    ctx.move_to(*pts[0])
    for q in pts[1:]: ctx.line_to(*q)
    ctx.close_path(); ctx.set_source_rgba(1, 0.82, 0.16, p); ctx.fill_preserve()
    ctx.set_line_width(0.06); ctx.set_source_rgba(0, 0, 0, p); ctx.stroke(); ctx.restore()

def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN; B = (0.45, 0.8, 1.0)
    BY = H * 0.265
    # velocímetro
    sp = max(win(t, 0.0, k["vamos"] - 0.15), win(t, k["grav"], k["curvas"] - 0.1), win(t, k["parar"], k["elec"] + 0.3))
    if sp: gauge(ctx, 250, 1340, 140, sp, speed(t), 100, "KM/H", Y)
    # el tren no lleva motor
    if k["motor"] + 0.4 <= t < k["cadena"]:
        C.badge(ctx, "0 KW", W / 2, BY, win(t, k["motor"] + 0.4, k["cadena"]), R, size=88)
    # altímetro (altura de la cabeza del tren)
    ap = max(win(t, k["cadena"], k["dientes"] - 0.1), win(t, k["clac1"], k["grav"]))
    if ap and not (k["treinta"] - 0.1 < t < k["pero1"]):
        z = head_pos(t)[2] - 1.5
        C.badge(ctx, "ALTURA %d M" % max(0, round(z)), W / 2, BY, ap, B, size=76)
    label(C, ctx, t, k["cadena"] + 0.5, k["treinta"] - 0.1, "CADENA", A, "chain", dx=-60, dy=170, size=60)
    a = win(t, k["treinta"], k["pero1"])
    if a:
        x, y = A("dim"); C.callout(ctx, "30 M", clampx(x + 130, 300), clampy(y), a, size=84)
    p = win(t, k["rompe"] + 0.3, k["dientes"] - 0.1)
    if p: x, y = A("train"); cross(ctx, clampx(x, 180), clampy(y - 40), 100, p)
    label(C, ctx, t, k["dientes"] + 0.6, k["clac1"] - 0.1, "DIENTES", A, "teeth", dx=0, dy=180, size=62)
    label(C, ctx, t, k["seguros"], k["arriba"] - 0.1, "SEGURO", A, "pawl", dx=-40, dy=-190, size=62)
    p = win(t, k["volando"] + 0.6, k["ruedas"] - 0.05)
    if p: x, y = A("train"); cross(ctx, clampx(x, 180), clampy(y - 60), 100, p)
    label(C, ctx, t, k["encima"], k["rizo"] - 0.1, "CARGA", A, "w_top", dx=-40, dy=-150, size=58)
    label(C, ctx, t, k["lados"] + 0.2, k["rizo"] - 0.1, "GUÍA", A, "w_side", dx=40, dy=-150, size=58)
    label(C, ctx, t, k["debajo"] + 0.2, k["rizo"] - 0.1, "ANTIVUELCO", A, "w_up", dx=0, dy=150, size=54)
    label(C, ctx, t, k["encima"] + 0.3, k["rizo"] - 0.1, "RAÍL", A, "rail", dx=-210, dy=40, size=54)
    # medidor de «veces tu peso»
    gp = max(win(t, k["redondo"], k["curioso"] + 1.0), win(t, k["cuatro"] - 0.2, k["parar"] - 0.1))
    if gp:
        g = gforce(t); col = R if t < k["circulos"] and g > 4.6 else (G if t > k["circulos"] else Y)
        gbar(ctx, 150, 1350, 760, gp, g, col)
        C.badge(ctx, "× %s" % ("%.1f" % g).replace(".", ","), W / 2, BY, gp, col, size=84)
    p = win(t, k["circulos"] + 0.3, k["lagrima"] + 0.3)
    if p: x, y = A("ghost"); cross(ctx, clampx(x, 180), clampy(y + 30), 90, p)
    # frenos de roce: chirrían y se gastan
    p = win(t, k["chirr"] + 1.0, k["imanes"] + 0.1)
    if p: x, y = A("pads"); cross(ctx, clampx(x, 180), clampy(y - 30), 100, p)
    label(C, ctx, t, k["imanes"] + 0.6, k["pasar"] - 0.2, "IMANES", A, "magnets", dx=0, dy=170, size=60)
    label(C, ctx, t, k["aletas"], k["pasar"] + 0.4, "ALETA", A, "fin", dx=-60, dy=130, size=60)
    p = win(t, k["elec"], k["sig"] + 0.2)
    if p:
        x, y = W / 2, BY + 30
        bolt(ctx, x, y, 80, p); cross(ctx, x, y, 110, p)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.45), (k["vamos"] - 0.1, C.s_whoosh(), 0.45), (k["primero"], C.s_pop(), 0.3),
         (k["motor"] + 0.4, C.s_fail(), 0.35), (k["cadena"] + 0.3, C.s_clank(), 0.3), (k["treinta"] + 0.5, C.s_coin(), 0.35),
         (k["rompe"] + 0.2, C.s_thud(), 0.5), (k["rompe"] + 0.3, C.s_fail(), 0.35), (k["dientes"], C.s_whoosh(), 0.35),
         (k["arriba"] + 0.2, C.s_whoosh(), 0.35), (k["bajada"], C.s_whoosh(1.0), 0.5), (k["noventa"] + 0.7, C.s_coin(), 0.35),
         (k["volando"] + 0.5, C.s_whoosh(), 0.4), (k["volando"] + 0.7, C.s_fail(), 0.35), (k["ruedas"], C.s_whoosh(), 0.35),
         (k["encima"], C.s_pop(), 0.4), (k["lados"] + 0.2, C.s_pop(), 0.4), (k["debajo"] + 0.2, C.s_pop(), 0.4),
         (k["rizo"], C.s_whoosh(), 0.4), (k["seis"] + 0.3, C.s_thud(), 0.45), (k["circulos"] + 0.3, C.s_fail(), 0.35),
         (k["lagrima"], C.s_whoosh(), 0.35), (k["cuatro"] - 0.2, C.s_whoosh(), 0.4), (k["cuatro"] + 1.0, C.s_win(), 0.35),
         (k["parar"], C.s_whoosh(), 0.35), (k["chirr"] + 0.2, C.s_buzz(1.2), 0.25), (k["chirr"] + 1.0, C.s_fail(), 0.35),
         (k["imanes"] + 0.3, C.s_pop(), 0.35), (k["aletas"], C.s_pop(), 0.35), (k["corrientes"], C.s_whoosh(), 0.3),
         (k["sintocar"] + 0.3, C.s_win(), 0.35), (k["elec"], C.s_fail(), 0.3), (k["sig"], C.s_whoosh(), 0.4)]
    # clac de los seguros al pasar cada diente
    for tt in teeth_clacs():
        E.append((tt, C.s_clank(), 0.35))
    return E

# ---------------- dientes (compartido con la escena) ----------------
TOOTH_STEP = 1.6; TOOTH_LEN = 1.35; TOOTH_H = 0.32
def teeth_d():
    m = 1.0; d0 = v2d(1.04, m); d1 = v2d(1.97, m)
    n = int((d1 - d0) / TOOTH_STEP)
    return [d0 + i * TOOTH_STEP for i in range(n)]
PAWL_BACK = 9.5           # el seguro (en el último vagón) toca los dientes a esta distancia por detrás de la cabeza

def teeth_clacs():
    TD = teeth_d(); out = []; prev = None
    t = k["clac1"] - 0.25
    while t < k["arriba"] - 0.3:
        d = v2d(train_v(t), 1.0) - PAWL_BACK
        if prev is not None:
            for d0 in TD:
                if prev < d0 + TOOTH_LEN <= d: out.append(t)
        prev = d; t += 1 / 60
    return out
