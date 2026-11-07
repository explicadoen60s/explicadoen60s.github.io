# Capa 2D de «Así lee tu móvil la huella»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("huella")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"segundo", "huella", "crestas", "valles", "aire", "placas", "condensador", "carga", "mucho", "nada", "píxel",
            "oscuro", "claro", "ochenta", "ocho", "siete", "setecientos", "foto", "termina", "divide", "mapa", "mapas",
            "coinciden", "desbloquea", "perfecta", "colarse", "cincuenta", "mil", "cinco", "código", "luz", "ultrasonido"}

def sg(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)
def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.8, 1.0)
    BY = H * 0.265
    if t < T("cómo lee"):
        v = 0.4 * sg(t, 0.4, T("sabe que"))
        C.badge(ctx, ("%.1f S" % v).replace(".", ","), W / 2, BY, win(t, 0.3, T("cómo lee")), Y, size=90)
        if t >= T("sabe que"): C.badge(ctx, "✓", W / 2, BY + 150, win(t, T("sabe que"), T("cómo lee")), G, size=100)
    label(C, ctx, t, T("tiene crestas") + 0.1, T("debajo"), "CRESTA", A, "ridge", dx=-60, dy=-260, size=62)
    label(C, ctx, t, T("y valles"), T("debajo"), "VALLE", A, "valley", dx=120, dy=-330, size=62)
    label(C, ctx, t, T("un poquito"), T("debajo"), "AIRE", A, "valley", dx=170, dy=120, size=56)
    label(C, ctx, t, T("placas"), T("donde toca"), "PLACA", A, "plate", dx=-120, dy=160, size=60)
    a0, a1 = T("donde toca"), T("así que cada")
    if a0 <= t < a1:
        f = sg(t, T("donde toca"), T("cambia mucho", fin=True)); v = 100 - 70 * f
        x, y = A("chg_r"); C.badge(ctx, "%d" % round(v), clampx(x), clampy(y + 120, hi=1400), win(t, a0, a1), R, size=70)
        if t >= T("donde hay un"):
            f2 = sg(t, T("donde hay un"), T("casi nada", fin=True)); v2 = 100 - 5 * f2
            x, y = A("chg_v"); C.badge(ctx, "%d" % round(v2), clampx(x + 120), clampy(y + 120, hi=1400), win(t, T("donde hay un"), a1), G, size=70)
    a0, a1 = T("un sensor"), T("pero tu móvil")
    if a0 <= t < a1:
        f = sg(t, T("un sensor"), T("píxeles", fin=True))
        C.badge(ctx, "%d × %d" % (round(88 * f), 88), W / 2, BY, win(t, a0, a1), B, size=84)
        if t >= T("más de siete"): C.badge(ctx, miles(7744 * sg(t, T("más de siete"), T("setecientos", fin=True))) + " PÍXELES", W / 2, BY + 140, win(t, T("más de siete"), a1), Y, size=70)
    if T("pero tu móvil") <= t < T("busca dónde"):
        C.badge(ctx, "✗ FOTO", W / 2, BY, win(t, T("no guarda"), T("busca dónde")), R, size=80)
    a0, a1 = T("busca dónde"), T("con esos puntos")
    if a0 <= t < a1:
        n = min(14, int(14 * sg(t, a0, a0 + 0.18 * 14 + 0.3) + 0.5))
        C.badge(ctx, "%d PUNTOS" % n, W / 2, BY, win(t, a0, a1), R, size=78)
    if T("y guarda") <= t < T("cuando vuelves"):
        C.badge(ctx, "✓ MAPA", W / 2, BY, win(t, T("y guarda"), T("cuando vuelves")), G, size=78)
    a0, a1 = T("si coinciden"), T("se desbloquea")
    if a0 <= t < a1 + 0.1:
        n = int(14 * sg(t, a0, T("puntos", 3, fin=True)))
        C.badge(ctx, "%d / 14" % n, W / 2, BY, win(t, a0, a1 + 0.1), G, size=90)
    if T("el sensor no") <= t < T("por eso"):
        v = 100 - 22 * sg(t, T("el sensor no"), T("perfecta", fin=True))
        C.badge(ctx, "%d %%" % round(v), W / 2, BY, win(t, T("el sensor no"), T("por eso")), Y, size=90)
    if T("la probabilidad") <= t < T("y para que"):
        v = 50000 * sg(t, T("la probabilidad") + 0.3, T("cincuenta mil", fin=True))
        C.badge(ctx, "1 / " + miles(max(1, v)), W / 2, BY, win(t, T("la probabilidad"), T("y para que")), R, size=90)
    a0, a1 = T("tras cinco"), T("en los móviles")
    if T("y para que") <= t < a1:
        k = 0 if t < a0 else min(5, 1 + int((t - a0) / 0.42))
        C.badge(ctx, "%d / 5" % k, W / 2, BY, win(t, T("y para que"), a1), R if k else Y, size=90)
    label(C, ctx, t, T("una luz"), T("o un ultrasonido"), "LUZ", A, "chip", dx=-170, dy=40, size=62)
    label(C, ctx, t, T("o un ultrasonido") + 0.2, T("sígueme") + 0.6, "ULTRASONIDO", A, "chip", dx=0, dy=150, size=56)
    label(C, ctx, t, T("bajo la pantalla"), T("una luz"), "PANTALLA", A, "D", dx=0, dy=150, size=58)

def sfx_events(C):
    E = [(0.45, C.s_thud(), 0.5), (T("sabe que"), C.s_win(), 0.4), (T("vamos a mirar"), C.s_whoosh(), 0.45),
         (T("tiene crestas") - 0.2, C.s_thud(), 0.45), (T("placas"), C.s_pop(), 0.35), (T("guarda una"), C.s_bleep(880), 0.25),
         (T("cambia mucho"), C.s_fail(), 0.3), (T("casi nada"), C.s_pop(), 0.3), (T("es un píxel"), C.s_pop(), 0.35),
         (T("un sensor"), C.s_whoosh(), 0.4), (T("setecientos"), C.s_coin(), 0.4), (T("no guarda"), C.s_fail(), 0.35),
         (T("dibuja un mapa"), C.s_whoosh(0.7), 0.35), (T("cuando vuelves"), C.s_thud(), 0.4), (T("compara"), C.s_whoosh(), 0.35),
         (T("se desbloquea"), C.s_win(), 0.45), (T("otra persona"), C.s_fail(), 0.35), (T("cincuenta mil"), C.s_coin(), 0.4),
         (T("el código"), C.s_pop(), 0.4), (T("en los móviles"), C.s_whoosh(), 0.4), (T("o un ultrasonido"), C.s_buzz(1.2), 0.25),
         (T("sígueme"), C.s_whoosh(), 0.4)]
    for k in range(5): E.append((T("tras cinco") + 0.42 * k + 0.2, C.s_fail(), 0.3))
    for k in range(14): E.append((T("busca dónde") + 0.18 * k, C.s_bleep(600 + 40 * k), 0.12))
    return E
