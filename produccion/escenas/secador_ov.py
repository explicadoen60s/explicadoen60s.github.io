# Capa 2D de «Si tuvieras que inventar el secador de pelo…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("secador")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"vatios", "horas", "calor", "aire", "ventilador", "motor", "rejilla", "frío", "alambre", "níquel", "cromo", "treinta",
            "mica", "corriente", "rojo", "caliente", "energía", "horno", "tapas", "recalienta", "lámina", "metales", "dobla",
            "sesenta", "corta", "vuelve", "fusible", "boquilla", "chorro"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]
def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def bars(ctx, C, t, a0, a1, rows, y0):
    """barras horizontales de potencia: rows = [(texto, valor, máx, color, t_inicio)]"""
    p = win(t, a0, a1)
    if p <= 0: return
    x0, wmax = 150, 780
    for k, (txt, v, vmax, col, ts) in enumerate(rows):
        u = ss((t - ts) / 1.0); y = y0 + k * 150
        C.rrect(ctx, x0, y, wmax, 64, 18); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.85 * p); ctx.fill()
        w = max(8, wmax * (v / vmax) * u)
        C.rrect(ctx, x0, y, w, 64, 18); ctx.set_source_rgba(*col, p); ctx.fill()
        C.outlined(ctx, f"{txt} {miles(v * u)} W", W / 2, y - 34, 50, fill=(1, 1, 1), stroke=9, alpha=p)

