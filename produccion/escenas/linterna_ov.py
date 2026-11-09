# Capa 2D de «Si tuvieras que inventar una linterna sin pilas…»
# También define el movimiento del imán, el voltaje, la carga del condensador y el brillo del led (los usa la escena 3D).
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("linterna")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"luz", "pilas", "linterna", "electricidad", "mano", "faraday", "tubo", "cobre", "imán", "bobina", "corriente",
            "voltaje", "agitas", "tirones", "diodos", "dirección", "condensador", "depósito", "bombilla", "segundo", "led",
            "treinta", "cinco", "minutos", "manivela", "principio", "pila"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def sg(t, a, b): return ss((t - a) / (b - a))
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]

# ---------------- movimiento (compartido con la escena) ----------------
def _K():
    return dict(luz=T("si esta"), vamos=T("vamos a inventar"), nec=T("necesitas"), enchufe=T("pero no hay"), mano=T("solo tienes"),
                truco=T("así que usas"), tubo=T("coges un tubo"), enrollas=T("le enrollas"), metes=T("y metes"),
                cada=T("cada vez que"), aparece=T("aparece corriente"), sin=T("sin tocarlo"), rapido=T("cuanto más"),
                agitas=T("así que agitas"), tirones=T("pero esa corriente"), sentido=T("un sentido"), otro=T("luego el otro"),
                nada=T("y luego nada"), diodos=T("así que pones unos"), cond=T("y un condensador"), dep=T("que la guarda"),
                curioso=T("y aquí viene"), bombilla=T("una bombilla"), segundo=T("en un segundo"), led=T("así que pones un led"),
                mucha=T("que da mucha"), treinta=T("con unos treinta"), cinco=T("consigues unos"), apaga=T("cuando se apaga"),
                vuelves=T("vuelves a agitar"), otras=T("otras cambian"), comoda=T("más cómoda"), ninguna=T("ninguna pila"),
                sig=T("sígueme"))
K = _K()

def shakes():
    k = K
    return [(0.0, k["luz"] + 3.2, 2.2), (k["agitas"], k["tirones"] - 0.1, 2.5), (k["diodos"], k["curioso"], 2.2),
            (k["segundo"] + 0.6, k["led"] + 0.7, 3.0), (k["treinta"], k["cinco"], 2.8), (k["vuelves"], k["otras"], 2.4),
            (k["sig"] - 0.1, DUR + 1, 2.2)]
SH = shakes()

def passes():
    k = K
    return [(k["metes"] + 0.4, k["metes"] + 1.8, -7.0, -2.0), (k["cada"] + 0.3, k["cada"] + 1.7, -2.0, 2.0),
            (k["rapido"] + 0.1, k["rapido"] + 0.55, 2.0, -2.0), (k["rapido"] + 0.8, k["rapido"] + 1.2, -2.0, 2.0),
            (k["rapido"] + 1.45, k["rapido"] + 1.85, 2.0, -2.0),
            (k["sentido"] - 0.6, k["sentido"] + 0.2, -2.0, 2.0), (k["otro"] - 0.25, k["otro"] + 0.55, 2.0, -2.0)]
PS = passes()

def shaking(t):
    for a, b, f in SH:
        if a <= t < b: return a, b, f
    return None

def shake_off(t):
    """desplazamiento del tubo a lo largo de su eje"""
    s = shaking(t)
    if not s: return 0.0
    a, b, f = s; env = min(1, (t - a) / 0.2, (b - t) / 0.2)
    return -0.45 * env * math.sin(2 * math.pi * f * (t - a))

def mag_x(t):
    s = shaking(t)
    if s:
        a, b, f = s; env = min(1, (t - a) / 0.25, (b - t) / 0.25)
        v = max(-1, min(1, 1.6 * math.sin(2 * math.pi * f * (t - a))))
        return mix(-2.0, 2.0 * v, env) if v > -2 else -2.0
    x = -2.0 if (t > K["metes"] or t < K["tubo"] - 1) else -7.0
    for a, b, x0, x1 in PS:
        if t >= b: x = x1
        elif t >= a: return x0 + (x1 - x0) * sg(t, a, b)
    return x

def mix(a, b, u): return a + (b - a) * u

def emf(t, h=1 / 60):
    phi = lambda x: math.exp(-(x / 0.8) ** 2)
    return -(phi(mag_x(t + h)) - phi(mag_x(t - h))) / (2 * h)

def volt(t):
    """-1..1 (la aguja)"""
    return math.tanh(emf(t) / 12)

def level(t):
    k = K
    return keyed(t, [(0, 0), (k["cond"] + 0.3, 0), (k["curioso"], 1.0), (k["bombilla"] + 1.0, 1.0), (k["segundo"] + 0.5, 0.0),
                     (k["segundo"] + 0.7, 0.0), (k["led"] + 0.6, 1.0), (k["treinta"] - 0.25, 0.97), (k["treinta"], 0.0),
                     (k["cinco"] - 0.1, 1.0), (k["apaga"] - 0.1, 0.02), (k["apaga"] + 0.3, 0.0), (k["vuelves"], 0.0),
                     (k["otras"], 0.45)])

