# Capa 2D de «Si tuvieras que inventar el detector de humo…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("detector")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"humo", "fuego", "cajita", "rendijas", "aire", "oscuras", "luz", "led", "sensor", "enfrente", "ángulo", "pared", "recta",
            "nada", "partículas", "rebota", "límite", "alarma", "sirena", "ochenta", "cinco", "decibelios", "tres", "metros", "tráfico",
            "polvo", "insecto", "malla", "varias", "pila", "pitido", "semanas", "sellada", "diez", "años"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]

LIMITE = 0.65
def lum(t):   # igual que en la escena
    v = keyed(t, [(0, 0.0), (T("una parte") - 0.2, 0.0), (T("una parte") + 0.5, 0.3), (T("cuanto más"), 0.32), (T("más luz", fin=True) + 0.4, 0.55),
                  (T("límite"), 0.58), (T("salta"), 0.85), (T("curioso") - 0.4, 0.85), (T("curioso") + 0.6, 0.0),
                  (T("el polvo") + 1.0, 0.0), (T("el polvo") + 1.8, 0.72), (T("mide") + 0.9, 0.72), (T("mide") + 2.0, 0.05)])
    return v

def medidor(ctx, C, t, v, p, x=150, y0=640, h=560):
    """barra vertical de luz que llega al sensor, con la línea del límite"""
    if p <= 0: return
    ctx.save(); s = C.back(p); ctx.translate(x, y0 + h / 2); ctx.scale(s, s); ctx.translate(0, -h / 2)
    w = 74
    C.rrect(ctx, -w / 2 - 14, -70, w + 28, h + 100, 22); ctx.set_source_rgba(0.08, 0.09, 0.14, 0.88); ctx.fill()
    C.rrect(ctx, -w / 2, 0, w, h, 12); ctx.set_source_rgba(0.2, 0.22, 0.3, 1); ctx.fill()
    hv = h * max(0, min(1, v)); over = v >= LIMITE
    col = C.RED if over else (0.45, 0.8, 1.0)
    if hv > 2: C.rrect(ctx, -w / 2, h - hv, w, hv, 12); ctx.set_source_rgb(*col); ctx.fill()
    yl = h * (1 - LIMITE)
    ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(5); ctx.set_dash([14, 9]); ctx.move_to(-w / 2 - 14, yl); ctx.line_to(w / 2 + 14, yl); ctx.stroke(); ctx.set_dash([])
    C.text_path(ctx, "LUZ", 34); e = ctx.text_extents("LUZ"); ctx.move_to(-e.x_advance / 2, -22); ctx.text_path("LUZ"); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.restore()
    if p > 0.5:
        C.outlined(ctx, "LÍMITE", x + 150, y0 + yl, 40, fill=(1, 1, 1), stroke=8, alpha=min(1, (p - 0.5) * 2))

def dial(ctx, C, t, v, p, cx=W / 2, cy=1330, r=150, extra=None):
    """decibelímetro de 0 a 100 dB"""
    if p <= 0: return
    ctx.save(); s = C.back(p); ctx.translate(cx, cy); ctx.scale(s, s)
    C.rrect(ctx, -r - 40, -r - 40, 2 * r + 80, r + 120, 30); ctx.set_source_rgba(0.08, 0.09, 0.14, 0.9); ctx.fill()
    ctx.set_line_width(26); ctx.set_source_rgb(0.25, 0.27, 0.35); ctx.arc(0, 0, r, math.pi, 2 * math.pi); ctx.stroke()
    f = max(0.002, min(1, v / 100)); ctx.set_source_rgb(1.0, 0.85 - 0.6 * f, 0.25)
    ctx.arc(0, 0, r, math.pi, math.pi + math.pi * f); ctx.stroke()
    a = math.pi + math.pi * f; ctx.set_line_width(8); ctx.set_source_rgb(1, 1, 1)
    ctx.move_to(0, 0); ctx.line_to((r - 30) * math.cos(a), (r - 30) * math.sin(a)); ctx.stroke(); ctx.arc(0, 0, 12, 0, 7); ctx.fill()
    txt = f"{int(round(v))} dB"; C.text_path(ctx, txt, 64); e = ctx.text_extents(txt)
    ctx.move_to(-e.x_advance / 2, 66); ctx.text_path(txt); ctx.set_source_rgb(*C.YL); ctx.fill()
    if extra:
        a85 = math.pi + math.pi * 0.85; ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(5)
        ctx.move_to((r + 16) * math.cos(a85), (r + 16) * math.sin(a85)); ctx.line_to((r + 40) * math.cos(a85), (r + 40) * math.sin(a85)); ctx.stroke()
    ctx.restore()
    if extra: C.outlined(ctx, extra, cx + 70, cy - r - 75, 42, fill=(1, 1, 1), stroke=8, alpha=extra_p(t))

