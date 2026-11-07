# Capa 2D de «Si tuvieras que inventar el spray…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("spray")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"nube", "finísima", "bote", "gotas", "gas", "aire", "presión", "menos", "flojo", "líquido", "butano", "propano",
            "medio", "grado", "cero", "veinte", "tres", "atmósferas", "hierve", "misma", "tubo", "válvula", "muelle", "agujero",
            "golpe", "calor", "helado", "cincuenta", "doce", "bares", "sol", "coche", "noruego", "veintiséis"}

def sg(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)

def bar(C, ctx, t, a, b, frac, col, title, y):
    p = win(t, a, b)
    if not p: return
    w, h = 560, 40; x0 = W / 2 - w / 2
    C.rrect(ctx, x0 - 12, y - 12, w + 24, h + 24, 20); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.92 * p); ctx.fill()
    C.rrect(ctx, x0, y, max(h, w * frac), h, 14); ctx.set_source_rgba(*col, p); ctx.fill()
    C.badge(ctx, title, W / 2, y - 58, p, col, size=56)

def fmt(v): return ("%.1f" % v).replace(".", ",")

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.8, 1.0)
    BY = H * 0.265
    label(C, ctx, t, T("qué hay") , T("vamos a inventarlo") + 0.3, "LÍQUIDO", A, "liq", dx=-200, dy=0, size=60)
    label(C, ctx, t, T("un gas"), T("pero si metes"), "GAS", A, "gas", dx=-180, dy=0, size=64)
    # aire a presión: cada pulsación baja
    a0, a1 = T("pero si metes"), T("así que usas")
    if a0 <= t < a1:
        ps = [T("cada vez") + 0.3, T("empuja menos") - 0.1, T("y al final") + 0.3]
        v = 6.0 - sum(1.8 * sg(t, p, p + 0.4) for p in ps)
        f = v / 6; col = G if f > 0.6 else (Y if f > 0.3 else R)
        bar(C, ctx, t, a0, a1, f, col, fmt(v) + " ATM", BY + 40)
    label(C, ctx, t, T("butano o"), T("el butano"), "BUTANO", A, "but", dx=-190, dy=0, size=60)
    a0, a1 = T("el butano"), T("dentro del", 2)
    if a0 <= t < a1:
        v = 20 - 20.5 * sg(t, T("hierve a"), T("bajo cero", fin=True))
        C.badge(ctx, fmt(v) + " °C", W / 2, BY, win(t, a0, a1), B, size=92)
    a0, a1 = T("dentro del", 2), T("pero el líquido")
    if a0 <= t < a1:
        C.badge(ctx, "20 °C", W / 2, BY, win(t, a0, a1), Y, size=70)
        v = 1 + 2 * sg(t, T("está a unas"), T("atmósferas", fin=True)) if t < T("cuando sale") else 3.0
        if T("cuando sale") <= t < T("rellena"): v = 3.0 - 0.6 * math.sin(math.pi * sg(t, T("cuando sale"), T("rellena")))
        bar(C, ctx, t, T("está a unas") - 0.2, a1, v / 3.5, B, fmt(v) + " ATM", BY + 170)
    label(C, ctx, t, T("un tubo"), T("y una válvula") + 0.3, "TUBO", A, "tube", dx=-170, dy=0, size=60)
    label(C, ctx, t, T("con un muelle"), T("al apretar"), "MUELLE", A, "spring", dx=-200, dy=40, size=58)
    label(C, ctx, t, T("un agujero"), T("y el gas"), "0,5 MM", A, "noz", dx=-150, dy=-120, size=58)
    a0, a1 = T("para hervir"), T("pero el calor")
    if a0 <= t < a1:
        v = 20 - 15 * sg(t, T("si pulverizas"), T("helado", fin=True))
        C.badge(ctx, "%d °C" % round(v), W / 2, BY, win(t, a0, a1), B, size=92)
    a0, a1 = T("pero el calor"), T("lo patentó")
    if a0 <= t < a1:
        v = 20 + 30 * sg(t, T("a cincuenta"), T("grados", 2, fin=True))
        C.badge(ctx, "%d °C" % round(v), W / 2, BY, win(t, a0, a1), R if v > 40 else Y, size=88)
        pb = 3 + 9 * sg(t, T("y el bote debe"), T("doce bares", fin=True))
        bar(C, ctx, t, T("a cincuenta"), a1, pb / 12, R if pb > 8 else Y, "%d BAR" % round(pb), BY + 200)
    if T("por eso nunca") <= t < T("lo patentó"):
        C.badge(ctx, "✗", W / 2, BY + 340, win(t, T("por eso nunca"), T("lo patentó")), R, size=100)
    a0, a1 = T("lo patentó"), T("sígueme")
    if a0 <= t < a1:
        v = 1900 + 26 * sg(t, T("en mil"), T("veintiséis", fin=True))
        C.badge(ctx, "%d" % round(v), W / 2, BY, win(t, a0, a1), Y, size=96)

def sfx_events(C):
    E = [(0.45, C.s_buzz(1.8), 0.35), (T("vamos a inventarlo"), C.s_whoosh(), 0.45), (T("un gas"), C.s_pop(), 0.4),
         (T("y al final") + 0.8, C.s_fail(), 0.4), (T("butano"), C.s_pop(), 0.4), (T("bajo cero"), C.s_coin(), 0.4),
         (T("atmósferas"), C.s_coin(), 0.4), (T("cuando sale"), C.s_buzz(1.0), 0.3), (T("y la presión vuelve"), C.s_win(), 0.35),
         (T("un tubo"), C.s_whoosh(), 0.35), (T("con un muelle"), C.s_clank(), 0.4), (T("al apretar"), C.s_clank(), 0.45),
         (T("al apretar") + 0.8, C.s_buzz(7.0), 0.28), (T("helado"), C.s_win(), 0.35), (T("sube mucho"), C.s_fail(), 0.35),
         (T("doce bares"), C.s_thud(), 0.5), (T("veintiséis"), C.s_coin(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    for k, p in enumerate([T("cada vez") + 0.3, T("empuja menos") - 0.1, T("y al final") + 0.3]):
        E.append((p, C.s_buzz(1.0), 0.3 - 0.07 * k))
    return E