def bright(t):
    k = K
    if t < k["vamos"]: return 0.85 + 0.15 * math.sin(t * 19)
    if k["bombilla"] + 0.6 <= t < k["segundo"] + 0.6: return level(t)       # bombilla antigua
    if k["led"] + 0.5 <= t < k["treinta"]: return min(1, (t - k["led"] - 0.5) / 0.3)
    if k["cinco"] <= t < k["apaga"] + 0.3: return min(1, level(t) * 6)
    if t >= k["ninguna"]: return 1.0
    return 0.0

def crank_ang(t):
    return max(0.0, t - K["otras"] - 0.6) * 5.0

# ---------------- dibujo ----------------
def gauge(ctx, t, x, y, r, p, v, rect=False):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); s = 0.6 + 0.4 * ss(p); ctx.scale(s, s)
    a0, a1 = math.radians(-160), math.radians(-20)
    rrect = None
    ctx.set_source_rgba(0.08, 0.09, 0.12, 0.9 * p); ctx.arc(0, 0, r * 1.12, math.pi, 0); ctx.close_path(); ctx.fill()
    # escala: verde a la derecha (+), roja a la izquierda (−)
    for lo, hi, col in ((a0, -math.pi / 2, (0.95, 0.35, 0.3)), (-math.pi / 2, a1, (0.3, 0.9, 0.45))):
        ctx.set_line_width(16); ctx.set_source_rgba(*col, p); ctx.arc(0, 0, r * 0.9, lo, hi); ctx.stroke()
    for i in range(11):
        a = a0 + (a1 - a0) * i / 10
        ctx.set_line_width(4 if i % 5 else 7); ctx.set_source_rgba(1, 1, 1, p)
        ctx.move_to(r * 0.72 * math.cos(a), r * 0.72 * math.sin(a)); ctx.line_to(r * (0.8 if i % 5 else 0.84) * math.cos(a), r * (0.8 if i % 5 else 0.84) * math.sin(a)); ctx.stroke()
    ctx.select_font_face("Poppins", 0, 1); ctx.set_font_size(r * 0.32)
    for s_, a in (("−", a0 + 0.25), ("+", a1 - 0.25)):
        e = ctx.text_extents(s_); ctx.move_to(r * 0.52 * math.cos(a) - e.x_advance / 2, r * 0.52 * math.sin(a) + r * 0.1); ctx.text_path(s_); ctx.fill()
    ctx.set_font_size(r * 0.36); e = ctx.text_extents("V"); ctx.move_to(-e.x_advance / 2, -r * 0.3); ctx.set_source_rgba(1, 0.82, 0.16, p); ctx.text_path("V"); ctx.fill()
    a = -math.pi / 2 + v * (a1 - a0) / 2
    ctx.set_line_cap(1); ctx.set_line_width(10); ctx.set_source_rgba(1, 1, 1, p)
    ctx.move_to(0, 0); ctx.line_to(r * 0.85 * math.cos(a), r * 0.85 * math.sin(a)); ctx.stroke()
    ctx.arc(0, 0, 16, 0, math.tau); ctx.fill()
    ctx.restore()