def extra_p(t): return min(1, max(0, (t - T("tráfico") + 0.2) / 0.3))

def pila_icon(ctx, C, t, v, p, cx=W / 2, cy=1340):
    if p <= 0: return
    ctx.save(); s = C.back(p); ctx.translate(cx, cy); ctx.scale(s, s)
    w, h = 300, 130
    C.rrect(ctx, -w / 2 - 30, -h / 2 - 30, w + 90, h + 60, 24); ctx.set_source_rgba(0.08, 0.09, 0.14, 0.88); ctx.fill()
    C.rrect(ctx, -w / 2, -h / 2, w, h, 16); ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(9); ctx.stroke()
    ctx.rectangle(w / 2 + 4, -h / 4, 20, h / 2); ctx.fill()
    col = C.GREEN if v > 0.5 else ((1.0, 0.75, 0.2) if v > 0.2 else C.RED)
    n = int(math.ceil(v * 5 - 1e-6))
    if v < 0.2 and v > 0.01 and (t * 3) % 1 < 0.4: n = 0
    for k in range(n):
        C.rrect(ctx, -w / 2 + 14 + k * 55, -h / 2 + 14, 46, h - 28, 6); ctx.set_source_rgb(*col); ctx.fill()
    ctx.restore()

def lectura(ctx, C, t, p, x0=280, y=1330):
    """mide varias veces: una columna por medida"""
    if p <= 0: return
    a = T("mide") - 0.2
    vals = [0.72, 0.7, 0.35, 0.08, 0.06, 0.05]
    n = max(0, min(len(vals), int((t - a) / 0.7) + 1)) if t >= a else 0
    ctx.save(); ctx.translate(W / 2, y); s = C.back(p); ctx.scale(s, s)
    C.rrect(ctx, -300, -150, 600, 210, 24); ctx.set_source_rgba(0.08, 0.09, 0.14, 0.88); ctx.fill()
    yl = 30 - 160 * LIMITE
    ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(4); ctx.set_dash([12, 8]); ctx.move_to(-280, yl); ctx.line_to(280, yl); ctx.stroke(); ctx.set_dash([])
    for k in range(n):
        v = vals[k]; hh = 160 * v; x = -250 + k * 88
        ctx.rectangle(x, 30 - hh, 60, hh); ctx.set_source_rgb(*(C.RED if v >= LIMITE else (0.45, 0.8, 1.0))); ctx.fill()
    ctx.restore()

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    Yb = H * 0.265
    label(C, ctx, t, 0.3, T("vamos") - 0.2, "HUMO", A, "humo", dx=-120, dy=-200, size=64)
    label(C, ctx, t, T("quieres") + 0.3, T("así que haces"), "HUMO", A, "fhumo", dx=60, dy=-170, size=60)
    label(C, ctx, t, T("fuego") - 0.2, T("así que haces"), "FUEGO", A, "fuego", dx=40, dy=170, size=60)
    label(C, ctx, t, T("rendijas") - 0.1, T("pero a oscuras"), "RENDIJAS", A, "rend", dx=60, dy=-150, size=58)
    label(C, ctx, t, T("oscuras") - 0.1, T("dentro pones"), "CÁMARA NEGRA", A, "camara", dx=0, dy=-160, size=54)
    label(C, ctx, t, T("led") - 0.1, T("pero no los"), "LED", A, "led", dx=-30, dy=-150, size=64)
    label(C, ctx, t, T("sensor") - 0.1, T("pero no los"), "SENSOR", A, "sensor", dx=20, dy=-150, size=58)
    a0, a1 = T("pero no los") + 0.2, T("en ángulo") + 0.3
    if a0 <= t < a1: C.badge(ctx, "✗ SIEMPRE VE LUZ", W / 2, Yb, win(t, a0, a1), R, size=66)
    label(C, ctx, t, T("en ángulo") + 0.8, T("con el aire"), "SENSOR", A, "sensor", dx=40, dy=-140, size=56)
    label(C, ctx, t, T("pared") - 0.1, T("con el aire") + 0.8, "PARED", A, "sep", dx=-40, dy=-140, size=58)
    label(C, ctx, t, T("recta") - 0.3, T("cuando entra"), "TRAMPA", A, "trap", dx=60, dy=160, size=56)
    # medidor de luz en el sensor
    a0, a1 = T("y el sensor"), T("sirena") - 0.2
    if a0 - 0.2 <= t < a1: medidor(ctx, C, t, lum(t), win(t, a0 - 0.2, a1))
    a0, a1 = T("el polvo"), T("se acaba") - 0.3
    if a0 <= t < a1: medidor(ctx, C, t, lum(t), win(t, a0, a1))
    label(C, ctx, t, T("partículas") - 0.1, T("una parte"), "PARTÍCULAS", A, "haz", dx=80, dy=200, size=54)
    a0, a1 = T("salta"), T("despertarte")
    if a0 - 0.1 <= t < a1 and (t * 4) % 1 < 0.6:
        ctx.set_source_rgba(*R, 0.55 * win(t, a0 - 0.1, a1)); ctx.set_line_width(26); ctx.rectangle(13, 13, W - 26, H - 26); ctx.stroke()
    # sirena y decibelios
    label(C, ctx, t, T("sirena") - 0.1, T("ochenta") - 0.2, "SIRENA", A, "sirena", dx=40, dy=-170, size=60)
    a0, a1 = T("ochenta") - 0.4, T("curioso") - 0.2
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0), (T("decibelios", fin=True), 85)]) + (1.2 * math.sin(t * 17) if t > T("decibelios", fin=True) else 0)
        dial(ctx, C, t, v, win(t, a0, a1), extra="AVENIDA" if t > T("tráfico") - 0.2 else None)
    a0, a1 = T("medidos"), T("curioso") - 0.2
    if a0 <= t < a1:
        p = win(t, a0, a1); x0, _ = A("sirena")
        C.arrow_dim(ctx, 170, 830, 1080, Y, min(1, (t - a0) / 0.6))
        C.outlined(ctx, "3 m", 500, 1010, 70, fill=Y, stroke=12, alpha=p)
    # polvo, insecto, malla y medidas
    label(C, ctx, t, T("el polvo") + 0.4, T("insecto"), "POLVO", A, "haz", dx=60, dy=-170, size=60)
    label(C, ctx, t, T("insecto") + 0.2, T("malla") + 0.2, "INSECTO", A, "bicho", dx=-40, dy=-170, size=58)
    label(C, ctx, t, T("malla") + 0.1, T("mide"), "MALLA", A, "malla", dx=-20, dy=-170, size=60)
    a0, a1 = T("mide") - 0.2, T("se acaba") - 0.3
    if a0 <= t < a1:
        lectura(ctx, C, t, win(t, a0, a1))
        p = win(t, T("pitar") - 0.2, a1)
        if p: C.badge(ctx, "✓ NO PITA", W / 2, Yb, p, G, size=74)
    # pila
    label(C, ctx, t, T("pila") - 0.1, T("cuando le queda"), "PILA", A, "pila", dx=0, dy=-170, size=62)
    a0, a1 = T("se acaba"), T("sígueme") + 0.2
    if a0 <= t < a1:
        v = keyed(t, [(a0, 1.0), (T("no puede avisarte", fin=True), 0.0), (T("cuando le queda") - 0.1, 0.0), (T("cuando le queda") + 0.4, 0.15),
                      (T("cambias") + 0.3, 0.15), (T("cambias") + 0.8, 1.0)])
        pila_icon(ctx, C, t, v, win(t, a0, a1))
    a0 = T("no puede avisarte")
    if a0 <= t < T("así que", 4) - 0.1:
        C.badge(ctx, "✗ 0 PITIDOS", W / 2, Yb, win(t, a0, T("así que", 4) - 0.1), R, size=70)
    a0, a1 = T("suelta"), T("cambias")
    if a0 <= t < a1:
        ph = (t - a0) % 1.6
        if ph < 0.6:
            x, y = A("sirena"); C.callout(ctx, "PIP", clampx(x), clampy(y - 170), min(1, ph / 0.12) * (1 - max(0, ph - 0.45) / 0.15), size=64)
    label(C, ctx, t, T("sellada") - 0.1, T("sígueme"), "SELLADA", A, "pila", dx=-60, dy=-170, size=60)
    a0, a1 = T("diez") - 0.3, DUR + 1
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0), (T("años", fin=True) + 0.2, 10)])
        C.badge(ctx, f"{int(round(v))} AÑOS", W / 2, Yb, win(t, a0, a1), G, size=84)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.35)]
    a = 0.1
    while a < T("vamos") - 0.3:
        E.append((a, C.s_bleep(3100), 0.35)); a += 0.25
    E += [(T("vamos"), C.s_whoosh(), 0.4), (T("fuego"), C.s_thud(), 0.3), (T("así que haces"), C.s_thud(), 0.45),
          (T("para que entre"), C.s_whoosh(), 0.35), (T("pero a oscuras"), C.s_clank(), 0.35), (T("led"), C.s_pop(), 0.45),
          (T("sensor"), C.s_pop(), 0.45), (T("pero no los"), C.s_fail(), 0.4), (T("en ángulo"), C.s_whoosh(), 0.35),
          (T("pared"), C.s_thud(), 0.4), (T("recta"), C.s_buzz(0.8), 0.2), (T("cuando entra"), C.s_whoosh(), 0.35),
          (T("rebota"), C.s_pop(), 0.4), (T("una parte"), C.s_coin(), 0.35), (T("límite"), C.s_pop(), 0.35)]
    a = T("salta")
    while a < T("despertarte"):
        E.append((a, C.s_bleep(3100), 0.4)); a += 0.25
    E += [(T("sirena"), C.s_clank(), 0.4), (T("decibelios"), C.s_buzz(1.6), 0.3), (T("medidos"), C.s_whoosh(), 0.35),
          (T("curioso"), C.s_whoosh(), 0.4), (T("el polvo") + 1.6, C.s_pop(), 0.4), (T("insecto"), C.s_buzz(1.2), 0.2),
          (T("malla"), C.s_clank(), 0.4), (T("pitar") , C.s_win(), 0.35), (T("se acaba"), C.s_fail(), 0.4)]
    a = T("suelta")
    while a < T("cambias"):
        E.append((a, C.s_bleep(3300), 0.35)); a += 1.6
    E += [(T("cambias") + 0.6, C.s_clank(), 0.4), (T("algunos") + 0.8, C.s_thud(), 0.4), (T("años"), C.s_win(), 0.4),
          (T("sígueme"), C.s_whoosh(), 0.4)]
    for k in range(4):
        E.append((T("mide") - 0.2 + 0.7 * k, C.s_bleep(1500), 0.2))
    return E
