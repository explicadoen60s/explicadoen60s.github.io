# Capa 2D de «Así funciona la baliza V16»
from _ovbase import *
from marcas import cargar
T, DUR = cargar("v16")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"triángulos", "imán", "tarjeta", "autovía", "arcén", "ciento", "veinte", "destellar", "kilómetro", "direcciones",
            "curva", "localizador", "sim", "envía", "curioso", "tráfico", "dgt", "paneles", "conectados", "cien", "segundos",
            "nadie", "doce", "años", "media", "hora"}

def sg(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)

def bar(C, ctx, t, a, b, frac, col, title, y):
    p = win(t, a, b)
    if not p: return
    w, h = 600, 44; x0 = W / 2 - w / 2
    C.rrect(ctx, x0 - 14, y - 14, w + 28, h + 28, 22); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.92 * p); ctx.fill()
    C.rrect(ctx, x0, y, max(h, w * frac), h, 16); ctx.set_source_rgba(*col, p); ctx.fill()
    C.badge(ctx, title, W / 2, y - 62, p, col, size=54)

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.8, 1.0)
    BY = H * 0.265
    if T("desde este") <= t < T("ahora llevas"):
        C.badge(ctx, "✗", W / 2, BY, win(t, T("ya no"), T("ahora llevas")), R, size=110)
    label(C, ctx, t, T("con imán") - 0.1, T("por qué"), "IMÁN", A, "mag", dx=-150, dy=60, size=60)
    label(C, ctx, t, T("una tarjeta") + 0.1, T("por qué"), "SIM", A, "sim", dx=-170, dy=-90, size=60)
    if T("justo donde") <= t < T("así que ahora"):
        v = 120 * sg(t, T("justo donde"), T("veinte", fin=True))
        C.badge(ctx, "%d KM/H" % round(v), W / 2, BY, win(t, T("justo donde"), T("así que ahora")), R, size=88)
    label(C, ctx, t, T("el imán") + 0.1, T("y empieza"), "CLAC", A, "bea", dy=-170, size=70)
    a0, a1 = T("su luz"), T("pero una luz")
    if a0 <= t < a1 + 0.3:
        v = 1000 * sg(t, a0 + 0.2, T("kilómetro", fin=True))
        s = ("%d M" % round(v)) if v < 999.5 else "1 KM"
        C.badge(ctx, s, W / 2, BY, win(t, a0, a1 + 0.3), Y, size=92)
        if t >= T("en todas"): C.badge(ctx, "360°", W / 2, BY + 140, win(t, T("en todas"), a1 + 0.3), Y, size=72)
    if T("si estás") <= t < T("así que dentro"):
        C.badge(ctx, "✗ NO SE VE", W / 2, BY, win(t, T("nadie la"), T("así que dentro")), R, size=72)
    label(C, ctx, t, T("un localizador"), T("y lo envía", fin=True), "GPS", A, "gps", dx=170, dy=-80, size=62)
    label(C, ctx, t, T("una tarjeta sim"), T("y lo envía", fin=True), "SIM", A, "sim", dx=-170, dy=-110, size=62)
    if T("calcula") <= t < T("y aquí"):
        C.badge(ctx, "40,41° N  3,70° O", W / 2, BY, win(t, T("calcula") + 0.3, T("y aquí")), B, size=58)
    a0 = T("esa posición")
    if a0 <= t < T("llega a la"):
        C.badge(ctx, "✗ MÓVIL", W / 2 - 200, BY, win(t, a0 + 0.4, T("llega a la")), R, size=64)
        C.badge(ctx, "✗ GRÚA", W / 2 + 200, BY, win(t, T("ni a la"), T("llega a la")), R, size=64)
    label(C, ctx, t, T("la dgt"), T("desde ahí") + 0.5, "AVISO", A, "dgt", dy=-90, size=62)
    label(C, ctx, t, T("paneles", fin=True), T("conectados") - 0.8, "PANEL", A, "panel", dy=-90, size=56)
    a0, a1 = T("y mientras"), T("y quién")
    if a0 <= t < a1:
        e = max(0.0, t - T("repite")); cyc = 1.6
        v = 100 if t < T("repite") else 100 * (1 - (e % cyc) / cyc)
        C.badge(ctx, "%d S" % round(v), W / 2, BY, win(t, a0, a1), B, size=92)
    a0, a1 = T("y quién"), T("y la batería")
    if a0 <= t < a1:
        if t < T("viene incluida"): C.badge(ctx, "0 €", W / 2, BY, win(t, T("nadie"), T("viene incluida")), G, size=100)
        else:
            v = 12 * sg(t, T("viene incluida") + 0.2, T("años", fin=True))
            C.badge(ctx, "%d AÑOS" % round(v), W / 2, BY, win(t, T("viene incluida"), a1), G, size=92)
    a0, a1 = T("y la batería"), T("sígueme")
    if a0 <= t < a1:
        f = sg(t, T("aguantar"), T("encendida", 2, fin=True))
        bar(C, ctx, t, a0, a1, f, G, "%d MIN" % round(30 * f), BY + 70)
    label(C, ctx, t, T("y la batería") + 0.2, T("sígueme"), "BATERÍA", A, "batt", dx=0, dy=170, size=58)

def sfx_events(C):
    E = [(0.33, C.s_clank(), 0.6), (T("ya no"), C.s_fail(), 0.4), (T("ahora llevas"), C.s_whoosh(), 0.4),
         (T("se te para"), C.s_whoosh(), 0.45), (T("justo donde"), C.s_whoosh(0.9), 0.5), (T("ciento"), C.s_whoosh(0.7), 0.45),
         (T("así que ahora"), C.s_whoosh(), 0.35), (T("el imán"), C.s_clank(), 0.6), (T("y empieza"), C.s_pop(), 0.4),
         (T("su luz"), C.s_whoosh(), 0.4), (T("kilómetro", fin=True), C.s_coin(), 0.4), (T("nadie la"), C.s_fail(), 0.4),
         (T("así que dentro"), C.s_whoosh(), 0.35), (T("calcula"), C.s_bleep(880), 0.3), (T("y lo envía"), C.s_pop(), 0.45),
         (T("esa posición") + 0.4, C.s_fail(), 0.3), (T("llega a la"), C.s_whoosh(), 0.4), (T("la dgt"), C.s_win(), 0.4),
         (T("el aviso"), C.s_whoosh(), 0.4), (T("paneles", fin=True), C.s_pop(), 0.4), (T("conectados"), C.s_pop(), 0.4),
         (T("repite"), C.s_bleep(990), 0.3), (T("repite") + 1.6, C.s_bleep(990), 0.3), (T("nadie"), C.s_coin(), 0.4),
         (T("años", fin=True), C.s_win(), 0.4), (T("encendida", 2), C.s_coin(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4)]
    for k in range(6): E.append((0.35 + k / 1.6, C.s_bleep(660), 0.12))
    return E
