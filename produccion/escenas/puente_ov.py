# Capa 2D de «¿Y si construyes un puente colgante?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("puente")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"puente", "colgado", "alambres", "mar", "kilómetro", "pilares", "torres", "doscientos", "veintisiete", "metros",
            "rascacielos", "setenta", "plantas", "cables", "cable", "hilas", "rueda", "mil", "quinientos", "cinco", "milímetros",
            "noventa", "centímetros", "ciento", "veintinueve", "kilómetros", "tres", "vueltas", "tierra", "fuerza", "hormigón",
            "enterrados", "tirantes", "tablero", "peso", "suelo"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]
def num(v): return f"{int(round(v)):,}".replace(",", ".")

def ruler(ctx, C, x, y0, y1, u, p, col):
    """regla vertical de y0 (base) a y1 (arriba) dibujada hasta u"""
    if p <= 0: return
    yt = y0 + (y1 - y0) * u
    for lw, c in ((16, (0, 0, 0)), (8, col)):
        ctx.set_line_width(lw); ctx.set_source_rgba(*c, p); ctx.set_line_cap(1)
        ctx.move_to(x, y0); ctx.line_to(x, yt); ctx.stroke()
        n = int(10 * u)
        for k in range(n + 1):
            yy = y0 + (y1 - y0) * k / 10; ctx.move_to(x - (22 if k % 5 == 0 else 12), yy); ctx.line_to(x, yy); ctx.stroke()
        ctx.move_to(x - 26, yt); ctx.line_to(x + 26, yt); ctx.stroke()

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.8, 1.0)
    Yb = H * 0.31
    def badge(C, ctx, t, a, b, text, col, size=70):
        p = win(t, a, b)
        if p: C.badge(ctx, text, W / 2, Yb, p, col, size=size)
    # apertura
    label(C, ctx, t, 0.3, T("no piensas"), "TIRANTES", A, "coche", dx=60, dy=-330, size=58)
    label(C, ctx, t, T("colgado") - 0.1, T("y si tuvieras"), "CABLE", A, "cable", dx=-40, dy=-150, size=64)
    # 1 km de agua
    a0, a1 = T("entre las dos"), T("no puedes")
    if a0 <= t < a1:
        p = win(t, a0, a1); (xl, yl), (xr, yr) = A("orL"), A("orR")
        xl, xr = max(70, xl), min(W - 150, xr); yy = min(yl, yr) - 70
        C.arrow_dim(ctx, xl, xr, yy, Y, p)
        v = keyed(t, [(a0 + 0.2, 0), (T("kilómetro", fin=True), 1000)])
        C.badge(ctx, ("+" if v > 999 else "") + f"{num(v)} M", W / 2, yy - 110, p, Y, size=74)
    label(C, ctx, t, T("agua profunda") - 0.1, T("no puedes"), "PROFUNDO", A, "fondo", dx=0, dy=-120, size=56)
    badge(C, ctx, t, T("pilares") - 0.1, T("así que levantas") - 0.1, "✗ PILAR", R, size=80)
    label(C, ctx, t, T("así que levantas") + 0.6, T("en el puente"), "TORRE", A, "torreL", dx=40, dy=-110, size=62)
    label(C, ctx, t, T("una cerca") + 0.5, T("en el puente"), "TORRE", A, "torreR", dx=-40, dy=-110, size=62)
    # 227 m y 70 plantas
    a0, a1 = T("en el puente"), T("pero las torres")
    if a0 <= t < a1:
        p = win(t, a0, a1); (xb, yb), (xt, yt) = A("baseL"), A("torreL")
        u = ss((t - T("doscientos") + 0.2) / (T("metros", fin=True) - T("doscientos") + 0.2))
        xr = min(W - 170, xt + 120); ruler(ctx, C, xr, yb, yt, u, p, Y)
        C.badge(ctx, f"{int(round(227 * u))} M", W / 2 + 120, Yb, p, Y, size=84)
    a0, a1 = T("como un rascacielos"), T("pero las torres")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0), (T("plantas", fin=True), 70)])
        C.badge(ctx, f"{int(round(v))} PLANTAS", W / 2 - 60, Yb + 130, win(t, a0, a1), B, size=70)
    badge(C, ctx, t, T("no sujetan") - 0.1, T("así que tiendes"), "✗ SIN CABLES", R, size=78)
    label(C, ctx, t, T("así que tiendes") + 0.8, T("pero un cable"), "CABLES", A, "torreL", dx=60, dy=-140, size=62)
    # bobina gigante
    label(C, ctx, t, T("pero un cable") + 0.5, T("así que lo hilas"), "UNA PIEZA", A, "bobina", dx=0, dy=-260, size=60)
    badge(C, ctx, t, T("ni subir") - 0.1, T("así que lo hilas"), "✗ NO SE PUEDE SUBIR", R, size=66)
    # hilado
    label(C, ctx, t, T("con una rueda"), T("cada cable"), "RUEDA", A, "rueda", dx=0, dy=-150, size=62)
    a0, a1 = T("alambre a"), T("y aquí")
    if a0 <= t < a1:
        k0 = T("cada cable"); k1 = T("dos alambres", fin=True)
        v = keyed(t, [(a0, 0), (k0, 4 * (k0 - a0) / 2.3 * 2), (k1, 27572)])
        if t < k0: v = 2 * int((t - a0) / 1.15 + 1)
        C.badge(ctx, f"{num(v)} ALAMBRES", W / 2, Yb, win(t, a0, a1), (1, 1, 1), size=74)
    label(C, ctx, t, T("cinco") - 0.1, T("y aquí"), "5 MM", A, "uno", dx=40, dy=120, size=64)
    a0, a1 = T("juntos"), T("y aquí") + 0.6
    if a0 <= t < a1:
        p = win(t, a0, a1); (xl, yl), (xr, yr) = A("detL"), A("detR"); yb = A("detB")[1] + 80
        C.arrow_dim(ctx, max(60, xl), min(W - 150, xr), yb, Y, p)
        v = keyed(t, [(a0 + 0.2, 0), (T("centímetros", fin=True), 92)])
        C.badge(ctx, f"{int(round(v))} CM", W / 2, yb + 110, p, Y, size=84)
    # vueltas a la Tierra
    a0, a1 = T("si estiras"), T("pero el cable")
    if a0 <= t < a1:
        u = ss((t - (T("si estiras") + 0.3)) / (T("tres vueltas", fin=True) - 0.2 - T("si estiras") - 0.3))
        p = win(t, a0, a1)
        C.badge(ctx, f"{num(129000 * u)} KM", W / 2, Yb, p, Y, size=84)
        n = int(129000 * u / 40075)
        C.badge(ctx, f"{n} VUELTAS", W / 2, Yb + 135, p, B if n < 3 else G, size=70)
    # fuerza y anclajes
    label(C, ctx, t, T("muchísima") - 0.1, T("bloques"), "FUERZA", A, "finL", dx=60, dy=-170, size=66)
    label(C, ctx, t, T("bloques"), T("ahora cuelgas"), "HORMIGÓN", A, "ancla", dx=60, dy=-40, size=62)
    badge(C, ctx, t, T("enterrados"), T("ahora cuelgas") + 0.3, "✓ ANCLADO", G, size=78)
    label(C, ctx, t, T("ahora cuelgas") + 0.4, T("el peso"), "TIRANTES", A, "tir", dx=0, dy=-180, size=60)
    label(C, ctx, t, T("y de ellos") + 0.4, T("el peso"), "TABLERO", A, "tablero", dx=0, dy=140, size=60)
    # camino del peso
    label(C, ctx, t, T("el peso"), T("sube por"), "PESO", A, "tir", dx=0, dy=-170, size=62)
    label(C, ctx, t, T("sube por"), T("y empuja"), "CABLE", A, "cableM", dx=0, dy=-150, size=62)
    label(C, ctx, t, T("y empuja") + 0.3, DUR - 0.5, "SUELO", A, "cimL", dx=0, dy=110, size=62)