def thermo(ctx, C, t, a0, a1, lvl, x=860, y=1000):
    """termómetro vertical sin cifras (se va al rojo)"""
    p = win(t, a0, a1)
    if p <= 0: return
    h = 420
    C.rrect(ctx, x - 26, y - h, 52, h, 26); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.9 * p); ctx.fill()
    ctx.arc(x, y + 20, 46, 0, math.tau); ctx.fill()
    col = (1.0, 0.85 - 0.6 * lvl, 0.2 - 0.05 * lvl)
    hh = (h - 30) * max(0.08, lvl)
    C.rrect(ctx, x - 14, y - hh, 28, hh + 10, 14); ctx.set_source_rgba(*col, p); ctx.fill()
    ctx.arc(x, y + 20, 34, 0, math.tau); ctx.fill()

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    BY = H * 0.265; O = (1.0, 0.55, 0.2)
    # potencia del secador
    a0, a1 = 0.0, T("vamos a")
    if t < a1:
        v = keyed(t, [(0.3, 0), (T("vatios", fin=True), 2000)])
        C.badge(ctx, miles(v) + " W", W / 2, BY, win(t, a0, a1), Y, size=96)
    # el pelo solo: horas
    a0, a1 = T("pero tarda"), T("el agua necesita")
    if a0 <= t < a1 + 0.3:
        h = keyed(t, [(a0, 0), (a1, 3)])
        C.badge(ctx, f"{h:.1f} H".replace(".", ","), W / 2, BY, win(t, a0, a1 + 0.3), B, size=90)
    label(C, ctx, t, T("el agua necesita") + 0.3, T("primero"), "VAPOR", A, "hair", dx=-60, dy=260, size=60)
    label(C, ctx, t, T("así que pones un") + 0.6, T("con un motor") + 0.2, "VENTILADOR", A, "fan", dx=40, dy=-200, size=58)
    label(C, ctx, t, T("con un motor"), T("aspira el"), "MOTOR", A, "motor", dx=-60, dy=-230, size=60)
    label(C, ctx, t, T("aspira el"), T("pero el aire frío"), "REJILLA", A, "grill", dx=60, dy=-170, size=60)
    # aire frío
    a0, a1 = T("pero el aire frío"), T("pones un alambre")
    if a0 <= t < a1: C.badge(ctx, "AIRE 22 °C", W / 2, BY, win(t, a0, a1), B, size=84)
    label(C, ctx, t, T("pones un alambre"), T("unos treinta"), "NI-CR", A, "coil", dx=0, dy=-230, size=64)
    a0, a1 = T("unos treinta"), T("cuando pasa la")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0), (T("enrollados") + 0.6, 30)])
        C.badge(ctx, f"{int(v)} CM", W / 2, BY, win(t, a0, a1), Y, size=90)
    label(C, ctx, t, T("una placa"), T("cuando pasa la"), "MICA", A, "mica", dx=-40, dy=220, size=62)
    # alambre al rojo y aire que sale caliente
    a0, a1 = T("cuando pasa la"), T("el aire lo")
    if a0 <= t < a1:
        v = keyed(t, [(a0 + 0.3, 20), (T("al rojo", fin=True), 550)])
        C.badge(ctx, f"ALAMBRE ~{miles(v)} °C", W / 2, BY, win(t, a0, a1), R if v > 400 else O, size=78)
    a0, a1 = T("el aire lo"), T("ese alambre")
    if a0 <= t < a1:
        v = keyed(t, [(a0 + 0.3, 22), (T("caliente", fin=True), 70)])
        C.badge(ctx, f"AIRE {int(v)} °C", W / 2, BY, win(t, a0, a1), O if v > 40 else B, size=84)
    # reparto de la energía
    a0, a1 = T("ese alambre"), T("pero si tapas")
    bars(ctx, C, t, a0, a1, [("ALAMBRE", 1900, 2000, R, a0 + 0.2), ("MOTOR", 100, 2000, B, T("mucho más") - 0.2)], H * 0.30)
    if t > T("por eso un"):
        C.badge(ctx, "TOTAL 2.000 W", W / 2, H * 0.30 + 290, win(t, T("por eso un"), a1), Y, size=70)
    # tapar la rejilla
    badge(C, ctx, t, T("el aire deja") + 0.2, T("el alambre sigue"), "✗ AIRE", R, size=92)
    thermo(ctx, C, t, T("el alambre sigue"), T("así que pones una") + 0.4, keyed(t, [(T("el alambre sigue"), 0.35), (T("recalienta", fin=True), 1.0)]))
    label(C, ctx, t, T("pero si tapas") + 0.6, T("el aire deja") + 0.6, "MANO", A, "hand", dx=0, dy=-200, size=60)
    # lámina bimetálica
    a0, a1 = T("de dos metales"), T("al calentarse")
    if a0 - 0.3 <= t < a1 + 0.4:
        label(C, ctx, t, a0 - 0.3, a1 + 0.4, "LATÓN", A, "bim", dx=-80, dy=-200, size=56)
        label(C, ctx, t, a0, a1 + 0.4, "ACERO", A, "bim", dx=80, dy=200, size=56)
    a0, a1 = T("al calentarse"), T("y por si")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 30), (T("cuando pasa de"), 50), (T("sesenta", fin=True), 60), (T("al enfriarse"), 60), (T("vuelve", fin=True) + 0.3, 45)])
        C.badge(ctx, f"LÁMINA {int(v)} °C", W / 2, BY, win(t, a0, a1), R if v >= 59.5 else O, size=82)
        if T("se separa") + 0.2 < t < T("al enfriarse"): C.badge(ctx, "OFF", W / 2, BY + 150, win(t, T("se separa") + 0.2, T("al enfriarse")), R, size=90)
        if t > T("vuelve") + 0.2: C.badge(ctx, "ON", W / 2, BY + 150, win(t, T("vuelve") + 0.2, a1), G, size=90)
    label(C, ctx, t, T("del contacto") - 0.2, T("al enfriarse"), "CONTACTO", A, "cont", dx=40, dy=200, size=54)
    label(C, ctx, t, T("un fusible"), T("por último"), "FUSIBLE", A, "fuse", dx=0, dy=-220, size=62)
    badge(C, ctx, t, T("se funde") + 0.4, T("por último"), "✗ CORRIENTE", R, size=80)
    label(C, ctx, t, T("una boquilla"), T("sígueme"), "BOQUILLA", A, "noz", dx=-40, dy=260, size=62)
    a0, a1 = T("que concentra"), DUR
    if a0 <= t < a1:
        v = keyed(t, [(a0, 70), (T("chorro", fin=True), 80)])
        C.badge(ctx, f"AIRE {int(v)} °C", W / 2, BY, win(t, a0, a1 - 0.3), O, size=84)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(1.2), 0.45), (0.2, C.s_buzz(3.0), 0.18), (T("vamos a"), C.s_whoosh(), 0.4), (T("pero tarda"), C.s_pop(), 0.35),
         (T("y aire que"), C.s_whoosh(), 0.4), (T("primero") + 0.1, C.s_thud(), 0.45), (T("así que pones un") + 0.6, C.s_pop(), 0.4),
         (T("con un motor"), C.s_clank(), 0.4), (T("aspira el"), C.s_whoosh(1.0), 0.4), (T("aspira el") + 0.3, C.s_buzz(3.0), 0.15),
         (T("pero el aire frío"), C.s_fail(), 0.3), (T("pones un alambre"), C.s_pop(), 0.4), (T("unos treinta"), C.s_whoosh(), 0.3),
         (T("una placa"), C.s_pop(), 0.35), (T("cuando pasa la"), C.s_buzz(1.6), 0.3), (T("al rojo"), C.s_coin(), 0.35),
         (T("el aire lo"), C.s_whoosh(), 0.4), (T("ese alambre"), C.s_pop(), 0.4), (T("mucho más"), C.s_pop(), 0.35),
         (T("por eso un"), C.s_win(), 0.35), (T("pero si tapas") + 0.8, C.s_thud(), 0.5), (T("el aire deja") + 0.2, C.s_fail(), 0.4),
         (T("y todo se"), C.s_buzz(1.4), 0.3), (T("así que pones una") + 0.3, C.s_pop(), 0.4), (T("y la lámina"), C.s_clank(), 0.3),
         (T("se separa"), C.s_clank(), 0.5), (T("vuelve"), C.s_clank(), 0.45), (T("un fusible"), C.s_pop(), 0.35),
         (T("se funde"), C.s_fail(), 0.45), (T("una boquilla"), C.s_clank(), 0.45), (T("que concentra"), C.s_whoosh(1.0), 0.45),
         (T("sígueme"), C.s_win(), 0.35)]
    return E
