# Capa 2D de «Así funciona la olla exprés»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("ollaexpres")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"tercio", "fuego", "tapa", "cien", "grados", "vapor", "escapa", "goma", "atrapado", "empuja", "presión", "bar",
            "ciento", "veinte", "rápido", "válvula", "muelle", "chorro", "silba", "seguridades", "deforma", "cierre", "bloquea"}

def sg(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)

def bar(C, ctx, t, a, b, frac, col, title, y):
    p = win(t, a, b)
    if not p: return
    w, h = 560, 40; x0 = W / 2 - w / 2
    C.rrect(ctx, x0 - 12, y - 12, w + 24, h + 24, 20); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.92 * p); ctx.fill()
    C.rrect(ctx, x0, y, max(h, w * frac), h, 14); ctx.set_source_rgba(*col, p); ctx.fill()
    C.badge(ctx, title, W / 2, y - 58, p, col, size=56)

def temp(t):
    v = 20 + 80 * sg(t, T("en una cazuela"), T("cien grados", fin=True))
    v += 20 * sg(t, T("hasta los ciento"), T("veinte grados", fin=True))
    return v

def press(t):
    p = sg(t, T("el vapor se queda"), T("un bar", fin=True))
    p += 0.35 * sg(t, T("pero la presión no"), T("la levanta")) - 0.35 * sg(t, T("la levanta"), T("y sale un") + 0.4)
    return p * (1 - sg(t, T("hasta que no"), T("no se abre")))

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.8, 1.0)
    BY = H * 0.265
    # gancho: tiempo de cocción 60 → 20 min
    if t < T("en una cazuela"):
        v = 60 - 40 * sg(t, 0.4, T("tercio", fin=True))
        C.badge(ctx, "⏱ %d MIN" % round(v) if False else "%d MIN" % round(v), W / 2, BY, win(t, -1, T("cómo lo hace")), G, size=90)
    # termómetro
    a0, a1 = T("en una cazuela"), T("pero")
    if a0 <= t < a1:
        v = temp(t); sh = 6 * math.sin(t * 30) if t > T("y por mucho") else 0
        C.badge(ctx, "%d °C" % round(v), W / 2 + sh, BY, win(t, a0, a1), R if v >= 99.5 else Y, size=96)
        if t >= T("no pasa de"): C.badge(ctx, "MÁX. 100 °C", W / 2, BY + 140, win(t, T("no pasa de"), a1), R, size=56)
    label(C, ctx, t, T("y una goma") + 0.1, T("el vapor se queda"), "GOMA", A, "gasket", dx=60, dy=-130, size=64)
    # presión y temperatura cerrada
    a0, a1 = T("el vapor se queda"), T("pero la presión no")
    if a0 <= t < a1:
        f = min(1, press(t))
        bar(C, ctx, t, a0, a1, f, B, "+%.1f BAR" % f, BY + 40)
    a0, a1 = T("y con más"), T("pero la presión no")
    if a0 <= t < a1:
        C.badge(ctx, "%d °C" % round(temp(t)), W / 2, BY + 190, win(t, a0, a1), R if temp(t) > 110 else Y, size=90)
    a0, a1 = T("y a esa"), T("pero la presión no")
    if a0 <= t < a1:
        v = 60 - 40 * sg(t, T("la comida"), T("rápido", fin=True))
        C.badge(ctx, "%d MIN" % round(v), W / 2, BY + 330, win(t, a0, a1), G, size=80)
    a0, a1 = T("pero la presión no"), T("y aquí viene")
    if a0 <= t < a1:
        f = press(t); col = R if f > 1.15 else B
        bar(C, ctx, t, a0, a1, min(1, f / 1.35), col, "+%.1f BAR" % f, BY + 40)
    label(C, ctx, t, T("una válvula"), T("cuando el vapor"), "VÁLVULA", A, "valve", dx=-60, dy=-120, size=60)
    label(C, ctx, t, T("con un muelle"), T("la levanta") + 0.3, "MUELLE", A, "spring", dx=210, dy=40, size=60)
    a0, a1 = T("tu olla lleva"), T("y si todas")
    if a0 <= t < a1:
        n = 1 + (t >= T("dos o tres")) + (t >= T("dos o tres") + 0.4)
        C.badge(ctx, ("%d SEGURIDADES" % n) if n > 1 else "1 SEGURIDAD", W / 2, BY, win(t, a0, a1), G, size=72)
    label(C, ctx, t, T("se deforma"), T("pero aún falta"), "GOMA", A, "bulge", dx=-60, dy=-140, size=62)
    if T("intentas") <= t < T("así que la tapa"): C.badge(ctx, "✗", W / 2, BY, win(t, T("intentas") + 0.3, T("así que la tapa")), R, size=110)
    label(C, ctx, t, T("un cierre"), T("hasta que no") + 0.4, "CIERRE", A, "pin", dx=0, dy=-140, size=62)
    a0, a1 = T("hasta que no"), T("sígueme")
    if a0 <= t < a1:
        f = press(t); bar(C, ctx, t, a0, a1, f, G if f < 0.05 else B, "+%.1f BAR" % f, BY + 40)

def sfx_events(C):
    E = [(0.0, C.s_buzz(4.8), 0.3), (T("tercio"), C.s_coin(), 0.4), (T("en una cazuela"), C.s_whoosh(), 0.4),
         (T("cien grados"), C.s_pop(), 0.4), (T("subas el fuego"), C.s_whoosh(0.8), 0.4), (T("no pasa de"), C.s_fail(), 0.35),
         (T("que se escapa"), C.s_whoosh(), 0.35), (T("así que cierras") + 0.9, C.s_clank(), 0.6), (T("y empuja"), C.s_thud(), 0.45),
         (T("un bar"), C.s_coin(), 0.4), (T("veinte grados"), C.s_win(), 0.4), (T("rápido"), C.s_coin(), 0.4),
         (T("sin límite"), C.s_fail(), 0.4), (T("una válvula"), C.s_pop(), 0.4), (T("con un muelle"), C.s_clank(), 0.4),
         (T("y sale un"), C.s_buzz(2.4), 0.35), (T("dos o tres"), C.s_pop(), 0.4), (T("dos o tres") + 0.4, C.s_pop(), 0.4),
         (T("se deforma"), C.s_whoosh(), 0.4), (T("intentas"), C.s_fail(), 0.4), (T("un cierre"), C.s_clank(), 0.5),
         (T("no se abre"), C.s_win(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