def sfx_events(C):
    E = [(0.05, C.s_whoosh(), 0.4), (0.1, C.s_buzz(2.2), 0.18)]
    E += [(T("colgado"), C.s_whoosh(), 0.35), (T("vamos a colgarlo"), C.s_whoosh(), 0.45), (T("vamos a colgarlo") + 0.6, C.s_thud(), 0.5),
          (T("kilómetro"), C.s_coin(), 0.4), (T("pilares"), C.s_fail(), 0.4), (T("así que levantas"), C.s_thud(), 0.5),
          (T("una cerca"), C.s_thud(), 0.5), (T("metros"), C.s_coin(), 0.45), (T("plantas"), C.s_pop(), 0.4),
          (T("no sujetan"), C.s_fail(), 0.4), (T("pero las torres") + 1.6, C.s_thud(), 0.55), (T("así que tiendes"), C.s_whoosh(), 0.4),
          (T("pero un cable") + 0.6, C.s_clank(), 0.45), (T("ni subir"), C.s_fail(), 0.4), (T("así que lo hilas"), C.s_whoosh(), 0.4),
          (T("con una rueda"), C.s_buzz(2.4), 0.2), (T("cada cable"), C.s_whoosh(), 0.4), (T("dos alambres"), C.s_coin(), 0.45),
          (T("cinco"), C.s_pop(), 0.4), (T("centímetros"), C.s_coin(), 0.4), (T("si estiras"), C.s_whoosh(), 0.45),
          (T("kilómetros"), C.s_coin(), 0.45), (T("tres vueltas"), C.s_win(), 0.4), (T("pero el cable"), C.s_whoosh(), 0.4),
          (T("muchísima"), C.s_clank(), 0.45), (T("bloques"), C.s_thud(), 0.55), (T("enterrados"), C.s_win(), 0.35),
          (T("ahora cuelgas"), C.s_pop(), 0.35), (T("y de ellos"), C.s_clank(), 0.35), (T("el peso"), C.s_whoosh(), 0.35),
          (T("y empuja"), C.s_thud(), 0.5), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