def cross(ctx, x, y, r, p, col=(0.93, 0.2, 0.22)):
    if p <= 0: return
    ctx.save(); ctx.set_line_cap(1)
    for lw, c in ((26, (0, 0, 0)), (15, col)):
        ctx.set_line_width(lw); ctx.set_source_rgba(*c, p)
        ctx.arc(x, y, r, 0, math.tau); ctx.stroke()
        ctx.move_to(x - r * 0.7, y - r * 0.7); ctx.line_to(x + r * 0.7, y + r * 0.7); ctx.stroke()
    ctx.restore()

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    k = K; BY = H * 0.265
    GX, GY, GR = 720, 1360, 150
    # voltímetro
    gp = max(win(t, 0, k["vamos"]), win(t, k["truco"] + 0.3, k["tubo"] - 0.2), win(t, k["cada"], k["curioso"]),
             win(t, k["treinta"], k["cinco"]), win(t, k["vuelves"], k["otras"] - 0.1), win(t, k["otras"] + 0.4, k["ninguna"] - 0.2),
             win(t, k["sig"], DUR + 1))
    if gp:
        if k["truco"] < t < k["tubo"]: v = math.tanh(2.2 * math.sin((t - k["truco"] - 0.3) * 4.2) * math.cos((t - k["truco"]) * 2.1))
        elif k["otras"] < t < k["ninguna"]: v = 0.75 * abs(math.sin(4 * (t - k["otras"] - 0.6))) if t > k["otras"] + 0.6 else 0.0
        else: v = volt(t)
        if t > k["diodos"] + 0.8: v = abs(v)          # con diodos: siempre en el mismo sentido
        gauge(ctx, t, GX, GY, GR, gp, v)
    # Faraday, 1831
    a0, a1 = k["truco"], k["tubo"]
    if a0 <= t < a1:
        yr = int(round(keyed(t, [(a0 + 0.8, 1700), (T("treinta y uno", fin=True), 1831)])))
        C.badge(ctx, str(yr), W / 2, BY, win(t, a0 + 0.8, a1), Y, size=96)
    # enchufe y pila tachados
    for key, tt in (("plug", k["enchufe"] + 0.6), ("bat", k["enchufe"] + 1.0)):
        p = win(t, tt, k["truco"] + 0.2)
        if p: x, y = A(key); cross(ctx, x, y, 110, p)
    label(C, ctx, t, k["enrollas"] + 0.6, k["metes"], "COBRE", A, "coil", dx=-150, dy=-170, size=62)
    label(C, ctx, t, k["metes"] + 1.0, k["cada"] + 0.4, "IMÁN", A, "mag", dx=-120, dy=170, size=62)
    label(C, ctx, t, k["diodos"] + 0.4, k["cond"], "DIODOS", A, "diodes", dx=-60, dy=170, size=60)
    label(C, ctx, t, k["cond"] + 0.3, k["curioso"], "CONDENSADOR", A, "cap", dx=60, dy=-190, size=56)
    # carga del condensador
    lp = max(win(t, k["cond"] + 0.5, k["led"] - 0.1), win(t, k["led"] + 0.4, DUR + 1) * (0 if k["otras"] - 0.6 < t < k["ninguna"] + 0.2 else 1))
    if lp:
        x, y = A("cap"); C.badge(ctx, f"{int(round(100 * level(t)))} %", clampx(x - 150, 200), clampy(y + 170, 500, 1400), lp, G, size=60)
    label(C, ctx, t, k["bombilla"] + 0.4, k["led"], "BOMBILLA", A, "bulb", dx=-260, dy=-40, size=56)
    # 1 segundo
    a0, a1 = k["bombilla"] + 0.6, k["led"]
    if a0 <= t < a1:
        s = min(1.0, max(0.0, (t - k["bombilla"] - 1.0) / max(0.1, k["segundo"] + 0.5 - k["bombilla"] - 1.0)))
        C.badge(ctx, f"{s:.1f} s".replace(".", ","), W / 2, BY, win(t, a0, a1), R, size=88)
    label(C, ctx, t, k["led"] + 0.4, k["treinta"] - 0.3, "LED", A, "led", dx=-200, dy=-40, size=64)
    # 30 s de agitar → 5 min de luz
    a0, a1 = k["treinta"], k["cinco"]
    if a0 <= t < a1:
        s = int(30 * sg(t, a0 + 0.1, a1 - 0.1))
        C.badge(ctx, f"AGITAR 0:{s:02d}", W / 2, BY, win(t, a0, a1), Y, size=78)
    a0, a1 = k["cinco"], k["vuelves"]
    if a0 <= t < a1:
        m = 300 * sg(t, a0 + 0.1, k["apaga"] - 0.1)
        C.badge(ctx, f"LUZ {int(m // 60)}:{int(m % 60):02d}", W / 2, BY, win(t, a0, a1), G, size=78)
    label(C, ctx, t, k["otras"] + 0.5, k["comoda"] + 0.3, "MANIVELA", A, "crank", dx=0, dy=-200, size=62)
    label(C, ctx, t, k["otras"] + 2.2, k["ninguna"] - 0.2, "IMÁN", A, "rotor", dx=-170, dy=-120, size=58)
    p = win(t, k["ninguna"] + 0.4, k["sig"])
    if p: x, y = A("bat"); cross(ctx, x, y, 100, p)

def sfx_events(C):
    k = K
    E = [(0.0, C.s_whoosh(), 0.4)]
    for a, b, f in SH:                       # golpes del imán en los topes al agitar
        n = int((b - a) * f * 2)
        for i in range(min(n, 30)):
            tt = a + 0.25 / f + i / (2 * f)
            if tt < min(b, DUR): E.append((tt, C.s_clank(), 0.12))
    E += [(k["vamos"], C.s_whoosh(), 0.4), (k["enchufe"] + 0.6, C.s_fail(), 0.4), (k["enchufe"] + 1.0, C.s_fail(), 0.35),
          (k["mano"], C.s_pop(), 0.4), (k["truco"] + 0.4, C.s_whoosh(), 0.4), (k["tubo"], C.s_pop(), 0.45),
          (k["metes"] + 1.7, C.s_thud(), 0.45), (k["cada"] + 1.0, C.s_bleep(1500), 0.3), (k["rapido"] + 0.3, C.s_whoosh(), 0.35),
          (k["diodos"], C.s_pop(), 0.45), (k["cond"], C.s_pop(), 0.45), (k["curioso"] + 0.3, C.s_win(), 0.35),
          (k["bombilla"] + 0.6, C.s_buzz(1.2), 0.25), (k["segundo"] + 0.5, C.s_fail(), 0.4), (k["led"] + 0.5, C.s_pop(), 0.5),
          (k["apaga"], C.s_fail(), 0.3), (k["otras"] + 0.3, C.s_whoosh(), 0.4), (k["ninguna"] + 0.4, C.s_fail(), 0.4),
          (k["sig"], C.s_whoosh(), 0.4)]
    return E
